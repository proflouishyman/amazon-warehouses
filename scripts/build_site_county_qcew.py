"""Join facilities.csv (county name + state) to QCEW county fips by name; emit tidy county NAICS 493 series
for counties that contain >=1 listed Amazon site. Name-join only; unmatched rows are listed."""
import os as _os
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))  # project root, so scripts run from any checkout
import csv, re, collections
P=_ROOT+'/data/'
ST={'AL':'Alabama','AK':'Alaska','AZ':'Arizona','AR':'Arkansas','CA':'California','CO':'Colorado','CT':'Connecticut','DE':'Delaware','DC':'District of Columbia','FL':'Florida','GA':'Georgia','HI':'Hawaii','ID':'Idaho','IL':'Illinois','IN':'Indiana','IA':'Iowa','KS':'Kansas','KY':'Kentucky','LA':'Louisiana','ME':'Maine','MD':'Maryland','MA':'Massachusetts','MI':'Michigan','MN':'Minnesota','MS':'Mississippi','MO':'Missouri','MT':'Montana','NE':'Nebraska','NV':'Nevada','NH':'New Hampshire','NJ':'New Jersey','NM':'New Mexico','NY':'New York','NC':'North Carolina','ND':'North Dakota','OH':'Ohio','OK':'Oklahoma','OR':'Oregon','PA':'Pennsylvania','RI':'Rhode Island','SC':'South Carolina','SD':'South Dakota','TN':'Tennessee','TX':'Texas','UT':'Utah','VT':'Vermont','VA':'Virginia','WA':'Washington','WV':'West Virginia','WI':'Wisconsin','WY':'Wyoming'}
def norm(s): 
    s=s.lower().replace('saint ','st. ').replace('st ','st. ')
    s=re.sub(r' (county|parish|city and borough|borough|census area|municipality)$','',s.strip())
    return re.sub(r'[^a-z0-9. ]','',s).strip()
titles={}
for r in csv.DictReader(open(P+'raw/labor/area_titles.csv')):
    f=r['area_fips']
    if f.isdigit() and not f.endswith('000'):
        t=r['area_title']
        if ', ' in t:
            c,s=t.rsplit(', ',1)
            titles[(norm(c),s)]=(f,t)
fac=list(csv.DictReader(open(P+'processed/facilities.csv')))
site=collections.defaultdict(lambda: collections.Counter()); unmatched=collections.Counter(); first={}
for x in fac:
    if not x['county'] or x['state'] not in ST: unmatched[('no county/state',x['state'])]+=1; continue
    k=(norm(x['county']),ST[x['state']])
    hit=titles.get(k) or titles.get((norm(x['county'])+' city',ST[x['state']]))
    if not hit: unmatched[(x['county'],x['state'])]+=1; continue
    site[hit[0]][x['facility_type']]+=1
    if x['opening_year'].isdigit(): first[hit[0]]=min(first.get(hit[0],9999),int(x['opening_year']))
print('site counties matched',len(site),'unmatched rows',sum(unmatched.values()))
ow=csv.writer(open(P+'processed/amazon_site_counties_naics493_annual.csv','w',newline=''))
ow.writerow(['year','county_fips','county_title','naics','establishments','avg_employment','avg_weekly_wage','disclosure_code','listed_sites_total','listed_sites_by_type','earliest_listed_opening_year'])
for r in csv.DictReader(open(P+'processed/bls_qcew_naics49x_county_private_annual.csv')):
    if r['area_fips'] in site and r['naics'] in('493','4931','493110'):
        s=site[r['area_fips']]
        ow.writerow([r['year'],r['area_fips'],r['area_title'],r['naics'],r['establishments'],r['avg_employment'],r['avg_weekly_wage'],r['disclosure_code'],sum(s.values()),';'.join(f'{k}={v}' for k,v in sorted(s.items())),first.get(r['area_fips'],'')])
with open(P+'processed/amazon_site_county_match_unmatched.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['county_or_reason','state','n_facility_rows'])
    for (a,b),n in unmatched.most_common(): w.writerow([a,b,n])
