"""Parse FACTS (site code, city, state, type label, sq ft, year opened, status) from archived
MWPVL Amazon pages (HTML text tables only; image tables are not OCRed). No prose is stored.
Inputs : data/raw/mwpvl_wayback/<ts>.html (fetched via web.archive.org/web/<ts>id_/<url>), data/raw/mwpvl_wayback/cdx.json
Outputs: data/processed/mwpvl_wayback_facts.csv, mwpvl_wayback_sites.csv, mwpvl_wayback_snapshots.csv
"""
import csv, glob, json, os, re, sys
from html.parser import HTMLParser
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = f'{ROOT}/data/raw/mwpvl_wayback'; OUT = f'{ROOT}/data/processed'

class P(HTMLParser):
    def __init__(s):
        super().__init__(convert_charrefs=True); s.rows=[]; s.stack=[]; s.skip=0
    def handle_starttag(s,t,a):
        a=dict(a)
        if t in('script','style'): s.skip+=1
        if t=='tr': s.stack.append({'cells':[],'cur':None})
        elif t in('td','th') and s.stack: s.stack[-1]['cur']={'txt':[],'alt':[]}
        elif t=='img' and s.stack and s.stack[-1]['cur'] is not None and a.get('alt'): s.stack[-1]['cur']['alt'].append(a['alt'])
        elif t in('p','li','br') and s.stack and s.stack[-1]['cur'] is not None: s.stack[-1]['cur']['txt'].append(' ')
    def handle_endtag(s,t):
        if t in('script','style'): s.skip-=1
        if t in('td','th') and s.stack and s.stack[-1]['cur'] is not None:
            r=s.stack[-1]; c=r['cur']; r['cells'].append((re.sub(r'\s+',' ',''.join(c['txt'])).strip(),' '.join(c['alt']))); r['cur']=None
        elif t=='tr' and s.stack: s.rows.append(s.stack.pop()['cells'])
    def handle_data(s,d):
        if s.skip: return
        for r in s.stack:
            if r['cur'] is not None: r['cur']['txt'].append(d)

STATES = {'Alabama':'AL','Alaska':'AK','Arizona':'AZ','Arkansas':'AR','California':'CA','Colorado':'CO','Connecticut':'CT','Delaware':'DE','Florida':'FL','Georgia':'GA','Hawaii':'HI','Idaho':'ID','Illinois':'IL','Indiana':'IN','Iowa':'IA','Kansas':'KS','Kentucky':'KY','Louisiana':'LA','Maine':'ME','Maryland':'MD','Massachusetts':'MA','Michigan':'MI','Minnesota':'MN','Mississippi':'MS','Missouri':'MO','Montana':'MT','Nebraska':'NE','Nevada':'NV','New Hampshire':'NH','New Jersey':'NJ','New Mexico':'NM','New York':'NY','North Carolina':'NC','North Dakota':'ND','Ohio':'OH','Oklahoma':'OK','Oregon':'OR','Pennsylvania':'PA','Rhode Island':'RI','South Carolina':'SC','South Dakota':'SD','Tennessee':'TN','Texas':'TX','Utah':'UT','Vermont':'VT','Virginia':'VA','Washington':'WA','West Virginia':'WV','Wisconsin':'WI','Wyoming':'WY'}
MONTHS = 'January February March April May June July August September October November December'.split()

def parse_addr(a):
    parts=[p.strip() for p in a.split(',')]
    for i in range(len(parts)-1,-1,-1):
        m=re.match(r'^(%s)\b'%'|'.join(sorted(STATES,key=len,reverse=True)),parts[i])
        if m: return (parts[i-1] if i>0 else ''), STATES[m.group(1)]
    return '',''

def classify(desc, addr):
    d=desc.lower(); t=[]
    if 'sortation' in d or 'sort center' in d: t.append('sortation_center')
    if 'prime now' in d or 'hub' in d and 'prime' in d: t.append('prime_now')
    if 'fresh' in d or 'pantry' in d or 'grocery' in d: t.append('fresh_pantry')
    if 'return' in d: t.append('returns')
    if 'delivery station' in d: t.append('delivery_station')
    if 'cross' in d and 'dock' in d: t.append('crossdock')
    if 'non-sortable' in d or 'non sortable' in d or 'nonsortable' in d: t.append('non_sortable_fc')
    elif 'sortable' in d: t.append('sortable_fc')
    if any(k in d for k in ('specialty','jewelry','shoe','apparel','media','heavy','bulky','kiva','robot')) and not t: t.append('specialty')
    return '+'.join(t) if t else 'unspecified'

