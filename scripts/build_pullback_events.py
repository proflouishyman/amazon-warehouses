"""Consolidate pullback facts and facility events into public, citation-only files.

Run:  python3 -I scripts/build_pullback_events.py

Reads (all in data/processed):
  jhu_* facility, facility_events, openings and pullback extracts (subscription databases),
  industry_trade_press_openings.csv, facilities_master.csv, mwpvl_wayback_sites_all.csv,
  mwpvl_wayback_image_facts.csv.
Writes:
  pullback_sites.csv       one row per site and status (closed, closed_temporary, closed_partial,
                           cancelled, delayed, paused, sublease, removed_from_mwpvl_list)
  pullback_aggregates.csv  dated tallies as stated by a source, plus MWPVL snapshot tallies
  facility_events_all.csv  opening and announcement events, same columns as
                           industry_trade_press_openings.csv plus `sources`

Public-file rules: no quotes, no document IDs, no subscription URLs, no free text copied
from the jhu_* extracts. Only structured facts (place, type, size, status, date) and a
"Publication, date (via database)" citation are kept. Source free text is used only to
assign a short reason_class label by keyword.
"""
import csv, datetime, os, re, statistics, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'data/processed')


def rd(name):
    with open(os.path.join(P, name), newline='', encoding='utf-8') as fh:
        return list(csv.DictReader(fh))


