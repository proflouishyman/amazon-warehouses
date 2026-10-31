import os as _os
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))  # project root, so scripts run from any checkout
import csv, glob, sys, re, collections
csv.field_size_limit(10**9)
R=_ROOT+'/data/raw/injuries/'
files=sorted(glob.glob(R+'x*/*.csv'))+[R+'cy2025.csv']
for f in files:
    yc=collections.Counter(); n=0; am=collections.Counter()
    with open(f,newline='',encoding='utf-8-sig',errors='replace') as fh:
        for r in csv.DictReader(fh):
            n+=1; yc[r['year_filing_for']]+=1
            t=(r['company_name']+' '+r['establishment_name']).lower()
            if 'amazon' in t:
                am[(r['company_name'].strip()[:40])]+=1
    print(f.split('/')[-1],n,dict(yc))
    print('  ',am.most_common(12))
