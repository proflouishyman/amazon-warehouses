#!/usr/bin/env python3
"""Build NoSQL-reader-style JSONL documents from the Amazon logistics project data.

Run:  python3 -I scripts/build_nosql.py [--only facilities,subsidies,...] [--no-text] [--verify-hashes]

Output: data/nosql/<collection>.jsonl  (gitignored: contains private and subscription material).
Format notes: data/nosql/FORMAT_NOTES.md. Rerunnable: an existing output file whose content differs is
copied to data/nosql/_backups/ before it is overwritten. Nothing is ever deleted.

Every document carries the reader's envelope (_id, ocr_text, summary, sections, rows, filename, relative_path,
file_path, file_hash, collection, archive_structure, entities, document_type, year, schema_version) plus
provenance {source_files[{path, sha256, manifest_id, kind}], build_script, build_date, access_class}.
"""
import argparse
import collections
import concurrent.futures
import csv
import hashlib
import html
import html.parser
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'data'
PROC = DATA / 'processed'
OUT = DATA / 'nosql'
BUILD_DATE = '2026-10-31'
SCRIPT = 'scripts/build_nosql.py'
SCHEMA_VERSION = 1
TEXT_CAP = 150_000          # characters kept per extracted source text
HTML_READ_CAP = 12_000_000  # bytes of an HTML file read before stripping
PDF_MAX_PAGES = 150
ACCESS_RANK = {'public': 0, 'jhu_subscription': 1, 'pitchbook': 2}
csv.field_size_limit(sys.maxsize)

# ----------------------------------------------------------------------------- helpers
_sha_cache = {}


def sha256_file(path):
    path = Path(path)
    k = str(path)
    if k not in _sha_cache:
        h = hashlib.sha256()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(1 << 20), b''):
                h.update(chunk)
        _sha_cache[k] = h.hexdigest()
    return _sha_cache[k]


def rd(name, base=None):
    p = (base or PROC) / name
    with open(p, newline='', encoding='utf-8', errors='replace') as f:
        return list(csv.DictReader(f))


def rel(p):
    return str(Path(p).resolve().relative_to(ROOT))


NO_NUM = re.compile(r'(naics|fips|zip|cik|accession|code|(^|_)id$|_id_|pbid|phone|case_number|source_id|sic|air_ids|geoid|tract|row_id|occ_)', re.I)
NUM = re.compile(r'^-?\d+(\.\d+)?$')


def coerce(k, v):
    """CSV string -> number where it is clearly numeric (never for code-like columns)."""
    if v is None:
        return None
    if not isinstance(v, str):
        return v
    v = v.strip()
    if v == '':
        return None
    if NO_NUM.search(k) or not NUM.match(v):
        return v
    if len(v) > 1 and v[0] == '0' and not v.startswith('0.'):
        return v
    try:
        f = float(v)
    except ValueError:
        return v
    if '.' not in v and len(v) < 16:
        return int(v)
    return f


def clean(d, drop=()):
    return {k: coerce(k, v) for k, v in d.items() if k not in drop and coerce(k, v) is not None}


def slug(s, n=40):
    return re.sub(r'[^a-z0-9]+', '-', str(s).lower()).strip('-')[:n] or 'x'


SUB_RE = re.compile(r'via (ProQuest|NewsBank|Nexis|EBSCO|S&P|Capital IQ|Mergent|Value Line|IBISWorld|Hoovers|Avention|EIU|Gale|Sage|FT\.com|WSJ|Factiva|MarketResearch|Business Source|JHU)'
                    r'|proquest_subscription|jhu_subscription|ProQuest result list', re.I)
PB_RE = re.compile(r'pitchbook', re.I)


def access_of_text(*texts):
    t = ' '.join(x for x in texts if x)
    if SUB_RE.search(t):
        return 'jhu_subscription'
    return 'public'


def max_access(classes):
    cs = [c for c in classes if c]
    return max(cs, key=lambda c: ACCESS_RANK.get(c, 1)) if cs else 'public'


def oid(coll, key):
    return {'$oid': hashlib.sha1(f'{coll}:{key}'.encode()).hexdigest()[:24]}


# ----------------------------------------------------------------------------- manifest
class Manifest:
    def __init__(self):
        with open(DATA / 'sources_manifest.csv', newline='', encoding='utf-8') as f:
            self.rows = list(csv.DictReader(f))
        self.by_path = {r['local_path']: r for r in self.rows}
        self.by_id = {r['source_id']: r for r in self.rows}
        self.by_url = {}
        for r in self.rows:
            u = self.nurl(r['url_or_doc_id'])
            if u:
                self.by_url.setdefault(u, r)

    @staticmethod
    def nurl(u):
        u = (u or '').strip().lower()
        if not u.startswith('http'):
            return ''
        u = re.sub(r'^https?://(www\.)?', '', u)
        u = re.sub(r'^web\.archive\.org/web/\d+(im_|id_)?/', 'wayback:', u)
        return u.rstrip('/')

    def find(self, path=None, url=None):
        if path:
            p = path if path.startswith('data/') else 'data/' + path.lstrip('/')
            if p in self.by_path:
                return self.by_path[p]
        if url:
            return self.by_url.get(self.nurl(url))
        return None


MAN = None


def src_file_entry(path, kind='processed_input'):
    p = ROOT / path
    return {'path': path, 'sha256': sha256_file(p), 'manifest_id': None, 'kind': kind}


def manifest_entry(m, kind='manifest_source'):
    return {'path': m['local_path'], 'sha256': m['sha256'], 'manifest_id': m['source_id'], 'kind': kind, 'access_class': m['access']}


# ----------------------------------------------------------------------------- document builder
def render_text(title, summary, sections, rows):
    L = [title, '']
    if summary:
        L += [summary, '']
    for s in sections:
        L.append(s['section_name'].upper())
        for f in s['fields']:
            L.append(f"{f['field_name']}: {f['value']}")
        L.append('')
    by = collections.OrderedDict()
    for r in rows:
        by.setdefault(r.get('table', 'rows'), []).append(r)
    for t, rs in by.items():
        cols = []
        for r in rs:
            for k in r:
                if k not in ('table', 'access_class') and k not in cols:
                    cols.append(k)
        L.append(f'[{t}] ' + ' | '.join(cols))
        for r in rs:
            L.append(' | '.join('' if r.get(c) is None else str(r.get(c)) for c in cols))
        L.append('')
    return '\n'.join(L).strip() + '\n'


def sec(name, d, skip_empty=True):
    fields = []
    for k, v in d.items():
        if skip_empty and (v is None or v == '' or v == []):
            continue
        fields.append({'field_name': k, 'value': v})
    return {'section_name': name, 'fields': fields} if fields else None


def make_doc(coll, key, *, title, summary, sections, rows=(), source_files, document_type, year=None, entities=None,
             physical_box='', file_path=None, links=None, source_refs=None, base_access='public', extra=None,
             ocr_text=None, truncated=None, source_image_path=None):
    sections = [s for s in sections if s]
    rows = list(rows)
    classes = {base_access}
    classes.update(r.get('access_class') for r in rows if r.get('access_class'))
    classes.update(sf.get('access_class') for sf in source_files if sf.get('access_class'))
    acc = max_access(classes)
    doc = {
        '_id': oid(coll, key),
        'doc_id': f'{coll}:{key}',
        'entity_type': coll,
        'entity_key': key,
        'collection': f'amazon_{coll}',
        'filename': f'{slug(key, 80)}.json',
        'relative_path': f'nosql/{coll}/{slug(key, 80)}.json',
        'file_path': file_path or (source_files[0]['path'] if source_files else None),
        'source_image_path': source_image_path,
        'ocr_text': ocr_text if ocr_text is not None else render_text(title, summary, sections, rows),
        'summary': summary,
        'sections': sections,
        'rows': rows,
        'entities': entities or {'PERSON': [], 'GPE': [], 'DATE': [], 'ORG': []},
        'document_type': document_type,
        'year': year,
        'archive_structure': {'format': 'structured_record', 'series': coll, 'physical_box': physical_box or coll,
                              'page_id': key, 'path_components': ['amazon', coll]},
        'title': title,
        'links': links or {},
        'source_refs': source_refs or [],
        'provenance': {'source_files': source_files, 'build_script': SCRIPT, 'build_date': BUILD_DATE, 'access_class': acc},
        'access_class': acc,
        'access_classes': sorted(classes, key=lambda c: ACCESS_RANK.get(c, 1)),
        'contains_subscription': acc != 'public',
        'ocr_text_truncated': truncated,
        'sections_degenerate': False,
        'schema_version': SCHEMA_VERSION,
        'built': BUILD_DATE,
    }
    if extra:
        doc.update(extra)
    h = hashlib.sha256(json.dumps(doc, sort_keys=True, ensure_ascii=False, default=str).encode()).hexdigest()
    doc['file_hash'] = h
    return doc


