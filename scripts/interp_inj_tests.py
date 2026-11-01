"""Hypothesis tests for the injury interpretation page. Run with python3 -I (stdlib only).
Reads: raw OSHA ITA 300A files (same scan, dedupe and validity filter as scripts/build_injury_tables.py),
       data/processed/facilities.csv + facility_osha_by_year.csv (H3),
       data/raw/injuries/severe_injury/extracted/*.csv (H4, OSHA Severe Injury Reports).
Writes: data/processed/interp_inj_*.csv  (the notes in data/notes/interp_injury_tests.md quote only these).
Validity filter (rate_valid): hours>=1000, employees>=1, 300 <= hours/employee <= 4500, all case counts present.
Amazon vs non-Amazon: scripts/amazon_names.py. Rates are hours-weighted: sum(cases)*200000/sum(hours).
"""
import os as _os
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import csv, glob, re, collections, os, sys, random, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from amazon_names import amazon_rule
csv.field_size_limit(10**9)
R = _ROOT + '/data/raw/injuries/'
P = _ROOT + '/data/processed/'
NAICS_SEG = ('493110', '492110')
BANDS = [('<250', 0, 249), ('250-499', 250, 499), ('500-999', 500, 999), ('1000+', 1000, 10**9)]
BAND_NAMES = [b[0] for b in BANDS]
YEARS = list(range(2016, 2025))      # 2025 ITA is partial (filed through 2026-08-31): not used
B = 400                               # bootstrap draws
rng = random.Random(20261101)


def num(x):
    try:
        return float(x)
    except Exception:
        return None


def naics6(x):
    try:
        return str(int(float(x)))[:6]
    except Exception:
        return ''


def band(emp):
    for nm, lo, hi in BANDS:
        if lo <= emp <= hi:
            return nm


def write(name, rows):
    cols = []
    for r in rows:
        for k in r:
            if k not in cols:
                cols.append(k)
    with open(P + name, 'w', newline='') as fh:
        w = csv.DictWriter(fh, cols)
        w.writeheader()
        w.writerows(rows)
    print('wrote', name, len(rows))


def rnd(v, d=3):
    return None if v is None else round(v, d)


# ---------------------------------------------------------------- load ITA
files = sorted(glob.glob(R + 'x*/*.csv')) + [R + 'cy2025.csv']
best = {}
for f in files:
    with open(f, newline='', encoding='utf-8-sig', errors='replace') as fh:
        for d in csv.DictReader(fh):
            r = {k.lower(): v for k, v in d.items()}
            c = r['company_name'].strip(); e = r['establishment_name'].strip()
            n = naics6(r['naics_code'])
            am = bool(amazon_rule(c, e, r.get('ein', ''), n))
            if not (am or n in NAICS_SEG):
                continue
            y = int(float(r['year_filing_for']))
            k = (y, e.lower(), r['street_address'].lower(), r['city'].lower(), r['state'])
            rid = float(r['id'])
            if k in best and best[k]['rid'] >= rid:
                continue
            best[k] = dict(rid=rid, y=y, am=am, n=n, emp=num(r['annual_average_employees']), h=num(r['total_hours_worked']),
                           dafw=num(r['total_dafw_cases']), djtr=num(r['total_djtr_cases']), oth=num(r['total_other_cases']),
                           dd=num(r['total_dafw_days']), jd=num(r['total_djtr_days']), st=r['state'].strip().upper(),
                           ny=r.get('naics_year', ''), zip=re.sub(r'\D', '', r['zip_code'])[:5], street=r['street_address'])
recs = list(best.values())


def ok(r):
    return None not in (r['emp'], r['h'], r['dafw'], r['djtr'], r['oth']) and r['h'] >= 1000 and r['emp'] >= 1 and 300 <= r['h'] / r['emp'] <= 4500


for r in recs:
    r['ok'] = ok(r)
    r['band'] = band(r['emp']) if r['emp'] is not None else None
    r['seg_ok'] = r['n'] in NAICS_SEG

SEGS = {'493110': lambda r: r['n'] == '493110', '492110': lambda r: r['n'] == '492110', 'both': lambda r: r['n'] in NAICS_SEG}


def agg(rs):
    rs = list(rs)
    h = sum(r['h'] for r in rs)
    d = dict(n_sites=len(rs), hours=round(h), employees=round(sum(r['emp'] for r in rs)),
             dafw_cases=sum(r['dafw'] for r in rs), djtr_cases=sum(r['djtr'] for r in rs), other_cases=sum(r['oth'] for r in rs),
             dafw_days_raw=sum(r['dd'] or 0 for r in rs), djtr_days_raw=sum(r['jd'] or 0 for r in rs))
    # OSHA's Form 300 instructions cap days at 180 per case; some filers exceed that (data-entry errors), so days are capped per site
    d['dafw_days'] = sum(min(r['dd'] or 0, 180 * r['dafw']) for r in rs)
    d['djtr_days'] = sum(min(r['jd'] or 0, 180 * r['djtr']) for r in rs)
    d['sites_with_days_over_180_per_case'] = sum(1 for r in rs if (r['dd'] or 0) > 180 * r['dafw'] or (r['jd'] or 0) > 180 * r['djtr'])
    d['dart_cases'] = d['dafw_cases'] + d['djtr_cases']
    d['total_cases'] = d['dart_cases'] + d['other_cases']
    for m, c in (('trc', 'total_cases'), ('dart', 'dart_cases'), ('dafw', 'dafw_cases'), ('djtr', 'djtr_cases')):
        d[m + '_rate'] = rnd(d[c] * 200000 / h, 3) if h else None
    return d


