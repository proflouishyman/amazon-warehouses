import csv, os, re, sys, json
sys.path.insert(0, os.path.dirname(__file__))
from subsidies_summary_lib import summarize, write
D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
P = D + '/processed'
S = "CO MN MO OR WI NV SC AR CT IA KS LA NM OK MS NE NH ME VT WV ID MT ND SD WY AK HI DC".split()
old = list(csv.DictReader(open(P + '/subsidies_verified.pre_gapfill.csv')))
cols = list(old[0].keys())
rank = {'primary': 3, 'secondary': 2, 'unverified': 1}
# index of files under raw/subsidies by basename
byname = {}
for root, _, fs in os.walk(D + '/raw/subsidies'):
    for f in fs:
        byname.setdefault(f, []).append(os.path.relpath(os.path.join(root, f), D))
def norm_lf(val, st, unresolved):
    out = []
    for t in [t.strip() for t in re.split(r';(?![^()]*\))', val or '') if t.strip()]:
        c = re.sub(r'\s*\(.*\)\s*$', '', t)
        if c.startswith(D + '/'): c = c[len(D) + 1:]
        if c.startswith('data/'): c = c[5:]
        cands = [c, f'raw/subsidies/{st}/{c}']
        hit = next((x for x in cands if os.path.isfile(D + '/' + x)), None)
        if not hit and os.path.basename(c) in byname:
            hit = byname[os.path.basename(c)][0] if len(byname[os.path.basename(c)]) == 1 else next((x for x in byname[os.path.basename(c)] if f'/{st}/' in x), None)
        if hit: out.append(hit)
        else:
            out.append(c); unresolved.append((st, t))
    seen = []
    for x in out:
        if x not in seen: seen.append(x)
    return '; '.join(seen)
def kind(x):
    rk = (x.get('row_kind') or '').strip()
    if rk == 'not_searched': return 'not_searched_marker'
    if rk: return rk
    if x['facility_desc'].startswith('searched_none') or x['program'].strip() == 'none found': return 'searched_none'
    return 'award'
new = []
for s in S:
    for i, x in enumerate(csv.DictReader(open(f'{P}/subsidies_by_state/{s}.csv')), start=2):
        r = {c: '' for c in cols}
        r.update({k: v for k, v in x.items() if k in cols})
        r['state'] = s
        r['row_kind'] = kind(x)
        r['merged_from'] = f'{s}.csv#{i}'
        new.append(r)
kept = [r for r in old if r['state'] not in S]
removed = [r for r in old if r['state'] in S]
rows = kept + new
unres = []
for r in rows:
    r['local_file'] = norm_lf(r['local_file'], r['state'], unres)
# dedup
def key(r):
    return (r['state'], r['locality'].lower().strip(), r['award_year'], r['amount_usd'], r['amount_basis'], re.sub(r'\W+', ' ', r['program'].lower())[:60], r['row_kind'] if r['row_kind'] != 'award' else '')
best = {}; order = []; dropped = 0
for r in rows:
    k = key(r)
    if k not in best: best[k] = r; order.append(k); continue
    dropped += 1
    a = best[k]; b = r
    win, lose = (b, a) if rank[b['verification_level']] >= rank[a['verification_level']] else (a, b)
    alts = [u for u in (win['alt_sources'].split('; ') + [lose['source_url']] + lose['alt_sources'].split('; ')) if u and u != win['source_url']]
    win['alt_sources'] = '; '.join(dict.fromkeys(alts)); best[k] = win
out = sorted((best[k] for k in order), key=lambda r: r['state'])  # stable
with open(P + '/subsidies_verified.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, cols); w.writeheader(); w.writerows(out)
write(P + '/subsidies_verified_summary.csv', summarize(out))
json.dump({'unresolved': unres, 'dropped': dropped, 'old_rows_replaced': len(removed), 'total': len(out)}, open('/tmp/claude-502/gapfill_report.json', 'w'), indent=1) if os.path.isdir('/tmp/claude-502') else None
print('total', len(out), 'dropped dup', dropped, 'replaced', len(removed), 'new', len(new))
print('unresolved', len(unres)); [print(u) for u in unres]
