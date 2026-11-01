#!/usr/bin/env python3
"""INTERP ENV: scenario netting of Amazon logistics-building and delivery emissions against
the store buildings and shopping trips that e-commerce may displace.

Run:  python3 -I scripts/interp_env_netting.py        (standard library only)

Inputs (all in data/processed unless stated):
  interp_env_inputs_filings.csv   hand-assembled 10-K values with accession numbers
  interp_env_params.csv           every scalar assumption, low / central / high, with status
  interp_env_category_params.csv  per-category attribution inputs (PLACEHOLDER until interp_spend_* exist)
  amazon_10k_square_footage_by_segment.csv, amazon_10k_square_footage.csv   Amazon sq ft (10-K)
  bench_network_facilities.csv    Target distribution-centre sq ft (10-K)
  egrid_us_average_output_rate_by_year.csv                                  US average grid CO2e
  amazon_carbon_footprint_by_report_vintage.csv                             Amazon reported Scope 1/2
  data/raw/retail_context/interp_env_census_tsnotadjustedsales.xlsx         Census quarterly e-commerce (optional;
                                  the annual table is cached in interp_env_census_ecommerce_annual.csv)
  data/raw/retail_context/cbecs2018_c1/c14.xlsx                             CBECS check (optional)

Outputs: data/processed/interp_env_*.csv (see the list at the bottom). Nothing outside interp_env_* is written.
Every output number is ESTIMATE or DERIVED; none is a measurement of Amazon's facilities or deliveries.
"""
import csv, os, re, zipfile, xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'data', 'processed')
RAW = os.path.join(ROOT, 'data', 'raw', 'retail_context')
YEARS = list(range(2015, 2026))
LB_PER_MWH_TO_KG_PER_KWH = 0.45359237 / 1000.0


def rd(name):
    with open(os.path.join(P, name), newline='') as f:
        return list(csv.DictReader(f))


def wr(name, rows, fields=None):
    fields = fields or list(rows[0])
    with open(os.path.join(P, name), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print('wrote', name, len(rows), 'rows')


def rnd(x, n=2):
    return None if x is None else round(x, n)


# ---------------------------------------------------------------- parameters
PRM = {r['name']: (float(r['low']), float(r['central']), float(r['high'])) for r in rd('interp_env_params.csv')}
TAGS = ('low', 'central', 'high')


def prm(name, tag):
    return PRM[name][TAGS.index(tag)]


# ---------------------------------------------------------------- filings inputs
FIL = {}
for r in rd('interp_env_inputs_filings.csv'):
    FIL[(r['entity'], int(r['cal_year']), r['metric'])] = (float(r['value']), r['accession'])


def fil(e, y, m):
    return FIL[(e, y, m)][0]


# ---------------------------------------------------------------- grid factor
EGRID = {}
for r in rd('egrid_us_average_output_rate_by_year.csv'):
    EGRID[int(r['egrid_data_year'])] = (float(r['lb_per_MWh_total_output']), r['gas'])


def grid_kg_per_kwh(year):
    ys = [y for y in EGRID if y <= year]
    y0 = max(ys)
    return EGRID[y0][0] * LB_PER_MWH_TO_KG_PER_KWH, y0, EGRID[y0][1]


# ---------------------------------------------------------------- tiny xlsx reader
NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}


def read_xlsx(path):
    z = zipfile.ZipFile(path)
    ss = []
    if 'xl/sharedStrings.xml' in z.namelist():
        for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si', NS):
            ss.append(''.join(t.text or '' for t in si.iter('{%s}t' % NS['m'])))
    x = ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
    rows = []
    for r in x.iter('{%s}row' % NS['m']):
        row = {}
        for c in r.findall('m:c', NS):
            col = re.match(r'[A-Z]+', c.get('r')).group()
            v = c.find('m:v', NS)
            if v is None:
                row[col] = None
            else:
                row[col] = ss[int(v.text)] if c.get('t') == 's' else v.text
        rows.append(row)
    return rows


# ---------------------------------------------------------------- 0. CBECS check
def cbecs_check():
    out = []
    try:
        c1 = read_xlsx(os.path.join(RAW, 'cbecs2018_c1.xlsx'))
        c14 = read_xlsx(os.path.join(RAW, 'cbecs2018_c14.xlsx'))
    except Exception as e:  # raw files are gitignored
        print('CBECS xlsx not available, check skipped:', e)
        return out

    def find(rows, label):
        for r in rows:
            if (r.get('A') or '').strip() == label:
                return r
        raise KeyError(label)
    for lab in ('Retail (other than mall)', 'Mercantile', 'Warehouse and storage', 'Enclosed and strip malls', 'Food sales'):
        a = find(c1, lab)          # B bldgs (k), C floorspace (M sq ft), ..., I..: natural gas TBtu col H
        floor = float(a['C'])
        gas_tbtu = float(a['G'])   # C1 columns: B bldgs, C floorspace, D site total, E primary, F electricity, G natural gas
        b = find(c14, lab)         # C kWh/sqft mean, G p25.. see header; cols: B per bldg, C per sqft, D per worker, E p25, F median, G p75
        out.append(dict(building_activity=lab, floorspace_million_sqft=floor, natural_gas_tbtu=gas_tbtu,
                        gas_kbtu_per_sqft_derived=rnd(gas_tbtu / floor * 1000, 2), elec_kwh_per_sqft_mean=b['C'],
                        elec_p25=b['E'], elec_median=b['F'], elec_p75=b['G'],
                        source='CBECS 2018 tables C1 (gas TBtu / floorspace) and C14, data/raw/retail_context'))
    return out