def sel(who, seg, y=None, b=None, valid=True):
    return [r for r in recs if r['am'] == (who == 'amazon') and SEGS[seg](r) and (y is None or r['y'] == y)
            and (b is None or r['band'] == b) and (r['ok'] or not valid)]


# ---------------------------------------------------------------- reconcile with existing table
agg_ex = {}
for d in csv.DictReader(open(P + 'osha_ita_aggregates_by_year.csv')):
    agg_ex[(int(d['year']), d['who'], d['naics_segment'])] = d
rec_rows = []
for who in ('amazon', 'non_amazon'):
    for y in YEARS:
        a = agg(sel(who, 'both', y))
        ex = agg_ex.get((y, who, '493110+492110'))
        if a['n_sites']:
            rec_rows.append(dict(year=y, who=who, my_n=a['n_sites'], existing_n=ex and ex['n_establishments'], my_hours=a['hours'],
                                 existing_hours=ex and ex['hours'], my_trc=a['trc_rate'], existing_trc=ex and ex['trc_rate'],
                                 match=bool(ex and int(ex['n_establishments']) == a['n_sites'] and int(ex['hours']) == a['hours'])))
write('interp_inj_reconcile.csv', rec_rows)

# ---------------------------------------------------------------- H1 size bands
h1 = []
for seg in SEGS:
    for who in ('amazon', 'non_amazon'):
        for y in YEARS:
            for b in BAND_NAMES + ['all']:
                rs = sel(who, seg, y, None if b == 'all' else b)
                if rs:
                    h1.append(dict(segment=seg, who=who, year=y, size_band=b, **agg(rs)))
write('interp_inj_h1_size_bands.csv', h1)


def matched(am_rs, pe_rs):
    """Indirect standardisation: expected Amazon cases if each size band had the non-Amazon peer rate.
    Returns dict of ratios (crude and matched) for trc/dart/dafw, plus coverage."""
    out = {}
    pb = collections.defaultdict(lambda: [0.0, 0.0, 0.0, 0.0])
    for r in pe_rs:
        x = pb[r['band']]
        x[0] += r['h']; x[1] += r['dafw'] + r['djtr'] + r['oth']; x[2] += r['dafw'] + r['djtr']; x[3] += r['dafw']
    ab = collections.defaultdict(lambda: [0.0, 0.0, 0.0, 0.0])
    for r in am_rs:
        x = ab[r['band']]
        x[0] += r['h']; x[1] += r['dafw'] + r['djtr'] + r['oth']; x[2] += r['dafw'] + r['djtr']; x[3] += r['dafw']
    pH = sum(x[0] for x in pb.values()); aH = sum(x[0] for x in ab.values())
    if not pH or not aH:
        return None
    for i, m in ((1, 'trc'), (2, 'dart'), (3, 'dafw')):
        arate = sum(x[i] for x in ab.values()) * 200000 / aH
        prate = sum(x[i] for x in pb.values()) * 200000 / pH
        covH = sum(ab[b][0] for b in ab if pb.get(b) and pb[b][0] > 0)
        exp = sum(ab[b][0] * pb[b][i] / pb[b][0] for b in ab if pb.get(b) and pb[b][0] > 0)
        act = sum(ab[b][i] for b in ab if pb.get(b) and pb[b][0] > 0)
        out[m] = dict(amz=arate, peer=prate, crude=arate / prate if prate else None,
                      matched=act / exp if exp else None, matched_peer_rate=exp * 200000 / covH if covH else None,
                      amz_rate_covered=act * 200000 / covH if covH else None, coverage=covH / aH)
    return out


def pct(v, q):
    v = sorted(x for x in v if x is not None)
    if not v:
        return None
    return v[min(len(v) - 1, max(0, int(round(q * (len(v) - 1)))))]


def boot(am_rs, pe_rs):
    """Site-level bootstrap: Amazon sites resampled overall, peers within size band."""
    pe_by = collections.defaultdict(list)
    for r in pe_rs:
        pe_by[r['band']].append(r)
    draws = {m: {'crude': [], 'matched': []} for m in ('trc', 'dart', 'dafw')}
    for _ in range(B):
        a = [am_rs[rng.randrange(len(am_rs))] for _ in am_rs]
        p = []
        for bl in pe_by.values():
            p += [bl[rng.randrange(len(bl))] for _ in bl]
        o = matched(a, p)
        if not o:
            continue
        for m in draws:
            draws[m]['crude'].append(o[m]['crude']); draws[m]['matched'].append(o[m]['matched'])
    return draws


