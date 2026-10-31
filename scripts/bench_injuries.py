"""Benchmark Amazon's OSHA ITA 300A injury rates against retail and logistics peers and NAICS 493 as a whole.

Rerun:  python3 -I scripts/bench_injuries.py          (about 1-2 minutes; reads 10 ITA files, writes 5 CSVs + 1 manifest)

Inputs (all local, nothing is downloaded):
  data/raw/facilities/osha_ita/x_*/*.csv  and  ITA_300A_Summary_Data_2025_through_08-31-2026.csv   (CY2016-CY2025, OSHA ITA Form 300A)
  data/processed/bls_soii_rates.csv                                                              (BLS SOII, NAICS 493110 reference rates)
  scripts/amazon_names.py                                                                        (Amazon matching rule, reused unchanged)

Outputs (the only files this script writes):
  data/processed/bench_injuries_establishments.csv    one row per matched peer/Amazon establishment-year inside the logistics scope
  data/processed/bench_injuries_peer_year.csv         per peer x scope x year: n, hours, TRC/DART/DAFW (hours-weighted), site median and IQR, share of sites above BLS
  data/processed/bench_injuries_493110_distribution.csv  ITA 493110 site-rate percentiles by year, excluding Amazon (and excluding Amazon + peers)
  data/processed/bench_injuries_name_audit.csv        every matched establishment name by NAICS (in-scope rows) so the rule can be audited
  data/processed/bench_injuries_match_audit.csv       every matched company name x NAICS with the status (included or the reason excluded)
  data/raw/benchmark/injuries/ita_inputs_manifest.json  sha256, size and row counts of the input files

Method (same as the Amazon series, see data/notes/injuries.md):
  dedupe on (year, street, city, state, establishment name), keeping the highest submission id;
  TRC = (DAFW+DJTR+other)*200000/hours, DART = (DAFW+DJTR)*200000/hours, DAFW = DAFW*200000/hours;
  rate_valid = hours >= 1000, all case counts present, employees >= 1 and 300 <= hours/employee <= 4500;
  aggregates are hours-weighted (sum cases * 200000 / sum hours over rate_valid sites).
Matching rules per peer are in PEERS below and are described in data/notes/bench_injuries.md.
"""
import csv, glob, re, os, sys, json, hashlib, collections, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from amazon_names import amazon_rule  # noqa: E402

csv.field_size_limit(10 ** 9)
ITA_DIR = ROOT + '/data/raw/facilities/osha_ita/'
OUT = ROOT + '/data/processed/'
RAW_OUT = ROOT + '/data/raw/benchmark/injuries/'
BLS_CSV = OUT + 'bls_soii_rates.csv'
ITA_URL = 'https://www.osha.gov/Establishment-Specific-Injury-and-Illness-Data'
FILES = sorted(glob.glob(ITA_DIR + 'x_*/*.csv')) + [ITA_DIR + 'ITA_300A_Summary_Data_2025_through_08-31-2026.csv']
YEARS = list(range(2016, 2026))
PARTIAL_YEARS = {2025}   # CY2025 file holds submissions received through 2026-08-31 only
I = re.I

# ---------------------------------------------------------------------------------------------
# Peer matching rules.  A row matches a peer when, in this order:
#   1. company_name matches one of the peer's company regexes (anchored at the start, so contractors working AT a peer site
#      and filed under their own name, e.g. "Lazer Spot Inc" with establishment "Target (T555) Woodland, CA", never match);
#   2. company_name is blank and the EIN is one of the peer's EINs, or the establishment name matches a company regex;
#   3. the EIN is one of the peer's EINs and the company name is something else (a site or client name, e.g. Kroger "Ruler Logistics",
#      Ryder "Electrolux"): matched ONLY when the NAICS is a logistics code (492, 493, 42x), because the same EINs also file
#      stores, dairies and bakeries; rule label 'ein_other_name_in_logistics_naics'. Otherwise the audit status is
#      'not_matched_ein_other_name_nonlogistics_naics'.
# `type`: retailer (store chains whose DCs file separately), 3pl (contract logistics), parcel (carriers).
# `dc_re`: only for retailers whose DCs are coded to a RETAIL NAICS: a row in a non-logistics NAICS is kept when the
#   establishment name matches dc_re (and state != DC, which would otherwise match "Washington DC" store names).
# `supplementary`: peers added beyond the ones asked for, shown separately.
# ---------------------------------------------------------------------------------------------
PEERS = collections.OrderedDict()