# ---------------------------------------------------------------- 0b. Census annual e-commerce
def census_annual():
    path = os.path.join(RAW, 'interp_env_census_tsnotadjustedsales.xlsx')
    cache = 'interp_env_census_ecommerce_annual.csv'
    if os.path.exists(path):
        rows = read_xlsx(path)
        q = {}
        for r in rows:
            m = re.match(r'(\d)(?:st|nd|rd|th) quarter (\d{4})', (r.get('B') or '').strip())
            if m and r.get('C') and r.get('D'):
                q[(int(m.group(2)), int(m.group(1)))] = (float(r['C']), float(r['D']))
        out = []
        for y in range(2000, 2026):
            if all((y, k) in q for k in (1, 2, 3, 4)):
                tot = sum(q[(y, k)][0] for k in (1, 2, 3, 4))
                ec = sum(q[(y, k)][1] for k in (1, 2, 3, 4))
                out.append(dict(year=y, total_retail_sales_usd_m=round(tot), ecommerce_sales_usd_m=round(ec),
                                ecommerce_share_pct=round(ec / tot * 100, 2),
                                source='Census Bureau Quarterly Retail E-Commerce Sales, not-adjusted time series, sum of 4 quarters (released 2026-Q2 edition)'))
        wr(cache, out)
        return out
    return [dict(year=int(r['year']), total_retail_sales_usd_m=float(r['total_retail_sales_usd_m']),
                 ecommerce_sales_usd_m=float(r['ecommerce_sales_usd_m']), ecommerce_share_pct=float(r['ecommerce_share_pct']),
                 source=r['source']) for r in rd(cache)]


# ---------------------------------------------------------------- 1. floor space and sales
def amazon_sqft_k(y):
    seg = [r for r in rd('amazon_10k_square_footage_by_segment.csv') if int(r['fiscal_year']) == y and r['segment'] == 'North America']
    seg_total = float(seg[0]['leased_sqft_thousands']) + float(seg[0]['owned_sqft_thousands'])
    st = [r for r in rd('amazon_10k_square_footage.csv') if int(r['fiscal_year']) == y and r['space_type'] == 'physical_stores'
          and r['region'] == 'North America']
    stores = sum(float(r['square_feet_thousands']) for r in st)   # 0 before Whole Foods (2017)
    return seg_total, stores, seg[0]['source_10k_accession']


def target_dc_sqft_k(y):
    for r in rd('bench_network_facilities.csv'):
        if r['slug'] == 'target' and r['metric'] == 'sqft_thousand' and r['geography'] == 'US' and int(r['cal_year_approx']) == y \
                and r['facility_type'] in ('distribution_center', 'supply_chain_facility'):
            return float(r['value']), r['accession'], r['facility_type']
    return None, None, None


def build_floor_sales():
    s3 = prm('amazon_3p_gmv_share', 'central')
    rows = []
    for y in YEARS:
        seg_total, stores, acc = amazon_sqft_k(y)
        logi = seg_total - stores
        na = fil('amazon', y, 'na_segment_net_sales')
        phys = fil('amazon', y, 'ww_physical_stores')   # worldwide physical-store sales used as NA proxy (8 of 623 stores are intl)
        online = fil('amazon', y, 'ww_online_stores')
        tot = fil('amazon', y, 'ww_total_net_sales')
        aws = fil('amazon', y, 'ww_aws')
        k = (online / (1 - s3)) / (tot - aws - phys)        # GMV-to-revenue gross-up, worldwide, ex AWS ex physical stores
        na_ex = na - phys
        rows.append(dict(
            cal_year=y, entity='amazon_na',
            logistics_sqft_thousand=logi, stores_sqft_thousand=stores, sqft_basis='NA segment total sq ft minus NA physical stores',
            sqft_accession=acc, sales_usd_m=na, sales_ex_physical_stores_usd_m=round(na_ex), gmv_grossup_k=round(k, 4),
            gmv_proxy_usd_m=round(k * na_ex), dc_sqft_thousand=None,
            sales_accession=FIL[('amazon', y, 'na_segment_net_sales')][1],
            sales_basis='NA segment net sales (online + 3P fees + ads + subscriptions + stores; incl Canada, Mexico); GMV = k x (NA sales ex stores)'))
        wsq = fil('walmart_us', y, 'retail_sqft_thousand')
        t_dc, t_acc, t_type = target_dc_sqft_k(y)
        tsq = fil('target', y, 'retail_sqft_thousand')
        ratio = t_dc / tsq if t_dc else None
        rows.append(dict(
            cal_year=y, entity='walmart_us', logistics_sqft_thousand=None, stores_sqft_thousand=wsq,
            sqft_basis='Walmart U.S. segment retail sq ft (Jan 31 of next year)', sqft_accession=FIL[('walmart_us', y, 'retail_sqft_thousand')][1],
            sales_usd_m=fil('walmart_us', y, 'segment_net_sales'), sales_ex_physical_stores_usd_m=None, gmv_grossup_k=None,
            gmv_proxy_usd_m=None, dc_sqft_thousand=round(wsq * ratio) if ratio else None,
            sales_accession=FIL[('walmart_us', y, 'segment_net_sales')][1],
            sales_basis='Walmart U.S. segment net sales incl. its eCommerce; DC sq ft is a PROXY = Target DC/store ratio x Walmart US store sq ft (Walmart discloses no DC sq ft)'))
        rows.append(dict(
            cal_year=y, entity='target', logistics_sqft_thousand=None, stores_sqft_thousand=tsq,
            sqft_basis='Target retail sq ft (excl. office, DC, vacant)', sqft_accession=FIL[('target', y, 'retail_sqft_thousand')][1],
            sales_usd_m=fil('target', y, 'total_revenue'), sales_ex_physical_stores_usd_m=None, gmv_grossup_k=None,
            gmv_proxy_usd_m=None, dc_sqft_thousand=t_dc,
            sales_accession=FIL[('target', y, 'total_revenue')][1] + '; DC ' + str(t_acc),
            sales_basis='Target total revenue (incl. its digital sales); DC row type ' + str(t_type) + ' (definition widened FY2022)'))
    return rows


