"""Census batch geocoder (benchmark Public_AR_Current, vintage Current_Current). Reads facilities_pregeocode.csv, writes raw responses to data/raw/facilities/census_geocode_*.csv and data/processed/facilities_geocoded_cache.csv"""
import os as _os
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))  # project root, so scripts run from any checkout
import csv, subprocess, io, re, sys, os
P=_ROOT+'/data/'
rows=list(csv.DictReader(open(P+'processed/facilities_pregeocode.csv')))
def clean_street(s):
    s=re.sub(r'\b(suite|ste|bldg|building|unit|su)\b.*$','',s,flags=re.I).strip(' ,')
    return s
inp=[]
for i,r in enumerate(rows):
    if r['street_address'] and r['city'] and r['state']:
        inp.append([i,clean_street(r['street_address']),r['city'],r['state'],r['zip']])
res={}
for k in range(0,len(inp),800):
    chunk=inp[k:k+800]; fn=P+f'raw/facilities/census_input_{k//800}.csv'
    with open(fn,'w',newline='') as fh: csv.writer(fh).writerows(chunk)
    out=P+f'raw/facilities/census_geocode_{k//800}.csv'
    subprocess.run(['curl','-s','-m','280','--form',f'addressFile=@{fn}','--form','benchmark=Public_AR_Current','--form','vintage=Current_Current','https://geocoding.geo.census.gov/geocoder/geographies/addressbatch','-o',out],check=True)
    for rec in csv.reader(open(out,newline='',encoding='utf-8',errors='replace')):
        if len(rec)>=6 and rec[2]=='Match':
            ll=rec[5].split(',')
            geo=rec[8:12] if len(rec)>=12 else ['']*4   # tigerline id, side, state fips, county fips
            res[int(rec[0])]=dict(lat=ll[1],lon=ll[0],matched=rec[4],type=rec[3],statefp=rec[8] if len(rec)>8 else '',countyfp=rec[9] if len(rec)>9 else '')
    print(k,len(res),file=sys.stderr)
import json; json.dump(res,open(P+'processed/facilities_geocode_cache.json','w'))
print(len(inp),len(res))
