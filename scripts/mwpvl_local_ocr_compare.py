#!/usr/bin/env python3
"""Compare local OCR rows with the Claude transcription. Writes mwpvl_ocr_disagreements.csv and prints agreement stats."""
import csv, re, collections, json, os
P = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "processed")
cl = list(csv.DictReader(open(f"{P}/mwpvl_wayback_image_facts.csv")))
oc = list(csv.DictReader(open(f"{P}/mwpvl_wayback_image_facts_localocr.csv")))
def nsq(s):
    s = re.sub(r"[,\s]", "", s or ""); return s if s.isdigit() else ("" if s in ("-", "") else s)
def nyr(s):
    m = re.search(r"(19|20)\d\d", s or ""); return m.group(0) if m else ""
def ncity(s): return re.sub(r"[^a-z]", "", (s or "").lower())
def toks(s): return [t for t in re.split(r"[/\s,]+", (s or "").upper()) if t]
cimg = collections.defaultdict(list)
for r in cl: cimg[f"{r['snapshot_ts']}__{re.sub(r'\.png$', '', r['image_name'])}"].append(r)
oimg = collections.defaultdict(list)
for r in oc: oimg[r["image"]].append(r)
fields = ["site_code", "city", "state", "sq_ft", "year_opened"]
agree = collections.Counter(); tot = collections.Counter(); per_img = {}; dis = []; unmatched = collections.Counter(); nrows = collections.Counter()
for img, crow in cimg.items():
    orow = oimg.get(img)
    if not orow:
        unmatched["image_no_ocr"] += len(crow); continue
    used = set(); a = collections.Counter(); t = collections.Counter()
    for c in crow:
        j = None; code = c["site_code"].upper()
        if code:
            for i, o in enumerate(orow):
                if i not in used and code in toks(o["site_code"]) and (not c["state"] or o["state"] == c["state"] or True): j = i; break
        basis = "code" if j is not None else None
        if j is None:
            for i, o in enumerate(orow):
                if i not in used and ncity(o["city"]) == ncity(c["city"]) and o["state"] == c["state"] and nsq(o["sq_ft"]) == nsq(c["sq_ft"]): j = i; break
        if j is not None and basis is None: basis = "city_state_sqft"
        if j is None:
            for i, o in enumerate(orow):
                if i not in used and ncity(o["city"]) == ncity(c["city"]) and o["state"] == c["state"]: j = i; basis = "city_state"; break
        nrows["claude"] += 1
        if j is None: unmatched["claude_row_unmatched"] += 1; continue
        # shared-code rows share one OCR row: do not consume, so each code matches
        if len(toks(orow[j]["site_code"])) <= 1: used.add(j)
        o = orow[j]; nrows["matched"] += 1
        cv = dict(site_code=code, city=ncity(c["city"]), state=c["state"], sq_ft=nsq(c["sq_ft"]), year_opened=c["year_opened"])
        ov = dict(site_code=(code if code in toks(o["site_code"]) else o["site_code"].upper()), city=ncity(o["city"]), state=o["state"], sq_ft=nsq(o["sq_ft"]), year_opened=nyr(o["year_opened"]))
        for f in fields:
            t[f] += 1; tot[f] += 1
            if cv[f] == ov[f]: a[f] += 1; agree[f] += 1
            else: dis.append(dict(image=img, row_in_image=c["row_in_image"], field=f, site_code=c["site_code"], city=c["city"], state=c["state"], match_basis=basis, claude=c[f] if f != "city" else c["city"], ocr=o[f], ocr_normalized=ov[f], claude_normalized=cv[f], raw_year_text=c["raw_year_text"], claude_transcription=c["transcription"], models_agree="n/a (single local model)", decision=""))
    per_img[img] = (sum(a.values()), sum(t.values()))
print("rows", dict(nrows), dict(unmatched))
for f in fields: print(f, agree[f], tot[f], round(agree[f] / max(1, tot[f]), 4))
print("overall", sum(agree.values()), sum(tot.values()), round(sum(agree.values()) / sum(tot.values()), 4))
w = csv.DictWriter(open(f"{P}/mwpvl_ocr_disagreements.csv", "w", newline=""), fieldnames=list(dis[0].keys())); w.writeheader(); w.writerows(dis)
json.dump({k: v for k, v in per_img.items()}, open("/private/tmp/claude-502/per_img.json", "w"))
print("disagreements", len(dis), collections.Counter(d["field"] for d in dis))
worst = sorted(per_img.items(), key=lambda kv: kv[1][0] / max(1, kv[1][1]))[:8]; print(worst)
