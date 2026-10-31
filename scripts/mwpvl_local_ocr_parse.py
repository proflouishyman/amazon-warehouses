#!/usr/bin/env python3
"""Parse local OCR html tables into data/processed/mwpvl_wayback_image_facts_localocr.csv."""
import csv, glob, html, os, re
ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
OUT = f"{ROOT}/processed/mwpvl_wayback_image_facts_localocr.csv"
ST = {"Alabama":"AL","Alaska":"AK","Arizona":"AZ","Arkansas":"AR","California":"CA","Colorado":"CO","Connecticut":"CT","Delaware":"DE","Florida":"FL","Georgia":"GA","Hawaii":"HI","Idaho":"ID","Illinois":"IL","Indiana":"IN","Iowa":"IA","Kansas":"KS","Kentucky":"KY","Louisiana":"LA","Maine":"ME","Maryland":"MD","Massachusetts":"MA","Michigan":"MI","Minnesota":"MN","Mississippi":"MS","Missouri":"MO","Montana":"MT","Nebraska":"NE","Nevada":"NV","New Hampshire":"NH","New Jersey":"NJ","New Mexico":"NM","New York":"NY","North Carolina":"NC","North Dakota":"ND","Ohio":"OH","Oklahoma":"OK","Oregon":"OR","Pennsylvania":"PA","Rhode Island":"RI","South Carolina":"SC","South Dakota":"SD","Tennessee":"TN","Texas":"TX","Utah":"UT","Vermont":"VT","Virginia":"VA","Washington":"WA","West Virginia":"WV","Wisconsin":"WI","Wyoming":"WY","District of Columbia":"DC"}
def cells(tr): return [html.unescape(re.sub(r"<[^>]+>", " ", c)).strip() for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.S)]
def norm_ws(s): return re.sub(r"\s+", " ", s).strip()
def parse(path):
    txt = open(path).read(); out = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", txt, re.S):
        c = [norm_ws(x) for x in cells(tr)]
        if len(c) < 5 or c[0].lower() in ("state", "") and c[1].lower() == "code": continue
        if c[1].lower() == "code": continue
        state_full, code, loc, sq, yr = c[0], c[1], c[2], c[3], c[4]
        desc = c[5] if len(c) > 5 else ""
        parts = [p.strip() for p in loc.split(",")]
        city = ""
        for i, p in enumerate(parts):
            if p in ST and i >= 1: city = re.sub(r"\s*\(.*\)", "", parts[i-1]); break
        out.append(dict(site_code=code, city=city, state=ST.get(state_full, state_full), sq_ft=sq, year_opened=yr, type_label=desc))
    return out
rows = []
for d in sorted(glob.glob(f"{ROOT}/raw/mwpvl_wayback/ocr_local/*/")):
    model = os.path.basename(d.rstrip("/"))
    for f in sorted(glob.glob(d + "*.md")):
        seen = set()
        for r in parse(f):
            k = tuple(r.values())
            if k in seen: continue  # overlap strips duplicate rows
            seen.add(k); rows.append(dict(image=os.path.basename(f)[:-3], model=model, **r))
with open(OUT, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames="image model site_code city state sq_ft year_opened type_label".split()); w.writeheader(); w.writerows(rows)
print(len(rows), "rows,", len({r["image"] for r in rows}), "images")
