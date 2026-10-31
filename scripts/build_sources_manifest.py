#!/usr/bin/env python3
"""Catalog data/raw and data/private in place. Read-only on the sources; writes only the manifest CSV."""
import os, re, csv, sys, json, hashlib, glob, time, datetime
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = ROOT + '/data'
OUT = DATA + '/sources_manifest.csv'
SKIP_DIR = {'__pycache__'}
SKIP_FILE = {'.DS_Store'}

# ---------------------------------------------------------------- walk
files = []
for top in ('raw', 'private'):
    for dp, dn, fn in os.walk(f'{DATA}/{top}'):
        dn[:] = [d for d in dn if d not in SKIP_DIR]
        for f in fn:
            if f in SKIP_FILE or f.endswith('.pyc'):
                continue
            files.append(os.path.join(dp, f))
files.sort()
rel = lambda p: os.path.relpath(p, DATA)  # relative to data/
print('files', len(files), file=sys.stderr)

# ---------------------------------------------------------------- hash
def hsh(p):
    try:
        h = hashlib.sha256()
        with open(p, 'rb') as fh:
            while True:
                b = fh.read(1 << 22)
                if not b: break
                h.update(b)
        return p, h.hexdigest(), os.path.getsize(p), os.path.getmtime(p)
    except Exception as e:
        return p, 'ERR:' + type(e).__name__, -1, 0
t0 = time.time()
with ThreadPoolExecutor(8) as ex:
    H = {p: (s, z, m) for p, s, z, m in ex.map(hsh, files)}
print('hashed in', round(time.time() - t0), 's', file=sys.stderr)

# ---------------------------------------------------------------- index.csv metadata
IDX = {}   # rel path (to data/) -> dict(title,publication,date,url,topic,retrieved,doc_id)
def load_index(ipath):
    base = os.path.dirname(ipath)
    try:
        rows = list(csv.DictReader(open(ipath, encoding='utf-8', errors='replace')))
    except Exception:
        return
    for r in rows:
        f = r.get('file') or r.get('image_name') or ''
        if not f: continue
        g = lambda *ks: next((r[k] for k in ks if r.get(k)), '')
        d = dict(title=g('title'), publication=g('publication', 'issuer'), date=g('date'),
                 url=g('url', 'url_or_doc_id', 'url/doc id', 'url_or_docid', 'doc_id_url', 'archived_url'),
                 topic=g('topic'), retrieved=g('retrieved'), doc_id=g('doc_id'))
        IDX[rel(os.path.join(base, f))] = d
        tf = r.get('text_file')
        if tf:
            IDX.setdefault(rel(os.path.join(base, tf)), d)
for ip in glob.glob(f'{DATA}/private/*/index.csv') + glob.glob(f'{DATA}/private/*/*/index.csv') + \
          glob.glob(f'{DATA}/raw/subsidies/*/index.csv'):
    load_index(ip)
BLOCKED = set()
_bp = f'{DATA}/private/proquest_central/blocked_pending_fulltext.csv'
if os.path.exists(_bp):
    load_index(_bp)
    for _r in csv.DictReader(open(_bp, encoding='utf-8')):
        BLOCKED.add(rel(os.path.join(f'{DATA}/private/proquest_central', _r['file'])))
print('index rows', len(IDX), 'blocked', len(BLOCKED), file=sys.stderr)

# ---------------------------------------------------------------- corpus for used_by
code_files = sorted(glob.glob(f'{ROOT}/scripts/*.py') + glob.glob(f'{DATA}/raw/benchmark/*/_scripts/*.py') +
                    glob.glob(f'{DATA}/raw/benchmark/*/*.py') + glob.glob(f'{DATA}/raw/benchmark/*/*/*.py'))
note_files = sorted(glob.glob(f'{DATA}/notes/*.md') + glob.glob(f'{ROOT}/README.md'))
page_files = sorted(glob.glob(f'{ROOT}/*.html'))
proc_files = sorted(p for p in glob.glob(f'{DATA}/processed/*') if os.path.isfile(p))
TOK = re.compile(r'[A-Za-z0-9][A-Za-z0-9_.\-]{5,}')
def toks(p):
    try:
        return set(TOK.findall(open(p, encoding='utf-8', errors='replace').read()))
    except Exception:
        return set()
corpus = {}   # label -> (kind, set, text-for-substring or None)
def add(p, kind, keep_text):
    t = open(p, encoding='utf-8', errors='replace').read() if (keep_text or True) else ''
    corpus[p] = (kind, set(TOK.findall(t)), t if keep_text else None)
for p in code_files: add(p, 'script', True)
for p in note_files: add(p, 'notes', True)
for p in page_files: add(p, 'page', True)
for p in proc_files:
    if os.path.getsize(p) < 200e6 and p.rsplit('.', 1)[-1] in ('csv', 'json', 'md', 'txt', 'tsv'):
        add(p, 'processed', False)
print('corpus', len(corpus), file=sys.stderr)

proc_names = {os.path.basename(p) for p in proc_files}
# script -> processed outputs it writes (string literals that name a processed file)
script_out = {}
for p, (k, s, t) in corpus.items():
    if k != 'script': continue
    outs = set()
    for m in re.finditer(r"[\w\-.]+\.(?:csv|json|md|tsv)\b", t):
        if m.group(0) in proc_names: outs.add(m.group(0))
    script_out[p] = sorted(outs)