def peer(pid, label, ptype, company, eins=(), exclude=None, dc_re=None, supplementary=False, notes='', wholesale_out=()):
    PEERS[pid] = dict(label=label, type=ptype, company=[(l, re.compile(r, I)) for l, r in company], eins=set(eins),
                      exclude=re.compile(exclude, I) if exclude else None,
                      dc_re=re.compile(dc_re, I) if dc_re else None, supplementary=supplementary, notes=notes,
                      wholesale_out=set(wholesale_out))


peer('walmart', 'Walmart (incl. Sam\'s Club, Jet.com and other e-commerce units)', 'retailer',
     [('walmart_company', r"^\W*wal[- ]?mart\b"),
      ('sams_club', r"^\W*sam[`'’]?s\s+(west|east|club|wholesale)\b"),
      ('walmart_ecom_unit', r"\(\s*wal[- ]?mart[^)]*\)\s*$")],
     eins=['710862119', '710415188', '743019386', '710794414', '710794412', '660475164'],
     exclude=r"mckesson|cencora|amerisource",
     notes='Stores file as 452/455/445 and are excluded by NAICS. DCs file as 493110. Walmart private-fleet transportation files as 484 and is excluded. Sam\'s Club DCs filed under Wal-Mart Stores are not separable from Walmart.')
peer('target', 'Target', 'retailer',
     [('target_company', r"^\W*target(?:\s+corporation|\s+corp\.?)?\W*$")],
     eins=['410215170'],
     dc_re=r"\b(DC|FDC|UDC|DDC|SDC|CDC|RDC)\b|fulfillment center|distribution center|\bTFC\b|sortation center|return center|flow center|receive center",
     notes='Target files nearly all supply-chain sites under retail NAICS 452110/452112/452210 with "DC", "FDC", "UDC", "Fulfillment Center", "TFC" (Target.com fulfillment), "Sortation Center", "Return Center", "Flow Center" or "Receive Center" in the establishment name (the last five added 2026-10-31 on the bench review; the 10-K counts 66 supply chain facilities including sortation centers); D###/G###/R### "Office" rows (NAICS 551114, about 5 employees each) are store-district offices, not DCs, and are excluded.')
peer('home_depot', 'The Home Depot', 'retailer',
     [('home_depot_company', r"^\W*(the\s+)?home\s+depot\b")],
     eins=['581853319'],
     dc_re=r"\b(RDC|MDC|SDC|DC|FDC|DFC)\b",
     notes='RDC/MDO filings are NAICS 493110; a few DCs file under 444110 with "DC" or "MDC" in the name.')
peer('lowes', "Lowe's", 'retailer',
     [('lowes_company', r"^\W*lowe['`’]?s(?!\s+foods)\b"), ('lowes_company_nospace', r"^\W*lowes(?!\s*foods)\b")],
     eins=['560578072', '560748358'],
     exclude=r"lowes\s*foods",
     dc_re=r"flatbed dist|\b(RDC|DFC|XD|BDC|ADC|CDC)\b|distribution|3PL|fulfillment",
     wholesale_out=['423710'],
     notes="RDC/DFC/ADC filings are 493110. Flatbed distribution centers file under 444190. NAICS 423710 rows (names 2807-xxxx and 2807-xxxM, and, since the bench review, the 11 DC-named rows such as Charlotte Pro Fulfillment Center, 3PL-FC, BDC and ADC) are reported separately as retailer_42x and kept out of the headline because they are filed as wholesale and their function is not documented.")
peer('costco', 'Costco', 'retailer',
     [('costco_company', r"^\W*costco\b")],
     eins=['911223280', '844917236'],
     dc_re=r"\b(DDC|MDO|DEPOT)\b|costco logistics",
     notes='Depots file as 493110 (or 452311/455211 for a few years). "CW Trading" (423940) is a trading arm and is kept out of the headline.')
peer('kroger', 'Kroger (incl. banner companies)', 'retailer',
     [('kroger_company', r"^\W*kroger\b"),
      ('kroger_banner', r"^\W*(fred\s+meyer|dillons|roundy['`’]?s|smith['`’]?s\s+food|smiths\s+food|harris\s+teeter|ralphs\s+grocery|king\s+soopers|fry['`’]?s\s+food|qfc|quality\s+food\s+centers|city\s+market|pick\s*n\s*save|mariano['`’]?s|baker['`’]?s)\b")],
     eins=['311569568', '310345740', '311678530', '380900860', '844893897', '371333024', '870258768', '480196590', '930798201',
           '390854535', '954356030', '561390087'],
     notes='Stores file as 445 and Kroger manufacturing as 311, both excluded by NAICS; DCs, fulfillment centers (Ocado network) and banner "Logistics" sites file as 493110.')
