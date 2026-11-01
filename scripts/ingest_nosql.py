#!/usr/bin/env python3
"""Validate data/nosql/*.jsonl and (optionally) load it into a NEW MongoDB database.

  python3 -I scripts/ingest_nosql.py --validate-only        # stdlib only, no server needed
  python3 scripts/ingest_nosql.py --uri mongodb://localhost:27017 [--db amazon_logistics] [--with-documents-view]

Safety rules (enforced in code):
  * Never touches `railroad_documents`, `admin`, `local`, `config`; the target db name must start with "amazon".
  * Refuses if the target database already holds any collection that is not one of ours.
  * Only upserts by _id (replace_one upsert). Never drops, deletes or updates other collections.
  * Starts nothing and installs nothing: if the server is not reachable it reports that and exits 2
    (after the validation pass).
Authentication: put credentials in --uri or the AMAZON_MONGO_URI environment variable; nothing is read from the reader's config.
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'data' / 'nosql'
COLLECTIONS = ['facilities', 'subsidies', 'deals', 'companies', 'sources', 'series']
EXTRA_ALLOWED = {'documents', '_build_meta'}   # documents = optional union view for the reader
PROTECTED_DBS = {'railroad_documents', 'admin', 'local', 'config'}
ACCESS = {'public': 0, 'jhu_subscription': 1, 'pitchbook': 2}
REQUIRED = ['_id', 'doc_id', 'entity_type', 'entity_key', 'collection', 'filename', 'relative_path', 'file_path', 'file_hash', 'ocr_text', 'summary',
            'sections', 'rows', 'entities', 'document_type', 'archive_structure', 'provenance', 'access_class', 'access_classes', 'schema_version']
HEX64 = re.compile(r'^[0-9a-f]{64}$')
HEX24 = re.compile(r'^[0-9a-f]{24}$')
MAX_BSON = 16 * 1024 * 1024


def validate(coll, path, limit_errors=20):
    """Schema check of one JSONL file (the schema documented in data/nosql/FORMAT_NOTES.md). Returns (n_docs, errors, stats)."""
    errs, n = [], 0
    ids, hashes, dids = set(), set(), set()
    stats = {'bytes': 0, 'access': {}, 'rows': 0, 'truncated': 0, 'max_doc_bytes': 0}

    def err(msg):
        if len(errs) < limit_errors:
            errs.append(msg)

    with open(path, encoding='utf-8') as f:
        for ln, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            n += 1
            nb = len(line.encode('utf-8'))
            stats['bytes'] += nb
            stats['max_doc_bytes'] = max(stats['max_doc_bytes'], nb)
            try:
                d = json.loads(line)
            except Exception as e:  # noqa: BLE001
                err(f'{coll}:{ln} bad json {e}')
                continue
            tag = f'{coll}:{ln}:{d.get("doc_id")}'
            for k in REQUIRED:
                if k not in d:
                    err(f'{tag} missing {k}')
            if nb > MAX_BSON * 0.9:
                err(f'{tag} document is {nb} bytes, near the 16 MB BSON limit')
            o = d.get('_id')
            if not (isinstance(o, dict) and HEX24.match(str(o.get('$oid', '')))):
                err(f'{tag} _id must be {{"$oid": 24 hex}}')
            else:
                if o['$oid'] in ids:
                    err(f'{tag} duplicate _id')
                ids.add(o['$oid'])
            if d.get('file_hash') in hashes:
                err(f'{tag} duplicate file_hash (unique index would reject)')
            hashes.add(d.get('file_hash'))
            if d.get('doc_id') in dids:
                err(f'{tag} duplicate doc_id')
            dids.add(d.get('doc_id'))
            if d.get('entity_type') != coll or d.get('collection') != f'amazon_{coll}':
                err(f'{tag} entity_type/collection mismatch')
            if not isinstance(d.get('ocr_text'), str):
                err(f'{tag} ocr_text not a string')
            if not isinstance(d.get('summary'), str) or not d.get('summary'):
                err(f'{tag} summary empty')
            for s in d.get('sections') or []:
                if not (isinstance(s, dict) and s.get('section_name') and isinstance(s.get('fields'), list)):
                    err(f'{tag} bad section {str(s)[:80]}')
                    break
                if any(not (isinstance(x, dict) and 'field_name' in x and 'value' in x) for x in s['fields']):
                    err(f'{tag} bad section field in {s.get("section_name")}')
                    break
            rows = d.get('rows')
            if not isinstance(rows, list):
                err(f'{tag} rows not a list')
                rows = []
            stats['rows'] += len(rows)
            rc = {'public'}
            for r in rows:
                if not isinstance(r, dict) or 'table' not in r:
                    err(f'{tag} row without table discriminator')
                    break
                rc.add(r.get('access_class', 'public'))
            ac = d.get('access_class')
            if ac not in ACCESS:
                err(f'{tag} access_class {ac!r} not in {sorted(ACCESS)}')
            else:
                stats['access'][ac] = stats['access'].get(ac, 0) + 1
                if any(c not in ACCESS for c in rc) or max(ACCESS.get(c, 1) for c in rc) > ACCESS[ac]:
                    err(f'{tag} access_class {ac} is less restrictive than a row class {sorted(rc)}')
            p = d.get('provenance') or {}
            if p.get('build_script') != 'scripts/build_nosql.py' or p.get('build_date') != '2026-10-31' or p.get('access_class') != ac:
                err(f'{tag} provenance build_script/build_date/access_class wrong')
            sfs = p.get('source_files') or []
            if not sfs:
                err(f'{tag} provenance.source_files empty')
            for sf in sfs:
                if not (sf.get('path') and HEX64.match(str(sf.get('sha256', '')))):
                    err(f'{tag} source file without path or sha256: {str(sf)[:100]}')
                    break
            if not HEX64.match(str(d.get('file_hash', ''))):
                err(f'{tag} file_hash not sha256')
            if d.get('ocr_text_truncated'):
                stats['truncated'] += 1
                t = d['ocr_text_truncated']
                if not all(k in t for k in ('original_chars', 'kept_chars', 'chars_removed')):
                    err(f'{tag} ocr_text_truncated missing keys')
    return n, errs, stats


def validate_all(only=None):
    ok, report = True, {}
    for c in COLLECTIONS:
        if only and c not in only:
            continue
        p = OUT / f'{c}.jsonl'
        if not p.exists():
            print(f'{c:11s} MISSING {p}')
            ok = False
            continue
        n, errs, st = validate(c, p)
        report[c] = {'docs': n, 'errors': len(errs), **st}
        print(f'{c:11s} {n:6d} docs  {st["bytes"] / 1e6:8.1f} MB  rows {st["rows"]:7d}  truncated {st["truncated"]:4d}  access {st["access"]}  '
              f'max doc {st["max_doc_bytes"] / 1e6:.2f} MB  {"OK" if not errs else "ERRORS"}')
        for e in errs:
            print('   ', e)
        ok = ok and not errs
    return ok, report


def load_docs(path):
    try:
        from bson import json_util
        for line in open(path, encoding='utf-8'):
            if line.strip():
                yield json_util.loads(line)
    except ImportError:
        raise SystemExit('pymongo/bson not installed: pip install pymongo (only needed for ingest, not for --validate-only)')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--uri', default=os.environ.get('AMAZON_MONGO_URI', 'mongodb://localhost:27017'))
    ap.add_argument('--db', default='amazon_logistics')
    ap.add_argument('--validate-only', action='store_true')
    ap.add_argument('--dry-run', action='store_true', help='connect and run the safety checks, write nothing')
    ap.add_argument('--with-documents-view', action='store_true',
                    help="also create a read-only view 'documents' (union of the six collections) so the reader can browse this database")
    ap.add_argument('--only', default='', help='comma list of collections')
    a = ap.parse_args()
    only = set(x for x in a.only.split(',') if x) or None

    ok, vreport = validate_all(only)
    if not ok:
        print('validation FAILED; nothing ingested')
        return 1
    if a.validate_only:
        print('validation OK (no server contacted)')
        return 0

    if a.db in PROTECTED_DBS or not a.db.startswith('amazon'):
        print(f'refusing: database name {a.db!r} is protected or not an amazon* name')
        return 1
    try:
        from pymongo import MongoClient, ReplaceOne, ASCENDING
    except ImportError:
        print('pymongo not installed; validation passed, ingest skipped (pip install pymongo to ingest)')
        return 2
    client = MongoClient(a.uri, serverSelectionTimeoutMS=3000)
    try:
        client.admin.command('ping')
    except Exception as e:  # noqa: BLE001
        print(f'MongoDB not reachable at the given uri ({type(e).__name__}); nothing started or installed. Validation passed.')
        return 2
    db = client[a.db]
    existing = db.list_collection_names()
    foreign = [c for c in existing if c not in COLLECTIONS and c not in EXTRA_ALLOWED]
    if foreign:
        print(f'refusing: database {a.db!r} already holds non-Amazon collections: {foreign}')
        return 1
    if 'documents' in existing and db['documents'].options().get('viewOn') is None:
        print("refusing: 'documents' exists in the target db and is a normal collection (not our view)")
        return 1
    for c in COLLECTIONS:
        if c in existing and db[c].count_documents({'provenance.build_script': {'$ne': 'scripts/build_nosql.py'}}, limit=1):
            print(f'refusing: {a.db}.{c} contains documents not written by build_nosql.py')
            return 1
    if a.dry_run:
        print('dry run: safety checks passed; nothing written')
        return 0

    result = {}
    for c in COLLECTIONS:
        if only and c not in only:
            continue
        col = db[c]
        batch, n = [], 0
        for d in load_docs(OUT / f'{c}.jsonl'):
            batch.append(ReplaceOne({'_id': d['_id']}, d, upsert=True))
            if len(batch) >= 200:
                col.bulk_write(batch, ordered=False)
                n += len(batch)
                batch = []
        if batch:
            col.bulk_write(batch, ordered=False)
            n += len(batch)
        col.create_index([('file_hash', ASCENDING)], unique=True)
        col.create_index([('doc_id', ASCENDING)], unique=True)
        col.create_index([('entity_key', ASCENDING)])
        col.create_index([('access_class', ASCENDING)])
        col.create_index([('collection', ASCENDING), ('archive_structure.physical_box', ASCENDING)])
        col.create_index([('ocr_text', 'text'), ('summary', 'text'), ('title', 'text')], default_language='none', name='text_ocr_summary_title')
        result[c] = {'upserted_or_replaced': n, 'count_in_db': col.count_documents({})}
        print(f'{c:11s} loaded {n:6d}  count in db {result[c]["count_in_db"]}')
    if a.with_documents_view and 'documents' not in db.list_collection_names():
        db.command('create', 'documents', viewOn='facilities', pipeline=[{'$unionWith': {'coll': c}} for c in COLLECTIONS if c != 'facilities'])
        print("created read-only view 'documents'")
    db['_build_meta'].replace_one({'_id': 'amazon_logistics'}, {'_id': 'amazon_logistics', 'build_date': '2026-10-31', 'script': 'scripts/build_nosql.py',
                                                                'ingest_script': 'scripts/ingest_nosql.py'}, upsert=True)

    # verification: counts + 3 sample queries
    print('--- verification')
    for c, r in result.items():
        n_file = vreport[c]['docs']
        print(f'{c}: file {n_file} vs db {r["count_in_db"]}', 'OK' if n_file == r['count_in_db'] else 'MISMATCH')
    q1 = db.facilities.find_one({'site_code': 'ABE1'}, {'doc_id': 1, 'summary': 1, 'access_class': 1})
    print('Q1 facilities site_code=ABE1:', q1)
    q2 = db.subsidies.count_documents({'verification_level': 'primary', 'recipient_class': 'direct'})
    print('Q2 subsidies primary+direct:', q2)
    q3 = db.sources.count_documents({'$text': {'$search': 'fulfillment'}, 'access_class': 'public'})
    print('Q3 sources public text hits for "fulfillment":', q3)
    return 0


if __name__ == '__main__':
    sys.exit(main())
