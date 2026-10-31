"""Trade-press openings: parse years, pick one press date per roster site, locate every press row.

Called by scripts/build_master.py (function build(fac_rows)); also runnable alone for a summary.
Input : data/processed/industry_trade_press_openings.csv (203 rows; subscription-free article URLs only are linked)
        Census 2020 Gazetteer places, county subdivisions and counties (data/raw/census/gaz_places, gaz_cousubs, gaz_counties) for city / county centroids.
Output: data/processed/trade_press_openings_located.csv (one row per press row: press_year, lat, lon, loc_method, loc_approx)
Returns: {facility_id: dict(press_opening_year, press_source_url, press_quality, press_confidence)}

A press year is the leading 4-digit year of opening_date, kept only if <= 2026 (later dates are planned, not openings).
Only EXACT and PROBABLE matches whose roster state equals the press row's state feed the master table.
Choice among several rows for one site: exact over probable, then high over medium over low confidence, then a row with a
public article URL, then the earliest year.
"""
import csv, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'data/processed')
MAXY = 2026
CONF = {'high': 0, 'medium': 1, 'low': 2}
QUAL = {'exact': 0, 'probable': 1}
SUFFIX = ('city', 'town', 'village', 'borough', 'municipality', 'cdp', 'township', 'city and borough', 'urban county')


def press_year(s):
    m = re.match(r'\s*(\d{4})\b', s or '')
    y = int(m.group(1)) if m else None
    return y if y and y <= MAXY else None


def _gaz(path):
    with open(path, encoding='utf-8') as fh:
        return [{k.strip(): (v or '').strip() for k, v in r.items()} for r in csv.DictReader(fh, delimiter='\t')]


def _norm(n):
    n = re.sub(r'\(.*?\)', '', n or '')
    n = re.sub(r'\b(area|city not given|city not in title)\b', '', n, flags=re.I)
    return re.sub(r'\s+', ' ', n.replace('St.', 'Saint')).strip().lower()


def centroids():
    pl, co, cs = {}, {}, {}
    for r in _gaz(os.path.join(ROOT, 'data/raw/census/gaz_places/2020_Gaz_place_national.txt')):
        nm = r['NAME'].lower()
        for s in SUFFIX:
            if nm.endswith(' ' + s):
                nm = nm[:-len(s) - 1]
                break
        k = (r['USPS'], nm)
        # prefer an incorporated place (funcstat A) over a CDP of the same name
        if k not in pl or (r['FUNCSTAT'] == 'A' and pl[k][2] != 'A'):
            pl[k] = (float(r['INTPTLAT']), float(r['INTPTLONG']), r['FUNCSTAT'])
    for r in _gaz(os.path.join(ROOT, 'data/raw/census/gaz_counties/2020_Gaz_counties_national.txt')):
        co[(r['USPS'], r['NAME'].lower())] = (float(r['INTPTLAT']), float(r['INTPTLONG']))
    for r in _gaz(os.path.join(ROOT, 'data/raw/census/gaz_cousubs/2020_Gaz_cousubs_national.txt')):
        nm = re.sub(r' (town|township|borough|city|village|plantation|location|CCD)$', '', r['NAME'], flags=re.I).lower()
        cs.setdefault((r['USPS'], nm), (float(r['INTPTLAT']), float(r['INTPTLONG'])))
    return pl, co, cs


def locate(row, pl, co, cs):
    st, city = row['state'].strip(), _norm(row['city'])
    if not st or not city:
        return None
    if city.endswith(' county'):
        c = co.get((st, city))
        return (c[0], c[1], 'county_centroid_census_gazetteer2020') if c else None
    c = pl.get((st, city))
    if c:
        return (c[0], c[1], 'city_centroid_census_gazetteer2020')
    c = cs.get((st, re.sub(r' township$', '', city)))
    if c:
        return (c[0], c[1], 'town_centroid_census_gazetteer2020')
    c = co.get((st, city + ' county'))
    return (c[0], c[1], 'county_centroid_census_gazetteer2020') if c else None


def build(fac_rows, write=True):
    with open(os.path.join(P, 'industry_trade_press_openings.csv'), newline='', encoding='utf-8') as fh:
        rows = list(csv.DictReader(fh))
    pl, co, cs = centroids()
    by_code = {}
    for f in fac_rows:
        by_code.setdefault(f['site_code'].upper(), []).append(f)
    out, cands, skipped = [], {}, []
    for i, r in enumerate(rows):
        r = dict(r)
        r['press_row_id'] = 'TP%03d' % (i + 1)
        r['press_year'] = press_year(r['opening_date']) or ''
        r['press_url'] = r['article_url'].strip()
        r['url_kind'] = 'article' if r['press_url'] else ('proquest_subscription' if r['proquest_url'] else 'none')
        r['matched_facility_id'] = ''
        loc = None
        if r['match_quality'] in QUAL and r['match_site_code']:
            fs = [f for f in by_code.get(r['match_site_code'].upper(), []) if f['state'] == r['state'] and f['lat']]
            if fs:
                f = fs[0]
                r['matched_facility_id'] = f['facility_id']
                loc = (float(f['lat']), float(f['lon']), 'roster_site_geocode')
                if r['press_year']:
                    cands.setdefault(f['facility_id'], []).append(r)
            else:
                skipped.append((r['match_site_code'], r['state']))
        if not loc:
            loc = locate(r, pl, co, cs)
        r['lat'], r['lon'], r['loc_method'] = (round(loc[0], 5), round(loc[1], 5), loc[2]) if loc else ('', '', 'none')
        r['loc_approx'] = '' if not loc else ('no' if loc[2] == 'roster_site_geocode' else 'yes')
        out.append(r)
    best = {}
    for fid, rs in cands.items():
        rs.sort(key=lambda r: (QUAL[r['match_quality']], CONF[r['confidence']], r['url_kind'] != 'article', r['press_year']))
        b = rs[0]
        best[fid] = dict(press_opening_year=b['press_year'], press_source_url=b['press_url'] or b['proquest_url'],
                         press_quality=b['match_quality'], press_confidence=b['confidence'])
    if write:
        cols = ['press_row_id', 'site_code', 'city', 'state', 'facility_type', 'sq_ft', 'announced_date', 'opening_date', 'press_year',
                'publication', 'article_date', 'article_url', 'url_kind', 'quote', 'confidence', 'evidence_basis', 'note',
                'match_site_code', 'match_quality', 'matched_facility_id', 'lat', 'lon', 'loc_method', 'loc_approx']
        with open(os.path.join(P, 'trade_press_openings_located.csv'), 'w', newline='', encoding='utf-8') as fh:
            w = csv.DictWriter(fh, fieldnames=cols, extrasaction='ignore')
            w.writeheader()
            w.writerows(out)
    n_loc = sum(1 for r in out if r['lat'] != '')
    print('trade press: %d rows, %d located (%d approximate), %d sites with a press opening year, matched rows with no roster site: %s'
          % (len(out), n_loc, sum(1 for r in out if r['loc_approx'] == 'yes'), len(best), skipped))
    return best


if __name__ == '__main__':
    with open(os.path.join(P, 'facilities.csv'), newline='', encoding='utf-8') as fh:
        build(list(csv.DictReader(fh)))
