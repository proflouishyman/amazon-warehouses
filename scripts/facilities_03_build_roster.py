"""Merge OSHA ITA Amazon rows + TaxJar lists + MWPVL historical text -> data/processed/facilities_pregeocode.csv"""
import os as _os
_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))  # project root, so scripts run from any checkout
import csv, re, collections, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from amazon_names import amazon_rule
R=_ROOT+'/data/raw/facilities/'
OSHA_URL='https://www.osha.gov/Establishment-Specific-Injury-and-Illness-Data'
TJ_FC='https://blog.taxjar.com/amazon-warehouse-locations/'
TJ_SORT='https://www.taxjar.com/blog/amazon-sort-centers-locations'
MW='https://www.mwpvl.com/html/amazon_com.html'
EXCL=re.compile(r'WFM|Amazon Go|Fresh|Robotics|Corporate|Customer Service|Seller|Production|Physical Stores|Kuiper|Leo',re.I)
CODE=re.compile(r'\b(K[A-Z]{3}|[A-Z]{3,4}\d{1,2})\b')
rows=list(csv.DictReader(open(R+'osha_amazon_rows.csv')))
def yr(v): 
    try: return int(float(v))
    except: return None
def norm_street(s):
    s=re.sub(r'[^a-z0-9 ]','',s.lower()); return s.split()[0] if s.split() else ''
recs0=collections.defaultdict(list)
for r in rows:
    cn=r['company_name'].strip()
    nm=r['establishment_name'].strip()
    if not amazon_rule(cn,nm,r.get('ein',''),r['naics_code']) or re.search('web services|environmental',cn,re.I): continue
    if EXCL.search(nm): continue
    naics=str(r['naics_code']).split('.')[0]
    if naics[:3] in ('445','455','311','323','333','551','561') : continue
    tail=re.split(r'\s[-:]\s*',nm)[-1] if re.search(r'\s[-:]\s*',nm) else nm
    m=CODE.findall(tail) or CODE.findall(nm)
    if not m: continue
    code=m[-1]
    if re.fullmatch(r'K[A-Z]{3}',code): pass
    elif not re.search(r'\d',code): continue
    prefix=re.split(r'\s[-:]\s',nm)[0].strip()
    y=yr(r['year_filing_for'])
    if not y: continue
    z=re.sub(r'\D','',r['zip_code'])[:5]
    z=z.zfill(5) if z else ''
    recs0[code].append(dict(y=y,naics=naics,prefix=prefix,street=r['street_address'].strip(),city=r['city'].strip(),state=r['state'].strip().upper(),zip=z))

def skey(d):
    t=re.sub(r'[^a-z0-9 ]','',d['street'].lower()).split()
    num=t[0] if t else ''; w=next((x for x in t[1:] if x.isalpha() and x not in('n','s','e','w','north','south','east','west')),'')
    return (num,w[:3])
recs={}
for code,L in recs0.items():
    cl=[]  # list of lists
    for d in sorted(L,key=lambda d:d['y']):
        hit=None
        for c in cl:
            if any(skey(d)==skey(e) or (d['zip'] and d['zip']==e['zip']) or (d['state']==e['state'] and re.sub('[^a-z]','',d['city'].lower())[:4]==re.sub('[^a-z]','',e['city'].lower())[:4]) for e in c): hit=c;break
        if hit is not None: hit.append(d)
        else: cl.append([d])
    for i,c in enumerate(cl): recs[(code,i)]=c
