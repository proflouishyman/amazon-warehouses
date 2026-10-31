"""Parse legacy MWPVL table (c. 2012) of Amazon FCs: code, address, country, sq ft, month/year opened, description -> data/raw/facilities/mwpvl_legacy_parsed.csv (US rows only)"""
import os as _os
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))  # project root, so scripts run from any checkout
import re, html, csv
D=_ROOT+'/data/raw/facilities/'
t=open(D+'mwpvl_strategy.html',errors='ignore').read()
blocks=re.split(r'<tr valign="top"[^>]*>',t)[1:]
out=[]
for b in blocks:
    ps=[html.unescape(re.sub(r'<[^>]+>','',x)).replace('\xa0',' ').strip() for x in re.findall(r'<p[^>]*>(.*?)</p>',b,flags=re.S)]
    ps=[re.sub(r'\s+',' ',p) for p in ps if p.strip()]
    alt=re.search(r'alt="([^"]+)"',b)
    if not alt or alt.group(1)!='United States of America' or len(ps)<3 or not re.match(r'[A-Z0-9]{3,4}\d$',ps[0]): continue
    lis=[html.unescape(re.sub(r'<[^>]+>','',x)).replace('\xa0',' ').strip() for x in re.findall(r'<li[^>]*>(.*?)</li>',b,flags=re.S)]
    code,addr=ps[0],ps[1]
    sq=re.sub(r'[^\d]','',ps[2]) if re.search(r'\d',ps[2]) else ''
    my=' '.join(ps[3:5]) if len(ps)>=5 or (len(ps)==4 and re.search(r'(19|20)\d\d',ps[3])) else ''
    m=re.search(r'(19|20)\d\d',my)
    out.append(dict(code=code,address=addr,sq_ft=sq,opened_text=my,opened_year=m.group(0) if m else '',desc=' | '.join(lis)))
with open(D+'mwpvl_legacy_parsed.csv','w',newline='') as fh:
    w=csv.DictWriter(fh,fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
print(len(out)); 
for r in out[:6]+out[-4:]: print(r)