peer('ups', 'UPS (package network and Supply Chain Solutions)', 'parcel',
     [('ups_company', r"^\W*(united\s+parcel\s+service|ups(?!\s+(store|flight|freight)))\b")],
     eins=['582480149'],
     exclude=r"^\W*ups\s+(store|flight)|jetstream|worldwide\s+flight",
     notes='Package centers, hubs and the air hub file as 492110; Supply Chain Solutions (SCS) warehouses and Mail Innovations file as 493110; UPS rows coded NAICS 484 (trucking) are excluded: they are filed as United Parcel Service and carry SLIC-coded building names (UPS package or feeder operations coded as trucking, not UPS Freight); UPS 488xxx rows (air gateways, SCS customs brokerage) are also excluded.')
peer('fedex_ground', 'FedEx Ground', 'parcel',
     [('fedex_ground_company', r"^\W*fedex\s+ground\b")],
     eins=['341441019', '621721435'],
     notes='FedEx Ground files as 492110 (hubs, terminals) under the name FedEx Ground through CY2023. From CY2024 (FedEx merged Ground into Federal Express Corporation in June 2024) no filing carries the Ground name, so CY2024+ Ground rows are inferred: a Federal Express Corporation row whose address was filed by FedEx Ground in CY2016-CY2023 and never by FedEx Express (match_rule federal_express_corp_2024plus_ground_address_continuity). Treat as approximate; CY2025 is also partial.')
peer('fedex_express', 'FedEx Express (supplementary)', 'parcel',
     [('fedex_express_company', r"^\W*(fedex\s+express|federal\s+express|fedex\s+services)\b")],
     eins=['710427007'], supplementary=True,
     notes='Supplementary. CY2024+ rows are Express addresses by continuity (see fedex_ground). FedEx Office (print shops) and FedEx Freight (trucking, 484) are excluded.')
peer('fedex_unassigned_2024plus', 'FedEx 2024+ filings not assignable to Express or Ground (supplementary)', 'parcel', [], supplementary=True,
     notes='From June 2024 FedEx Ground was merged into Federal Express Corporation and CY2024+ filings carry only that name. Rows are split by address continuity (see fedex_ground); rows at addresses never seen before 2024 or seen under both go here.')
peer('fedex_supply_chain', 'FedEx Supply Chain (supplementary)', '3pl',
     [('fedex_sc_company', r"^\W*fedex\s+supply\s+chain\b")],
     eins=['251766580', '260269389'], supplementary=True,
     notes='Supplementary. Contract warehouses (formerly GENCO); some filed under the client name with the FedEx Supply Chain EIN.')
peer('gxo', 'GXO Logistics (incl. XPO Logistics supply chain before the 2021 spin-off)', '3pl',
     [('gxo_company', r"^\W*gxo\b"),
      ('xpo_supply_chain_predecessor', r"^\W*xpo\b(?!.*(last\s*mile|freight|rxo|express|manufactur))")],
     eins=['562237457', '421399841', '943130689', '112874859', '862098312'],
     notes='GXO was spun out of XPO in August 2021. XPO-named filers (CY2017-CY2021) are matched when the EIN is one of the GXO entities, the EIN is blank, or the company name says Supply Chain; XPO Last Mile, freight, express and RXO are excluded by name and by NAICS (only 492/493/42x are kept). XPO 493110 filers with a foreign EIN and no Supply Chain in the name (about 15 rows) are not matched. match_rule xpo_supply_chain_predecessor marks these rows.')
peer('dhl_supply_chain', 'DHL Supply Chain (incl. Exel)', '3pl',
     [('dhl_supply_chain_company', r"^\W*(dhl\s+supply\s+chain|exel\b|dhl\s+continental|dhl\s+-)")],
     eins=['042801160', '42801160'],
     notes='Contract warehouses, NAICS 493110 (and 422/424 for a few Hillebrand and pharma sites).')
peer('dhl_express_ecom', 'DHL Express and eCommerce (supplementary)', 'parcel',
     [('dhl_express_ecom_company', r"^\W*dhl\b(?!\s+supply)")],
     eins=['943380425', '541427505'], supplementary=True,
     notes='Supplementary. DHL Express service centers and DHL eCommerce sort sites, NAICS 492110.')
peer('ryder', 'Ryder System (Supply Chain Solutions)', '3pl',
     [('ryder_company', r"^\W*ryder\b")],
     eins=['591506958', '872620504'],
     notes='Ryder SCS contract warehouses file as 493110; fleet management (484) and maintenance shops (811) are excluded by NAICS.')

