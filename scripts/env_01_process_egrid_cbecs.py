"""ENVIRONMENT domain: process eGRID (2018-2023) and CBECS 2018 raw downloads to CSV.
Run with: python3 -I env_01_process_egrid_cbecs.py  (needs openpyxl)
"""
import csv, os, openpyxl
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, 'data/raw/environment'); OUT = os.path.join(ROOT, 'data/processed')

def rows(path, sheet):
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    return list(wb[sheet].iter_rows(values_only=True))

sub, st = [], []
files = {2018:'egrid2018_summary_tables.xlsx',2019:'egrid2019_summary_tables.xlsx',2020:'egrid2020_summary_tables.xlsx',
         2021:'eGRID2021_summary_tables.xlsx',2022:'egrid2022_summary_tables.xlsx'}
for yr, f in files.items():
    for r in rows(os.path.join(RAW, f), 'Table 1'):
        r = tuple(x for x in r if x is not None)  # drop empty leading/trailing cells (layout differs by year)
        if r and len(str(r[0])) == 4 and len(r) > 8 and isinstance(r[2], (int, float)):
            sub.append(dict(year=yr, subregion=r[0], name=r[1], co2_lb_mwh=r[2], ch4_lb_mwh=r[3], n2o_lb_mwh=r[4], co2e_lb_mwh=r[5],
                            nox_lb_mwh=r[6], nox_ozone_lb_mwh=r[7], so2_lb_mwh=r[8], source=f))
    for r in rows(os.path.join(RAW, f), 'Table 3'):
        r = tuple(x for x in r if x is not None)
        if r and len(str(r[0])) == 2 and len(r) > 7 and isinstance(r[1], (int, float)):
            st.append(dict(year=yr, state=r[0], co2_lb_mwh=r[1], ch4_lb_mwh=r[2], n2o_lb_mwh=r[3], co2e_lb_mwh=r[4], nox_lb_mwh=r[5],
                           nox_ozone_lb_mwh=r[6], so2_lb_mwh=r[7], source=f))
# 2023 from full data workbook (column names by eGRID code)
f23 = 'egrid2023_data_rev2.xlsx'
def tbl(sheet):
    R = rows(os.path.join(RAW, f23), sheet); codes = R[1]
    return [dict(zip(codes, r)) for r in R[2:] if r[0]]
for d in tbl('SRL23'):
    sub.append(dict(year=2023, subregion=d['SUBRGN'], name=d['SRNAME'], co2_lb_mwh=d['SRCO2RTA'], ch4_lb_mwh=d['SRCH4RTA'], n2o_lb_mwh=d['SRN2ORTA'],
                    co2e_lb_mwh=d['SRC2ERTA'], nox_lb_mwh=d['SRNOXRTA'], nox_ozone_lb_mwh=d['SRNOXRTO'], so2_lb_mwh=d['SRSO2RTA'], source=f23))
for d in tbl('ST23'):
    st.append(dict(year=2023, state=d['PSTATABB'], co2_lb_mwh=d['STCO2RTA'], ch4_lb_mwh=d['STCH4RTA'], n2o_lb_mwh=d['STN2ORTA'],
                   co2e_lb_mwh=d['STC2ERTA'], nox_lb_mwh=d['STNOXRTA'], nox_ozone_lb_mwh=d['STNOXRTO'], so2_lb_mwh=d['STSO2RTA'], source=f23))
for name, data in (('egrid_subregion_rates_2018_2023.csv', sub), ('egrid_state_rates_2018_2023.csv', st)):
    data = [d for d in data if isinstance(d['co2e_lb_mwh'], (int, float))]
    with open(os.path.join(OUT, name), 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(data[0])); w.writeheader(); w.writerows(data)
    print(name, len(data))

# CBECS 2018 warehouse intensities
def cb(f):
    return rows(os.path.join(RAW, f), 'Sheet1' if False else openpyxl.load_workbook(os.path.join(RAW, f), read_only=True).sheetnames[0])
def find(R, label):
    return next(r for r in R if r[0] and str(r[0]).strip().startswith(label) and r[1] not in ('', None))
c1, c14, c13 = cb('cbecs2018_c1.xlsx'), cb('cbecs2018_c14.xlsx'), cb('cbecs2018_c13.xlsx')
w1, a1 = find(c1, 'Warehouse and storage'), find(c1, 'All buildings')
w14, a14 = find(c14, 'Warehouse and storage'), find(c14, 'All buildings')
w13 = find(c13, 'Warehouse and storage')
KWH_PER_BTU = 1/3412.14
out = [
 ('warehouse_buildings_thousand', w1[1], 'Table C1'), ('warehouse_floorspace_million_sqft', w1[2], 'Table C1'),
 ('warehouse_major_fuels_tbtu', w1[3], 'Table C1'), ('warehouse_electricity_site_tbtu', w1[5], 'Table C1'),
 ('warehouse_natural_gas_tbtu', w1[6], 'Table C1'),
 ('warehouse_electricity_billion_kwh', w13[6], 'Table C13'),
 ('warehouse_elec_kwh_per_sqft_mean', w14[2], 'Table C14'), ('warehouse_elec_kwh_per_sqft_p25', w14[4], 'Table C14'),
 ('warehouse_elec_kwh_per_sqft_median', w14[5], 'Table C14'), ('warehouse_elec_kwh_per_sqft_p75', w14[6], 'Table C14'),
 ('warehouse_elec_price_usd_per_kwh', w14[9], 'Table C14'),
 ('allbuildings_elec_kwh_per_sqft_mean', a14[2], 'Table C14'),
 ('warehouse_gas_kbtu_per_sqft_derived', round(w1[6]*1e12/(w1[2]*1e6)/1000, 2), 'Derived: C1 gas TBtu / C1 floorspace'),
 ('warehouse_elec_kwh_per_sqft_derived_C13', round(w13[6]*1e9/(w13[2]*1e6), 2), 'Derived: C13 kWh / C13 floorspace of electricity-using warehouses'),
]
with open(os.path.join(OUT, 'cbecs2018_warehouse_intensity.csv'), 'w', newline='') as fh:
    w = csv.writer(fh); w.writerow(['metric', 'value', 'cbecs_table_or_method']); w.writerows(out)
print(out)
# CBECS by census region and size class (all buildings, mean kWh/sqft; context for regional/size sensitivity)
reg = []
for r in c14:
    if r[0] and r[1] not in ('', None) and str(r[0]).strip() in ('Northeast','Midwest','South','West','New England','Middle Atlantic','East North Central','West North Central','South Atlantic','East South Central','West South Central','Mountain','Pacific','Cold or very cold','Cool','Mixed mild','Warm','Hot or very hot') or (r[0] and str(r[0]).strip() in ('200,001 to 500,000','Over 500,000','100,001 to 200,000')):
        reg.append((str(r[0]).strip(), r[2], r[4], r[5], r[6]))
with open(os.path.join(OUT, 'cbecs2018_all_building_intensity_by_region_size.csv'), 'w', newline='') as fh:
    w = csv.writer(fh); w.writerow(['category','mean_kwh_per_sqft','p25','median','p75']); w.writerows(reg)
