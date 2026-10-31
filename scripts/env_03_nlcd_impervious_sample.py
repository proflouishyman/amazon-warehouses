"""ENVIRONMENT domain: sample NLCD impervious-surface percent around facility coordinates.
Service: MRLC GeoServer WMS GetFeatureInfo, layer NLCD_<year>_Impervious_L48 (years 2001-2021 available on 2026-10-31).
The service returns the raster value as PALETTE_INDEX (observed 0 for forest/farmland and ~91-96 at an airport apron/downtown, i.e. percent impervious per 30 m pixel).
Method: 3x3 grid of points at +/-0.0006 deg (~65 m) around the coordinate; report mean and max percent. This is a POINT SAMPLE of the
surroundings, not the parcel footprint; it understates impervious area for large sites (>500 ft across) and includes neighbouring parcels.
Usage: python3 -I env_03_nlcd_impervious_sample.py in.csv out.csv [year]     (in.csv needs columns: lat, lon; other columns are kept)
"""
import csv, json, sys, time, urllib.request
def sample(lat, lon, year=2021):
    vals = []
    for dy in (-0.0006, 0, 0.0006):
        for dx in (-0.0006, 0, 0.0006):
            x, y, d = lon + dx, lat + dy, 0.0005
            url = ('https://www.mrlc.gov/geoserver/mrlc_display/NLCD_%d_Impervious_L48/wms?service=WMS&version=1.1.1&request=GetFeatureInfo'
                   '&layers=NLCD_%d_Impervious_L48&query_layers=NLCD_%d_Impervious_L48&info_format=application/json&srs=EPSG:4326'
                   '&bbox=%f,%f,%f,%f&width=101&height=101&x=50&y=50') % (year, year, year, x - d, y - d, x + d, y + d)
            for attempt in range(3):
                try:
                    j = json.load(urllib.request.urlopen(url, timeout=30)); break
                except Exception:
                    time.sleep(2); j = None
            if j and j['features']:
                vals.append(j['features'][0]['properties'].get('PALETTE_INDEX'))
    vals = [v for v in vals if v is not None]
    return (round(sum(vals) / len(vals), 1), max(vals), len(vals)) if vals else (None, None, 0)
if __name__ == '__main__':
    src, dst = sys.argv[1], sys.argv[2]; yr = int(sys.argv[3]) if len(sys.argv) > 3 else 2021
    rows = list(csv.DictReader(open(src))); out = []
    for r in rows:
        m, mx, n = sample(float(r['lat']), float(r['lon']), yr)
        r.update(nlcd_year=yr, impervious_pct_mean_3x3=m, impervious_pct_max_3x3=mx, nlcd_points_ok=n); out.append(r)
    with open(dst, 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    print(len(out), 'rows ->', dst)
