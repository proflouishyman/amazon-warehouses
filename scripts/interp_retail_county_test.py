#!/usr/bin/env python3
"""Interpretation test: did counties that gained an Amazon fulfillment center (FC) lose more
retail establishments afterwards than similar counties that did not?   Run: python3 -I scripts/interp_retail_county_test.py

Descriptive event-study evidence, not causal proof.  Public data only (Census County Business Patterns,
Census county population estimates, the Census geocoder, and this repo's facilities_master.csv).
Stdlib only (numpy/pandas/statsmodels are not installed here).  Outputs:
  data/processed/interp_retail_fc_county_map.csv      FC -> county FIPS and the county's first-FC year
  data/processed/interp_retail_event_study.csv        indexed event-study means and bootstrap CIs
  data/processed/interp_retail_pooled_regression.csv  two-way FE regressions, cluster-robust by county
  data/processed/interp_retail_pretrends.csv          pre-period and covariate comparison
  data/processed/interp_retail_sample_counts.csv      counties per group and sector
Raw: data/raw/retail_context/cbp_county/ (gitignored).
"""
import csv, io, json, math, os, random, sys, time, urllib.request, urllib.parse, zipfile
from collections import defaultdict, Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, 'data/raw/retail_context/cbp_county')
PROC = os.path.join(ROOT, 'data/processed')
os.makedirs(RAW, exist_ok=True)
YEARS = list(range(2010, 2024))
SEED = 20261101
NBOOT = 2000
MIN_BASE = 5          # minimum establishments at t-1 for a county-sector to enter an index
KS = list(range(-3, 5))

# CBP county-file NAICS codes (files 2010-2023 use NAICS 2007/2012/2017 vintages; county files never carry the 2022 vintage)
SECTORS = {
    'retail_total': '44----',
    'general_merchandise': '452///',      # NAICS 452 (2017 vintage restructured 4521 into 4522/4523, the 3-digit total is continuous)
    'clothing': '448///',
    'electronics_appliance': '443///',
    'sporting_hobby_book': '451///',
    'placebo_grocery_4451': '4451//',
    'placebo_food_services': '722///',
}
PLACEBO = {'placebo_grocery_4451', 'placebo_food_services'}


