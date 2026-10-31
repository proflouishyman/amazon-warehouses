#!/usr/bin/env python3
"""Reconcile the double-entry transcriptions of the archived MWPVL facility table images
(2016-03 to 2026-01), merge them with the text-era facts (2012-2016), and match to
facilities_master.csv.

Inputs (data/raw/mwpvl_wayback/transcriptions/, gitignored):
  passes.json        two independent transcriptions (pass_a, pass_b) of each image
  adjudications.json one decision for every row on which the passes disagreed on a content
                     field (site code, sq ft, year, city) or on a type-changing description,
                     or where only one pass had the row; each decision records its basis
                     (viewed_image_crop / vision_ocr_of_cell / merged_description_text)
Outputs (data/processed/):
  mwpvl_wayback_image_facts.csv   one row per site code per image
  mwpvl_wayback_sites_all.csv     one row per site code, text era + image era
Run: python3 -I scripts/mwpvl_image_reconcile.py   (stdlib only; prints the summary counts)
"""
import csv, difflib, json, re, sys, collections
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TR = ROOT / 'data/raw/mwpvl_wayback/transcriptions'
PROC = ROOT / 'data/processed'

ST = {'AL':'Alabama','AK':'Alaska','AZ':'Arizona','AR':'Arkansas','CA':'California','CO':'Colorado','CT':'Connecticut','DE':'Delaware','DC':'District of Columbia','FL':'Florida','GA':'Georgia','HI':'Hawaii','ID':'Idaho','IL':'Illinois','IN':'Indiana','IA':'Iowa','KS':'Kansas','KY':'Kentucky','LA':'Louisiana','ME':'Maine','MD':'Maryland','MA':'Massachusetts','MI':'Michigan','MN':'Minnesota','MS':'Mississippi','MO':'Missouri','MT':'Montana','NE':'Nebraska','NV':'Nevada','NH':'New Hampshire','NJ':'New Jersey','NM':'New Mexico','NY':'New York','NC':'North Carolina','ND':'North Dakota','OH':'Ohio','OK':'Oklahoma','OR':'Oregon','PA':'Pennsylvania','RI':'Rhode Island','SC':'South Carolina','SD':'South Dakota','TN':'Tennessee','TX':'Texas','UT':'Utah','VT':'Vermont','VA':'Virginia','WA':'Washington','WV':'West Virginia','WI':'Wisconsin','WY':'Wyoming','PR':'Puerto Rico'}
ABBR = {v.lower(): k for k, v in ST.items()}
ABBR.update({'michegan': 'MI', 'ilinois': 'IL', 'washington dc': 'DC', 'washington d.c.': 'DC'})
SEVERITY = ['closed', 'cancelled', 'sublease', 'on_hold', 'delayed', 'planned', 'active']
NOT_OPEN = {'planned', 'delayed', 'on_hold', 'cancelled'}

def st_abbr(s):
    s = (s or '').strip()
    if s.upper() in ST: return s.upper()
    return ABBR.get(s.lower(), s)

def g(r, f): return (r.get(f) or '').strip() if r else ''
def toks(s): return sorted(set(re.findall(r'[a-z0-9]+', (s or '').lower().replace("'", ''))))
def digits(s): return re.sub(r'[^0-9]', '', s or '')
def ncode(c): return re.sub(r'\s+', '', (c or '').upper())
def rowtext(r): return (g(r, 'status') + ' ' + g(r, 'type_label')).strip() if r else ''

def key(r):
    c = ncode(g(r, 'site_code'))
    return c if c else 'city:' + ' '.join(toks(g(r, 'city')))

def align(A, B):
    """Pair rows of the two passes in table order (difflib on code, or city when no code)."""
    sm = difflib.SequenceMatcher(None, [key(r) for r in A], [key(r) for r in B], autojunk=False)
    out = []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op in ('equal', 'replace'):
            n = min(i2 - i1, j2 - j1)
            out += [(A[i1 + t], B[j1 + t]) for t in range(n)]
            out += [(A[i1 + t], None) for t in range(n, i2 - i1)]
            out += [(None, B[j1 + t]) for t in range(n, j2 - j1)]
        elif op == 'delete': out += [(A[t], None) for t in range(i1, i2)]
        elif op == 'insert': out += [(None, B[t]) for t in range(j1, j2)]
    return out