# ---------------------------------------------------------------- 2. building energy per $ of sales
def sqft_kg(year, kwh_sqft, kbtu_sqft):
    ef, _, _ = grid_kg_per_kwh(year)
    return kwh_sqft * ef + kbtu_sqft * prm('gas_kg_co2e_per_kbtu', 'central')


def intensity(kind, tag):
    if kind == 'warehouse':
        return prm('wh_elec_kwh_per_sqft', tag), prm('wh_gas_kbtu_per_sqft', tag)
    if kind == 'retail':
        return prm('retail_elec_kwh_per_sqft', tag), prm('retail_gas_kbtu_per_sqft', tag)
    raise KeyError(kind)


def build_intensity(fs):
    by = {(r['cal_year'], r['entity']): r for r in fs}
    out = []
    for y in YEARS:
        ef, efy, efg = grid_kg_per_kwh(y)
        a, w, t = by[(y, 'amazon_na')], by[(y, 'walmart_us')], by[(y, 'target')]

        def row(entity, boundary, kind_note, sqft_k, kinds, denom_name, denom_usd_m):
            for tag in TAGS:
                kg = 0.0
                for sq, kind in zip(sqft_k, kinds):
                    kw, gs = intensity(kind, tag)
                    kg += sq * 1000 * sqft_kg(y, kw, gs)
                out.append(dict(cal_year=y, entity=entity, boundary=boundary, intensity_case=kind_note, case=tag,
                                sqft_thousand=round(sum(sqft_k)), emissions_t_co2e=round(kg / 1000),
                                denominator=denom_name, sales_usd_m=round(denom_usd_m),
                                kg_co2e_per_1000_usd=round(kg / (denom_usd_m * 1000), 3),
                                grid_lb_per_mwh_year_used=efy, grid_gas_basis=efg, status='ESTIMATE'))
        # Amazon: warehouse-only network, three denominators; plus retail-intensity case
        for dn, dv in (('NA net sales ex stores (revenue)', a['sales_ex_physical_stores_usd_m']), ('NA GMV proxy', a['gmv_proxy_usd_m'])):
            row('amazon_na', 'network (warehouse intensity)', 'CBECS warehouse', [a['logistics_sqft_thousand']], ['warehouse'], dn, dv)
            row('amazon_na', 'network (retail intensity, sensitivity)', 'CBECS retail non-mall', [a['logistics_sqft_thousand']], ['retail'], dn, dv)
        row('walmart_us', 'stores only', 'CBECS retail non-mall', [w['stores_sqft_thousand']], ['retail'], 'Walmart US net sales', w['sales_usd_m'])
        # Walmart with DC proxy (central/low/high of the DC ratio multiplier is applied to sq ft)
        for tag in TAGS:
            mult = prm('walmart_dc_ratio_multiplier', tag)
            dc = w['dc_sqft_thousand'] * mult
            kw_r, gs_r = intensity('retail', tag)
            kw_w, gs_w = intensity('warehouse', tag)
            kg = w['stores_sqft_thousand'] * 1000 * sqft_kg(y, kw_r, gs_r) + dc * 1000 * sqft_kg(y, kw_w, gs_w)
            out.append(dict(cal_year=y, entity='walmart_us', boundary='stores + DC (DC sq ft PROXY)', intensity_case='retail stores, warehouse DCs',
                            case=tag, sqft_thousand=round(w['stores_sqft_thousand'] + dc), emissions_t_co2e=round(kg / 1000),
                            denominator='Walmart US net sales', sales_usd_m=round(w['sales_usd_m']),
                            kg_co2e_per_1000_usd=round(kg / (w['sales_usd_m'] * 1000), 3),
                            grid_lb_per_mwh_year_used=efy, grid_gas_basis=efg, status='ESTIMATE'))
        row('target', 'stores only', 'CBECS retail non-mall', [t['stores_sqft_thousand']], ['retail'], 'Target total revenue', t['sales_usd_m'])
        row('target', 'stores + DC', 'retail stores, warehouse DCs', [t['stores_sqft_thousand'], t['dc_sqft_thousand']], ['retail', 'warehouse'],
            'Target total revenue', t['sales_usd_m'])
    return out


# ---------------------------------------------------------------- shared helpers for sections 3-6
def central():
    return {n: v[1] for n, v in PRM.items()}


def lowhigh(name):
    return PRM[name][0], PRM[name][2]


def per_pkg_kg(P):
    """kg CO2e per delivered package: last-mile van + middle-mile truck (+ optional air) x (1 + returns)."""
    last = P['delivery_miles_per_package'] * P['van_kg_co2e_per_mile']
    mid = P['middle_mile_truck_miles_per_parcel_path'] * P['truck_kg_co2e_per_vehicle_mile'] / P['parcels_per_trailer']
    air = P['air_share_of_packages'] * P['package_weight_lb'] / 2000.0 * P['air_miles_per_package'] * P['air_kg_co2e_per_short_ton_mile']
    return last, mid, air, (last + mid + air) * (1 + P['returns_rate_online'])


