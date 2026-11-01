#!/usr/bin/env python3
"""Three-way comparison per cell: Claude transcription vs Unlimited-OCR-2-4bit vs DeepSeek-OCR-8bit.
Needs mwpvl_local_ocr_parse.py to have been run over both model dirs (writes model + location columns).
Writes data/processed/mwpvl_ocr_3way.csv (every cell where any model differs from Claude) and
mwpvl_ocr_3way_flags.csv (DISTINCT cases where Unlimited and DeepSeek agree with each other but differ from Claude).
Normalisation (beyond the single-model compare): city parentheticals stripped, Claude city found among the OCR
address parts = "format"; an OCR year that is a number > 10,000 = column shift (not a year disagreement)."""
import csv, re, collections, os, json
P = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "processed")
U, D = "Unlimited-OCR-2-4bit", "DeepSeek-OCR-8bit"
cl = list(csv.DictReader(open(f"{P}/mwpvl_wayback_image_facts.csv")))
oc = list(csv.DictReader(open(f"{P}/mwpvl_wayback_image_facts_localocr.csv")))
def nsq(s):
    s = re.sub(r"[,\s]", "", s or ""); return s if s.isdigit() else ("" if s in ("-", "") else s)
def nyr_old(s):
    m = re.search(r"(19|20)\d\d", s or ""); return m.group(0) if m else ""
def nyr(s):
    t = re.sub(r"[,\s]", "", s or "")
    if t.isdigit() and int(t) > 10000: return "SHIFT"
    return nyr_old(s)
def ncity_old(s): return re.sub(r"[^a-z]", "", (s or "").lower())
def ncity(s): return ncity_old(re.sub(r"\s*\([^)]*\)", "", s or ""))
def toks(s): return [t for t in re.split(r"[/\s,]+", (s or "").upper()) if t]
def loc_parts(loc): return {ncity(p) for p in (loc or "").split(",") if ncity(p) and not p.strip().isdigit()}
FIELDS = ["site_code", "city", "state", "sq_ft", "year_opened"]
cimg = collections.defaultdict(list)
for r in cl: cimg[f"{r['snapshot_ts']}__{re.sub(r'\.png$', '', r['image_name'])}"].append(r)
oimg = {U: collections.defaultdict(list), D: collections.defaultdict(list)}
for r in oc:
    if r["model"] in oimg: oimg[r["model"]][r["image"]].append(r)

def align(crow, orow):
    """Claude row -> matched OCR row (or None), same logic as mwpvl_local_ocr_compare.py."""
    used = set(); res = []
    for c in crow:
        j = None; code = c["site_code"].upper()
        if code:
            for i, o in enumerate(orow):
                if i not in used and code in toks(o["site_code"]): j = i; break
        if j is None:
            for i, o in enumerate(orow):
                if i not in used and ncity_old(o["city"]) == ncity_old(c["city"]) and o["state"] == c["state"] and nsq(o["sq_ft"]) == nsq(c["sq_ft"]): j = i; break
        if j is None:
            for i, o in enumerate(orow):
                if i not in used and ncity_old(o["city"]) == ncity_old(c["city"]) and o["state"] == c["state"]: j = i; break
        if j is not None and len(toks(orow[j]["site_code"])) <= 1: used.add(j)
        res.append(orow[j] if j is not None else None)
    return res

def vals(c, o, new=True):
    """normalised (claude, ocr) values for each field plus status for the OCR side."""
    code = c["site_code"].upper(); out = {}
    cv = dict(site_code=code, city=ncity(c["city"]) if new else ncity_old(c["city"]), state=c["state"], sq_ft=nsq(c["sq_ft"]), year_opened=c["year_opened"])
    ov = dict(site_code=(code if code in toks(o["site_code"]) else o["site_code"].upper()), city=ncity(o["city"]) if new else ncity_old(o["city"]),
              state=o["state"], sq_ft=nsq(o["sq_ft"]), year_opened=nyr(o["year_opened"]) if new else nyr_old(o["year_opened"]))
    for f in FIELDS:
        if cv[f] == ov[f]: st = "agree"
        elif new and f == "year_opened" and ov[f] == "SHIFT": st = "shift"
        elif new and f == "city" and cv["city"] and cv["city"] in loc_parts(o.get("location")): st = "format"
        else: st = "disagree"
        out[f] = (cv[f], ov[f], st)
    return out

