"""Build data/processed/market_context.csv: a small, citation-only table of market-context figures.

Run:  python3 -I scripts/build_market_context.py

Every row is a FACT read from a processed extract (jhu_* subscription extracts or the public
Pitney Bowes files) with a citation "Publication, date, title (via database)". No quotes, no
document IDs, no proxy URLs. The only computed rows are marked basis='derived' (EIU online share =
online retail sales / retail sales, both EIU series).
"""
import csv, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'data/processed')


def rd(name):
    with open(os.path.join(P, name), newline='', encoding='utf-8') as fh:
        return list(csv.DictReader(fh))


ROWS = []


def add(topic, measure, entity, year, value, unit, basis, citation, note=''):
    ROWS.append(dict(topic=topic, measure=measure, entity=entity, year=year, value=value, unit=unit, basis=basis,
                     citation=citation, note=note))


def num(x):
    x = str(x).strip()
    try:
        f = float(x)
        return int(f) if f == int(f) and '.' not in x else f
    except ValueError:
        return x


# ---------------------------------------------------------------- 1. Prologis: Amazon share of net effective rent
for r in rd('jhu_mergent_archives_realestate_amazon_tenancy.csv'):
    if r['landlord'] != 'Prologis':
        continue
    pub = re.sub(r"\s*-\s*(10K or Int'l Equivalent|Annual/10K Report)$", '', r['publication']).strip()
    cit = '%s, annual report (Form 10-K) for FY%s, %s (via Mergent Archives)' % (pub, r['as_of_year'], r['doc_date'])
    if r['measure'] == 'amazon_pct_net_effective_rent_consolidated':
        add('prologis_amazon_rent_share', 'Amazon share of Prologis net effective rent, consolidated', 'Prologis',
            r['as_of_year'], num(r['value']), 'percent', 'as stated', cit)
    elif r['measure'] == 'amazon_pct_net_effective_rent_owned_and_managed':
        add('prologis_amazon_rent_share', 'Amazon share of Prologis net effective rent, owned and managed', 'Prologis',
            r['as_of_year'], num(r['value']), 'percent', 'as stated', cit)
    elif r['measure'] == 'amazon_rank_among_top_customers':
        add('prologis_amazon_rent_share', 'Amazon rank among Prologis top customers', 'Prologis', r['as_of_year'],
            num(r['value']), 'rank', 'as stated', cit)
for r in rd('jhu_value_line_real_estate.csv'):
    yr = '20' + r['as_of'].split('/')[-1]
    cit = 'Value Line Investment Survey, %s, %s (via Value Line)' % (r['report_date'], r['report_title'])
    add('prologis_amazon_rent_share', 'Amazon share of Prologis net effective rent, as shown by Value Line', 'Prologis',
        yr, num(r['amazon_pct_net_effective_rent']), 'percent', 'as stated', cit,
        'Value Line lists Amazon as largest customer; its 2022 figure equals the owned-and-managed measure in the 10-K')

# ---------------------------------------------------------------- 2. Amazon share of UPS revenue
ups = {}  # (year, value) -> dict(value, cites[], note)


def ups_add(year, value, cite, note=''):
    d = ups.setdefault((year, value), dict(value=value, cites=[], note=note))
    if cite not in d['cites']:
        d['cites'].append(cite)


for r in rd('jhu_mergent_archives_amazon_carrier_relationships.csv'):
    if r['counterparty'] == 'UPS' and r['metric'] == 'amazon_share_of_consolidated_revenue':
        pub = re.sub(r"\s*-\s*(10K or Int'l Equivalent|Annual/10K Report)$", '', r['publication']).strip()
        ups_add(r['fiscal_year'], r['value'],
                '%s, annual report (Form 10-K), %s (via Mergent Archives)' % (pub, r['doc_date']),
                'UPS reports no single customer at or above 10 percent for 2018' if r['value'].startswith('<') else '')
for r in rd('jhu_proquest_business_market_research_3pl.csv'):
    if r['metric'] == 'ups_amazon_customer_share_of_ups_revenue':
        c = '%s, %s, %s (via ProQuest Business Market Research Collection)' % (
            'The Insight Partners', r['pub_date'], r['report_title'])
        ups_add('2023', '11.8', c)
        ups_add('2024', r['value'], c)
