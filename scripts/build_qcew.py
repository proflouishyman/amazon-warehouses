"""Build tidy QCEW tables for NAICS 493/4931/493110/492/4921/4922.
2001-2013 from BLS annual_by_industry zips; 2014-2025 from BLS CEW Open Data API files."""
import os as _os
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))  # project root, so scripts run from any checkout
import zipfile, csv, glob, os, re, io
RAW=_ROOT+'/data/raw/labor/'
OUT=_ROOT+'/data/processed/'
INDS={'493','4931','493110','492','4921','4922'}
titles={r['area_fips']:r['area_title'] for r in csv.DictReader(open(RAW+'area_titles.csv'))}
EX=RAW+'cew_extract/'; os.makedirs(EX,exist_ok=True)
# extract needed members
for z in sorted(glob.glob(RAW+'cew_*_annual_by_industry.zip')):
    y=re.search(r'cew_(\d{4})_',z).group(1)
    zf=zipfile.ZipFile(z)
    for n in zf.namelist():
        m=re.match(r'.*/\d{4}\.annual (\d+) ',n)
        if m and m.group(1) in INDS:
            fn=EX+f'cew_a_{y}_{m.group(1)}.csv'
            if not os.path.exists(fn): open(fn,'wb').write(zf.read(n))
files=sorted(glob.glob(EX+'cew_a_*_*.csv')+[f for f in glob.glob(RAW+'cew_a_*_*.csv')])
def level(f):
    if f=='US000': return 'national'
    if f.isdigit() and f.endswith('000'): return 'state'
    if f.isdigit(): return 'county'
    return None
own={'0':'total all ownerships','1':'federal gov','2':'state gov','3':'local gov','5':'private'}
cols=['year','area_fips','area_title','geo_level','state_fips','naics','ownership_code','ownership','establishments','avg_employment','total_annual_wages','avg_weekly_wage','avg_annual_pay','disclosure_code']
w_ns=csv.writer(open(OUT+'bls_qcew_naics49x_national_state_annual.csv','w',newline=''))
w_c=csv.writer(open(OUT+'bls_qcew_naics49x_county_private_annual.csv','w',newline=''))
w_ns.writerow(cols); w_c.writerow(cols)
seen=set(); n_ns=n_c=0
for fn in files:
    for r in csv.DictReader(open(fn,newline='')):
        if r['industry_code'] not in INDS: continue
        lv=level(r['area_fips'])
        if not lv: continue
        k=(r['year'],r['area_fips'],r['industry_code'],r['own_code'])
        if k in seen: continue
        seen.add(k)
        row=[r['year'],r['area_fips'],titles.get(r['area_fips'],''),lv,r['area_fips'][:2] if lv!='national' else '',r['industry_code'],r['own_code'],own.get(r['own_code'],r['own_code']),(r.get('annual_avg_estabs') or r.get('annual_avg_estabs_count')),r['annual_avg_emplvl'],r['total_annual_wages'],r['annual_avg_wkly_wage'],r['avg_annual_pay'],r['disclosure_code']]
        if lv in('national','state'): w_ns.writerow(row); n_ns+=1
        elif r['own_code']=='5': w_c.writerow(row); n_c+=1
print(n_ns,n_c,len(files))
