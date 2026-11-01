# MWPVL International (Wayback Machine) opening-year facts

Status: built 2026-10-31. Not yet integrated into any page or build script.

## Attribution language (use verbatim)
"Site code, city, state, facility type, square footage, opening year and status are facts compiled from archived pages of MWPVL International (mwpvl.com) as captured by the Internet Archive Wayback Machine. Each row cites its snapshot URL. No MWPVL text, analysis or images are reproduced. MWPVL's figures are its own estimates and may differ from Amazon's."
Every row in `mwpvl_wayback_facts.csv` carries its own `wayback_url`. Site-level rows are derived from those facts (`source` column).

## Method
1. CDX query `mwpvl.com/html/amazon*` (781 captures, collapse=digest). The only page with a facility list is `html/amazon_com.html` ("Amazon Distribution Network Strategy"; 298 HTTP-200 text/html captures, 2012-06-22 to 2026-10-22). No capture of it exists before 2012-06, so 2010 and 2011 cannot be covered.
2. Fetched raw HTML with the `id_` suffix (`web.archive.org/web/<ts>id_/<url>`), 2.5 s between requests, a descriptive User-Agent. Some responses are gzip even without Accept-Encoding; they were decompressed. Saved in `data/raw/mwpvl_wayback/` (gitignored via `data/raw/`), with `cdx.json`.
3. Parsed only HTML text tables (stdlib `html.parser`, nested-table aware): six columns (site code, address, country flag alt text, sq ft, year opened, description). Script: `scripts/parse_mwpvl_wayback.py` (new file; reruns end to end from the raw folder).
4. Field derivation:
   - city and state: parsed from the address (city = component before the US state name); non-US rows dropped.
   - sq_ft: first number in the square-feet cell (footnote markers dropped); blank for TBD/empty.
   - year_opened: first 4-digit year in the Year Opened cell. `raw_year_text` keeps the cell (month, "Q4 2015", "Planned for 2012").
   - mwpvl_type: a controlled label chosen by keyword matching on MWPVL's description (sortable_fc, non_sortable_fc, sortation_center, prime_now, fresh_pantry, returns, delivery_station, crossdock, specialty, unspecified; joined with `+` for mixed sites). The description prose itself is NOT stored. 'unspecified' is common (31% of rows) because many rows have no type wording.
   - status: heuristic. `planned` if the year/description cell says planned, future, rumour, proposed, TBD, to be opened, under construction, or the opening date is after the snapshot date; otherwise `active` (listed and not flagged). `status_basis` records which rule fired. No row was marked `closed`: the only "closed" wording in text-era snapshots concerned scheduled closures (TUL1, RN01 and the Fernley site replaced by RN02), which are not closures, so those stay `active`.
   - Rows listing several codes in one cell (e.g. "ONT5/ONT7", "IND2 IND3") are split into one row per code, each repeating the shared sq ft; `shared_row=Y`. Square footage on those rows is for the whole building, not per code.
   - US rows with no site code (Prime Now hubs and unnamed sortation sites, 4-10 per snapshot) are skipped and counted in `mwpvl_wayback_snapshots.csv` (`us_rows_no_code`).
5. `mwpvl_wayback_sites.csv`: one row per code. `year_opened` is the earliest year seen when snapshots disagree, with `year_conflict=Y` and all values in `year_opened_all`. `closed_by_snapshot` is set only when the code vanishes from a later text snapshot (`closed_basis=absent_from_later_snapshot`), which is weak evidence: MWPVL also reshuffled and merged rows (for example AVP2/AVP3) and 2012-era lists were incomplete.

## Snapshots (42 fetched; 29 are annual/semi-annual picks, the rest quarterly picks for the text era or probes)
Counts: CDX HTTP-200 captures of amazon_com.html / fetched / parsed as text.
| Year | CDX captures | Fetched | Text-parsed | Image-only |
|---|---|---|---|---|
| 2012 | 8 | 3 | 3 | 0 |
| 2013 | 7 | 4 | 4 | 0 |
| 2014 | 8 | 4 | 4 | 0 |
| 2015 | 22 | 5 | 5 | 0 |
| 2016 | 33 | 6 | 2 | 4 |
| 2017 | 20 | 2 | 0 | 2 |
| 2018 | 24 | 2 | 0 | 2 |
| 2019 | 22 | 2 | 0 | 2 |
| 2020 | 20 | 2 | 0 | 2 |
| 2021 | 18 | 2 | 0 | 2 |
| 2022 | 15 | 2 | 0 | 2 |
| 2023 | 18 | 2 | 0 | 2 |
| 2024 | 19 | 2 | 0 | 2 |
| 2025 | 19 | 2 | 0 | 2 |
| 2026 | 25 | 2 | 0 | 2 |