# ---------------------------------------------------------------- 3a. NHTS and ARTS calibration inputs
def arts_store_sales():
    """Store-based retail sales that online can displace = total retail - motor vehicle and parts (441) - gasoline stations (447)
    - nonstore retailers (454), Census ARTS 2022 benchmarked, USD million."""
    path = os.path.join(ROOT, 'data', 'raw', 'interp_spend', 'census', 'estats', 'arts2022bm_sales.xlsx')
    cache = 'interp_env_arts_store_sales.csv'
    if os.path.exists(path):
        rows = read_xlsx(path)
        hdr = rows[3]
        col = {str(v).rstrip('r'): k for k, v in hdr.items() if v and str(v).rstrip('r').isdigit()}
        want = {'total': lambda r, a, b: b.startswith('Retail sales, total ') or b.startswith('Retail sales, total …'),
                '441': None, '447': None, '454': None}
        out = []
        for yr in ('2017', '2022'):
            c = col[yr]
            vals = {}
            for r in rows[4:]:
                b = (r.get('B') or '').strip()
                a = r.get('A')
                if b.startswith('Retail sales, total') and 'excl' not in b and 'total' not in vals:
                    vals['total'] = float(r[c])
                if a in ('441', '447', '454'):
                    vals[a] = float(r[c])
            out.append(dict(year=int(yr), total_retail_usd_m=vals['total'], motor_vehicle_parts_441_usd_m=vals['441'], gasoline_447_usd_m=vals['447'],
                            nonstore_454_usd_m=vals['454'],
                            instore_base_usd_m=vals['total'] - vals['441'] - vals['447'] - vals['454'],
                            source='Census ARTS 2022 benchmarked sales.xlsx (https://www2.census.gov/programs-surveys/arts/tables/2022benchmarked/sales.xlsx), 2022r and 2017 columns'))
        wr(cache, out)
        return {r['year']: r for r in out}
    return {int(r['year']): {k: (float(v) if k != 'source' else v) for k, v in r.items()} for r in rd(cache)}


def nhts():
    d = {}
    for r in rd('interp_env_nhts_inputs.csv'):
        d[r['item']] = (float(r['nhts_2022']), float(r['nhts_2017']))
    return d


def shopping_vmt_per_k(arts, nh, basis):
    """Vehicle-miles driven per $1,000 of in-store sales, calibrated on NHTS VMT, not on trip counts x legs."""
    i = 1 if basis.endswith('2017') else 0
    yr = 2017 if i else 2022
    hh = nh['shopping_and_errands_person_trips_national_million'][i] * 1e6 / (nh['shopping_person_trips_per_household'][i] + nh['errands_person_trips_per_household'][i])
    vmt = nh['shopping_vmt_per_household'][i] + (nh['errands_vmt_per_household'][i] if basis.startswith('shopping_plus_errands') else 0.0)
    return hh, vmt * hh, vmt * hh / (arts[yr]['instore_base_usd_m'] * 1e6) * 1000.0


# ---------------------------------------------------------------- 3b. own emissions and avoided emissions per $1,000
def category_weights():
    cats = rd('interp_env_category_params.csv')
    w = {}
    for c in cats:
        if c['group'] != 'category_2022':
            continue
        inc = (float(c['online_share_end']) - float(c['online_share_start'])) * float(c['pce_musd_end'])
        w[c['category']] = (inc, c['cbecs_building_category'], c['sales_per_sqft_usd_override'], c['sensitivity_exclude'])
    tot = sum(v[0] for v in w.values())
    return {k: (v[0] / tot, v[1], v[2], v[3]) for k, v in w.items()}


def own_per_k(P, fs_by, year, wh_kwh=None, wh_gas=None):
    """Amazon NA own emissions, kg CO2e per $1,000 of Amazon NA GMV. Returns (buildings, delivery, total)."""
    a = fs_by[(year, 'amazon_na')]
    kw = wh_kwh if wh_kwh is not None else P['wh_elec_kwh_per_sqft']
    gs = wh_gas if wh_gas is not None else P['wh_gas_kbtu_per_sqft']
    ef = grid_kg_per_kwh(year)[0]
    bld_kg = a['logistics_sqft_thousand'] * 1000 * (kw * ef + gs * P['gas_kg_co2e_per_kbtu'])
    per_k_den = a['gmv_proxy_usd_m'] * 1000.0
    last, mid, air, pk = per_pkg_kg(P)
    deliv = pk / P['amazon_usd_per_package'] * 1000.0
    return bld_kg / per_k_den, deliv, bld_kg / per_k_den + deliv


def avoided_per_k(P, fs_by, year, nh, arts, weights, vmt_basis='shopping_2022', density='central', grocery_weight=None, car_ef=None):
    """Avoided emissions per $1,000 of IN-STORE spend removed (sigma = 1). Returns (trips, buildings, total, detail)."""
    hh, vmt_nat, miles_per_k = shopping_vmt_per_k(arts, nh, vmt_basis)
    ef = car_ef if car_ef is not None else P['car_kg_co2e_per_mile']
    trips = miles_per_k * ef * (1 - P['trip_complement_offset'])
    end = 2022
    dw = fs_by[(end, 'walmart_us')]['stores_sqft_thousand'] * 1000 / (fs_by[(end, 'walmart_us')]['sales_usd_m'] * 1e6)
    dt = fs_by[(end, 'target')]['stores_sqft_thousand'] * 1000 / (fs_by[(end, 'target')]['sales_usd_m'] * 1e6)
    dens = {'low': dw, 'central': (dw + dt) / 2, 'high': dt}[density]          # sq ft per USD of store sales
    efg = grid_kg_per_kwh(end)[0]
    gw = sum(v[0] for k, v in weights.items() if v[1] == 'food_sales') if grocery_weight is None else grocery_weight
    # retail (non-food) building kg per $1,000 of in-store spend
    retail_kg_sqft = P['retail_elec_kwh_per_sqft'] * efg + P['retail_gas_kbtu_per_sqft'] * P['gas_kg_co2e_per_kbtu']
    food_kg_sqft = CBECS_CAT['food_sales'][0][1] * efg + CBECS_CAT['food_sales'][1] * P['gas_kg_co2e_per_kbtu']
    b_retail = 1000 * dens * P['substitution_realisation'] * retail_kg_sqft
    b_food = 1000 / 749.0 * P['substitution_realisation'] * food_kg_sqft
    bld = (1 - gw) * b_retail + gw * b_food
    return trips, bld, trips + bld, dict(miles_per_k=miles_per_k, vmt_national_bn=vmt_nat / 1e9, households_m=hh / 1e6, grocery_weight=gw,
                                           b_retail=b_retail, b_food=b_food, dens=dens)


CBECS_CAT = {'food_sales': ((47.4, 53.3, 69.9), 47.7)}