# directory prefixes referenced by scripts (literal 'raw/...' or 'private/...' strings), plus manual aliases
dir_refs = defaultdict(set)   # data-relative dir prefix -> set(script)
recursive_pre = set()          # prefixes whose whole subtree counts
for p, (k, s, t) in corpus.items():
    if k not in ('script', 'notes', 'page') or not t: continue
    for m in re.finditer(r"(?:data/)?((?:raw|private)/[A-Za-z0-9_./*{}\-]+)", t):
        pre = m.group(1).rstrip('/')
        wild = any(c in pre for c in '{*')
        if wild: pre = re.split(r'[{*]', pre)[0].rstrip('/')
        if pre.count('/') < 1: continue
        if k != 'script' and pre.count('/') < 2: continue   # a note naming just 'raw/labor' does not cover everything below it
        dir_refs[pre].add(p)
        if wild or pre.count('/') >= 2: recursive_pre.add(pre)
# scripts that live inside a raw/benchmark/<x>/ tree read files by relative path from there
for p, (k, s, t) in corpus.items():
    if k == 'script' and '/data/raw/benchmark/' in p:
        d = os.path.relpath(os.path.dirname(p), DATA)
        if d.endswith('_scripts'): d = os.path.dirname(d)
        dir_refs[d].add(p); recursive_pre.add(d)
MANUAL_DIR = {  # data-relative prefix -> scripts that read it through variables (verified by grep of RAW/OUT assignments)
}
def script_hits(r):
    out = set()
    for pre, ss in dir_refs.items():
        if r == pre or (r.startswith(pre + '/') and (pre in recursive_pre or r.count('/') == pre.count('/') + 1)):
            out |= ss
    return out

# ---------------------------------------------------------------- rules
def pretty(fn):
    s = os.path.splitext(fn)[0]
    return re.sub(r'[_]+', ' ', s).strip()

def html_title(p):
    try:
        with open(p, 'rb') as fh:
            b = fh.read(60000).decode('utf-8', 'replace')
        m = re.search(r'<title[^>]*>(.*?)</title>', b, re.S | re.I)
        if m:
            t = re.sub(r'\s+', ' ', m.group(1)).strip()
            if t and 'just a moment' not in t.lower(): return t
    except Exception:
        pass
    return ''

CIK = {'amazon': '1018724', 'costco': '909832', 'fedex': '1048911', 'homedepot': '354950', 'target': '27419',
       'ups': '1090727', 'walmart': '104169'}
CO = {'amazon': 'Amazon.com, Inc.', 'costco': 'Costco Wholesale Corp.', 'fedex': 'FedEx Corp.',
      'homedepot': 'The Home Depot, Inc.', 'target': 'Target Corp.', 'ups': 'United Parcel Service, Inc.',
      'walmart': 'Walmart Inc.'}
def edgar(cik, acc):
    return f'https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc.replace("-", "")}/'