Text-parsed snapshots (US rows): 2012-06-22 (30), 2012-09-09 (31), 2012-10-05 (32), 2013-01-16 (40), 2013-03-26 (40), 2013-07-04 (48), 2013-10-06 (49), 2014-02-06 (56), 2014-04-24 (57), 2014-07-15 (60), 2014-10-27 (85), 2015-01-18 (86), 2015-04-02 (86), 2015-07-28 (89), 2015-09-09 (90), 2015-10-06 (98), 2016-01-09 (136), 2016-02-24 (151). Full list with Wayback URLs: `data/processed/mwpvl_wayback_snapshots.csv`.
No capture between 2016-02-24 and 2016-03-18 was fetched beyond the three probes; 2016-02-24 is the last snapshot with a text table (2016-03-18 and 2016-03-30 probes are already image-only).

Other pages fetched and checked, none parsed:
- `amazon_com_distribution_network_strategy.html` (captured 2015-11-07 and 2025-05-04): a stale copy of the 2012-06 page (identical 155,660 bytes in both captures, same 43 rows). Content date is not the capture date, so it is excluded to avoid false dating.
- `amazon_building_new_sortation_network.html` (2015, 2018, 2022, 2026) and `amazon_maps.html` (2020, 2022, 2026): no site-code tables (images/prose only). The 2026-05 maps capture is a bot-challenge page.

## Parse coverage
- 18 text snapshots, 1,264 fact rows, 170 distinct site codes (US only).
- Missing fields: sq_ft blank on 31 rows, year_opened blank on 28 rows.
- Status: 1,185 active, 79 planned, 0 closed.
- Never covered: any site first listed after 2016-02 (all of the 2016-2026 build-out) and every site MWPVL does not list.

## Image-only gaps (not OCRed, per instruction)
From the 2016-03/04 captures through 2026-10 the facility tables are PNG images ("Amazon-Distribution-Center-Summary-Table", per-network images). All snapshots from 2016-03-18 onward (fetched: 2016-04-05, 2016-07-08, 2017-01/07, 2018-01/07, 2019-01/07, 2020-01/07, 2021-01/07, 2022-03/07, 2023-01/06, 2024-01/06, 2025-01/07, 2026-01/07) are image-only: 2016 (from March) through 2026 yield no text facts. Text-parseable years are 2012 through early 2016 only.

## Matching to facilities
- Match by `site_code` against `facilities_master.csv` / `facilities.csv` (same 1,761 rows, same codes; compound codes split on space, slash, comma).
- 142 of 170 MWPVL sites match (83.5%), covering 143 master rows (AVP3 appears twice). 28 do not match: AVP6, BOS2, CAE2, DLA1, DLA2, DSF1, EWR6, IND6, JFK7, LCK1, MCI1, MDW1, OAK6, ONT7, PIT1, RN01, RN02, RN04, SDF7, UFL1, UGA1, UNC1, UOH1, UOH2, UTX1, UTX2, UTX5, UWA3 (many are closed, renamed, planned-never-built or Prime Now/hub codes).
- Master `year_basis` of matched rows: first_osha_filing 98, opening_year 25, blank 12, press_opening_year 8.
- Sites with `year_basis=first_osha_filing` that would gain a MWPVL year_opened: 95 rows (94 distinct codes; 89 rows have latest MWPVL status active, 6 still `planned` at the last text snapshot: BDL5, CMH1, MDW2, MIA1, MKE2, SAT1, so their year is a projection). 6 of the 95 have conflicting years across snapshots (use `year_opened_all`). 3 more first_osha_filing rows matched but MWPVL gave no year. The first OSHA filing year (2016-2021) is never earlier than MWPVL's year for these rows (OSHA data start 2016).
- Agreement check on 33 matched rows that already have a press/opening year: 29 equal, 4 differ (BWI1 press 2006 vs MWPVL 2010; MDW6 2017 vs 2015; MSP1 2016 vs 2017; TPA1 2016 vs 2014). MWPVL's dates are announced/estimated and can be a year off; flag these as MWPVL-sourced, keep press years where they exist.

## Conflicts (year_opened differs across snapshots)
BDL1 2014/2015; BWI1 2010/2014/2015; BWI5 2014/2015; EWR6 2013/2014; FTW1 2015/2016; ONT7 2013/2014; RIC3 2012/2014; SDF4 2005/2012; SDF6 2011/2012; SDF7 2005/2012; UFL1 2014/2015. Most are planned dates that slipped (the later value is usually the real opening) or a row restated when MWPVL merged codes. The sites file uses the earliest value and flags the conflict; the integrator should prefer the latest value for sites that were `planned` at the earlier snapshot.

