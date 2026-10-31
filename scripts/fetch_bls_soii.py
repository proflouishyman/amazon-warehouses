"""Fetch BLS SOII incidence rates (per 100 FTE) via BLS Public Data API v1 (no key).
Series ID: IS|II + U + supersector + industry(6) + datatype(3 = injury+illness rate, size class 0) + casetype + area(100=national)
 casetype 1 total recordable, 2 DART (days away/restricted/transfer), 3 days away, 4 job transfer/restriction.
IS = reference years 2014+ (NAICS 2012+), II = through 2013.
"""
import os as _os
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))  # project root, so scripts run from any checkout
import json, csv, urllib.request, time, datetime
RAW=_ROOT+'/data/raw/injuries/bls_soii_api_responses.json'
OUT=_ROOT+'/data/processed/bls_soii_rates.csv'
IND={'000000':('000','Private industry, all workers'),'SP2TRW':('TTU','Transportation and warehousing (NAICS 48-49)'),
     '493000':('TTU','Warehousing and storage (NAICS 493)'),'493100':('TTU','Warehousing and storage (NAICS 4931)'),
     '493110':('TTU','General warehousing and storage (NAICS 493110/49311)'),
     '492000':('TTU','Couriers and messengers (NAICS 492)'),'492100':('TTU','Couriers and express delivery services (NAICS 4921)')}
CT={'1':'total_recordable','2':'dart','3':'days_away','4':'job_transfer_restriction'}
def q(ids,sy,ey):
    req=urllib.request.Request("https://api.bls.gov/publicAPI/v1/timeseries/data/",json.dumps({"seriesid":ids,"startyear":str(sy),"endyear":str(ey)}).encode(),{"Content-Type":"application/json"})
    return json.load(urllib.request.urlopen(req,timeout=90))
raw=[];rows={}
for pre,(sy,ey) in [('II',(2003,2012)),('II',(2013,2013)),('IS',(2014,2023)),('IS',(2024,2024))]:
    ids=[]; meta={}
    for ind,(ss,name) in IND.items():
        s = '000' if ind=='000000' else ss
        for c in CT:
            sid=f"{pre}U{s}{ind}3{c}100"; ids.append(sid); meta[sid]=(ind,name,c)
    # API v1 caps 25 series per call
    for i in range(0,len(ids),25):
        j=q(ids[i:i+25],sy,ey); raw.append(j); time.sleep(1)
        for s in j['Results']['series']:
            ind,name,c=meta[s['seriesID']]
            for d in s['data']:
                rows[(int(d['year']),ind,CT[c])]=(name,float(d['value']),s['seriesID'])
json.dump(dict(retrieved='2026-10-31',responses=raw),open(RAW,'w'))
with open(OUT,'w',newline='') as f:
    w=csv.writer(f); w.writerow(['year','naics','industry','case_type','rate_per_100_fte','series_id','source'])
    for (y,ind,c),(name,v,sid) in sorted(rows.items()):
        w.writerow([y,ind,name,c,v,sid,'BLS SOII via api.bls.gov v1, retrieved 2026-10-31'])
print(len(rows),'values; years',min(k[0] for k in rows),max(k[0] for k in rows))
