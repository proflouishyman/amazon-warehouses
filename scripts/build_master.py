"""Build data/processed/facilities_master.csv and the population-access tables.

Run:  python3 -I scripts/build_master.py

Inputs  : facilities.csv, osha_ita_amazon_establishments.csv, 
          egrid / CBECS model via scripts/env_04_screening_model.py (imported), Census CenPop2020 tract
          centroids (data/raw/census, https://www2.census.gov/geo/docs/reference/cenpop2020/tract/).
Outputs : facilities_master.csv, facility_osha_by_year.csv, osha_unmatched_establishments.csv,
          population_access_by_year.csv, population_access_by_state.csv, master_match_report.json

Everything environmental is a SCREENING ESTIMATE (electricity and heating only; truck emissions are not estimated) (per 1,000,000 sq ft unless a sourced sq_ft exists).
Population access uses 2020 tract population (population-weighted tract centroids) for every year;
only the set of sites changes by year, so it is NOT a measure of population change.
"""
import csv, datetime, glob, importlib.util, json, math, os, re, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'data/processed')


def rd(name):
    with open(os.path.join(P, name), newline='', encoding='utf-8') as fh:
        return list(csv.DictReader(fh))


def wr(name, rows, cols=None):
    cols = cols or list(rows[0])
    with open(os.path.join(P, name), 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction='ignore')
        w.writeheader()
        w.writerows(rows)


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------------- 1. facilities + OSHA join
fac = rd('facilities.csv')
# geography QA: geocoded point must fall in the row's state and the ZIP must belong to the state (scripts/facilities_08_check_geo.py)
_spec = importlib.util.spec_from_file_location('geocheck', os.path.join(ROOT, 'scripts/facilities_08_check_geo.py'))
geocheck = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(geocheck)
GEO = geocheck.check_rows(fac)
for _i, _f in enumerate(fac):
    _f['geo_state_check'], _f['geo_state_check_detail'] = GEO[_i]
GEO_FAIL = {'point_outside_state', 'zip_state_mismatch', 'no_state', 'state_not_us'}
geo_counts = collections.Counter(v[0] for v in GEO.values())
print('geography check:', dict(geo_counts), 'hard failures:', sum(v for k, v in geo_counts.items() if k in GEO_FAIL))
by_code = collections.defaultdict(list)
for f in fac:
    by_code[f['site_code'].upper()].append(f)

STREET_ABBR = {'street': 'st', 'avenue': 'ave', 'road': 'rd', 'drive': 'dr', 'boulevard': 'blvd', 'parkway': 'pkwy',
               'highway': 'hwy', 'court': 'ct', 'lane': 'ln', 'north': 'n', 'south': 's', 'east': 'e', 'west': 'w'}


def akey(street, zipc):
    s = re.sub(r'[^a-z0-9 ]', ' ', (street or '').lower()).split()
    s = [STREET_ABBR.get(t, t) for t in s]
    z = re.sub(r'\D', '', zipc or '')[:5]
    if len(s) < 2 or not z or not s[0][:1].isdigit():
        return None
    return s[0] + ' ' + s[1] + ' ' + z


by_addr = collections.defaultdict(list)
for f in fac:
    k = akey(f['street_address'].split(',')[0], f['zip'] or (re.search(r'(\d{5})(?:-\d{4})?\s*[–-]?\s*$', f['street_address']) or [None, ''])[1])
    if k:
        by_addr[k].append(f)

CODE_RE = re.compile(r'^[A-Z][A-Z0-9]{2,5}$')


def site_code(name):
    toks = re.split(r'\s+', (name or '').strip())
    for t in reversed(toks[-2:]):
        t = t.strip(':-').upper()
        if CODE_RE.match(t) and any(c.isdigit() for c in t):
            return t
    return None