old_cnt = {m: collections.Counter() for m in (U, D)}; new_cnt = {m: collections.Counter() for m in (U, D)}
tot = collections.Counter(); pair = collections.defaultdict(collections.Counter)
cells = []; nomatch = collections.Counter()
for img, crow in cimg.items():
    al = {m: (align(crow, oimg[m][img]) if oimg[m].get(img) else [None] * len(crow)) for m in (U, D)}
    for k, c in enumerate(crow):
        ou, od = al[U][k], al[D][k]
        if ou is None: nomatch["U_unmatched"] += 1
        if od is None: nomatch["D_unmatched"] += 1
        if ou is None and od is None: continue
        vu = vals(c, ou) if ou else None; vd = vals(c, od) if od else None
        vuo = vals(c, ou, False) if ou else None; vdo = vals(c, od, False) if od else None
        for f in FIELDS:
            tot[f] += 1
            for m, v, vo in ((U, vu, vuo), (D, vd, vdo)):
                if v is None: continue
                pair[f][f"{m}_n"] += 1
                if vo[f][2] == "agree": old_cnt[m][f] += 1
                if v[f][2] in ("agree", "format"): new_cnt[m][f] += 1
            sU = vu[f][2] if vu else "nomatch"; sD = vd[f][2] if vd else "nomatch"
            uval = vu[f][1] if vu else None; dval = vd[f][1] if vd else None
            if vu and vd:
                pair[f]["both_n"] += 1
                if uval == dval: pair[f]["U_eq_D"] += 1
                if uval == dval and sU in ("agree", "format") and sD in ("agree", "format"): pair[f]["all3"] += 1
            if sU in ("agree", "format") and sD in ("agree", "format"): continue
            if sU == "nomatch" or sD == "nomatch": cat = "one_model_unmatched"
            elif sU == "shift" or sD == "shift": cat = "column_shift"
            elif sU == "disagree" and sD == "disagree" and uval == dval: cat = "claude_vs_both_agreeing"
            elif sU == "disagree" and sD == "disagree": cat = "all_three_differ"
            elif sU == "disagree": cat = "only_unlimited_disagrees"
            else: cat = "only_deepseek_disagrees"
            cv = (vu or vd)[f][0]
            cells.append(dict(image=img, row_in_image=c["row_in_image"], snapshot=c["snapshot_ts"], field=f, site_code=c["site_code"], city=c["city"], state=c["state"],
                              claude=c[f], claude_norm=cv, unlimited_raw=(ou[f] if ou else ""), unlimited_norm=uval if uval is not None else "", unlimited_status=sU,
                              deepseek_raw=(od[f] if od else ""), deepseek_norm=dval if dval is not None else "", deepseek_status=sD, category=cat, raw_year_text=c["raw_year_text"]))
cat_cnt = collections.Counter((x["field"], x["category"]) for x in cells)
with open(f"{P}/mwpvl_ocr_3way.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(cells[0].keys())); w.writeheader(); w.writerows(cells)

# distinct flags
fl = collections.OrderedDict()
for x in cells:
    if x["category"] != "claude_vs_both_agreeing": continue
    key = (x["site_code"] or f"(no code) {x['city']}", x["field"], x["claude_norm"], x["unlimited_norm"])
    e = fl.setdefault(key, dict(site_code=key[0], field=x["field"], claude_value=x["claude"], claude_norm=x["claude_norm"], ocr_value=x["unlimited_norm"],
                                unlimited_raw=x["unlimited_raw"], deepseek_raw=x["deepseek_raw"], city=x["city"], state=x["state"], n_cells=0, snaps=set(), first_snapshot=x["snapshot"], first_image=x["image"], first_row_in_image=x["row_in_image"], raw_year_text=x["raw_year_text"]))
    e["n_cells"] += 1; e["snaps"].add(x["snapshot"])
prio = {"year_opened": 1, "site_code": 2, "sq_ft": 3, "state": 4, "city": 5}
flags = []
for e in fl.values():
    e["n_snapshots"] = len(e.pop("snaps")); e["priority"] = prio[e["field"]]; e["decision"] = ""; e["evidence_crop_path"] = ""
    flags.append(e)
flags.sort(key=lambda e: (e["priority"], -e["n_snapshots"], e["site_code"]))
fn = ["priority", "field", "site_code", "claude_value", "claude_norm", "ocr_value", "unlimited_raw", "deepseek_raw", "city", "state", "n_cells", "n_snapshots", "first_snapshot", "first_image", "first_row_in_image", "raw_year_text", "decision", "evidence_crop_path"]
with open(f"{P}/mwpvl_ocr_3way_flags.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=fn); w.writeheader(); w.writerows(flags)

# distinct all-differences collapse (any model vs Claude), for the notes
distinct_any = set((x["site_code"], x["field"], x["claude_norm"], x["unlimited_norm"] if x["unlimited_status"] == "disagree" else x["deepseek_norm"]) for x in cells if x["category"] not in ("column_shift", "one_model_unmatched"))
print("claude rows unmatched:", dict(nomatch))
print("cells", dict(tot))
print("\nagreement with Claude (old norm -> new norm), per model, field: cells")
for m in (U, D):
    for f in FIELDS:
        n = pair[f][f"{m}_n"]; print(f"{m:22s} {f:12s} n={n:6d} old={old_cnt[m][f]/n:.4f} new={new_cnt[m][f]/n:.4f}")
    a = sum(old_cnt[m].values()); b = sum(new_cnt[m].values()); n = sum(pair[f][f"{m}_n"] for f in FIELDS)
    print(f"{m:22s} OVERALL      n={n} disagree_old={n-a} disagree_new={n-b}")
print("\nU vs D equal, and three-way all-agree, per field (rows matched by both)")
for f in FIELDS:
    n = pair[f]["both_n"]; print(f"{f:12s} both_n={n:6d} U=D {pair[f]['U_eq_D']/n:.4f} all3 {pair[f]['all3']/n:.4f}")
print("\ncategories:"); [print(" ", k, v) for k, v in sorted(cat_cnt.items())]
print("\nflags (distinct) by field:", dict(collections.Counter(e["field"] for e in flags)), "cells:", dict(collections.Counter({f: sum(e["n_cells"] for e in flags if e["field"] == f) for f in prio})))
print("distinct any-model differences:", len(distinct_any))
