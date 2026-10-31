"""Parse TaxJar FC and sort-center pages -> data/raw/facilities/taxjar_parsed.csv"""
import os as _os
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))  # project root, so scripts run from any checkout
import re, csv, html
D=_ROOT+'/data/raw/facilities/'
def text(fn):
    t=open(D+fn,errors='ignore').read()
    t=re.sub(r'<script.*?</script>|<style.*?</style>','',t,flags=re.S)
    t=re.sub(r'</(p|li|h\d|div|br)>|<br\s*/?>','\n',t)
    t=re.sub(r'<[^>]+>','',t)
    return [re.sub(r'\s+',' ',html.unescape(l)).strip() for l in t.split('\n') if l.strip()]
STATES={'Alabama':'AL','Alaska':'AK','Arizona':'AZ','Arkansas':'AR','California':'CA','Colorado':'CO','Connecticut':'CT','Delaware':'DE','Florida':'FL','Georgia':'GA','Idaho':'ID','Illinois':'IL','Indiana':'IN','Iowa':'IA','Kansas':'KS','Kentucky':'KY','Louisiana':'LA','Maine':'ME','Maryland':'MD','Massachusetts':'MA','Michigan':'MI','Minnesota':'MN','Mississippi':'MS','Missouri':'MO','Montana':'MT','Nebraska':'NE','Nevada':'NV','New Hampshire':'NH','New Jersey':'NJ','New Mexico':'NM','New York':'NY','North Carolina':'NC','North Dakota':'ND','Ohio':'OH','Oklahoma':'OK','Oregon':'OR','Pennsylvania':'PA','Rhode Island':'RI','South Carolina':'SC','South Dakota':'SD','Tennessee':'TN','Texas':'TX','Utah':'UT','Vermont':'VT','Virginia':'VA','Washington':'WA','West Virginia':'WV','Wisconsin':'WI','Wyoming':'WY'}
out=[]
# FC page: "#CODE [& #CODE] - street, city, ST zip - X County"
L=text('blog_taxjar_com_amazon_warehouse_locations_.html')
for l in L:
    if not l.startswith('#'): continue
    parts=re.split(r'\s+[–—-]\s+',l)
    if len(parts)<2: continue
    codes=re.findall(r'[A-Z]{3,4}\d{1,2}',parts[0])
    addr=parts[1]; county=parts[2] if len(parts)>2 else ''
    for c in codes: out.append(dict(page='fc',code=c,raw_address=addr,county=county.replace(' County','').strip(),raw=l))
# sort page: HTML table rows State | codes | address | county
t=open(D+'taxjar_sort_centers.html',errors='ignore').read()
for tr in re.findall(r'<tr>(.*?)</tr>',t,flags=re.S):
    tds=[html.unescape(re.sub(r'<[^>]+>','',x)).replace('\xa0',' ').strip() for x in re.findall(r'<td>(.*?)</td>',tr,flags=re.S)]
    if len(tds)!=4 or tds[0]=='State': continue
    for c in re.findall(r'[A-Z]{3,4}\d{1,2}',tds[1]): out.append(dict(page='sort',code=c,raw_address=tds[2],county=tds[3].replace(' County','').strip(),raw=' | '.join(tds)))
with open(D+'taxjar_parsed.csv','w',newline='') as fh:
    w=csv.DictWriter(fh,fieldnames=['page','code','raw_address','county','raw']); w.writeheader(); w.writerows(out)
import collections; print(collections.Counter(r['page'] for r in out))