h1m = []; draws_store = {}
for seg in SEGS:
    for y in YEARS:
        am_rs = sel('amazon', seg, y); pe_rs = sel('non_amazon', seg, y)
        if len(am_rs) < 5 or not pe_rs:
            if am_rs:
                h1m.append(dict(segment=seg, year=y, amazon_sites=len(am_rs), peer_sites=len(pe_rs), note='too few Amazon sites (<5) for a rate comparison'))
            continue
        o = matched(am_rs, pe_rs)
        dr = boot(am_rs, pe_rs)
        draws_store[(seg, y)] = dr
        row = dict(segment=seg, year=y, amazon_sites=len(am_rs), peer_sites=len(pe_rs),
                   amazon_sites_1000plus=sum(1 for r in am_rs if r['band'] == '1000+'),
                   peer_sites_1000plus=sum(1 for r in pe_rs if r['band'] == '1000+'),
                   amazon_hours_share_1000plus=rnd(sum(r['h'] for r in am_rs if r['band'] == '1000+') / sum(r['h'] for r in am_rs), 3),
                   peer_hours_share_1000plus=rnd(sum(r['h'] for r in pe_rs if r['band'] == '1000+') / sum(r['h'] for r in pe_rs), 3),
                   amazon_hours_covered_by_peer_bands=rnd(o['dart']['coverage'], 3))
        for m in ('trc', 'dart', 'dafw'):
            row.update({m + '_amazon': rnd(o[m]['amz']), m + '_peer_all_sizes': rnd(o[m]['peer']), m + '_peer_size_matched': rnd(o[m]['matched_peer_rate']),
                        m + '_ratio_crude': rnd(o[m]['crude'], 3), m + '_ratio_crude_lo': rnd(pct(dr[m]['crude'], .025), 3), m + '_ratio_crude_hi': rnd(pct(dr[m]['crude'], .975), 3),
                        m + '_ratio_matched': rnd(o[m]['matched'], 3), m + '_ratio_matched_lo': rnd(pct(dr[m]['matched'], .025), 3), m + '_ratio_matched_hi': rnd(pct(dr[m]['matched'], .975), 3)})
        h1m.append(row)
write('interp_inj_h1_matched.csv', h1m)

# H1 within-band ratios (Amazon rate / non-Amazon rate in the same band), segment both
h1w = []
for seg_, y, b in [(sg, yy, bb) for sg in SEGS for yy in YEARS for bb in BAND_NAMES]:
    if True:
        a = agg(sel('amazon', seg_, y, b)); p = agg(sel('non_amazon', seg_, y, b))
        if a['n_sites'] and p['n_sites']:
            row = dict(segment=seg_, year=y, size_band=b, amazon_sites=a['n_sites'], peer_sites=p['n_sites'])
            for m in ('trc', 'dart', 'dafw'):
                row[m + '_amazon'] = a[m + '_rate']; row[m + '_peer'] = p[m + '_rate']
                row[m + '_ratio'] = rnd(a[m + '_rate'] / p[m + '_rate'], 3) if p[m + '_rate'] else None
            h1w.append(row)
write('interp_inj_h1_within_band_ratios.csv', h1w)

# ---------------------------------------------------------------- H2 substitution
def h2_metrics(a):
    return dict(dafw_share_of_dart=rnd(a['dafw_cases'] / a['dart_cases'], 4) if a['dart_cases'] else None,
                djtr_days_per_djtr_case=rnd(a['djtr_days'] / a['djtr_cases'], 2) if a['djtr_cases'] else None,
                dafw_days_per_dafw_case=rnd(a['dafw_days'] / a['dafw_cases'], 2) if a['dafw_cases'] else None,
                restricted_days_per_dart_case=rnd(a['djtr_days'] / a['dart_cases'], 2) if a['dart_cases'] else None)


h2 = []
for seg in ('both', '493110', '492110'):
    for y in YEARS:
        am_rs = sel('amazon', seg, y); pe_rs = sel('non_amazon', seg, y)
        if not am_rs:
            continue
        a = agg(am_rs)
        h2.append(dict(segment=seg, year=y, group='amazon', n_sites=a['n_sites'], dart_cases=a['dart_cases'], dafw_cases=a['dafw_cases'], djtr_cases=a['djtr_cases'],
                       dart_rate=a['dart_rate'], dafw_rate=a['dafw_rate'], djtr_rate=a['djtr_rate'], sites_days_capped=a['sites_with_days_over_180_per_case'], **h2_metrics(a)))
        if not pe_rs:
            continue
        p = agg(pe_rs)
        h2.append(dict(segment=seg, year=y, group='non_amazon_all_sizes', n_sites=p['n_sites'], dart_cases=p['dart_cases'], dafw_cases=p['dafw_cases'], djtr_cases=p['djtr_cases'],
                       dart_rate=p['dart_rate'], dafw_rate=p['dafw_rate'], djtr_rate=p['djtr_rate'], sites_days_capped=p['sites_with_days_over_180_per_case'], **h2_metrics(p)))
        # size-matched: per band peer metric weighted by Amazon's cases in that band
        pb = {b: agg([r for r in pe_rs if r['band'] == b]) for b in BAND_NAMES}
        ab = {b: agg([r for r in am_rs if r['band'] == b]) for b in BAND_NAMES}
        use = [b for b in BAND_NAMES if ab[b]['n_sites'] and pb[b]['n_sites'] and pb[b]['dart_cases'] > 0]
        if use:
            w = sum(ab[b]['dart_cases'] for b in use)
            share = sum(ab[b]['dart_cases'] * pb[b]['dafw_cases'] / pb[b]['dart_cases'] for b in use) / w if w else None
            wj = sum(ab[b]['djtr_cases'] for b in use if pb[b]['djtr_cases'] > 0)
            jd = sum(ab[b]['djtr_cases'] * pb[b]['djtr_days'] / pb[b]['djtr_cases'] for b in use if pb[b]['djtr_cases'] > 0) / wj if wj else None
            wd = sum(ab[b]['dafw_cases'] for b in use if pb[b]['dafw_cases'] > 0)
            dd = sum(ab[b]['dafw_cases'] * pb[b]['dafw_days'] / pb[b]['dafw_cases'] for b in use if pb[b]['dafw_cases'] > 0) / wd if wd else None
            h2.append(dict(segment=seg, year=y, group='non_amazon_size_matched', n_sites=sum(pb[b]['n_sites'] for b in use),
                           dafw_share_of_dart=rnd(share, 4), djtr_days_per_djtr_case=rnd(jd, 2), dafw_days_per_dafw_case=rnd(dd, 2),
                           note='peer band values weighted by Amazon case counts in the bands %s' % '|'.join(use)))