def wr(name, hdr, rows):
    path = os.path.join(P, name)
    with open(path, 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        w.writerow(hdr)
        for r in rows:
            w.writerow([r.get(h, '') for h in hdr])
    print(name, len(rows))


# ---------------------------------------------------------------- dates
MON = {m: i + 1 for i, m in enumerate('jan feb mar apr may jun jul aug sep oct nov dec'.split())}


def pdate(s):
    """Normalise to YYYY-MM-DD, YYYY-MM or YYYY ('' if none)."""
    s = (s or '').strip()
    if not s:
        return ''
    m = re.match(r'(\d{4})-(\d{2})-(\d{2})', s)
    if m:
        return m.group(0)
    m = re.match(r'(\d{4})-(\d{2})\b', s)
    if m:
        return m.group(0)
    m = re.match(r'(\d{1,2})/(\d{1,2})/(\d{4})', s)
    if m:
        return '%s-%02d-%02d' % (m.group(3), int(m.group(1)), int(m.group(2)))
    m = re.search(r'\b([A-Za-z]{3,9})\.? (\d{1,2}), (\d{4})', s)
    if m and m.group(1)[:3].lower() in MON:
        return '%s-%02d-%02d' % (m.group(3), MON[m.group(1)[:3].lower()], int(m.group(2)))
    m = re.search(r'\b([A-Za-z]{3,9}) (\d{4})\b', s)
    if m and m.group(1)[:3].lower() in MON:
        return '%s-%02d' % (m.group(2), MON[m.group(1)[:3].lower()])
    m = re.match(r'(\d{4})\b', s)
    if m:
        return m.group(1)
    return ''


def dnum(d):
    """Date string to an ordinal (mid-period for partial dates); None if empty."""
    if not d:
        return None
    p = d.split('-')
    y = int(p[0])
    mo = int(p[1]) if len(p) > 1 else 7
    dy = int(p[2]) if len(p) > 2 else 15
    try:
        return datetime.date(y, mo, min(dy, 28)).toordinal()
    except ValueError:
        return None


# ---------------------------------------------------------------- names
DB = {'EBSCO Business Source Ultimate': 'EBSCO Business Source Ultimate',
      'EBSCO Regional Business News': 'EBSCO Regional Business News',
      'ProQuest US Newsstream': 'ProQuest US Newsstream',
      'ProQuest ABI/INFORM Collection': 'ProQuest ABI/INFORM',
      'ProQuest Central': 'ProQuest Central',
      'NewsBank Access World News': 'NewsBank Access World News',
      'Nexis Uni (LexisNexis)': 'Nexis Uni',
      'S&P Capital IQ (NetAdvantage)': 'S&P Capital IQ',
      'Wall Street Journal 1984-current (ProQuest)': 'ProQuest',
      'Financial Times (FT.com digital subscription via JHU)': 'FT.com'}


def dbname(s):
    s = (s or '').strip()
    return DB.get(s, re.sub(r'\s*\(.*?\)', '', s))


def pubname(s):
    s = (s or '').strip()
    s = re.sub(r':\s*Web Edition.*$', '', s)
    s = re.sub(r'\s*\(.*?\)', '', s)
    s = re.sub(r',\s*[Tt]he\s*$', '', s)
    s = re.sub(r',\s*(North America|Eastern|Combined) ed\.?$', '', s)
    s = re.sub(r'\s*-\s*Online$', '', s)
    return s.strip()


def cite(pub, date, db):
    pub = pubname(pub)
    date = pdate(date) or (date or '').strip()
    out = pub
    if date:
        out += ', ' + date
    if db:
        out += ' (via %s)' % db
    return out


# ---------------------------------------------------------------- places
STATES = {'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA',
          'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK',
          'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY', 'DC'}
STATE_NAMES = {'alabama': 'AL', 'alaska': 'AK', 'arizona': 'AZ', 'arkansas': 'AR', 'california': 'CA', 'colorado': 'CO',
               'connecticut': 'CT', 'delaware': 'DE', 'florida': 'FL', 'georgia': 'GA', 'hawaii': 'HI', 'idaho': 'ID',
               'illinois': 'IL', 'indiana': 'IN', 'iowa': 'IA', 'kansas': 'KS', 'kentucky': 'KY', 'louisiana': 'LA',
               'maine': 'ME', 'maryland': 'MD', 'massachusetts': 'MA', 'michigan': 'MI', 'minnesota': 'MN',
               'mississippi': 'MS', 'missouri': 'MO', 'montana': 'MT', 'nebraska': 'NE', 'nevada': 'NV',
               'new hampshire': 'NH', 'new jersey': 'NJ', 'new mexico': 'NM', 'new york': 'NY', 'north carolina': 'NC',
               'north dakota': 'ND', 'ohio': 'OH', 'oklahoma': 'OK', 'oregon': 'OR', 'pennsylvania': 'PA',
               'rhode island': 'RI', 'south carolina': 'SC', 'south dakota': 'SD', 'tennessee': 'TN', 'texas': 'TX',
               'utah': 'UT', 'vermont': 'VT', 'virginia': 'VA', 'washington': 'WA', 'west virginia': 'WV',
               'wisconsin': 'WI', 'wyoming': 'WY'}
STATE_NAMES_ORDERED = sorted(STATE_NAMES.items(), key=lambda kv: -len(kv[0]))
# bases where the part in brackets, not the part before it, is the place
CITY_ALIAS = {'bexar (san antonio)': 'San Antonio', 'minnehaha (sioux falls)': 'Sioux Falls', 'blount (alcoa)': 'Alcoa',
              'dickinson (league city)': 'League City', 'montgomery (union)': 'Union',
              'egg harbor city (galloway)': 'Galloway', 'everett (chelsea)': 'Everett',
              'papillion (omaha)': 'Papillion', 'new york city': 'New York'}


def clean_city(c):
    c = (c or '').strip()
    if not c:
        return ''
    low = c.lower()
    for k, v in CITY_ALIAS.items():
        if low.startswith(k):
            return v
    c = re.sub(r'\s*\(.*', '', c).strip()
    c = re.sub(r'\s+area$', '', c, flags=re.I)
    return c


def cityk(c):
    c = clean_city(c).lower().replace("'", '').replace('’', '')
    c = re.sub(r'\b(charter )?(township|twp\.?)\b', '', c)
    c = re.sub(r'^(city of|town of)\s+', '', c)
    c = c.replace('saint ', 'st ').replace('st. ', 'st ')
    return re.sub(r'[^a-z0-9 ]', '', c).strip()


def skip_place(city, state):
    c = (city or '').lower()
    s = (state or '').strip()
    if s == 'QC' or 'germany' in c:
        return True
    if s and s not in STATES:
        return True
    if any(k in c for k in ('multiple', '(multi', 'network', 'nationwide', 'region')) and not s:
        return True
    if re.search(r'\barea\s*$', c):
        return True  # area-level mentions (for example a metro area), not a site
    return ';' in c


# ---------------------------------------------------------------- types
def canon_type(t):
    t = (t or '').lower()
    if not t or t in ('all', 'network', '(not stated)', 'facility', 'facilities', 'mixed network', 'industrial'):
        return ''
    if 'customer service' in t or 'office' in t or re.search(r'\bstores?\b', t):
        return 'NONLOG'
    if 'delivery' in t or 'last-mile' in t or 'last mile' in t:
        return 'delivery station'
    if 'sortable' in t:
        return 'fulfillment center'
    if 'sort' in t and 'fulfil' not in t:
        return 'sortation center'
    if ('big' in t and 'bulky' in t) or 'non-sort' in t or 'bulk' in t:
        return 'big-and-bulky fulfillment center'
    if 'robot' in t and ('fulfil' in t or 'facility' in t or 'center' in t or 'centre' in t):
        return 'robotic fulfillment center'
    if 'air' in t.split() or 'air hub' in t or 'air cargo' in t or 'air gateway' in t:
        return 'air hub'
    if 'cross' in t and 'dock' in t:
        return 'inbound cross-dock'
    if 'fulfil' in t or 'fc' in t.split() or 'regional' in t:
        return 'fulfillment center'
    if 'sort' in t:
        return 'sortation center'
    if any(k in t for k in ('distribution', 'warehouse', 'logistics', 'returns', 'receiving', 'inbound', 'industrial')):
        return 'distribution center'
    return ''


def tclass(ct):
    return {'delivery station': 'ds', 'sortation center': 'sort', 'big-and-bulky fulfillment center': 'fc',
            'robotic fulfillment center': 'fc', 'fulfillment center': 'fc', 'air hub': 'air',
            'inbound cross-dock': 'xd', 'distribution center': 'dc'}.get(ct, '')


def compat(a, b, sa=None, sb=None):
    """Type classes match: 'dc' (generic warehouse wording) fits anything, cross-docks fit FC and sort
    centers, and two rows of identical stated size are taken as the same building."""
    if not a or not b or a == b or 'dc' in (a, b):
        return True
    if sa and sb and sa == sb:
        return True
    return {a, b} <= {'xd', 'fc'} or {a, b} <= {'xd', 'sort'}


def master_class(ft):
    return {'fulfillment_center': 'fc', 'delivery_station': 'ds', 'sort_center': 'sort', 'air_hub': 'air',
            'other_logistics': 'dc'}.get(ft, '')


def mwpvl_class(t):
    t = t or ''
    if 'delivery_station' in t:
        return 'ds'
    if 'fc' in t:
        return 'fc'
    if 'sortation' in t:
        return 'sort'
    if 'air_hub' in t:
        return 'air'
    if 'crossdock' in t:
        return 'xd'
    return 'dc'


PB_TYPE = {'ds': 'delivery_station', 'fc': 'fulfillment_center', 'sort': 'sort_center', 'air': 'air_hub',
           'xd': 'cross_dock', 'dc': 'other_logistics', '': ''}


def toint(x):
    x = re.sub(r'[^\d]', '', str(x or ''))
    return int(x) if x else None


# ---------------------------------------------------------------- master index
MASTER = rd('facilities_master.csv')
MIDX = collections.defaultdict(list)
MCODE = {r['site_code']: r for r in MASTER if r['site_code']}
for _r in MASTER:
    MIDX[(cityk(_r['city']), _r['state'])].append(_r)


def master_year(r):
    for k in ('opening_year', 'press_opening_year', 'first_osha_filing_year'):
        if str(r.get(k) or '').isdigit():
            return int(r[k])
    return None


def match_master(code, city, state, tc, year=None, allow_blank_type=True):
    """Return (site_code, quality)."""
    if code and code in MCODE:
        return code, 'exact'
    if not city or not state:
        return '', 'none'
    cands = [r for r in MIDX.get((cityk(city), state), []) if r['site_code']]
    cands = [r for r in cands if (tc and compat(tc, master_class(r['facility_type']))) or (not tc and allow_blank_type)]
    if len(cands) == 1:
        return cands[0]['site_code'], 'probable'
    if len(cands) > 1 and year:
        ys = sorted((abs(master_year(r) - year), r['site_code']) for r in cands if master_year(r))
        if ys and (len(ys) == 1 or ys[0][0] < ys[1][0]) and ys[0][0] <= 1:
            return ys[0][1], 'probable'
    return '', 'none'


# ================================================================ record loading
def rec(**k):
    base = dict(site_code='', city='', state='', ftype='', sq_ft=None, event='', edate='', adate='', pub='', db='',
                conf='', evidence='', text='', n=1, srcfile='')
    base.update(k)
    return base


def load_all():
    out = []
    f = 'jhu_ebsco_business_source_ultimate_facilities.csv'
    for r in rd(f):
        out.append(rec(site_code=r['site_code'], city=r['city'], state=r['state'], ftype=r['facility_type'],
                       sq_ft=toint(r['sq_ft']), event=r['event'], edate=pdate(r['event_date']),
                       adate=pdate(r['article_date']), pub=r['publication'], db=dbname(r['database']),
                       text=r['detail'], srcfile=f))
    f = 'jhu_ebsco_regional_business_news_facilities.csv'
    for r in rd(f):
        out.append(rec(city=r['city'], state=r['state'], ftype=r['facility_type'], sq_ft=toint(r['sq_ft']),
                       event=r['event_type'], adate=pdate(r['article_date']), pub=r['publication'],
                       db=dbname(r['database']), text=r['fact_summary'], srcfile=f))
    f = 'jhu_newsbank_access_world_news_facility_events.csv'
    for r in rd(f):
        out.append(rec(city=r['city'], state=r['state'], ftype=r['facility_type'], sq_ft=toint(r['sq_ft']),
                       event=r['event'], edate=pdate(r['event_date']), adate=pdate(r['article_date']),
                       pub=r['publication'], db=dbname(r['database']), text=r['note'], srcfile=f))
    f = 'jhu_nexis_uni_openings.csv'
    for r in rd(f):
        out.append(rec(site_code=r['site_code'], city=r['city'], state=r['state'], ftype=r['facility_type'],
                       sq_ft=toint(r['sq_ft']), event=r['event'], edate=pdate(r['event_date']),
                       adate=pdate(r['article_date']), pub=r['publication'], db=dbname(r['database']),
                       text=r['fact'], srcfile=f))
    f = 'jhu_proquest_abi_inform_facilities.csv'
    for r in rd(f):
        out.append(rec(city=r['city'], state=r['state'], ftype=r['facility_type'], sq_ft=toint(r['sq_ft']),
                       event=r['event_type'], edate=pdate(r['event_date']), adate=pdate(r['pub_date']),
                       pub=r['publication'], db=dbname(r['database']), conf=r['confidence'],
                       evidence=r['evidence_basis'], text=r['fact'], srcfile=f))
    f = 'jhu_proquest_central_facility_events.csv'
    for r in rd(f):
        out.append(rec(site_code=r['site_code'], city=r['city'], state=r['state'], ftype=r['facility_type'],
                       sq_ft=toint(r['sq_ft']), event=r['event_type'], edate=pdate(r['event_date']),
                       adate=pdate(r['article_date']), pub=r['publication'], db=dbname(r['database']),
                       conf=r['confidence'], text=r['detail'], srcfile=f))
    for f in ('jhu_proquest_us_newsstream_facilities.csv', 'jhu_proquest_us_newsstream_facilities_pullback.csv'):
        for r in rd(f):
            out.append(rec(site_code=r['site_code'], city=r['city'], state=r['state'], ftype=r['facility_type'],
                           sq_ft=toint(r['sq_ft']), event=r['event'], edate=pdate(r['event_date']),
                           adate=pdate(r['article_date']), pub=r['publication'], db=dbname(r['database']),
                           evidence=r['evidence_basis'], text=r['jobs_or_investment_or_detail'], srcfile=f))
    f = 'jhu_wsj_proquest_openings.csv'
    for r in rd(f):
        out.append(rec(site_code=r['site_code'], city=r['city'], state=r['state'], ftype=r['facility_type'],
                       sq_ft=toint(r['sq_ft']), event=r['fact_type'], edate=pdate(r['event_date']),
                       adate=pdate(r['article_date']), pub=r['publication'], db=dbname(r['database']),
                       evidence=r['evidence'], text=r['detail'], srcfile=f))
    f = 'jhu_newsbank_access_world_news_pullback_sites_2022.csv'
    for r in rd(f):
        st = {'closed': 'closed', 'cancelled': 'cancelled', 'delayed opening': 'delayed', 'on hold': 'on hold'}[r['status']]
        out.append(rec(city=r['city'], state=r['state'], ftype=r['facility_type'], event=st,
                       adate=pdate(r['article_date']), pub=r['publication'], db=dbname(r['database']),
                       n=int(r['count'] or 1), text='', srcfile=f))
    return out


# ================================================================ pullback classification
def pb_status(ev, text=''):
    """Pullback status from the event label and, for closures, the text; '' if not a pullback fact."""
    e = (ev or '').lower().strip()
    if not e:
        return ''
    if e.startswith('opened') or any(k in e for k in ('land purchase', 'closing extend', 'tax agreement', 'incentive',
                                                       'layoff', 'no_', 'delay_check', 'groundbreaking')):
        return ''
    if 'sublease' in e or 'sublet' in e:
        return 'sublease'
    if 'partial' in e:
        return 'closed_partial'
    if 'delayed_or_abandoned' in e:
        return 'delayed'
    if 'cancel' in e or 'withdr' in e or 'abandon' in e:
        return 'cancelled'
    if 'delay' in e or 'postpone' in e or 'built_unopened' in e:
        return 'delayed'
    if 'paus' in e or 'hold' in e or 'suspend' in e:
        return 'paused'
    if 'clos' in e:
        t = (text or '').lower()
        if any(k in e for k in ('temporar', 'conversion', 'retrofit', 'refit', 'expansion', 'fire', 'two-year')) or \
                re.search(r'temporar|idled', t):
            return 'closed_temporary'
        return 'closed'
    return ''


def reason_class(text):
    t = (text or '').lower()
    if 'covid' in t:
        return 'covid'
    if 'tornado' in t or 'fire ' in t or 'bed bug' in t or 'structural' in t or 'design error' in t or 'city code' in t:
        return 'disaster_or_safety'
    if 'lease' in t and ('not renew' in t or 'expir' in t or 'non-renew' in t):
        return 'lease_end'
    if any(k in t for k in ('renovat', 'retrofit', 'refit', 'convert', 'conversion', 'reopen')):
        return 'conversion_or_retrofit'
    return ''


# ================================================================ CLUSTERING
def sq_compat(a, b):
    if not a or not b:
        return True
    return 0.7 <= a / b <= 1.43


CONF_RANK = {'low': 0, 'medium': 1, 'high': 2}


def up(c):
    return {'low': 'medium', 'medium': 'high', 'high': 'high'}[c]


def build_pullback_sites(recs):
    items = []
    for r in recs:
        st = pb_status(r['event'], r['text'])
        if not st:
            continue
        ct = canon_type(r['ftype'])
        if ct == 'NONLOG':
            continue
        cities = [r['city']]
        if r['city'].strip().lower() == 'sacramento / irvine':
            cities = ['Sacramento', 'Irvine']
        for c in cities:
            if skip_place(c, r['state']) or not clean_city(c) or r['state'] not in STATES:
                continue
            ev = (r['event'] or '').lower()
            conf = r['conf'] or ''
            if 'abandon' in ev or 'expected' in ev:
                conf = 'low'
            items.append(dict(site_code=r['site_code'], city=clean_city(c), state=r['state'], tc=tclass(ct),
                              sq_ft=r['sq_ft'], status=st, date=r['edate'] or r['adate'],
                              cite=cite(r['pub'], r['adate'], r['db']), pubk=pubname(r['pub']), n=r['n'], conf=conf,
                              evidence=r['evidence'], text=r['text'], mw=False))
    M = rd('mwpvl_wayback_sites_all.csv')
    mw_items = []
    for r in M:
        hist = [h for h in r['status_history'].split(' > ') if h]
        seen = set()
        for h in hist:
            d, _, s = h.partition(':')
            status = {'delayed': 'delayed', 'on_hold': 'paused', 'sublease': 'sublease'}.get(s)
            if not status or s in seen:
                continue
            seen.add(s)
            mw_items.append(dict(site_code=r['site_code'], city=clean_city(r['latest_city']), state=r['latest_state'],
                                 tc=mwpvl_class(r['latest_mwpvl_type']), sq_ft=toint(r['latest_sq_ft']), status=status,
                                 date=d, cite=cite('MWPVL (Marc Wulfraat)', d, 'Wayback Machine'), pubk='MWPVL', n=1,
                                 conf='high' if int(r['n_snapshots'] or 0) >= 2 else 'medium',
                                 evidence='', text='', mw=True))
        if r['absent_from_snapshot']:
            d = r['absent_from_snapshot']
            mw_items.append(dict(site_code=r['site_code'], city=clean_city(r['latest_city']), state=r['latest_state'],
                                 tc=mwpvl_class(r['latest_mwpvl_type']), sq_ft=toint(r['latest_sq_ft']),
                                 status='removed_from_mwpvl_list', date=d,
                                 cite=cite('MWPVL (Marc Wulfraat)', d, 'Wayback Machine'), pubk='MWPVL', n=1,
                                 conf='low', evidence='', text='', mw=True))
    clusters = []
    byk = collections.defaultdict(list)

    def add(it):
        k = (cityk(it['city']), it['state'], it['status'])
        cands = [c for c in byk[k] if compat(c['tc'], it['tc'], c['sq_ft'], it['sq_ft'])
                 and sq_compat(c['sq_ft'], it['sq_ft'])
                 and (not it['site_code'] or not c['codes'] or it['site_code'] in c['codes'])]
        if it['mw']:
            cands = [c for c in cands if it['site_code'] in c['codes']]
        # attach only when unambiguous: one candidate, or several that all share one site code (or none)
        if cands and len({tuple(sorted(c['codes'])) for c in cands}) == 1:
            c = cands[0]
        else:
            c = dict(k=k, tc=it['tc'], sq_ft=it['sq_ft'], codes=set(), items=[])
            byk[k].append(c)
            clusters.append(c)
        c['items'].append(it)
        if it['site_code']:
            c['codes'].add(it['site_code'])
        if it['tc'] and (not c['tc'] or c['tc'] == 'dc'):
            c['tc'] = it['tc']
        if it['sq_ft'] and not c['sq_ft']:
            c['sq_ft'] = it['sq_ft']

    for it in mw_items:
        add(it)
    for it in sorted(items, key=lambda x: x['date'] or '9999'):
        add(it)
    rows = []
    for c in clusters:
        its = c['items']
        codes = sorted(c['codes'])
        code = codes[0] if len(codes) == 1 else ''
        city = its[0]['city']
        state = its[0]['state']
        tc = c['tc']
        status = c['k'][2]
        basis = 'mwpvl_site_code' if code else ''
        if not code and status not in ('cancelled', 'removed_from_mwpvl_list'):
            code, mq = match_master('', city, state, tc, allow_blank_type=False)
            basis = 'city_state_type_unique' if code else ''
        dates = sorted([i['date'] for i in its if i['date']], key=lambda d: (dnum(d) or 0))
        cites = []
        for i in sorted(its, key=lambda x: x['cite']):
            if i['cite'] not in cites:
                cites.append(i['cite'])
        pubs = {i['pubk'] for i in its}
        confs = [i['conf'] for i in its if i['conf'] in CONF_RANK]
        weak = all(('snippet' in (i['evidence'] or '').lower()) or ('title' in (i['evidence'] or '').lower())
                   for i in its)
        if status == 'removed_from_mwpvl_list':
            conf = 'low'
        elif confs:
            conf = max(confs, key=lambda x: CONF_RANK[x])
            if len(pubs) >= 2:
                conf = up(conf)
        elif weak:
            conf = 'low'
        else:
            conf = 'high' if len(pubs) >= 2 else 'medium'
        sqs = [i['sq_ft'] for i in its if i['sq_ft']]
        sq = collections.Counter(sqs).most_common(1)[0][0] if sqs else ''
        reasons = [x for x in (reason_class(i['text']) for i in its) if x]
        reason = collections.Counter(reasons).most_common(1)[0][0] if reasons else ''
        rows.append(dict(site_code=code, city=city, state=state, type=PB_TYPE.get(tc, ''), sq_ft=sq, status=status,
                         date=dates[0] if dates else '', sources='; '.join(cites), confidence=conf,
                         n_sites=max(i['n'] for i in its), reason_class=reason, match_basis=basis))
    rows.sort(key=lambda r: (r['state'], r['city'], r['status'], r['date']))
    return rows


# ================================================================ aggregates (curated tallies + MWPVL snapshots)
AGG = []


def agg(date, source, closed='', cancelled='', delayed='', sq_ft='', states='', closed_or_cancelled='', paused='',
        sublease='', total_stated='', scope='', note=''):
    AGG.append(dict(date=date, closed=closed, cancelled=cancelled, delayed=delayed, sq_ft=sq_ft, states=states,
                    source=source, closed_or_cancelled=closed_or_cancelled, paused=paused, sublease=sublease,
                    total_stated=total_stated, scope=scope, note=note))


def build_aggregates():
    # Figures are the ones printed in the cited articles, read from the jhu_* aggregate, event and openings
    # extracts. "More than" and "at least" figures are entered as the stated floor and noted.
    agg('2022-07', 'USA Today Online, 2022-08-01 (via Nexis Uni); Bluffton Today, 2022-08-17 (via NewsBank Access World News)',
        total_stated=16, states=12, scope='delayed_or_cancelled',
        note='FreightWaves count of sites delayed or cancelled, confirmed by an Amazon spokesperson per USA Today; not split between delayed and cancelled')
    agg('2022-07', 'Hays Post, 2022-07-20 (via NewsBank Access World News)', total_stated=16, scope='delayed_or_cancelled',
        note='Modern Shipper count of planned warehouses cancelled or delayed in 2022; may overlap the FreightWaves 16')
    agg('2022-08', 'USA Today Online, 2022-08-01 (via Nexis Uni)', total_stated=25, delayed=15,
        scope='cancelled_closed_sublease_or_hold',
        note='Floor (more than 25) of delivery stations and FCs cancelled, closed, listed for sublease or on hold, per WSJ citing MWPVL as of early August 2022; a further 15 delayed')
    agg('2022-08', 'Daytona Beach News-Journal, 2022-08-11 (via NewsBank Access World News)', total_stated=40,
        scope='cancelled_closed_delayed_or_hold', note='Floor (more than 40) per MWPVL via FreightWaves')
    agg('2022-09-02', 'The Seattle Times, 2022-09-02 (via NewsBank Access World News); FOX 2 WJBK, 2022-09-03 (via NewsBank Access World News); Bloomberg.com, 2022-09-02 (via EBSCO Business Source Ultimate)',
        closed_or_cancelled=42, sq_ft=25000000, scope='closed_or_cancelled',
        note='MWPVL tally via Bloomberg; almost 25 million sq ft; Fortune (2024-01-23, via EBSCO Business Source Ultimate) later cites 44 cancelled or closed as of September 2022')
    agg('2022-09-02', 'The Seattle Times, 2022-09-02 (via NewsBank Access World News); Bloomberg.com, 2022-09-02 (via EBSCO Business Source Ultimate)',
        delayed=21, sq_ft=28000000, scope='delayed', note='MWPVL tally via Bloomberg; nearly 28 million sq ft as stated')
    agg('2022-09', 'Wall Street Journal, 2022-09 (via ProQuest)', closed=15, cancelled=25, total_stated=66,
        scope='closed_cancelled_delayed',
        note='MWPVL via WSJ: 66 facilities shut, cancelled or delayed; of 15 closed buildings 14 were delivery stations; of 25 cancelled projects 10 were larger FCs; delayed count not given separately')
    agg('2022-09-06', 'Supply Chain Dive, 2022-09-06 (via Nexis Uni)', closed_or_cancelled=42, delayed=24, total_stated=66,
        sq_ft=24600000, states=28, scope='closed_cancelled_delayed_or_paused',
        note='MWPVL tally; ground-level sq ft; 271 facilities of nearly 100 million sq ft still in the pipeline')
    agg('2022-09-10', 'The News Press, 2022-09-10 (via ProQuest US Newsstream)', closed_or_cancelled=42, delayed=24,
        scope='closed_cancelled_delayed',
        note='MWPVL list: 29 delivery stations, 11 FCs and 2 planned air hub or sortation centers closed or cancelled; 24 completed or nearly completed sites delayed')
    agg('2022-09-15', 'International Business Times, 2022-09-15 (via NewsBank Access World News)', closed=21, cancelled=21,
        delayed=27, total_stated=71, scope='closed_cancelled_delayed_or_hold',
        note='MWPVL via IBT; delayed count includes on hold; the stated total of 71 does not equal the sum of the parts (69) as printed')
    agg('2022-09-15', 'FOX 8 WGHP, 2022-09-15 (via NewsBank Access World News)', closed=21, cancelled=44, delayed=25,
        scope='closed_cancelled_delayed',
        note='MWPVL via CNBC list as printed; the closures figure is given in the text of the same article')
    agg('2022-09', 'Nevada Journal, 2022-09-22 (via NewsBank Access World News)', total_stated=66,
        scope='delayed_cancelled_or_closed', note='MWPVL via AP')
    agg('2022-09', 'The Bulletin, 2022-11-02 (via NewsBank Access World News)', delayed=24, scope='delayed',
        note='industry trackers, September 2022')
    agg('2022-11-10', 'Financial Times, 2022-11-10 (via FT.com)', total_stated=50, scope='paused_or_cancelled',
        note='Floor (at least 50) US warehouses paused or cancelled, citing MWPVL')
    agg('2023-02-24', 'Supply Chain Dive, 2023-02-24 (via Nexis Uni); Supply Chain Dive, 2023-02-28 (via ProQuest ABI/INFORM); Worcester Telegram & Gazette, 2023-04-06 (via NewsBank Access World News)',
        total_stated=99, sq_ft=32300000, states=30, scope='closed_cancelled_or_delayed',
        note='MWPVL tally; the later Worcester article reprints the same figures')
    agg('2022-05-21', 'Bloomberg.com, 2022-05-21 (via EBSCO Business Source Ultimate); Wall Street Journal, 2022-05-24 (via ProQuest); The Associated Press, 2022-05-23 (via Nexis Uni)',
        sq_ft=10000000, scope='sublease',
        note='Floor (at least 10 million) sq ft Amazon sought to sublet; some reports give up to 30 million; Amazon confirmed a sublease plan per AP')
    agg('2023-10', 'Supply Chain Dive, 2023-11-30 (via EBSCO Business Source Ultimate); Supply Chain Dive, 2023-11-30 (via ProQuest ABI/INFORM)',
        sq_ft=1500000, scope='sublease',
        note='About 1.5 million sq ft listed for sublease in October 2023 per CoStar and Bloomberg as cited')
    # MWPVL snapshot tallies from the structured image-era status field
    R = rd('mwpvl_wayback_image_facts.csv')
    snap = collections.defaultdict(dict)
    for r in R:
        if r['status'] in ('delayed', 'on_hold', 'sublease'):
            snap[r['snapshot_date']][r['site_code']] = (r['status'], toint(r['sq_ft']), r['state'])
    allsnaps = sorted({r['snapshot_date'] for r in R})
    absent = collections.defaultdict(list)
    for r in rd('mwpvl_wayback_sites_all.csv'):
        if r['absent_from_snapshot']:
            absent[r['absent_from_snapshot']].append(r['site_code'])
    for d in allsnaps:
        s = snap.get(d, {})
        if not s:
            continue
        cnt = collections.Counter(v[0] for v in s.values())
        sq = sum(v[1] or 0 for v in s.values())
        states = len({v[2] for v in s.values() if v[2]})
        agg(d, 'MWPVL (Marc Wulfraat), %s (via Wayback Machine)' % d, delayed=cnt.get('delayed', 0),
            paused=cnt.get('on_hold', 0), sublease=cnt.get('sublease', 0), sq_ft=sq or '', states=states or '',
            scope='mwpvl_snapshot',
            note='Distinct site codes flagged in this capture (image-era status field); sq_ft sums MWPVL listed size of those sites; %d codes first absent from this capture are not counted as closures' % len(absent.get(d, [])))
    return AGG


# ================================================================ FACILITY EVENTS
ANN_WORDS = ('announce', 'planned', 'proposed', 'approved', 'slated', 'confirmed', 'planning')


def ev_kind(ev):
    e = (ev or '').lower().strip()
    if not e or pb_status(ev):
        return ''
    if any(k in e for k in ('lease', 'sold', 'sale', 'purchase', 'hiring', 'network', 'presence', 'existing',
                            'operating', 'expansion', 'market', 'construction', 'developer', 'securitized',
                            'headline', 'site_visit', 'fee', 'pullback', 'history', 'delay', 'closure', 'closed')):
        return ''
    if 'expected' in e:
        return 'ann'
    if e.startswith('opened') or e.startswith('opening') or 'launch' in e:
        return 'open'
    if any(k in e for k in ANN_WORDS):
        return 'ann'
    return ''


def load_capiq(gaz):
    out = []
    f = 'jhu_sp_capital_iq_netadvantage_amazon_facility_events.csv'
    for r in rd(f):
        if r['geography_guess'] != 'US_or_unspecified' or r['facility_kind_guess'] not in (
                'fulfillment_or_warehouse', 'delivery_station', 'air', 'lease_or_site'):
            continue
        h = r['headline']
        hl = h.lower()
        if re.search(r'\bopens\b|\blaunch(es)?\b', hl):
            kind = 'open'
        elif re.search(r'announces|chooses|plans to (open|build)|to open', hl):
            kind = 'ann'
        else:
            continue
        if re.search(r'tech hub|corporate|office|alexa|hire|hiring|energy|solar|renewable', hl) and 'fulfil' not in hl \
                and 'delivery station' not in hl and ' air ' not in hl:
            continue
        st = ''
        for nm, ab in STATE_NAMES_ORDERED:
            if re.search(r'\b' + nm + r'\b', hl):
                st = ab
                break
        city = ''
        for (ck, s2), cname in gaz:
            if re.search(r'\b' + re.escape(cname) + r'\b', h) and (not st or st == s2):
                city, st = cname, s2
                break
        if not st:
            continue
        ft = {'fulfillment_or_warehouse': 'fulfillment center', 'delivery_station': 'delivery station', 'air': 'air hub',
              'lease_or_site': ''}[r['facility_kind_guess']]
        if 'delivery station' in hl:
            ft = 'delivery station'
        out.append(rec(city=city, state=st, ftype=ft, sq_ft=toint(r['square_feet_in_headline']),
                       event='announced' if kind == 'ann' else 'opened', adate=pdate(r['date']) or pdate(r['event_date']),
                       edate=pdate(r['event_date']), pub='S&P Capital IQ Key Developments', db='S&P Capital IQ',
                       evidence='headline only', srcfile=f))
    return out


def strip_quotes(s):
    s = re.sub(r'“.*?”|"[^"]*"', '', s or '')
    s = re.sub(r'\s{2,}', ' ', s).strip(' ;,')
    return s


def build_events(recs):
    items = []
    tp = rd('industry_trade_press_openings.csv')
    for r in tp:
        ct = canon_type(r['facility_type']) or r['facility_type']
        if skip_place(r['city'], r['state']):
            continue
        has_pq = bool(r['proquest_url'])
        items.append(dict(site_code=r['site_code'], city=clean_city(r['city']), state=r['state'], ct=ct, tc=tclass(ct),
                          sq_ft=toint(r['sq_ft']), ann=pdate(r['announced_date']), opn=pdate(r['opening_date']),
                          pub=r['publication'], adate=r['article_date'],
                          cite=cite(r['publication'], r['article_date'], 'ProQuest' if has_pq else ''),
                          pubk=pubname(r['publication']), conf=r['confidence'], evidence=r['evidence_basis'],
                          note=strip_quotes(r['note']), article_url=r['article_url'], msc=r['match_site_code'],
                          mq=r['match_quality'], tp=True))
    gaz = set()
    for r in recs + [dict(city=m['city'], state=m['state']) for m in MASTER] + \
            [dict(city=t['city'], state=t['state']) for t in tp]:
        c = clean_city(r['city'])
        if c and r['state'] in STATES and not skip_place(r['city'], r['state']) and c.lower() not in STATE_NAMES:
            gaz.add(((cityk(c), r['state']), c))
    stop = {'mobile', 'orange', 'reading', 'union', 'columbia', 'independence', 'florence', 'hope', 'sparks', 'monroe',
            'jackson', 'lincoln', 'washington', 'alexandria', 'phoenix', 'houston', 'dallas', 'charlotte', 'amazon',
            'air', 'prime', 'fresh', 'republic'}
    states_of = collections.defaultdict(set)
    for (ck, s2), cname in gaz:
        states_of[ck].add(s2)
    gaz_sorted = sorted([g for g in gaz if g[0][0] not in stop and len(g[0][0]) >= 4 and len(states_of[g[0][0]]) == 1],
                        key=lambda g: -len(g[1]))
    allrecs = recs + load_capiq(gaz_sorted)
    for r in allrecs:
        kind = ev_kind(r['event'])
        if not kind:
            continue
        if skip_place(r['city'], r['state']) or r['state'] not in STATES:
            continue
        ct = canon_type(r['ftype'])
        if ct == 'NONLOG':
            continue
        d = r['edate'] or r['adate']
        note = 'event date taken from article date' if (not r['edate'] and r['adate']) else ''
        items.append(dict(site_code=r['site_code'], city=clean_city(r['city']), state=r['state'], ct=ct, tc=tclass(ct),
                          sq_ft=r['sq_ft'], ann=d if kind == 'ann' else '', opn=d if kind == 'open' else '',
                          pub=r['pub'], adate=r['adate'], cite=cite(r['pub'], r['adate'], r['db']),
                          pubk=pubname(r['pub']), conf=r['conf'], evidence=r['evidence'], note=note, article_url='',
                          msc='', mq='', tp=False))

    def idate(it):
        return dnum(it['ann'] or it['opn'])

    items.sort(key=lambda it: (idate(it) or 10 ** 7))
    clusters = []
    byk = collections.defaultdict(list)
    for it in items:
        k = (cityk(it['city']), it['state'])
        cands = []
        for c in byk[k]:
            if not compat(c['tc'], it['tc'], c['sq_ft'], it['sq_ft']) or not sq_compat(c['sq_ft'], it['sq_ft']):
                continue
            if it['site_code'] and c['codes'] and it['site_code'] not in c['codes']:
                continue
            ok = True
            a, o = dnum(it['ann']), dnum(it['opn'])
            if a is not None and c['ann']:
                ok = ok and min(abs(a - x) for x in c['ann']) <= 548
            if o is not None and c['opn']:
                ok = ok and min(abs(o - x) for x in c['opn']) <= 548
            if a is not None and c['opn']:
                ok = ok and a <= min(c['opn']) + 90
            if o is not None and c['ann']:
                ok = ok and o >= min(c['ann']) - 60
            if ok:
                allds = c['ann'] + c['opn']
                dist = abs((idate(it) or 0) - statistics.mean(allds)) if allds else 0
                cands.append((dist, len(clusters) and clusters.index(c), c))
        if cands:
            cands.sort(key=lambda x: (x[0], x[1]))
            c = cands[0][2]
        else:
            c = dict(k=k, tc=it['tc'], sq_ft=it['sq_ft'], codes=set(), ann=[], opn=[], items=[])
            byk[k].append(c)
            clusters.append(c)
        c['items'].append(it)
        if it['site_code']:
            c['codes'].add(it['site_code'])
        if dnum(it['ann']) is not None:
            c['ann'].append(dnum(it['ann']))
        if dnum(it['opn']) is not None:
            c['opn'].append(dnum(it['opn']))
        if it['tc'] and (not c['tc'] or c['tc'] == 'dc'):
            c['tc'] = it['tc']
        if it['sq_ft'] and not c['sq_ft']:
            c['sq_ft'] = it['sq_ft']
    rows = []
    SPEC = {'robotic fulfillment center': 3, 'big-and-bulky fulfillment center': 3, 'delivery station': 3,
            'air hub': 3, 'sortation center': 3, 'inbound cross-dock': 3, 'fulfillment center': 2,
            'distribution center': 1}
    for c in clusters:
        its = c['items']
        anns = sorted([i['ann'] for i in its if i['ann']], key=lambda d: dnum(d) or 0)
        opns = sorted([i['opn'] for i in its if i['opn']], key=lambda d: dnum(d) or 0)
        cts = [i['ct'] for i in its if i['ct']]
        ct = max(cts, key=lambda t: (SPEC.get(t, 0), cts.count(t))) if cts else ''
        sqs = [i['sq_ft'] for i in its if i['sq_ft']]
        sq = collections.Counter(sqs).most_common(1)[0][0] if sqs else ''
        codes = sorted(c['codes'])
        stated = codes[0] if len(codes) == 1 else ''
        cites = []
        for i in sorted(its, key=lambda x: x['cite']):
            if i['cite'] not in cites:
                cites.append(i['cite'])
        pubs = {i['pubk'] for i in its}
        confs = [i['conf'] for i in its if i['conf'] in CONF_RANK]
        weak = all(any(w in (i['evidence'] or '').lower() for w in ('snippet', 'title', 'headline')) for i in its)
        if confs:
            conf = max(confs, key=lambda x: CONF_RANK[x])
            if len(pubs) >= 2:
                conf = up(conf)
        else:
            conf = 'low' if weak else ('high' if len(pubs) >= 3 else 'medium')
        first = sorted(its, key=lambda i: (dnum(pdate(i['adate'])) or 10 ** 7))[0]
        tpi = [i for i in its if i['tp']]
        urls = [i['article_url'] for i in tpi if i['article_url']]
        notes = []
        for i in tpi:
            if i['note'] and i['note'] not in notes:
                notes.append(i['note'])
        if any(i['note'] == 'event date taken from article date' for i in its):
            notes.append('some event dates taken from article dates')
        if len(pubs) > 1:
            notes.append('%d publications' % len(pubs))
        ev = [i['evidence'] for i in its if i['evidence']]
        evid = 'full text' if any('full text' in e for e in ev) else (ev[0] if ev else 'not recorded in extract')
        yr = int((opns + anns)[0][:4]) if (opns + anns) else None
        tp_msc = [i for i in tpi if i['msc'] in MCODE and i['mq'] in ('exact', 'probable')]
        if tp_msc:
            msc, mq = tp_msc[0]['msc'], tp_msc[0]['mq']
        else:
            msc, mq = match_master(stated, its[0]['city'], its[0]['state'], c['tc'], year=yr)
        rows.append(dict(site_code=stated, city=its[0]['city'], state=its[0]['state'], facility_type=ct, sq_ft=sq,
                         announced_date=anns[0] if anns else '', opening_date=opns[0] if opns else '',
                         publication=pubname(first['pub']), article_date=pdate(first['adate']) or first['adate'],
                         proquest_url='', article_url=urls[0] if urls else '', quote='', confidence=conf,
                         evidence_basis=evid, note='; '.join(notes), match_site_code=msc, match_quality=mq,
                         sources='; '.join(cites)))
    rows.sort(key=lambda r: (r['state'], r['city'], r['announced_date'] or r['opening_date']))
    return rows


def main():
    recs = load_all()
    sites = build_pullback_sites(recs)
    wr('pullback_sites.csv', ['site_code', 'city', 'state', 'type', 'sq_ft', 'status', 'date', 'sources', 'confidence',
                              'n_sites', 'reason_class', 'match_basis'], sites)
    aggs = build_aggregates()
    wr('pullback_aggregates.csv', ['date', 'closed', 'cancelled', 'delayed', 'sq_ft', 'states', 'source',
                                   'closed_or_cancelled', 'paused', 'sublease', 'total_stated', 'scope', 'note'],
       sorted(aggs, key=lambda r: (r['date'], r['scope'])))
    ev = build_events(recs)
    wr('facility_events_all.csv', ['site_code', 'city', 'state', 'facility_type', 'sq_ft', 'announced_date',
                                   'opening_date', 'publication', 'article_date', 'proquest_url', 'article_url',
                                   'quote', 'confidence', 'evidence_basis', 'note', 'match_site_code',
                                   'match_quality', 'sources'], ev)


if __name__ == '__main__':
    main()