## Caveats
- MWPVL years are MWPVL's own reporting (sometimes projected); treat as secondary to press releases.
- Types and statuses are keyword heuristics on short descriptive text; verify before using type as an analytic category.
- Sq ft on `shared_row=Y` rows is for the combined building.


## Local OCR cross-check

Independent third read of the archived MWPVL table images with a local model, to cross-check the Claude double-entry transcription (`data/processed/mwpvl_wayback_image_facts.csv`).

- **Model**: Unlimited-OCR-2-4bit, in-process via mlx_vlm (`dean_thesis/.venv_unlimited`), prompt "Multi page parsing.", temperature 0, max_tokens 8192. DeepSeek-OCR-8bit was **not run**: the oMLX server was not running and there is no documented routine start step, so the plan was Unlimited only. The cross-check is therefore one local model against Claude, not two.
- **Images**: 172 table images read (index.csv minus 20 summary tables). Whole-image read for 117; 55 tall images hit the token cap or looped and were re-read as 1000 px strips with 80 px overlap (overlap duplicates removed in parsing). No errors. 32 images (the 2018 map set, `2018-USA-Amazon-*`, 2018 to 2020 snapshots) are US point maps, not tables, and yield no rows; they cannot be read by OCR.
- **Timing**: 50.9 s per image on average (whole images 7.9 s; tiled images 142 s). Total 8,753 s. Raw outputs: `data/raw/mwpvl_wayback/ocr_local/Unlimited-OCR-2-4bit/<image>.md` + `timing.jsonl`.
- **Scripts**: `scripts/mwpvl_local_ocr.py` (run), `mwpvl_local_ocr_parse.py` (to `data/processed/mwpvl_wayback_image_facts_localocr.csv`, 15,352 rows from 140 images), `mwpvl_local_ocr_compare.py`.
- **Alignment**: per image, a Claude row is matched to an OCR row by site code (a code within the OCR code cell, so shared-code rows match), else city+state+sq_ft, else city+state. 16,067 of 16,638 Claude rows matched (571 unmatched, mostly rows OCR dropped or cut at strip joins). Sq_ft normalised for commas, year_opened to the 4-digit year ("Q2 2022" = "2022"), city lower-cased letters only.
- **Agreement with Claude (matched rows)**: site_code 98.2%, city 90.5% (mostly address-parsing differences, e.g. "Cordova, Memphis"; city is the least informative field here), state 99.6%, sq_ft 98.8%, year_opened 98.7%; overall 97.1% of 80,335 cells. Per image: median 97.6%, 22 of 140 images at 99% or better, lowest 86.9%. Lowest: 20170116114556__Amazon_Sortation_Center_Netwo (139/160), 20190701022302__Amazon-Sortation-Center-Netwo (252/290), 20220701183828__Amazon-Delivery-Station-Netwo (213/245), 20180713165546__Amazon-Delivery-Station-Netwo (200/230), 20220307202113__Amazon-Delivery-Station-Netwo (158/180).
- **Disagreements**: 2,295 cells in `data/processed/mwpvl_ocr_disagreements.csv` (city 1,529, site_code 291, year_opened 207, sq_ft 195, state 73). With a single local model, "models agree" is not testable, so every Unlimited-vs-Claude disagreement is listed (column `match_basis` shows alignment reliability: `code` is reliable; `city_state*` less so).
- **Decisions**: 40 highest-impact cells (32 year_opened, 8 site_code; 44 CSV rows because shared-code rows share a key) were checked by viewing a crop of the row from the image. Result: in all 30 cells where the row was visible, **Claude was right and the local OCR wrong** (typically adjacent-row shifts in year, or letter/digit swaps such as UWA1 read as UVA1, ONT5 as ONTS, KBOI as KB01). 1 more was supported by a partial view. 9 could not be settled because the estimated crop window missed the row (no pixel coordinates were available); those are marked unresolved and Claude's value was not contradicted. No edits were made to the Claude file.
- **Conclusion**: no evidence of Claude transcription errors in the sampled cells; the remaining ~2,255 undecided cells are dominated by local OCR errors and city-parsing differences and have not been reviewed.

## Image-era transcription (2016-03 to 2026-01), added 2026-10-31
This section supersedes "Image-only gaps" above: the image tables are now transcribed.
Script: `scripts/mwpvl_image_reconcile.py` (new file, stdlib only). It reads `data/raw/mwpvl_wayback/transcriptions/passes.json` (both transcriptions of every image) and `adjudications.json` (every decision with its basis and evidence), then writes `mwpvl_wayback_image_facts.csv` and `mwpvl_wayback_sites_all.csv`.