write('interp_inj_h2_substitution.csv', h2)
# bootstrap CI for 2019->2024 change in Amazon DAFW share of DART and gap to peers (segment both)
H2M = ('dafw_share_of_dart', 'djtr_days_per_djtr_case', 'dafw_days_per_dafw_case')
chg = []
for seg in ('both', '493110'):
    for grp in ('amazon', 'non_amazon_all_sizes', 'non_amazon_size_matched'):
        v = {}
        for r in h2:
            if r['segment'] == seg and r['group'] == grp:
                v[r['year']] = r
        for m in H2M:
            if 2019 in v and 2024 in v and v[2019].get(m) is not None and v[2024].get(m) is not None:
                chg.append(dict(segment=seg, group=grp, metric=m, y2019=v[2019][m], y2024=v[2024][m], change=rnd(v[2024][m] - v[2019][m], 4),
                                pct_change=rnd((v[2024][m] / v[2019][m] - 1) * 100, 1)))


def boot_share(rs, field_num, field_den):
    out = []
    for _ in range(B):
        s = [rs[rng.randrange(len(rs))] for _ in rs]
        d = sum(field_den(r) for r in s)
        out.append(sum(field_num(r) for r in s) / d if d else None)
    return out


for seg_c, grp, who in [(sg, g, w) for sg in ('both', '493110') for g, w in (('amazon', 'amazon'), ('non_amazon_all_sizes', 'non_amazon'))]:
    for m, fn, fd in (('dafw_share_of_dart', lambda r: r['dafw'], lambda r: r['dafw'] + r['djtr']),
                      ('djtr_days_per_djtr_case', lambda r: min(r['jd'] or 0, 180 * r['djtr']), lambda r: r['djtr']),
                      ('dafw_days_per_dafw_case', lambda r: min(r['dd'] or 0, 180 * r['dafw']), lambda r: r['dafw'])):
        b19 = boot_share(sel(who, seg_c, 2019), fn, fd); b24 = boot_share(sel(who, seg_c, 2024), fn, fd)
        diff = [b - a for a, b in zip(b19, b24) if a is not None and b is not None]
        for c in chg:
            if c['group'] == grp and c['metric'] == m and c['segment'] == seg_c:
                c['change_lo'] = rnd(pct(diff, .025), 4); c['change_hi'] = rnd(pct(diff, .975), 4)
write('interp_inj_h2_change_2019_2024.csv', chg)

# ---------------------------------------------------------------- H3 facility type
fac = {d['facility_id']: d for d in csv.DictReader(open(P + 'facilities.csv'))}
fy = list(csv.DictReader(open(P + 'facility_osha_by_year.csv')))


def heur(f):
    b = f['type_basis']
    return 'heuristic' if (b.startswith('heuristic') or b.startswith('NAICS 492110 courier') or b.startswith('unclassified') or 'AMZL' in b) else 'label_or_list'


# 'AMZL' label is Amazon's own label but the facility notes say it "may include some sort sites": counted as label-based with that caveat
def heur2(f):
    b = f['type_basis']
    return 'heuristic' if (b.startswith('heuristic') or b.startswith('NAICS 492110 courier') or b.startswith('unclassified')) else 'label_or_list'


H3 = []
for d in fy:
    f = fac.get(d['facility_id'])
    if not f or d['rate_valid'] != 'True':
        continue
    try:
        h = float(d['hours']); emp = float(d['employees'])
    except Exception:
        continue
    H3.append(dict(y=int(d['year']), type=f['facility_type'], basis=heur2(f), conf=f['confidence'], h=h, emp=emp, tot=float(d['total_cases']),
                   dart=float(d['dart_cases']), dafw=float(d['dafw_cases']), band=band(emp)))