for r in rd('jhu_ft_com_delivery_econ.csv'):
    if r['metric'] == 'Amazon share of UPS revenue 2024':
        ups_add('2024', '12', 'Financial Times, %s, %s (via FT.com)' % (r['article_date'], r['title']),
                'FT figure, rounded; The Insight Partners gives 11.8 for the same year')
for r in rd('jhu_ibisworld_amazon_facts.csv'):
    if r['metric'] == 'amazon_share_of_ups_revenue':
        ups_add(r['year'], r['value'], 'IBISWorld, %s (%s), %s, citing the UPS filing (via MyIBISWorld)' % (
            r['report_title'], r['report_code'], r['edition']))
for r in rd('jhu_sp_capital_iq_netadvantage_analyst_industry_facts.csv'):
    if r['metric'] == 'Amazon share of UPS revenue':
        ups_add(r['period'].replace('FY', ''), r['value'],
                'CFRA Equity Research, %s, %s (via S&P Capital IQ)' % (r['date'], r['title'].split(' (CFRA')[0] + ', CFRA report'))
for (y, _v) in sorted(ups):
    d = ups[(y, _v)]
    v = d['value']
    add('amazon_share_of_ups_revenue', 'Amazon share of UPS consolidated revenue', 'UPS', y,
        v if v.startswith('<') else num(v), 'percent', 'as stated', '; '.join(d['cites']), d['note'])

# ---------------------------------------------------------------- 3. Amazon Logistics parcel volume and share
PB = [r for r in rd('industry_pitney_bowes_parcel_index.csv') if r['carrier'] == 'AmazonLogistics']
LABEL = {'volume': ('Amazon Logistics US parcel volume', 'billion parcels'),
         'volume_share': ('Amazon Logistics share of US parcel volume', 'percent'),
         'revenue': ('Amazon Logistics US parcel revenue', 'USD billion'),
         'revenue_share': ('Amazon Logistics share of US parcel revenue', 'percent')}
for r in PB:
    if r['metric'] in LABEL:
        m, u = LABEL[r['metric']]
        add('amazon_logistics_parcels', m, 'Amazon Logistics', r['data_year'], num(r['value']), u, 'as stated',
            '%s, %s' % (r['source_name'], r['source_url']), r['note'])
have = {(r['data_year'], r['metric']) for r in PB}
for r in rd('logistics_us_parcel_volume.csv'):
    if r['carrier'] == 'Amazon Logistics' and r['share_of_volume_pct'] and (r['year'], 'volume_share') not in have \
            and r['share_basis'] == 'as published':
        add('amazon_logistics_parcels', 'Amazon Logistics share of US parcel volume', 'Amazon Logistics', r['year'],
            num(r['share_of_volume_pct']), 'percent', 'as stated',
            'Pitney Bowes Parcel Shipping Index, release year %s, %s' % (r['index_edition_release_year'], r['source_url']),
            'filled from logistics_us_parcel_volume.csv')
for r in rd('jhu_ibisworld_amazon_facts.csv'):
    if r['metric'] == 'amazon_logistics_parcel_share':
        add('amazon_logistics_parcels', 'Amazon Logistics share of US parcel market (ShipMatrix)', 'Amazon Logistics',
            r['year'], num(r['value']), 'percent', 'as stated',
            'IBISWorld, %s (%s), %s, citing ShipMatrix (via MyIBISWorld)' % (r['report_title'], r['report_code'], r['edition']),
            'IBISWorld notes Pitney Bowes volume shares differ')
for r in rd('jhu_gale_directory_library_parcels.csv'):
    if r['entity'] == 'Amazon Logistics':
        cit = 'Market Share Reporter, 33rd ed., %s, %s (via Gale Directory Library)' % (r['pub_date'], r['title'])
        if r['metric'] == 'us_parcel_share_pct':
            add('amazon_logistics_parcels', 'Amazon Logistics share of US parcel volume (ShipMatrix via Logistics Management)',
                'Amazon Logistics', r['period'], num(r['value']), 'percent', 'as stated',
                cit + ', citing ShipMatrix via Logistics Management, 2021-06-29', 'share by weekly volume')
        else:
            add('amazon_logistics_parcels', 'Amazon Logistics average weekday parcels (ShipMatrix via Logistics Management)',
                'Amazon Logistics', r['period'], num(r['value']), 'million parcels, average weekday (extract unit: %s)' % r['unit'],
                'as stated', cit + ', citing ShipMatrix via Logistics Management, 2021-06-29')

