# Facilities roster notes

Output: `data/processed/facilities.csv` (1,761 rows, 1,749 distinct site codes; was 1,701 before the 2026-10-31 name-rule and geography review). Built by `scripts/facilities_01..07_*.py` (run with `python3 -I`). Retrieval date for all sources: 2026-10-31. No JHU subscription sources were used.

## Sources
| Source | Publisher | URL | Used for | Caveats |
|---|---|---|---|---|
| OSHA ITA Form 300A establishment data CY2016-2025 (2025 file runs through 2026-08-31) | US OSHA | https://www.osha.gov/Establishment-Specific-Injury-and-Illness-Data | Backbone: site code, address, NAICS, years filed | Only establishments required to file appear. Form 300A electronic submission has covered NAICS 4931 (warehousing) sites with 20 or more employees since the 2016 data year; the 2019 and 2023 rules changed only Forms 300 and 301. 2016 data were collected late and compliance was low in the first years, so a first filing year is a LOWER BOUND on opening, not the opening year. Absence from 2025 is not proof of closure. Names are free text typed by Amazon. |
| TaxJar "Where are the Amazon fulfillment centers" | TaxJar (blog.taxjar.com), page modified 2025-10-29 per page metadata | https://blog.taxjar.com/amazon-warehouse-locations/ | 67 sites not in OSHA data; county; FC type corroboration | Third-party compilation, no per-row dates, some "seasonal" and legacy entries. |
| TaxJar "Where are all Amazon sort centers" | TaxJar | https://www.taxjar.com/blog/amazon-sort-centers-locations | Sort-center type labels (63 listings) | Same. |
| MWPVL International, Amazon article, legacy table "as at April 2012" | MWPVL International | https://mwpvl.com/html/amazon_com_distribution_network_strategy.html | Opening year and sq ft for 30 large US FCs (1997-2011), 1997-99 history | Only 30 large US sites; sq ft is the 2012 estimate (excludes later expansions). MWPVL states it no longer posts updates online and sells current data commercially; we used only the facts (code, year, sq ft) with attribution and did not use or transcribe their current image tables. |
| MWPVL intro text | MWPVL | https://www.mwpvl.com/html/amazon_com.html | Seattle 1997 (93,000 sq ft), McDonough GA opened 1999 and closed 2001 | City level only. Also states 123+ buildings closed, canceled or delayed in 2022-23. |
| US Census Bureau geocoder (batch API, Public_AR_Current) | US Census | https://geocoding.geo.census.gov/geocoder/ | lat/lon, county FIPS | See geo_method. |
| Census 2020 ZCTA gazetteer and ZCTA-county relationship file; national_county2020.txt | US Census | https://www2.census.gov/geo/docs/ | ZIP-centroid fallback, county names | Centroid is approximate. |

Raw files: `data/raw/facilities/` (OSHA zips and extracted CSVs in `osha_ita/` are about 0.5 GB, gitignored; `osha_amazon_rows.csv` is the filtered extract).

