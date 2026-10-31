"""ENVIRONMENT domain: build (a) Amazon sustainability metrics by year (transcribed from the downloaded
report PDFs; page numbers are PDF page indices of the file in data/raw/environment) and (b) eGRID helper tables.
Values were read from pdftotext -layout output of the PDFs; re-check against the PDF page before reuse.
Run: python3 -I env_02_build_amazon_sustainability_and_grid_tables.py   (needs openpyxl for part b)
"""
import csv, os, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, 'data/raw/environment'); OUT = os.path.join(ROOT, 'data/processed')
R23, R24, R25 = 'amazon_sustainability_report_2023.pdf', 'amazon_sustainability_report_2024.pdf', 'amazon_sustainability_report_2025.pdf'

# ---- (a) carbon footprint, MMT CO2e. One row per (report vintage, metric, year). Scope 2 and 3 are market-based (report footnote).
# Vintages differ because Amazon recalculated 2022+ under an updated Carbon Methodology (see 2024/2025 report table headers).
fp = []
def add(vintage, src, page, metric, years, vals, unit='MMT CO2e'):
    for y, v in zip(years, vals):
        if v is not None:
            fp.append(dict(report_vintage=vintage, metric=metric, year=y, value=v, unit=unit, source_file=src, pdf_page=page))
Y19_23 = [2019, 2020, 2021, 2022, 2023]; Y19_24 = Y19_23 + [2024]; Y19_25 = Y19_24 + [2025]
# 2023 report, PDF p11 (table: carbon intensity is g CO2e per $ gross merchandise sales)
add('2023 report', R23, 11, 'carbon_intensity_g_per_usd_GMS', Y19_23, [122.8, 102.7, 100.8, 93.0, 80.8], 'g CO2e per $ GMS')
add('2023 report', R23, 11, 'scope1_direct', Y19_23, [5.76, 9.62, 12.11, 13.32, 14.27])
add('2023 report', R23, 11, 'scope1_fossil_fuels', Y19_23, [5.57, 9.37, 11.89, 12.96, 14.00])
add('2023 report', R23, 11, 'scope1_refrigerants', Y19_23, [0.19, 0.25, 0.22, 0.36, 0.27])
add('2023 report', R23, 11, 'scope2_purchased_electricity_market', Y19_23, [5.50, 5.27, 4.07, 3.14, 2.79])
add('2023 report', R23, 11, 'scope3_indirect', Y19_23, [39.91, 45.75, 55.36, 54.28, 51.76])
add('2023 report', R23, 11, 'total_footprint', Y19_23, [51.17, 60.64, 71.54, 70.74, 68.82])
# 2024 report, PDF p50 (carbon intensity row label present but values not captured by text extraction -> omitted)
add('2024 report', R24, 50, 'scope1_direct', Y19_24, [5.76, 9.62, 12.11, 13.02, 14.22, 15.13])
add('2024 report', R24, 50, 'scope1_fossil_fuels', Y19_24, [5.57, 9.37, 11.89, 12.60, 13.85, 14.80])
add('2024 report', R24, 50, 'scope1_refrigerants', Y19_24, [0.19, 0.25, 0.22, 0.42, 0.37, 0.33])
add('2024 report', R24, 50, 'scope2_purchased_electricity_market', Y19_24, [5.50, 5.27, 4.07, 3.06, 2.76, 2.80])
add('2024 report', R24, 50, 'scope3_indirect', Y19_24, [39.91, 45.75, 55.36, 49.02, 47.40, 50.32])
add('2024 report', R24, 50, 'total_footprint', Y19_24, [51.17, 60.64, 71.54, 65.10, 64.38, 68.25])
# 2025 report, PDF p46 (carbon intensity is g CO2e per $ of revenue here, a different denominator from the 2023 report)
add('2025 report', R25, 46, 'carbon_intensity_g_per_usd_revenue', Y19_25, [182.4, 157.1, 152.3, 127.2, 113.6, 109.0, 112.8], 'g CO2e per $ revenue')
add('2025 report', R25, 46, 'scope1_direct', Y19_25, [5.76, 9.62, 12.11, 13.02, 14.22, 15.13, 15.37])
add('2025 report', R25, 46, 'scope1_fossil_fuels', Y19_25, [5.57, 9.37, 11.89, 12.60, 13.85, 14.80, 15.00])
add('2025 report', R25, 46, 'scope1_refrigerants', Y19_25, [0.19, 0.25, 0.22, 0.42, 0.37, 0.33, 0.37])
add('2025 report', R25, 46, 'scope2_purchased_electricity_market', Y19_25, [5.50, 5.27, 4.07, 3.06, 2.76, 2.80, 3.74])
add('2025 report', R25, 46, 'scope3_indirect', Y19_25, [39.91, 45.75, 55.36, 49.29, 48.30, 51.62, 61.74])
add('2025 report', R25, 46, 'total_footprint', Y19_25, [51.17, 60.64, 71.54, 65.37, 65.28, 69.55, 80.85])
# Scope 3 sub-categories, 2025 report p46 (2022-2025 only; 2022 Capital goods etc. as printed)
add('2025 report', R25, 46, 'scope3_capital_goods', [2022, 2023, 2024, 2025], [10.39, 10.03, 11.82, 16.96])
add('2025 report', R25, 46, 'scope3_upstream_transport_distribution', [2022, 2023, 2024, 2025], [10.10, 8.88, 9.61, 10.87])
add('2025 report', R25, 46, 'scope3_downstream_transport_distribution', [2022, 2023, 2024, 2025], [3.31, 3.52, 3.73, 4.01])
add('2025 report', R25, 46, 'scope3_employee_commuting', [2022, 2023, 2024, 2025], [2.93, 2.70, 2.76, 2.98])
add('2025 report', R25, 46, 'scope3_fuel_energy_related', [2022, 2023, 2024, 2025], [4.40, 5.03, 4.55, 5.70])
with open(os.path.join(OUT, 'amazon_carbon_footprint_by_report_vintage.csv'), 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=list(fp[0])); w.writeheader(); w.writerows(fp)