def wr(name, rows, fields):
    with open(os.path.join(PROC, name), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow(r)


# ------------------------------------------------------------------ CBP extract (cached)
def load_cbp():
    out = os.path.join(RAW, 'cbp_county_sector_extract.csv')
    if not os.path.exists(out):
        codes = set(SECTORS.values())
        rows = []
        for y in YEARS:
            z = os.path.join(RAW, 'cbp%02dco.zip' % (y % 100))
            if not os.path.exists(z):
                u = 'https://www2.census.gov/programs-surveys/cbp/datasets/%d/cbp%02dco.zip' % (y, y % 100)
                urllib.request.urlretrieve(u, z)
                time.sleep(0.5)
            with zipfile.ZipFile(z) as zf:
                nm = zf.namelist()[0]
                with zf.open(nm) as fh:
                    rd = csv.DictReader(io.TextIOWrapper(fh, encoding='latin-1'))
                    rd.fieldnames = [h.lower() for h in rd.fieldnames]
                    for r in rd:
                        if r['naics'] in codes or r['naics'] == '------':
                            rows.append((y, r['fipstate'] + r['fipscty'], r['naics'], r['est']))
        with open(out, 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow(['year', 'fips', 'naics', 'est'])
            w.writerows(rows)
    est = defaultdict(dict)       # (sector, fips) -> {year: est}
    present = defaultdict(set)    # fips -> years with an all-sector row
    inv = {v: k for k, v in SECTORS.items()}
    with open(out) as f:
        for r in csv.DictReader(f):
            y = int(r['year'])
            if r['naics'] == '------':
                present[r['fips']].add(y)
            else:
                est[(inv[r['naics']], r['fips'])][y] = int(r['est'])
    return est, present


# ------------------------------------------------------------------ population (2010 Census base) and region
def load_pop():
    p = os.path.join(RAW, 'co-est2019-alldata.csv')
    if not os.path.exists(p):
        urllib.request.urlretrieve('https://www2.census.gov/programs-surveys/popest/datasets/2010-2019/counties/totals/co-est2019-alldata.csv', p)
    pop = {}
    byname = {}
    with open(p, encoding='latin-1') as f:
        for r in csv.DictReader(f):
            if r['SUMLEV'] != '050':
                continue
            fips = r['STATE'] + r['COUNTY']
            pop[fips] = dict(pop2010=int(r['CENSUS2010POP']), pop2019=int(r['POPESTIMATE2019']), region=r['REGION'],
                             state=r['STATE'], name=r['CTYNAME'], stname=r['STNAME'])
            nm = r['CTYNAME']
            for suf in (' County', ' Parish', ' Borough', ' Census Area', ' city', ' Municipio'):
                if nm.endswith(suf):
                    nm = nm[:-len(suf)]
            byname[(r['STNAME'], nm.lower())] = fips
    return pop, byname


def band(p):
    for i, cut in enumerate((10000, 25000, 50000, 100000, 250000, 500000, 1000000)):
        if p < cut:
            return i
    return 7


BAND_LABEL = ['<10k', '10-25k', '25-50k', '50-100k', '100-250k', '250-500k', '500k-1M', '1M+']

ABBR = {'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut',
        'DE': 'Delaware', 'DC': 'District of Columbia', 'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois',
        'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
        'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi', 'MO': 'Missouri', 'MT': 'Montana',
        'NE': 'Nebraska', 'NV': 'Nevada', 'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York',
        'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania',
        'RI': 'Rhode Island', 'SC': 'South Carolina', 'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah',
        'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming'}


# ------------------------------------------------------------------ facilities -> county FIPS
def geocode_fcs(pop, byname):
    cache_p = os.path.join(RAW, 'census_coordinates_cache.json')
    cache = json.load(open(cache_p)) if os.path.exists(cache_p) else {}
    fac = list(csv.DictReader(open(os.path.join(PROC, 'facilities_master.csv'))))
    out = []
    n_api = 0
    for r in fac:
        r['_fips'], r['_how'] = '', ''
        if r['lat'] and r['lon']:
            key = '%s,%s' % (r['lon'], r['lat'])
            if key not in cache:
                url = ('https://geocoding.geo.census.gov/geocoder/geographies/coordinates?x=%s&y=%s'
                       '&benchmark=Public_AR_Current&vintage=Current_Current&format=json' % (r['lon'], r['lat']))
                res = None
                for attempt in range(4):
                    try:
                        with urllib.request.urlopen(url, timeout=40) as h:
                            j = json.load(h)
                        cs = j['result']['geographies'].get('Counties', [])
                        res = cs[0]['GEOID'] if cs else ''
                        break
                    except Exception:
                        time.sleep(2 + 3 * attempt)
                cache[key] = res
                n_api += 1
                time.sleep(0.25)
                if n_api % 25 == 0:
                    json.dump(cache, open(cache_p, 'w'))
            if cache.get(key):
                r['_fips'], r['_how'] = cache[key], 'census_coordinates_api'
        if not r['_fips'] and r['county'] and r['state'] in ABBR:
            nm = r['county'].replace(' County', '').strip().lower()
            f = byname.get((ABBR[r['state']], nm))
            if f:
                r['_fips'], r['_how'] = f, 'master_county_name_state'
        out.append(r)
    json.dump(cache, open(cache_p, 'w'))
    return out


STRONG = {'mwpvl_opening_year', 'epi_mwpvl2012_opening_year', 'press_event_year'}


def classify_facilities(fac):
    """Per county: first FC year (strong basis only), plus ambiguity and other-facility flags."""
    cty = defaultdict(lambda: dict(strong=[], weak=[], undated=0, fc_n=0, other_n=0, ids=[]))
    mapped = []
    for r in fac:
        if not r['_fips']:
            continue
        c = cty[r['_fips']]
        if r['facility_type'] != 'fulfillment_center':
            c['other_n'] += 1
            continue
        c['fc_n'] += 1
        yr = r['year_used']
        flag = r['year_flag']
        basis = r['year_basis']
        usable = (yr.isdigit() and basis in STRONG and 'year_after_first_osha_filing' not in flag and 'projection' not in flag)
        if usable:
            c['strong'].append(int(yr))
            used = 'strong'
        elif yr.isdigit():
            c['weak'].append(int(yr))
            used = 'weak'
        else:
            c['undated'] += 1
            used = 'undated'
        c['ids'].append(r['facility_id'])
        mapped.append(dict(facility_id=r['facility_id'], site_code=r['site_code'], state=r['state'], county_name=r['county'],
                           county_fips=r['_fips'], fips_method=r['_how'], year_used=yr, year_basis=basis, year_flag=flag,
                           year_class=used))
    info = {}
    for f, c in cty.items():
        first = min(c['strong']) if c['strong'] else None
        wk = min(c['weak']) if c['weak'] else None
        ambiguous = (c['undated'] > 0) or (first is None and c['fc_n'] > 0) or (wk is not None and first is not None and wk < first)
        if c['fc_n'] == 0:
            ambiguous = False
        info[f] = dict(first=first, weak_first=wk, ambiguous=ambiguous, fc_n=c['fc_n'], other_n=c['other_n'])
    return info, mapped


# ------------------------------------------------------------------ helpers
def mean(x):
    return sum(x) / len(x) if x else float('nan')


def pct(xs, q):
    xs = sorted(xs)
    i = q * (len(xs) - 1)
    lo, hi = int(math.floor(i)), int(math.ceil(i))
    return xs[lo] + (xs[hi] - xs[lo]) * (i - lo)


def boot_ci(vals, rng):
    n = len(vals)
    if n < 3:
        return float('nan'), float('nan')
    ms = []
    for _ in range(NBOOT):
        s = 0.0
        for _ in range(n):
            s += vals[rng.randrange(n)]
        ms.append(s / n)
    return pct(ms, 0.025), pct(ms, 0.975)


def series(est, sector, fips):
    d = est.get((sector, fips), {})
    return [d.get(y, 0) for y in YEARS]


def idx(s, E, k):
    """index (t-1 = 100) at event time k for event year E; None when outside 2010-2023 or base too small"""
    b = E - 1 - YEARS[0]
    t = E + k - YEARS[0]
    if b < 0 or t < 0 or t >= len(YEARS):
        return None
    if s[b] < MIN_BASE:
        return None
    return 100.0 * s[t] / s[b]


def build_groups(spec, info, pop, universe):
    """treated, not-yet-treated, never-treated county sets under a specification."""
    treated, nyt, never = {}, {}, set()
    for f in universe:
        i = info.get(f)
        if i is None:
            never.add(f)
            continue
        if i['fc_n'] == 0:
            if spec['allow_other_fac'] or i['other_n'] == 0:
                never.add(f)
            continue
        if spec['include_weak']:
            # weak-basis years (first OSHA filing is an upper bound on opening) are treated as if they were openings
            yrs = [y for y in (i['first'], i['weak_first']) if y]
            first = min(yrs) if yrs else None
            if first is None:
                continue
        else:
            if i['ambiguous'] or i['first'] is None:
                continue
            first = i['first']
        if 2013 <= first <= 2019:
            treated[f] = first
        elif first >= 2021:
            nyt[f] = first
        # first FC 2020 and pre-2013 first FCs: excluded from all groups
    return treated, nyt, never


def match(treated, pools, pop):
    """for each treated county, controls in the same state and 2010-population band; else same Census region and band"""
    cell_state, cell_region = defaultdict(list), defaultdict(list)
    for f in pools:
        p = pop[f]
        cell_state[(p['state'], band(p['pop2010']))].append(f)
        cell_region[(p['region'], band(p['pop2010']))].append(f)
    m = {}
    for t in treated:
        p = pop[t]
        b = band(p['pop2010'])
        c = [x for x in cell_state.get((p['state'], b), []) if x != t]
        how = 'state_band'
        if not c:
            c = [x for x in cell_region.get((p['region'], b), []) if x != t]
            how = 'region_band'
        m[t] = (c, how)
    return m


def event_study(sector, est, treated, nyt, never, pop, rng, label, rows, counts):
    # treated counties with a usable base
    T = {f: E for f, E in treated.items() if idx(series(est, sector, f), E, -1) is not None}
    res = {}
    for gname, pool in (('never_treated', never), ('not_yet_treated', set(nyt))):
        m = match(T, pool, pop)
        # per treated county: control index at each k (mean over matched controls, masking post-own-FC years for not-yet-treated)
        per_k_t = {k: [] for k in KS}
        per_k_c = {k: [] for k in KS}
        per_k_d = {k: [] for k in KS}
        n_matched, nctrl, how_ct = 0, [], Counter()
        for f, E in T.items():
            c, how = m[f]
            if not c:
                continue
            n_matched += 1
            how_ct[how] += 1
            used = 0
            ctrl_by_k = {k: [] for k in KS}
            for g in c:
                s = series(est, sector, g)
                if idx(s, E, -1) is None:
                    continue
                if gname == 'not_yet_treated' and nyt[g] <= E - 1:
                    continue
                used += 1
                for k in KS:
                    if gname == 'not_yet_treated' and E + k >= nyt[g]:
                        continue   # control already has its own FC by this year
                    v = idx(s, E, k)
                    if v is not None:
                        ctrl_by_k[k].append(v)
            if used == 0:
                n_matched -= 1
                continue
            nctrl.append(used)
            st = series(est, sector, f)
            for k in KS:
                tv = idx(st, E, k)
                if tv is None or not ctrl_by_k[k]:
                    continue
                cm = mean(ctrl_by_k[k])
                per_k_t[k].append(tv)
                per_k_c[k].append(cm)
                per_k_d[k].append(tv - cm)
        res[gname] = (per_k_t, per_k_c, per_k_d)
        counts.append(dict(sector=sector, spec=label, group='treated_matched_to_' + gname, n_counties=n_matched,
                           mean_controls_per_treated=round(mean(nctrl), 1) if nctrl else '',
                           matched_state_band=how_ct['state_band'], matched_region_band=how_ct['region_band']))
        for k in KS:
            for what, vals in (('treated_for_' + gname, per_k_t[k]), ('control_' + gname, per_k_c[k]), ('diff_vs_' + gname, per_k_d[k])):
                if not vals:
                    continue
                lo, hi = boot_ci(vals, rng)
                rows.append(dict(sector=sector, spec=label, series=what, k=k, n_counties=len(vals), mean_index=round(mean(vals), 3),
                                 ci95_lo=round(lo, 3), ci95_hi=round(hi, 3)))
    counts.append(dict(sector=sector, spec=label, group='treated_with_base', n_counties=len(T)))
    return res


# ------------------------------------------------------------------ fixed-effects regression (stdlib)
def demean(y, groups, iters=200, tol=1e-10):
    """alternating-projection residualisation of y on several sets of group dummies"""
    y = list(y)
    for it in range(iters):
        delta = 0.0
        for g in groups:
            s, c = defaultdict(float), defaultdict(int)
            for v, gi in zip(y, g):
                s[gi] += v
                c[gi] += 1
            for j, gi in enumerate(g):
                m = s[gi] / c[gi]
                y[j] -= m
                delta = max(delta, abs(m))
        if delta < tol:
            break
    return y


def fe_reg(obs, fe_defs):
    """obs: list of (county, year, y, post, group_key_dict); returns beta, se (cluster by county), G, N"""
    y = [o[2] for o in obs]
    x = [o[3] for o in obs]
    groups = [[fd(o) for o in obs] for fd in fe_defs]
    yt, xt = demean(y, groups), demean(x, groups)
    sxx = sum(a * a for a in xt)
    beta = sum(a * b for a, b in zip(xt, yt)) / sxx
    e = [b - beta * a for a, b in zip(xt, yt)]
    sc = defaultdict(float)
    for o, a, ee in zip(obs, xt, e):
        sc[o[0]] += a * ee
    G, N = len(sc), len(obs)
    meat = sum(v * v for v in sc.values())
    k = len(set(groups[0])) + len(set(groups[-1]))  # approximate parameter count for small-sample factor
    adj = (G / (G - 1.0)) * ((N - 1.0) / max(N - k, 1.0))
    se = math.sqrt(adj * meat / (sxx * sxx))
    return beta, se, G, N


def pooled(sector, est, treated, nyt, never, pop, matched_union, label, rows):
    def build(sample):
        obs = []
        for f in sample:
            s = series(est, sector, f)
            if s[0] < MIN_BASE:
                continue
            E = treated.get(f)
            lim = nyt.get(f)
            for j, y in enumerate(YEARS):
                yr = YEARS[j]
                if lim is not None and yr >= lim:
                    continue
                post = 1.0 if (E is not None and yr >= E) else 0.0
                p = pop[f]
                obs.append((f, yr, math.log(s[j] + 1.0), post, (p['region'], band(p['pop2010']))))
        return obs

    specs = []
    sample_m = [f for f in list(treated) + list(nyt) + list(never) if f in matched_union]
    sample_all = list(treated) + list(nyt) + list(never)
    for sname, sample in (('matched_sample', sample_m), ('all_eligible_counties', sample_all)):
        obs = build(sample)
        if not any(o[3] for o in obs):
            continue
        for fename, fed in (('county+year FE', [lambda o: o[0], lambda o: o[1]]),
                            ('county+year FE and region x size-band x year FE', [lambda o: o[0], lambda o: (o[4], o[1])])):
            if sname == 'all_eligible_counties' and fename == 'county+year FE':
                pass
            b, se, G, N = fe_reg(obs, fed)
            rows.append(dict(sector=sector, spec=label, sample=sname, fixed_effects=fename, coef_post_fc=round(b, 5), se_cluster_county=round(se, 5),
                             ci95_lo=round(b - 1.96 * se, 5), ci95_hi=round(b + 1.96 * se, 5), pct_effect=round(100 * (math.exp(b) - 1), 3),
                             n_counties=G, n_obs=N, n_treated=len({o[0] for o in obs if o[0] in treated})))


# ------------------------------------------------------------------ main
def main():
    rng = random.Random(SEED)
    est, present = load_cbp()
    pop, byname = load_pop()
    fac = geocode_fcs(pop, byname)
    info, mapped = classify_facilities(fac)

    # county first-FC table (written for every mapped county with an FC)
    fcmap = []
    cnt = Counter(r['county_fips'] for r in mapped)
    for r in mapped:
        i = info[r['county_fips']]
        r['county_first_fc_year_strong'] = i['first'] or ''
        r['county_ambiguous'] = 'Y' if i['ambiguous'] else ''
        fcmap.append(r)
    wr('interp_retail_fc_county_map.csv', fcmap, list(fcmap[0].keys()))

    universe = [f for f in pop if not f.startswith('09') and all(y in present.get(f, ()) for y in YEARS)]
    unmatched_cbp = [f for f in info if f not in universe]

    SPECS = {
        'primary': dict(allow_other_fac=False, include_weak=False),
        'sens_allow_other_amazon_sites_in_controls': dict(allow_other_fac=True, include_weak=False),
        'sens_include_osha_bound_years': dict(allow_other_fac=False, include_weak=True),
    }
    es_rows, counts, reg_rows, pre_rows = [], [], [], []
    for label, spec in SPECS.items():
        treated, nyt, never = build_groups(spec, info, pop, universe)
        counts.append(dict(sector='all', spec=label, group='treated_first_FC_2013_2019', n_counties=len(treated)))
        counts.append(dict(sector='all', spec=label, group='not_yet_treated_first_FC_2021plus', n_counties=len(nyt)))
        counts.append(dict(sector='all', spec=label, group='never_treated_candidates', n_counties=len(never)))
        sectors = list(SECTORS) if label == 'primary' else ['retail_total', 'general_merchandise', 'placebo_food_services']
        for sector in sectors:
            res = event_study(sector, est, treated, nyt, never, pop, rng, label, es_rows, counts)
            # matched union for the regression
            T = {f: E for f, E in treated.items() if idx(series(est, sector, f), E, -1) is not None}
            mu = set(T)
            for pool in (never, set(nyt)):
                m = match(T, pool, pop)
                for t, (c, _) in m.items():
                    mu.update(c)
            pooled(sector, est, treated, nyt, never, pop, mu, label, reg_rows)
        if label == 'primary':
            # pre-trends and covariates, treated vs matched never-treated (retail total basis)
            T = {f: E for f, E in treated.items() if idx(series(est, 'retail_total', f), E, -1) is not None}
            m = match(T, never, pop)
            rows = defaultdict(list)
            for f, E in T.items():
                c, _ = m[f]
                if not c:
                    continue
                g = lambda ff: pop[ff]['pop2019'] / pop[ff]['pop2010']
                rows['pop_growth_2010_2019_ratio'].append((g(f), mean([g(x) for x in c])))
                rows['log_pop_2010'].append((math.log(pop[f]['pop2010']), mean([math.log(pop[x]['pop2010']) for x in c])))
                st, E0 = series(est, 'retail_total', f), E
                ci = [series(est, 'retail_total', x) for x in c]
                ci = [s for s in ci if idx(s, E0, -1) is not None and idx(s, E0, -3) is not None]
                if idx(st, E0, -3) is not None and ci:
                    rows['retail_est_index_at_t-3_(t-1=100)'].append((idx(st, E0, -3), mean([idx(s, E0, -3) for s in ci])))
                s10 = st[0]
                rows['retail_est_2010'].append((s10, mean([series(est, 'retail_total', x)[0] for x in c])))
            for k, v in rows.items():
                d = [a - b for a, b in v]
                lo, hi = boot_ci(d, rng)
                pre_rows.append(dict(measure=k, n_counties=len(v), treated_mean=round(mean([a for a, _ in v]), 4),
                                     matched_never_mean=round(mean([b for _, b in v]), 4), diff=round(mean(d), 4),
                                     ci95_lo=round(lo, 4), ci95_hi=round(hi, 4)))
            # by-year-cohort composition
            for E in range(2013, 2020):
                counts.append(dict(sector='all', spec=label, group='treated_cohort_%d' % E, n_counties=sum(1 for v in treated.values() if v == E)))

    wr('interp_retail_event_study.csv', es_rows, ['sector', 'spec', 'series', 'k', 'n_counties', 'mean_index', 'ci95_lo', 'ci95_hi'])
    wr('interp_retail_pooled_regression.csv', reg_rows, ['sector', 'spec', 'sample', 'fixed_effects', 'coef_post_fc', 'se_cluster_county',
                                                         'ci95_lo', 'ci95_hi', 'pct_effect', 'n_counties', 'n_obs', 'n_treated'])
    wr('interp_retail_pretrends.csv', pre_rows, ['measure', 'n_counties', 'treated_mean', 'matched_never_mean', 'diff', 'ci95_lo', 'ci95_hi'])
    cf = ['sector', 'spec', 'group', 'n_counties', 'mean_controls_per_treated', 'matched_state_band', 'matched_region_band']
    wr('interp_retail_sample_counts.csv', counts, cf)
    st = Counter(r['fips_method'] for r in mapped)
    print('FCs mapped to a county:', len(mapped), dict(st), 'counties with an FC:', len(info), 'not in CBP/pop universe:', len(unmatched_cbp), unmatched_cbp[:10])
    print('done')


if __name__ == '__main__':
    main()
