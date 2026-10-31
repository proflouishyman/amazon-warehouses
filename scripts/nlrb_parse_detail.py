import os as _os
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))  # project root, so scripts run from any checkout
import re,html,glob,csv,os
RAW=_ROOT+'/data/raw/labor/nlrb/case/'
P=_ROOT+'/data/processed/'
idx={r['case_number']:r for r in csv.DictReader(open(P+'nlrb_amazon_cases_search_index.csv'))}
def txt(fn):
    t=open(fn,errors='ignore').read()
    t=re.sub(r'<(script|style)[^>]*>.*?</\1>',' ',t,flags=re.S);t=re.sub(r'<[^>]+>',' ',t);return re.sub(r'\s+',' ',html.unescape(t))
LAB=['Case Number','Date Filed','Status','Location','Region Assigned','Tally Issued Date','No. of Eligible Voters','Void Ballots','Total Ballots Counted','Challenged Ballots','Votes for Labor Union','Tally Type','Ballot Type','Unit ID','Votes Against','Challenges Determinative','Reason Closed','Labor Union','Voting Unit','Union to Certify','Date Closed','No. of Employees']
def fields(seg):
    out={}
    pat='('+'|'.join(re.escape(l) for l in LAB)+r')(?: \(Unit [A-Z]\))?:'
    parts=re.split(pat,seg)
    for i in range(1,len(parts)-1,2): out.setdefault(parts[i],parts[i+1].strip())
    return out
cases=[];tallies=[]
for cn,r in idx.items():
    fn=RAW+cn+'.html'
    if not os.path.exists(fn): continue
    t=txt(fn)
    i=t.find('Case Number:'); j=t.find('Docket Activity',i)
    seg=t[i:j]
    f=fields(seg.split('Tally Issued Date:')[0])
    allg=''
    k=t.find('Allegations',j); l=t.find('Participants',k)
    if k>0:
        a=t[k+len('Allegations'):l].strip()
        allg='' if 'not available' in a else ' | '.join(x.strip() for x in re.split(r'(?=8\([a-z]\)\(\d\))',a) if x.strip())
    d0=t.find('Issued/Filed By',j); d1=t.find('The Docket Activity list',d0)
    dock=[x.strip() for x in re.split(r'(?=\b\d\d/\d\d/\d{4}\b)',t[d0+15:d1]) if x.strip()] if d0>0 else []
    dl=' ; '.join(dock).lower()
    disp=[]
    for kw,lab in [('withdrawal','withdrawal approved'),('dismissal','dismissal letter'),('settlement','settlement item'),('complaint and notice','complaint issued'),('deferral','deferred'),('compliance','compliance'),('board decision','board decision'),('election','election item')]:
        if kw in dl: disp.append(lab)
    rc=f.get('Reason Closed','')
    if not rc and 'Reason Closed:' in seg: rc=fields(seg[seg.rfind('Tally Issued Date:'):]).get('Reason Closed','')
    cases.append([cn,r['case_type'],r['case_name'],f.get('Date Filed',r['date_filed']),f.get('Status',r['status']),rc,f.get('No. of Employees',''),f.get('Location',r['location']),f.get('Region Assigned',r['region']),allg,len(dock),dock[0] if dock else '',';'.join(disp),r['url']])
    if 'Tally Issued Date:' in seg:
        for tp in seg.split('Tally Issued Date:')[1:]:
            g=fields('Tally Issued Date:'+tp)
            tallies.append([cn,r['case_name'],f.get('Date Filed'),f.get('Location'),g.get('Tally Issued Date'),g.get('Tally Type'),g.get('No. of Eligible Voters'),g.get('Total Ballots Counted'),g.get('Votes for Labor Union'),g.get('Votes Against'),g.get('Void Ballots'),g.get('Challenged Ballots'),g.get('Challenges Determinative'),rc,g.get('Labor Union') or f.get('Labor Union'),r['url']])
with open(P+'nlrb_amazon_cases.csv','w',newline='') as o:
    w=csv.writer(o); w.writerow(['case_number','case_type','case_name','date_filed','status','reason_closed','no_of_employees_listed','location','region','allegations','docket_items_shown','latest_docket_item','disposition_keywords_in_shown_docket','url']); w.writerows(cases)
with open(P+'nlrb_amazon_election_tallies.csv','w',newline='') as o:
    w=csv.writer(o); w.writerow(['case_number','case_name','date_filed','location','tally_date','tally_type','eligible_voters','ballots_counted','votes_for_union','votes_against','void_ballots','challenged_ballots','challenges_determinative','reason_closed','union','url']); w.writerows(tallies)
print(len(cases),len(tallies))

# post-process: add entity_class (name-based heuristic)
import re as _re
rows=list(csv.DictReader(open(P+'nlrb_amazon_cases.csv')))
def cls(r):
    n=r['case_name'].lower()
    if _re.search(r'web services|\baws\b|data services',n): return 'aws_or_data_center_entity'
    if r['case_type']=='CB' or _re.search(r'teamsters|labor union|amazonians|union',n): return 'charge_against_union_or_union_named'
    return 'amazon_employer_charge_or_petition'
for r in rows: r['entity_class']=cls(r)
with open(P+'nlrb_amazon_cases.csv','w',newline='') as o:
    w=csv.DictWriter(o,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
import collections; print(collections.Counter(r['entity_class'] for r in rows))