def classify(desc):
    d = desc.lower(); t = []
    if 'sortation' in d or 'sort center' in d: t.append('sortation_center')
    if 'prime now' in d or ('hub' in d and 'prime' in d): t.append('prime_now')
    if 'fresh' in d or 'pantry' in d or 'grocery' in d or 'whole foods' in d: t.append('fresh_pantry')
    if 'return' in d: t.append('returns')
    if 'delivery station' in d or re.search(r'\bds\b', d): t.append('delivery_station')
    if ('cross' in d and 'dock' in d) or 'ixd' in d: t.append('crossdock')
    if 'air hub' in d or 'airhub' in d or 'air sortation hub' in d or 'air gateway' in d: t.append('air_hub')
    if 'non-sortable' in d or 'non sortable' in d or 'nonsortable' in d: t.append('non_sortable_fc')
    elif 'sortable' in d: t.append('sortable_fc')
    if any(k in d for k in ('specialty', 'jewelry', 'shoe', 'apparel', 'media', 'heavy', 'bulky', 'kiva', 'robot', 'amxl')) and not t: t.append('specialty')
    return '+'.join(t) if t else 'unspecified'

def diff(a, b):
    if a is None or b is None: return ['missing']
    d = []
    if ncode(g(a, 'site_code')) != ncode(g(b, 'site_code')): d.append('site_code')
    if toks(g(a, 'city')) != toks(g(b, 'city')): d.append('city')
    if st_abbr(g(a, 'state')) != st_abbr(g(b, 'state')): d.append('state')
    if digits(g(a, 'sq_ft')) != digits(g(b, 'sq_ft')): d.append('sq_ft')
    if toks(g(a, 'year_opened')) != toks(g(b, 'year_opened')): d.append('year_opened')
    if set(toks(rowtext(a))) != set(toks(rowtext(b))): d.append('text')
    return d

MONTHS = 'january february march april may june july august september october november december'.split()
def year_of(yr):
    m = re.search(r'\b(19|20)\d\d\b', yr or ''); return int(m.group()) if m else None
def month_of(yr):
    yr = (yr or '').lower(); q = re.search(r'q([1-4])', yr)
    return next((i + 1 for i, n in enumerate(MONTHS) if n in yr), int(q.group(1)) * 3 - 2 if q else 0)