def build_breakeven(fs, arts, nh):
    fs_by = {(r['cal_year'], r['entity']): r for r in fs}
    weights = category_weights()
    P0 = central()
    year = 2022
    ob, od, ot = own_per_k(P0, fs_by, year)
    at, ab, atot, det = avoided_per_k(P0, fs_by, year, nh, arts, weights)
    be0 = ot / atot
    gmv = fs_by[(year, 'amazon_na')]['gmv_proxy_usd_m']
    rows = [dict(row='CENTRAL', varied='none', value='', own_buildings_kg_per_1000=rnd(ob, 2), own_delivery_kg_per_1000=rnd(od, 2), own_total_kg_per_1000=rnd(ot, 2),
                 avoided_trips_kg_per_1000_instore=rnd(at, 2), avoided_buildings_kg_per_1000_instore=rnd(ab, 2), avoided_total_kg_per_1000_instore=rnd(atot, 2),
                 breakeven_substitution=rnd(be0, 3), note='per $1,000 of Amazon NA GMV (own) and per $1,000 of in-store spend removed (avoided); break-even = own / avoided')]

    def add(label, varied, value, P=None, wh=None, vmt_basis='shopping_2022', density='central', gw=None, car=None, own_year=year, note=''):
        P = P or P0
        ob_, od_, ot_ = own_per_k(P, fs_by, own_year, *(wh or (None, None)))
        at_, ab_, atot_, d_ = avoided_per_k(P, fs_by, year, nh, arts, weights, vmt_basis, density, gw, car)
        rows.append(dict(row=label, varied=varied, value=value, own_buildings_kg_per_1000=rnd(ob_, 2), own_delivery_kg_per_1000=rnd(od_, 2), own_total_kg_per_1000=rnd(ot_, 2),
                         avoided_trips_kg_per_1000_instore=rnd(at_, 2), avoided_buildings_kg_per_1000_instore=rnd(ab_, 2), avoided_total_kg_per_1000_instore=rnd(atot_, 2),
                         breakeven_substitution=rnd(ot_ / atot_, 3), note=note))
        return ot_ / atot_

    def with_(**kw):
        P = dict(P0); P.update(kw); return P
    # --- one assumption at a time ---
    for name, label in (('van_kg_co2e_per_mile', 'van kg CO2e per mile'), ('delivery_miles_per_package', 'van miles per package'),
                        ('middle_mile_truck_miles_per_parcel_path', 'middle-mile truck miles per parcel'), ('parcels_per_trailer', 'parcels per trailer'),
                        ('amazon_usd_per_package', 'USD per package'), ('trip_complement_offset', 'trip offset'), ('substitution_realisation', 'store energy realisation')):
        lo, hi = lowhigh(name)
        for v, tag in ((lo, 'low'), (hi, 'high')):
            add('ONE-AT-A-TIME', label, '%s=%s' % (tag, v), P=with_(**{name: v}))
    for tag, ef in (('low', PRM['car_kg_co2e_per_mile'][0]), ('high', PRM['car_kg_co2e_per_mile'][2])):
        add('ONE-AT-A-TIME', 'car kg CO2e per mile', '%s=%s' % (tag, ef), car=ef)
    for tag, dd in (('Walmart density', 'low'), ('Target density', 'high')):
        add('ONE-AT-A-TIME', 'store sq ft per $', tag, density=dd)
    for tag, (k, g) in (('warehouse low', (PRM['wh_elec_kwh_per_sqft'][0], PRM['wh_gas_kbtu_per_sqft'][0])), ('warehouse high', (PRM['wh_elec_kwh_per_sqft'][2], PRM['wh_gas_kbtu_per_sqft'][2]))):
        add('ONE-AT-A-TIME', 'Amazon building intensity (CBECS)', tag, wh=(k, g))
    add('ONE-AT-A-TIME', 'Amazon buildings at retail intensity', 'retail 13.7 kWh + 16.75 kBtu', wh=(P0['retail_elec_kwh_per_sqft'], P0['retail_gas_kbtu_per_sqft']))
    for r_ in (0.15, 0.30):
        add('ONE-AT-A-TIME', 'online returns', 'rate=%s (one extra outbound-equivalent transport per return)' % r_, P=with_(returns_rate_online=r_), note='returns are a sensitivity, not part of the central case; store-side returns not modelled')
    add('ONE-AT-A-TIME', 'air', 'air share 5% at 1,000 miles', P=with_(air_share_of_packages=0.05), note='central omits Amazon Air (no public domestic share)')
    add('ONE-AT-A-TIME', 'trip VMT basis', 'shopping + errands VMT 2022 (errands are not retail purchases: upper bound)', vmt_basis='shopping_plus_errands_2022')
    add('ONE-AT-A-TIME', 'trip VMT basis', 'NHTS 2017 shopping VMT per household and 2017 in-store sales', vmt_basis='shopping_2017', note='NHTS 2022 has a method break (retail_context.md 5.2)')
    add('ONE-AT-A-TIME', 'category mix', 'no grocery in the mix', gw=0.0)
    add('ONE-AT-A-TIME', 'category mix', 'grocery 30% of the mix', gw=0.30)
    add('ONE-AT-A-TIME', 'year of Amazon own emissions', '2025 (grid 2023, 481,952k sq ft)', own_year=2025)
    # --- stacked corners ---
    Plo = dict(P0); Phi = dict(P0)
    for n in ('van_kg_co2e_per_mile', 'delivery_miles_per_package', 'middle_mile_truck_miles_per_parcel_path', 'parcels_per_trailer', 'amazon_usd_per_package'):
        Plo[n], Phi[n] = PRM[n][0], PRM[n][2]
    Plo['trip_complement_offset'], Phi['trip_complement_offset'] = 0.0, 0.5
    Plo['substitution_realisation'], Phi['substitution_realisation'] = 1.0, 0.25
    # break-even LOW corner: own at low limits, avoided at high limits
    a1 = own_per_k(Plo, fs_by, year, PRM['wh_elec_kwh_per_sqft'][0], PRM['wh_gas_kbtu_per_sqft'][0])
    b1 = avoided_per_k(Plo, fs_by, year, nh, arts, weights, 'shopping_plus_errands_2022', 'high', None, PRM['car_kg_co2e_per_mile'][2])
    a2 = own_per_k(Phi, fs_by, year, PRM['wh_elec_kwh_per_sqft'][2], PRM['wh_gas_kbtu_per_sqft'][2])
    Phi2 = dict(Phi)
    b2 = avoided_per_k(Phi2, fs_by, year, nh, arts, weights, 'shopping_2022', 'low', None, PRM['car_kg_co2e_per_mile'][0])
    for lab, a_, b_ in (('STACKED all-optimistic-for-Amazon corner (own low, avoided high; NOT a range)', a1, b1),
                        ('STACKED all-pessimistic-for-Amazon corner (own high, avoided low; NOT a range)', a2, b2)):
        rows.append(dict(row=lab, varied='all assumptions at their limits together', value='', own_buildings_kg_per_1000=rnd(a_[0], 2), own_delivery_kg_per_1000=rnd(a_[1], 2),
                         own_total_kg_per_1000=rnd(a_[2], 2), avoided_trips_kg_per_1000_instore=rnd(b_[0], 2), avoided_buildings_kg_per_1000_instore=rnd(b_[1], 2),
                         avoided_total_kg_per_1000_instore=rnd(b_[2], 2), breakeven_substitution=rnd(a_[2] / b_[2], 3),
                         note='extreme corner: every assumption at its limit in the same direction; not an uncertainty interval'))
    one = [r['breakeven_substitution'] for r in rows if r['row'] == 'ONE-AT-A-TIME']
    summary = dict(year=year, gmv_usd_m=gmv, central_breakeven=rnd(be0, 3), one_at_a_time_min=min(one), one_at_a_time_max=max(one),
                   own_total=ot, own_buildings=ob, own_delivery=od, avoided_trips=at, avoided_buildings=ab, avoided_total=atot, detail=det,
                   corner_low=rows[-2]['breakeven_substitution'], corner_high=rows[-1]['breakeven_substitution'])
    # illustration: net in Mt at labelled sigma values (central case)
    ill = []
    for sg in (0.05, 0.10, 0.20, 0.30, 0.40, 0.60, 1.00):
        net = (ot - sg * atot) * gmv * 1000.0 / 1e9
        ill.append(dict(substitution_per_online_dollar=sg, own_kt=round(ot * gmv * 1000 / 1e6, 0), avoided_kt=round(sg * atot * gmv * 1000 / 1e6, 0), net_kt=round(net * 1000, 0),
                        label='ILLUSTRATION ONLY at an assumed substitution value; no value is a finding' + ('; 1.0 = UPPER BOUND, not supported by the literature' if sg == 1.0 else ''),
                        basis='Amazon NA GMV proxy 2022 x per-$1,000 figures of the central case; Amazon share of e-commerce is not needed because both sides are per Amazon online dollar'))
    return rows, summary, ill


