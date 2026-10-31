import os as _os
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))  # project root, so scripts run from any checkout
import csv,collections
P=_ROOT+'/data/processed/'
emp=collections.defaultdict(float); n=collections.defaultdict(int); sup=collections.defaultdict(int); tot=collections.defaultdict(set)
for r in csv.DictReader(open(P+'amazon_site_counties_naics493_annual.csv')):
    if r['naics']!='493': continue
    tot[r['year']].add(r['county_fips'])
    if r['disclosure_code']=='N' or r['avg_employment'] in('','0') and r['disclosure_code']: sup[r['year']]+=1; continue
    emp[r['year']]+=float(r['avg_employment']); n[r['year']]+=1
nat={r['year']:float(r['avg_employment']) for r in csv.DictReader(open(P+'bls_qcew_naics49x_national_state_annual.csv')) if r['area_fips']=='US000' and r['naics']=='493' and r['ownership_code']=='5'}
with open(P+'amazon_site_counties_naics493_summary.csv','w',newline='') as o:
    w=csv.writer(o); w.writerow(['year','site_counties_with_493_rows','site_counties_disclosed','site_counties_suppressed_or_zero','site_counties_private_493_employment_disclosed_sum','us_private_493_employment','share_of_us'])
    for y in sorted(emp): w.writerow([y,len(tot[y]),n[y],sup[y],int(emp[y]),int(nat[y]),round(emp[y]/nat[y],4)])
