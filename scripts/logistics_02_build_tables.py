"""Build the logistics tidy CSVs from values read out of the saved sources (see data/notes/logistics.md).
Run: python3 -I logistics_02_build_tables.py
Every row carries source_url, publisher, retrieved (2026-10-31), confidence and notes. Nothing here is interpolated."""
import os as _os
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))  # project root, so scripts run from any checkout
import csv, os
P=_ROOT+'/data/processed'
R='2026-10-31'
def write(name, header, rows):
    with open(f'{P}/{name}','w',newline='',encoding='utf8') as f:
        w=csv.writer(f); w.writerow(header); w.writerows(rows)
    print(name,len(rows))

SEC='https://www.sec.gov/Archives/edgar/data/1018724/'
K={ # fiscal year -> (accession folder, doc)
2000:('000089102000000622','n/a'),}
tenk_url={2000:'0001032210-01-500087/d10k405.txt',2001:'0001032210-02-000059/d10k405.htm',2002:'0000950149-03-000355/v87419ore10vk.htm',
2003:'0001193125-04-029488/d10k.htm',2004:'0001193125-05-047032/d10k.htm',2005:'0001193125-06-034166/d10k.htm',2006:'0001193125-07-034081/d10k.htm',
2007:'0001193125-08-024707/d10k.htm',2008:'0001193125-09-014406/d10k.htm',2009:'0001193125-10-016098/d10k.htm',2010:'0001193125-11-016253/d10k.htm',
2011:'0001193125-12-032846/d269317d10k.htm',2012:'0001193125-13-028520/d445434d10k.htm',2013:'0001018724-14-000006/amzn-20131231x10k.htm',
2014:'0001018724-15-000006/amzn-20141231x10k.htm',2015:'0001018724-16-000172/amzn-20151231x10k.htm',2016:'0001018724-17-000011/amzn-20161231x10k.htm',
2017:'0001018724-18-000005/amzn-20171231x10k.htm',2018:'0001018724-19-000004/amzn-20181231x10k.htm',2019:'0001018724-20-000004/amzn-20191231x10k.htm',
2020:'0001018724-21-000004/amzn-20201231.htm',2021:'0001018724-22-000005/amzn-20211231.htm',2022:'0001018724-23-000004/amzn-20221231.htm',
2023:'0001018724-24-000008/amzn-20231231.htm',2024:'0001018724-25-000004/amzn-20241231.htm',2025:'0001018724-26-000004/amzn-20251231.htm'}
def url(fy):
    a,d=tenk_url[fy].split('/'); return f"{SEC}{a.replace('-','')}/{d}"

# ---- 1. 10-K Item 2 square footage (thousand sq ft), as printed
# (fy, na_fulfil_leased, na_fulfil_owned, intl_leased, intl_owned, na_segment_leased, na_segment_owned, na_stores_leased, na_stores_owned)
T=[(2004,4465,0,1483,0),(2005,7560,0,2620,0),(2006,8434,0,3419,0),(2007,8905,0,4729,0),(2008,11973,0,5321,0),(2009,11848,0,5739,0),(2010,15761,0,10339,0),
(2011,26364,0,17690,0),(2012,35261,339,30761,22),(2013,48013,329,36131,122),(2014,57898,735,43969,272),
(2015,69890,1765,47976,670,67103,398),(2016,97215,2237,59175,1257,93716,586),(2017,131419,4406,67832,5190,147277,2140,20349,735),
(2018,153917,4467,72596,2085,165503,1977,19176,724),(2019,187148,5591,76868,2570,199473,1983,20072,662),(2020,285677,8461,104668,3449,298879,3813,21157,662),
(2021,370392,16663,129035,9601,383660,9863,22396,662),(2022,391598,22058,148146,12613,403984,13595,22881,662),(2023,413017,25630,173765,14802,424145,15438,22871,707),
(2024,448168,36869,176287,18958,457104,20741,23975,707),(2025,474128,45803,185814,20660,481153,25437,23932,706)]
rows=[]
for t in T:
    fy=t[0]; na=t[1]+t[2]; intl=t[3]+t[4]
    seg=(t[5]+t[6]) if len(t)>5 else ''
    stores=(t[7]+t[8]) if len(t)>7 else ''
    netseg=(seg-stores) if (seg!='' and stores!='') else ''
    note=('FY2004-2010: leased fulfillment and warehouse operations only (owns no real estate); FY2011 line is "Fulfillment and other" (includes data centers); '
          'FY2012+ line is "Fulfillment, data centers, and other" and includes AWS data centers in North America, so it OVERSTATES logistics space. '
          'NA segment columns (FY2015+) exclude corporate offices and AWS segment but include physical stores; net column subtracts stores (FY2017+).')
    rows.append([fy,t[1],t[2],na,t[3],t[4],intl,t[5] if len(t)>5 else '',t[6] if len(t)>5 else '',seg,stores,netseg,url(fy),'Amazon.com, Inc. Form 10-K, Item 2 Properties (via SEC EDGAR)',R,'high (as printed); definitions change',note])