def build_reconcile(arts, nh, summary):
    rows = []
    hh, vmt_nat, mpk = shopping_vmt_per_k(arts, nh, 'shopping_2022')
    hh2, vmt2, mpk2 = shopping_vmt_per_k(arts, nh, 'shopping_2017')
    hh_a, vmt_a, mpk_a = shopping_vmt_per_k(arts, nh, 'shopping_plus_errands_2022')
    vt_per_hh = nh['shopping_vehicle_trips_per_household'][0]
    rows.append(dict(item='households implied by NHTS Table 4-1 / Table 3-2 (2022), million', value=round(hh / 1e6, 1), note='89,384M shopping-and-errand person trips / (337 + 364) per household'))
    rows.append(dict(item='NHTS shopping VMT national 2022, bn miles', value=round(vmt_nat / 1e9, 1), note='1,320 VMT per household (Table 3-4, printed p.20) x households'))
    rows.append(dict(item='NHTS shopping + errands VMT national 2022, bn miles', value=round(vmt_a / 1e9, 1), note='(1,320 + 2,220) x households'))
    rows.append(dict(item='VMT per shopping vehicle trip, miles', value=round(nh['shopping_vmt_per_household'][0] / vt_per_hh, 2), note='1,320 / 229 vehicle trips (Table 3-6); compare Table 3-5 trip length 5.8'))
    rows.append(dict(item='shopping vehicle trips per shopping person trip', value=round(vt_per_hh / nh['shopping_person_trips_per_household'][0], 2), note='229 / 337; vehicle occupancy 1.53 persons per vehicle (Table 5-2, printed p.41)'))
    pop22 = 333.287557
    rows.append(dict(item='shopping+errand person trips per person per day, from national total / Census population', value=round(nh['shopping_and_errands_person_trips_national_million'][0] / pop22 / 365, 3),
                     note='89,384M / 333.287557M (Census Vintage 2022, POPESTIMATE2022, https://www2.census.gov/programs-surveys/popest/datasets/2020-2022/state/totals/NST-EST2022-ALLDATA.csv) / 365; NHTS Table 4-5 gives 0.80 (different population base)'))
    old = 0.80 * 365 * pop22 * 1e6 * 2 * 6.5
    rows.append(dict(item='FIRST-RUN implied shopping-and-errand vehicle-miles, bn (0.80 trips x 365 x population x 2 legs x 6.5 mi)', value=round(old / 1e9), note='treated person trips as car trips, doubled the return leg that NHTS already counts, and mixed 2009 length with 2022 counts'))
    rows.append(dict(item='ratio first-run implied VMT / NHTS shopping+errands VMT', value=round(old / vmt_a, 1), note='the first run overstated shopping vehicle-miles by this factor'))
    rows.append(dict(item='ratio first-run implied VMT / NHTS shopping-only VMT', value=round(old / vmt_nat, 1), note=''))
    rows.append(dict(item='in-store sales base 2022 (ARTS total - 441 - 447 - 454), USD bn', value=round(arts[2022]['instore_base_usd_m'] / 1e3, 1), note='verified from the ARTS file; the review recalled about 3.55 tn'))
    rows.append(dict(item='in-store sales base 2017, USD bn', value=round(arts[2017]['instore_base_usd_m'] / 1e3, 1), note='same construction'))
    rows.append(dict(item='shopping VMT per $1,000 in-store sales 2022, miles', value=round(mpk, 1), note='central calibration'))
    rows.append(dict(item='shopping VMT per $1,000 in-store sales 2017, miles', value=round(mpk2, 1), note='2017 NHTS and 2017 sales'))
    rows.append(dict(item='shopping+errands VMT per $1,000 in-store sales 2022, miles', value=round(mpk_a, 1), note='upper bound; errands are not retail purchases'))
    return rows