def agg3(rs):
    h = sum(r['h'] for r in rs)
    return dict(n_facility_years=len(rs), hours=round(h), avg_employees=round(sum(r['emp'] for r in rs) / len(rs)), total_cases=round(sum(r['tot'] for r in rs)),
                dart_cases=round(sum(r['dart'] for r in rs)), dafw_cases=round(sum(r['dafw'] for r in rs)),
                trc_rate=rnd(sum(r['tot'] for r in rs) * 200000 / h, 3), dart_rate=rnd(sum(r['dart'] for r in rs) * 200000 / h, 3),
                dafw_rate=rnd(sum(r['dafw'] for r in rs) * 200000 / h, 3))


h3 = []
for y in YEARS:
    for t in sorted({r['type'] for r in H3}):
        for sub in ('all', 'label_or_list_typed_only'):
            rs = [r for r in H3 if r['y'] == y and r['type'] == t and (sub == 'all' or r['basis'] == 'label_or_list')]
            if rs:
                h3.append(dict(year=y, facility_type=t, subset=sub, share_typed_heuristically=rnd(sum(1 for r in rs if r['basis'] == 'heuristic') / len(rs), 3), **agg3(rs)))
write('interp_inj_h3_type_year.csv', h3)
h3b = []
for t in sorted({r['type'] for r in H3}):
    for b in BAND_NAMES:
        for sub in ('all', 'label_or_list_typed_only'):
            rs = [r for r in H3 if 2021 <= r['y'] <= 2024 and r['type'] == t and r['band'] == b and (sub == 'all' or r['basis'] == 'label_or_list')]
            if rs:
                h3b.append(dict(years='2021-2024', facility_type=t, size_band=b, subset=sub, **agg3(rs)))
write('interp_inj_h3_type_band_2021_2024.csv', h3b)
h3c = []
for t in sorted({r['type'] for r in H3}):
    rs = [r for r in H3 if r['type'] == t]
    cnt = collections.Counter(fac[d['facility_id']]['type_basis'][:60] for d in fy if fac.get(d['facility_id']) and fac[d['facility_id']]['facility_type'] == t)
    h3c.append(dict(facility_type=t, valid_facility_years=len(rs), heuristic_share=rnd(sum(1 for r in rs if r['basis'] == 'heuristic') / len(rs), 3) if rs else None))
write('interp_inj_h3_typing_quality.csv', h3c)

# ---------------------------------------------------------------- Amazon NAICS mix (recoding check)
mix = collections.Counter(); mixh = collections.Counter()
for r in recs:
    if r['am'] and r['ok']:
        mix[(r['y'], r['n'], r['ny'])] += 1; mixh[(r['y'], r['n'], r['ny'])] += r['h']
write('interp_inj_amazon_naics_mix.csv', [dict(year=k[0], naics=k[1], naics_year_field=k[2], valid_sites=v, hours=round(mixh[k])) for k, v in sorted(mix.items())])

# ---------------------------------------------------------------- H4 severe injuries
STATE_PLAN_PRIVATE = {'AK', 'AZ', 'CA', 'HI', 'IN', 'IA', 'KY', 'MD', 'MI', 'MN', 'NV', 'NM', 'NC', 'OR', 'PR', 'SC', 'TN', 'UT', 'VT', 'VA', 'WA', 'WY'}
FULL = {'ALASKA': 'AK', 'ARIZONA': 'AZ', 'CALIFORNIA': 'CA', 'HAWAII': 'HI', 'INDIANA': 'IN', 'IOWA': 'IA', 'KENTUCKY': 'KY', 'MARYLAND': 'MD', 'MICHIGAN': 'MI',
        'MINNESOTA': 'MN', 'NEVADA': 'NV', 'NEW MEXICO': 'NM', 'NORTH CAROLINA': 'NC', 'OREGON': 'OR', 'PUERTO RICO': 'PR', 'SOUTH CAROLINA': 'SC', 'TENNESSEE': 'TN',
        'UTAH': 'UT', 'VERMONT': 'VT', 'VIRGINIA': 'VA', 'WASHINGTON': 'WA', 'WYOMING': 'WY'}
sir_file = glob.glob(R + 'severe_injury/extracted/*.csv')[0]
sir = list(csv.DictReader(open(sir_file, newline='', encoding='utf-8-sig', errors='replace')))
# consistency check: SIR FederalState==0 states must equal the 22 private-sector state plans
sir_state0 = {s for s in {r['State'] for r in sir if r['FederalState'] == '0'}}
write('interp_inj_h4_state_plan_list.csv',
      [dict(state_or_territory=k, abbrev=v, treated_as='state plan (private sector covered): excluded from numerator and denominator',
            sir_FederalState_flag_zero=k in sir_state0,
            source='OSHA State Plans page https://www.osha.gov/stateplans (22 plans covering private sector, retrieved 2026-11-01); SIR FederalState column agrees') for k, v in sorted(FULL.items())]
      + [dict(state_or_territory='CT IL ME MA NJ NY VI', abbrev='', treated_as='public-sector-only state plans: private sector is federal OSHA, so INCLUDED',
              sir_FederalState_flag_zero=False, source='OSHA State Plans page https://www.osha.gov/stateplans')])