### Method: double entry plus adjudication
1. Two Claude agents transcribed each image independently (pass A and pass B), reading zoomed tiles.
2. The passes were aligned row by row in table order, keyed on site code (or city when there is no code). They were compared after normalising formatting: state name vs abbreviation, "-" vs blank square feet, commas, and word order in the city.
3. Rows where every field matched are `agreed`.
4. Differences only in description wording are `adjudicated` by rule (`rule:description_union`). The usual case was one pass condensing or dropping a clause. The two readings are merged, and type and status are derived from the union.
5. Differences only because one city reading names more places are also `adjudicated` by rule (`rule:fuller_city`); the fuller reading is kept.
6. Every other disagreement was settled against the image. The fields involved were site code, square feet, year, a city with different words, a description implying a different facility type, and rows present in only one pass. The basis is recorded per row:
   - `viewed_image_crop` (36 rows plus 6 rows dropped): the row crop was viewed.
   - `vision_ocr_of_cell` (145 rows, almost all city choices): decided from a macOS Vision OCR read of that cell. The text-era city rule applies: the place name just before the state in the address. PIT5, RIC2, MDW2, LAX5 and others were spot-checked by eye.
   - `merged_description_text` (48 rows): the cell holds both readings. This was confirmed on crops of SCA4, DCS4/HCO1 and WML1, for example "Mini Fulfillment Center / Amazon Fresh / Delivery Station".
7. Cross-checks after reconciliation:
   - Every agreed row with a code was compared with a Vision OCR read of the same image: 8,488 rows were located, and their sq ft and year were checked. One correlated error was found and fixed: UCA6 in 2026-01, where both passes read 37,000 and the image shows 37,800 (`vision_ocr_cross_check_of_agreed_rows`). The other 179 mismatches were OCR column bleed.
   - The 2025-01 and 2026-01 images are byte-identical, so four independent passes read the same tables. 1,795 of 1,804 rows match on table, code or city, sq ft and year. Of the 9 that differ, 8 are codeless rows with different city wording and 1 is UCA6.

### Problems found in the passes (fixed)
- Two passes transcribed the wrong image: pass A of 2020-01 FC and pass B of 2021-01 FC both contain the 186-row 2020-01 delivery-station table, probably from a tile folder shared with another agent. For those two images the single valid pass is used: 2020-01 FC from pass B (211 rows) and 2021-01 FC from pass A (300 rows). Each was checked against a Vision OCR read, and 6 rows were also checked on crops. Basis: `single_valid_pass_checked_vs_vision_ocr`, 511 table rows.
- Pass A of 2016-04-05 FC carried in rows from the 2016-07 table: ABE8, LGA8, CHS1, FTW4, plus EWR8/EWR9 and LGA7 values. Pass A of 2018-07 FC added a "Dallas Q4 2020" row from 2019-01. The 5 phantom rows were confirmed absent from the images and dropped.
- 20 exact duplicate rows inside one image were dropped; MWPVL repeats some rows (DSM4, for example).

### Counts
- Images: index.csv lists 192.
  - 20 are summary tables (not transcribed).
  - 8 are 2020-01 "2018-USA-*" map images, identical to earlier captures (not transcribed).
  - 164 were double-entered. 24 of these are US maps with dots and no table, so 140 table images yielded rows.
- Table rows: 14,828. Of these, 9,986 are agreed (67%), 4,841 adjudicated and 1 flagged.
- The adjudicated rows by basis:
  - rule:description_union: 3,705
  - rule:fuller_city: 282, plus 113 that are both
  - single_valid_pass: 511
  - vision_ocr_of_cell: 145
  - merged_description_text: 48
  - viewed_image_crop: 36
  - OCR cross-check: 1
- Content disagreements needing image adjudication: 235 rows. By field: 147 city, 53 type-changing description, 11 year, 7 site code, 7 one-pass-only rows, 5 sq ft, plus a few rows with more than one field.
- Fact rows (multi-code cells split one row per code, `shared_row=Y`; `code_cell` keeps the original): 16,638. Of these, 15,072 have a code and 1,566 are codeless (planned or unnamed sites, kept in the image facts but not in the site file).
- Flagged cells: 1. The Charlton, MA row (2021-07 FC, no code) reads "Q1 2923" in the image, a source typo; year_opened is left blank. No cell was unreadable.

### Images not found / not usable
- None missing. Every US table image linked from an in-range snapshot had a Wayback capture; archive.today was not needed.
- Table types absent from the page, not archive gaps:
  - 2016: no food, whole_foods, crossdock, air_hub or heavy_bulky.
  - 2017: no whole_foods, crossdock, air_hub or heavy_bulky.
  - 2018–2019: no air_hub or heavy_bulky.
  - 2020: no heavy_bulky.
