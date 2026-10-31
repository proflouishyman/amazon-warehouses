"""Geography QA for data/processed/facilities.csv (run by build_master.py, or alone: python3 -I scripts/facilities_08_check_geo.py).

For every row with coordinates, two independent tests:
  1. point-in-state: the geocoded point must fall inside the polygon of the row's state in the Census 2020 cartographic
     state boundary file (cb_2020_us_state_20m, 1:20M, so coastlines and borders are generalised by up to a few km).
     A point outside its state's polygon but within TOL_KM of it passes as 'near_border'; farther fails.
  2. zip-to-state: the row's ZIP must belong to the row's state in the Census 2020 ZCTA-county relationship file
     (a ZIP that straddles a border passes if any overlapping county is in the state).
Rows with no state, no ZIP, or no coordinates are reported too. Output: data/processed/facility_geo_check.csv
(every row that is not 'ok') and facility_geo_check_summary.json. check_rows(rows) is importable.
"""
import csv, json, math, os, re, struct, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'data/processed')
SHP = os.path.join(ROOT, 'data/raw/census/cb_state_20m/cb_2020_us_state_20m')
REL = os.path.join(ROOT, 'data/raw/facilities/census_ref/rel.txt')
TOL_KM = 15.0
FIPS_ST = {'01': 'AL', '02': 'AK', '04': 'AZ', '05': 'AR', '06': 'CA', '08': 'CO', '09': 'CT', '10': 'DE', '11': 'DC', '12': 'FL', '13': 'GA',
           '15': 'HI', '16': 'ID', '17': 'IL', '18': 'IN', '19': 'IA', '20': 'KS', '21': 'KY', '22': 'LA', '23': 'ME', '24': 'MD', '25': 'MA',
           '26': 'MI', '27': 'MN', '28': 'MS', '29': 'MO', '30': 'MT', '31': 'NE', '32': 'NV', '33': 'NH', '34': 'NJ', '35': 'NM', '36': 'NY',
           '37': 'NC', '38': 'ND', '39': 'OH', '40': 'OK', '41': 'OR', '42': 'PA', '44': 'RI', '45': 'SC', '46': 'SD', '47': 'TN', '48': 'TX',
           '49': 'UT', '50': 'VT', '51': 'VA', '53': 'WA', '54': 'WV', '55': 'WI', '56': 'WY', '72': 'PR'}


def read_states():
    """Minimal ESRI shapefile (polygon) + dbf reader: returns {state_abbr: [ring, ...]} with ring = [(lon, lat), ...]."""
    with open(SHP + '.dbf', 'rb') as fh:
        d = fh.read()
    nrec, hlen, rlen = struct.unpack('<xxxxIHH', d[:12])
    fields, off = [], 32
    while d[off] != 0x0D:
        fields.append((d[off:off + 11].split(b'\0')[0].decode(), d[off + 16])); off += 32
    names = []
    for i in range(nrec):
        rec = d[hlen + i * rlen: hlen + (i + 1) * rlen]
        p, row = 1, {}
        for n, ln in fields:
            row[n] = rec[p:p + ln].decode('latin-1').strip(); p += ln
        names.append(row['STUSPS'])
    with open(SHP + '.shp', 'rb') as fh:
        s = fh.read()
    pos, out = 100, collections.defaultdict(list)
    for i in range(nrec):
        clen = struct.unpack('>I', s[pos + 4:pos + 8])[0] * 2
        c = s[pos + 8:pos + 8 + clen]; pos += 8 + clen
        if struct.unpack('<i', c[:4])[0] != 5:
            continue
        nparts, npts = struct.unpack('<ii', c[36:44])
        parts = list(struct.unpack('<%di' % nparts, c[44:44 + 4 * nparts])) + [npts]
        pts = struct.unpack('<%dd' % (2 * npts), c[44 + 4 * nparts: 44 + 4 * nparts + 16 * npts])
        for a, b in zip(parts, parts[1:]):
            out[names[i]].append([(pts[2 * k], pts[2 * k + 1]) for k in range(a, b)])
    return out


