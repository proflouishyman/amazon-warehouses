#!/usr/bin/env python3
"""Generate data/SOURCES.md from data/sources_manifest.csv (counts only; no subscription content)."""
import csv, re, collections, datetime, os
ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
R = list(csv.DictReader(open(ROOT + '/sources_manifest.csv', encoding='utf-8')))
mb = lambda b: f'{b/1e6:,.0f} MB' if b >= 1e6 else f'{b/1e3:,.0f} KB'
def grp(r):
    p, lp = r['publisher'], r['local_path']
    if '/subsidies/' in lp: return 'State and local subsidy records (50 states and DC)'
    if 'mwpvl_wayback' in lp: return 'MWPVL via Internet Archive (snapshots, table images, OCR)'
    if p.startswith('SEC EDGAR'): return 'SEC EDGAR (Amazon and peer 10-Ks, submissions, XBRL facts)'
    if p.startswith('Press or'): return 'Press and company wage releases'
    if p.startswith('Project code'): return 'Project code kept beside the data (not sources)'
    if p.startswith('n/a'): return 'Housekeeping files'
    return re.sub(r'\s*\(.*\)$', '', p) or 'Unknown'
def folders(rows, n=3):
    c = collections.Counter('/'.join(r['local_path'].split('/')[:n]) for r in rows)
    return ', '.join(f'`{k}`' for k, _ in c.most_common(3)) + (' ...' if len(c) > 3 else '')
pub = [r for r in R if r['access'] == 'public']
sub = [r for r in R if r['access'] != 'public']
DOM = ['facilities', 'financial', 'labor', 'injuries', 'environment', 'logistics', 'industry']
size = lambda rows: sum(int(r['size_bytes']) for r in rows)
dup_extra = [r for r in R if 'duplicate_of:' in r['flags']]
orph = [r for r in R if 'orphan' in r['flags']]
L = []
A = L.append
A('# Source library')
A('')
A(f'Snapshot {datetime.date.today().isoformat()}. Every file under `data/raw` and `data/private` is catalogued in [`sources_manifest.csv`](sources_manifest.csv), one row per file '
  f'({len(R):,} files, {size(R)/1e9:.1f} GB). Nothing was moved or deleted to build it: files that scripts read stay where the scripts expect them, and the catalog points at them in place. '
  f'{len(pub):,} files ({size(pub)/1e9:.1f} GB) are public sources; {len(sub):,} files ({size(sub)/1e6:,.0f} MB) come from JHU subscription databases.')
A('')
A('Both folders are gitignored (`data/raw/`, `data/private/`). This guide and the manifest are the public record of what exists.')
A('')
A('## Manifest columns')
A('')
A('`source_id` (stable: hash of the path), `title`, `publisher`, `publication_date`, `url_or_doc_id`, `access` (public, jhu_subscription, paid), `domain`, `local_path` (relative to the project root), '
  '`size_bytes`, `sha256`, `retrieved_date`, `used_by` (scripts, notes and processed files that cite the file; first 12 shown), `role`, `flags`.')
A('')
A('`role` separates original sources (`source`, `source_image`) from derived or housekeeping files stored next to them (`derived_text`, `derived_ocr`, `extracted`, `derived_extract`, `derived_geocode`, '
  '`derived_parse`, `catalog`, `search_results`, `work_file`, `challenge_page`, `probe`, `code`, `unindexed`).')
A('`flags` holds `orphan`, `duplicate_group_of_N` (first copy), `duplicate_of:<source_id>` (later copies), `empty_file`, `challenge_page_not_article`, `notes_mention_only`, `work_file`.')
A('')
A('## Layout by domain and publisher (public sources)')
A('')
for d in DOM:
    rows = [r for r in pub if r['domain'] == d]
    if not rows: continue
    A(f'### {d.capitalize()} ({len(rows):,} files, {mb(size(rows))})')
    A('')
    A('| Publisher | Files | Size | Where |')
    A('|---|---:|---:|---|')
    g = collections.defaultdict(list)
    for r in rows: g[grp(r)].append(r)
    for k, v in sorted(g.items(), key=lambda kv: -len(kv[1])):
        A(f'| {k} | {len(v):,} | {mb(size(v))} | {folders(v)} |')
    A('')
A('Note on `data/raw/benchmark/`: it holds the peer-company comparison inputs (Costco, FedEx, Home Depot, Target, UPS, Walmart) for the environment, injuries, labor, network/financial and warehousing-industry benchmarks. '
  'Its 10-K copies overlap the Amazon 10-K folders (`financial/tenk`, `labor/10k`, `logistics/sec10k`), which is where most duplicates come from.')
