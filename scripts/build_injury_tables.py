"""Build comparison tables. Reads raw ITA (all establishments) + BLS CSV. Run with python3 -I.
QC filter (applied identically to Amazon and non-Amazon for the 'qc' rates): hours>=1000, employees>=1,
 hours per employee between 300 and 4500, case counts present, DAFW+DJTR<=total cases (always true by construction).
Amazon vs non-Amazon is decided by scripts/amazon_names.py (see data/notes/injuries.md).
Dedupe: per (year, establishment_name, street_address, city, state) keep the highest submission id.
"""
import os as _os
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))  # project root, so scripts run from any checkout
import csv, glob, re, collections, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from amazon_names import amazon_rule
csv.field_size_limit(10**9)
R=_ROOT+'/data/raw/injuries/'
P=_ROOT+'/data/processed/'
files=sorted(glob.glob(R+'x*/*.csv'))+[R+'cy2025.csv']
def num(x):
    try: return float(x)
    except: return None
def naics6(x):
    try: return str(int(float(x)))[:6]
    except: return ''
best={}
for f in files:
    with open(f,newline='',encoding='utf-8-sig',errors='replace') as fh:
        for d in csv.DictReader(fh):
            r={k.lower():v for k,v in d.items()}
            c=r['company_name'].strip(); e=r['establishment_name'].strip()
            n=naics6(r['naics_code'])
            am=bool(amazon_rule(c,e,r.get('ein',''),n))
            if not (am or n in ('493110','492110') or n.startswith('493')): continue
            y=int(float(r['year_filing_for']))
            k=(y,e.lower(),r['street_address'].lower(),r['city'].lower(),r['state'])
            rid=float(r['id'])
            if k in best and best[k]['rid']>=rid: continue
            best[k]=dict(rid=rid,y=y,am=am,n=n,emp=num(r['annual_average_employees']),h=num(r['total_hours_worked']),
              dafw=num(r['total_dafw_cases']),djtr=num(r['total_djtr_cases']),oth=num(r['total_other_cases']),
              dd=num(r['total_dafw_days']),jd=num(r['total_djtr_days']),st=r['state'])
recs=list(best.values())
def ok(r):
    return None not in (r['emp'],r['h'],r['dafw'],r['djtr'],r['oth']) and r['h']>=1000 and r['emp']>=1 and 300<=r['h']/r['emp']<=4500
def group(rs):
    rs=list(rs); n=len(rs)
    h=sum(r['h'] for r in rs); emp=sum(r['emp'] for r in rs)
    dafw=sum(r['dafw'] for r in rs); djtr=sum(r['djtr'] for r in rs); oth=sum(r['oth'] for r in rs)
    tot=dafw+djtr+oth; dart=dafw+djtr
    f=lambda v: round(v*200000/h,2) if h else None
    return dict(n_establishments=n,avg_employees=round(emp),hours=round(h),total_cases=round(tot),dart_cases=round(dart),dafw_cases=round(dafw),
                dafw_days=round(sum(r['dd'] or 0 for r in rs)),djtr_days=round(sum(r['jd'] or 0 for r in rs)),
                trc_rate=f(tot),dart_rate=f(dart),dafw_rate=f(dafw))
SEG={'493110':lambda r:r['n']=='493110','492110':lambda r:r['n']=='492110','493110+492110':lambda r:r['n'] in('493110','492110'),
     'all_naics':lambda r:True,'493xxx':lambda r:r['n'].startswith('493')}
out=[]
for who in ('amazon','non_amazon'):
    for seg,fn in SEG.items():
        if who=='non_amazon' and seg=='all_naics': continue
        for y in sorted(set(r['y'] for r in recs)):
            rs=[r for r in recs if r['y']==y and fn(r) and (r['am']==(who=='amazon')) and ok(r)]
            if rs: out.append(dict(year=y,who=who,naics_segment=seg,**group(rs)))
cols=list(out[0].keys())
with open(P+'osha_ita_aggregates_by_year.csv','w',newline='') as fh:
    w=csv.DictWriter(fh,cols); w.writeheader(); w.writerows(out)
# state-level Amazon
st=[]
for y in sorted(set(r['y'] for r in recs)):
    for s in sorted(set(r['st'] for r in recs if r['am'] and r['y']==y)):
        rs=[r for r in recs if r['y']==y and r['am'] and r['st']==s and ok(r)]
        if rs: st.append(dict(year=y,state=s,**group(rs)))
with open(P+'osha_ita_amazon_by_state_year.csv','w',newline='') as fh:
    w=csv.DictWriter(fh,list(st[0].keys())); w.writeheader(); w.writerows(st)
# comparison
bls={}
for d in csv.DictReader(open(P+'bls_soii_rates.csv')): bls[(int(d['year']),d['naics'],d['case_type'])]=float(d['rate_per_100_fte'])
A={(o['year'],o['who'],o['naics_segment']):o for o in out}
comp=[]
for y in range(2016,2026):
    row=dict(year=y)
    for key,(who,seg) in {'amz_493110':('amazon','493110'),'amz_492110':('amazon','492110'),'amz_logistics':('amazon','493110+492110'),'amz_all':('amazon','all_naics'),'ita_nonamz_493110':('non_amazon','493110'),'ita_nonamz_492110':('non_amazon','492110')}.items():
        o=A.get((y,who,seg))
        row[key+'_n']=o['n_establishments'] if o else None
        row[key+'_hours']=o['hours'] if o else None
        for m in ('trc','dart','dafw'): row[f'{key}_{m}']=o[m+'_rate'] if o else None
    for key,nx in {'bls_493110':'493110','bls_493':'493000','bls_4921':'492100','bls_private':'000000'}.items():
        for m,ct in (('trc','total_recordable'),('dart','dart'),('dafw','days_away')): row[f'{key}_{m}']=bls.get((y,nx,ct))
    for m in ('trc','dart','dafw'):
        a=row[f'amz_493110_{m}']; b=row[f'bls_493110_{m}']; c=row[f'ita_nonamz_493110_{m}']
        row[f'ratio_amz493110_to_bls_{m}']=round(a/b,2) if a and b else None
        row[f'ratio_amz493110_to_itanonamz_{m}']=round(a/c,2) if a and c else None
    comp.append(row)
with open(P+'injury_comparison_by_year.csv','w',newline='') as fh:
    w=csv.DictWriter(fh,list(comp[0].keys())); w.writeheader(); w.writerows(comp)
print(len(recs),'records scanned')
for r in comp: print(r['year'],'AMZ493110',r['amz_493110_n'],r['amz_493110_trc'],r['amz_493110_dart'],'| AMZlog',r['amz_logistics_trc'],r['amz_logistics_dart'],'| ITAnon493110',r['ita_nonamz_493110_n'],r['ita_nonamz_493110_trc'],r['ita_nonamz_493110_dart'],'| BLS',r['bls_493110_trc'],r['bls_493110_dart'],'| BLSpriv',r['bls_private_trc'])