# ---------------------------------------------------------------- 3c. per-item basket table (one store outing vs one package)
BASKETS = (1, 2, 3, 5, 8, 10, 15, 20, 30, 50, 70)


def build_transport():
    P0 = central()
    rows, be = [], []
    cases = (('online_favourable', 'high', 'low'), ('central', 'central', 'central'), ('store_favourable', 'low', 'high'))
    pick = {'low': 0, 'central': 1, 'high': 2}

    def PS(tag):
        return {n: PRM[n][pick[tag]] for n in PRM}
    for name, st, dl in cases:
        S, D = PS(st), PS(dl)
        trip = S['trip_legs_per_outing'] * S['nhts_oneway_trip_miles'] * S['car_kg_co2e_per_mile'] * S['trip_chaining_allocation']
        last, mid, air, tot = per_pkg_kg({**D, 'returns_rate_online': 0.0, 'air_share_of_packages': 0.0})
        for n in BASKETS:
            rows.append(dict(case=name, store_case=st, delivery_case=dl, items_per_shopping_outing=n, store_outing_kg_co2e=round(trip, 3), store_kg_per_item=round(trip / n, 4),
                             lastmile_kg_per_package=round(last, 4), middlemile_kg_per_package=round(mid, 4), delivery_kg_per_package_no_returns=round(tot, 4),
                             items_per_package=1, online_minus_store_kg_per_item=round(tot - trip / n, 4), lower_channel='online' if tot < trip / n else 'store', status='ESTIMATE'))
        for r_ in (0.0, 0.15, 0.30):
            _, _, _, tr = per_pkg_kg({**D, 'returns_rate_online': r_, 'air_share_of_packages': 0.0})
            be.append(dict(case=name, returns_rate=r_, store_outing_kg_co2e=round(trip, 3), delivery_kg_per_package=round(tr, 4), breakeven_items_per_outing=round(trip / tr, 2),
                           breakeven_oneway_miles_at_10_items=round(10 * tr / (S['trip_legs_per_outing'] * S['car_kg_co2e_per_mile'] * S['trip_chaining_allocation']), 2),
                           reading='online has lower transport CO2e per item when the basket is smaller than break-even items per outing (one item per package; returns only if rate > 0)'))
    shah = 2 * 4.83 * 0.18 / 30
    lit = [
        dict(source='Shahmohammadi et al. 2020 ES&T 54(6):3499 (retail_context.md 3.1)', scope='UK FMCG total per item', metric='median kg CO2e per item', pure_play=0.18, traditional=0.10, bricks_and_clicks=0.07,
             note='90% intervals: 0.08-0.52, 0.04-0.37, 0.05-0.11; groceries/household/personal care; returns excluded'),
        dict(source='Shahmohammadi et al. 2020', scope='last mile only per item', metric='median kg CO2e per item', pure_play=0.11, traditional=0.04, bricks_and_clicks=0.02,
             note='US store last-mile median 0.065 (UK 0.041); car trip 4.83 km one way, 0.18 kg/km, basket BetaPERT 1/30/70'),
        dict(source='First-principles replication of the Shahmohammadi US store trip', scope='last mile only per item', metric='2 x 4.83 km x 0.18 kg/km / 30 items', pure_play=None,
             traditional=round(shah, 4), bricks_and_clicks=None, note='close to their reported 0.065 US median'),
        dict(source='Jaller and Pahwa 2020 poster (retail_context.md 3.2)', scope='San Francisco daily, all-online vs all-in-store', metric='CO2 change vs in-store', pure_play='-75% / -64% / -42% (Q1 / median / Q3)',
             traditional=None, bricks_and_clicks='omni-channel +2% / +2% / +4%', note='POSTER numbers; full substitution with consolidated delivery; VMT -92/-88/-81%; NOx can rise'),
    ]
    return rows, be, lit