- Same-digest captures were skipped:
  - 2022-07-01 has no FC image, because it is identical to 2022-03.
  - 2022-07-01 has only Part 2 of the delivery-station list.
  - 2023-06, 2024-06, 2025-07 and 2026-07 are identical to the January captures.
- Mislabelled or stale files:
  - `20220307202113__Amazon-Food-Distribution-Center-Network-in-USA_1.png` actually holds an FC table (812x23718). Its rows carry `table_type=fc`, and there is no 2022-03 food table.
  - The 2017-07-13 delivery-station image is byte-identical to the 2016-03-30 one (stale).
  - **Every 2026-01-17 image is byte-identical to its 2025-01-19 capture.** MWPVL's tables were last updated between 2024-01 and 2025-01. Treat 2025-01-19 as the last real data date; a 2026 `last_snapshot` adds no information.
- Not downloaded by design: rest-of-world tables (`images/_row_excluded/`) and the 2015 North America map images.

### Image facts columns (`mwpvl_wayback_image_facts.csv`)
- Per row: snapshot_ts, snapshot_date, year, table_type, image_name, row_in_image, site_code, code_cell, shared_row, city, state (2-letter), sq_ft (integer), year_opened (4-digit), raw_year_text, status, status_basis, mwpvl_type, type_label, transcription, adjudication_basis, adjudication_note, image_url (the archived `im_` URL).
- city is as printed, typos included: "Pittsburg", "Bueno Park", "Fort Meyers", "Joilet".
- `type_label` is the description text, the union of both readings. These are facts used for typing; do not republish it as prose.
- `mwpvl_type` uses the text-era keyword classifier, extended with air_hub and IXD.
- `status` is a heuristic, relative to the snapshot date:
  - planned: an opening date after the snapshot, "not yet confirmed"/TBD/"no ETA", or a project codename with the current or a future year.
  - delayed: a delay remark, with the site not yet open.
  - on_hold: on hold, paused, "delayed indefinitely" or "may be cancelled".
  - sublease: put up for sublease.
  - cancelled: cancelled, not revived.
  - closed: closed. Clauses about another code or a building's former use are ignored, for example "replaces AVP6 which was closed" or "site of the Century Plaza closed in 2009".
  - active: otherwise.
- MWPVL never marks a listed Amazon site as closed. DLA2's "Closed June 2017; reopened" is read as active. Closures show only as rows that disappear.

### Merged site file (`mwpvl_wayback_sites_all.csv`)
- One row per site code across the text era (18 snapshots, 2012-06 to 2016-02) and the image era (20 snapshots, 2016-03 to 2026-01). There are 1,749 codes: 170 from the text era and 1,579 first seen in images.
- Codes "RN04" and "DB01" are normalised to RNO4 and DBO1, since codes are 3 letters plus a digit.
- Columns:
  - first_snapshot / first_era, last_snapshot / last_era, and n_snapshots.
  - year_opened, with year_opened_all, year_sequence and year_resolution.
  - latest_sq_ft (the most recent non-blank value), latest_status and status_history.
  - latest_city, latest_state, latest_mwpvl_type and type_history (changes only).
  - image_tables.
  - absent_from_snapshot: the first later capture of the same table type that lacks the code. This is weak evidence of closure. Stale and partial captures are skipped. Some "dropped" codes reappear inside another row's description (CLE9, DCH9, DLX2, and LAS5, which was converted to an IXD).
  - master match columns.
- Rule for year_opened:
  - One value per snapshot. When it changes and the earlier snapshot called the site planned, delayed or on hold, the later year wins (`later_year_after_planned`, 55 sites).
  - Any other change is flagged (`year_conflict=Y`, 274 sites) and resolved to the value MWPVL printed in the most snapshots, ties going to the later one (`conflict_modal_value`).
  - Conflicts are mostly bare years that slipped without a "planned" remark, plus code reuse. MDW6 was a Chicago sortation center in 2016 and the Romeoville FC from 2017. BWI1 shows six different years.
  - `year_is_projection=Y` when the chosen year was only ever stated for a site not yet open.
- Latest status counts: 1,695 active, 34 planned, 16 delayed, 3 sublease, 1 on hold.

### Match to facilities_master.csv
- Match by site code: **1,418 of 1,749 MWPVL codes match (81.1%)**, covering 1,428 master rows.
- Of the 331 unmatched codes, 191 are still listed in 2025/26. These are mostly delivery stations (D*), Fresh codes (F*), Prime Now (U*), 3PL (X*), ICAO air-hub codes (K*) and heavy-bulky codes (H*).
- **1,327 master rows (1,317 codes) with `year_basis=first_osha_filing` gain an MWPVL year_opened**, up from 95 with the text era alone.
  - Compared with the first OSHA filing year: 853 are the same year, 398 have an earlier MWPVL year (mostly sites opened before OSHA ITA data begin in 2016), and 76 have an MWPVL year one year later.
  - 14 of the 1,327 are projections, and 188 have conflicting years across snapshots; check `year_sequence` before using them.
