"""Subscription bibliography: data/processed/bibliography_subscription.csv.

Run:  python3 -I scripts/build_bibliography.py

Turns the citations of facts drawn from JHU subscription databases (data/processed/jhu_*.csv, which stay local and gitignored) into one public-safe list:
publication, date, title, database, cited_in_public_data.
No quotes, no document ids, no URLs and no proxy links are written: only the four bibliographic fields and a flag saying whether the citation
appears in a published fact file (market_context.csv, pullback_sites.csv, pullback_aggregates.csv, facility_events_all.csv).
Pages cite these facts as "Publication, date, title (via database)".
"""
import csv, glob, os, re, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'data/processed')
OUT = os.path.join(P, 'bibliography_subscription.csv')
DATE_COLS = ('article_date', 'pub_date', 'published', 'doc_date', 'date')
PROXY = re.compile(r'ezproxy|\.proxy\.|login\.proxy|proquest\.com/docview|jhu\.idm|https?://', re.I)
FALLBACK_PUB = {'jhu_ibisworld_': ('IBISWorld', 'IBISWorld')}


def clean(s):
    return re.sub(r'\s+', ' ', (s or '')).strip()


rows = collections.OrderedDict()
for fp in sorted(glob.glob(os.path.join(P, 'jhu_*.csv'))):
    base = os.path.basename(fp)
    with open(fp, newline='', encoding='utf-8') as fh:
        for r in csv.DictReader(fh):
            pub, db = clean(r.get('publication')), clean(r.get('database'))
            title = clean(r.get('title') or r.get('report_title'))
            date = next((clean(r[c]) for c in DATE_COLS if clean(r.get(c))), '') or clean(r.get('edition'))
            for pre, (p_, d_) in FALLBACK_PUB.items():
                if base.startswith(pre):
                    pub, db = pub or p_, db or d_
            if not pub or not (title or date):
                continue
            pub = re.sub(r'\s*\(JHU subscription\)', '', pub)
            k = (pub, date, title, db)
            rows.setdefault(k, 0)
            rows[k] += 1

# citations that appear in published fact files
cit = {'market_context': [], 'pullback': [], 'facility_events': []}
def pieces(s):
    return [p.strip() for p in re.split(r';\s+', s or '') if p.strip()]
for fn, key, col in (('market_context.csv', 'market_context', 'citation'), ('pullback_sites.csv', 'pullback', 'sources'),
                     ('pullback_aggregates.csv', 'pullback', 'source'), ('facility_events_all.csv', 'facility_events', 'sources')):
    with open(os.path.join(P, fn), newline='', encoding='utf-8') as fh:
        for r in csv.DictReader(fh):
            cit[key].extend(x.lower() for x in pieces(r.get(col)))


def cited(pub, date, title):
    hit = []
    p = pub.lower()
    y = date[:4]
    for key, lst in cit.items():
        for c in lst:
            if p and p.split(' (')[0] in c and ((date and date.lower() in c) or (y and y in c)):
                hit.append(key)
                break
    return ';'.join(hit)


out = []
for (pub, date, title, db), n in rows.items():
    c = cited(pub, date, title)
    out.append(dict(publication=pub, date=date, title=title, database=db, cited_in_public_data=c or 'no'))
for r in out:
    for k, v in r.items():
        if PROXY.search(v):
            raise SystemExit('bibliography guard: URL or proxy text in %s: %s' % (k, v[:80]))
out.sort(key=lambda r: (r['database'].lower(), r['publication'].lower(), r['date'], r['title']))
with open(OUT, 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=['publication', 'date', 'title', 'database', 'cited_in_public_data'])
    w.writeheader()
    w.writerows(out)
print('bibliography rows: %d (cited in a public fact file: %d); databases: %d' % (len(out), sum(1 for r in out if r['cited_in_public_data'] != 'no'), len({r['database'] for r in out})))
print(collections.Counter(r['database'] for r in out).most_common())
