"""Build data/processed/logistics_deals_public.csv from the local licensed-database deal file.
Citation-only: public source first, 'also PitchBook' second. No database descriptions or IDs.
Amount is kept only when the matched public page's title/snippet states it (checked here); year only, not day."""
import csv, json, os, re, urllib.parse
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'data/processed/jhu_pitchbook_deals.csv')
XC = os.path.join(ROOT, 'data/private/pitchbook/public_xcheck.jsonl')
OUT = os.path.join(ROOT, 'data/processed/logistics_deals_public.csv')
EXCLUDE = ('Parsons Business Park', 'Colchester Industrial', 'Rappi')  # Rappi: cited article is dated a year after the deal; match doubtful
#  # press describes data-center sites, not logistics

# Adversarial source check 2026-10-31 (data/notes/pitchbook_check.md). Keys: (PitchBook target name prefix, PitchBook date).
DROP = {
    ('Physical Intelligence', '2024-10-22'),  # cited source names Jeff Bezos personally, not Amazon or its fund
    ('BETA Technologies', '2026-02-11'),      # 13G disclosure of an existing 5.3% holding, not a new transaction
    ('Target', '2025-12-01'),                 # Rock Hill land is for a retail development; source dated 2026
}
FIX = {  # source_url / source_type replace the matched page; year / actor / target replace the output fields
    ('Air Transport Services Group', '2016-03-08'): {'source_url': 'https://www.airtransport.cc/about/news/year/2016/atsg-confirms-deal-amazon-operate-air-transport-network', 'source_type': 'primary'},
    ('Rivian Automotive', '2019-02-17'): {'actor': 'Amazon'},   # Climate Pledge Fund did not exist until 2020; WSJ says Amazon led
    ('Rivian Automotive', '2020-07-10'): {'actor': 'Amazon'},   # source names Amazon.com, not the fund
    ('Rightbot', '2025-01-06'): {'year': '2026'},               # cited article is dated 2026-01-06
    ('Ninjacart', '2022-05-18'): {'year': '2021'},              # cited article (PTI) is dated 2021-12-13
    ('West Jefferson Mega Warehouse', '2026-02-25'): {'target': 'Property purchase (see source)'},  # property name, not the seller
    ('Cardinal Capital', '2026-07-30'): {'target': 'Property purchase (see source)'},               # seller not named in source
    ('Symbotic', '2022-06-07'): {'source_url': 'https://www.supplychaindive.com/news/Walmart-invests-Symbotic-tech-stake/626140/', 'source_type': 'press'},
    ('Walmart Advanced Systems', '2022-11-09'): {'target': 'Alert Innovation', 'source_url': 'https://corporate.walmart.com/news/2022/10/06/expanding-walmarts-market-fulfillment-center-capabilities-through-automation', 'source_type': 'primary'},
    ('Inspectorio', '2018-07-10'): {'source_url': 'https://www.startribune.com/minneapolis-startup-inspectorio-raises-10-million-with-help-from-target-ecolab/488045821', 'source_type': 'press'},
}


def keyed(table, r):
    for (t, d), v in (table.items() if isinstance(table, dict) else ((k, True) for k in table)):
        if r['target'].startswith(t) and r['date'] == d:
            return v
    return None


PAGE_AMOUNTS = {  # cited-page URL fragment -> amount the adversarial check read on that page (pitchbook_check.md, 2026-10-31)
    'amazon-acquires-former-register-facility-for-63m': 63.2e6,
    'amazon-buys-143-acres-in-fort-myers': 66.5e6,
    'shopping-splurge-amazon-pays-record': 393.9e6,
    'amazon-west-town-warehouse-same-day-deliveries': 195e6,
    'industrial-complex-in-frederickson-for-219m': 219.5e6,
    'amazon-buys-former-forever-21': 146.2e6,
    'flipkart-walmart-invest-145mn-in-ninjacart': 145e6,
    'walmart-pays-121-5m-for-gaston-county-warehouse': 121.5e6,
}


def amount_forms(v):
    m = v / 1e6
    forms = set()
    for x in (m, round(m, 1)):
        s = ('%g' % x)
        forms.add('$' + s + ' million'); forms.add('$' + s + 'm'); forms.add('$' + s + ' m')
        forms.add('$' + s + 'million'); forms.add('$' + s + 'mn')
    if m >= 1000:
        b = '%g' % (m / 1000)
        forms |= {'$' + b + ' billion', '$' + b + 'b', '$' + b + 'bn', '$' + b + ' bn'}
    forms.add('${:,.0f}'.format(v))
    return [f.lower() for f in forms]


