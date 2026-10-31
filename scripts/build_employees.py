import os as _os
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))  # project root, so scripts run from any checkout
import re,glob,html,csv,os
RAW=_ROOT+'/data/raw/labor/10k/'
rows=[]
for line in open(RAW+'list.tsv'):
    d,f,a,p=line.rstrip('\n').split('\t')
    if f=='10-K/A': continue
    fn=glob.glob(RAW+f'{d}_{f.replace("/","-")}_{a}.*')[0]
    t=open(fn,errors='ignore').read(); t=re.sub(r'<[^>]+>',' ',t); t=re.sub(r'\s+',' ',html.unescape(t))
    m=re.search(r'(?:employed|we employed) (?:approximately )?([\d,]+) (?:full-time and part- ?time )?(?:full-time )?employees',t)
    if not m: raise SystemExit('no match '+fn)
    n=int(m.group(1).replace(',',''))
    i=m.start(); quote=t[max(0,i-40):m.end()+30].strip()
    fy=int(d[:4])-1
    nd=a.replace('-','')
    url=f'https://www.sec.gov/Archives/edgar/data/1018724/{nd}/'+(p if p else a+'.txt')
    rows.append([fy,n,'full-time' if fy==1997 else 'full-time and part-time',d,f,a,url,quote])
with open(_ROOT+'/data/processed/amazon_employees_by_year.csv','w',newline='') as o:
    w=csv.writer(o); w.writerow(['fiscal_year_end_dec31','employees','headcount_basis','filing_date','form','sec_accession','source_url','quoted_text'])
    for r in sorted(rows): w.writerow(r)
print(len(rows))