AMZ_SIR = re.compile(r'amazon', re.I)
AMZ_SIR_EXCL = re.compile(r'amazon (fresh|web services|go)\b|amazon environmental|amazone|ultra fast fresh|amazon\.com.*web services', re.I)


def sir_amazon(name):
    return bool(AMZ_SIR.search(name)) and not AMZ_SIR_EXCL.search(name)


def addr_key(zipc, street):
    z = re.sub(r'\D', '', zipc or '')[:5]
    t = re.sub(r'[^a-z0-9 ]', '', (street or '').lower()).split()
    return (z, t[0] if t else '', (t[1][:3] if len(t) > 1 else ''))


# symmetric, same-year address match against VALID ITA filers of the same comparison set (the same sites that make up the hours denominator)
ADDR = collections.defaultdict(set)
for r in recs:
    if r['ok'] and r['seg_ok'] and r['st'] not in STATE_PLAN_PRIVATE:
        g = 'amazon' if r['am'] else 'non_amazon_' + r['n']
        ADDR[(g, r['y'])].add(addr_key(r['zip'], r['street']))
HAZ = [('vehicle / truck / forklift / pedestrian struck', re.compile(r'vehicle|truck|forklift|pedestrian|roadway|motor', re.I)),
       ('fall, slip or trip', re.compile(r'fall|slip|trip', re.I)),
       ('caught in / compressed / crushed', re.compile(r'caught|compress|crush', re.I)),
       ('struck by object', re.compile(r'struck by|struck against|falling object', re.I)),
       ('heat / cold / environmental', re.compile(r'heat|cold|environmental', re.I)),
       ('violence / other person', re.compile(r'violence|assault|person', re.I))]


def haz(title):
    for nm, rx in HAZ:
        if rx.search(title or ''):
            return nm
    return 'other'


hazc = collections.defaultdict(collections.Counter); hazt = collections.defaultdict(collections.Counter)
sev = collections.defaultdict(lambda: collections.Counter())
sev_rows = []
for r in sir:
    ev = r['EventDate']; y = int(ev.split('/')[-1]) if ev else None
    if y is None or y > 2024 or y < 2016:
        continue
    if r['FederalState'] != '1' or r['State'] in FULL:
        continue
    nm = r['Employer']
    n6 = naics6(r['Primary NAICS'])
    if sir_amazon(nm):
        grp = 'amazon'
    elif n6 == '493110':
        grp = 'non_amazon_493110'
    elif n6 == '492110':
        grp = 'non_amazon_492110'
    else:
        continue
    hosp = num(r['Hospitalized']) or 0; amp = num(r['Amputation']) or 0; eye = num(r['Loss of Eye']) or 0
    matched_addr = addr_key(r['Zip'], r['Address1']) in ADDR[(grp, y)]
    hg = haz(r['EventTitle'])
    for g in (grp, 'non_amazon_both' if grp.startswith('non_amazon') else None):
        if g:
            hazc[g][hg] += 1; hazt[g][r['EventTitle'].strip()] += 1
            for gg in (g, g + '_matched' if matched_addr else None):
                if gg:
                    c = sev[(gg, y)]
                    c['reports'] += 1; c['hospitalized'] += hosp; c['amputations'] += amp; c['loss_of_eye'] += eye
    if grp == 'amazon':
        sev_rows.append(dict(year=y, employer=nm.strip(), state=r['State'], naics=n6, hospitalized=hosp, amputation=amp))
hz_rows = []
for g, c in hazc.items():
    tot = sum(c.values())
    for k, v in c.most_common():
        hz_rows.append(dict(group=g, kind='hazard_category', label=k, reports=v, share=rnd(v / tot, 3), window='2016-2024 (all valid-state SIR reports in group)'))
    for k, v in hazt[g].most_common(8):
        hz_rows.append(dict(group=g, kind='top_EventTitle', label=k, reports=v, share=rnd(v / tot, 3), window='2016-2024'))
write('interp_inj_h4_hazard_mix.csv', hz_rows)
write('interp_inj_h4_amazon_sir_rows.csv', sev_rows)   # employer names only (businesses), no narratives, no person data


def fed_hours(who, seg, y, valid=True):
    rs = [r for r in recs if r['am'] == (who == 'amazon') and r['y'] == y and SEGS[seg](r) and r['st'] not in STATE_PLAN_PRIVATE and (r['ok'] or not valid)
          and r['h'] is not None]
    return sum(r['h'] for r in rs), len(rs)


def pois_ci(k, conf=0.95):
    """Exact (Garwood) Poisson interval for count k, via bisection on the Poisson CDF."""
    def cdf(kk, mu):  # P(X<=kk)
        s = 0.0; t = math.exp(-mu)
        for i in range(kk + 1):
            if i > 0:
                t *= mu / i
            s += t
        return s
    a = (1 - conf) / 2
    lo = 0.0
    if k > 0:
        l, h = 0.0, k + 10 * math.sqrt(k + 1) + 10
        for _ in range(100):
            m = (l + h) / 2
            if 1 - cdf(k - 1, m) < a: l = m
            else: h = m
        lo = (l + h) / 2
    l, h = 0.0, k + 10 * math.sqrt(k + 1) + 10
    for _ in range(100):
        m = (l + h) / 2
        if cdf(k, m) > a: l = m
        else: h = m
    return lo, (l + h) / 2


