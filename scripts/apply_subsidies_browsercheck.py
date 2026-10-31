"""Browser-pass adversarial check (2026-10-31): apply verified fixes to subsidies_verified.csv
and rebuild the summary. Backs up first; refuses to overwrite an existing backup."""
import csv, os, shutil, sys
sys.path.insert(0, os.path.dirname(__file__))
from subsidies_summary_lib import summarize, write
P = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed')
SRC = os.path.join(P, 'subsidies_verified.csv')
SUM = os.path.join(P, 'subsidies_verified_summary.csv')
for a, b in [(SRC, 'subsidies_verified.pre_browsercheck.csv'), (SUM, 'subsidies_verified_summary.pre_browsercheck.csv')]:
    dst = os.path.join(P, b)
    if not os.path.exists(dst):
        shutil.copy2(a, dst)
with open(SRC, newline='') as f:
    rd = csv.DictReader(f); fields = rd.fieldnames; rows = list(rd)
cur = [r for r in csv.reader(open(SUM, newline=''))][1:]
assert [[str(c) for c in r] for r in summarize(rows)] == cur, 'summary mismatch before edit'

PFX = 'Browser-pass check 2026-10-31: downgraded from {old} to unverified (kept as a lead, out of verified totals). '
FIXES = [
    (dict(state='SD', locality='Sioux Falls', award_year='2021', amount_usd='94371313', merged_from='SD.csv#2'),
     'primary',
     'The saved TIF #23 project plan (siouxfalls_gov_TIF23_project_plan.pdf) never names Amazon. The $94,371,313 is the '
     'TIF requested by the Sioux Falls Development Foundation for the whole 539-acre Foundation Park North: it includes a '
     '$30,000,000 off-site Economic Development Competitiveness Fund and $30,184,577 of financing costs, against '
     '$2.5B of projected tenant investment across the park. The recipient is a park developer, not Amazon or a developer '
     'acting for Amazon, so the figure is not an Amazon subsidy at this amount.'),
    (dict(state='KS', locality='Salina', award_year='2025', amount_usd='6000000', merged_from='KS.csv#16'),
     'primary',
     'The SAA memo (salina_airport_authority_board_2026-01-19_item116.pdf, p.3-4) shows the $6,000,000 is temporary-note '
     'financing for the street and utility network of the 80-acre Project 80 (Amazon bought 20 acres). About $1,560,000 '
     'was not spent on it and is being reallocated to the airport terminal and MRO hangars, and the permanent financing is '
     'retired by special assessments on all benefited landowners (Amazon included). It is financing repaid by the '
     'landowners, not an established subsidy value.'),
    (dict(state='NM', award_year='2021', amount_usd='6500000', merged_from='NM.csv#2'),
     'secondary',
     'The only saved text (minuteman_2021_no_incentives_amazon_abq.html, a reprint of KRQE) says the $6.5M was county '
     'spending on the Upper Petroglyphs industrial park, that Amazon did not receive it, that "most of that money has been '
     'recouped by Bernalillo County in fees Amazon has paid", and that no incentive money was used. The KRQE file is an '
     'empty 403 page. A cost mostly recovered from Amazon is not a realized subsidy of $6.5M.'),
    (dict(state='WI', locality='Kenosha', award_year='2013', amount_usd='7000000', merged_from='WI.csv#6'),
     'secondary',
     'Same WEDC 2013 award as the 10.3M Kenosha row (WI.csv#3): the $7M was quoted in Nov 2013 for the first building '
     '($141M, 1,100 jobs); BizTimes "The Amazon Effect" gives up to $10.3M for the two-building project ($155M, 1,250 '
     'jobs) and BizTimes 2019 says "$10.3 million in credits awarded to Amazon for its Kenosha facilities in 2013". Both '
     'rows sat in the WI 2013 announced_max secondary group, so the same credits were summed twice (35.3M).'),
]
changed = 0
for m, old, why in FIXES:
    hit = [r for r in rows if all(r[k] == v for k, v in m.items())]
    assert len(hit) == 1, (m, len(hit))
    r = hit[0]
    assert r['verification_level'] == old and r['row_kind'] == 'award', (m, r['verification_level'])
    r['verification_level'] = 'unverified'
    r['notes'] = (r['notes'].rstrip() + ' ' + PFX.format(old=old) + why).strip()
    changed += 1
with open(SRC, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)
write(SUM, summarize(rows))
print('rows changed:', changed, 'rows total:', len(rows))