class Writer:
    """Writes data/nosql/<coll>.jsonl, backing up a differing existing file first."""

    def __init__(self):
        OUT.mkdir(parents=True, exist_ok=True)
        self.stats = {}

    def write(self, coll, docs):
        tmp = OUT / f'.{coll}.jsonl.tmp'
        ids = set()
        with open(tmp, 'w', encoding='utf-8') as f:
            for d in docs:
                k = d['_id']['$oid']
                if k in ids:
                    raise SystemExit(f'duplicate _id in {coll}: {d["doc_id"]}')
                ids.add(k)
                f.write(json.dumps(d, ensure_ascii=False, default=str) + '\n')
        final = OUT / f'{coll}.jsonl'
        if final.exists():
            if sha256_file_nocache(final) == sha256_file_nocache(tmp):
                tmp.unlink()
                self.stats[coll] = (len(ids), final.stat().st_size, 'unchanged')
                return
            bdir = OUT / '_backups'
            bdir.mkdir(exist_ok=True)
            shutil.copy2(final, bdir / f'{coll}.{time.strftime("%Y%m%d_%H%M%S")}.jsonl')
        tmp.replace(final)
        self.stats[coll] = (len(ids), final.stat().st_size, 'written')


def sha256_file_nocache(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()


# ----------------------------------------------------------------------------- subsidies
def load_awards():
    js = (ROOT / 'assets' / 'data_subsidies.js').read_text(encoding='utf-8')
    j = json.loads(js[js.index('=') + 1:].strip().rstrip(';'))
    cols, rows = j['awards']['cols'], j['awards']['rows']
    aw = [dict(zip(cols, r)) for r in rows]
    csvrows = [r for r in rd('subsidies_verified.csv') if r['row_kind'] == 'award']
    K = ('state', 'locality', 'county', 'facility_desc', 'program', 'award_year', 'amount_usd', 'source_url')
    pool = collections.defaultdict(list)
    for r in csvrows:
        pool[tuple(str(r[k]) for k in K)].append(r)
    for a in aw:
        lst = pool.get(tuple(str(a.get(k, '') if a.get(k) is not None else '') for k in K))
        a['_csv'] = lst.pop(0) if lst else {}
    return aw


def split_codes(s, known):
    toks = re.findall(r'[A-Z][A-Z0-9]{2,4}', s or '')
    return [t for t in toks if t in known]


def build_subsidies(site_to_fids):
    aw = load_awards()
    docs, used, by_site = [], collections.Counter(), collections.defaultdict(list)
    files = [src_file_entry('assets/data_subsidies.js'), src_file_entry('data/processed/subsidies_verified.csv')]
    for a in aw:
        c = a['_csv']
        base = '|'.join(str(a.get(k)) for k in ('state', 'locality', 'facility_desc', 'program', 'award_year', 'amount_usd', 'source_url'))
        key = f"SUB-{a['state']}-{hashlib.sha1(base.encode()).hexdigest()[:8]}"
        used[key] += 1
        if used[key] > 1:
            key += f'-{used[key]}'
        lf = c.get('local_file') or ''
        m = MAN.find(path=lf if lf else None, url=a.get('source_url'))
        srcdoc = ('data/' + lf.lstrip('/')) if lf else None
        sf = list(files)
        if m:
            sf.append(manifest_entry(m))
        codes = split_codes(a.get('site_code') or '', site_to_fids)
        fids = sorted({f for cd in codes for f in site_to_fids[cd]})
        for cd in codes:
            by_site[cd].append(key)
        amt = coerce('amount_usd', a.get('amount_usd') or '')
        basis = a.get('amount_basis') or 'no amount'
        summ = (f"{a.get('program') or 'Subsidy'} ({a.get('subsidy_type') or 'type not stated'}), {a['state']}"
                f"{', ' + a['locality'] if a.get('locality') else ''}, {a.get('award_year') or 'year not stated'}; "
                f"{('$%s (%s)' % (format(int(amt), ','), basis)) if isinstance(amt, (int, float)) else 'no amount stated'}; "
                f"verification {a.get('verification_level')}; recipient class {a.get('recipient_class')}.")
        rows = []
        base_access = m['access'] if m else 'public'
        secs = [
            sec('Award', {k: coerce(k, a.get(k) or '') for k in ('state', 'locality', 'county', 'facility_desc', 'site_code', 'program', 'award_year',
                                                                  'amount_usd', 'amount_basis', 'subsidy_type', 'term_years', 'jobs_promised',
                                                                  'investment_promised', 'issuer')}),
            sec('Verification', {'verification_level': a.get('verification_level'), 'basis': basis, 'source_url': a.get('source_url'),
                                 'alt_sources': c.get('alt_sources'), 'notes': c.get('notes'), 'row_kind': a.get('row_kind')}),
            sec('Recipient', {'recipient_class': a.get('recipient_class'), 'recipient_rule': a.get('recipient_rule'),
                              'recipient_mixed': a.get('recipient_mixed'), 'overlap_flag': a.get('overlap_flag')}),
            sec('Source document', {'local_path': srcdoc, 'manifest_id': m['source_id'] if m else None,
                                    'sha256': m['sha256'] if m else None,
                                    'on_disk': (ROOT / srcdoc).exists() if srcdoc else None}),
        ]
        docs.append(make_doc('subsidies', key, title=f"Subsidy {key}: {a.get('program') or 'none found'} ({a['state']})", summary=summ,
                             sections=secs, rows=rows, source_files=sf, document_type='subsidy_award',
                             year=coerce('award_year', a.get('award_year') or ''), entities={'PERSON': [], 'GPE': [a['state']] + ([a['locality']] if a.get('locality') else []), 'DATE': [str(a.get('award_year'))] if a.get('award_year') else [], 'ORG': [x for x in [a.get('issuer')] if x]},
                             physical_box=a['state'], file_path=srcdoc or a.get('source_url'), base_access=base_access,
                             links={'facility_ids': fids, 'site_codes': codes, 'source_manifest_ids': [m['source_id']] if m else []},
                             source_refs=[{'manifest_id': m['source_id'], 'local_path': m['local_path'], 'access': m['access']}] if m else [],
                             extra={'verification_level': a.get('verification_level'), 'recipient_class': a.get('recipient_class'),
                                    'amount_basis': a.get('amount_basis'), 'amount_usd': amt, 'state': a['state'],
                                    'source_document_path': srcdoc, 'source_url': a.get('source_url')}))
    return docs, by_site


# ----------------------------------------------------------------------------- facilities
MASTER_GROUPS = [
    ('Identity and location', ['facility_id', 'site_code', 'facility_type', 'type_basis', 'street_address', 'city', 'state', 'zip', 'county', 'lat', 'lon',
                               'location_source', 'geo_method', 'geo_note', 'geo_state_check', 'geo_state_check_detail', 'status', 'sq_ft', 'sq_ft_source', 'confidence']),
    ('Year basis', ['year_used', 'year_basis', 'year_source', 'year_flag', 'year_basis_legacy', 'opening_year', 'opening_year_basis',
                    'opening_year_source_url', 'closing_year', 'mwpvl_year', 'mwpvl_year_resolution', 'mwpvl_year_is_projection', 'press_opening_year',
                    'press_source_url', 'event_opening_year', 'first_osha_filing_year', 'last_osha_filing_year', 'mwpvl_sq_ft', 'mwpvl_sq_ft_snapshot',
                    'mwpvl_status']),
    ('OSHA match and latest filing', ['osha_match_status', 'osha_matched_years', 'osha_matched_year_count', 'osha_latest_year', 'osha_latest_employees',
                                      'osha_latest_hours', 'osha_latest_total_cases', 'osha_latest_trc_rate', 'osha_pooled_trc_rate', 'osha_pooled_hours',
                                      'osha_total_cases_all_years']),
    ('Pullback status', ['pullback_status', 'pullback_date', 'pullback_history']),
    ('Population within distance (2020)', ['pop_within_20mi_2020', 'pop_within_50mi_2020']),
]


def mw_rows_from_history(sa):
    out = {}
    for part in (sa.get('status_history') or '').split(' > '):
        if ':' in part:
            d, s = part.split(':', 1)
            out.setdefault(d, {})['status'] = s
    for part in (sa.get('type_history') or '').split(' > '):
        if ':' in part:
            d, s = part.split(':', 1)
            out.setdefault(d, {})['mwpvl_type'] = s
    return out


def build_facilities(sub_by_site, sub_docs):
    master = rd('facilities_master.csv')
    site_to_fids = collections.defaultdict(list)
    for r in master:
        if r['site_code']:
            site_to_fids[r['site_code']].append(r['facility_id'])
    known = set(site_to_fids)
    osha = collections.defaultdict(list)
    for r in rd('facility_osha_by_year.csv'):
        osha[r['facility_id']].append(r)
    facts = collections.defaultdict(list)
    for r in rd('mwpvl_wayback_facts.csv'):
        facts[r['site_code']].append(r)
    sites_all = {r['site_code']: r for r in rd('mwpvl_wayback_sites_all.csv')}
    events = rd('facility_events_all.csv')
    ek = {(e['city'], e['state'], e['article_date'], e['publication']) for e in events}
    tp_extra = [t for t in rd('trade_press_openings_located.csv') if (t['city'], t['state'], t['article_date'], t['publication']) not in ek]
    pull = rd('pullback_sites.csv')
    sub_by_key = {d['entity_key']: d for d in sub_docs}

    ev_by_site, ev_unlinked = collections.defaultdict(list), []

    def ev_row(e, origin):
        a = access_of_text(e.get('sources'), e.get('url_kind'), e.get('evidence_basis'))
        return {'table': 'event', 'origin': origin, **clean({k: e.get(k) for k in (
            'press_row_id', 'site_code', 'match_site_code', 'facility_type', 'city', 'state', 'sq_ft', 'announced_date', 'opening_date', 'publication', 'article_date', 'article_url',
            'confidence', 'evidence_basis', 'match_quality', 'note', 'quote', 'sources', 'url_kind')}), 'access_class': a}

    for e in events:
        cs = split_codes(e.get('site_code'), known) or (split_codes(e.get('match_site_code'), known) if e.get('match_quality') in ('exact', 'probable') else [])
        r = ev_row(e, 'facility_events_all')
        (ev_by_site[cs[0]].append(r) if cs else ev_unlinked.append(r))
        for c in cs[1:]:
            ev_by_site[c].append(r)
    for t in tp_extra:
        cs = split_codes(t.get('site_code'), known) or split_codes(t.get('match_site_code'), known)
        r = ev_row(t, 'trade_press_openings_located')
        (ev_by_site[cs[0]].append(r) if cs else ev_unlinked.append(r))
        for c in cs[1:]:
            ev_by_site[c].append(r)
    pull_by_site, pull_unlinked = collections.defaultdict(list), []
    for p in pull:
        r = {'table': 'pullback', **clean({k: p.get(k) for k in ('site_code', 'city', 'state', 'type', 'sq_ft', 'status', 'date', 'confidence', 'reason_class', 'match_basis', 'n_sites', 'sources')}),
             'access_class': access_of_text(p.get('sources'))}
        cs = split_codes(p.get('site_code'), known)
        (pull_by_site[cs[0]].append(r) if cs else pull_unlinked.append(r))
    osha_files = [m for m in MAN.rows if 'osha_ita' in m['local_path'] and m['role'] == 'source']

    pf = {n: src_file_entry(p) for n, p in {
        'master': 'data/processed/facilities_master.csv', 'osha': 'data/processed/facility_osha_by_year.csv',
        'facts': 'data/processed/mwpvl_wayback_facts.csv', 'sites_all': 'data/processed/mwpvl_wayback_sites_all.csv',
        'events': 'data/processed/facility_events_all.csv', 'tp': 'data/processed/trade_press_openings_located.csv',
        'pull': 'data/processed/pullback_sites.csv'}.items()}
    docs = []
    for r in master:
        fid, sc = r['facility_id'], r['site_code']
        r = dict(r)
        r['location_source'] = 'roster'
        for fld in ('city', 'state'):
            if r.get(fld):
                continue
            cands = []
            for f_ in sorted(facts.get(sc, []), key=lambda x: x['snapshot_date'], reverse=True) if sc else []:
                cands.append((f_.get(fld), 'mwpvl_snapshot:' + f_['snapshot_date']))
            sa_ = sites_all.get(sc) if sc else None
            if sa_:
                cands.append((sa_.get('latest_' + fld), 'mwpvl_sites_all:latest'))
            for e in (ev_by_site.get(sc, []) if sc else []):
                cands.append((e.get(fld), 'event:' + str(e.get('publication'))))
            for e in (pull_by_site.get(sc, []) if sc else []):
                cands.append((e.get(fld), 'pullback'))
            for v, src in cands:
                if v:
                    r[fld] = v
                    r['location_source'] = src if r['location_source'] == 'roster' else r['location_source'] + '+' + src
                    break
        used = {'location_source'}
        secs = []
        for name, cols in MASTER_GROUPS:
            d = {c: coerce(c, r.get(c, '')) for c in cols}
            used.update(cols)
            secs.append(sec(name, d))
        env = {c: coerce(c, v) for c, v in r.items() if c.startswith('env_')}
        used.update(c for c in r if c.startswith('env_'))
        secs.append(sec('Environmental screening estimates (ESTIMATE, not measured)', env))
        srcd = {c: r.get(c) for c in ('sources', 'source_url', 'source_detail')}
        used.update(srcd)
        secs.append(sec('Roster sources', srcd))
        other = {c: coerce(c, v) for c, v in r.items() if c not in used and c not in ('lat', 'lon')}
        secs.append(sec('Other roster columns', other))
        rows, sf, mids = [], [pf['master']], {}
        # MWPVL
        sa = sites_all.get(sc) if sc else None
        if sa:
            sf.append(pf['sites_all'])
            secs.append(sec('MWPVL history summary (Wayback snapshots)', {k: coerce(k, sa.get(k, '')) for k in (
                'first_snapshot', 'last_snapshot', 'n_snapshots', 'year_opened', 'year_opened_all', 'year_sequence', 'year_conflict', 'year_resolution',
                'year_is_projection', 'latest_sq_ft', 'latest_sq_ft_snapshot', 'latest_status', 'latest_city', 'latest_state', 'latest_mwpvl_type',
                'image_tables', 'absent_from_snapshot', 'source')}))
            for u in (sa.get('first_url'), sa.get('last_url')):
                m = MAN.find(url=u)
                if m:
                    mids[m['source_id']] = ('mwpvl_snapshot_image', m)
        seen = set()
        for f_ in facts.get(sc, []) if sc else []:
            sf.append(pf['facts'])
            seen.add(f_['snapshot_date'])
            rows.append({'table': 'mwpvl_snapshot', 'origin': 'html_era_parse', **clean({k: f_.get(k) for k in (
                'snapshot_date', 'status', 'mwpvl_type', 'sq_ft', 'year_opened', 'raw_year_text', 'status_basis', 'city', 'state', 'wayback_url')}), 'access_class': 'public'})
            m = MAN.find(url=f_.get('wayback_url'))
            if m:
                mids[m['source_id']] = ('mwpvl_snapshot_html', m)
        if sa:
            for d, v in sorted(mw_rows_from_history(sa).items()):
                if d not in seen:
                    rows.append({'table': 'mwpvl_snapshot', 'origin': 'image_era_change_log', 'snapshot_date': d, **v,
                                 'access_class': 'public'})
        # OSHA
        for o in sorted(osha.get(fid, []), key=lambda x: x['year']):
            rows.append({'table': 'osha_year', **clean(o, drop=('facility_id',)), 'access_class': 'public'})
        if osha.get(fid):
            sf.append(pf['osha'])
            for m in osha_files:
                mids[m['source_id']] = ('osha_ita_file', m)
        # events
        evs = ev_by_site.get(sc, []) if sc else []
        if evs:
            sf.append(pf['events'])
            if any(e['origin'] == 'trade_press_openings_located' for e in evs):
                sf.append(pf['tp'])
        for e in evs:
            rows.append(dict(e))
            m = MAN.find(url=e.get('article_url'))
            if m:
                mids[m['source_id']] = ('event_article', m)
        # pullback
        pbs = pull_by_site.get(sc, []) if sc else []
        if pbs:
            sf.append(pf['pull'])
        rows += pbs
        # subsidies
        sids = sorted(set(sub_by_site.get(sc, []))) if sc else []
        for s in sids:
            sd = sub_by_key[s]
            ex = sd
            rows.append({'table': 'subsidy', 'award_id': s, **clean({'program': next((f_['value'] for sc_ in sd['sections'] for f_ in sc_['fields'] if f_['field_name'] == 'program'), None),
                                                                  'award_year': sd['year'], 'amount_usd': sd['amount_usd'], 'amount_basis': sd['amount_basis'],
                                                                  'verification_level': sd['verification_level'], 'recipient_class': sd['recipient_class'],
                                                                  'source_document_path': sd['source_document_path']}), 'access_class': sd['access_class']})
            for mid in sd['links']['source_manifest_ids']:
                mids[mid] = ('subsidy_source_document', MAN.by_id[mid])
        m = MAN.find(url=r.get('source_url'))
        if m:
            mids[m['source_id']] = ('roster_source', m)
        m = MAN.find(url=r.get('press_source_url'))
        if m:
            mids[m['source_id']] = ('press_source', m)
        refs = []
        for mid, (why, m) in sorted(mids.items()):
            refs.append({'manifest_id': mid, 'local_path': m['local_path'], 'access': m['access'], 'why': why})
            sf.append(manifest_entry(m))
        # dedupe source files
        sfd = {}
        for s_ in sf:
            sfd[(s_['path'], s_.get('manifest_id'))] = s_
        sf = list(sfd.values())
        pst = r.get('pullback_status') or 'none recorded'
        locs = ', '.join(x for x in (r['city'], r['state']) if x) or ('address only: ' + (r.get('street_address') or 'unknown'))
        summ = (f"{r['facility_type'].replace('_', ' ')} {sc or '(no site code)'} ({fid}), {locs}. "
                f"Year used {r.get('year_used') or 'unknown'} (basis: {r.get('year_basis') or 'none'}). "
                f"{len(osha.get(fid, []))} OSHA year(s), {sum(1 for x in rows if x['table'] == 'mwpvl_snapshot')} MWPVL snapshot row(s), "
                f"{len(evs)} event(s), pullback status: {pst}.")
        yr = coerce('year_used', r.get('year_used') or '')
        docs.append(make_doc(
            'facilities', fid, title=f"Facility {sc or fid}: {r['facility_type'].replace('_', ' ')}, {locs}", summary=summ,
            sections=secs, rows=rows, source_files=sf, document_type='facility', year=yr if isinstance(yr, int) else None,
            entities={'PERSON': [], 'GPE': [x for x in (r['city'], r['state'], r.get('county')) if x], 'DATE': [str(yr)] if yr else [], 'ORG': ['Amazon']},
            physical_box=r['facility_type'], links={'subsidy_ids': sids, 'site_code': sc, 'source_manifest_ids': sorted(mids)},
            source_refs=refs,
            extra={'site_code': sc or None, 'facility_id': fid, 'facility_type': r['facility_type'], 'state': r['state'], 'city': r['city'],
                   'year_used': yr, 'year_basis': r.get('year_basis') or None, 'pullback_status': r.get('pullback_status') or None,
                   'site_code_shared': bool(sc and len(site_to_fids[sc]) > 1)}))
    return docs, site_to_fids, ev_unlinked, pull_unlinked, tp_extra


# ----------------------------------------------------------------------------- deals
def norm_target(s):
    s = re.sub(r'\(.*?\)', '', (s or '').lower())
    s = re.sub(r'\b(inc|llc|corp|corporation|ltd|co|the|holdings|systems)\b', '', s)
    return re.sub(r'[^a-z0-9]', '', s)


def build_deals():
    pb = rd('jhu_pitchbook_deals.csv')
    pub = rd('logistics_deals_public.csv')
    f_pb, f_pub = src_file_entry('data/processed/jhu_pitchbook_deals.csv'), src_file_entry('data/processed/logistics_deals_public.csv')
    links_pb, links_pub = collections.defaultdict(list), collections.defaultdict(list)
    for i, p in enumerate(pb):
        for j, q in enumerate(pub):
            a, b = norm_target(p['target']), norm_target(q['target'])
            if len(a) < 4 or len(b) < 4 or not (a in b or b in a):
                continue
            ya, yb = (p['date'] or '')[:4], str(q['year'])
            if not (ya.isdigit() and yb.isdigit() and abs(int(ya) - int(yb)) <= 1):
                continue
            if re.sub(r'[^a-z]', '', p['acquirer_or_investor'].lower())[:4] != re.sub(r'[^a-z]', '', q['actor'].lower())[:4]:
                continue
            links_pb[i].append(j)
            links_pub[j].append(i)
    docs, used = [], collections.Counter()

    def pbkey(p):
        return 'PB-' + (p.get('pitchbook_id') or slug(p['target'])) + '-' + slug(p['acquirer_or_investor'], 12)

    pbkeys = [pbkey(p) for p in pb]
    pubkeys = []
    for q in pub:
        k = f"PUB-{q['year']}-{slug(q['actor'], 10)}-{slug(q['target'], 30)}"
        used[k] += 1
        pubkeys.append(k if used[k] == 1 else f'{k}-{used[k]}')
    for i, p in enumerate(pb):
        key = pbkeys[i]
        confirmed = (p.get('public_confirmed') or '').strip().lower() == 'yes'
        status = 'public_confirmed' if confirmed else 'private_pitchbook_only'
        m = MAN.find(url=p.get('public_source_url'))
        sf = [f_pb] + ([manifest_entry(m)] if m else [])
        amt = coerce('amount_usd', p.get('amount_usd') or '')
        summ = (f"{p['acquirer_or_investor']} -> {p['target']}, {p['deal_type']}, {p['date']}; "
                f"{('$%s (%s)' % (format(int(amt), ','), p.get('amount_basis'))) if isinstance(amt, (int, float)) else 'amount not stated'}. "
                f"Status: {status.replace('_', ' ')}.")
        secs = [sec('Deal', clean({k: p.get(k) for k in ('acquirer_or_investor', 'target', 'date', 'deal_type', 'amount_usd', 'amount_basis', 'category', 'logistics_relevance')})),
                sec('Confirmation', {'deal_status': status, 'public_confirmed': p.get('public_confirmed'), 'public_source_url': p.get('public_source_url'),
                                     'public_source_type': p.get('public_source_type')}),
                sec('PitchBook identifiers and citation', {'pitchbook_id': p.get('pitchbook_id'), 'target_pbid': p.get('target_pbid'), 'citation': p.get('citation')})]
        rows = []
        if confirmed and p.get('public_source_url'):
            rows.append({'table': 'public_confirmation', 'public_source_url': p['public_source_url'], 'public_source_type': p.get('public_source_type'), 'access_class': 'public'})
        docs.append(make_doc('deals', key, title=f"Deal (PitchBook): {p['acquirer_or_investor']} / {p['target']} ({(p['date'] or '')[:4]})", summary=summ, sections=secs, rows=rows,
                             source_files=sf, document_type='deal', year=coerce('y', (p['date'] or '')[:4]) if (p['date'] or '')[:4].isdigit() else None,
                             entities={'PERSON': [], 'GPE': [], 'DATE': [p['date']] if p['date'] else [], 'ORG': [p['acquirer_or_investor'], p['target']]},
                             physical_box=p.get('category') or 'deal', base_access='pitchbook',
                             links={'public_deal_ids': [pubkeys[j] for j in links_pb.get(i, [])], 'source_manifest_ids': [m['source_id']] if m else []},
                             extra={'deal_status': status, 'public_confirmed': confirmed, 'source_class': 'pitchbook', 'actor': p['acquirer_or_investor'],
                                    'target': p['target'], 'amount_usd': amt, 'amount_basis': p.get('amount_basis') or None, 'category': p.get('category')}))
    for j, q in enumerate(pub):
        key = pubkeys[j]
        m = MAN.find(url=q.get('source_url'))
        sf = [f_pub] + ([manifest_entry(m)] if m else [])
        amt = coerce('amount_usd', q.get('amount_usd') or '')
        summ = (f"{q['actor']} -> {q['target']}, {q['deal_type']}, {q['year']}; "
                f"{('$%s' % format(int(amt), ',')) if isinstance(amt, (int, float)) else 'amount not stated'} ({q.get('amount_note') or 'no note'}). "
                f"Public source ({q.get('source_type')}): {q.get('source_publisher')}.")
        secs = [sec('Deal', clean({k: q.get(k) for k in ('year', 'actor', 'peer_group', 'target', 'category', 'deal_type', 'amount_usd', 'amount_note')})),
                sec('Confirmation', {'deal_status': 'public_confirmed', 'source_url': q.get('source_url'), 'source_publisher': q.get('source_publisher'),
                                     'source_type': q.get('source_type'), 'citation': q.get('citation')})]
        docs.append(make_doc('deals', key, title=f"Deal (public): {q['actor']} / {q['target']} ({q['year']})", summary=summ, sections=secs, rows=[],
                             source_files=sf, document_type='deal', year=coerce('year', q['year']),
                             entities={'PERSON': [], 'GPE': [], 'DATE': [str(q['year'])], 'ORG': [q['actor'], q['target']]},
                             physical_box=q.get('category') or 'deal', base_access='public',
                             links={'pitchbook_deal_ids': [pbkeys[i] for i in links_pub.get(j, [])], 'source_manifest_ids': [m['source_id']] if m else []},
                             extra={'deal_status': 'public_confirmed', 'public_confirmed': True, 'source_class': 'public', 'actor': q['actor'], 'target': q['target'],
                                    'amount_usd': amt, 'category': q.get('category'), 'peer_group': q.get('peer_group'), 'source_url': q.get('source_url')}))
    return docs


# ----------------------------------------------------------------------------- companies
COMPANIES = collections.OrderedDict([
    ('amazon', dict(name='Amazon.com Inc.', kind='company', cik='1018724')),
    ('walmart', dict(name='Walmart Inc.', kind='company', cik='104169')),
    ('target', dict(name='Target Corp', kind='company')),
    ('costco', dict(name='Costco Wholesale', kind='company', cik='909832')),
    ('homedepot', dict(name='The Home Depot', kind='company')),
    ('ups', dict(name='United Parcel Service', kind='company')),
    ('fedex', dict(name='FedEx Corp', kind='company')),
    ('ryder', dict(name='Ryder System (Supply Chain Solutions)', kind='company_injury_peer_only')),
    ('gxo', dict(name='GXO Logistics', kind='company_injury_peer_only')),
    ('kroger', dict(name='Kroger', kind='company_injury_peer_only')),
    ('lowes', dict(name="Lowe's", kind='company_injury_peer_only')),
    ('dhl', dict(name='DHL (Express eCommerce and Supply Chain, OSHA filers)', kind='company_injury_peer_only')),
    ('group_3pl', dict(name='Peer group: third-party logistics', kind='peer_group')),
    ('group_parcel_carriers', dict(name='Peer group: parcel carriers', kind='peer_group')),
    ('group_retailer_dcs', dict(name='Peer group: retailer distribution centers', kind='peer_group')),
    ('ita_493_ex_amazon', dict(name='OSHA ITA NAICS 493 excluding Amazon', kind='industry_aggregate')),
    ('ita_493110_ex_amazon', dict(name='OSHA ITA NAICS 493110 excluding Amazon', kind='industry_aggregate')),
    ('ita_493110_ex_amazon_ex_peers', dict(name='OSHA ITA NAICS 493110 excluding Amazon and named peers', kind='industry_aggregate')),
])
NAME2SLUG = {'amazon.com inc.': 'amazon', 'amazon': 'amazon', 'carriers vs amazon': 'amazon', 'walmart inc.': 'walmart', 'walmart': 'walmart', 'target corp': 'target',
             'target': 'target', 'costco wholesale': 'costco', 'costco': 'costco', 'the home depot': 'homedepot', 'home depot': 'homedepot', 'homedepot': 'homedepot',
             'home_depot': 'homedepot', 'united parcel service': 'ups', 'ups': 'ups', 'fedex corp': 'fedex', 'fedex': 'fedex', 'fedex_express': 'fedex',
             'fedex_ground': 'fedex', 'fedex_supply_chain': 'fedex', 'fedex_unassigned_2024plus': 'fedex', 'dhl_express_ecom': 'dhl', 'dhl_supply_chain': 'dhl',
             'all': None, 'comparability': None}


def comp_slug(name):
    n = (name or '').strip().lower()
    if n in NAME2SLUG:
        return NAME2SLUG[n]
    return n if n in COMPANIES else None


BENCH_TABLES = [
    # file, domain, table name, company column
    ('bench_injuries_peer_year.csv', 'injuries', 'injuries_peer_year', 'peer'),
    ('bench_network_headline_comparison.csv', 'network', 'network_headline', 'slug'),
    ('bench_network_facilities.csv', 'network', 'network_facilities', 'slug'),
    ('bench_network_amazon_ref.csv', 'network', 'network_amazon_ref', 'slug'),
    ('bench_network_employees_ecom.csv', 'network', 'network_employees_ecom', 'slug'),
    ('bench_network_financial_xbrl.csv', 'financial', 'financial_xbrl', 'slug'),
    ('bench_labor_employees_by_year.csv', 'labor', 'labor_employees', 'company'),
    ('bench_labor_announced_wages.csv', 'labor', 'labor_announced_wages', 'company'),
    ('bench_labor_announced_vs_qcew493.csv', 'labor', 'labor_announced_vs_qcew493', 'company'),
    ('bench_labor_nlrb_counts_by_year.csv', 'labor', 'labor_nlrb_counts', 'company'),
    ('bench_labor_union_representation.csv', 'labor', 'labor_union_representation', 'company'),
    ('bench_environment_emissions.csv', 'environment', 'environment_emissions', 'company'),
    ('bench_environment_intensity.csv', 'environment', 'environment_intensity', 'company'),
    ('bench_environment_renewables_fleet.csv', 'environment', 'environment_renewables_fleet', 'company'),
    ('bench_environment_boundaries.csv', 'environment', 'environment_boundaries', 'company'),
]
ROW_DROP = {'quoted_text', 'local_raw_file', 'accession', 'input_accessions'}


def build_companies(series_ids_for_amazon):
    rows_by = collections.defaultdict(list)
    files_by = collections.defaultdict(dict)
    mids_by = collections.defaultdict(dict)
    for fn, dom, tname, ccol in BENCH_TABLES:
        fe = src_file_entry('data/processed/' + fn)
        for r in rd(fn):
            sl = comp_slug(r[ccol])
            if not sl:
                continue
            row = {'table': tname, 'domain': dom, **clean(r, drop=ROW_DROP | {ccol})}
            if ccol == 'peer':
                row['peer'] = r['peer']
            elif r.get(ccol) and r[ccol].lower() != sl:
                row['company_label'] = r[ccol]
            raw = r.get('local_raw_file') or ''
            m = MAN.find(path=raw or None, url=r.get('source_url') or r.get('announced_source_url'))
            if m:
                row['source_manifest_id'] = m['source_id']
                mids_by[sl][m['source_id']] = m
            row['access_class'] = m['access'] if m else 'public'
            rows_by[sl].append(row)
            files_by[sl][fn] = fe
    # 10-K filings index -> manifest ids per company
    fe = src_file_entry('data/processed/bench_network_filings_index.csv')
    for r in rd('bench_network_filings_index.csv'):
        sl = comp_slug(r['slug'])
        m = MAN.find(path=r.get('local_raw_file') or None, url=r.get('source_url'))
        if sl and m:
            mids_by[sl][m['source_id']] = m
            files_by[sl]['bench_network_filings_index.csv'] = fe
            rows_by[sl].append({'table': 'filings_index', 'domain': 'financial', **clean(r, drop={'local_raw_file'}), 'source_manifest_id': m['source_id'], 'access_class': m['access']})
    defs = collections.defaultdict(list)
    fe = src_file_entry('data/processed/bench_network_definitions.csv')
    for r in rd('bench_network_definitions.csv'):
        sl = comp_slug(r['company_slug'])
        if sl:
            defs[sl].append(r)
            files_by[sl]['bench_network_definitions.csv'] = fe
    docs = []
    for sl, c in COMPANIES.items():
        rows = rows_by.get(sl, [])
        doms = collections.Counter(r['domain'] for r in rows)
        secs = [sec('Identity', {'slug': sl, 'name': c['name'], 'kind': c['kind'], 'cik': c.get('cik'),
                                 'injury_peer_keys': sorted({r['peer'] for r in rows if r.get('peer')}) or None})]
        if defs.get(sl):
            secs.append(sec('Definitions and comparability', {f"{d['topic']}": d['definition_or_difference'] + (' [' + d['how_files_handle_it'] + ']' if d.get('how_files_handle_it') else '') for d in defs[sl]}))
        secs.append(sec('Benchmark series counts', {f'rows_{k}': v for k, v in sorted(doms.items())}))
        sf = list(files_by[sl].values())
        for mid, m in sorted(mids_by[sl].items()):
            sf.append(manifest_entry(m))
        links = {'source_manifest_ids': sorted(mids_by[sl])}
        if sl == 'amazon':
            links['series_ids'] = series_ids_for_amazon
        summ = (f"{c['name']} ({c['kind'].replace('_', ' ')}). Benchmark rows: " + (', '.join(f'{k} {v}' for k, v in sorted(doms.items())) or 'none') + '.')
        docs.append(make_doc('companies', sl, title=f"Company: {c['name']}", summary=summ, sections=secs, rows=rows, source_files=sf, document_type=c['kind'],
                             entities={'PERSON': [], 'GPE': [], 'DATE': [], 'ORG': [c['name']]}, physical_box=c['kind'], links=links,
                             source_refs=[{'manifest_id': mid, 'local_path': m['local_path'], 'access': m['access']} for mid, m in sorted(mids_by[sl].items())],
                             extra={'slug': sl, 'name': c['name'], 'kind': c['kind']}))
    return docs


# ----------------------------------------------------------------------------- series
# (file, group columns, id prefix, title, domain, time column, note)
SERIES = [
    ('bls_soii_rates.csv', ['naics', 'case_type'], 'bls_soii', 'BLS SOII injury and illness rate per 100 FTE', 'injuries', 'year', 'BLS SOII via the BLS public API'),
    ('bench_warehousing_industry_qcew_national_annual.csv', ['naics', 'ownership'], 'qcew_national', 'BLS QCEW national annual averages', 'labor', 'year', ''),
    ('bls_qcew_naics49x_national_state_annual.csv', ['naics', 'ownership_code'], 'qcew_state', 'BLS QCEW NAICS 49x national and state annual averages (rows are area-year)', 'labor', 'year', ''),
    ('bench_warehousing_industry_qcew_size_class_q1.csv', ['naics'], 'qcew_sizeclass_q1', 'BLS QCEW first-quarter establishment size classes', 'industry', 'year', ''),
    ('bench_warehousing_industry_cbp_size_class.csv', ['naics'], 'cbp_sizeclass', 'Census County Business Patterns establishment size classes', 'industry', 'year', ''),
    ('bench_warehousing_industry_economic_census.csv', ['census_year', 'table'], 'economic_census', 'Economic Census warehousing and storage tables', 'industry', 'census_year', ''),
    ('bench_warehousing_industry_oews_wages.csv', ['naics'], 'oews_wages', 'BLS OEWS occupational wages by industry', 'labor', 'year', ''),
    ('bench_warehousing_industry_oews_premium.csv', [], 'oews_premium', 'OEWS warehousing wage premium over all industries', 'labor', 'year', ''),
    ('bench_warehousing_industry_amazon_share_493.csv', [], 'amazon_share_493', 'Amazon share of NAICS 493 (QCEW, CBP, OSHA ITA)', 'industry', 'year', ''),
    ('bench_warehousing_industry_amazon_vs_qcew_size.csv', [], 'amazon_vs_qcew_size', 'Amazon OSHA sites against QCEW size classes', 'industry', 'year', ''),
    ('bench_labor_qcew493_wage_series.csv', [], 'qcew493_wages', 'QCEW NAICS 493 average weekly wage series', 'labor', 'year', ''),
    ('bench_injuries_493110_distribution.csv', ['population'], 'osha_493110_distribution', 'Distribution of site injury rates, OSHA ITA NAICS 493110', 'injuries', 'year', ''),
    ('osha_ita_aggregates_by_year.csv', ['who', 'naics_segment'], 'osha_ita_aggregates', 'OSHA ITA aggregates by year', 'injuries', 'year', ''),
    ('osha_ita_amazon_by_state_year.csv', [], 'osha_ita_amazon_state', 'OSHA ITA Amazon establishments by state and year', 'injuries', 'year', ''),
    ('injury_comparison_by_year.csv', [], 'injury_comparison', 'Amazon vs BLS vs other ITA injury rates by year', 'injuries', 'year', ''),
    ('amazon_income_statement_annual.csv', [], 'amazon_10k_income', 'Amazon 10-K annual income statement figures', 'financial', 'fiscal_year', ''),
    ('amazon_capex_annual.csv', [], 'amazon_10k_capex', 'Amazon 10-K annual capital expenditure', 'financial', 'fiscal_year', ''),
    ('amazon_ppe_year_end.csv', [], 'amazon_10k_ppe', 'Amazon 10-K year-end property and equipment', 'financial', 'fiscal_year', ''),
    ('amazon_shipping_costs_annual.csv', [], 'amazon_10k_shipping', 'Amazon 10-K annual shipping costs', 'financial', 'fiscal_year', ''),
    ('amazon_employees_by_year.csv', [], 'amazon_10k_employees', 'Amazon 10-K employees by year', 'labor', 'fiscal_year_end_dec31', ''),
    ('amazon_10k_square_footage.csv', [], 'amazon_10k_sqft', 'Amazon 10-K square footage by space type and region', 'facilities', 'fiscal_year', ''),
    ('amazon_10k_square_footage_by_segment.csv', [], 'amazon_10k_sqft_segment', 'Amazon 10-K segment square footage', 'facilities', 'fiscal_year', ''),
    ('amazon_sustainability_other_metrics.csv', [], 'amazon_sustainability_other', 'Amazon sustainability report: other metrics', 'environment', 'year', ''),
    ('amazon_carbon_footprint_by_report_vintage.csv', [], 'amazon_carbon', 'Amazon carbon footprint by sustainability-report vintage', 'environment', 'year', ''),
    ('amazon_turnover_published_estimates.csv', [], 'amazon_turnover', 'Published estimates of Amazon warehouse turnover', 'labor', '', ''),
    ('amazon_wage_announcements.csv', [], 'amazon_wage_announcements', 'Amazon wage announcements', 'labor', 'announce_date', ''),
    ('amazon_site_counties_naics493_summary.csv', [], 'site_counties_493', 'Amazon site counties: NAICS 493 QCEW coverage summary', 'labor', 'year', ''),
    ('logistics_timeline.csv', [], 'logistics_timeline', 'Amazon logistics timeline', 'logistics', 'date', ''),
    ('logistics_sqft_by_year.csv', [], 'logistics_sqft', 'Amazon square footage by year', 'logistics', 'fiscal_year_end_dec31', ''),
    ('logistics_us_fc_counts_2000_2003.csv', [], 'logistics_fc_counts_early', 'US fulfillment-center counts 2000-2003', 'logistics', 'fiscal_year', ''),
    ('logistics_facility_count_snapshots.csv', [], 'logistics_snapshots', 'Facility-count snapshots (MWPVL, press)', 'logistics', 'as_of', ''),
    ('logistics_osha_site_counts_by_year.csv', ['group'], 'logistics_osha_site_counts', 'Distinct OSHA-filing site codes by year', 'logistics', 'year', ''),
    ('logistics_air_fleet.csv', [], 'logistics_air_fleet', 'Amazon Air fleet counts', 'logistics', 'as_of', ''),
    ('logistics_air_hubs.csv', [], 'logistics_air_hubs', 'Amazon Air hubs', 'logistics', 'date', ''),
    ('logistics_dsp.csv', [], 'logistics_dsp', 'Delivery service partner program metrics', 'logistics', 'date', ''),
    ('logistics_us_parcel_volume.csv', ['carrier'], 'parcel_volume', 'US parcel volume by carrier (Pitney Bowes Parcel Shipping Index)', 'logistics', 'year', ''),
    ('industry_pitney_bowes_parcel_index.csv', ['carrier'], 'pitney_bowes_index', 'Pitney Bowes Parcel Shipping Index tables', 'logistics', 'data_year', ''),
    ('industry_epi_fc_openings_2017.csv', [], 'epi_fc_openings', 'EPI fulfillment-center openings by state and county (2017)', 'facilities', 'open_year', ''),
    ('industry_epi_fc_cumulative_counts.csv', [], 'epi_fc_cumulative', 'EPI cumulative FC openings', 'facilities', 'as_of_year_end', ''),
    ('industry_amazon_leased_sqft.csv', [], 'industry_leased_sqft', 'Amazon leased square footage (industry sources)', 'industry', '', ''),
    ('industry_amazon_robot_counts.csv', [], 'amazon_robot_counts', 'Amazon robot counts', 'logistics', 'as_of', ''),
    ('market_context.csv', ['topic'], 'market_context', 'Parcel, e-commerce and warehouse-market context', 'industry', 'year', ''),
    ('population_access_by_year.csv', ['set'], 'population_access_year', 'Population within 20 and 50 miles of an Amazon site, by site-opening year', 'facilities', '', ''),
    ('population_access_by_state.csv', ['set'], 'population_access_state', 'Population within 20 and 50 miles of an Amazon site, by state', 'facilities', '', ''),
    ('egrid_us_average_output_rate_by_year.csv', [], 'egrid_us', 'eGRID US average output emission rate', 'environment', 'egrid_data_year', ''),
    ('egrid_state_rates_2018_2023.csv', [], 'egrid_state', 'eGRID state emission rates 2018-2023', 'environment', 'year', ''),
    ('egrid_subregion_rates_2018_2023.csv', [], 'egrid_subregion', 'eGRID subregion emission rates 2018-2023', 'environment', 'year', ''),
    ('cbecs2018_warehouse_intensity.csv', [], 'cbecs_warehouse', 'CBECS 2018 warehouse energy intensity', 'environment', '', ''),
    ('cbecs2018_all_building_intensity_by_region_size.csv', [], 'cbecs_all_buildings', 'CBECS 2018 all-building intensity by region and size', 'environment', '', ''),
    ('pullback_aggregates.csv', [], 'pullback_aggregates', 'Aggregate pullback counts (closed, cancelled, delayed)', 'facilities', 'date', ''),
    ('nlrb_amazon_election_tallies.csv', [], 'nlrb_elections', 'NLRB representation election tallies, Amazon', 'labor', 'tally_date', ''),
    ('mwpvl_wayback_snapshots.csv', [], 'mwpvl_snapshots', 'MWPVL Wayback snapshots parsed', 'facilities', 'snapshot_date', ''),
]
MAX_SERIES_ROWS = 6000


def build_series(ev_unlinked, pull_unlinked):
    docs, ids = [], []
    for fn, gcols, prefix, title, dom, tcol, note in SERIES:
        rows_ = rd(fn)
        fe = src_file_entry('data/processed/' + fn)
        groups = collections.OrderedDict()
        for r in rows_:
            groups.setdefault(tuple(r.get(c, '') for c in gcols), []).append(r)
        for gk, rs in groups.items():
            key = prefix + ('__' + '_'.join(slug(x, 24) for x in gk) if gcols else '')
            gdesc = ', '.join(f'{c}={v}' for c, v in zip(gcols, gk))
            trunc = None
            cut = rs
            if len(rs) > MAX_SERIES_ROWS:
                cut = rs[:MAX_SERIES_ROWS]
                trunc = {'original_chars': len(rs), 'kept_chars': MAX_SERIES_ROWS, 'chars_removed': len(rs) - MAX_SERIES_ROWS, 'unit': 'rows', 'reason': 'row cap'}
            rows = []
            m_ids = {}
            for r in cut:
                row = {'table': prefix, **clean(r, drop=set(gcols) | {'local_raw_file'})}
                row['access_class'] = access_of_text(*(r.get(c) for c in ('citation', 'sources', 'source', 'publisher', 'source_type', 'note', 'basis')))
                m = MAN.find(path=r.get('local_raw_file') or None, url=r.get('source_url') or r.get('url'))
                if m:
                    row['source_manifest_id'] = m['source_id']
                    m_ids[m['source_id']] = m
                rows.append(row)
            times = [coerce(tcol, r.get(tcol, '')) for r in rs if tcol and r.get(tcol)]
            tmin = min(times, key=str) if times else None
            tmax = max(times, key=str) if times else None
            secs = [sec('Series', {'series_id': key, 'title': title, 'group': gdesc or None, 'domain': dom, 'time_column': tcol or None,
                                   'first': tmin, 'last': tmax, 'n_rows': len(rs), 'columns': list(rs[0].keys()), 'note': note or None, 'source_table': 'data/processed/' + fn})]
            sf = [fe] + [manifest_entry(m) for m in m_ids.values()]
            summ = f"{title}{' (' + gdesc + ')' if gdesc else ''}: {len(rs)} rows" + (f', {tmin} to {tmax}.' if tmin is not None else '.')
            yr = tmin if isinstance(tmin, int) else None
            docs.append(make_doc('series', key, title=f"Series: {title}{' [' + gdesc + ']' if gdesc else ''}", summary=summ, sections=secs, rows=rows, source_files=sf,
                                 document_type='time_series', year=yr, physical_box=dom, truncated=trunc,
                                 links={'source_manifest_ids': sorted(m_ids)}, source_refs=[{'manifest_id': k, 'local_path': m['local_path'], 'access': m['access']} for k, m in m_ids.items()],
                                 extra={'series_id': key, 'domain': dom, 'n_rows': len(rs)}))
            ids.append(key)
    # unlinked events / pullback rows: kept so nothing is lost
    for key, title, rs, fns in (('events_unlinked', 'Facility events not linked to a site code', ev_unlinked, ['facility_events_all.csv', 'trade_press_openings_located.csv']),
                                ('pullback_unlinked', 'Pullback rows not linked to a site code', pull_unlinked, ['pullback_sites.csv'])):
        sf = [src_file_entry('data/processed/' + f) for f in fns]
        docs.append(make_doc('series', key, title=f'Series: {title}', summary=f'{title}: {len(rs)} rows (city-level or unmatched; no site code).',
                             sections=[sec('Series', {'series_id': key, 'title': title, 'n_rows': len(rs), 'domain': 'facilities'})], rows=rs, source_files=sf,
                             document_type='time_series', physical_box='facilities', extra={'series_id': key, 'domain': 'facilities', 'n_rows': len(rs)}))
        ids.append(key)
    return docs, ids


# ----------------------------------------------------------------------------- sources
class _Strip(html.parser.HTMLParser):
    SKIP = {'script', 'style', 'noscript', 'svg', 'head'}
    BLOCK = {'p', 'div', 'br', 'li', 'tr', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'table', 'section', 'article', 'ul', 'ol', 'blockquote', 'pre'}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self.skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self.skip += 1
        elif tag in self.BLOCK:
            self.out.append('\n')

    def handle_endtag(self, tag):
        if tag in self.SKIP:
            self.skip = max(0, self.skip - 1)
        elif tag in self.BLOCK:
            self.out.append('\n')
        elif tag in ('td', 'th'):
            self.out.append(' | ')

    def handle_data(self, d):
        if not self.skip:
            self.out.append(d)


def html_to_text(raw):
    p = _Strip()
    try:
        p.feed(raw)
        p.close()
    except Exception:
        pass
    t = ''.join(p.out).replace('\xa0', ' ')
    t = re.sub(r'[ \t]+', ' ', t)
    return re.sub(r'\n\s*\n+', '\n', t).strip()


def extract_text(path, ext):
    """Return (text, method) or (None, reason)."""
    try:
        if ext in ('.txt', '.md', '.dat'):
            with open(path, 'rb') as f:
                raw = f.read(TEXT_CAP * 4 + 1)
            return raw.decode('utf-8', 'replace'), 'read_text'
        if ext in ('.html', '.htm', '.xml'):
            with open(path, 'rb') as f:
                raw = f.read(HTML_READ_CAP)
            return html_to_text(raw.decode('utf-8', 'replace')), 'html_to_text'
        if ext == '.pdf':
            r = subprocess.run(['pdftotext', '-layout', '-l', str(PDF_MAX_PAGES), str(path), '-'], capture_output=True, timeout=120)
            return r.stdout.decode('utf-8', 'replace'), f'pdftotext(first {PDF_MAX_PAGES} pages)'
    except subprocess.TimeoutExpired:
        return None, 'pdftotext_timeout'
    except Exception as e:  # noqa: BLE001
        return None, f'extract_error:{type(e).__name__}'
    return None, 'not_text_bearing'


TEXT_EXT = {'.txt', '.md', '.dat', '.html', '.htm', '.xml', '.pdf'}
NO_TEXT_ROLES = {'probe', 'challenge_page'}


def build_sources(do_text=True, verify=False):
    rows = MAN.rows
    results = {}

    def work(m):
        p = ROOT / m['local_path']
        ext = p.suffix.lower()
        flags = m.get('flags') or ''
        if not do_text:
            return m['source_id'], (None, 'text_extraction_disabled')
        if ext not in TEXT_EXT:
            return m['source_id'], (None, 'not_text_bearing')
        if m['role'] in NO_TEXT_ROLES or 'empty_file' in flags or 'challenge_page_not_article' in flags:
            return m['source_id'], (None, 'skipped_' + (m['role'] if m['role'] in NO_TEXT_ROLES else 'empty_or_challenge'))
        if not p.exists():
            return m['source_id'], (None, 'missing_on_disk')
        return m['source_id'], extract_text(p, ext)

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        for sid, res in ex.map(work, rows):
            results[sid] = res
    fe = src_file_entry('data/sources_manifest.csv', kind='manifest')
    docs = []
    for m in rows:
        text, method = results[m['source_id']]
        trunc, ocr_text = None, None
        if text is not None:
            text = text.replace('\x00', '')
            n = len(text)
            if n > TEXT_CAP:
                trunc = {'original_chars': n, 'kept_chars': TEXT_CAP, 'chars_removed': n - TEXT_CAP, 'reason': f'cap {TEXT_CAP} characters ({method})'}
                text = text[:TEXT_CAP]
            ocr_text = text
        else:
            ocr_text = ''
        ub = [x for x in re.split(r'\s*[;|]\s*', m['used_by'] or '') if x]
        meta = {k: coerce(k, m[k]) for k in ('title', 'publisher', 'publication_date', 'url_or_doc_id', 'access', 'domain', 'local_path', 'size_bytes',
                                              'sha256', 'retrieved_date', 'role', 'flags')}
        secs = [sec('Manifest entry', {'source_id': m['source_id'], **meta}),
                sec('Use in this project', {'used_by': ub or None, 'n_used_by_listed': len(ub), 'note': 'manifest lists the first 12 users only' if len(ub) >= 12 else None}),
                sec('Text extraction', {'status': 'extracted' if text is not None else 'none', 'method_or_reason': method, 'chars_kept': len(ocr_text) if text is not None else 0,
                                        'truncated': bool(trunc)})]
        if verify and (ROOT / m['local_path']).exists() and sha256_file(ROOT / m['local_path']) != m['sha256']:
            secs.append(sec('Hash check', {'result': 'MISMATCH with manifest sha256'}))
        summ = f"{m['title'] or Path(m['local_path']).name} ({m['publisher'] or 'publisher not recorded'}, {m['publication_date'] or 'undated'}); {m['access']}; role {m['role']}; " + \
               (f"{len(ocr_text):,} characters of text{' (capped)' if trunc else ''}." if text is not None else f'no text ({method}).')
        entry = {'path': m['local_path'], 'sha256': m['sha256'], 'manifest_id': m['source_id'], 'kind': 'source_file', 'access_class': m['access']}
        docs.append(make_doc('sources', m['source_id'], title=m['title'] or Path(m['local_path']).name, summary=summ, sections=secs, rows=[],
                             source_files=[entry, fe], document_type='source_' + (m['role'] or 'file'), year=None,
                             entities={'PERSON': [], 'GPE': [], 'DATE': [m['publication_date']] if m['publication_date'] else [], 'ORG': [m['publisher']] if m['publisher'] else []},
                             physical_box=m['domain'], file_path=m['local_path'], source_image_path=m['local_path'], base_access=m['access'],
                             links={'used_by': ub}, ocr_text=ocr_text, truncated=trunc,
                             extra={'access_class_manifest': m['access'], 'domain': m['domain'], 'role': m['role'], 'flags': m['flags'] or None,
                                    'text_status': 'extracted' if text is not None else method, 'source_sha256': m['sha256'], 'url_or_doc_id': m['url_or_doc_id'] or None}))
    return docs


# ----------------------------------------------------------------------------- main
def main():
    global MAN
    ap = argparse.ArgumentParser()
    ap.add_argument('--only', default='', help='comma list of collections (default all). facilities builds subsidies first.')
    ap.add_argument('--no-text', action='store_true', help='skip text extraction for sources')
    ap.add_argument('--verify-hashes', action='store_true', help='re-hash every source file and flag mismatches with the manifest (slow, reads ~7 GB)')
    a = ap.parse_args()
    want = set(x for x in a.only.split(',') if x) or {'facilities', 'subsidies', 'deals', 'companies', 'sources', 'series'}
    MAN = Manifest()
    w = Writer()
    t0 = time.time()
    # facilities need site codes; subsidies need the site-code map: build roster map first (cheap)
    master = rd('facilities_master.csv')
    s2f = collections.defaultdict(list)
    for r in master:
        if r['site_code']:
            s2f[r['site_code']].append(r['facility_id'])
    sub_docs, sub_by_site = build_subsidies(s2f)
    if 'subsidies' in want:
        w.write('subsidies', sub_docs)
    fac_docs, _, ev_unl, pb_unl, _ = build_facilities(sub_by_site, sub_docs)
    if 'facilities' in want:
        w.write('facilities', fac_docs)
    if 'deals' in want:
        w.write('deals', build_deals())
    ser_docs, ser_ids = build_series(ev_unl, pb_unl)
    if 'series' in want:
        w.write('series', ser_docs)
    if 'companies' in want:
        amazon_series = [i for i in ser_ids if i.startswith('amazon_') or i in ('injury_comparison', 'logistics_timeline', 'logistics_sqft', 'logistics_air_fleet', 'logistics_air_hubs', 'logistics_dsp')]
        w.write('companies', build_companies(amazon_series))
    if 'sources' in want:
        w.write('sources', build_sources(not a.no_text, a.verify_hashes))
    for c, (n, size, st) in w.stats.items():
        print(f'{c:12s} {n:6d} docs  {size / 1e6:9.1f} MB  {st}')
    print(f'unlinked event rows {len(ev_unl)}, unlinked pullback rows {len(pb_unl)}; {time.time() - t0:.0f}s')


if __name__ == '__main__':
    main()