osha = rd('osha_ita_amazon_establishments.csv')
matched, unmatched = [], []
how_ct = collections.Counter()
for r in osha:
    code = site_code(r['establishment_name'])
    cands = by_code.get(code, []) if code else []
    f, how = None, None
    if cands:
        z = (r['zip_code'] or '')[:5]
        f = next((c for c in cands if c['zip'] == z), None) or next(
            (c for c in cands if akey(c['street_address'].split(',')[0], c['zip']) == akey(r['street_address'], z)), None) or cands[0]
        how = 'site_code'
    else:
        k = akey(r['street_address'], r['zip_code'])
        if k and k in by_addr:
            f, how = by_addr[k][0], 'street_address_zip'
    if f:
        r['facility_id'] = f['facility_id']
        r['match_method'] = how
        matched.append(r)
        how_ct[how] += 1
    else:
        unmatched.append(r)

# per-facility-year table (a facility can have >1 OSHA row in a year, e.g. split filings: sum them)
fy = collections.OrderedDict()
for r in matched:
    k = (r['facility_id'], int(r['year']))
    d = fy.setdefault(k, dict(facility_id=r['facility_id'], year=int(r['year']), osha_rows=0, employees=0.0, hours=0.0,
                                total_cases=0.0, dart_cases=0.0, dafw_cases=0.0, deaths=0.0, naics=r['naics_code'],
                                valid=True))
    d['osha_rows'] += 1
    for a, b in (('employees', 'employees'), ('hours', 'hours'), ('total_cases', 'total_cases'),
                 ('dart_cases', 'dart_cases'), ('dafw_cases', 'dafw_cases'), ('deaths', 'deaths')):
        d[a] += num(r[b]) or 0
    d['valid'] = d['valid'] and (r['rate_valid'] == 'True')
fy_rows = []
for d in fy.values():
    h = d['hours']
    # same validity filter as the headline injury series (build_injury_tables.py): 300-4,500 hours per employee
    ok = d['valid'] and h >= 1000 and d['employees'] >= 1 and 300 <= h / d['employees'] <= 4500
    d['trc_rate'] = round(d['total_cases'] * 200000 / h, 2) if ok else ''
    d['dart_rate'] = round(d['dart_cases'] * 200000 / h, 2) if ok else ''
    d['dafw_rate'] = round(d['dafw_cases'] * 200000 / h, 2) if ok else ''
    d['rate_valid'] = ok
    d['naics'] = re.sub(r'\.0+$', '', str(d['naics']))
    fy_rows.append(d)
wr('facility_osha_by_year.csv', fy_rows,
   ['facility_id', 'year', 'osha_rows', 'naics', 'employees', 'hours', 'total_cases', 'dart_cases', 'dafw_cases',
    'deaths', 'trc_rate', 'dart_rate', 'dafw_rate', 'rate_valid'])
wr('osha_unmatched_establishments.csv', unmatched,
   ['year', 'id', 'company_name', 'establishment_name', 'street_address', 'city', 'state', 'zip_code', 'naics_code',
    'industry_description', 'employees', 'hours'])

fy_by_fac = collections.defaultdict(list)
for d in fy_rows:
    fy_by_fac[d['facility_id']].append(d)

# ---------------------------------------------------------------- 2. environment screening estimates
spec = importlib.util.spec_from_file_location('env04', os.path.join(ROOT, 'scripts/env_04_screening_model.py'))
env04 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(env04)
env = {}
for f in fac:
    la, lo = num(f['lat']), num(f['lon'])
    if la is None or lo is None:
        continue
    env[f['facility_id']] = env04.model(dict(facility_id=f['facility_id'], state=f['state'], sqft=1000000, lat=la, lon=lo, year=2023))

# ---------------------------------------------------------------- 3. population access
TR = []
for fn in sorted(glob.glob(os.path.join(ROOT, 'data/raw/census/CenPop2020_Mean_TR*.txt'))):
    with open(fn, encoding='utf-8-sig') as fh:
        for r in csv.DictReader(fh):
            TR.append((r['STATEFP'], int(r['POPULATION']), float(r['LATITUDE']), float(r['LONGITUDE'])))