GROUPS = {  # combined peer groups (primary peers only, supplementary excluded)
    'group_retailer_dcs': [p for p, d in PEERS.items() if d['type'] == 'retailer'],
    'group_3pl': ['gxo', 'dhl_supply_chain', 'ryder'],
    'group_parcel_carriers': ['ups', 'fedex_ground'],
}
LABELS = {'amazon': 'Amazon (logistics sites, same rule as the Amazon series)',
          'ita_493_ex_amazon': 'All ITA filers in NAICS 493 excluding Amazon',
          'ita_493110_ex_amazon': 'All ITA filers in NAICS 493110 excluding Amazon',
          'ita_493110_ex_amazon_ex_peers': 'ITA 493110 excluding Amazon and every matched peer',
          'group_retailer_dcs': 'Retailer DCs combined (Walmart, Target, Home Depot, Lowe\'s, Costco, Kroger)',
          'group_3pl': '3PL combined (GXO, DHL Supply Chain, Ryder)',
          'group_parcel_carriers': 'Parcel carriers combined (UPS, FedEx Ground)'}
for p, d in PEERS.items():
    LABELS[p] = d['label']
TYPES = {'amazon': 'ecommerce', 'ita_493_ex_amazon': 'industry', 'ita_493110_ex_amazon': 'industry',
         'ita_493110_ex_amazon_ex_peers': 'industry', 'group_retailer_dcs': 'group', 'group_3pl': 'group',
         'group_parcel_carriers': 'group'}
for p, d in PEERS.items():
    TYPES[p] = d['type']


def norm_naics(x):
    return re.sub(r'\.0+$', '', str(x or '').strip())


def norm_ein(x):
    return re.sub(r'\D', '', x or '')


def match_peer(company, estab, ein):
    """Return (peer_id, rule_label) or (None, audit_status). Walks peers in order, first match wins."""
    c = (company or '').strip()
    e = (estab or '').strip()
    ein = norm_ein(ein)
    hit_ein = None
    for pid, d in PEERS.items():
        if d['exclude'] and c and d['exclude'].search(c):
            continue
        if c:
            for lab, rx in d['company']:
                if rx.search(c):
                    if lab == 'xpo_supply_chain_predecessor' and not (ein in d['eins'] or ein == '' or re.search(r'suppl', c, I)):
                        return None, 'not_matched_xpo_other_ein'
                    return pid, lab
        else:
            if ein and ein in d['eins']:
                return pid, 'blank_company_peer_ein'
            for lab, rx in d['company']:
                if rx.search(e) and lab != 'xpo_supply_chain_predecessor':
                    return pid, 'blank_company_' + lab
        if ein and ein in d['eins'] and c and hit_ein is None:
            hit_ein = pid
    if hit_ein:
        return hit_ein, 'ein_other_name_in_logistics_naics'
    return None, None


def scope_group(pid, naics, estab, state):
    """Return (scope_group, in_headline, reason_if_excluded)."""
    g3 = naics[:3]
    d = PEERS.get(pid)
    if g3 == '493':
        return '493', True, ''
    if g3 == '492':
        return '492', True, ''
    if naics[:2] == '42':
        if pid == 'amazon':
            return '42x', False, ''
        if naics in d['wholesale_out']:
            return '42x', False, ''   # e.g. Lowe's 423710: filed as wholesale, kept out of the headline
        if d['type'] in ('3pl', 'parcel') or (d['dc_re'] and d['dc_re'].search(estab) and state != 'DC'):
            return '42x', True, ''
        return '42x', False, ''   # retailer wholesale-coded: reported, kept out of the headline
    if d and d['dc_re'] and state != 'DC' and d['dc_re'].search(estab):
        return 'retail_coded_dc', True, ''
    return None, False, 'excluded_naics_' + (g3 or 'blank')


def num(x):
    try:
        return float(x)
    except Exception:
        return None


def rates(r):
    h, emp = r['hours'], r['employees']
    dafw, djtr, oth = r['dafw_cases'], r['djtr_cases'], r['other_cases']
    tot = None if None in (dafw, djtr, oth) else dafw + djtr + oth
    dart = None if None in (dafw, djtr) else dafw + djtr
    r['total_cases'], r['dart_cases'] = tot, dart
    ok = bool(h and h >= 1000 and tot is not None and emp and emp >= 1 and 300 <= h / emp <= 4500)
    r['rate_valid'] = ok
    r['trc'] = round(tot * 200000 / h, 3) if ok else None
    r['dart'] = round(dart * 200000 / h, 3) if ok else None
    r['dafw'] = round(dafw * 200000 / h, 3) if ok else None
    return r