write('logistics_sqft_by_year.csv',['fiscal_year_end_dec31','na_fulfil_dc_other_leased_ksf','na_fulfil_dc_other_owned_ksf','na_fulfil_dc_other_total_ksf','intl_fulfil_dc_other_leased_ksf','intl_fulfil_dc_other_owned_ksf','intl_total_ksf','na_segment_leased_ksf','na_segment_owned_ksf','na_segment_total_ksf','na_physical_stores_total_ksf','na_segment_less_stores_ksf','source_url','publisher','retrieved','confidence','caveats'],rows)

# early US fulfillment-centre counts (primary, 10-K text)
early=[(2000,8,3210,'Seven FCs listed (Seattle, New Castle, Fernley, Lexington, Campbellsville, Coffeyville, Grand Forks) plus McDonough GA whose closure was announced Jan 2001; 3.21 million sq ft for the seven listed','n/a (listed text of FY2000 10-K)'),
(2001,6,3120,'Six US FCs: New Castle, Fernley, Coffeyville, Lexington, Campbellsville, Grand Forks',''),
(2002,6,3100,'Six US FCs; plus six off-site storage/shipping facilities of ~1.1 million sq ft',''),
(2003,6,3200,'Six US FCs; plus six off-site facilities of ~1.2 million sq ft','')]
write('logistics_us_fc_counts_2000_2003.csv',['fiscal_year','us_fulfillment_centers','us_fc_sqft_ksf','description','note','source_url','publisher','retrieved','confidence'],
 [[y,n,s,d,'FY2000 count of 8 = 7 listed + McDonough (closure announced Jan 2001); my reading, label as approximate' if y==2000 else '',url(y),'Amazon.com, Inc. Form 10-K Item 2 (via SEC EDGAR)',R,'high' ] for y,n,s,d,_ in early])

# ---- 2. facility-count snapshots (no interpolation)
S=[
('2025-09-30','all US sites with OSHA 2025 filings',1399,'Moraine Research (CoStar+OSHA ITA CY2025+Amazon 10-K)','https://morainecre.com/resources/research/amazon-logistics-network-map','Published 2026-10-04, ninth edition; method matches OSHA filings to CoStar buildings; closed-mid-2025 sites still counted','medium (single third-party analysis)'),
('2025-09-30','inbound cross-dock',53,'Moraine Research','https://morainecre.com/resources/research/amazon-logistics-network-map','','medium'),
('2025-09-30','fulfillment sortable',84,'Moraine Research','https://morainecre.com/resources/research/amazon-logistics-network-map','','medium'),
('2025-09-30','fulfillment non-sortable',93,'Moraine Research','https://morainecre.com/resources/research/amazon-logistics-network-map','','medium'),
('2025-09-30','fulfillment other',123,'Moraine Research','https://morainecre.com/resources/research/amazon-logistics-network-map','partly unresolved types','low-medium'),
('2025-09-30','heavy-bulky XL fulfillment',39,'Moraine Research','https://morainecre.com/resources/research/amazon-logistics-network-map','','medium'),
('2025-09-30','sort center',162,'Moraine Research','https://morainecre.com/resources/research/amazon-logistics-network-map','','medium'),
('2025-09-30','delivery station',392,'Moraine Research','https://morainecre.com/resources/research/amazon-logistics-network-map','','medium'),
('2025-09-30','rural delivery station',192,'Moraine Research','https://morainecre.com/resources/research/amazon-logistics-network-map','','medium'),
('2025-09-30','same-day site',115,'Moraine Research','https://morainecre.com/resources/research/amazon-logistics-network-map','','medium'),
('2025-09-30','other or unresolved',146,'Moraine Research','https://morainecre.com/resources/research/amazon-logistics-network-map','','low'),
('2021','all US facilities ("more than 935")',935,'Transport Geography (data derived from MWPVL International)','https://transportgeography.org/?page_id=11857','Lower-bound wording; no per-type counts on page','medium'),
('2025-Q1','sortation centers (US, approx 90)',90,'MWPVL via redstagfulfillment.com (secondary)','https://redstagfulfillment.com/how-many-amazon-warehouses-are-there/','Conflicts with Moraine 162 sort centers in Sept 2025; definitions differ; do not combine','low'),
('2022-2023','buildings closed, cancelled or delayed (mainly US)',123,'MWPVL International','https://www.mwpvl.com/html/amazon_com.html','Over 123 buildings; context for the 2022-23 pullback','medium'),
]
write('logistics_facility_count_snapshots.csv',['as_of','facility_type','count','publisher_or_method','source_url','caveats','confidence','retrieved'],[[*x,R] for x in S])
