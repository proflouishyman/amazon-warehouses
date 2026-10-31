import os as _os
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))  # project root, so scripts run from any checkout
import re,html,glob,csv
D=_ROOT+'/data/raw/labor/nlrb/list/'
seen={};
for fn in sorted(glob.glob(D+'p*.html')):
    t=open(fn).read()
    blocks=t.split('<div class="wrapper-div">')[1:]
    for b in blocks:
        m=re.search(r'<a href="/case/([^"]+)">([^<]*)</a>\s*</h2>',b)
        if not m: continue
        cn=m.group(1); title=html.unescape(m.group(2)).strip()
        def f(label):
            x=re.search(r'<strong>'+label+r':\s*</strong>\s*([^<]*)<',b); return html.unescape(x.group(1)).strip() if x else ''
        seen[cn]=[cn,title,f('Date Filed'),f('Status'),f('Location'),f('Region Assigned')]
print(len(seen))
def code(cn): return cn.split('-')[1]
with open(_ROOT+'/data/processed/nlrb_amazon_cases_search_index.csv','w',newline='') as o:
    w=csv.writer(o); w.writerow(['case_number','case_type','case_name','date_filed','status','location','region','url'])
    for cn,r in seen.items(): w.writerow([cn,code(cn),r[1],r[2],r[3],r[4],r[5],'https://www.nlrb.gov/case/'+cn])
import collections
print(collections.Counter(code(c) for c in seen).most_common(12))