def meta_for(r, p):
    """return dict(title, publisher, date, url, domain, access, role) from path rules (r relative to data/)."""
    fn = os.path.basename(r)
    parts = r.split('/')
    top = parts[0]
    D = dict(title='', publisher='', date='', url='', domain='', access='public', role='source')
    if parts[-1] == 'index.csv' or re.match(r'index\.pre_', parts[-1]) or parts[-1] in ('blocked_pending_fulltext.csv', 'search_results_index.csv'):
        D['role'] = 'catalog'
    if '/_scripts/' in r or fn.endswith('.py'):
        D['role'] = 'code'
    # ---------- private
    if top == 'private':
        db = parts[1]
        D['access'] = 'jhu_subscription'
        D['publisher'] = {'ebsco_business_source_ultimate': 'EBSCO Business Source Ultimate', 'ebsco_regional_business_news': 'EBSCO Regional Business News',
                          'eiu_data': 'Economist Intelligence Unit', 'ft_com': 'Financial Times', 'gale_directory_library': 'Gale Directory Library',
                          'hoovers_avention': 'D&B Hoovers', 'ibisworld': 'IBISWorld', 'marketresearch_com_academic': 'MarketResearch.com Academic',
                          'mergent_archives': 'Mergent Archives', 'mergent_intellect': 'Mergent Intellect', 'mergent_market_atlas': 'Mergent Market Atlas',
                          'newsbank_access_world_news': 'NewsBank Access World News', 'nexis_uni': 'Nexis Uni', 'proquest_abi_inform': 'ProQuest ABI/INFORM',
                          'proquest_business_market_research': 'ProQuest Business Market Research', 'proquest_central': 'ProQuest Central',
                          'proquest_us_newsstream': 'ProQuest US Newsstream', 'sage_business': 'SAGE Business Cases', 'sp_capital_iq_netadvantage': 'S&P Capital IQ NetAdvantage',
                          'statista': 'Statista', 'value_line': 'Value Line', 'wsj_proquest': 'Wall Street Journal via ProQuest',
                          'industry': 'ProQuest trade-press cache', '_access_probe_2026-10-31': 'Database access probe'}.get(db, db)
        D['_db'] = db
        return D
    # ---------- public raw
    sub = parts[1] if len(parts) > 1 else ''
    D['domain'] = {'benchmark': '', 'census': 'facilities', 'environment': 'environment', 'facilities': 'facilities',
                   'financial': 'financial', 'industry': 'industry', 'injuries': 'injuries', 'labor': 'labor',
                   'logistics': 'logistics', 'mwpvl_wayback': 'facilities', 'subsidies': 'financial'}.get(sub, '')
    m = None
    if sub == 'benchmark':
        b = parts[2]
        D['domain'] = {'environment': 'environment', 'injuries': 'injuries', 'labor': 'labor',
                       'network_financial': 'financial', 'warehousing_industry': 'industry'}.get(b, 'industry')
    if fn in ('.gitignore', '.zipdone'):
        D.update(publisher='n/a (housekeeping file)', title=fn, role='housekeeping'); return D
    if D['role'] == 'code':
        D.update(publisher='Project code kept beside the data (not a source)', title='Build script ' + fn, domain=D['domain'] or 'industry'); return D
    m = re.match(r'(\d{10})_(\d{4}-\d\d-\d\d)_(\d{10}-\d\d-\d{6})', fn)
    if m:
        cik = str(int(m.group(1))); co = next((k for k, v in CIK.items() if v == cik), '')
        D.update(publisher=f'SEC EDGAR ({CO.get(co, "CIK " + cik)})', date=m.group(2), url=edgar(cik, m.group(3)), title=f'{CO.get(co, "CIK " + cik)} annual report filed via {m.group(3)}')
        return D
    if '/sub/' in r and fn.endswith('.json'):
        nm = re.match(r'[a-z]+', fn).group(0)
        D.update(publisher='SEC EDGAR', title=f'EDGAR submissions index: {CO.get(nm, nm)}', url=f'https://data.sec.gov/submissions/CIK{int(CIK[nm]):010d}.json' if nm in CIK else 'https://data.sec.gov/submissions/', role='source'); return D
    if fn == 'list.tsv' and '10k' in r:
        D.update(publisher='SEC EDGAR', title='List of Amazon 10-K filings (derived from EDGAR submissions)', role='derived_list'); return D
    if fn.lower().startswith('cbp') and fn.lower().endswith('.txt'):
        yy = re.search(r'cbp(\d\d)', fn.lower()).group(1)
        D.update(publisher='U.S. Census Bureau', title=f'County Business Patterns 20{yy} national file: {fn}', date='20' + yy, url='https://www.census.gov/programs-surveys/cbp/data/datasets.html', role='extracted' if '/x_' in r else 'source'); return D
    # ---- SEC filings
    m = re.match(r'(?:(\d{4})_(10-K\w*)_|(\d{4}-\d\d-\d\d)_(10-K[\w-]*)_)(\d{10}-\d\d-\d{6})', fn)
    if m and sub in ('financial', 'labor'):
        acc = m.group(5)
        D.update(publisher='SEC EDGAR (Amazon.com, Inc.)', title=f'Amazon.com, Inc. Form {m.group(2) or m.group(4)} ({acc})', url=edgar(CIK['amazon'], acc))
        D['date'] = m.group(3) or m.group(1) or ''
        if sub == 'labor': D['domain'] = 'labor'
        if '/tenk_txt/' in r: D['role'] = 'derived_text'
        return D
    m = re.match(r'(costco|fedex|homedepot|target|ups|walmart|amazon)_(\d{4}-\d\d-\d\d)_(\d{10}-\d\d-\d{6})(\.item2\.txt|\.|)', fn)
    if m and 'benchmark' in r:
        co, dt, acc = m.group(1), m.group(2), m.group(3)
        D.update(publisher=f'SEC EDGAR ({CO[co]})', date=dt, url=edgar(CIK[co], acc),
                 title=f'{CO[co]} annual report filed via {acc}' + (' (Item 2 Properties extract)' if 'item2' in fn else ''))
        if 'item2' in fn or '/tenk_txt/' in r: D['role'] = 'derived_text'
        return D
    m = re.match(r'fy(\d{4})_', fn)
    if m and 'sec10k' in r:
        D.update(publisher='SEC EDGAR (Amazon.com, Inc.)', title=f'Amazon.com, Inc. 10-K fiscal year {m.group(1)}', date=m.group(1), url=f'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=1018724&type=10-K')
        return D
    m = re.match(r'amzn-(\d{4})(\d\d)(\d\d)\.htm', fn)
    if m:
        D.update(publisher='SEC EDGAR (Amazon.com, Inc.)', title=f'Amazon.com, Inc. Form 10-K for fiscal year ended {m.group(1)}-{m.group(2)}-{m.group(3)}', date=f'{m.group(1)}-{m.group(2)}-{m.group(3)}', url='https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=1018724&type=10-K')
        return D
    if re.search(r'(submissions|sub_\d|sub\.json|sub_00|^sub_)', fn) or fn in ('tenk_list.json', '10k_list.tsv'):
        m2 = re.search(r'CIK0*(\d+)|sub_0*(\d+)', fn)
        cik = (m2.group(1) or m2.group(2)) if m2 else ''
        co = next((k for k, v in CIK.items() if v == cik), '')
        nm = next((k for k in CIK if fn.startswith(k)), co)
        if nm and not cik: cik = CIK[nm]
        D.update(publisher='SEC EDGAR', title=f'EDGAR submissions index{" for " + CO[nm] if nm in CO else ""}' if 'list' not in fn else 'List of 10-K filings (derived from EDGAR submissions)',
                 url=f'https://data.sec.gov/submissions/CIK{int(cik):010d}.json' if cik else 'https://data.sec.gov/submissions/')
        D['role'] = 'derived_list' if 'list' in fn else 'source'
        return D
    if sub in ('financial', 'benchmark') and fn in ('companyfacts.json', 'amazon.json', 'costco.json', 'fedex.json', 'homedepot.json', 'target.json', 'ups.json', 'walmart.json') and ('facts' in r or sub == 'financial' or 'sec_revenue' in r):
        nm = fn[:-5] if fn != 'companyfacts.json' else 'amazon'
        D.update(publisher='SEC EDGAR XBRL company facts', title=f'XBRL company facts: {CO.get(nm, nm)}', url=f'https://data.sec.gov/api/xbrl/companyfacts/CIK{int(CIK[nm]):010d}.json')
        return D
    # ---- Good Jobs First
    if 'gjf' in r or 'subsidytracker' in fn:
        D.update(publisher='Good Jobs First (Subsidy Tracker)', title='Subsidy Tracker parent page: Amazon.com' + (' (saved page or challenge page)' if 'gjf' in r else ''),
                 url='https://subsidytracker.goodjobsfirst.org/parent/amazoncom', domain='financial')
        return D
    # ---- subsidies
    if sub == 'subsidies':
        st = parts[2] if len(parts) > 2 else ''
        D['publisher'] = 'unspecified (not in the state index.csv; filename prefix: ' + re.split(r'[_-]', fn)[0] + ')'
        D['title'] = pretty(fn)
        return D
    # ---- environment
    if sub == 'environment' or 'benchmark/environment' in r:
        if fn.startswith('amazon_sustainability_report'):
            D.update(publisher='Amazon', title='Amazon Sustainability Report ' + re.search(r'\d{4}', fn).group(0), url='https://sustainability.aboutamazon.com/reporting', date=re.search(r'\d{4}', fn).group(0))
        elif fn.startswith('amazon_carbon') or fn.startswith('amazon_renewable'):
            D.update(publisher='Amazon', title='Amazon ' + pretty(fn).replace('amazon ', ''), url='https://sustainability.aboutamazon.com/reporting')
        elif fn.startswith('cbecs'):
            D.update(publisher='U.S. EIA', title='Commercial Buildings Energy Consumption Survey 2018: ' + pretty(fn), url='https://www.eia.gov/consumption/commercial/data/2018/', date='2018')
        elif 'egrid' in fn.lower():
            D.update(publisher='U.S. EPA', title='eGRID: ' + pretty(fn), url='https://www.epa.gov/egrid')
        elif fn.startswith('ghg'):
            D.update(publisher='U.S. EPA', title='GHG Emission Factors Hub 2025: ' + pretty(fn), url='https://www.epa.gov/climateleadership/ghg-emission-factors-hub', date='2025')
        elif fn.startswith('epa_moves6'):
            D.update(publisher='U.S. EPA', title='MOVES heavy-duty exhaust emission rates (EPA-420-R-26-007)', url='https://www.epa.gov/moves', date='2026')
        elif fn.startswith('echo_air'):
            D.update(publisher='U.S. EPA ECHO', title='ECHO air facility query results for Amazon: ' + pretty(fn), url='https://echodata.epa.gov/echo/')
        elif fn.startswith('ninth_circuit'):
            D.update(publisher='U.S. Court of Appeals, Ninth Circuit', title='South Coast AQMD v. Amazon Air (No. 20-70272) opinion', date='2022-10-11', url='https://cdn.ca9.uscourts.gov/datastore/opinions/2022/10/11/20-70272.pdf')
        elif fn.startswith('scaqmd') or fn.startswith('waire'):
            D.update(publisher='South Coast AQMD', title='WAIRE Program: ' + pretty(fn), url='https://www.aqmd.gov/waire')
        elif fn.startswith('acs5'):
            D.update(publisher='U.S. Census Bureau', title='ACS 5-year 2023 variables used', url='https://api.census.gov/data/2023/acs/acs5/variables.html', date='2023')
        elif 'benchmark/environment' in r:
            co = parts[3] if len(parts) > 3 else ''
            D.update(publisher={'ups': 'UPS', 'costco': 'Costco', 'fedex': 'FedEx', 'homedepot': 'The Home Depot', 'target': 'Target', 'walmart': 'Walmart', 'sec_revenue': 'SEC EDGAR XBRL'}.get(co, co),
                     title=f'{co} sustainability or ESG source: {pretty(fn)}')
            if fn.endswith('.txt'): D['role'] = 'derived_text'
        return D
    # ---- census
    if sub == 'census':
        D.update(publisher='U.S. Census Bureau', domain='facilities')
        if fn.startswith('CenPop2020'):
            D.update(title='2020 Census tract population centers: ' + fn, url='https://www2.census.gov/geo/docs/reference/cenpop2020/tract/' + fn, date='2020')
        elif 'gaz' in r.lower():
            D.update(title='2020 Census Gazetteer: ' + pretty(fn), url='https://www.census.gov/geographies/reference-files/time-series/geo/gazetteer-files.html', date='2020')
        elif 'cb_' in r:
            D.update(title='Cartographic boundary file, states 1:20m (2020): ' + fn, url='https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.html', date='2020')
        return D
    # ---- facilities
    if sub == 'facilities':
        if fn.startswith('mwpvl'):
            D.update(publisher='MWPVL International', url='https://www.mwpvl.com/html/' + {'mwpvl_amazon.html': 'amazon.html', 'mwpvl_maps.html': 'amazon_maps.html', 'mwpvl_strategy.html': 'amazon_com_distribution_network_strategy.html'}.get(fn, ''))
            if fn == 'mwpvl_legacy_parsed.csv': D.update(role='derived_parse', title='MWPVL legacy facility table, parsed from Wayback snapshots', url='')
        elif fn.startswith('taxjar') or 'taxjar' in fn:
            D.update(publisher='TaxJar', url='https://blog.taxjar.com/amazon-warehouse-locations/')
            if fn == 'taxjar_parsed.csv': D.update(role='derived_parse', title='TaxJar Amazon warehouse list, parsed')
        elif fn.startswith('cavac'):
            D.update(publisher='Cavacopedia', title='List of Amazon locations (Cavacopedia)')
        elif fn.startswith('warehousegig'):
            D.update(publisher='WarehouseGig', url='https://warehousegig.com/blog/amazon-fulfillment-warehousing-locations/')
        elif fn.startswith('wikipedia'):
            D.update(publisher='Wikipedia', title='List of Amazon locations (Wikipedia)', url='https://en.wikipedia.org/wiki/List_of_Amazon_locations')
        elif fn.startswith('wikidata'):
            D.update(publisher='Wikidata', title='Wikidata query: Amazon sites', url='https://query.wikidata.org/')
        elif fn.startswith('census_geocode') or fn.startswith('census_input'):
            D.update(publisher='U.S. Census Bureau Geocoder', title=f'Census batch geocoder {"input" if "input" in fn else "output"}: {fn}', url='https://geocoding.geo.census.gov/geocoder/', role='derived_geocode')
        elif fn.startswith('osha_amazon_rows') or 'osha_ita' in r:
            D.update(publisher='OSHA', url='https://www.osha.gov/Establishment-Specific-Injury-and-Illness-Data', domain='injuries' if 'osha_ita' in r else 'facilities')
            if 'osha_ita' in r:
                D['title'] = 'OSHA Injury Tracking Application data: ' + pretty(fn)
                if '/x_' in r: D['role'] = 'extracted'
            else:
                D.update(title='Amazon rows extracted from OSHA ITA', role='derived_extract')
        elif fn == 'national_county2020.txt':
            D.update(publisher='U.S. Census Bureau', title='National county file 2020', url='https://www2.census.gov/geo/docs/reference/codes2020/national_county2020.txt')
        elif 'census_ref' in r:
            D.update(publisher='U.S. Census Bureau', title='Census reference file: ' + pretty(fn), url='https://www.census.gov/geographies/reference-files.html')
        return D
    # ---- industry
    if sub == 'industry':
        P = {'cunningham': ('University of Minnesota', 'Cunningham (2023) The Local Economic Impacts of Amazon, PhD dissertation (text)', '2023', 'https://hdl.handle.net/11299/'),
             'epi_chart': ('Economic Policy Institute', 'EPI chart: Amazon fulfillment centers total', '', ''),
             'epi_unfulfilled': ('Economic Policy Institute', 'Unfulfilled Promises: Amazon fulfillment centers do not generate broad-based employment growth (Zipperer and Jones)', '2018', 'https://files.epi.org/pdf/138921.pdf'),
             'epi.txt': ('Economic Policy Institute', 'EPI Unfulfilled Promises, text extract', '2018', 'https://files.epi.org/pdf/138921.pdf'),
             'jtlu_2438.pdf': ('Journal of Transport and Land Use', 'Schorung, Lecourt and Dablanc: Assessing the spatial footprint of e-commerce logistics (Amazon in the US)', '2024', 'https://doi.org/10.5198/jtlu.2024.2438'),
             'jtlu.txt': ('Journal of Transport and Land Use', 'Schorung et al. JTLU 17(1), text extract', '2024', 'https://doi.org/10.5198/jtlu.2024.2438'),
             'lease_avisonyoung': ('Avison Young', 'Avison Young bulk industrial lease report', '', ''),
             'lease_commercialobserver': ('Commercial Observer', 'Commercial Observer 2022 article on Amazon industrial leasing', '2022', ''),
             'lease_compstak': ('CompStak', 'Industrial Market Overview Report: Part Four', '', ''),
             'lease_realdeal_2019': ('The Real Deal', 'The Real Deal 2019 article on Amazon leasing', '2019', ''),
             'lease_realdeal_2023': ('The Real Deal', 'The Real Deal 2023 article on Amazon leasing', '2023', ''),
             'mwpvl_amazon_com': ('MWPVL International', 'Amazon Distribution Network Strategy', '', 'https://www.mwpvl.com/html/amazon_com.html'),
             'pb_psi_2020': ('Pitney Bowes (via Post&Parcel)', 'Pitney Bowes Parcel Shipping Index 2020 coverage', '2020', ''),
             'pb_psi_2021': ('Pitney Bowes (via MH&L News)', 'Pitney Bowes Parcel Shipping Index 2021 coverage', '2021', ''),
             'pb_psi_2022': ('Pitney Bowes (via FreightWaves)', 'Pitney Bowes Parcel Shipping Index 2022 coverage', '2022', ''),
             'pb_psi_2023': ('Pitney Bowes', 'Pitney Bowes Parcel Shipping Index 2023', '2023', ''),
             'pb_psi_2024': ('Pitney Bowes', 'Pitney Bowes Parcel Shipping Index 2024', '2024', ''),
             'pb_psi_2025': ('Pitney Bowes', 'Pitney Bowes Parcel Shipping Index 2025', '2025', ''),
             'robots_csmonitor': ('Christian Science Monitor', 'Article on Amazon warehouse robots (2014)', '2014', ''),
             'robots_entrepreneur': ('Entrepreneur', 'Article on Amazon robots (2025)', '2025', ''),
             'robots_thestar': ('Toronto Star', 'Article on Amazon warehouse robots (2014)', '2014', ''),
             'robots_yahoo': ('Yahoo / Business Insider', 'Article on Amazon robots', '', ''),
             'tg_amazon_facilities': ('The Geography of Transport Systems', 'E-Commerce Facilities Operated by Amazon in the United States, 2021', '2021', ''),
             'tg_amazon_fc': ('The Geography of Transport Systems', 'Amazon E-Fulfillment Centers Network', '', ''),
             'wiki_amazon_robotics': ('Wikipedia', 'Amazon Robotics (wikitext)', '', 'https://en.wikipedia.org/wiki/Amazon_Robotics')}
        for k, v in P.items():
            if fn.startswith(k):
                D.update(publisher=v[0], title=v[1], date=v[2], url=v[3])
                if fn.endswith('.txt') and k in ('epi.txt', 'jtlu.txt'): D['role'] = 'derived_text'
                break
        return D
    # ---- injuries
    if sub == 'injuries':
        D.update(publisher='OSHA / BLS')
        if fn.startswith('cy') and fn.endswith('.zip'):
            D.update(publisher='OSHA', title=f'OSHA ITA establishment-level injury data CY{fn[2:6]} (zip)', url='https://www.osha.gov/Establishment-Specific-Injury-and-Illness-Data', date=fn[2:6])
        elif parts[2].startswith('x') and len(parts) > 3 or (len(parts) > 2 and re.match(r'x\d{4}', parts[2])):
            D.update(publisher='OSHA', title=f'OSHA ITA CY{parts[2][1:]} data, extracted csv', url='https://www.osha.gov/Establishment-Specific-Injury-and-Illness-Data', date=parts[2][1:], role='extracted')
        elif 'bls' in fn:
            D.update(publisher='U.S. BLS', title='BLS SOII API ' + ('responses' if 'responses' in fn else 'probe'), url='https://api.bls.gov/publicAPI/v2/timeseries/data/')
        elif fn in ('find.html', 'ita_page.html', 'pdq.html'):
            D.update(publisher='OSHA' if fn != 'pdq.html' else 'U.S. BLS', title=html_title(p) or pretty(fn), url='https://www.osha.gov/Establishment-Specific-Injury-and-Illness-Data')
        return D
    # ---- logistics
    if sub == 'logistics':
        if fn.startswith('pb_'):
            y = re.search(r'20\d\d', fn).group(0)
            D.update(publisher='Pitney Bowes', title=f'Pitney Bowes Parcel Shipping Index press release {y}', date=y)
        elif fn.startswith('murphy'):
            D.update(publisher='Senator Chris Murphy / Amazon', title='Amazon response to Sen. Murphy on delivery service partners')
        elif fn == '_item2_extract.txt':
            D.update(publisher='SEC EDGAR (Amazon.com, Inc.)', title='Item 2 Properties extract from Amazon 10-Ks', role='derived_text')
        return D
    # ---- labor
    if sub == 'labor':
        if 'nlrb' in r:
            m = re.match(r'(\d{2}-[A-Z]{2}-\d+)', fn)
            D.update(publisher='NLRB', domain='labor')
            if m: D.update(title=f'NLRB case {m.group(1)}', url=f'https://www.nlrb.gov/case/{m.group(1)}')
            elif fn.startswith('p') and '/list' in r: D.update(title=f'NLRB case search results page {fn}', url='https://www.nlrb.gov/search/case')
            return D
        if re.match(r'cew_', fn) or fn == 'area_titles.csv':
            y = re.search(r'(20\d\d)', fn)
            D.update(publisher='U.S. BLS QCEW', date=y.group(1) if y else '', url='https://www.bls.gov/cew/downloadable-data-files.htm')
            if fn.endswith('.zip'): D['title'] = f'QCEW annual averages by industry {y.group(1) if y else ""} (zip)'
            elif fn == 'area_titles.csv': D['title'] = 'QCEW area titles'
            else:
                D['title'] = 'QCEW annual extract: ' + pretty(fn); D['role'] = 'extracted' if 'cew_extract' in r else 'derived_extract'
            return D
        if parts[2] == 'wages':
            D.update(publisher='Press or Amazon (see page title)', title=html_title(p) or 'Amazon wage announcement ' + pretty(fn))
            return D
        return D
    # ---- benchmark specifics
    if sub == 'benchmark':
        b = parts[2]
        if b == 'warehousing_industry':
            if fn.startswith('cbp'):
                y = re.search(r'cbp(\d\d)', fn)
                yr = ('20' + y.group(1)) if y else ''
                D.update(publisher='U.S. Census Bureau', title=f'County Business Patterns {yr} national file: {fn}', date=yr, url='https://www.census.gov/programs-surveys/cbp/data/datasets.html', role='extracted' if '/x_' in r else 'source')
            elif 'econ_census' in r or fn.startswith('EC') or fn.startswith('ec'):
                D.update(publisher='U.S. Census Bureau', title='Economic Census: ' + pretty(fn), url='https://www.census.gov/programs-surveys/economic-census.html', role='extracted' if '/x' in parts[3] else 'source')
            elif 'oews' in r or fn.startswith('oes'):
                D.update(publisher='U.S. BLS OEWS', title='Occupational Employment and Wage Statistics: ' + pretty(fn), url='https://www.bls.gov/oes/')
            elif 'qcew' in r:
                D.update(publisher='U.S. BLS QCEW', title='QCEW size-class extract NAICS 49x Q1', url='https://www.bls.gov/cew/downloadable-data-files.htm')
            return D
        if b == 'injuries':
            D.update(publisher='OSHA', title='ITA inputs manifest', role='catalog')
            return D
        if b == 'labor':
            if 'nlrb' in r:
                m = re.match(r'(\d{2}-[A-Z]{2}-\d+)', fn)
                D.update(publisher='NLRB')
                if m: D.update(title=f'NLRB case {m.group(1)}', url=f'https://www.nlrb.gov/case/{m.group(1)}')
                elif fn.startswith('p0'): D.update(title=f'NLRB case search results page {fn}', url='https://www.nlrb.gov/search/case')
                else: D.update(title=pretty(fn))
                return D
            if 'wages' in r:
                D.update(publisher='Press or company release (see title)', title=html_title(p) or pretty(fn))
                return D
        return D
    # ---- mwpvl wayback
    if sub == 'mwpvl_wayback':
        D.update(publisher='MWPVL International (via Internet Archive)', domain='facilities')
        m = re.match(r'(?:(.+?)__)?(\d{14})\.html', fn)
        if m:
            slug = m.group(1) or 'amazon'
            path = {'amazon': 'amazon', 'amazon_maps': 'amazon_maps', 'amazon_building_new_sortation_network': 'amazon_building_new_sortation_network', 'amazon_com_distribution_network_strategy': 'amazon_com_distribution_network_strategy'}.get(slug, slug)
            D.update(title=f'MWPVL {slug.replace("_", " ")} page, Wayback snapshot {m.group(2)}', date=f'{m.group(2)[:4]}-{m.group(2)[4:6]}-{m.group(2)[6:8]}',
                     url=f'https://web.archive.org/web/{m.group(2)}/https://www.mwpvl.com/html/{path}.html')
        elif fn == 'cdx.json':
            D.update(title='Wayback CDX listing for mwpvl.com Amazon pages', url='https://web.archive.org/cdx/search/cdx?url=mwpvl.com/html/amazon*', role='catalog')
        elif 'ocr_local' in r:
            D.update(title='Local OCR of MWPVL table image: ' + fn, role='derived_ocr')
        elif 'transcriptions' in r:
            D.update(title='Transcription adjudication data: ' + fn, role='derived_transcription')
        elif 'images' in r:
            D.update(title='MWPVL table image (Wayback): ' + fn, role='source_image')
        return D
    return D

