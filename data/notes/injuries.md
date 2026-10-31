# Workplace injuries: data notes

Retrieval date for everything below: 2026-10-31. Scripts: `scripts/profile_ita.py`, `extract_amazon_ita.py`, `fetch_bls_soii.py`, `build_injury_tables.py` (run with `python3 -I`).

## 1. OSHA Injury Tracking Application (ITA), Form 300A establishment summaries
- Publisher: US Department of Labor, OSHA. Landing page https://www.osha.gov/Establishment-Specific-Injury-and-Illness-Data (redirects to https://www.osha.gov/itadata). Data are public domain.
- Raw files in `data/raw/injuries/` (zips in `cyYYYY.zip`, extracted to `xYYYY/`; CY2025 is a CSV). URLs (all under https://www.osha.gov/sites/default/):
  - CY2025: largefiles/ITA_300A_Summary_Data_2025_through_08-31-2026.csv (PARTIAL: submissions received through 2026-08-31, still being filed)
  - CY2024: files/ITA_300A_Summary_Data_2024_through_12-31-2025.zip
  - CY2023: files/ITA_300A_Summary_Data_2023_through_12-31-2024.zip
  - CY2022: files/ITA-data-cy2022.zip; CY2021: files/ITA-data-cy2021.zip; CY2020: files/ITA-Data-CY-2020.zip
  - CY2019/2018/2017/2016: files/ITA%20Data%20CY%20YYYY.zip
- Coverage: 2016 to 2025 (10 reporting years). Who must file electronically (Form 300A summary): establishments in designated industries with 20 or more employees, which includes NAICS 4931 (warehousing and storage), since the 2016 data year; establishments with 250 or more employees in other industries file as well. The 2019 rule and the 2023 rule changed only the Form 300 and Form 301 (case-detail) requirements, not this Form 300A requirement. So the growth in Amazon filers from 2016 to 2025 reflects network growth and improving compliance, not rule changes. OSHA collected the 2016 data late (the collection opened in mid-2017) and compliance was low in the first years, so 2016 (and to a lesser degree 2017 and 2018) are the least complete years. (Correction 2026-10-31: an earlier version of these notes, the Methods page and several page captions said filing rules widened in 2023 and 2019; that is wrong for 300A and was removed everywhere.)
- CY2016: only 3 Amazon-matched rows (2 manufacturing, 1 `Amazon.com.dedc LLC`). Amazon fulfilment-centre filings are essentially absent from the 2016 file, so no 2016 Amazon warehouse rate is reported. Do not read the 4.19 in 2016 in `injury_comparison_by_year.csv` as an Amazon figure (n=1 establishment).
- Fields kept: establishment_name, company_name, address, city, state, zip, NAICS, industry description, annual average employees, total hours worked, deaths, DAFW cases, DJTR cases, other recordable cases, DAFW days, DJTR days. Individual-level case detail files were NOT downloaded (no personal data).

### Name-matching rules for Amazon-affiliated establishments (final, from the 2026-10-31 methods review)
Implemented once in `scripts/amazon_names.py` and used by `extract_amazon_ita.py`, `build_injury_tables.py`, `facilities_01_osha_extract.py`, `facilities_03_build_roster.py` and `logistics_01_osha_site_counts.py`. The rule label of every matched row is in the `match_rule` column of `osha_ita_amazon_establishments.csv`. A row is Amazon if:
1. `company_name` starts with `Amazon.com` (Amazon.com Services LLC / Inc., Amazon.com.dedc / kydc / indc / azdc / ksdc / nvdc LLC and typo variants): 7,304 rows. Rule `company_amazon.com`.
2. `company_name` starts with `Amazon Retail` (Fresh, Go and other Amazon stores, mostly NAICS 445): 269 rows.
3. `company_name` starts with `Golden State FC LLC` (Amazon's California fulfillment entity, filings for 2017 and 2018): 51 rows (21 in CY2017 and 30 in CY2018). The raw files hold 25 CY2017 and 30 CY2018 rows containing "Golden State FC"; the other 4 CY2017 rows are ABM (a janitorial contractor) filings at OAK3 and OAK4, which are excluded.
4. `company_name` is `Prime Now LLC` (Amazon's one-to-two-hour delivery subsidiary; sites labelled `Global Specialty Fulfillment : U..`, 2017 to 2025): 557 rows, of which most are small grocery-type sites coded NAICS 445. Found by searching the raw files for Amazon organisation labels and by EIN 813530904.
5. `company_name` starts with `Amazon Leo`, `Amazon Kuiper`, `Amazon Project Kuiper` or `Amazon Web Services`: 21 rows (not logistics; they only enter the all-NAICS Amazon figure).
6. `company_name` is bare `Amazon` (any case) AND the EIN is blank or an Amazon EIN (91-1646860 Amazon.com Inc., 82-0544687 Amazon.com Services LLC, 71-0933087, 91-2172399 Amazon Retail), and a blank-EIN row with a courier NAICS (492) must say "Amazon" in its establishment name: 17 rows (Robotics BOS12 and BOS13, PDX7, LAX43, SEA124 ...).
7. `company_name` is blank AND the establishment name carries one of Amazon's own organisation labels with a site code (`North America Fulfillment Centers (FCs) : XXX9`, `Global Specialty Fulfillment : ...`, `AMZL : ...`, `Amazon Transportation Services : ...`, `Physical Stores : ...`, `Transportation : XXX9`): 8 rows (2018). A blank company with an `Amazon ...` establishment name but no label and no Amazon EIN (for example buildings run by a property manager) is not matched.
8. Any other company name, only if the establishment name has one of the strict labels (`North America Fulfillment Centers`, `Global Specialty Fulfillment`, `AMZL`, `Amazon Transportation Services`) with a site code: 1 row (a legacy-named 2018 filing).
EXCLUDED even though "Amazon" appears in a name: `Amazon Environmental Inc.` (Maviro; NAICS 325510; 6 rows), `Amazone USA Inc.` (NAICS 423820; 1 row); delivery service partners (DSPs) filed under an Amazon-like company name (company `Amazon` or `AMAZON` with establishment Agema Integrated Solutions, Black Eagle Express Delivery, Lyfeline Logistics Management, Caravan 12th Corporation, Forthright Strategies and others with their own EIN; `Amazon Delivery Center`, `Amazon Logistic`, `Amazon Logistics Inc.`, `Amazon (Ursa Logistics LLC as a contractor`): 44 rows removed compared with the old rule); and contractors at Amazon sites (ABM, Sizemore, SPS North America, SBM, C&W, Compass Group, Eurest, XPO, Catamount, delivery service partners filed under their own names, Worldwide Flight Services, and so on).
Search for other Amazon entities (2026-10-31): the raw files of all ten years were searched for company or establishment names containing amazon, amzn, "Golden State FC", Prime, Pillpack, Whole Foods, Zappos, AMZ, and for Amazon organisation labels, and by EIN (the four Amazon EINs above) and by street address and ZIP of the matched Amazon sites. No `Amazon Fulfillment Services` or `Amazon Data Services` company filings exist (Amazon Data Services appears only as an establishment name in ABM janitorial filings). `Amazon.com.dedc`, `.kydc`, `.indc`, `.azdc`, `.ksdc`, `.nvdc` are all covered by rule 1. Not added, and flagged: Whole Foods Market (Amazon-owned grocery, other NAICS 445), Pillpack LLC (1 row, pharmacy) and Prime Air Corp (3 rows, aircraft operations, EIN 660602415; no site code and not clearly Amazon-filed), which are not warehouse sites. Two blank-company `Amazon Warehouse` rows with no EIN (2022, 2024, NAICS 4922) were left out as unverifiable. At addresses shared with Amazon sites the other filers are DSPs, FedEx, DHL and other carriers or contractors, none of which is Amazon.
- Dedupe: per (year, establishment name, address, city, state) keep the highest submission id (later resubmissions supersede).

### Rates
- TRC rate = (DAFW + DJTR + other recordable cases) * 200,000 / hours. DART rate = (DAFW + DJTR) * 200,000 / hours. Days-away rate = DAFW * 200,000 / hours. This equals cases per 100 FTE (200,000 h = 100 FTE-years).
- Per-establishment rates are in `osha_ita_amazon_establishments.csv` (blank when invalid: `rate_valid` now applies the same filter as the headline series). Aggregates are hours-weighted (sum cases / sum hours), not an average of rates.
- QC filter for aggregates (applied identically to Amazon and non-Amazon): hours >= 1,000, employees >= 1, hours per employee between 300 and 4,500, all case counts present. About 0-5% of Amazon rows per year fail. Since the 2026-10-31 review `rate_valid` in the establishment file, the site table and the site histogram use this same filter (before, they used only hours >= 1,000).

### Files produced (data/processed/)
- `osha_ita_amazon_establishments.csv`: 8,228 establishment-year rows (7,656 before the review), with a `match_rule` column, 2016-2025, one row per establishment-year, with TRC/DART/DAFW rates.
- `osha_ita_aggregates_by_year.csv`: hours-weighted aggregates by year for Amazon and for non-Amazon filers, by NAICS segment (493110, 492110, 493110+492110, 493xxx, all NAICS for Amazon).
- `osha_ita_amazon_by_state_year.csv`: Amazon aggregates by state and year.
- `injury_comparison_by_year.csv`: the side-by-side table (Amazon vs ITA non-Amazon vs BLS).

### Important NAICS comparability problem
Amazon's own NAICS coding changed: through 2020 almost all Amazon logistics sites filed as 493110 (General warehousing and storage), including delivery stations and sort centres. From CY2021 filings roughly 600-800 sites per year are coded 492110 (Couriers and express delivery services) and only ~320-480 stay 493110. Therefore "Amazon 493110" is not the same set of buildings before and after 2021 (685 valid establishments in 2020, 317 in 2021), and the like-for-like series is `amz_logistics` (493110 + 492110 combined). Delivery-station-type sites after 2021 should be compared with BLS 4921 (couriers and express delivery services), also provided.

## 2. BLS Survey of Occupational Injuries and Illnesses (SOII)
- Publisher: US Bureau of Labor Statistics. Retrieved via the BLS Public Data API v1 (https://api.bls.gov/publicAPI/v1/timeseries/data/, no key). bls.gov and download.bls.gov file pages returned 403 to scripted requests, so the series ids were derived from the BLS series-id documentation (https://www.bls.gov/help/hlpforma.htm, https://download.bls.gov/pub/time.series/is/is.txt) and checked against the published 2024 Table 1 (https://www.bls.gov/web/osh/table-1-industry-rates-national.htm): total recordable 4.8 (NAICS 493) and 4.9 (49311) matched exactly.
- Series pattern: `IS|II` + `U` + supersector + industry + `3` (injury and illness rate per 100 FTE, all establishment sizes) + case type + `100` (national, private industry). Case type 1 total recordable, 2 DART, 3 days away from work, 4 job transfer/restriction. IS = reference years 2014 onward; II = 2003-2013. Supersector `TTU`, except private industry total which uses `000`/`000000`. Raw API responses: `data/raw/injuries/bls_soii_api_responses.json`.
- Industries: 000000 (private industry, all), SP2TRW (transportation and warehousing 48-49), 493000 (NAICS 493), 493100 (4931), 493110 (general warehousing and storage), 492000 (couriers and messengers), 492100 (couriers and express delivery).
- Years: 2003-2024. The 2025 reference-year SOII is not out as of 2026-10-31 (BLS normally releases in November); nothing was invented for 2025.
- NAICS 493110 vs 49311: BLS publishes this at the 5-digit level (49311); the API series carrying code 493110 returns the same values as 49311 (e.g. 2024: 4.9 total recordable, 4.3 DART).
- Gotcha: when reading the BLS HTML Table 1 through a summarising tool, the column order for DART components appeared swapped. The API series are authoritative: for 493110 in 2024, days away = 1.6 and job transfer/restriction = 2.7 (DART 4.3). Check before relying on any scraped reading of the table.
- Series breaks: the II to IS switch (2013/2014) and NAICS revisions mean 2003-2013 and 2014+ are not perfectly comparable; the sharp 2003 to 2012 decline is partly a real trend and partly a methodology change (e.g. 2011 reporting). Do not splice carelessly.
- File: `bls_soii_rates.csv` (616 values).

## 3. Comparison table (`injury_comparison_by_year.csv`), headline values and the 2026-10-31 name-rule change
Amazon logistics sites (hours-weighted, QC-filtered, NAICS 493110 + 492110) old rule -> new rule, with BLS 493110 for reference. TRC = total recordable cases per 100 FTE.

| Year | Amazon sites old -> new | TRC old -> new | DART old -> new | Other ITA 493110 TRC old -> new | BLS 493110 TRC / DART |
|---|---|---|---|---|---|
| 2016 | 1 -> 1 | 4.19 -> 4.19 | 3.86 -> 3.86 | 4.27 -> 4.27 | 5.0 / 3.7 |
| 2017 | 141 -> 166 | 7.24 -> 7.46 | 6.26 -> 6.49 | 4.31 -> 4.12 | 5.2 / 3.9 |
| 2018 | 233 -> 293 | 7.75 -> 7.95 | 6.85 -> 7.00 | 4.46 -> 4.27 | 5.2 / 4.0 |
| 2019 | 258 -> 268 | 8.94 -> 8.93 | 7.77 -> 7.75 | 4.18 -> 4.18 | 4.9 / 3.7 |
| 2020 | 654 -> 685 | 6.61 -> 6.56 | 5.96 -> 5.92 | 4.17 -> 4.18 | 5.0 / 4.0 |
| 2021 | 893 -> 890 | 7.85 -> 7.85 | 6.96 -> 6.96 | 4.49 -> 4.49 | 5.6 / 4.7 |
| 2022 | 1,023 -> 1,016 | 6.95 -> 6.95 | 6.57 -> 6.57 | 4.20 -> 4.20 | 5.7 / 4.8 |
| 2023 | 1,062 -> 1,113 | 6.50 -> 6.47 | 6.13 -> 6.10 | 3.76 -> 3.76 | 4.8 / 4.2 |
| 2024 | 1,124 -> 1,171 | 6.02 -> 6.00 | 5.66 -> 5.63 | 3.71 -> 3.71 | 4.9 / 4.3 |
| 2025 (partial) | 1,215 -> 1,257 | 5.01 -> 5.00 | 4.63 -> 4.62 | 3.66 -> 3.66 | not published |

What moved the numbers: in 2017 Golden State FC LLC adds +0.22 TRC (21 sites); in 2018 Golden State adds +0.09, blank-company filings that carry Amazon's own site labels add +0.14 (FAT1, LGB6, DEN2, IND8, LAS5, JFK8, FTW6, ITX2) and Prime Now (27 small sites at 3.75) subtracts 0.03. After 2020 the changes come from Prime Now sites and removal of delivery-partner rows and are 0.03 or less. The non-Amazon ITA 493110 comparison group falls in 2017 and 2018 because Golden State FC sites were previously inside it. The 2026-10-31 review's earlier estimate (7.47 for 2017 and 7.86 for 2018) counted Golden State only. Use the `amz_logistics_*` columns for 2021 onward; `amz_493110_*` for 2017-2020 where they coincide. The CSV has exact values.

### "Industry excluding Amazon"
- Not computable from BLS: SOII publishes no hours or establishment-level split, and BLS rates include Amazon. A true BLS-minus-Amazon rate needs the industry's total hours, which BLS does not publish at this level, so none is reported.
- Provided instead: `ita_nonamz_493110_*`, the hours-weighted rate of every NON-Amazon ITA filer coded NAICS 493110 (3,400 to 7,500 establishments a year). It is not BLS-comparable: ITA filers are the larger and designated-industry establishments only, self-reported, and include some contractors working at Amazon sites. Roughly: 2017 4.12 / 3.22; 2021 4.49 / 3.68; 2024 3.71 / 2.96 (TRC / DART). It runs below the BLS 493110 rate in most years; likely reasons (not tested here) are the different establishment mix (ITA filers are larger or designated-industry sites only) and self-reporting differences, so treat it as an internal like-for-like benchmark, not as BLS minus Amazon.

## 4. Caveats
- OSHA ITA data are employer self-reported, not audited; under-recording is documented in the literature and cannot be corrected here. Amazon's own filings are a floor.
- Establishment counts are not a clean measure of network size: only filing establishments appear, and early-year compliance was low (see coverage above). Rule changes are not the explanation for the growth.
- Establishment size: Amazon's filers are large establishments, while BLS SOII rates cover all sizes. Injury rates vary with establishment size, so the Amazon-versus-BLS ratio mixes a size effect with any real difference. BLS publishes size-related tables (quartile tables Q1 to Q6, "detailed industry by establishment size", and size-class series in the SOII database), but the BLS site and download server returned access-denied pages to scripted requests and the BLS API v1 daily quota was exhausted on 2026-10-31, so no size-matched BLS rate for NAICS 493 could be retrieved. Nothing was estimated. Next step: open the BLS quartile and size-class tables in a browser, or retry the API after the quota resets.
- Hours: Amazon reports hours worked, including part-time and seasonal staff; average employees are annual averages and can understate seasonal peaks. Rates use hours, so are not distorted by that.
- BLS SOII is an employer survey sample that includes Amazon in the industry rate: the BLS 493110 rate is therefore pulled up by Amazon, and the gap to Amazon is a lower bound on the gap to the rest of the industry.
- BLS 2021-2022 were COVID-affected years in several industries. No BLS 2025.
- Amazon attributes part of the gap to its larger share of new hires, its recording practices, and a different mix; these claims are not tested here.

## 5. Context only (not used as data)
- Strategic Organizing Center (SOC), analyses of OSHA ITA data: "Primed for Pain" (June 2021, https://thesoc.org/?p=491), "In Denial" (April 2023, https://thesoc.org/wp-content/uploads/sites/342/SOC_In-Denial_Amazon-Injury-Report-April-2023.pdf), "Same-Day Injury Report" (May 2024, https://thesoc.org/wp-content/uploads/sites/342/SOC_Same-Day-Injury-Report-May-2024.pdf). Our independent 2020 DART (5.96) and 2023 total recordable (6.50) are close to the 5.9 and 6.5 those reports are reported to cite, which is a consistency check, not a dependency. SOC is a coalition of unions (SEIU, Teamsters and others), so treat as advocacy-sourced analysis of public data.
- Amazon has disputed these comparisons (it argues the right comparator also includes its courier and delivery peers). The 4921 BLS series is provided so the dashboard can show both comparators.

## 6. Gaps
- No 2016 Amazon warehouse rate; no BLS 2025; no true BLS-minus-Amazon rate; Amazon-owned sites filed under names with no Amazon label or EIN not captured; case-detail (injury type, body part) files not downloaded; no state-level BLS benchmark pulled (national only); no JHU subscription sources used (Chrome not checked; none needed).