# ---------------------------------------------------------------- 4. IBISWorld 49311 General Warehousing and Storage
IB = 'IBISWorld, General Warehousing & Storage in the US (49311), Oct 2026 (via MyIBISWorld)'
for r in rd('jhu_ibisworld_industry_timeseries.csv'):
    if r['report_code'] == '49311' and r['metric'] == 'Annual revenue ($bn)':
        add('ibisworld_49311', 'Industry revenue', 'NAICS 49311 industry', r['year'], num(r['value']), 'USD billion',
            'IBISWorld estimate' if r['period_type'] == 'historical' else 'IBISWorld estimate or forecast', IB)
for r in rd('jhu_ibisworld_industry_snapshot.csv'):
    if r['report_code'] == '49311':
        add('ibisworld_49311', r['metric'], 'NAICS 49311 industry', '2026', r['value_2026'], 'as printed',
            'IBISWorld estimate', IB, 'CAGR 2021-26 %s; 2026-31 %s' % (r['cagr_2021_26'], r['cagr_2026_31'] or 'n/a'))
for r in rd('jhu_ibisworld_industry_segments.csv'):
    if r['report_code'] == '49311':
        add('ibisworld_49311', '%s: %s' % (r['table'], r['segment']), 'NAICS 49311 industry', '2026', num(r['share_pct']),
            'percent of industry revenue', 'IBISWorld estimate', IB, 'revenue %s %s' % (r['revenue'], r['unit']))
for r in rd('jhu_ibisworld_industry_company_share.csv'):
    if r['report_code'] == '49311' and r['company'] != 'Other Companies' and r['year'] in ('2022', '2026'):
        add('ibisworld_49311', 'Company share of industry revenue: ' + r['company'], 'NAICS 49311 industry', r['year'],
            num(r['share_pct']), 'percent', 'IBISWorld estimate', IB, 'revenue %s %s' % (r['revenue'], r['unit']))
add('ibisworld_49311', 'Amazon in top company list', 'NAICS 49311 industry', '2026', 'not listed', 'text',
    'inference from IBISWorld company table', IB, 'captive e-commerce warehousing is outside the industry definition')

# ---------------------------------------------------------------- 5. EIU online share of US retail
EIU_S = rd('jhu_eiu_data_us_online_retail_series.csv')
online = {r['year']: r for r in EIU_S if r['series_id'] == '158664'}
total = {r['year']: r for r in EIU_S if r['series_id'] == '534'}
for y in sorted(online):
    r = online[y]
    add('eiu_online_share', 'Online retail sales', 'United States', y, round(float(r['value']), 1), 'USD billion',
        r['status'], 'EIU Viewpoint Data, %s, %s (via EIU Data)' % (r['published'], r['title']))
for y in sorted(total):
    r = total[y]
    add('eiu_online_share', 'Retail sales', 'United States', y, round(float(r['value']), 1), 'USD billion', r['status'],
        'EIU Viewpoint Data, %s, %s (via EIU Data)' % (r['published'], r['title']))
for y in sorted(set(online) & set(total)):
    add('eiu_online_share', 'Online share of retail sales (online retail sales / retail sales)', 'United States', y,
        round(float(online[y]['value']) / float(total[y]['value']) * 100, 1), 'percent', 'derived',
        'EIU Viewpoint Data, %s (via EIU Data)' % online[y]['published'],
        'computed here from the two EIU series; %s' % online[y]['status'])
for r in rd('jhu_eiu_data_us_online_retail_facts.csv'):
    if r['metric'] in ('Online share of US retail sales', 'Amazon share of US online sales'):
        add('eiu_online_share', r['metric'], 'United States', '2025' if 'Online share' in r['metric'] else '',
            r['fact'], 'as printed', r['basis'],
            '%s, %s, %s (via EIU Data)' % (r['publication'], r['published'], r['title']))

HDR = ['topic', 'measure', 'entity', 'year', 'value', 'unit', 'basis', 'citation', 'note']
with open(os.path.join(P, 'market_context.csv'), 'w', newline='', encoding='utf-8') as fh:
    w = csv.writer(fh)
    w.writerow(HDR)
    for r in ROWS:
        w.writerow([r[h] for h in HDR])
print('market_context.csv', len(ROWS))