DOMAIN_FROM_TOPIC = {'facilities': 'facilities', 'openings': 'facilities', 'facilities_openings': 'facilities', 'facilities_pullback': 'facilities',
                     'openings_pullback': 'facilities', 'closures': 'facilities', 'closures_pullback': 'facilities', 'amazon_air': 'logistics', 'air': 'logistics',
                     'robotics': 'logistics', 'robotics_air': 'logistics', 'delivery': 'logistics', 'delivery_economics': 'logistics', 'delivery_econ': 'logistics',
                     'couriers': 'logistics', '3pl': 'logistics', 'parcels': 'logistics', 'ecommerce': 'industry', 'warehousing': 'industry', 'labor': 'labor',
                     'wages_hiring': 'labor', 'injuries': 'injuries', 'safety': 'injuries', 'financial': 'financial', 'company_reports': 'financial',
                     'amazon_financials': 'financial', 'amazon_filings': 'financial', 'trade_journals': 'industry', 'industry_surveys': 'industry',
                     'market_share': 'industry', 'environment': 'environment'}
def private_domain(r, D, ix):
    t = (ix or {}).get('topic') or ''
    if not t:
        parts = r.split('/')
        t = parts[2] if len(parts) > 3 else ''
    t = t.lower()
    for k, v in DOMAIN_FROM_TOPIC.items():
        if t == k: return v
    if any(w in t for w in ('financ', 'filing', 'income', 'balance', 'cash')): return 'financial'
    if 'labor' in t or 'wage' in t or 'union' in t: return 'labor'
    if any(w in t for w in ('injur', 'safety', 'osha')): return 'injuries'
    if any(w in t for w in ('facil', 'open', 'closure', 'site')): return 'facilities'
    if any(w in t for w in ('air', 'robot', 'deliver', 'parcel', 'logist')): return 'logistics'
    if any(w in t for w in ('envir', 'energy', 'sustain')): return 'environment'
    return 'industry'