TOTAL_POP = sum(t[1] for t in TR)
FIPS_ST = {'01': 'AL', '02': 'AK', '04': 'AZ', '05': 'AR', '06': 'CA', '08': 'CO', '09': 'CT', '10': 'DE', '11': 'DC',
           '12': 'FL', '13': 'GA', '15': 'HI', '16': 'ID', '17': 'IL', '18': 'IN', '19': 'IA', '20': 'KS', '21': 'KY',
           '22': 'LA', '23': 'ME', '24': 'MD', '25': 'MA', '26': 'MI', '27': 'MN', '28': 'MS', '29': 'MO', '30': 'MT',
           '31': 'NE', '32': 'NV', '33': 'NH', '34': 'NJ', '35': 'NM', '36': 'NY', '37': 'NC', '38': 'ND', '39': 'OH',
           '40': 'OK', '41': 'OR', '42': 'PA', '44': 'RI', '45': 'SC', '46': 'SD', '47': 'TN', '48': 'TX', '49': 'UT',
           '50': 'VT', '51': 'VA', '53': 'WA', '54': 'WV', '55': 'WI', '56': 'WY'}

located = [f for f in fac if num(f['lat']) is not None]
SITES = [(num(f['lat']), num(f['lon']), f['facility_id'], f['facility_type']) for f in located]
grid = collections.defaultdict(list)
for i, s in enumerate(SITES):
    grid[(int(math.floor(s[0])), int(math.floor(s[1])))].append(i)


def hav_mi(a, b, c, d):
    p = math.pi / 180
    x = math.sin((c - a) * p / 2) ** 2 + math.cos(a * p) * math.cos(c * p) * math.sin((d - b) * p / 2) ** 2
    return 3958.8 * 2 * math.asin(math.sqrt(x))


# sets of sites: filed (matched) in year y, plus the whole located roster
filed_in = collections.defaultdict(set)
for d in fy_rows:
    filed_in[d['year']].add(d['facility_id'])
SETS = {str(y): filed_in[y] for y in sorted(filed_in)}
SETS['roster_all'] = {s[2] for s in SITES}
TYPES = ['all', 'fulfillment_center', 'delivery_station', 'sort_center']
fid_type = {s[2]: s[3] for s in SITES}
fid_idx = {s[2]: i for i, s in enumerate(SITES)}

# acc[(set,type)] -> [pop20,pop50]; per-state for two sets; per-site pop20
acc = {(sk, t): [0, 0] for sk in SETS for t in TYPES}
st_acc = collections.defaultdict(lambda: [0, 0, 0])  # (set,state) -> pop, p20, p50
site_pop20 = collections.Counter()
site_pop50 = collections.Counter()
STATE_SETS = ('2025', 'roster_all')
for stfp, pop, la, lo in TR:
    if pop <= 0:
        continue
    cl, cn = int(math.floor(la)), int(math.floor(lo))
    dlon = int(50 / (69.0 * max(0.2, math.cos(math.radians(la))))) + 1
    near = []
    for a in range(cl - 1, cl + 2):
        for b in range(cn - dlon, cn + dlon + 1):
            for i in grid.get((a, b), ()):
                d = hav_mi(la, lo, SITES[i][0], SITES[i][1])
                if d <= 50:
                    near.append((d, SITES[i][2]))
    # per-type nearest
    for sk in SETS:
        sset = SETS[sk]
        best = {t: 1e9 for t in TYPES}
        for d, fid in near:
            if fid in sset:
                if d < best['all']:
                    best['all'] = d
                t = fid_type[fid]
                if t in best and d < best[t]:
                    best[t] = d
        for t in TYPES:
            if best[t] <= 20:
                acc[(sk, t)][0] += pop
            if best[t] <= 50:
                acc[(sk, t)][1] += pop
        if sk in STATE_SETS:
            e = st_acc[(sk, FIPS_ST[stfp])]
            e[0] += pop
            if best['all'] <= 20:
                e[1] += pop
            if best['all'] <= 50:
                e[2] += pop
    for d, fid in near:
        site_pop50[fid] += pop
        if d <= 20:
            site_pop20[fid] += pop
# states with no tract near anything still need a denominator
for stfp, pop, la, lo in TR:
    for sk in STATE_SETS:
        st_acc[(sk, FIPS_ST[stfp])]  # ensure key (population added above only when pop>0)