CODE = re.compile(r'\b[A-Z]{3,4}\d\b|\b[A-Z]{2}\d{2}\b')
def status_of(text, yr, snap, codes=''):
    """Heuristic status from the description and the year cell, relative to the snapshot date.
    Returns (status, basis). Clauses that name another site code, or speak of a building's former
    use ('replaces X which was closed', 'site of the Century Plaza closed in 2009'), are ignored."""
    own = set(c for c in re.split(r'[/\s]+', codes or '') if c)
    t = (text + ' ' + (yr or '')).lower()
    sy, sm = int(snap[:4]), int(snap[4:6])
    y = year_of(yr); future = bool(y and (y > sy or (y == sy and month_of(yr) > sm)))
    def foreign(cl): return bool(set(CODE.findall(cl)) - own) or re.search(r'replac|formerly|former |site of|shuttered|previously|used to contain|theat', cl.lower())
    cl = [c for c in re.split(r'[.;|]\s*', text) if c.strip()]
    if any(re.search(r'\bcancel+ed\b|\bscrapped\b|\bterminated\b', c, re.I) and not re.search(r'may be|reinitiat|previously|reviv', c, re.I) and not foreign(c) for c in cl) and not re.search(r'reviv|reinitiat', t):
        return 'cancelled', 'text_says_cancelled'
    if any(re.search(r'\bclosed\b|\bclosing\b|\bclosure\b|\bshut ?down\b', c, re.I) and not foreign(c) and not re.search(r'reopen|scheduled|will|to be', c, re.I) for c in cl) and not re.search(r'reopen', t):
        return 'closed', 'text_says_closed'
    if re.search(r'subleas', t): return 'sublease', 'text_says_put_up_for_sublease'
    if re.search(r'\bon hold\b|\bpaused\b|indefinitely|may be cancel', t): return 'on_hold', 'text_says_on_hold_or_may_be_cancelled'
    if re.search(r'delay(?!ed allocation)', t) and (future or not y or y >= sy - 1 or re.search(r'delay\w* (?:opening )?since', t)):
        return 'delayed', 'text_says_delayed_not_yet_open'
    if future: return 'planned', 'opening_date_after_snapshot'
    if re.search(r'\btbd\b|not (?:yet )?(?:formal+y |officially )?confirmed|unconfirmed|to be confirmed|no eta|under construction|being constructed|planned|proposed|rumou?r|conjecture', t) \
            and not re.search(r'role of (?:the )?(?:facility|building|fc|\w{4}) (?:to be confirmed|tbd)|sq\.? ?ft\.? (?:to be confirmed|tbd)', t):
        return 'planned', 'text_says_planned_or_unconfirmed'
    if re.search(r'\bproject [a-z]+', t) and not re.search(r'project (?:delay|was|on|cancel|startup|may|paus)', t) and (not y or y >= sy):
        return 'planned', 'project_codename_current_year'
    return 'active', 'default_listed_and_not_flagged'

def merge_text(t1, t2):
    """Union of two readings of one description cell. The passes mostly differ by omission
    (one pass condensed or dropped a clause), so keep the fuller reading and append any clause
    of the other that adds words."""
    t1, t2 = (t1 or '').strip(), (t2 or '').strip()
    if len(t2) > len(t1): t1, t2 = t2, t1
    s1 = set(toks(t1)); extra = []
    for c in re.split(r'(?<=[.;|])\s+|\s*\|\s*', t2):
        c = c.strip(' ;|')
        if c and not set(toks(c)) <= s1: extra.append(c); s1 |= set(toks(c))
    return (t1 + ('; ' + '; '.join(extra) if extra else '')).strip()

def fix_code(c):
    """Site codes are 3 letters (airport code) + digit. 'RN04' and 'DB01' are typed with a zero."""
    c = ncode(c)
    return c[:2] + 'O' + c[3:] if re.fullmatch(r'[A-Z]{2}0\d', c) else c

def split_codes(cell): return [c for c in re.split(r'[/\s,]+', ncode(cell).replace('/', ' / ')) if c and c != '/']