FULL_ST={'Alabama':'AL','Alaska':'AK','Arizona':'AZ','Arkansas':'AR','California':'CA','Colorado':'CO','Connecticut':'CT','Delaware':'DE','Florida':'FL','Georgia':'GA','Hawaii':'HI','Idaho':'ID','Illinois':'IL','Indiana':'IN','Iowa':'IA','Kansas':'KS','Kentucky':'KY','Louisiana':'LA','Maine':'ME','Maryland':'MD','Massachusetts':'MA','Michigan':'MI','Minnesota':'MN','Mississippi':'MS','Missouri':'MO','Montana':'MT','Nebraska':'NE','Nevada':'NV','New Hampshire':'NH','New Jersey':'NJ','New Mexico':'NM','New York':'NY','North Carolina':'NC','North Dakota':'ND','Ohio':'OH','Oklahoma':'OK','Oregon':'OR','Pennsylvania':'PA','Rhode Island':'RI','South Carolina':'SC','South Dakota':'SD','Tennessee':'TN','Texas':'TX','Utah':'UT','Vermont':'VT','Virginia':'VA','Washington':'WA','West Virginia':'WV','Wisconsin':'WI','Wyoming':'WY'}
tj=list(csv.DictReader(open(R+'taxjar_parsed.csv')))
sortcodes={r['code'] for r in tj if r['page']=='sort'}
fccodes={r['code'] for r in tj if r['page']=='fc'}
out=[]
for (code,_i),L in recs.items():
    L.sort(key=lambda d:d['y']); last=L[-1]; first=L[0]
    years=sorted({d['y'] for d in L})
    prefs={d['prefix'] for d in L}; first_letter=code[0]
    basis=''
    if re.fullmatch(r'K[A-Z]{3}',code): typ,basis,conf='air_hub','4-letter K code = ICAO airport id (Amazon Air hub); name in OSHA filing','medium'
    elif code in sortcodes: typ,basis,conf='sort_center','listed on TaxJar sort-center page','medium'
    elif any('Fulfillment' in p for p in prefs): typ,basis,conf='fulfillment_center','OSHA filing org label "Fulfillment Centers"/"Global Specialty Fulfillment"','medium'
    elif any(p=='AMZL' for p in prefs): typ,basis,conf='delivery_station','OSHA filing org label "AMZL" (Amazon Logistics); may include some sort sites','medium'
    elif last['naics']=='492110' and first_letter in 'DHVU': typ,basis,conf='delivery_station','heuristic: NAICS 492110 + code prefix D/H/V/U','low'
    elif last['naics']=='492110' and first_letter=='S': typ,basis,conf='sort_center','heuristic: NAICS 492110 + code prefix S','low'
    elif last['naics']=='492110': typ,basis,conf='other_logistics','NAICS 492110 courier; prefix does not identify DS vs sort','low'
    elif last['naics']=='493110' and first_letter=='S': typ,basis,conf='sort_center','heuristic: NAICS 493110 + code prefix S','low'
    elif last['naics']=='493110': typ,basis,conf='fulfillment_center','heuristic: NAICS 493110 general warehousing (FC, inbound or large non-sort)','low'
    else: typ,basis,conf='other_logistics','unclassified NAICS '+last['naics'],'low'
    if code in fccodes and typ=='other_logistics': typ,basis='fulfillment_center','listed on TaxJar FC page'
    srcs=['OSHA ITA 300A']
    if code in fccodes: srcs.append('TaxJar FC list')
    if code in sortcodes: srcs.append('TaxJar sort list')
    if conf=='medium' and last['y']>=2023: conf='high' if len(srcs)>1 or typ in('fulfillment_center','delivery_station') else conf
    out.append(dict(site_code=code,facility_type=typ,type_basis=basis,street_address=last['street'],city=last['city'],state=last['state'],zip=last['zip'],
      county='',lat='',lon='',opening_year='',opening_year_basis='',opening_year_source_url='',first_osha_filing_year=years[0],last_osha_filing_year=years[-1],closing_year='',
      status='in_2025_osha_filing' if years[-1]>=2025 else 'not_in_2025_osha_filing',sq_ft='',sq_ft_source='',
      confidence=conf,sources=';'.join(srcs),source_url=OSHA_URL,source_detail='OSHA ITA Form 300A establishment records CY'+str(years[0])+'-'+str(years[-1])))
have={(r['site_code']) for r in out}
# TaxJar-only additions
for r in tj:
    if r['code'] in have: continue
    a=r['raw_address']; m=re.search(r'^(.*?),?\s*([^,]+?),?\s*([A-Z]{2})\s*(\d{5})?(?:-\d{4})?\s*$',a)
    if not m: m=re.search(r'^(.*?),\s*([^,]+),\s*([A-Za-z]+)\s*(\d{5})?$',a)
    street,city,state,zp=(m.groups() if m else (a,'','',''))
    if len(state)>2: state=FULL_ST.get(state.strip().title(),'')
    typ='sort_center' if r['page']=='sort' else 'fulfillment_center'
    out.append(dict(site_code=r['code'],facility_type=typ,type_basis='TaxJar '+r['page']+' list',street_address=street.strip(', '),city=city.strip(),state=state,zip=zp or '',
      county=r['county'].split('(')[0].strip(),lat='',lon='',opening_year='',opening_year_basis='',opening_year_source_url='',first_osha_filing_year='',last_osha_filing_year='',closing_year='',
      status='listed_by_taxjar_2025_not_in_osha_data',sq_ft='',sq_ft_source='',confidence='low',
      sources='TaxJar '+r['page']+' list',source_url=TJ_FC if r['page']=='fc' else TJ_SORT,source_detail='TaxJar blog list (page modified 2025-10-29); '+r['raw'][:120]))
    have.add(r['code'])