def percentile(vals, q):
    v = sorted(vals)
    if not v:
        return None
    k = (len(v) - 1) * q / 100.0
    lo = int(k)
    hi = min(lo + 1, len(v) - 1)
    return v[lo] + (v[hi] - v[lo]) * (k - lo)


def rnd(x, n=3):
    return None if x is None else round(x, n)


def load_bls():
    bls = {}
    m = {'total_recordable': 'trc', 'dart': 'dart', 'days_away': 'dafw'}
    with open(BLS_CSV, newline='') as fh:
        for r in csv.DictReader(fh):
            if r['naics'] == '493110' and r['case_type'] in m:
                bls[(int(r['year']), m[r['case_type']])] = float(r['rate_per_100_fte'])
    return bls


def main():
    os.makedirs(RAW_OUT, exist_ok=True)
    src_of = {}
    best = {}              # dedupe key -> row, for rows that matter
    manifest = []
    audit = collections.Counter()      # (peer, rule, company, ein, naics6, status) -> rows (before dedupe, raw count)
    for f in FILES:
        n_rows = 0
        h = hashlib.sha256()
        with open(f, 'rb') as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b''):
                h.update(chunk)
        with open(f, newline='', encoding='utf-8-sig', errors='replace') as fh:
            for raw in csv.DictReader(fh):
                n_rows += 1
                r = {k.lower(): v for k, v in raw.items()}
                c, e = r['company_name'].strip(), r['establishment_name'].strip()
                ein = norm_ein(r.get('ein', ''))
                naics = norm_naics(r['naics_code'])
                year = int(float(r['year_filing_for']))
                st = r['state'].strip()
                amz = amazon_rule(c, e, r.get('ein', ''), naics)
                pid, rule = None, None
                if amz:
                    pid, rule = 'amazon', amz
                else:
                    pid, rule_or_status = match_peer(c, e, ein)
                    if pid and rule_or_status == 'ein_other_name_in_logistics_naics' and not (naics[:3] in ('492', '493') or naics[:2] == '42'):
                        audit[(pid, rule_or_status, c[:60], ein, naics, 'not_matched_ein_other_name_nonlogistics_naics')] += 1
                        pid, rule_or_status = None, None
                    if pid:
                        rule = rule_or_status
                    elif rule_or_status:
                        audit[('', '', c[:60], ein, naics, rule_or_status)] += 1
                is493 = naics[:3] == '493'
                if not pid and not is493:
                    continue
                grp, head, why = (None, False, '')
                if pid:
                    grp, head, why = scope_group(pid, naics, e, st)
                    status = 'included_headline' if (grp and head) else ('included_not_headline_' + grp if grp else why)
                    audit[(pid, rule, c[:60], ein, naics, status)] += 1
                    if not grp and not is493:
                        continue
                row = dict(year=year, ita_id=r['id'], peer=pid or '', match_rule=rule or '', scope_group=grp or '', in_headline=bool(head),
                           ein=ein, company_name=c, establishment_name=e, establishment_id=r.get('establishment_id', ''),
                           street_address=r['street_address'].strip(), city=r['city'].strip(), state=st, zip_code=r['zip_code'].strip(),
                           naics_code=naics, industry_description=r['industry_description'].strip(),
                           employees=num(r['annual_average_employees']), hours=num(r['total_hours_worked']),
                           deaths=num(r['total_deaths']), dafw_cases=num(r['total_dafw_cases']), djtr_cases=num(r['total_djtr_cases']),
                           other_cases=num(r['total_other_cases']), source_file=os.path.basename(f))
                key = (year, row['street_address'].lower(), row['city'].lower(), st, e.lower())
                prev = best.get(key)
                if prev is None or float(row['ita_id']) > float(prev['ita_id']):
                    best[key] = row
        manifest.append(dict(file=os.path.relpath(f, ROOT), bytes=os.path.getsize(f), sha256=h.hexdigest(), data_rows=n_rows))
        print('read', os.path.basename(f), n_rows, file=sys.stderr)
    # second dedupe pass: the same site resubmitted under a re-punctuated name (Costco "0260 - TOLLESON AZ (WET) DEPOT" vs "0260   TOLLESON AZ (WET) DEPOT")
    # has a different name key. Drop rows that share year, address and the full numeric signature (hours, employees, all case counts), keeping the highest id.
    # Zero Amazon rows are affected, so the Amazon series is unchanged.
    sig = {}
    for r in best.values():
        k = (r['year'], re.sub(r'\W+', ' ', r['street_address'].lower()).strip(), r['city'].lower(), r['state'], r['hours'], r['employees'],
             r['dafw_cases'], r['djtr_cases'], r['other_cases'], r['deaths'])
        if not r['hours']:
            sig[(id(r),)] = r
            continue
        prev = sig.get(k)
        if prev is None or float(r['ita_id']) > float(prev['ita_id']):
            sig[k] = r
    n_sig = len(best) - len(sig)
    print('second-pass duplicates dropped', n_sig, file=sys.stderr)
    rows = [rates(r) for r in sig.values()]
    # FedEx: from CY2024 the Ground business files under Federal Express Corporation. Assign by address continuity with CY2016-CY2023 filings.
    def addr(r):
        return (re.sub(r'\W+', ' ', r['street_address'].lower()).strip(), r['city'].lower(), r['state'])
    g_addr = {addr(r) for r in rows if r['peer'] == 'fedex_ground' and r['year'] <= 2023}
    e_addr = {addr(r) for r in rows if r['peer'] == 'fedex_express' and r['year'] <= 2023}
    for r in rows:
        if r['peer'] == 'fedex_express' and r['year'] >= 2024:
            a = addr(r)
            if a in g_addr and a not in e_addr:
                r['peer'], r['match_rule'] = 'fedex_ground', 'federal_express_corp_2024plus_ground_address_continuity'
            elif a in e_addr and a not in g_addr:
                r['match_rule'] = 'federal_express_corp_2024plus_express_address_continuity'
            else:
                r['peer'], r['match_rule'] = 'fedex_unassigned_2024plus', 'federal_express_corp_2024plus_unassigned'
    # partial_year: FedEx Ground CY2024 rows are the post-merger (June to December 2024) part of the year only. Same sites: median hours per
    # employee 1,048 (CY2023) -> 645 (CY2024); hours ratio 0.62. Kept in the files, flagged, and left out of headline comparisons and groups.
    for r in rows:
        r['partial_year'] = bool(r['peer'] == 'fedex_ground' and r['year'] == 2024)
    for r in rows:
        r['source'] = 'OSHA ITA Form 300A, file %s, submission id %s; %s' % (r['source_file'], r['ita_id'], ITA_URL)
    # a peer match may have been deduped against a non-matching row under the same key; matched rows win only if latest id. Keep as is (same rule as Amazon).

    # ---- establishment table: peers + Amazon, in logistics scope
    est = [r for r in rows if r['peer'] and r['scope_group']]
    est.sort(key=lambda r: (r['peer'], r['year'], r['state'], r['city'], r['street_address'], r['establishment_name']))
    cols = ['peer', 'match_rule', 'scope_group', 'in_headline', 'year', 'ein', 'company_name', 'establishment_name', 'establishment_id',
            'street_address', 'city', 'state', 'zip_code', 'naics_code', 'industry_description', 'employees', 'hours', 'deaths',
            'dafw_cases', 'djtr_cases', 'other_cases', 'total_cases', 'dart_cases', 'trc', 'dart', 'dafw', 'rate_valid', 'partial_year', 'ita_id',
            'source_file', 'source']
    with open(OUT + 'bench_injuries_establishments.csv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, cols, extrasaction='ignore')
        w.writeheader()
        w.writerows(est)
    print('establishments', len(est))

    # ---- peer x scope x year
    bls = load_bls()
    bls_all = {}
    with open(BLS_CSV, newline='') as fh:
        for r in csv.DictReader(fh):
            if r['naics'] == '493000' and r['case_type'] in ('total_recordable', 'dart', 'days_away'):
                bls_all[(int(r['year']), {'total_recordable': 'trc', 'dart': 'dart', 'days_away': 'dafw'}[r['case_type']])] = float(r['rate_per_100_fte'])
    peer_ids = set(PEERS) | {'amazon'}
    peer_rows = [r for r in rows if r['peer'] in peer_ids and r['scope_group']]
    pool = {}   # population name -> list of rows
    for pid in peer_ids:
        pool[pid] = {'headline': [r for r in peer_rows if r['peer'] == pid and r['in_headline']]}
        for sg in ('493', '492', '42x', 'retail_coded_dc'):
            pool[pid][sg] = [r for r in peer_rows if r['peer'] == pid and r['scope_group'] == sg]
        pool[pid]['retailer_42x_not_headline'] = [r for r in peer_rows if r['peer'] == pid and r['scope_group'] == '42x' and not r['in_headline']]
    for g, members in GROUPS.items():
        pool[g] = {'headline': [r for r in peer_rows if r['peer'] in members and r['in_headline'] and not r['partial_year']]}
        for sg in ('493', '492'):
            pool[g][sg] = [r for r in peer_rows if r['peer'] in members and r['scope_group'] == sg]
    pool_493 = [r for r in rows if r['naics_code'][:3] == '493' and r['peer'] != 'amazon']
    pool_493110 = [r for r in pool_493 if r['naics_code'] == '493110']
    pool['ita_493_ex_amazon'] = {'headline': pool_493}
    pool['ita_493110_ex_amazon'] = {'headline': pool_493110}
    pool['ita_493110_ex_amazon_ex_peers'] = {'headline': [r for r in pool_493110 if not r['peer']]}

    def agg(rs, year):
        sub = [r for r in rs if r['year'] == year]
        val = [r for r in sub if r['rate_valid']]
        o = dict(n_establishments=len(sub), n_valid=len(val))
        o['partial_year'] = bool(sub) and all(r['partial_year'] for r in sub)
        hrs = sum(r['hours'] for r in val)
        o['hours_valid'] = int(hrs)
        o['employees_valid'] = int(sum(r['employees'] for r in val))
        for k, cc in (('trc', 'total_cases'), ('dart', 'dart_cases'), ('dafw', 'dafw_cases')):
            cs = sum(r[cc] for r in val)
            o[k + '_cases'] = int(cs)
            o[k] = rnd(cs * 200000 / hrs, 3) if hrs else None
            xs = [r[k] for r in val]
            o[k + '_site_median'] = rnd(percentile(xs, 50))
            o[k + '_site_p25'] = rnd(percentile(xs, 25))
            o[k + '_site_p75'] = rnd(percentile(xs, 75))
            b = bls.get((year, k))
            o['bls_493110_' + k] = b
            o[k + '_share_sites_above_bls'] = rnd(sum(1 for x in xs if x > b) / len(xs), 4) if (b is not None and xs) else None
        o['bls_493_trc'] = bls_all.get((year, 'trc'))
        o['bls_493_dart'] = bls_all.get((year, 'dart'))
        o['bls_493_dafw'] = bls_all.get((year, 'dafw'))
        o['hours_per_valid_site'] = int(hrs / len(val)) if val else None
        return o

    pcols = ['peer', 'peer_label', 'peer_type', 'supplementary', 'scope', 'year', 'year_note', 'n_establishments', 'n_valid',
             'low_n_flag', 'partial_year', 'headline_comparison_ok', 'hours_valid', 'employees_valid', 'hours_per_valid_site', 'trc_cases', 'dart_cases', 'dafw_cases', 'trc', 'dart', 'dafw',
             'trc_site_median', 'trc_site_p25', 'trc_site_p75', 'dart_site_median', 'dart_site_p25', 'dart_site_p75',
             'dafw_site_median', 'dafw_site_p25', 'dafw_site_p75', 'trc_share_sites_above_bls', 'dart_share_sites_above_bls',
             'dafw_share_sites_above_bls', 'bls_493110_trc', 'bls_493110_dart', 'bls_493110_dafw', 'bls_493_trc', 'bls_493_dart',
             'bls_493_dafw', 'source']
    src_peer = ('Computed by scripts/bench_injuries.py from OSHA ITA Form 300A establishment files CY2016-CY2025 (%s); '
                'BLS reference: SOII NAICS 493110 via data/processed/bls_soii_rates.csv (BLS Public Data API). '
                'Establishment-level rows and ids: bench_injuries_establishments.csv' % ITA_URL)
    out = []
    for pid, scopes in pool.items():
        for sc, rs in scopes.items():
            if not rs:
                continue
            for y in YEARS:
                a = agg(rs, y)
                if a['n_establishments'] == 0:
                    continue
                note = 'partial: CY2025 submissions received through 2026-08-31' if y in PARTIAL_YEARS else ('low OSHA compliance in first collection year' if y == 2016 else '')
                if a['partial_year']:
                    note = 'partial_year: FedEx Ground CY2024 filings cover about June to December 2024 only (after the merger into Federal Express Corporation); hours and cases are not full-year; do not compare'
                if pid == 'group_parcel_carriers' and y == 2024:
                    note = 'FedEx Ground CY2024 excluded as partial_year, so this is UPS only in 2024; not comparable with other years'
                a.update(peer=pid, peer_label=LABELS[pid], peer_type=TYPES[pid], supplementary=bool(PEERS.get(pid, {}).get('supplementary')),
                         scope=sc, year=y, year_note=note, headline_comparison_ok=(sc == 'headline' and not a['partial_year'] and y not in PARTIAL_YEARS), low_n_flag='n_valid<10' if a['n_valid'] < 10 else '', source=src_peer)
                out.append(a)
    with open(OUT + 'bench_injuries_peer_year.csv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, pcols, extrasaction='ignore')
        w.writeheader()
        w.writerows(out)
    print('peer_year', len(out))

    # ---- 493110 distribution (ex Amazon) by year
    dcols = ['population', 'year', 'year_note', 'measure', 'n_sites_valid', 'hours_valid', 'hours_weighted_rate', 'mean_site_rate', 'p05', 'p10', 'p25',
             'p50', 'p75', 'p90', 'p95', 'p99', 'bls_493110_rate', 'share_sites_above_bls', 'source']
    src_dist = ('Computed by scripts/bench_injuries.py from OSHA ITA Form 300A files CY2016-CY2025 (%s), NAICS 493110 filers, Amazon matched by '
                'scripts/amazon_names.py removed; rate_valid sites only; BLS: SOII 493110 via data/processed/bls_soii_rates.csv' % ITA_URL)
    dist = []
    for popname, rs in (('ita_493110_ex_amazon', pool_493110), ('ita_493110_ex_amazon_ex_peers', [r for r in pool_493110 if not r['peer']]),
                        ('ita_493110_amazon', [r for r in rows if r['peer'] == 'amazon' and r['naics_code'] == '493110'])):
        for y in YEARS:
            val = [r for r in rs if r['year'] == y and r['rate_valid']]
            if not val:
                continue
            hrs = sum(r['hours'] for r in val)
            for k, cc in (('trc', 'total_cases'), ('dart', 'dart_cases'), ('dafw', 'dafw_cases')):
                xs = [r[k] for r in val]
                b = bls.get((y, k))
                dist.append(dict(population=popname, year=y, year_note='partial: CY2025 submissions received through 2026-08-31' if y in PARTIAL_YEARS else '',
                                 measure=k, n_sites_valid=len(val), hours_valid=int(hrs),
                                 hours_weighted_rate=rnd(sum(r[cc] for r in val) * 200000 / hrs), mean_site_rate=rnd(sum(xs) / len(xs)),
                                 **{('p%02d' % q): rnd(percentile(xs, q)) for q in (5, 10, 25, 50, 75, 90, 95, 99)},
                                 bls_493110_rate=b, share_sites_above_bls=rnd(sum(1 for x in xs if x > b) / len(xs), 4) if b is not None else None,
                                 source=src_dist))
    with open(OUT + 'bench_injuries_493110_distribution.csv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, dcols)
        w.writeheader()
        w.writerows(dist)
    print('distribution', len(dist))

    # ---- name audit: in-scope matched establishment names by NAICS
    names = collections.defaultdict(lambda: dict(years=set(), n=0, states=set(), headline=False, rule=set(), company=set()))
    for r in est:
        k = (r['peer'], r['scope_group'], r['naics_code'], r['establishment_name'])
        d = names[k]
        d['years'].add(r['year']); d['n'] += 1; d['states'].add(r['state']); d['headline'] = r['in_headline']
        d['rule'].add(r['match_rule']); d['company'].add(r['company_name'])
    with open(OUT + 'bench_injuries_name_audit.csv', 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['peer', 'scope_group', 'naics_code', 'establishment_name', 'company_names_filed_under', 'match_rules', 'in_headline',
                    'n_establishment_years', 'years', 'states', 'source'])
        for k in sorted(names):
            d = names[k]
            w.writerow([k[0], k[1], k[2], k[3], ' | '.join(sorted(d['company'])), ' | '.join(sorted(d['rule'])), d['headline'], d['n'],
                        ','.join(str(y) for y in sorted(d['years'])), ','.join(sorted(d['states'])),
                        'OSHA ITA Form 300A establishment files, see bench_injuries_establishments.csv for ids; ' + ITA_URL])
    print('name_audit', len(names))

    # ---- match audit: company x NAICS x status (raw rows before dedupe)
    with open(OUT + 'bench_injuries_match_audit.csv', 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['peer', 'match_rule', 'company_name', 'ein', 'naics_code', 'status', 'raw_rows_before_dedupe', 'source'])
        for k, v in sorted(audit.items(), key=lambda kv: (kv[0][0], kv[0][5], -kv[1], kv[0][2])):
            w.writerow(list(k) + [v, 'OSHA ITA Form 300A establishment files; ' + ITA_URL])
    print('match_audit', len(audit))

    with open(RAW_OUT + 'ita_inputs_manifest.json', 'w') as fh:
        json.dump(dict(generated=datetime.date.today().isoformat(), note='Input files used by scripts/bench_injuries.py; the files themselves stay in data/raw/facilities/osha_ita/',
                       source=ITA_URL, files=manifest), fh, indent=1)


if __name__ == '__main__':
    main()
