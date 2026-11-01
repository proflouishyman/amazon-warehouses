#!/usr/bin/env python3
"""Record the crop-viewed decisions on mwpvl_ocr_3way_flags.csv and write mwpvl_corrections_ocr.csv.
Decisions were made by viewing a crop of each flagged row (target row marked with a red bar, rows above and below shown) on 2026-11-01.
Flags are keyed by (field, site_code, claude_norm, ocr_value) so this is safe to rerun after mwpvl_ocr_3way.py.
Evidence crops (PNG) are kept in data/raw/mwpvl_wayback/ocr_local/evidence_crops/."""
import csv, os, shutil, collections
A = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
P = f"{A}/processed"; EV = f"{A}/raw/mwpvl_wayback/ocr_local/evidence_crops"; SRC = os.environ.get("MWPVL_CROP_DIR")
fl = list(csv.DictReader(open(f"{P}/mwpvl_ocr_3way_flags.csv")))
REASON = {  # flag number (order of non-city flags in the file when settled) -> reason; every flag settled claude_correct unless in OCR_CORRECT
 **{i: ("ocr_year_cell_dropped_description_read_instead" if i in (2, 4, 10, 11, 12, 13, 14, 15, 16, 18, 19, 27, 28, 29, 30, 31) else "ocr_read_year_of_adjacent_row") for i in range(0, 32)},
 **{i: "code_cell_blank_in_image_ocr_invented_code" for i in (32, 34, 35)},
 **{i: "shared_code_cell_split_by_claude_one_row_per_code" for i in (33, 36, 42, 45)},
 **{i: "ocr_letter_digit_confusion" for i in (37, 38, 39, 40, 41, 43, 44, 46, 47, 48)},
 49: "ocr_read_wrong_sqft", 50: "sqft_cell_is_dash_ocr_read_other_value", 51: "ocr_read_wrong_sqft", 52: "ocr_read_wrong_sqft", 53: "sqft_cell_is_TBD_placeholder_kept_blank", 54: "ocr_read_wrong_sqft",
 55: "source_typo_Aizona_normalised_to_AZ", 56: "ocr_state_error", 57: "source_typo_Aizona_normalised_to_AZ", 58: "ocr_state_error", 59: "ocr_misspelt_Michigan", 60: "ocr_state_error"}
OCR_CORRECT = {55, 57}   # state field only: image prints "Aizona" (source typo); Claude copied it verbatim, OCR gave AZ. A normalisation, not a transcription error.
n = 0; os.makedirs(EV, exist_ok=True)
for r in fl:
    if r["priority"] == "5": r["decision"] = ""; continue
    i = n; n += 1; r["decision"] = "ocr_correct" if i in OCR_CORRECT else "claude_correct"; r["reason"] = REASON[i]
    src = f"{SRC}/flag_{i:02d}.png" if SRC else None
    dst = f"{EV}/flag_{i:02d}_{r['field']}_{r['site_code'].replace(' ', '_').replace('(', '').replace(')', '')}.png"
    if src and os.path.exists(src) and not os.path.exists(dst): shutil.copy(src, dst)
    if os.path.exists(dst): r["evidence_crop_path"] = os.path.relpath(dst, os.path.dirname(A))
for r in fl: r.setdefault("reason", "")
fn = list(fl[0].keys()); w = csv.DictWriter(open(f"{P}/mwpvl_ocr_3way_flags.csv", "w", newline=""), fieldnames=fn); w.writeheader(); w.writerows(fl)
# corrections: every Claude cell whose state is the typo 'Aizona' (6 cells), not only the flagged ones
cl = list(csv.DictReader(open(f"{P}/mwpvl_wayback_image_facts.csv")))
ev = {r["site_code"]: r["evidence_crop_path"] for r in fl if r["decision"] == "ocr_correct"}
out = [dict(site_code=c["site_code"], snapshot=c["snapshot_ts"], field="state", old=c["state"], new="AZ", evidence_crop_path=ev.get(c["site_code"] or "", next(iter(ev.values()), "")), note=f"table {c['image_name']} row {c['row_in_image']}; image prints Aizona (source typo), normalisation only")
       for c in cl if c["state"] == "Aizona"]
w = csv.DictWriter(open(f"{P}/mwpvl_corrections_ocr.csv", "w", newline=""), fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
print(collections.Counter((r["field"], r["decision"]) for r in fl if r["priority"] != "5"), len(out), "correction rows")
