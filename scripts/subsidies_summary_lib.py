import csv, collections
def summarize(rows):
    g = collections.OrderedDict()
    for x in rows:
        if x['row_kind'] != 'award':
            continue
        k = (x['state'], x['award_year'] or 'unknown', x['amount_basis'] or 'no_amount_stated', x['verification_level'])
        g.setdefault(k, []).append(x)
    out = []
    for k in sorted(g):
        rs = g[k]
        amts = [float(r['amount_usd']) for r in rs if r['amount_usd'].strip()]
        n = len(amts)
        t = round(sum(amts), 2); tot = '' if n == 0 else (str(int(t)) if t == int(t) else str(t))
        note = ('no dollar amount stated; excluded from totals' if k[2] == 'no_amount_stated' else
                'single basis; do not add to other bases' if len(rs) == 1 else
                'single basis; do not add to other bases; rows overlap within packages, indicative')
        out.append([k[0], k[1], k[2], k[3], len(rs), n, tot, note])
    return out
def write(path, out):
    with open(path, 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['state','award_year','amount_basis','verification_level','rows','rows_with_amount','amount_usd','note']); w.writerows(out)
