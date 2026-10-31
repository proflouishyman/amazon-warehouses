# Benchmark workstream: adversarial review log

Review date: 2026-10-31. Method: read the scripts and output files, recompute from the raw inputs (OSHA ITA CSVs, 10-K text, sustainability-report PDFs), and verify XBRL figures against SEC EDGAR (data.sec.gov companyconcept API). The collector reports were not used as evidence.

## Mechanical fixes applied

### 1. FedEx headcount, FY2024 to FY2026: segment figure used as company total
- **Where.** `data/raw/benchmark/network_financial/build_facilities.py`, FedEx employee list. The bad values flowed into `data/processed/bench_network_employees_ecom.csv` (3 rows) and `data/processed/bench_network_headline_comparison.csv` (2 rows).
- **Error.** The rows are labelled `employees / total / Worldwide`, but the values (430,000, 440,000 and 452,000) are the "Federal Express employed approximately ..." sentence. That sentence covers the Federal Express Corporation segment only.
- **Correct figures.** The same 10-Ks give company-wide counts in "FedEx employed approximately X permanent full-time and Y permanent part-time employees":
  - FY2024 (0000950170-24-083577): 306,000 + 199,000 = 505,000.
  - FY2025 (0001048911-25-000011): 300,000 + 210,000 = 510,000.
  - FY2026 (0001048911-26-000105): 300,000 + 230,000 = 530,000.
  - These use the same basis as the FY2022 and FY2023 rows already in the file (derived sum, excludes contractors).
- **Effect.** FedEx CY2024 revenue per employee falls from 199.8 to 172.4 USD thousand, which moves FedEx below UPS (185.9).
- **Rebuild.** I re-ran `build_facilities.py` and `build_compare.py`. A diff against the previous outputs shows that only these 5 rows changed. The previous CSVs and the previous script are backed up in the review session's scratchpad.
- **Note updated.** `bench_network_financial.md`, lines 17 and 28.

### 2. `bench_network_financial.md` line 17: wrong Walmart fiscal-year label
- **Error.** The revenue-per-employee line said Walmart's figure was the "FY ended Jan 2026".
- **Fix.** The CY2024 row uses period_end 2025-01-31 (FY2025, accession 0000104169-26-000055 for revenue and 0000104169-25-000021 for headcount), so the label now reads "FY ended Jan 2025". Only the text label changed; the data was already right.

## Issues found but not fixed (severity)

### Injuries (`scripts/bench_injuries.py`)
- **MEDIUM. FedEx Ground CY2024 rows look partial-year.** I compared the 585 sites present in both CY2023 and CY2024 (rate-valid). Employees are unchanged (ratio 0.99), but hours fell to 0.62 and total cases to 0.65; median hours per employee went from 1,048 to 645. The CY2024 Federal Express Corporation filings for Ground addresses appear to cover about 7 months (after the June 2024 merger). The rate (20.4) is roughly preserved because cases and hours fall together, but the hours, case counts and `hours_per_valid_site` for 2024 are not full-year. The note calls 2024 "approximate" but does not say why.
- **MEDIUM. Target false negatives.** The Target name rule (`dc_re`) misses supply-chain sites that file under retail NAICS:
  - Sortation Centers (Minneapolis, Houston, Dallas, Atlanta, Philadelphia, Austin, Chicago, Chicago North, Denver, Miami).
  - Return Centers (East Coast, West Coast, Indianapolis).
  - "Target.com ... TFC" sites (Joliet, Burlington, Woodbury, Savannah, Tucson, Ontario).
  - Perth Amboy Flow Center and Houston Receive Center.
  - **Effect.** Adding `\bTFC\b|sortation center|return center|flow center|receive center` raises CY2024 Target valid sites from 43 to 65 and moves TRC from 8.63 to 8.09 and DART from 7.99 to 7.44. In CY2023, sites go from 41 to 61 and TRC from 6.60 to 6.18.
  - **Corroboration.** The 65 matches the 10-K's 66 "supply chain facilities", a count that includes sortation centers.
  - **Why not fixed.** The fix changes the matching rule and the headline numbers, so it needs a decision and a re-run.