snip = {}
for line in open(XC):
    j = json.loads(line)
    for r in j['res'].get('results', []):
        snip.setdefault(j['k'], []).append(r)

PUB = {'aboutamazon.com': 'Amazon (aboutamazon.com)', 'businesswire.com': 'Business Wire', 'prnewswire.com': 'PR Newswire',
       'corporate.walmart.com': 'Walmart corporate news', 'airtransport.cc': 'ATSG (Air Transport International)', 'corporate.target.com': 'Target corporate news', 'symbotic.com': 'Symbotic newsroom'}


def pub(url):
    h = urllib.parse.urlparse(url).netloc.lower().replace('www.', '')
    if h in PUB:
        return PUB[h]
    return h


def who(a):
    if a.startswith('Walmart'): return 'Walmart'
    if a.startswith('Target'): return 'Target'
    if 'Climate Pledge' in a: return 'Amazon (via Climate Pledge Fund)'
    if 'Industrial Innovation' in a and 'Amazon.com' not in a: return 'Amazon (via Industrial Innovation Fund)'
    return 'Amazon'


def clean_target(t, cat):
    if cat == 'real_estate':
        base = re.sub(r'\s*\(.*$', '', t).strip()
        if base.lower().startswith(('amazon', 'walmart', 'target')) or not base:
            return 'Property purchase (see source)'
        return 'Property purchase from ' + base
    t = re.sub(r'\s*\(.*?\)', '', t).strip()
    return {'Amazon Robotics': 'Kiva Systems', 'Delivery Drivers': 'Delivery Drivers Inc.', 'Colis Prive': 'Colis Priv\u00e9'}.get(t, t)


rows = []
for r in csv.DictReader(open(SRC, newline='', encoding='utf-8')):
    if r['public_confirmed'] != 'yes' or not r['public_source_url']:
        continue
    if any(x in r['target'] for x in EXCLUDE) or keyed(DROP, r):
        continue
    fx = keyed(FIX, r) or {}
    if 'source_url' in fx:
        r['public_source_url'] = fx['source_url']; r['public_source_type'] = fx['source_type']
    d = r['date']
    dt = r['deal_type']
    typ = 'property purchase' if dt.startswith('Corporate Asset') else ('acquisition' if dt.startswith('Merger') else 'investment')
    amt = ''
    note = 'amount not shown: not confirmed in the cited source'
    if r['amount_usd'] and r['amount_basis'] == 'disclosed':
        v = float(r['amount_usd'])
        key = '%s|%s|%s|%s' % (r['acquirer_or_investor'], r['target'], '', '')
        text = ''
        for k, rs in snip.items():
            parts = k.split('|')
            if parts[1] == r['target'] and any(x['url'] == r['public_source_url'] for x in rs):
                text += ' '.join((x['title'] + ' ' + x.get('snippet', '')) for x in rs if x['url'] == r['public_source_url']).lower()
        # amounts the adversarial check read on the cited page itself (pitchbook_check.md), beyond the snippet match
        if any(f in text for f in amount_forms(v)):
            amt = str(int(v)); note = 'amount as stated in the cited source (round or purchase size, not necessarily the buyer\'s or investor\'s share)'
    page_amt = next((a for frag, a in PAGE_AMOUNTS.items() if frag in r['public_source_url']), None)
    if page_amt:  # publish the amount the cited page states, not PitchBook's figure
        amt = str(int(page_amt)); note = 'amount as stated in the cited source (round or purchase size, not necessarily the buyer\'s or investor\'s share)'
    rows.append({'year': fx.get('year', d[:4]), 'actor': fx.get('actor', who(r['acquirer_or_investor'])), 'peer_group': 'peer' if who(r['acquirer_or_investor']) in ('Walmart', 'Target') else 'amazon',
                 'target': fx.get('target', clean_target(r['target'], r['category'])), 'category': r['category'], 'deal_type': typ,
                 'amount_usd': amt, 'amount_note': note, 'source_url': r['public_source_url'], 'source_publisher': pub(r['public_source_url']),
                 'source_type': r['public_source_type'], 'citation': '%s; also PitchBook (via JHU Libraries, accessed 2026-10-31)' % pub(r['public_source_url'])})
rows.sort(key=lambda x: (x['peer_group'], x['category'], x['year'], x['target']))
with open(OUT, 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, list(rows[0])); w.writeheader(); w.writerows(rows)
print(len(rows), 'rows;', sum(1 for r in rows if r['amount_usd']), 'with amount;', sum(1 for r in rows if r['peer_group'] == 'peer'), 'peer')