def binom_cdf(k, n, p):
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k + 1))


def rate_ratio_ci(x1, h1_, x0, h0_):
    """Exact conditional (binomial) CI for rate ratio (x1/h1)/(x0/h0)."""
    n = x1 + x0
    if n == 0 or x1 == 0 or x0 == 0:
        return None, None
    def pbin(p_lo):
        pass
    a = 0.025
    # p = proportion of events in group 1 under ratio rr: p = rr*h1/(rr*h1+h0)
    def solve(target_upper):
        l, h = 1e-6, 1e6
        for _ in range(200):
            m = math.sqrt(l * h)
            p = m * h1_ / (m * h1_ + h0_)
            v = (1 - binom_cdf(x1 - 1, n, p)) if target_upper else binom_cdf(x1, n, p)
            if target_upper:
                if v < a: l = m
                else: h = m
            else:
                if v > a: l = m
                else: h = m
        return math.sqrt(l * h)
    return solve(True), solve(False)


h4 = []
for y in YEARS:
    if y < 2016:
        continue
    ha, na = fed_hours('amazon', 'both', y)
    ha_all, _ = fed_hours('amazon', 'both', y, valid=False)
    for grp, who, seg in (('amazon', 'amazon', 'both'), ('non_amazon_both', 'non_amazon', 'both'), ('non_amazon_493110', 'non_amazon', '493110'), ('non_amazon_492110', 'non_amazon', '492110'),
                           ('amazon_matched', 'amazon', 'both'), ('non_amazon_both_matched', 'non_amazon', 'both'), ('non_amazon_493110_matched', 'non_amazon', '493110'), ('non_amazon_492110_matched', 'non_amazon', '492110')):
        hh, nn = fed_hours(who, seg, y)
        hall, _ = fed_hours(who, seg, y, valid=False)
        c = sev.get((grp, y), collections.Counter())
        row = dict(year=y, group=grp, denominator_sites=nn, denominator_hours_valid_federal_states=round(hh), denominator_hours_all_filed_federal_states=round(hall),
                   sir_reports=c['reports'], hospitalized_persons=c['hospitalized'], amputation_persons=c['amputations'], loss_of_eye_persons=c['loss_of_eye'])
        for m, key in (('reports', 'reports'), ('hosp', 'hospitalized'), ('amp', 'amputations')):
            k = int(c[key])
            row['%s_per_100M_hours' % m] = rnd(k / hh * 1e8, 2) if hh else None
            if hh:
                lo, hi = pois_ci(k)
                row['%s_per_100M_lo' % m] = rnd(lo / hh * 1e8, 2); row['%s_per_100M_hi' % m] = rnd(hi / hh * 1e8, 2)
        h4.append(row)
write('interp_inj_h4_severe_by_year.csv', h4)
# pooled windows and ratios
pooled = []
CMP = (('both', 'non_amazon_both', 'both'), ('493110', 'non_amazon_493110', '493110'), ('492110', 'non_amazon_492110', '492110'))
for lab, ys in (('2017-2024', range(2017, 2025)), ('2017-2019', range(2017, 2020)), ('2020-2022', range(2020, 2023)), ('2021-2024', range(2021, 2025)), ('2022-2024', range(2022, 2025))):
    for suffix in ('_matched', ''):
        for peer_lab, pgrp, pseg in CMP:
            ha = sum(fed_hours('amazon', 'both', y)[0] for y in ys); hn = sum(fed_hours('non_amazon', pseg, y)[0] for y in ys)
            for key in ('reports', 'hospitalized', 'amputations'):
                ca = sum(sev.get(('amazon' + suffix, y), collections.Counter())[key] for y in ys)
                cn = sum(sev.get((pgrp + suffix, y), collections.Counter())[key] for y in ys)
                if not cn or not ca:
                    continue
                ra = ca / ha * 1e8; rn = cn / hn * 1e8
                lo, hi = rate_ratio_ci(int(ca), ha, int(cn), hn)
                pooled.append(dict(window=lab, measure=key, peer_set=peer_lab,
                                   numerator_set=('HEADLINE: symmetric same-year address match to valid ITA filers' if suffix else 'all SIR reports: BIASED LOW (peer reports include non-filers)') ,
                                   is_headline=bool(suffix and peer_lab == 'both' and key == 'reports' and lab == '2017-2024'),
                                   amazon_count=int(ca), amazon_hours=round(ha), amazon_per_100M=rnd(ra, 2), peer_count=int(cn),
                                   peer_hours=round(hn), peer_per_100M=rnd(rn, 2), rate_ratio=rnd(ra / rn, 3), ratio_lo=rnd(lo, 3), ratio_hi=rnd(hi, 3)))
