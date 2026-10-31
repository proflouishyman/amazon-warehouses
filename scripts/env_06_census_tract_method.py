"""ENVIRONMENT domain: Census ACS tract demographics near facilities (METHOD + helpers; the integrator joins to facilities).
Step 1 (tested 2026-10-31, no key needed): coordinates -> 2020 tract GEOID with the Census Geocoder
        https://geocoding.geo.census.gov/geocoder/geographies/coordinates?x=<lon>&y=<lat>&benchmark=Public_AR_Current&vintage=Current_Current&format=json
Step 2 (NOT run: the Census API returned "missing key"; set env var CENSUS_API_KEY, free at api.census.gov/data/key_signup.html):
        ACS 5-year detailed tables by tract, one call per state:
        https://api.census.gov/data/<vintage>/acs/acs5?get=NAME,<VARS>&for=tract:*&in=state:<FIPS>&key=...
        Variables (labels verified against the 2023 variables.json, see data/raw/environment/acs5_2023_variables_used.json):
        B01003_001E pop; B03002_001E/003E/004E/006E/012E race-ethnicity; B19013_001E median HH income; B17001_001E/002E poverty;
        B25003_001E/003E renters; B23025_003E/005E labor force/unemployed; B08201_001E/002E zero-vehicle households.
Step 3 (neighbourhood, optional): tract internal-point centroids from the Census Gazetteer
        https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2024_Gazetteer/2024_Gaz_tracts_national.zip
        take all tracts whose centroid is within R km (suggest 1.6 km = 1 mile and 5 km) of the facility and compute
        population-weighted shares (sum numerator / sum denominator, never a mean of tract percentages).
Caveats: ACS 5-year tract estimates carry margins of error (request the _M columns); median income cannot be pooled, report the
        value for the containing tract only; tract centroid selection ignores that a tract may be mostly non-residential
        (warehouse tracts often have tiny populations - flag pop < 500); 2020 tract geography applies to ACS vintages 2020+.
Usage (step 1): python3 -I env_06_census_tract_method.py in.csv out.csv     (columns lat, lon)
"""
import csv, json, sys, time, urllib.request
def tract(lat, lon):
    url = ('https://geocoding.geo.census.gov/geocoder/geographies/coordinates?x=%f&y=%f&benchmark=Public_AR_Current'
           '&vintage=Current_Current&format=json') % (lon, lat)
    for _ in range(3):
        try:
            g = json.load(urllib.request.urlopen(url, timeout=40))['result']['geographies']
            t = g['Census Tracts'][0]; return t['GEOID'], t['STATE'] + t['COUNTY']
        except Exception:
            time.sleep(2)
    return None, None
if __name__ == '__main__':
    rows = list(csv.DictReader(open(sys.argv[1])))
    for r in rows:
        r['tract_geoid_2020'], r['county_fips'] = tract(float(r['lat']), float(r['lon']))
    with open(sys.argv[2], 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print(len(rows), 'rows ->', sys.argv[2])