A('')
A('## Public and subscription-only')
A('')
A('**Public** (`access = public`): government and agency data (SEC, BLS, Census, OSHA, EPA, NLRB, state and local records), company reports, the MWPVL Wayback snapshots, press pages and academic papers. '
  'Third-party pages and PDFs are kept locally for provenance but the raw folder is not published (some are copyrighted); rebuild with `scripts/`.')
A('')
A('**Subscription-only** (`access = jhu_subscription`): everything under `data/private/`, fetched through the JHU Sheridan Libraries licence. Never publish the files, text, extracts or quotes from them. '
  'The manifest lists only title, publication, date, a document id or link, and counts for these rows. Facts that came from them live in `data/processed/jhu_*.csv`, which should be reviewed before any public release.')
A('')
A('| Database | Files | Size |')
A('|---|---:|---:|')
g = collections.defaultdict(list)
for r in sub: g[r['publisher'] if False else r['local_path'].split('/')[2]].append(r)
names = {}
for r in sub: names.setdefault(r['local_path'].split('/')[2], None)
for k, v in sorted(g.items(), key=lambda kv: -len(kv[1])):
    A(f'| `{k}` | {len(v):,} | {mb(size(v))} |')
A('')
A('By domain (subscription files): ' + ', '.join(f'{d} {sum(1 for r in sub if r["domain"] == d):,}' for d in DOM) + '.')
A('')
A('No `paid` (one-off purchase) sources are held. The manifest `domain` for subscription articles comes from the database folder or the topic recorded at fetch time.')
A('')
A('## Duplicates')
A('')
dgroups = collections.Counter(r['flags'] for r in R if 'duplicate_group_of_' in r['flags'])
ngroups = sum(dgroups.values())
A(f'{ngroups} groups of identical files (same sha256) hold {len(dup_extra)} redundant copies, about {mb(sum(int(r["size_bytes"]) for r in dup_extra))}. Nothing was deleted. The first copy in path order is the group head; later copies are flagged `duplicate_of:<head source_id>`.')
A('')
fam = collections.Counter()
byhead = {r['source_id']: r for r in R}
for r in dup_extra:
    h = byhead.get(r['flags'].split('duplicate_of:')[1].split(';')[0])
    a = '/'.join(r['local_path'].split('/')[1:4]); b = '/'.join(h['local_path'].split('/')[1:4]) if h else '?'
    if a == b: a = b = '/'.join(r['local_path'].split('/')[1:5])
    fam[(a, b)] += 1
fam2 = collections.Counter()
for (a, b), n in fam.items(): fam2[tuple(sorted({a, b}))] += n
A('Main duplicate families (copies, by folder pair):')
A('')
for k, n in fam2.most_common(8): A(f'- {n} copies: {" and ".join(f"`data/{x}`" for x in k)}')
A('')
A('Typical causes: peer and Amazon 10-Ks fetched into several folders; OSHA ITA zips kept in both `facilities/osha_ita` and `injuries`; identical MWPVL Wayback snapshots; repeated image crops; empty `item2` extracts '
  f'({sum(1 for r in R if "empty_file" in r["flags"])} empty files, flagged `empty_file`).')
A('')
A('## Orphans')
A('')
po = [r for r in orph if r['access'] == 'public']
A(f'An orphan is a file that no script, note, page or processed file cites by filename, document id or accession, and whose directory no script or note names. {len(orph):,} files are flagged: {len(po)} public and {len(orph) - len(po):,} subscription.')
A('')
for r in po: A(f'- `{r["local_path"]}`: {r["title"]}')
A('')
A('The subscription orphans are saved full-text articles, search-result dumps, screenshots and probe files from which no fact row has been extracted yet (they are kept, not discarded). '
  'Largest groups: ' + ', '.join(f'`{k}` {v}' for k, v in collections.Counter('/'.join(r['local_path'].split('/')[2:4]) for r in orph if r['access'] != 'public').most_common(5)) + '. '
  'Citation matching depends on `data/processed/jhu_*.csv` as of the snapshot; parallel extraction runs may cite more of them later. Rerun the build script to refresh.')
A('')
ch = [r for r in R if r['role'] == 'challenge_page']
A(f'**ProQuest challenge pages**: {len(ch)} saved ProQuest pages are robot-challenge pages, not articles (role `challenge_page`): 168 in `proquest_central`, listed in `blocked_pending_fulltext.csv` for re-fetch once a person clears the challenge in the browser, and 11 in `proquest_abi_inform/_challenge_pages`. Their titles in the manifest are the article titles the page was meant to load, not content.')
A('')
A('## Rebuild')
A('')
A('`python3 scripts/build_sources_manifest.py` rewrites the manifest (read-only on the sources, about 10 seconds); `python3 scripts/gen_sources_md.py` rewrites this file from it.')
A('')
open(ROOT + '/SOURCES.md', 'w').write('\n'.join(L))