- Agreement where the master already has a year:
  - opening_year: 26 of 26 equal.
  - press_opening_year: 27 of 31 equal. The exceptions are TPA1 (press 2016 vs MWPVL 2014), MDW6 (2017 vs 2016), PDX7 (2018 vs 2019) and BWI1 (2006 vs 2013, a reused code).

### What the image era shows
- Listed US rows per capture grow from 171 (2016-03) to 1,005 (2021-01), 1,295 (2021-07) and about 1,500 to 1,600 from 2023.
  - 2022-03 shows 1,793 rows because its FC table appears twice.
  - 2022-07 is partial.
- Opening years in the site file peak in 2021 (382 sites) and 2020 (346). They then fall: 125 in 2022, 102 in 2023, 84 in 2024 and 36 in 2025.
- **The 2022–23 pullback is visible in the status text.** Rows flagged delayed, on hold, sublease or cancelled went from 1 per capture through 2021-07, to 27 in 2023-01, 45 in 2024-01 and 40 in 2025-01. The 2026-01 count (23) falls only because the same text is re-read against a later snapshot date; the images are identical. Examples:
  - "Opening delayed indefinitely" (Porter Ranch, Houston).
  - "Project Paused" (San Francisco SoMa).
  - "Project may be cancelled" (Rochester sortation).
  - "Building put up for sublease" (DGI1 New Castle DE, DHX8 Houston, Pinellas Park).
  - "Cancelled in 2023-Dec. Revived in late 2024" (Rockville, Project Rocky).
  - Many "Project delayed 1–2 years" FC and IXD rows: ELK1, SAT3, TYS1, BNA6, LAN2 and RDU4.
- Codes that vanish from later captures (absent_from_snapshot): 36 in 2023-01, 29 in 2024-01 and 51 in 2025-01.
  - The 2025-01 drops include the 3PL non-sortable FCs XUSB, XUSC, XUSE and XLA3, older Prime Now hubs (UCA1, UCA4, UIL1, UMA3, UNV1), several Z*/X* rural delivery stations, and the CVG3 IXD.
  - Treat these as removals from MWPVL's list, not confirmed closures.
- No listed Amazon site is marked closed in the image era. The only own-site closure text is DLA2 (closed June 2017, reopened). Other closure mentions concern replaced sites: AVP6 (closed July 2016, replaced by AVP8) and CHS1 (closed Feb 2017, replaced by CAE3).

### Caveats
- MWPVL figures are its own estimates; they are often projected and sometimes reuse codes.
- Status and type are keyword heuristics.
- City is the place name just before the state; where an address names two places, the other is lost. Use `code_cell` and `type_label` for detail.
- The Vision OCR used here is a locator and third reading, not a published source.

## Outside check of BWI2 and DCA1 (2026-10-31)
Method: browser searches (scripts/browser_search.py) for each site, then the article pages were opened. The MWPVL CSVs were not edited; differences go in `data/processed/mwpvl_corrections.csv`.

### BWI2 (Baltimore, MD; 2010 Broening Highway)
- MWPVL (`mwpvl_wayback_sites_all.csv`): year_opened 2015, latest 1,017,600 sq ft, sortable FC. The 2014-10-27 capture lists it as "Planned for 2015"; captures from 2015-09 onward say "March 2015".
- Outside sources agree with 2015:
  - Baltimore Sun, 2015-07-30, "Amazon hiring outpaces projections": the caption says Amazon opened a one million sq ft fulfillment center on Broening Highway on March 30 (2015).
  - AP via Washington Times, 2015-09-29, "Amazon opens new fulfillment center in Baltimore": grand-opening ceremony at the 1 million sq ft center on 2015-09-29.
  - Baltimore Business Journal, 2014-07, "Amazon comes to Baltimore to talk warehouses, hiring" (search snippet only): center "scheduled to open next spring".
- Why trade press may say 2014: the project was announced and the building was under construction in 2014 (the Baltimore Business Journal piece is dated 2014-07). No source found that says it opened in 2014.
- Result: MWPVL year 2015 is confirmed (physical opening 2015-03-30, ceremony 2015-09-29). No correction. The 2014-10 capture's 345,000 sq ft "sortation_center" row under this code is an earlier, smaller plan; the 2015+ captures show about 1.0 million sq ft, matching press.
- A Daily Record item (2015-01-28) says a much smaller Amazon facility, also on Broening Highway, opened in Baltimore shortly before; this may explain the early 345,000 sq ft entry. Not resolved.

