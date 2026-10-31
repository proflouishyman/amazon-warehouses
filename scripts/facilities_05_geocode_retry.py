"""Second geocoding pass for rows the first pass missed: street + zip only, with aggressive street cleaning."""
import os as _os
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))  # project root, so scripts run from any checkout
import csv, subprocess, re, json, sys
P=_ROOT+'/data/'
rows=list(csv.DictReader(open(P+'processed/facilities_pregeocode.csv')))
res={int(k):v for k,v in json.load(open(P+'processed/facilities_geocode_cache.json')).items()}
def clean(s):
    s=s.split(',')[0]
    s=re.sub(r'\b(suite|ste|bldg|building|unit|su|floor|fl|#)\b.*$','',s,flags=re.I)
    s=re.sub(r'\s+(?:[A-Z][a-z]+ ){0,2}(?:NJ|PA|IL|CA|TX)\s*$','',s)
    return s.strip(' .,-')
inp=[[i,clean(r['street_address']),'',r['state'],r['zip']] for i,r in enumerate(rows) if i not in res and r['street_address'] and r['state'] and r['zip'] and re.match(r'\d',r['street_address'])]
fn=P+'raw/facilities/census_input_retry.csv'; csv.writer(open(fn,'w',newline='')).writerows(inp)
out=P+'raw/facilities/census_geocode_retry.csv'
subprocess.run(['curl','-s','-m','280','--form',f'addressFile=@{fn}','--form','benchmark=Public_AR_Current','--form','vintage=Current_Current','https://geocoding.geo.census.gov/geocoder/geographies/addressbatch','-o',out],check=True)
n=0
for rec in csv.reader(open(out,newline='',encoding='utf-8',errors='replace')):
    if len(rec)>=10 and rec[2]=='Match':
        ll=rec[5].split(','); res[int(rec[0])]=dict(lat=ll[1],lon=ll[0],matched=rec[4],type=rec[3]+'_retry',statefp=rec[8],countyfp=rec[9]); n+=1
json.dump(res,open(P+'processed/facilities_geocode_cache.json','w'))
print(len(inp),n,len(res))