pa_rows = []
for sk in SETS:
    for t in TYPES:
        n = sum(1 for fid in SETS[sk] if t == 'all' or fid_type.get(fid) == t)
        p20, p50 = acc[(sk, t)]
        pa_rows.append(dict(set=sk, site_type=t, n_sites=n, pop20=p20, pop50=p50, pop_total_2020=TOTAL_POP,
                            share20=round(p20 / TOTAL_POP, 4), share50=round(p50 / TOTAL_POP, 4),
                            note=('sites with a matched OSHA ITA filing in that calendar year' if sk != 'roster_all'
                                  else 'every located site in facilities.csv (upper bound; includes unverified rows)')))
wr('population_access_by_year.csv', pa_rows)
ps_rows = [dict(set=k[0], state=k[1], pop2020=v[0], pop20=v[1], pop50=v[2],
                share20=round(v[1] / v[0], 4) if v[0] else '', share50=round(v[2] / v[0], 4) if v[0] else '')
           for k, v in sorted(st_acc.items())]
wr('population_access_by_state.csv', ps_rows)

# ---------------------------------------------------------------- 4. subsidies (what can honestly be joined)
# (subsidy data removed: pending verification; see data/notes/financial.md)

# ---------------------------------------------------------------- 5. master table
# trade-press opening years (EXACT / PROBABLE matches, stated date 2026 or earlier): scripts/build_trade_press.py
_spec = importlib.util.spec_from_file_location('tpress', os.path.join(ROOT, 'scripts/build_trade_press.py'))
tpress = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tpress)
PRESS = tpress.build(fac)

# Year-basis hierarchy (one year per site, first rule that gives a year wins):
#   1 mwpvl_opening_year          MWPVL opening year from the Wayback captures (mwpvl_wayback_sites_all.csv, mwpvl_corrections.csv applied).
#                                  Skipped when year_is_projection = Y (MWPVL still listed the site as planned or delayed with a future
#                                  year, so the year is a plan, not an opening). year_resolution is kept in year_flag when not single_value.
#   2 epi_mwpvl2012_opening_year  facilities.csv opening_year (EPI 2017 appendix and the April 2012 MWPVL table)
#   3 press_event_year            year of the opening date in facility_events_all.csv (press and subscription-news events), matched EXACT or
#                                  PROBABLE to the roster by site code and state, event type compatible with the roster type, not in the
#                                  future; trade_press_openings (build_trade_press) is the fallback when the events file gives nothing
#   4 first_osha_filing           first OSHA ITA filing year ("operating by", an upper bound on the opening year)
# year_flag marks weaker evidence: mwpvl_year_conflict, mwpvl_later_year_after_planned, mwpvl_projection_not_used,
# year_after_first_osha_filing (the year is later than a filing the site made, so the site was already operating).
SPLIT = re.compile(r'[\s/,]+')
TODAY = datetime.date.today().isoformat()
CORR_FIELD = {'city': 'latest_city', 'state': 'latest_state', 'sq_ft': 'latest_sq_ft', 'year': 'year_opened', 'year_opened': 'year_opened'}
mw = {r['site_code'].upper(): dict(r) for r in rd('mwpvl_wayback_sites_all.csv')}
corr_applied = 0
for c in rd('mwpvl_corrections.csv'):
    col = CORR_FIELD.get(c['field'])
    r = mw.get(c['site_code'].upper())
    if col and r is not None and c['corrected_value'] != '':
        r[col] = c['corrected_value']
        corr_applied += 1
print('MWPVL corrections applied:', corr_applied)

EVENT_TYPE_OK = {'fulfillment_center': ('fulfillment center', 'robotic fulfillment center', 'big-and-bulky fulfillment center', 'distribution center', 'inbound cross dock'),
                 'delivery_station': ('delivery station',), 'sort_center': ('sortation center', 'sort center'),
                 'air_hub': ('air hub',), 'other_logistics': None}
QRANK = {'exact': 0, 'probable': 1}
CRANK = {'high': 0, 'medium': 1, 'low': 2}