def build_image_facts():
    P = json.load(open(TR / 'passes.json'))
    ADJ = {(a['image'], a['idx']): a for a in json.load(open(TR / 'adjudications.json'))}
    used = set(); rows = []; stats = collections.Counter()
    for im in P:
        A = (im['pass_a'] or {}).get('rows') or []; B = (im['pass_b'] or {}).get('rows') or []
        stats['images'] += 1
        if not A and not B: stats['images_no_table'] += 1; continue
        stats['images_with_rows'] += 1
        if im['invalid_pass']:
            good = B if im['invalid_pass'] == 'a' else A
            pairs = [(r, None, 'single') for r in good]
        else:
            pairs = [(x, y, None) for x, y in align(A, B)]
        seen = set()
        for i, (x, y, single) in enumerate(pairs):
            note = ''; basis = ''
            if single:
                r = x; trans = 'adjudicated'; basis = 'single_valid_pass_checked_vs_vision_ocr'
                note = 'the other pass transcribed a different image (shared tile folder); this pass was checked against a Vision OCR read'
                code, city, state, sq, yr, text = g(r, 'site_code'), g(r, 'city'), g(r, 'state'), g(r, 'sq_ft'), g(r, 'year_opened'), rowtext(r)
            else:
                d = diff(x, y); adj = ADJ.get((im['image'], i))
                if adj:
                    used.add((im['image'], i))
                    assert adj['a_code'] == (g(x, 'site_code') if x else None) and adj['b_code'] == (g(y, 'site_code') if y else None), (im['image'], i)
                    dec = adj['decision']
                    if dec.get('drop'): stats['rows_dropped_absent_from_image'] += 1; continue
                    base = x if (x and dec.get('keep') != 'b') else y
                    other = y if base is x else x
                    code = dec.get('site_code', g(base, 'site_code')); city = dec.get('city', max(g(x, 'city'), g(y, 'city'), key=len) if x and y else g(base, 'city'))
                    state = g(base, 'state'); sq = dec.get('sq_ft', g(base, 'sq_ft')); yr = dec.get('year_opened', g(base, 'year_opened'))
                    tf = dec.get('type_from')
                    text = rowtext(x if tf == 'a' else y) if tf else merge_text(rowtext(x), rowtext(y))
                    trans = 'adjudicated'; basis = adj['basis']
                    note = 'disagreed on ' + adj['why'] + ('; row present in one pass only, confirmed in image' if dec.get('keep') else '')
                else:
                    hard = [f for f in d if f in ('site_code', 'state', 'sq_ft', 'year_opened', 'missing')]
                    if hard: raise SystemExit(f'unadjudicated disagreement {im["image"]} {i} {hard}')
                    code, state, sq, yr = g(x, 'site_code'), g(x, 'state'), g(x, 'sq_ft') or g(y, 'sq_ft'), g(x, 'year_opened')
                    city = max(g(x, 'city'), g(y, 'city'), key=len)   # city: same words, or one reading names more places
                    text = merge_text(rowtext(x), rowtext(y))
                    if not d: trans = 'agreed'
                    else:
                        trans = 'adjudicated'
                        basis = 'rule:' + ('fuller_city' if 'city' in d else '') + ('+' if 'city' in d and 'text' in d else '') + ('description_union' if 'text' in d else '')
                        note = 'passes differed only in ' + '/'.join(d) + ' wording; type and status derived from the union'
            sqd = digits(sq); sqv = int(sqd) if sqd and len(sqd) >= 3 else ''
            yv = year_of(yr)
            if yv and not (1990 <= yv <= 2035): yv = None
            if re.search(r'\b(?:2[1-9]\d\d|3\d\d\d)\b', yr or ''):
                trans = 'flagged'; note = (note + '; ' if note else '') + f'year cell reads "{yr}" in the image (source typo); year left blank'
            k = (ncode(code), tuple(toks(city)), sqv, yr)
            if k in seen: stats['duplicate_rows_in_image_dropped'] += 1; continue
            seen.add(k)
            st, sb = status_of(text, yr, im['snapshot_ts'], ncode(code))
            codes = split_codes(code) or ['']
            for c in codes:
                rows.append(dict(snapshot_ts=im['snapshot_ts'], snapshot_date=f"{im['snapshot_ts'][:4]}-{im['snapshot_ts'][4:6]}-{im['snapshot_ts'][6:8]}",
                    year=im['year'], table_type=im['content_type'], image_name=im['image'].split('__', 1)[1], row_in_image=i + 1,
                    site_code=c, code_cell=ncode(code), shared_row='Y' if len(codes) > 1 else '',
                    city=city, state=st_abbr(state), sq_ft=sqv, year_opened=yv or '', raw_year_text=yr,
                    status=st, status_basis=sb, mwpvl_type=classify(text), type_label=text,
                    transcription=trans, adjudication_basis=basis, adjudication_note=note, image_url=im['archived_url']))
                stats['fact_rows_' + trans] += 1
            stats['table_rows_' + trans] += 1
    missing = set(ADJ) - used
    if missing: raise SystemExit(f'adjudications not applied: {sorted(missing)[:5]}')
    return rows, stats