# ---------------------------------------------------------------- build rows
def mtime_date(m):
    return datetime.date.fromtimestamp(m).isoformat() if m else ''
rows = []
for p in files:
    r = rel(p)
    sha, size, mt = H[p]
    D = meta_for(r, p)
    ix = IDX.get(r)
    if ix is None:  # nexis sub-index etc.
        pass
    title, pub, date, url, ret = D['title'], D['publisher'], D['date'], D['url'], ''
    if ix:
        if ix['title']: title = ix['title']
        if ix['publication']: pub = ix['publication']
        if ix['date']: date = ix['date']
        if ix['url']: url = ix['url']
        ret = ix['retrieved']
    if D['role'] == 'source' and r.startswith('private/') and r.endswith(('.csv',)) and os.path.basename(r) in ('search_results_index.csv',):
        D['role'] = 'catalog'
    if r.startswith('private/'):
        D['domain'] = private_domain(r, D, ix)
        if '/_work/' in r or '/_challenge_pages/' in r or '/_raw/' in r or '/_searches/' in r or '/_search/' in r or '/_access_probe' in r:
            D['role'] = {'_work': 'work_file', '_challenge_pages': 'challenge_page', '_raw': 'search_results', '_searches': 'search_results', '_search': 'search_results'}.get(
                next((x for x in r.split('/') if x in ('_work', '_challenge_pages', '_raw', '_searches', '_search')), ''), 'probe')
        if D['role'] == 'source' and '_db' in D and D['_db'] == 'proquest_central' and r.endswith('.json') and not ix:
            D['role'] = 'search_or_challenge_unindexed'
        if ix is None and D['role'] == 'source':
            D['role'] = 'unindexed'
        if D.get('_db') == 'ft_com' and ix is not None:
            pass
    if r in BLOCKED: D['role'] = 'challenge_page'
    if not title:
        t = html_title(p) if r.endswith(('.html', '.htm')) and size < 50e6 else ''
        title = t or pretty(os.path.basename(r))
    if not ret: ret = mtime_date(mt)
    if date == ret or date == '2026-10-31': date = ''
    sid = 'src_' + hashlib.sha256(r.encode()).hexdigest()[:10]
    rows.append(dict(source_id=sid, title=title, publisher=pub, publication_date=date, url_or_doc_id=url, access=D['access'],
                     domain=D['domain'] or 'industry', local_path='data/' + r, size_bytes=size, sha256=sha, retrieved_date=ret,
                     role=D['role'], _p=p, _r=r))