# Historical anchors from MWPVL public intro text
hist=[('Seattle','WA','fulfillment_center',1997,'',93000,'first Amazon FC, ~93,000 sq ft, largely manual'),
('McDonough','GA','fulfillment_center',1999,2001,None,'later closed in 2001')]
for c,s,t,o,cl,sf,note in hist:
    out.append(dict(site_code='',facility_type=t,type_basis='MWPVL history text',street_address='',city=c,state=s,zip='',county='',lat='',lon='',
      opening_year=o,opening_year_basis='MWPVL International public article text',opening_year_source_url=MW,first_osha_filing_year='',last_osha_filing_year='',closing_year=cl,status='historical_anchor_city_level_only',
      sq_ft=sf or '',sq_ft_source=('MWPVL International public article text' if sf else ''),confidence='medium',sources='MWPVL',source_url=MW,source_detail='1997-1999 network history paragraph. City-level only; site code and address not given; may be the same site as a currently coded site in same city. '+note))

# Legacy MWPVL table (April 2012) -- site code, address, sq ft, month/year opened
MWL='https://mwpvl.com/html/amazon_com_distribution_network_strategy.html'
ST={'Alabama':'AL','Arizona':'AZ','Arkansas':'AR','California':'CA','Delaware':'DE','Indiana':'IN','Kansas':'KS','Kentucky':'KY','Nevada':'NV','New Hampshire':'NH','Pennsylvania':'PA','South Carolina':'SC','Tennessee':'TN','Washington':'WA','Texas':'TX','Georgia':'GA','Virginia':'VA','New Jersey':'NJ','Ohio':'OH','Illinois':'IL','Florida':'FL','Oregon':'OR','Utah':'UT','Colorado':'CO','Maryland':'MD'}
ALIAS={'RN01':'RNO1'}
bycode={r['site_code']:r for r in out if r['site_code']}
for r in csv.DictReader(open(R+'mwpvl_legacy_parsed.csv')):
    code=ALIAS.get(r['code'],r['code'])
    if not re.match(r'[A-Z]{3,4}\d',code): continue
    if code in bycode:
        t=bycode[code]
        if r['opened_year']: t['opening_year']=int(r['opened_year']); t['opening_year_basis']='MWPVL International legacy table (as of April 2012); month/year: '+r['opened_text']; t['opening_year_source_url']=MWL
        if r['sq_ft']: t['sq_ft']=int(r['sq_ft']); t['sq_ft_source']='MWPVL legacy table April 2012 estimate (size then, may have been expanded since)'
        t['sources']+=';MWPVL legacy 2012'
        if 'MWPVL legacy' not in t['source_detail']: t['source_detail']+=' | MWPVL legacy 2012 table: '+r['desc'][:100]
        continue
    parts=[x.strip() for x in r['address'].split(',')]
    zp=parts[-1] if re.fullmatch(r'\d{5}',parts[-1]) else ''
    stt=ST.get(parts[-2] if zp else parts[-1],'')
    city=parts[-3] if zp else parts[-2]; street=', '.join(parts[:-3]) if zp else ', '.join(parts[:-2])
    out.append(dict(site_code=code,facility_type='fulfillment_center',type_basis='MWPVL legacy table (large FC list)',street_address=street,city=city,state=stt,zip=zp,county='',lat='',lon='',
      opening_year=int(r['opened_year']) if r['opened_year'] else '',opening_year_basis='MWPVL International legacy table (as of April 2012); '+r['opened_text'],opening_year_source_url=MWL,
      first_osha_filing_year='',last_osha_filing_year='',closing_year='',status='listed_2012_mwpvl_not_in_osha_data',
      sq_ft=int(r['sq_ft']) if r['sq_ft'] else '',sq_ft_source='MWPVL legacy table April 2012 estimate',confidence='low',sources='MWPVL legacy 2012',source_url=MWL,
      source_detail='MWPVL legacy table (April 2012): '+r['desc'][:100]))
# manual geography corrections for OSHA typos (data/processed/facility_geo_overrides.csv); every change has a reason
OV=list(csv.DictReader(open(_ROOT+'/data/processed/facility_geo_overrides.csv')))
n_ov=0
for o in OV:
    for r in out:
        if r['site_code']==o['site_code'] and o['street_contains'].lower() in r['street_address'].lower():
            r[o['field']]=o['value']; n_ov+=1
            r['source_detail']+=' | geography corrected: '+o['field']+' -> '+o['value']
print('overrides applied',n_ov)
cols=list(out[0].keys())
with open(_ROOT+'/data/processed/facilities_pregeocode.csv','w',newline='') as fh:
    w=csv.DictWriter(fh,fieldnames=cols); w.writeheader(); w.writerows(out)
print(len(out),collections.Counter(r['facility_type'] for r in out),collections.Counter(r['confidence'] for r in out),collections.Counter(r['status'] for r in out))
print('codes',len({r['site_code'] for r in out if r['site_code']}))
