import os as _os
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))  # project root, so scripts run from any checkout
import urllib.request, csv, os, time
from concurrent.futures import ThreadPoolExecutor
RAW=_ROOT+'/data/raw/labor/nlrb/case/'
os.makedirs(RAW,exist_ok=True)
import os
UA=os.environ.get('CRAWL_UA','Mozilla/5.0 (academic research crawler)')
cases=[r['case_number'] for r in csv.DictReader(open(_ROOT+'/data/processed/nlrb_amazon_cases_search_index.csv'))]
def go(cn):
    fn=RAW+cn+'.html'
    if os.path.exists(fn) and os.path.getsize(fn)>5000: return
    for a in range(4):
        try:
            t=urllib.request.urlopen(urllib.request.Request('https://www.nlrb.gov/case/'+cn,headers={'User-Agent':UA}),timeout=40).read().decode('utf8','ignore')
            open(fn,'w').write(t); time.sleep(0.4); return
        except Exception: time.sleep(3*(a+1))
with ThreadPoolExecutor(4) as ex: list(ex.map(go,cases))
print('done')