# ---------------------------------------------------------------- used_by
doc_label = lambda p: os.path.relpath(p, ROOT)
by_tok = defaultdict(list)   # token -> corpus keys, only for non-script docs
for p, (k, s, t) in corpus.items():
    if k == 'script': continue
    for tk in s: by_tok[tk].append(p)

for row in rows:
    r, p = row['_r'], row['_p']
    base = os.path.basename(r)
    used = set()
    keys = {base}
    stem = os.path.splitext(base)[0]
    ix = IDX.get(r)
    if ix and ix.get('doc_id'): keys.add(ix['doc_id'])
    if r.startswith('private/'):
        keys.add(stem)
    if r.startswith('raw/census/') and len(base.split('.')[0]) >= 12: keys.add(base.split('.')[0])
    macc = re.search(r'\d{10}-\d\d-\d{6}', base)
    if macc: keys.add(macc.group(0))
    keys = {k for k in keys if len(k) >= 7}
    for k in keys:
        for cp in by_tok.get(k, ()):
            if cp == p: continue
            used.add(cp)
        for cp, (kind, s, t) in corpus.items():
            if kind == 'script' and t and k in t:
                used.add(cp)
    # also the "file" column of private index.csv: docs cited by id in processed CSVs: covered above
    if row['role'] != 'catalog':
        for sp in script_hits(r):
            used.add(sp)
    # html pages: url substring
    if row['url_or_doc_id'].startswith('http') and row['access'] == 'public':
        for cp, (kind, s, t) in corpus.items():
            if kind in ('page', 'notes') and t and row['url_or_doc_id'] in t:
                used.add(cp)
    # scripts bring their outputs
    outs = set()
    labels = set()
    for cp in used:
        kind = corpus[cp][0]
        if kind == 'script':
            labels.add(doc_label(cp))
            for o in script_out.get(cp, ()): labels.add('data/processed/' + o)
        elif kind == 'processed':
            labels.add('data/processed/' + os.path.basename(cp))
        elif kind == 'notes':
            labels.add(doc_label(cp))
        else:
            labels.add(os.path.basename(cp))
    row['used_by_list'] = sorted(labels)