def event_year(d):
    m = re.match(r'\s*(\d{4})(?:-(\d{2}))?(?:-(\d{2}))?', d or '')
    if not m:
        return None
    y = int(m.group(1))
    if y > 2026 or (m.group(2) and m.group(3) and d.strip()[:10] > TODAY) or (m.group(2) and not m.group(3) and d.strip()[:7] > TODAY[:7]):
        return None
    return y


EV_BY_CODE = collections.defaultdict(list)
for i, e in enumerate(rd('facility_events_all.csv')):
    if e['match_quality'] in QRANK and e['match_site_code'] and event_year(e['opening_date']):
        EV_BY_CODE[e['match_site_code'].upper()].append(e)


def events_for(f):
    out = []
    for c in SPLIT.split(f['site_code'].upper()):
        for e in EV_BY_CODE.get(c, []):
            if e['state'] and f['state'] and e['state'] != f['state']:
                continue
            ok = EVENT_TYPE_OK.get(f['facility_type'])
            if ok is not None and e['facility_type'] and e['facility_type'].lower() not in ok:
                continue
            out.append(e)
    return out


def mwpvl_for(f):
    return [mw[c] for c in SPLIT.split(f['site_code'].upper()) if c in mw]


# pullback: one status per roster site, the strongest evidence wins; the date is that row's date; the full history is kept
PB_SEV = ['closed', 'closed_partial', 'closed_temporary', 'sublease', 'paused', 'cancelled', 'delayed', 'removed_from_mwpvl_list']
PB_BY_CODE = collections.defaultdict(list)
for r in rd('pullback_sites.csv'):
    for c in SPLIT.split(r['site_code'].upper()):
        if c:
            PB_BY_CODE[c].append(r)
pb_matched_rows = set()

