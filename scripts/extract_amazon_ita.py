"""Extract Amazon-affiliated establishments from OSHA ITA 300A files.
Matching rules live in scripts/amazon_names.py (shared with build_injury_tables.py) and are documented in
data/notes/injuries.md: Amazon.com* / Amazon Retail / Golden State FC LLC / Prime Now LLC / Amazon Leo, Kuiper, AWS company names,
bare "Amazon" with a blank or Amazon EIN, and Amazon's own org labels in the establishment name.
Excluded: contractors (ABM, Sizemore, SPS, C&W...), delivery-service partners filed under an Amazon-like name, Amazon Environmental
Inc. and Amazone USA Inc.
Also reports duplicates (same year/address/establishment_id) and drops exact superseded dupes by keeping latest created_timestamp.
"""
import os as _os
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))  # project root, so scripts run from any checkout
import csv, glob, re, collections, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from amazon_names import amazon_rule
csv.field_size_limit(10**9)
R=_ROOT+'/data/raw/injuries/'
O=_ROOT+'/data/processed/'
files=sorted(glob.glob(R+'x*/*.csv'))+[R+'cy2025.csv']
def num(x):
    try: return float(x)
    except: return None
rows=[];excl=collections.Counter()
for f in files:
    with open(f,newline='',encoding='utf-8-sig',errors='replace') as fh:
        for r in (dict((k.lower(),v) for k,v in d.items()) for d in csv.DictReader(fh)):
            c=r['company_name'].strip(); e=r['establishment_name'].strip()
            rule=amazon_rule(c,e,r.get('ein',''),r['naics_code'])
            if 'amazon' in (c+e).lower() and not rule:
                excl[(r['year_filing_for'][:4],c[:30])]+=1
            if not rule: continue
            rows.append(dict(year=int(float(r['year_filing_for'])),id=r['id'],match_rule=rule,ein=r.get('ein',''),company_name=c,establishment_name=e,
              establishment_id=r['establishment_id'],street_address=r['street_address'],city=r['city'],state=r['state'],zip_code=r['zip_code'],
              naics_code=r['naics_code'],industry_description=r['industry_description'],
              employees=num(r['annual_average_employees']),hours=num(r['total_hours_worked']),
              deaths=num(r['total_deaths']),dafw_cases=num(r['total_dafw_cases']),djtr_cases=num(r['total_djtr_cases']),
              other_cases=num(r['total_other_cases']),dafw_days=num(r['total_dafw_days']),djtr_days=num(r['total_djtr_days']),
              created_timestamp=r['created_timestamp'] if 'created_timestamp' in r else '',change_reason=r['change_reason']))
# dedupe: key year+address+city+state+name; keep latest id
best={}
for r in rows:
    k=(r['year'],r['street_address'].lower(),r['city'].lower(),r['state'],r['establishment_name'].lower())
    if k not in best or float(r['id'])>float(best[k]['id']): best[k]=r
print('matched',len(rows),'after dedupe',len(best))
out=[]
for r in best.values():
    h=r['hours']; 
    tot=None if None in (r['dafw_cases'],r['djtr_cases'],r['other_cases']) else r['dafw_cases']+r['djtr_cases']+r['other_cases']
    dart=None if None in (r['dafw_cases'],r['djtr_cases']) else r['dafw_cases']+r['djtr_cases']
    r['total_cases']=tot; r['dart_cases']=dart
    # same validity filter as the headline series in build_injury_tables.py: hours >= 1000, employees >= 1, 300-4500 hours per employee
    emp=r['employees']
    ok = bool(h and h>=1000 and tot is not None and emp and emp>=1 and 300<=h/emp<=4500)
    r['trc_rate']=round(tot*200000/h,3) if ok else None
    r['dart_rate']=round(dart*200000/h,3) if ok else None
    r['dafw_rate']=round(r['dafw_cases']*200000/h,3) if ok else None
    r['rate_valid']=bool(ok)
    out.append(r)
out.sort(key=lambda r:(r['year'],r['state'],r['city'],r['street_address']))
cols=list(out[0].keys())
with open(O+'osha_ita_amazon_establishments.csv','w',newline='') as fh:
    w=csv.DictWriter(fh,cols); w.writeheader(); w.writerows(out)
print('excluded name hits (year,company):'); 
for k,v in sorted(excl.items()): print(k,v)
print(collections.Counter((r['year'],r['naics_code']) for r in out).most_common(40))