# manual attributions (read from data/notes/*.md and grep of data/processed for the source name or URL; files cited by title, not filename)
P = 'data/processed/'; N = 'data/notes/'
MANUAL = [
 ('raw/industry/tg_amazon', [P+'logistics_facility_count_snapshots.csv', N+'industry_sources.md']),
 ('raw/industry/lease_', [P+'industry_amazon_leased_sqft.csv', N+'industry_sources.md']),
 ('raw/industry/robots_', [P+'industry_amazon_robot_counts.csv', N+'industry_sources.md']),
 ('raw/industry/wiki_amazon_robotics', [P+'industry_amazon_robot_counts.csv', N+'industry_sources.md']),
 ('raw/industry/pb_psi_', [P+'industry_pitney_bowes_parcel_index.csv', P+'logistics_us_parcel_volume.csv', N+'industry_sources.md']),
 ('raw/logistics/dsp/murphy', [P+'logistics_dsp.csv', N+'logistics.md']),
 ('raw/industry/epi_chart', [P+'industry_epi_fc_cumulative_counts.csv', N+'industry_sources.md']),
 ('raw/industry/jtlu.txt', [N+'industry_sources.md']),
 ('raw/financial/sub_00', [N+'financial.md']),
 ('raw/financial/submissions.json', [N+'financial.md']),
 ('raw/financial/tenk_txt/', [N+'financial.md']),
 ('raw/labor/cew_extract/', ['scripts/build_qcew.py']),
 ('raw/mwpvl_wayback/images/', ['scripts/mwpvl_image_reconcile.py', 'scripts/mwpvl_local_ocr.py', 'scripts/mwpvl_local_ocr_compare.py', 'scripts/mwpvl_local_ocr_parse.py', N+'mwpvl_wayback.md']),
 ('raw/census/gaz_counties/gaz.zip', ['scripts/build_trade_press.py']),
 ('raw/facilities/census_ref/gaz.zip', ['scripts/facilities_04_geocode.py']),
]
for row in rows:
    for frag, labs in MANUAL:
        if frag in row['_r']:
            ex = set()
            for l in labs:
                ex.add(l)
                if l.startswith('scripts/'):
                    for o in script_out.get(ROOT + '/' + l, ()): ex.add('data/processed/' + o)
            row['used_by_list'] = sorted(set(row['used_by_list']) | ex)