def inside(ring, x, y):
    c = False
    j = len(ring) - 1
    for i in range(len(ring)):
        xi, yi = ring[i]; xj, yj = ring[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            c = not c
        j = i
    return c


def dist_km(rings, x, y):
    best = 1e9
    kx = 111.32 * math.cos(math.radians(y)); ky = 110.57
    for ring in rings:
        for (x1, y1), (x2, y2) in zip(ring, ring[1:]):
            dx, dy = (x2 - x1) * kx, (y2 - y1) * ky
            px, py = (x - x1) * kx, (y - y1) * ky
            L = dx * dx + dy * dy
            t = 0 if L == 0 else max(0, min(1, (px * dx + py * dy) / L))
            best = min(best, math.hypot(px - t * dx, py - t * dy))
    return best


def zip_states():
    zs = collections.defaultdict(set)
    with open(REL, encoding='utf-8-sig') as fh:
        for l in fh:
            a = l.rstrip('\n').split('|')
            if a[0] == 'OID_ZCTA5_20' or not a[1] or not a[9]:
                continue
            zs[a[1]].add(FIPS_ST.get(a[9][:2]))
    return zs


def check_rows(rows):
    """rows: list of dicts with site_code,state,zip,lat,lon. Returns {index: (status, detail)}; status 'ok' or a failure/flag code."""
    states = read_states(); zs = zip_states()
    boxes = {s: [(min(p[0] for p in r), min(p[1] for p in r), max(p[0] for p in r), max(p[1] for p in r)) for r in rings] for s, rings in states.items()}
    res = {}
    for i, r in enumerate(rows):
        st, z = (r.get('state') or '').strip(), re.sub(r'\D', '', r.get('zip') or '')[:5]
        try:
            la, lo = float(r['lat']), float(r['lon'])
        except (KeyError, ValueError):
            res[i] = ('no_coordinates', 'row has no coordinates'); continue
        if not st:
            res[i] = ('no_state', 'row has no state'); continue
        if st not in states:
            res[i] = ('state_not_us', 'state %s is not a US state in the boundary file' % st); continue
        msgs, status = [], 'ok'
        ins = any(b[0] <= lo <= b[2] and b[1] <= la <= b[3] and inside(ring, lo, la) for b, ring in zip(boxes[st], states[st]))
        if not ins:
            d = dist_km(states[st], lo, la)
            if d <= TOL_KM:
                status = 'near_border'; msgs.append('point %.1f km outside %s polygon (generalised 1:20M boundary)' % (d, st))
            else:
                status = 'point_outside_state'
                where = [s for s, rg in states.items() if any(b[0] <= lo <= b[2] and b[1] <= la <= b[3] and inside(ring, lo, la) for b, ring in zip(boxes[s], rg))]
                msgs.append('point is %.0f km from %s; falls in %s' % (d, st, ','.join(where) or 'no state polygon'))
        if z and z in zs and st not in zs[z]:
            status = 'zip_state_mismatch' if status in ('ok', 'near_border') else status
            msgs.append('ZIP %s belongs to %s, row says %s' % (z, '/'.join(sorted(x for x in zs[z] if x)), st))
        elif z and z not in zs:
            if status == 'ok':
                status = 'zip_unknown'
            msgs.append('ZIP %s not in Census 2020 ZCTA file' % z)
        elif not z:
            if status == 'ok':
                status = 'no_zip'
            msgs.append('row has no ZIP')
        res[i] = (status, '; '.join(msgs))
    return res


if __name__ == '__main__':
    with open(os.path.join(P, 'facilities.csv'), newline='', encoding='utf-8') as fh:
        rows = list(csv.DictReader(fh))
    res = check_rows(rows)
    cnt = collections.Counter(v[0] for v in res.values())
    bad = [dict(facility_id=rows[i]['facility_id'], site_code=rows[i]['site_code'], state=rows[i]['state'], zip=rows[i]['zip'], city=rows[i]['city'],
                lat=rows[i]['lat'], lon=rows[i]['lon'], geo_method=rows[i]['geo_method'], status=v[0], detail=v[1])
           for i, v in res.items() if v[0] != 'ok']
    with open(os.path.join(P, 'facility_geo_check.csv'), 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, ['facility_id', 'site_code', 'state', 'zip', 'city', 'lat', 'lon', 'geo_method', 'status', 'detail'])
        w.writeheader(); w.writerows(bad)
    hard = {'point_outside_state', 'zip_state_mismatch', 'no_state', 'state_not_us'}
    summ = dict(rows=len(rows), counts=dict(cnt), failures_hard=sum(v for k, v in cnt.items() if k in hard))
    with open(os.path.join(P, 'facility_geo_check_summary.json'), 'w') as fh:
        json.dump(summ, fh, indent=1)
    print(json.dumps(summ))