def main():
    rows, stats = build_image_facts()
    cols = list(rows[0].keys())
    with open(PROC / 'mwpvl_wayback_image_facts.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
    # ---------------- merge with text era ----------------
    obs = collections.defaultdict(list)
    for r in csv.DictReader(open(PROC / 'mwpvl_wayback_facts.csv')):
        obs[fix_code(r['site_code'])].append(dict(date=r['snapshot_date'], era='text', table='', city=r['city'], state=r['state'],
            sq=r['sq_ft'], year=r['year_opened'], raw_year=r['raw_year_text'], status=r['status'], mtype=r['mwpvl_type'], url=r['wayback_url']))
    for r in rows:
        if not r['site_code']: continue
        obs[fix_code(r['site_code'])].append(dict(date=r['snapshot_date'], era='image', table=r['table_type'], city=r['city'], state=r['state'],
            sq=str(r['sq_ft']), year=str(r['year_opened']), raw_year=r['raw_year_text'], status=r['status'], mtype=r['mwpvl_type'], url=r['image_url']))
    # which snapshot dates carried each table type (for the weak 'absent from' signal)
    table_dates = collections.defaultdict(set)
    for r in rows: table_dates[r['table_type']].add(r['snapshot_date'])
    text_dates = sorted({o['date'] for v in obs.values() for o in v if o['era'] == 'text'})
    STALE = {'2026-01-17'}   # every 2026-01 image is byte-identical to its 2025-01 capture
    # captures that hold only part of a table type: 2017-07 delivery stations is a stale copy of the
    # 2016-03-30 image; 2022-07 has only Part 2 of the delivery-station list
    PARTIAL = {('delivery_station', '2017-07-13'), ('delivery_station', '2022-07-01')}
    sites = []
    for code, O in sorted(obs.items()):
        O.sort(key=lambda o: o['date'])
        dates = sorted({o['date'] for o in O})
        # year_opened: one value per snapshot (status-aware), then the conflict rule
        per = collections.OrderedDict()
        for o in O:
            if o['year']: per.setdefault(o['date'], []).append((int(o['year']), o['status']))
        cur = None; cur_st = None; flag = False; resolution = 'single_value'; seq = []
        for dte, vals in per.items():
            ys = sorted({v for v, _ in vals}); stt = min((s for _, s in vals), key=SEVERITY.index)
            if len(ys) > 1: flag = True
            yv = ys[0]; seq.append(f'{yv}@{dte}' + ('(' + stt + ')' if stt in NOT_OPEN else ''))
            if cur is None: cur, cur_st = yv, stt; continue
            if yv != cur:
                if cur_st in NOT_OPEN: cur, cur_st = yv, stt; resolution = 'later_year_after_planned'
                else: flag = True
            elif stt not in NOT_OPEN: cur_st = stt
        vals_all = sorted({v for vs in per.values() for v, _ in vs})
        if flag:
            # unexplained change (the earlier snapshot did not call the site planned): keep the value
            # MWPVL reported in the most snapshots, ties going to the later value, and flag the site
            cnt = collections.Counter(v for vs in per.values() for v in {x for x, _ in vs})
            lastpos = {v: k for k, vs in enumerate(per.values()) for v in {x for x, _ in vs}}
            cur = max(cnt, key=lambda v: (cnt[v], lastpos[v]))
            cur_st = [s for vs in per.values() for v, s in vs if v == cur][-1]
            resolution = 'conflict_modal_value'
        proj = 'Y' if cur is not None and cur_st in NOT_OPEN else ''
        sqo = [o for o in O if o['sq'] and o['sq'] != '0']
        last = [o for o in O if o['date'] == dates[-1]]
        lst = min((o['status'] for o in last), key=SEVERITY.index)
        st_hist = []; ty_hist = []
        for dte in dates:
            od = [o for o in O if o['date'] == dte]
            s = min((o['status'] for o in od), key=SEVERITY.index)
            t = '+'.join(sorted({p for o in od for p in o['mtype'].split('+')} - {'unspecified'})) or 'unspecified'
            if not st_hist or st_hist[-1][1] != s: st_hist.append((dte, s))
            if t != 'unspecified' and (not ty_hist or ty_hist[-1][1] != t): ty_hist.append((dte, t))
        tables = sorted({o['table'] for o in O if o['table']})
        last_tab = [o['table'] for o in last if o['table']]
        later = sorted(d for d in (table_dates[last_tab[0]] if last_tab else set(text_dates)) if d > dates[-1] and d not in STALE
                       and (last_tab[0] if last_tab else '', d) not in PARTIAL)
        if not last_tab and O[-1]['era'] == 'text':   # last seen in the text era: next image snapshot with any table
            later = sorted({r['snapshot_date'] for r in rows if r['snapshot_date'] > dates[-1]} | {d for d in text_dates if d > dates[-1]})
        sites.append(dict(site_code=code, first_snapshot=dates[0], first_era=O[0]['era'], last_snapshot=dates[-1], last_era=O[-1]['era'],
            n_snapshots=len(dates), year_opened=cur if cur is not None else '', year_opened_all='|'.join(map(str, vals_all)),
            year_sequence=' > '.join(seq), year_conflict='Y' if flag else '', year_resolution=resolution if cur is not None else '',
            year_is_projection=proj, latest_sq_ft=sqo[-1]['sq'] if sqo else '', latest_sq_ft_snapshot=sqo[-1]['date'] if sqo else '',
            latest_status=lst, status_history=' > '.join(f'{d}:{s}' for d, s in st_hist), latest_city=last[-1]['city'], latest_state=last[-1]['state'],
            latest_mwpvl_type=ty_hist[-1][1] if ty_hist else 'unspecified', type_history=' > '.join(f'{d}:{t}' for d, t in ty_hist),
            image_tables=';'.join(tables), absent_from_snapshot=later[0] if later else '', source='MWPVL International via Wayback Machine',
            first_url=O[0]['url'], last_url=last[-1]['url']))
    # ---------------- match to facilities_master ----------------
    M = list(csv.DictReader(open(PROC / 'facilities_master.csv')))
    bycode = collections.defaultdict(list)
    for m in M:
        for c in re.split(r'[\s/,]+', m['site_code'].upper()):
            if c: bycode[c].append(m)
    for s in sites:
        ms = bycode.get(s['site_code'], [])
        s['in_facilities_master'] = 'Y' if ms else ''
        s['master_facility_ids'] = ';'.join(m['facility_id'] for m in ms)
        s['master_year_basis'] = ';'.join(sorted({m['year_basis'] for m in ms}))
        s['master_first_osha_filing_year'] = ';'.join(sorted({m['first_osha_filing_year'] for m in ms if m['first_osha_filing_year']}))
    with open(PROC / 'mwpvl_wayback_sites_all.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(sites[0].keys())); w.writeheader(); w.writerows(sites)
    # ---------------- summary ----------------
    S = {s['site_code']: s for s in sites}
    matched = [s for s in sites if s['in_facilities_master']]
    gain = [m for m in M if m['year_basis'] == 'first_osha_filing' and S.get(m['site_code'].upper(), {}).get('year_opened') not in (None, '')]
    out = dict(stats)
    out.update(sites_total=len(sites), sites_matched=len(matched), match_rate=round(len(matched) / len(sites), 4),
        sites_image_era_only=sum(1 for s in sites if s['first_era'] == 'image'),
        master_rows_first_osha_gain_year=len(gain), master_codes_first_osha_gain_year=len({m['site_code'] for m in gain}),
        gain_year_is_projection=sum(1 for m in gain if S[m['site_code'].upper()]['year_is_projection']),
        gain_year_conflict=sum(1 for m in gain if S[m['site_code'].upper()]['year_conflict']),
        gain_mwpvl_earlier_than_osha=sum(1 for m in gain if m['first_osha_filing_year'] and int(S[m['site_code'].upper()]['year_opened']) < int(m['first_osha_filing_year'])),
        latest_status=dict(collections.Counter(s['latest_status'] for s in sites)),
        year_resolution=dict(collections.Counter(s['year_resolution'] for s in sites)))
    print(json.dumps(out, indent=1))

if __name__ == '__main__':
    main()