- **LOW. Industry comparator uses a different NAICS scope.** The headline 1.6x ratio sets Amazon at NAICS 493+492 (TRC 6.00) against ex-Amazon NAICS 493110 only (3.71). Amazon's 493-only figure is 6.19 (1.67x), so the stated gap is slightly understated, not overstated.
- **LOW. Wrong label in the note.** The note says "UPS Freight (trucking) files as 484 and is excluded". The 1,424 excluded UPS 484110 rows are filed as "United Parcel Service" and carry SLIC-coded building names (for example NCRLI Cary, 200 employees). They are UPS package or feeder operations coded as trucking, not UPS Freight. The exclusion may still be right, but the label is wrong. Another 412 UPS 488xxx rows (air gateways, SCS customs brokerage) are also excluded.
- **LOW. Lowe's 423710 rows partly in the headline.** The note says these rows are kept out of the headline, but 11 "Pro Fulfillment Center" rows are in it because the name matches "fulfillment".
- **OK.**
  - `rate_valid` is identical to the Amazon series (`extract_amazon_ita.py` line 51 and `build_injury_tables.py` line 40).
  - Independent recomputation from the raw files for 2019 and 2023:
    - UPS, FedEx Ground and Target match exactly.
    - Walmart matches exactly in 2023. In 2019 I got 193 sites at 2.95 against the script's 206 at 2.99; the difference is blank-company EIN rows and the Jet.com and Hayneedle units, which my simple rule omits.
  - Sampled matches: Walmart (WM 3xxx, 4xxx, 6xxx to 9xxx and 10xxx DC/FC numbers), GXO, DHL, Ryder, Costco, Home Depot, Kroger and UPS showed no stores and no unrelated companies.
  - Walmart 454110 (San Bruno and NY tech offices), 484121 (transport offices) and 811111 (fleet shops) are correctly excluded.

### Network and financial
- **OK. EDGAR check.** 21 XBRL figures match EDGAR exactly: 3 per company (revenue, capex and net PP&E) for Amazon, Walmart, Target, Home Depot, Costco, UPS and FedEx.
- **OK. Item 2 figures in the 10-K text.** Target 66 / 68.5M sq ft, Home Depot 108.3M sq ft, UPS about 1,000 facilities / 90M sq ft, Costco 31.9M sq ft and Walmart 192 US DCs (the FY2026 10-K) all appear in the filing text.
- **LOW. Fiscal-year alignment for FedEx.** Walmart, Target and Home Depot are aligned by the majority of months. FedEx is mapped as FY ending May (Y+1) to CY Y, so FY2025 (Jun 2024 to May 2025) stands for CY2024. That is defensible, and it is labelled in `bench_network_definitions.csv` and the headline file. The collector's prose said Walmart was "the year ended Jan 2026"; that was wrong in the prose only and is fixed in the note.
- **LOW. Revenue per square foot.** The ratio divides company-wide revenue (Amazon including AWS, all companies including international) by network square feet for a narrower geography. It is flagged in the row note as "only a rough" ratio but is presented as a headline figure.
- **LOW. Labor note on FedEx headcount.** `bench_labor.md` says there is "no company-wide headcount after FY2021" for FedEx. The FY2022 to FY2026 10-Ks give one (see fix 1), so a FedEx ULP-per-10,000 figure could be computed.

### Amazon share of NAICS 493
- **Method.** The numerator is the sum of ITA annual average employees at Amazon NAICS 493110 sites; the denominator is QCEW private NAICS 493 employment. This is defensible as an order-of-magnitude estimate.
- **Uncertainty.** It is stated, including that the figure is not a strict lower bound and that 2019 to 2020 are unusable.
- **Numerator check.** My figures from `bench_injuries_establishments.csv` (Amazon, 493110) are:
  - 2024: 612,189 (509 rows), against 611,272 in the share table.
  - 2025: 638,469, against 637,242.
- **LOW. 2019 numerator.** The same check gives 639,067 for 2019. That supports the "alt" 634k figure, not the 506k the share table uses, which implies about 51%. This strengthens the "2019 unusable" flag.
- **LOW. Column names.** `amazon_share_of_qcew_493_pct_lower_bound` contradicts the note's own statement that the figure is not a strict bound. A name such as `_approx` would match the text.

### Environment
- **OK. Page references.**
  - Sampled figures appear on the cited PDF pages (PDF page index):
    - Walmart CY2024 Scope 1 9.03 and Scope 2 6.61 (p30 and p106) and Scope 3 636.57 (p34).
    - Home Depot FY2024 Scope 1 818,000 and Category 11 143,843,000 (p81).
    - Costco FY2024 total 182.2M (p72).
    - UPS 2024 Scope 1 14,408,000 and 2025 Scope 1 14,897,000 (p39).
    - FedEx FY2025 Scope 1 13,932,537 and 169.29 t/$M (p43).
  - Target's derived FY2024 figure (2,567,880 x (1 - 0.413)) traces to the 41.3% in the 2025 report text and the baseline on p13 of the 2024 report.
- **OK. Boundary labels.** `bench_environment_boundaries.csv` labels the boundary differences for every company: AWS in Amazon Scope 2, the Walmart fleet in Scope 1, retailer Scope 3 Category 11, partial Scope 3 for UPS and FedEx, and carrier-Amazon double counting. Every intensity row carries `scope3_comparable = NO`.
- **OK. Amazon's own intensity.** Amazon's reported intensity is per dollar of revenue in the 2025 report (p46), and per dollar of GMS in the 2023 report. The file uses the 2025 basis consistently.
