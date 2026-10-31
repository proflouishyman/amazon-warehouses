import os as _os
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))  # project root, so scripts run from any checkout
import urllib.request, re, html, time, os, sys, csv
RAW=_ROOT+'/data/raw/labor/nlrb/list/'
os.makedirs(RAW,exist_ok=True)
import os
UA=os.environ.get('CRAWL_UA','Mozilla/5.0 (academic research crawler)')
def get(u):
    for a in range(4):
        try:
            return urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':UA}),timeout=40).read().decode('utf8','ignore')
        except Exception as e:
            time.sleep(3*(a+1))
    return ''
p=0; last_nonempty=-1
while True:
    fn=RAW+f'p{p:03d}.html'
    if os.path.exists(fn): t=open(fn).read()
    else:
        t=get(f'https://www.nlrb.gov/search/case/amazon?page={p}')
        open(fn,'w').write(t); time.sleep(0.6)
    n=len(re.findall(r'<a href="/case/[^"]+">[^<]*</a>\s*</h2>',t))
    print(p,n,flush=True)
    if n==0: break
    p+=1