write('interp_inj_h4_pooled.csv', pooled)
# companion: ITA DART and DAFW rates for the same federal-state pool, for comparing like with like
cmp4 = []
for lab, ys in (('2017-2024', range(2017, 2025)), ('2021-2024', range(2021, 2025))):
    for who in ('amazon', 'non_amazon'):
        rs = [r for r in recs if r['am'] == (who == 'amazon') and r['y'] in ys and SEGS['both'](r) and r['st'] not in STATE_PLAN_PRIVATE and r['ok']]
        cmp4.append(dict(window=lab, who=who, **agg(rs)))
write('interp_inj_h4_ita_same_pool.csv', cmp4)

# ---------------------------------------------------------------- replication of Senate / NELP size figures (NAICS 493110, valid sites, 1000+ employees)
nelp = []
for y in YEARS:
    a = [r for r in sel('amazon', '493110', y) if r['band'] == '1000+']; p = [r for r in sel('non_amazon', '493110', y) if r['band'] == '1000+']
    if a:
        ha_ = sum(r['h'] for r in a); hp_ = sum(r['h'] for r in p)
        nelp.append(dict(year=y, amazon_sites_1000plus=len(a), all_sites_1000plus=len(a) + len(p), amazon_share_of_sites=rnd(len(a) / (len(a) + len(p)), 3),
                         amazon_hours_1000plus=round(ha_), all_hours_1000plus=round(ha_ + hp_), amazon_share_of_hours=rnd(ha_ / (ha_ + hp_), 3),
                         amazon_employees_1000plus=round(sum(r['emp'] for r in a)), all_employees_1000plus=round(sum(r['emp'] for r in a + p)),
                         amazon_share_of_employees=rnd(sum(r['emp'] for r in a) / sum(r['emp'] for r in a + p), 3)))
write('interp_inj_nelp_senate_replication.csv', nelp)

# ---------------------------------------------------------------- band sensitivity: band by FTE = hours/2000 instead of reported average employees
# (Amazon's reported employees look like a headcount in 2019: few hours per employee, so reported-employee banding puts more of its sites in 1000+)
fte = []
for seg in SEGS:
    for y in YEARS:
        am_rs = sel('amazon', seg, y); pe_rs = sel('non_amazon', seg, y)
        if len(am_rs) < 5 or not pe_rs:
            continue
        saved = [(r, r['band']) for r in am_rs + pe_rs]
        for r in am_rs + pe_rs:
            r['band'] = band(r['h'] / 2000.0)
        o = matched(am_rs, pe_rs); n1000 = sum(1 for r in am_rs if r['band'] == '1000+')
        for r, b in saved:
            r['band'] = b
        fte.append(dict(segment=seg, year=y, amazon_sites_1000plus_by_fte=n1000, amazon_sites=len(am_rs), hours_per_employee_amazon=rnd(sum(r['h'] for r in am_rs) / sum(r['emp'] for r in am_rs), 0),
                        trc_ratio_matched_fte_band=rnd(o['trc']['matched'], 3), dart_ratio_matched_fte_band=rnd(o['dart']['matched'], 3), dafw_ratio_matched_fte_band=rnd(o['dafw']['matched'], 3)))
write('interp_inj_h1_matched_fte_band.csv', fte)

# ---------------------------------------------------------------- H5 trend
h5 = []
for seg in SEGS:
    for m in ('trc', 'dart', 'dafw'):
        ys = [y for y in YEARS if (seg, y) in draws_store]
        for y in ys:
            row = next(r for r in h1m if r['segment'] == seg and r['year'] == y)
            h5.append(dict(segment=seg, measure=m, year=y, ratio_crude=row[m + '_ratio_crude'], crude_lo=row[m + '_ratio_crude_lo'], crude_hi=row[m + '_ratio_crude_hi'],
                           ratio_size_matched=row[m + '_ratio_matched'], matched_lo=row[m + '_ratio_matched_lo'], matched_hi=row[m + '_ratio_matched_hi'],
                           amazon_sites=row['amazon_sites']))
write('interp_inj_h5_ratio_by_year.csv', h5)


def slope(xs, ys):
    n = len(xs); mx = sum(xs) / n; my = sum(ys) / n
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)


h5s = []
for seg in SEGS:
    for m in ('trc', 'dart', 'dafw'):
        for kind in ('crude', 'matched'):
            vals = {y: next(r for r in h1m if r['segment'] == seg and r['year'] == y)[m + '_ratio_' + kind] for y in YEARS if (seg, y) in draws_store}
            if 2019 in vals and 2024 in vals:
                diff = [b - a for a, b in zip(draws_store[(seg, 2019)][m][kind], draws_store[(seg, 2024)][m][kind])]
                yy = [y for y in vals if 2018 <= y <= 2024 and vals[y] is not None]
                h5s.append(dict(segment=seg, measure=m, ratio_kind=kind, ratio_2018=vals.get(2018), ratio_2019=vals[2019], ratio_2020=vals.get(2020), ratio_2022=vals.get(2022), ratio_2024=vals[2024],
                                change_2019_2024=rnd(vals[2024] - vals[2019], 3), change_lo=rnd(pct(diff, .025), 3), change_hi=rnd(pct(diff, .975), 3),
                                ols_slope_per_year_2018_2024=rnd(slope(yy, [vals[y] for y in yy]), 4)))
write('interp_inj_h5_trend_summary.csv', h5s)
print('done')
