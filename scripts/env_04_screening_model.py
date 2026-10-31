"""ENVIRONMENT domain: facility-level screening model (ESTIMATES, with low/central/high ranges).

Usage:
  python3 -I env_04_screening_model.py facilities.csv out.csv
  python3 -I env_04_screening_model.py --example out.csv        (three 1,000,000 sq ft reference buildings)
facilities.csv columns: facility_id, state, sqft, [lat, lon], [year] (calendar year to evaluate, default 2023).

Method (all parameters in PARAMS; every one is an assumption or a cited value, see data/notes/environment.md):
  electricity_kWh   = sqft x kWh/sqft                       (CBECS 2018 warehouse: p50 3.4 | mean 5.8 | all-commercial mean 12.6)
  grid_tCO2e        = electricity_kWh/1000 x eGRID subregion CO2e lb/MWh x 0.45359237/1000
  gas_tCO2e         = sqft x kBtu/sqft x 53.06 kg/mmBtu       (CBECS 11.38 kBtu/sqft derived; EPA Hub factor); x0.5 | x1 | x2
  Trucks: NOT ESTIMATED. The earlier truck trip rates came from search snippets; the one primary source found (SCAQMD 2014
  High Cube Warehouse Truck Trip Study) excludes e-commerce and parcel warehouses, so it does not describe fulfillment
  centers. No per-site truck columns are produced (see data/notes/environment.md).
Grid factor: eGRID subregion of nearest eGRID2023 plant (if lat/lon) else the state's largest-generation subregion.
Year handling: 2018-2023 use that year's subregion value; >2023 uses 2023; <2018 scales the 2023 subregion value by
(US average of that year / US average of 2023) - an estimate, flagged in the output column grid_factor_method.
"""
import csv, math, os, sys, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); P = os.path.join(ROOT, 'data/processed')
LB_TO_T = 0.45359237 / 1000
PARAMS = {  # (low, central, high)
 'elec_kwh_per_sqft': (3.4, 5.8, 12.6),
 'gas_kbtu_per_sqft': (11.38 * 0.5, 11.38, 11.38 * 2),
 'gas_kg_co2_per_mmbtu': 53.06,
 'operating_days': 365,
}
def rd(name): return list(csv.DictReader(open(os.path.join(P, name))))
sub = collections.defaultdict(dict)
for r in rd('egrid_subregion_rates_2018_2023.csv'): sub[r['subregion']][int(r['year'])] = float(r['co2e_lb_mwh'])
us = {int(r['egrid_data_year']): float(r['lb_per_MWh_total_output']) for r in rd('egrid_us_average_output_rate_by_year.csv')}
plants = [(float(r['lat']), float(r['lon']), r['subregion']) for r in rd('egrid2023_plant_locations_subregion.csv')]
dom = {}
for r in rd('egrid2023_state_to_subregion_generation_share.csv'):
    dom.setdefault(r['state'], r['subregion'])   # file is sorted by descending share within state

def hav(a, b, c, d):
    p = math.pi / 180; x = math.sin((c - a) * p / 2) ** 2 + math.cos(a * p) * math.cos(c * p) * math.sin((d - b) * p / 2) ** 2
    return 12742 * math.asin(math.sqrt(x))
def subregion(lat, lon, state):
    if lat is not None and lon is not None:
        return min(plants, key=lambda p: hav(lat, lon, p[0], p[1]))[2], 'nearest_plant'
    return dom.get(state), 'state_dominant'
def grid_factor(sr, year):
    s = sub[sr]
    if year > 2023: year = 2023
    if year in s: return s[year], 'egrid_%d_subregion' % year
    if year < 2018:
        usy = us.get(year) or us[min(us, key=lambda k: abs(k - year))]
        return s[2023] * usy / us[2023], 'scaled_from_2023_by_US_avg_ratio(est)'
    return s[2023], 'egrid_2023'

def model(row):
    sqft = float(row['sqft']); year = int(row.get('year') or 2023)
    lat = float(row['lat']) if row.get('lat') else None; lon = float(row['lon']) if row.get('lon') else None
    sr, how = subregion(lat, lon, row.get('state')); f, fm = grid_factor(sr, year)
    out = dict(row); out.update(subregion=sr, subregion_method=how, grid_lb_co2e_per_mwh=round(f, 1), grid_factor_method=fm)
    for i, tag in enumerate(('low', 'central', 'high')):
        kwh = sqft * PARAMS['elec_kwh_per_sqft'][i]
        out['elec_kwh_' + tag] = round(kwh)
        out['grid_tco2e_' + tag] = round(kwh / 1000 * f * LB_TO_T, 1)
        out['gas_tco2e_' + tag] = round(sqft * PARAMS['gas_kbtu_per_sqft'][i] / 1000 * PARAMS['gas_kg_co2_per_mmbtu'] / 1000, 1)
    out['estimate_flag'] = 'ESTIMATE: screening model, not measured; see data/notes/environment.md'
    return out

if __name__ == '__main__':
    if sys.argv[1] == '--example':
        rows = [dict(facility_id='REFERENCE_%s_1Msqft' % s, state=st, sqft=1000000, lat=lat, lon=lon, year=2023)
                for s, st, lat, lon in (('VA_SRVC', 'VA', 38.9, -77.4), ('CA_CAMX', 'CA', 34.0, -117.4), ('OH_RFCW', 'OH', 40.0, -83.0))]
        dst = sys.argv[2]
    else:
        rows = list(csv.DictReader(open(sys.argv[1]))); dst = sys.argv[2]
    res = [model(r) for r in rows]
    with open(dst, 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(res[0])); w.writeheader(); w.writerows(res)
    print(len(res), 'rows ->', dst)