master = []
basis_flag_ct = collections.Counter()
for f in fac:
    # first/last OSHA filing year come from the matched facility-year table, not the roster's own site-code grouping (fixes 40 mismatches, review 2026-10-31)
    _yrs = sorted(d['year'] for d in fy_by_fac.get(f['facility_id'], []))
    if _yrs:
        f['first_osha_filing_year'], f['last_osha_filing_year'] = str(_yrs[0]), str(_yrs[-1])
    m = dict(f)
    hist = sorted(fy_by_fac.get(f['facility_id'], []), key=lambda d: d['year'])
    m['osha_matched_years'] = ';'.join(str(d['year']) for d in hist)
    m['osha_matched_year_count'] = len(hist)
    if hist:
        last = hist[-1]
        m['osha_latest_year'] = last['year']
        m['osha_latest_employees'] = round(last['employees'])
        m['osha_latest_hours'] = round(last['hours'])
        m['osha_latest_total_cases'] = round(last['total_cases'])
        m['osha_latest_trc_rate'] = last['trc_rate']
        v = [d for d in hist if d['rate_valid']]
        hh = sum(d['hours'] for d in v)
        m['osha_pooled_trc_rate'] = round(sum(d['total_cases'] for d in v) * 200000 / hh, 2) if hh else ''
        m['osha_pooled_hours'] = round(hh)
        m['osha_total_cases_all_years'] = round(sum(d['total_cases'] for d in hist))
    m['osha_match_status'] = 'matched' if hist else 'no_match_in_establishment_file'
    # --- year basis
    pr = PRESS.get(f['facility_id'], {})
    m['press_opening_year'] = pr.get('press_opening_year', '')
    m['press_source_url'] = pr.get('press_source_url', '')
    mws = mwpvl_for(f)
    mwy = sorted(mws, key=lambda r: (r['year_opened'] or '9999'))
    mwr = mwy[0] if mwy else None
    m['mwpvl_year'] = mwr['year_opened'] if mwr else ''
    m['mwpvl_year_resolution'] = mwr['year_resolution'] if mwr else ''
    m['mwpvl_year_is_projection'] = mwr['year_is_projection'] if mwr else ''
    m['mwpvl_sq_ft'] = (mwr['latest_sq_ft'] if mwr else '')
    m['mwpvl_sq_ft_snapshot'] = (mwr['latest_sq_ft_snapshot'] if mwr and mwr['latest_sq_ft'] else '')
    m['mwpvl_status'] = mwr['latest_status'] if mwr else ''
    evs = events_for(f)
    evs.sort(key=lambda e: (QRANK[e['match_quality']], CRANK.get(e['confidence'], 3), event_year(e['opening_date'])))
    ev = evs[0] if evs else None
    m['event_opening_year'] = event_year(ev['opening_date']) if ev else ''
    year, basis, src, flag = '', '', '', []
    if mwr and mwr['year_opened'] and mwr['year_is_projection'] != 'Y':
        year, basis = int(mwr['year_opened']), 'mwpvl_opening_year'
        src = 'MWPVL via Wayback Machine, %s to %s (%s snapshots); site %s; years seen %s' % (
            mwr['first_snapshot'], mwr['last_snapshot'], mwr['n_snapshots'], mwr['site_code'], mwr['year_opened_all'])
        if mwr['year_resolution'] == 'conflict_modal_value':
            flag.append('mwpvl_year_conflict')
        elif mwr['year_resolution'] == 'later_year_after_planned':
            flag.append('mwpvl_later_year_after_planned')
    else:
        if mwr and mwr['year_opened'] and mwr['year_is_projection'] == 'Y':
            flag.append('mwpvl_projection_not_used')
        if f['opening_year']:
            year, basis = int(f['opening_year']), 'epi_mwpvl2012_opening_year'
            src = f['opening_year_basis'] or 'EPI or MWPVL 2012 table'
        elif ev:
            year, basis = event_year(ev['opening_date']), 'press_event_year'
            src = 'press or news event, %s (match %s, confidence %s): %s' % (ev['opening_date'], ev['match_quality'], ev['confidence'], ev['sources'][:160])
            m['press_opening_year'] = year
            m['press_source_url'] = ev['article_url'] or m['press_source_url']
        elif pr:
            year, basis = int(pr['press_opening_year']), 'press_event_year'
            src = 'trade-press opening report (%s match, %s confidence)' % (pr.get('press_quality', ''), pr.get('press_confidence', ''))
        elif f['first_osha_filing_year']:
            year, basis = int(f['first_osha_filing_year']), 'first_osha_filing'
            src = 'OSHA ITA first Form 300A filing year (operating by; upper bound on opening year)'
    if year and basis != 'first_osha_filing' and f['first_osha_filing_year'] and year > int(f['first_osha_filing_year']):
        flag.append('year_after_first_osha_filing')
    if basis == 'press_event_year' and f['first_osha_filing_year'] and int(f['first_osha_filing_year']) - year >= 3:
        flag.append('press_year_well_before_first_osha_filing')
    m['year_used'] = year
    m['year_basis'] = basis
    m['year_source'] = src
    m['year_flag'] = ';'.join(flag)
    # legacy names for the map page (to be dropped once map.js reads year_basis)
    m['year_basis_legacy'] = {'mwpvl_opening_year': 'opening_year', 'epi_mwpvl2012_opening_year': 'opening_year',
                              'press_event_year': 'press_opening_year', 'first_osha_filing': 'first_osha_filing'}.get(basis, '')
    for fl in flag:
        basis_flag_ct[(basis or 'undated', fl)] += 1
    # --- pullback
    rows_pb = []
    for c in SPLIT.split(f['site_code'].upper()):
        for r in PB_BY_CODE.get(c, []):
            if r['state'] and f['state'] and r['state'] != f['state']:
                continue
            if r not in rows_pb:
                rows_pb.append(r)
    m['pullback_status'] = m['pullback_date'] = m['pullback_history'] = ''
    if rows_pb:
        best = sorted(rows_pb, key=lambda r: (PB_SEV.index(r['status']) if r['status'] in PB_SEV else 99, r['date']))[0]
        m['pullback_status'], m['pullback_date'] = best['status'], best['date']
        m['pullback_history'] = '; '.join('%s %s' % (r['status'], r['date']) for r in sorted(rows_pb, key=lambda r: r['date']))
        for r in rows_pb:
            pb_matched_rows.add(id(r))
    e = env.get(f['facility_id'])
    if e:
        m['env_subregion'] = e['subregion']
        m['env_subregion_method'] = e['subregion_method']
        m['env_grid_lb_co2e_per_mwh_2023'] = e['grid_lb_co2e_per_mwh']
        for tag in ('low', 'central', 'high'):
            m['env_per1Msqft_grid_tco2e_' + tag] = e['grid_tco2e_' + tag]
        m['env_per1Msqft_gas_tco2e_central'] = e['gas_tco2e_central']
        sq = num(f['sq_ft'])
        if sq:
            k = sq / 1e6
            m['env_total_tco2e_central_sourced_sqft'] = round((e['grid_tco2e_central'] + e['gas_tco2e_central']) * k, 1)
            m['env_sqft_basis'] = 'sq_ft from facilities.csv (2012 MWPVL value, may be outdated)'
        else:
            m['env_sqft_basis'] = 'none: only per-1M-sq-ft intensity reported, no size assumed'
        m['env_flag'] = 'ESTIMATE: screening model, not measured; see data/notes/environment.md'
    m['pop_within_20mi_2020'] = site_pop20.get(f['facility_id'], '') if f['facility_id'] in fid_idx else ''
    m['pop_within_50mi_2020'] = site_pop50.get(f['facility_id'], '') if f['facility_id'] in fid_idx else ''
    master.append(m)

