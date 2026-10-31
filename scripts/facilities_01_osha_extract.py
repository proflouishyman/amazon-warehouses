"""Extract Amazon establishments from OSHA ITA 300A files -> data/raw/facilities/osha_amazon_rows.csv"""
import os as _os
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))  # project root, so scripts run from any checkout
import csv, glob, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from amazon_names import amazon_rule
csv.field_size_limit(10**8)
R=_ROOT+'/data/raw/facilities/osha_ita'
files=sorted(glob.glob(R+'/x_*/*.csv'))+[R+'/ITA_300A_Summary_Data_2025_through_08-31-2026.csv']
pat=re.compile(r'amazon|amzn|\bamz\b',re.I)
out=[]; keep=['establishment_name','company_name','ein','street_address','city','state','zip_code','naics_code','industry_description','annual_average_employees','total_hours_worked','total_deaths','total_dafw_cases','total_djtr_cases','total_other_cases','total_injuries','year_filing_for']
for f in files:
    with open(f,newline='',encoding='utf-8',errors='replace') as fh:
        rd=csv.DictReader(fh); rd.fieldnames=[h.lower() for h in rd.fieldnames]
        n=0
        for r in rd:
            if pat.search(r.get('company_name','')) or pat.search(r.get('establishment_name','')) or amazon_rule(r.get('company_name',''),r.get('establishment_name',''),r.get('ein',''),r.get('naics_code','')):
                d={k:r.get(k,'') for k in keep}; d['file']=os.path.basename(f); out.append(d); n+=1
        print(os.path.basename(f),n,file=sys.stderr)
with open(_ROOT+'/data/raw/facilities/osha_amazon_rows.csv','w',newline='') as fh:
    w=csv.DictWriter(fh,fieldnames=keep+['file']); w.writeheader(); w.writerows(out)
print(len(out))
