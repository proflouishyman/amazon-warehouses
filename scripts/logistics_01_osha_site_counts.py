"""Count distinct Amazon-operated US sites per year from OSHA ITA 300A rows (extracted by the facilities domain).
Run: python3 -I logistics_01_osha_site_counts.py
Method: keep rows that scripts/amazon_names.py classifies as Amazon-operated and whose establishment_name carries an Amazon site code
(3-4 char token, letters first, e.g. 'DSF8', 'JFK8'); dedupe by (year, code); group by NAICS (492110 courier/express ->
mostly delivery stations + some sort/cross-dock; 493110 general warehousing -> mostly FCs, sort centers, cross-docks).
This is a LOWER BOUND on the network: only filing establishments appear. Form 300A electronic submission has covered NAICS 4931
sites with 20+ employees since the 2016 data year (the 2019 and 2023 rules changed only Forms 300 and 301), so growth reflects
network growth and improving compliance, not rule changes; 2016 data were collected late with low compliance. Site types cannot
be separated cleanly from NAICS.
"""
import os as _os
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))  # project root, so scripts run from any checkout
import csv, re, collections, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from amazon_names import amazon_rule
BASE=_ROOT+'/data'
rows=list(csv.DictReader(open(f'{BASE}/raw/facilities/osha_amazon_rows.csv',encoding='utf8')))
pat=re.compile(r'(?:^|[\s:\-])([A-Z]{3}[0-9]{1,2}|[A-Z][A-Z0-9]{2,3}[0-9])\s*$')
seen={}
for r in rows:
    if not amazon_rule(r['company_name'],r['establishment_name'],r.get('ein',''),r['naics_code']): continue
    m=pat.search(r['establishment_name'].strip())
    if not m: continue
    yr=int(float(r['year_filing_for']))
    naics=str(int(float(r['naics_code']))) if r['naics_code'] else ''
    key=(yr,m.group(1))
    emp=float(r['annual_average_employees'] or 0)
    if key not in seen or emp>seen[key][1]: seen[key]=(naics,emp,r['state'])
out=collections.defaultdict(lambda:collections.Counter())
emp=collections.defaultdict(lambda:collections.Counter())
for (yr,code),(n,e,st) in seen.items():
    g={'492110':'naics_492110_courier_express','493110':'naics_493110_general_warehousing'}.get(n,'other_naics')
    out[yr][g]+=1; emp[yr][g]+=e
with open(f'{BASE}/processed/logistics_osha_site_counts_by_year.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['year','group','distinct_site_codes','sum_avg_employees','basis','caveat'])
    for yr in sorted(out):
        for g in sorted(out[yr]):
            w.writerow([yr,g,out[yr][g],int(emp[yr][g]),'OSHA ITA 300A via facilities-domain extract','lower bound; only filing sites appear; early-year compliance low; type inferred from NAICS only'])
for yr in sorted(out): print(yr,dict(out[yr]),sum(out[yr].values()))
