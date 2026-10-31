"""Gap-fill adversarial check (2026-10-31): apply verified fixes to subsidies_verified.csv
and rebuild the summary. Backs up first; refuses to overwrite an existing backup."""
import csv, os, shutil, sys
sys.path.insert(0, os.path.dirname(__file__))
from subsidies_summary_lib import summarize, write
P = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed')
SRC = os.path.join(P, 'subsidies_verified.csv')
SUM = os.path.join(P, 'subsidies_verified_summary.csv')
for a, b in [(SRC, 'subsidies_verified.pre_gapcheck.csv'), (SUM, 'subsidies_verified_summary.pre_gapcheck.csv')]:
    dst = os.path.join(P, b)
    if not os.path.exists(dst):
        shutil.copy2(a, dst)
with open(SRC, newline='') as f:
    rd = csv.DictReader(f); fields = rd.fieldnames; rows = list(rd)
# sanity: summary logic reproduces the current summary before edits
cur = [r for r in csv.reader(open(SUM, newline=''))][1:]
assert [[str(c) for c in r] for r in summarize(rows)] == cur, 'summary mismatch before edit'

FIXES = [
    # (match, field, old, new, note)
    (dict(state='MN', locality='Shakopee', award_year='2015', amount_usd='6400000', merged_from='MN.csv#2'),
     'verification_level', 'secondary', 'unverified',
     'Gap-fill check 2026-10-31: downgraded from secondary. The saved sources document a REQUEST in a draft TIF plan '
     '(MPR 2015-04-22, "asks for as much as $6.4 million") and Planning Commission approval only; no saved page shows '
     'council approval or an award. Finance & Commerce 2015-05-12 says $6.4M is the total new tax increment, that Scott '
     'County may take road costs off the top and that Amazon\'s slice was estimated at about $3.4M. Kept as a lead, '
     'out of verified totals.'),
]
changed = 0
for m, fld, old, new, note in FIXES:
    hit = [r for r in rows if all(r[k] == v for k, v in m.items())]
    assert len(hit) == 1, (m, len(hit))
    r = hit[0]
    assert r[fld] == old, (m, r[fld])
    r[fld] = new
    r['notes'] = (r['notes'].rstrip() + ' ' + note).strip()
    changed += 1
with open(SRC, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)
write(SUM, summarize(rows))
print('rows changed:', changed, 'rows total:', len(rows))