# ---------------------------------------------------------------- 4. evidence strip (studies as labelled points, no central sigma)
def build_evidence():
    return [
        dict(study='Pozzi (2013) RAND J. Econ 44(3)', what_it_measures='Online grocery orders from ONE chain: fall in that chain\'s own in-store spend per online dollar',
             number='under 0.40 USD per online dollar (own chain; a snippet of another version says 0.45, unverified)', unit_matches_sigma='Partly: it is the chain\'s own cannibalisation only; dollars taken from rival stores also count as avoided in-store spend',
             review_note='Do not call 0.40 a ceiling. Economy-wide in-store displacement for groceries is at least this, and plausibly more. Grocery only, one chain.', source='interp_spend.md section 7 (WP OPENED)'),
        dict(study='Chava, Oettl, Singh, Zeng (2022) NBER WP 30077', what_it_measures='Average nearby store sales after a fulfilment centre opens',
             number='-4% of store sales; exit probability +3 percentage points', unit_matches_sigma='No: a percent of store sales, not dollars per online dollar. Converting needs the local rise in online spend, which is not available here',
             review_note='Cannot be used as a low anchor for sigma in these units. Shows real store-level substitution near Amazon-type fulfilment centres.', source='interp_spend.md section 7 (paper OPENED)'),
        dict(study='Relihan (2022) CEP DP 1836', what_it_measures='Trips of online-grocery adopters (JPMorgan Chase Institute card data)',
             number='-7.4% grocery-store trips (6.8 to 6.3 per month); +12.3% local ground transport spend; more trips to coffee shops, restaurants, personal care, leisure, pharmacies',
             unit_matches_sigma='No: trips, not dollars. It informs the trip offset: the replaced store trip falls, other trips rise',
             review_note='Trips fall less than one-for-one; grocery only; not Amazon-specific.', source='interp_spend.md section 7 (paper OPENED)'),
        dict(study='Dolfen et al. (2019/2023) NBER WP 25610', what_it_measures='Visa spend: convenience gain from online vs offline merchants',
             number='convenience gain at most 0.4% of consumption; most gain is variety; online share about 5% (2007) to 8% (2017)', unit_matches_sigma='No', review_note='Context for how much online spending is new variety rather than substitution.', source='interp_spend.md section 7'),
        dict(study='Jaller and Pahwa (2020) poster', what_it_measures='All-online vs all-in-store day, San Francisco', number='CO2 -75 / -64 / -42%; omni-channel +2 to +4%', unit_matches_sigma='No (full substitution by construction)',
             review_note='Corresponds to sigma = 1 with consolidated delivery; poster, not the paper.', source='retail_context.md 3.2'),
    ]


# ---------------------------------------------------------------- 5. scale vs Amazon reported
def build_scale(fs):
    fs_by = {(r['cal_year'], r['entity']): r for r in fs}
    P0 = central()
    rep = {}
    for r in rd('amazon_carbon_footprint_by_report_vintage.csv'):
        if r['report_vintage'] == '2025 report':
            rep[(r['metric'], int(r['year']))] = float(r['value'])
    out = []
    for y in range(2019, 2026):
        a = fs_by[(y, 'amazon_na')]
        last, mid, air, pk = per_pkg_kg(P0)
        packages = a['gmv_proxy_usd_m'] * 1e6 / P0['amazon_usd_per_package']
        deliv_mt = packages * pk / 1e9
        ef = grid_kg_per_kwh(y)[0]
        elec_mt = a['logistics_sqft_thousand'] * 1000 * P0['wh_elec_kwh_per_sqft'] * ef / 1e9
        gas_mt = a['logistics_sqft_thousand'] * 1000 * P0['wh_gas_kbtu_per_sqft'] * P0['gas_kg_co2e_per_kbtu'] / 1e9
        na = fil('amazon', y, 'na_segment_net_sales')
        intl = fil('amazon', y, 'ww_total_net_sales') - fil('amazon', y, 'ww_aws') - na
        na_share = na / (na + intl)
        s1f = rep.get(('scope1_fossil_fuels', y))
        top = na_share * s1f if s1f else None
        out.append(dict(cal_year=y, bottom_up_NA_delivery_Mt=round(deliv_mt, 2), bottom_up_NA_building_gas_Mt=round(gas_mt, 2), bottom_up_NA_scope1_like_Mt=round(deliv_mt + gas_mt, 2),
                        bottom_up_NA_building_electricity_location_based_Mt=round(elec_mt, 2), NA_share_of_retail_segment_sales=round(na_share, 3),
                        reported_scope1_fossil_global_Mt=s1f, top_down_NA_scope1_fossil_Mt=rnd(top, 2),
                        ratio_bottom_up_to_top_down=rnd((deliv_mt + gas_mt) / top, 2) if top else None,
                        reported_scope2_market_global_Mt=rep.get(('scope2_purchased_electricity_market', y)),
                        reported_scope3_upstream_transport_Mt=rep.get(('scope3_upstream_transport_distribution', y)), reported_scope3_downstream_transport_Mt=rep.get(('scope3_downstream_transport_distribution', y)),
                        note='Top-down = NA share of retail-segment sales (NA / (NA + International)) x global Scope 1 fossil fuels; it also includes Amazon Air, non-NA fleets, stores and corporate use, so it is an upper-ish marker. Bottom-up omits air, FC-to-FC transfers and the van stem leg. A ratio well below 1 means the bottom-up is likely a floor.'))
    return out


# ---------------------------------------------------------------- main
def main():
    chk = cbecs_check()
    if chk:
        wr('interp_env_cbecs_check.csv', chk)
    cen = census_annual()
    fs = build_floor_sales()
    wr('interp_env_floor_space_sales.csv', fs)
    inten = build_intensity(fs)
    wr('interp_env_building_intensity_per_sales.csv', inten)
    tr, be, lit = build_transport()
    wr('interp_env_transport_per_item.csv', tr)
    wr('interp_env_transport_breakeven.csv', be)
    wr('interp_env_transport_literature.csv', lit)
    arts = arts_store_sales()
    nh = nhts()
    rows, summ, ill = build_breakeven(fs, arts, nh)
    wr('interp_env_breakeven_sensitivity.csv', rows)
    wr('interp_env_net_illustration_only.csv', ill)
    wr('interp_env_trip_reconciliation.csv', build_reconcile(arts, nh, summ))
    wr('interp_env_evidence_strip.csv', build_evidence())
    wr('interp_env_scale_vs_reported.csv', build_scale(fs))
    print('SUMMARY', {k: (round(v, 3) if isinstance(v, float) else v) for k, v in summ.items() if k != 'detail'})
    print('DETAIL', {k: round(v, 3) for k, v in summ['detail'].items()})
    for r in rows:
        print(r['row'][:12], '|', r['varied'][:30], '|', r['value'][:28], '| own', r['own_total_kg_per_1000'], '| avoided', r['avoided_total_kg_per_1000_instore'], '| BE', r['breakeven_substitution'])
    for r in ill:
        print(r['substitution_per_online_dollar'], r['own_kt'], r['avoided_kt'], r['net_kt'])


if __name__ == '__main__':
    main()