# ---- other sustainability facts (each is a single cited statement)
facts = [
 (2019, 'renewable_electricity_matched_pct', 42, '%', 'Energy Digital summary of 2022 report (secondary; not in the PDFs downloaded)', 'https://energydigital.com/articles/amazons-sustainability-report-outlines-the-future-of-energy', 'secondary'),
 (2021, 'renewable_electricity_matched_pct', 85, '%', 'Energy Digital summary of 2022 report (secondary)', 'https://energydigital.com/articles/amazons-sustainability-report-outlines-the-future-of-energy', 'secondary'),
 (2022, 'renewable_electricity_matched_pct', 90, '%', 'Amazon 2023 report goals table p6 ("90% matched | 100% matched"); also aboutamazon.com 2022 report page', R23 + ' p6', 'primary'),
 (2023, 'renewable_electricity_matched_pct', 100, '%', 'Amazon 2023 report p6, p12, p24 ("matched 100% ... achieved ... 2023")', R23 + ' p6/p12/p24', 'primary'),
 (2024, 'renewable_electricity_matched_pct', 100, '%', 'Amazon 2024 report p14', R24 + ' p14', 'primary'),
 (2025, 'renewable_electricity_matched_pct', 100, '%', 'Amazon 2025 report p11', R25 + ' p11', 'primary'),
 (2023, 'renewable_portfolio_capacity_GW', 28, 'GW', 'Amazon 2023 report p12 (up from 20 GW in 2022)', R23 + ' p12', 'primary'),
 (2024, 'renewable_portfolio_capacity_GW', 34, 'GW', 'Amazon 2024 report p14 (carbon-free energy capacity; 91,000 GWh/yr)', R24 + ' p14', 'primary'),
 (2025, 'carbon_free_energy_GWh', 131000, 'GWh', 'Amazon 2025 report p10', R25 + ' p10', 'primary'),
 (2024, 'us_renewable_projects_count', 281, 'projects', 'Amazon 2024 report p50 table (United States, 20,104 MW, 281 projects incl. in development/construction)', R24 + ' p50', 'primary'),
 (2025, 'us_carbon_free_projects_announced_30_states', 291, 'projects', 'Amazon 2025 report p11: 291 projects across 30 states, 25.6 GW expected capacity (US)', R25 + ' p11', 'primary'),
 (2022, 'electric_delivery_vans_global', 2600, 'vans', 'Amazon 2023 report p6 goals table (2.6K+); NOTE the 2024 report p6 shows 7K+ for the same year - discrepancy unresolved', R23 + ' p6', 'primary-conflicting'),
 (2022, 'electric_delivery_vans_global_alt', 7000, 'vans', 'Amazon 2024 report p6 goals table (7K+)', R24 + ' p6', 'primary-conflicting'),
 (2023, 'electric_delivery_vans_global', 19000, 'vans', 'Amazon 2023 report p17 ("19,000 electric delivery vans around the world"); 2024 report p6 also 19K+', R23 + ' p17', 'primary'),
 (2023, 'electric_delivery_vans_us_rivian', 11800, 'vans', 'Amazon 2023 report p17 (U.S. fleet 11,800 Rivian vans, up from 2,600 in 2022)', R23 + ' p17', 'primary'),
 (2024, 'electric_delivery_vans_global', 31400, 'vans', 'Amazon 2024 report p9, p12; >24,000 from Rivian', R24 + ' p9/p12', 'primary'),
 (2024, 'packages_delivered_by_EV_billion', 1.5, 'billion', 'Amazon 2024 report p12', R24 + ' p12', 'primary'),
 (2025, 'electric_delivery_vans_global', 52700, 'vans', 'Amazon 2025 report p5/p7/p9: 52.7K+; 37,400 US, 10,900 Europe, 4,400 India; fleet +68% in 2025', R25 + ' p9', 'primary'),
 (2025, 'electric_delivery_vans_us', 37400, 'vans', 'Amazon 2025 report p9', R25 + ' p9', 'primary'),
 (2025, 'packages_delivered_by_EV_billion', 2.4, 'billion', 'Amazon 2025 report p9', R25 + ' p9', 'primary'),
 (2023, 'single_use_plastic_packaging_used_MT_global', 88698, 'metric tons', 'Amazon 2025 report p22 table (North America 83,513)', R25 + ' p22', 'primary'),
 (2024, 'single_use_plastic_packaging_used_MT_global', 74137, 'metric tons', 'Amazon 2025 report p22 table (North America 68,679)', R25 + ' p22', 'primary'),
 (2025, 'single_use_plastic_packaging_used_MT_global', 74073, 'metric tons', 'Amazon 2025 report p22 table (North America 68,196)', R25 + ' p22', 'primary'),
 (2023, 'pct_NA_shipments_containing_plastic', 65, '%', 'Amazon 2025 report p22', R25 + ' p22', 'primary'),
 (2024, 'pct_NA_shipments_containing_plastic', 37, '%', 'Amazon 2025 report p22', R25 + ' p22', 'primary'),
 (2025, 'pct_NA_shipments_containing_plastic', 27, '%', 'Amazon 2025 report p22', R25 + ' p22', 'primary'),
 (2025, 'single_use_plastic_avoided_since_2020_MT', 223616, 'metric tons', 'Amazon 2025 report p22 (cumulative since 2020; North America 149,096)', R25 + ' p22', 'primary'),
 (2025, 'packaging_material_avoided_since_2015_million_MT', 5.4, 'million metric tons', 'Amazon 2025 report p22 (North America and Europe)', R25 + ' p22', 'primary'),
 (2023, 'per_shipment_packaging_weight_reduction_since_2015_pct', 43, '%', 'Amazon 2023 report p12', R23 + ' p12', 'primary'),
 (2025, 'NA_fulfillment_centers_shipping_no_plastic_pct', 52, '%', 'Amazon 2025 report p22', R25 + ' p22', 'primary'),
]
with open(os.path.join(OUT, 'amazon_sustainability_other_metrics.csv'), 'w', newline='') as fh:
    w = csv.writer(fh); w.writerow(['year', 'metric', 'value', 'unit', 'basis_and_note', 'source', 'source_type']); w.writerows(facts)