cols = list(fac[0].keys())
for m in master:
    for k in m:
        if k not in cols:
            cols.append(k)
wr('facilities_master.csv', master, cols)

# ---------------------------------------------------------------- 6. match report
fac_ids_matched = {m['facility_id'] for m in master if m['osha_match_status'] == 'matched'}
osha_ids = {(r['id']) for r in osha}
osha_matched_ids = {r['id'] for r in matched}
by_year = collections.defaultdict(lambda: [0, 0])
for r in osha:
    by_year[r['year']][0] += 1
for r in matched:
    by_year[r['year']][1] += 1
unm_naics = collections.Counter(re.sub(r'\.0+$', '', r['naics_code']) for r in unmatched)
rep = dict(
    year_basis=dict(collections.Counter(m['year_basis'] or 'undated' for m in master)),
    year_flags={k[0] + ' | ' + k[1]: v for k, v in sorted(basis_flag_ct.items())},
    year_after_first_osha_by_basis=dict(collections.Counter(m['year_basis'] for m in master if 'year_after_first_osha_filing' in m['year_flag']), ),
    mwpvl_corrections_applied=corr_applied,
    mwpvl_sq_ft_sites=sum(1 for m in master if m['mwpvl_sq_ft']),
    pullback_status=dict(collections.Counter(m['pullback_status'] for m in master if m['pullback_status'])),
    pullback_rows_with_site_code=len({id(r) for rs in PB_BY_CODE.values() for r in rs}),
    pullback_rows_matched_to_roster=len(pb_matched_rows),
    facilities=len(fac), geo_state_check=dict(geo_counts), geo_state_check_hard_failures=sum(v for k, v in geo_counts.items() if k in GEO_FAIL), osha_rows=len(osha), osha_rows_matched=len(matched), osha_rows_unmatched=len(unmatched),
    osha_row_match_rate=round(len(matched) / len(osha), 4), match_method=dict(how_ct),
    osha_rows_matched_by_year={y: dict(rows=v[0], matched=v[1], rate=round(v[1] / v[0], 3)) for y, v in sorted(by_year.items())},
    facilities_with_osha_match=len(fac_ids_matched), facility_match_rate=round(len(fac_ids_matched) / len(fac), 4),
    facilities_in_2025_flag=sum(1 for f in fac if f['status'] == 'in_2025_osha_filing'),
    facilities_in_2025_flag_but_no_match=sum(1 for m in master if m['status'] == 'in_2025_osha_filing' and m['osha_match_status'] != 'matched'),
    facilities_with_env=len(env), facilities_with_coords=len(located),
    unmatched_top_naics=unm_naics.most_common(8), tract_count=len(TR), total_pop_2020=TOTAL_POP,
    pop_sets={sk: len(v) for sk, v in SETS.items()})
with open(os.path.join(P, 'master_match_report.json'), 'w') as fh:
    json.dump(rep, fh, indent=1)
print(json.dumps(rep, indent=1))
