"""Apply geocodes, county names, ZIP-centroid fallback; write data/processed/facilities.csv"""
import os as _os
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))  # project root, so scripts run from any checkout
import csv, json, re, collections
P=_ROOT+'/data/'
C=P+'raw/facilities/census_ref/'
rows=list(csv.DictReader(open(P+'processed/facilities_pregeocode.csv')))
res={int(k):v for k,v in json.load(open(P+'processed/facilities_geocode_cache.json')).items()}
cname={}
for l in open(P+'raw/facilities/national_county2020.txt'):
    a=l.rstrip('\n').split('|')
    if a[0]=='STATE': continue
    cname[a[1]+a[2]]=(a[4],a[0])
zc={}
for l in open(C+'2020_Gaz_zcta_national.txt',encoding='utf-8'):
    a=l.split('\t')
    if a[0]=='GEOID': continue
    zc[a[0]]=(a[5].strip(),a[6].strip())
best={}
for l in open(C+'rel.txt',encoding='utf-8-sig'):
    a=l.rstrip('\n').split('|')
    if a[0]=='OID_ZCTA5_20' or not a[1] or not a[9]: continue
    try: ar=int(a[16])
    except: continue
    if a[1] not in best or ar>best[a[1]][0]: best[a[1]]=(ar,a[9])
order={'low':0,'medium':1,'high':2}; inv={v:k for k,v in order.items()}
out=[]
for i,r in enumerate(rows):
    g=res.get(i); r['geo_method']='none'; r['geo_note']=''
    if g:
        r['lat'],r['lon']=g['lat'],g['lon']; fp=g['statefp']+g['countyfp']
        r['county']=cname.get(fp,(r['county'],''))[0].replace(' County','') or r['county']
        mz=re.search(r'(\d{5})\s*$',g['matched']); r['zip']=mz.group(1) if mz else r['zip']; r['geo_method']='census_batch_'+g['type'].lower(); r['geo_note']='matched as: '+g['matched']
    elif r['zip'] and r['zip'] in zc:
        r['lat'],r['lon']=zc[r['zip']]; r['geo_method']='zip_centroid_census_zcta2020'
        r['geo_note']='Census geocoder found no street match; ZIP-code centroid, approximate (several km)'
        if not r['county'] and r['zip'] in best: r['county']=cname.get(best[r['zip']][1],('',''))[0].replace(' County','')
    cf=order[r['confidence']]
    if r['geo_method'].startswith('zip_centroid') or r['geo_method']=='none': cf=min(cf,1) if r['geo_method'].startswith('zip') else 0
    elif 'non_exact' in r['geo_method']: cf=min(cf,1)
    r['confidence']=inv[cf]
    out.append(r)
out.sort(key=lambda r:(r['state'],r['city'],r['site_code']))
cols=['facility_id','site_code','facility_type','street_address','city','state','zip','county','lat','lon','geo_method','opening_year','opening_year_basis','opening_year_source_url','first_osha_filing_year','last_osha_filing_year','closing_year','status','sq_ft','sq_ft_source','type_basis','geo_note','confidence','sources','source_url','source_detail']
for n,r in enumerate(out,1): r['facility_id']='F%04d'%n
with open(P+'processed/facilities.csv','w',newline='') as fh:
    w=csv.DictWriter(fh,fieldnames=cols,extrasaction='ignore'); w.writeheader(); w.writerows(out)
print(len(out),collections.Counter(r['geo_method'] for r in out),collections.Counter(r['confidence'] for r in out))