### DCA1 (Sparrows Point, MD; 1700 Sparrows Point Boulevard)
- MWPVL: year_opened 2018, latest 855,000 sq ft, sortable FC, city written "Sparrow's Point". JFK8 (Staten Island) is also 855,000 in MWPVL.
- Outside sources agree DCA1 is 855,000 sq ft, so the identical figure is a coincidence, not a copied value:
  - REBusinessOnline, 2017-11-09, "Amazon to Open 855,000 SF Fulfillment Center in Baltimore's Sparrows Point".
  - Technical.ly (2018) states 855,000 sq ft; the page itself was blocked from automated fetch, so only the search snippet was seen.
  - Baltimore Business Journal, 2018-08-21: 855,000 sq ft warehouse "soon to open" in Dundalk; Baltimore Magazine, 2018-10-09: new Sparrows Point center open.
  - CoStar headline: 855,514 sq ft.
  - Dundalk Eagle gives 850,000 sq ft (rounded).
- JFK8 is also reported at 855,000 sq ft by Newsday and amNY, so both MWPVL values are consistent with press.
- Result: sq ft and opening year confirmed. Only difference is the apostrophe in the city name ("Sparrow's Point" for "Sparrows Point"), recorded as a presentation correction.


## Second local OCR model and three-way check (DeepSeek-OCR-8bit), added 2026-11-01
This supersedes the "DeepSeek-OCR-8bit was not run" statement in "Local OCR cross-check" above. It adds a second local reader so that Claude disagreements can be filtered to cells where BOTH local models disagree with Claude. The Claude file (`mwpvl_wayback_image_facts.csv`) is not edited.

### Method
- **Server**: oMLX was already running on 127.0.0.1:8000 (`omlx-server`, pid started 2026-10-31 16:03, installed in the shared oMLX venv; other start routes in the logbooks: `/Applications/oMLX.app/Contents/MacOS/omlx-cli serve --model-dir ~/.omlx/models`). Nothing had to be started or installed; the earlier "server down" was a stale state. API key read from the OMLX_KEY environment variable (the local server key, not stored in the repo). Model served: DeepSeek-OCR-8bit, 8192 context.
- **Run**: `<omlx venv>/bin/python -I scripts/mwpvl_local_ocr.py --model DeepSeek-OCR-8bit` (the `--model` flag is new; the default is still Unlimited-OCR-2-4bit and that path is unchanged). Prompt `<|grounding|>Convert the document to markdown.`, temperature 0, max_tokens 8192, concurrency 1. Whole image first; strips (1000 px, 80 px overlap) when the output hit the token cap, looped, was empty, or oMLX's memory guard refused the whole image. Raw output: `data/raw/mwpvl_wayback/ocr_local/DeepSeek-OCR-8bit/<image>.md` and `timing.jsonl`.
- **Problems met and how they were handled** (all visible in timing.jsonl, which keeps every attempt, 306 lines for 172 images):
  - oMLX returned HTTP 400 "prefill memory guard rejected this prompt" from about the 2019-07 snapshot on. The server's resident memory crept up between calls (it estimates about 11 GB of KV for any request against a 14 to 16 GB ceiling). Unloading the idle model through `POST /v1/models/DeepSeek-OCR-8bit/unload` reset it, and the script now does that and retries (the 400 calls had wrongly left empty .md files; the script no longer writes a file on error and redoes empty ones).
  - 18 whole-image reads returned a short non-table answer (18 tokens) or dropped more than 10 percent of the rows. Those were re-read in strips; the first-pass files are kept as `<image>.md.firstpass`.
  - 2018 map images (24) have no table; DeepSeek returns about 17 tokens, as Unlimited did.
- **Timing**: 44.4 s per image over the 172 final records (7,639 s in total): 92 whole-image reads at 3.9 s, 80 strip-tiled reads at 91 s. That is faster than Unlimited (50.9 s per image, whole 7.9 s, tiled 142 s).
- **Parse**: `scripts/mwpvl_local_ocr_parse.py` now also writes a `location` column (the OCR address) and reads both model folders; `mwpvl_wayback_image_facts_localocr.csv` holds both models (31,531 rows: 15,523 Unlimited plus 16,008 DeepSeek). `mwpvl_local_ocr_compare.py` now filters to Unlimited, so the single-model numbers above still reproduce (2,294 vs 2,295 cells because the model filter excludes nothing else).
- **Three-way compare**: `scripts/mwpvl_ocr_3way.py`. The alignment of a Claude row to an OCR row is the same as before (code, else city+state+sq ft, else city+state), done separately per model. Normalisation added this time:
  1. City: a parenthetical qualifier is stripped on both sides ("Miami (Doral)" = "Miami"); a Claude city that appears as a comma-separated part of the OCR address is counted as `format`, not a disagreement.
  2. Year: an OCR year cell that is a number above 10,000 is a `column_shift` (square feet read into the year column), not a disagreement.
  3. Cells are collapsed to DISTINCT (site_code, field, claude value, OCR value) combinations.