## Method
1. From all OSHA 300A rows, keep rows that `scripts/amazon_names.py` classifies as Amazon (Amazon.com Services LLC and the .dedc/.kydc/... entities, Amazon Retail LLC, Golden State FC LLC, Prime Now LLC, Amazon's own site labels; full rules in `data/notes/injuries.md`). Contractors that merely mention Amazon (janitorial, security, DSPs, including DSPs filed under an Amazon-like company name), Amazon Environmental Inc. and Amazone USA Inc. are excluded. Stores (Go, Fresh), robotics, corporate, Kuiper/Leo and AWS rows are excluded from the roster by the establishment-name and NAICS filters.
2. Site code = last code-like token in the establishment name (`[A-Z]{3,4}\d{1,2}`, or `K` + 3 letters for air hubs). Records for one code are clustered by street number, ZIP, or city so that typos merge but genuine relocations (about 11 codes, for example DBL8, HDT2) stay as separate rows.
3. Latest filing gives the address. Types and confidence below.
4. TaxJar and MWPVL rows are added when their code is not already present; where it is present they corroborate the type and supply county, opening year and sq ft.
5. Census batch geocode (966 exact, 290 non-exact, 475 via ZIP centroid, 30 unlocated). Hand corrections for OSHA typos are in `data/processed/facility_geo_overrides.csv` (each with a reason) and applied by `facilities_03_build_roster.py` before geocoding. Then `facilities_08_check_geo.py` tests every located row (geocoded point inside the row's state polygon, ZIP belonging to the state).

## Type classification (column type_basis says which rule applied)
- `air_hub`: OSHA name is a 4-letter ICAO code starting with K (KCVG, KBWI, ...). 10 rows.
- `sort_center`: on TaxJar sort list, or OSHA/code heuristics (prefix S). 
- `fulfillment_center`: Amazon's own org label in the OSHA name ("North America Fulfillment Centers (FCs)", "Global Specialty Fulfillment"), TaxJar FC list, or NAICS 493110 fallback.
- `delivery_station`: OSHA org label "AMZL" or NAICS 492110 with code prefix D/H/V/U (heuristic, low confidence).
- `other_logistics`: NAICS 492110 courier sites whose code prefix does not tell delivery station from sort center (280 rows). Honest unknown.
- `returns_center`, `cross_dock`: NOT identifiable from these sources; no rows carry these types.

## Confidence
high: OSHA filing 2023+ AND type from Amazon's own label or two sources. medium: single-source type from a label/list, or high downgraded for non-exact geocode. low: heuristic type, TaxJar-only/MWPVL-only rows, or ZIP-centroid location. Of 1,761 rows: 315 high, 436 medium, 1,010 low.

## Columns of note
- `opening_year`: populated for only 30 rows (MWPVL, 1997-2011). All others blank on purpose. `first_osha_filing_year` is a lower bound only.
- `closing_year`: only McDonough GA (2001). `status` shows `in_2025_osha_filing` (1,336 rows) vs `not_in_2025_osha_filing` (357): an indicator, not a verified closure.
- `sq_ft`: 31 rows only.
- `county`: Census FIPS for matched rows; ZIP-to-county (largest overlap) for centroid rows; TaxJar for its rows.
- `geo_method` and `geo_note` document how each coordinate was obtained.

## Known gaps and risks
- Opening years and square footage for the roughly 1,650 other sites (and anything after 2012) are missing. Candidates not yet tried: Amazon press releases per site, county/state incentive records, Good Jobs First Subsidy Tracker (HTTP 403 to scripted fetch, may work via a browser), local news, MWPVL's commercial XLSX (paid), SEC 10-K properties (aggregate only).
- Sites that closed before 2016 (OSHA ITA starts 2016) or small sites not required to file are missing; the roster is stronger for 2020 onward. Pre-2012 history is covered only by 30 large FCs plus 2 anchors.
- Counts of filing establishments by year are a lower bound on network size, not a measure of growth by themselves: 2016 data were collected late and compliance was low in the first years. Rule changes do not explain the growth (300A has covered NAICS 4931 sites with 20+ employees since 2016 data).
- Delivery stations are probably under-covered before 2020 and sub-100-person sites in 2016-2019.
- Type heuristics for about 700 low-confidence rows may be wrong, especially DS vs sort vs other.
- 475 rows have ZIP-centroid, not street-level, coordinates (new-construction addresses are absent from TIGER); 30 rows have none (12 US rows whose full address the parser left in the street field, 16 Canadian rows, 2 city-only historical anchors).
- Geography check (added 2026-10-31): 0 hard failures and 2 near-border notes among the 1,731 located rows. Before the fixes the same check found 9 failures: TTN3 (ZIP 33837 is Florida; Cranbury NJ is 08512), DNY1 (Elizabeth NJ row had ZIP 90065, a Los Angeles ZIP, and city New York; corrected to 630 Sullivan Rd, Elizabeth NJ 07201 rather than dropped, because it is a different building from the other DNY1 row, a 2017 Manhattan filing placed at a ZIP centroid), HLI1 (state AZ, really Maumelle AR), CNM1 (state MP, really Albuquerque NM), CKS1 (state KS, but ZIP 64112 and 301 E 51st St are Kansas City MO), and CVG8, PPA1, POH1, PWA1 (TaxJar rows whose state name was not abbreviated; now KY, PA, OH, WA). The 30 rows without coordinates are listed in `facility_geo_check.csv` as no_coordinates.
- Some OSHA ZIP/state/city fields contain typos; the matched Census ZIP replaced the OSHA ZIP when a street match was found.
- Same site can appear twice if Amazon changed its code (for example a conversion), not de-duplicated by address.
- Whole Foods DCs, Amazon Fresh/Go stores and 3PL/DSP-operated depots are excluded or absent. Prime Now sites (Global Specialty Fulfillment : U..., many small) that carry a site code and a non-store NAICS are now in the roster (added 2026-10-31).
- CMA1 (Boston, 30 Northampton St) was typed fulfillment_center from its OSHA label (Global Specialty Fulfillment) and is now other_logistics: an urban Boston address and not a conventional fulfillment center; its true function is unverified (reclassified at the 2026-10-31 methods review; see `facility_geo_overrides.csv`).