# ---- US grid average series (lb/MWh). CO2 only for 2007-2014 (from eGRID GHGOutputRates PDFs); CO2e from 2016.
us = [(2007, 'CO2', 1293.05, 'eGRID2007_GHGOutputRates.pdf (U.S. total output)'), (2009, 'CO2', 1216.18, 'eGRID2009_GHGOutputRates.pdf'),
      (2010, 'CO2', 1232.35, 'eGRID2010_GHGOutputRates.pdf'), (2012, 'CO2', 1136.53, 'eGRID2012_GHGOutputRates.pdf'),
      (2014, 'CO2', 1122.9, 'eGRID2014_GHGOutputRates_v2.pdf'), (2016, 'CO2e', 1004.167, 'eGRID2016_summarytables.xlsx Table 1'),
      (2018, 'CO2e', 952.877, 'egrid2018_summary_tables.xlsx Table 1'), (2019, 'CO2e', 889.214, 'egrid2019_summary_tables.xlsx'),
      (2020, 'CO2e', 822.621, 'egrid2020_summary_tables.xlsx'), (2021, 'CO2e', 857.019, 'eGRID2021_summary_tables.xlsx'),
      (2022, 'CO2e', 827.52, 'egrid2022_summary_tables.xlsx'), (2023, 'CO2e', 770.884, 'egrid2023_data_rev2.xlsx sheet US23 USC2ERTA')]