# ---------------------------------------------------------------- flags: orphans, duplicates
grp = defaultdict(list)
for row in rows:
    if row['size_bytes'] > 0 and not row['sha256'].startswith('ERR'):
        grp[row['sha256']].append(row)
for row in rows:
    flags = []
    g = grp.get(row['sha256'], [])
    if len(g) > 1:
        first = g[0]
        if row is first: flags.append(f'duplicate_group_of_{len(g)}')
        else: flags.append('duplicate_of:' + first['source_id'])
    if row['size_bytes'] == 0: flags.append('empty_file')
    if row['sha256'].startswith('ERR'): flags.append('unreadable')
    prod = [u for u in row['used_by_list']]
    if not prod and row['role'] not in ('catalog',):
        if row['role'] in ('code',): flags.append('code_not_source')
        else: flags.append('orphan')
    elif prod and all(u.startswith('data/notes/') or u == 'README.md' for u in prod) and row['role'] not in ('catalog',):
        flags.append('notes_mention_only')
    if row['role'] in ('challenge_page',): flags.append('challenge_page_not_article')
    if row['role'] == 'work_file': flags.append('work_file')
    row['flags'] = ';'.join(flags)

COLS = ['source_id', 'title', 'publisher', 'publication_date', 'url_or_doc_id', 'access', 'domain', 'local_path', 'size_bytes', 'sha256',
        'retrieved_date', 'used_by', 'role', 'flags']
with open(OUT, 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=COLS, extrasaction='ignore')
    w.writeheader()
    for row in rows:
        row['used_by'] = ' | '.join(row['used_by_list'][:12]) + (f' | +{len(row["used_by_list"]) - 12} more' if len(row['used_by_list']) > 12 else '')
        w.writerow(row)
print('wrote', OUT, len(rows), file=sys.stderr)