- Outputs: `data/processed/mwpvl_ocr_3way.csv` (7,245 cells where at least one model differs from Claude, with a category), `mwpvl_ocr_3way_flags.csv` (the distinct short list, 384 rows), `mwpvl_corrections_ocr.csv`. Settling script: `scripts/mwpvl_ocr_3way_settle.py`. Evidence crops: `data/raw/mwpvl_wayback/ocr_local/evidence_crops/` (61 PNG).

### Counts before and after normalisation (cells disagreeing with Claude)
| Model | before (old rules) | after (new rules) | note |
|---|---|---|---|
| Unlimited | 2,294 of 80,335 | 1,692 (1,665 disagree + 27 column shift) | city 1,529 to 920 |
| DeepSeek | 3,635 of 79,875 | 3,042 | |
Distinct (site_code, field, claude, ocr) combinations: Unlimited 1,082 (from 1,665 cells); DeepSeek 2,175 (from 3,041 cells).

### Agreement with Claude, per field (after normalisation, matched rows; Unlimited n=16,067, DeepSeek n=15,975)
| Field | Unlimited vs Claude | DeepSeek vs Claude | Unlimited = DeepSeek | all three agree |
|---|---|---|---|---|
| site_code | 98.2% | 95.9% | 94.7% | 94.6% |
| city | 94.3% | 93.9% | 96.4% | 92.4% |
| state | 99.6% | 99.4% | 99.1% | 99.0% |
| sq_ft | 98.8% | 96.5% | 95.5% | 95.4% |
| year_opened | 98.7% | 95.2% | 94.6% | 94.3% |
The last two columns use the 15,674 Claude rows matched by both models. DeepSeek is the weaker reader (it often drops the year cell or reads the next row). 571 Claude rows have no Unlimited match, 663 no DeepSeek match.

### Cells where both local models agree with each other and differ from Claude
| Field | cells | distinct cases |
|---|---|---|
| year_opened | 38 | 32 |
| site_code | 20 | 17 |
| sq_ft | 9 | 6 |
| state | 10 | 6 |
| city (lower priority, not settled) | 631 | 323 |
The first four fields give 61 distinct cases (under the 120 cap), all settled. The city cases are mostly address-parsing differences and were not reviewed.

### Decisions (crop of the row viewed; rows above and below shown)
All 61 cases: 59 `claude_correct`, 2 `ocr_correct`, 0 `unreadable`.
- The two models agree with each other for correlated reasons, not because they are right: both read the adjacent row's year (16 cases), both dropped the year cell and returned the description or another cell (16 cases, mostly the 2023-01 delivery-station list), both share the same letter/digit confusion (BFI9 as BF19, MCI8 as MC18, UWA1 as UVA1, MSP5 as MSPS, DLI4 as DIL4), both ignored that a shared code cell was split into one row per code by Claude (HLA2/HLA8, ABE1/ABE2, FTW7/FTW9, LAX6/ULA6) or invented a code for a row whose code cell is blank (Fort Worth rows read as FTW3/FTW4, Los Angeles Prime Now as UCA10). sq_ft: both read a different row (Fort Worth, DET1, ONT7) or the placeholder "TBD" (IND7, kept blank).
- The 2 `ocr_correct` are one normalisation, not a transcription error: the 2021-07 to 2022-07 Sortation table prints the state as "Aizona" (a source typo) for AZA9 and TUS5; Claude copied it, the OCR returns AZ. The value is wrong as a state; `mwpvl_corrections_ocr.csv` lists all 6 cells with this typo (AZA9 x3, TUS5 x2, one codeless Tucson row) as Aizona to AZ. The build can apply it later; the Claude file is untouched.
- Conclusion: no transcription error in Claude's year_opened, site_code, sq_ft or state was found among the 61 cases where both local models disagreed with it. Note that a single state value, "Aizona", is invalid and should be normalised.
- Caveat: only the first occurrence of each distinct case was viewed; where a case spans several snapshots (n_snapshots in the flags file) the decision is applied to all of them on the assumption that the same table row repeats. Rows that only one model disagreed on (about 2,000 distinct cells) were not reviewed.