with open(os.path.join(OUT, 'egrid_us_average_output_rate_by_year.csv'), 'w', newline='') as fh:
    w = csv.writer(fh); w.writerow(['egrid_data_year', 'gas', 'lb_per_MWh_total_output', 'source']); w.writerows(us)

# ---- (b) eGRID 2023 plant table (for nearest-plant subregion lookup) and state -> subregion shares
import openpyxl
wb = openpyxl.load_workbook(os.path.join(RAW, 'egrid2023_data_rev2.xlsx'), read_only=True, data_only=True)
R = list(wb['PLNT23'].iter_rows(values_only=True)); codes = R[1]
ix = {c: i for i, c in enumerate(codes)}
plants, share = [], collections.defaultdict(lambda: collections.defaultdict(float))
for r in R[2:]:
    if not r[0]: continue
    st, sr, gen = r[ix['PSTATABB']], r[ix['SUBRGN']], r[ix['PLNGENAN']]
    lat, lon = r[ix['LAT']], r[ix['LON']]
    if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)) or sr in (None, '--'): continue
    plants.append((st, sr, round(lat, 4), round(lon, 4)))
    if isinstance(gen, (int, float)) and gen > 0: share[st][sr] += gen
with open(os.path.join(OUT, 'egrid2023_plant_locations_subregion.csv'), 'w', newline='') as fh:
    w = csv.writer(fh); w.writerow(['state', 'subregion', 'lat', 'lon']); w.writerows(plants)
with open(os.path.join(OUT, 'egrid2023_state_to_subregion_generation_share.csv'), 'w', newline='') as fh:
    w = csv.writer(fh); w.writerow(['state', 'subregion', 'share_of_state_net_generation'])
    for st in sorted(share):
        tot = sum(share[st].values())
        for sr, g in sorted(share[st].items(), key=lambda kv: -kv[1]):
            w.writerow([st, sr, round(g / tot, 4)])
print(len(fp), 'footprint rows;', len(facts), 'facts;', len(plants), 'plants')