def parse_snapshot(path, snap_date):
    p=P(); p.feed(open(path,encoding='latin1').read()); out=[]; skipped=0
    sy,sm=int(snap_date[:4]),int(snap_date[5:7])
    for r in p.rows:
        if len(r)!=6: continue
        code_cell,addr,ctry,sq,yr,desc=[x[0] for x in r[:1]]+[r[1][0],r[2][1] or r[2][0],r[3][0],r[4][0],r[5][0]]
        if code_cell=='Fulfillment Center' or not addr: continue
        city,st=parse_addr(addr)
        if not st: continue                      # non-US (Canada, ROW) or unparseable
        if ctry and 'United States' not in ctry and ctry.strip(): continue
        codes=[c for c in re.split(r'[\s/]+',code_cell) if re.fullmatch(r'[A-Z0-9]{3,5}',c) and re.search(r'\d',c)]
        if not codes: skipped+=1; continue        # US row with no site code
        m=re.search(r'\d[\d,]*',sq); sqft=int(m.group().replace(',','')) if m else ''
        ym=re.search(r'\b(19|20)\d\d\b',yr); yo=int(ym.group()) if ym else ''
        qm=re.search(r'Q([1-4])',yr); mm=next((i+1 for i,n in enumerate(MONTHS) if n in yr),(int(qm.group(1))*3-2 if qm else 0))
        text=(yr+' '+desc).lower()
        sched=re.search(r'(scheduled|to be|will be|going to be|plans? to|expected to|future)[^.]{0,40}clos',text) or 'will replace' in text
        if re.search(r'planned|conjecture|rumou?r|proposed|tbd|will open|to be opened|under construction',text): status,basis='planned','text_says_planned'
        elif ('closed' in text or 'closure' in text) and not sched: status,basis='closed','text_says_closed'
        elif sched and not yo: status,basis='active','closure_scheduled_not_closed'
        elif yo and (yo>sy or (yo==sy and mm>sm)): status,basis='planned','opening_date_after_snapshot'
        else: status,basis='active','default_listed_and_not_flagged'
        typ=classify(desc,addr)
        for c in codes:
            out.append(dict(site_code=c,city=city,state=st,mwpvl_type=typ,sq_ft=sqft,year_opened=yo,status=status,status_basis=basis,raw_year_text=yr,shared_row='Y' if len(codes)>1 else ''))
    return out,skipped

def main():
    cdx={}
    for t,o,s,m in json.load(open(f'{RAW}/cdx.json'))[1:]:
        cdx.setdefault(t,o)
    snaps=[]
    for f in sorted(glob.glob(f'{RAW}/[0-9]*.html')):
        ts=os.path.basename(f)[:14]; orig=cdx.get(ts,'https://www.mwpvl.com/html/amazon_com.html').replace(':80','')
        date=f'{ts[:4]}-{ts[4:6]}-{ts[6:8]}'; url=f'https://web.archive.org/web/{ts}/{orig}'
        rows,skipped=parse_snapshot(f,date)
        snaps.append(dict(snapshot_date=date,timestamp=ts,wayback_url=url,us_rows_parsed=len(rows),us_rows_no_code=skipped,
                          parse_mode='html_text_table' if rows else 'image_only_no_text_table'))
        snaps[-1]['_rows']=rows
    facts=[]
    for s in snaps:
        for r in s['_rows']: facts.append(dict(snapshot_date=s['snapshot_date'],wayback_url=s['wayback_url'],**r))
    fc=['snapshot_date','wayback_url','site_code','city','state','mwpvl_type','sq_ft','year_opened','status','status_basis','raw_year_text','shared_row']
    w=csv.DictWriter(open(f'{OUT}/mwpvl_wayback_facts.csv','w',newline=''),fc); w.writeheader(); w.writerows(facts)
    sc=['snapshot_date','timestamp','wayback_url','us_rows_parsed','us_rows_no_code','parse_mode']
    w=csv.DictWriter(open(f'{OUT}/mwpvl_wayback_snapshots.csv','w',newline=''),sc,extrasaction='ignore'); w.writeheader(); w.writerows(snaps)
    # per-site
    text=[s for s in snaps if s['_rows']]; last=text[-1]['snapshot_date']
    by={}
    for r in facts: by.setdefault(r['site_code'],[]).append(r)
    sites=[]
    for code,rs in sorted(by.items()):
        rs.sort(key=lambda r:r['snapshot_date'])
        yrs=sorted({r['year_opened'] for r in rs if r['year_opened']!=''})
        latest=rs[-1]; lsq=next((r['sq_ft'] for r in reversed(rs) if r['sq_ft']!=''),'')
        seen={r['snapshot_date'] for r in rs}
        closed=''
        flagged=[r for r in rs if r['status']=='closed']
        if flagged: closed=flagged[0]['snapshot_date']
        elif latest['snapshot_date']!=last:
            nxt=[s['snapshot_date'] for s in text if s['snapshot_date']>latest['snapshot_date']]; closed=nxt[0]
        sites.append(dict(site_code=code,earliest_snapshot=rs[0]['snapshot_date'],latest_snapshot=latest['snapshot_date'],
            year_opened=yrs[0] if len(yrs)==1 else (yrs[0] if yrs else ''),
            year_opened_all=';'.join(map(str,yrs)),year_conflict='Y' if len(yrs)>1 else '',
            earliest_year_seen=yrs[0] if yrs else '',latest_sq_ft=lsq,latest_status=latest['status'],latest_city=latest['city'],latest_state=latest['state'],
            latest_mwpvl_type=latest['mwpvl_type'],n_snapshots=len(seen),
            closed_by_snapshot=closed,closed_basis=('marked_closed' if flagged else ('absent_from_later_snapshot' if closed else '')),
            source='MWPVL International via Wayback Machine'))
    sc=list(sites[0]); w=csv.DictWriter(open(f'{OUT}/mwpvl_wayback_sites.csv','w',newline=''),sc); w.writeheader(); w.writerows(sites)
    print(len(snaps),'snapshots;',len(text),'text;',len(facts),'rows;',len(sites),'sites; last text snapshot',last)
main()
