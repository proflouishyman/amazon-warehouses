# Benchmark: ENVIRONMENT (Amazon vs Walmart, Target, Home Depot, Costco, UPS, FedEx)

Retrieved 2026-10-31. Raw files: `data/raw/benchmark/environment/<company>/` (PDFs, extracted text) plus `sec_revenue/` (SEC XBRL companyfacts JSON). Build scripts live next to the raw files (`_build_bench_environment.py`, `_build_bench_environment_part2.py`; run with `python3 -I`, they read only the saved raw files and the existing Amazon CSVs). Amazon figures are reused from `amazon_carbon_footprint_by_report_vintage.csv` and `amazon_sustainability_other_metrics.csv` (see `environment.md`), 2025-report vintage.

## Files

| File | Rows | Content |
|---|---|---|
| `data/processed/bench_environment_emissions.csv` | 121 | Scope 1, 2 (market and location), 3 and totals by company and year, metric tons CO2e, with source doc, URL, PDF page and a `derived` flag |
| `data/processed/bench_environment_intensity.csv` | 24 | g CO2e per $ revenue computed uniformly (revenue from SEC 10-K XBRL, accession in each row) next to each company's own reported intensity |
| `data/processed/bench_environment_renewables_fleet.csv` | 89 | Renewable share, on-site solar, storage, EV fleet and charging, targets |
| `data/processed/bench_environment_boundaries.csv` | 21 | What each inventory includes and excludes, with page refs |

Page refs are PDF page indices (as `pdftotext -f N`). UPS fleet counts come from a web page (no page).

## Headline comparisons

1. **Scope 1+2 per dollar: Amazon is above the store retailers and far below the carriers.** Latest year, market-based, computed as t CO2e per $M revenue (= g per $): Amazon 2025 26.7; Walmart CY2024 23.0; Target FY2024 14.1 (derived); Home Depot FY2025 9.4; Costco FY2024 10.2; UPS 2025 174.1; FedEx FY2025 170.2. File: `bench_environment_intensity.csv`. Walmart (22.98) and FedEx (169.29 location-based) reproduce the companies' own reported figures. Amazon's absolute Scope 1+2 is 19.11 Mt (2025) against Walmart's 15.65 Mt (CY2024), on revenue of $716.9B vs $681.0B. (`bench_environment_emissions.csv`, rows scope1+2.)
2. **Amazon's Scope 1+2 intensity fell faster than Walmart's over 2022-2025 but rose in 2025.** Amazon 31.3 (2022), 29.5, 28.1, 26.7 (2025); Walmart 24.9, 23.9, 23.0 (CY2022-CY2024). Amazon's Scope 2 rose 34% in 2025 (data centers, AMZ25 p10), and its Scope 1 grew from 13.0 Mt (2022) to 15.4 Mt (2025). UPS got worse in 2025 (165 to 174) after taking on a USPS air contract (UPS 2025 GRI p26).
3. **Scope 3 is not comparable and should not be charted side by side.** Amazon's Scope 3 is 61.7 Mt in 2025, about 86 g per $; Walmart's estimate is 636.6 Mt (about 935 g per $) and Home Depot's is 234.8 Mt (1,426 g per $), because retailers count purchased goods and the lifetime use of products sold (Home Depot Category 11 alone is 170.9 Mt, 72% of its footprint, HD p34/p81). Amazon's boundary lists Amazon-branded products, packaging, delivery and freight, capital goods, commuting and device use, not third-party seller or resale merchandise (`bench_environment_boundaries.csv`, Amazon rows).
4. **Renewable claims use different yardsticks.** Amazon: 100% matched by purchases (2023-2025). Walmart: 48.5% including grid mix, 30.6% from its own contracts (CY2024, p106). Target: 76% (FY2024, includes RECs and grid mix, p50). Costco 28% clean electricity (end CY2024, p30). UPS 27.4% (2025, p26). Home Depot states no share; 973,000 MWh renewable purchased vs 2.87 million MWh electricity purchased gives about 34% but that ratio is mine and the bases may differ. FedEx states 96.7 GWh sourced in FY25 and no share. File: `bench_environment_renewables_fleet.csv`.
5. **Electric fleet: only Amazon, FedEx and UPS publish counts.** Amazon 52,700 electric delivery vans in 2025 (37,400 US). FedEx 9,446 on- and off-road EVs in FY25 (8,018 in FY24; EV share of PUD purchase orders 50%, 100% target for 2030 now under review, FDX26 p24). UPS 580+ battery electric and 1.4K+ electric and hybrid vehicles, plus 19K+ alternative-fuel vehicles, 36.4% of ground fuel alternative (UPS 2025 p27). Walmart pilots electric semis and uses electric yard trucks at "some facilities" with no count (p31); Target, Home Depot and Costco give no EV delivery or yard-truck counts (Costco is testing EV trucks, p36; Home Depot has replaced 150+ forklifts in Mexico, p37). Amazon's vans include those run by delivery service partners; the carriers' counts are owned fleet.
6. **On-site solar at warehouses and stores.** Walmart 166 MW across 325 US facilities (all facility types, p29). Home Depot about 135 rooftop installations, 302 MWac solar company-wide (rooftop plus off-site, p35 and p81). Costco 126 on-site systems (no MW). FedEx 37 facilities generating solar, over 31 GWh in FY24. Amazon 337 rooftop projects at fulfillment centers, sortation centers and stores, but the printed capacity (42 MW) is inconsistent with the printed generation (454,000 MWh) and the sentence is cut at a page break (AMZ25 p10): see Gaps.

## Method and boundary notes

- Amazon includes AWS data centers in Scope 2 and its delivery network in Scope 1; the retailers have no AWS-equivalent but Walmart carries a private truck fleet in Scope 1 (transport fuel and mobile refrigerants about 24.9% of Scope 1, about 2.25 Mt, derived). Amazon buys delivery from carriers, so UPS and FedEx Scope 1 overlaps with Amazon Scope 3 (purchased delivery). Do not sum company totals.
- Intensity: t CO2e per $M revenue equals g per $. Walmart divides calendar-year emissions by fiscal-year revenue; I follow that. Revenue is SEC 10-K XBRL (`Revenues` or `RevenueFromContractWithCustomerExcludingAssessedTax`). Amazon's own intensity (112.8 g/$ in 2025) is for total Scope 1+2+3, so it is a different quantity from the Scope 1+2 ratios above.
- FedEx reports Scope 2 market-based equal to location-based for FY22-FY23 (difference judged de minimis). FedEx Scope 3 adds categories each year (FY23 4.8 Mt, FY24 9.8 Mt, FY25 14.9 Mt), so it is not a trend. UPS Scope 3 is partial (no purchased goods, capital goods).
- Fiscal years: Walmart FYE Jan; Target FYE Jan/Feb (FY2024 = year ended 1 Feb 2025); Home Depot FY2025 ended 1 Feb 2026; Costco FYE Aug/Sep; FedEx FYE 31 May; UPS and Amazon calendar year.

## Derived or estimated rows (flag `derived=yes`)

- Target FY2022-FY2024 Scope 1+2: the report prints only percent change from the 2017 baseline (-34.9%, -38.1%, -41.3%, 2025 report p55) and the "2.56M" baseline; absolute values use the 2,567,880 t baseline from the 2024 report p13. The FY2023 derivation (1,589,520) matches the printed 1,590,537 to 0.06%. Target Scope 3 FY2022-24 are derived the same way from a restated 52.13 Mt baseline and cover goal categories only; FY2024 excludes supplier-reported reductions.
- Walmart transport-fuel emissions (share x Scope 1); Home Depot renewable share ratio; UPS renewable share from the energy table (21.5%, which does not match the 27.4% headline and is not reconciled).

## Gaps and caveats

1. **CDP responses were not obtained.** They are not freely downloadable; all figures come from sustainability and ESG reports, not CDP.
2. **Amazon rooftop solar capacity (42 MW vs 454,000 MWh) is internally inconsistent** in the 2025 report text; not usable for per-facility ratios until the printed page is checked against the published web version.
3. **Home Depot intensity does not reconcile for FY2023 and FY2024.** Reported 10,800 and 10,900 t per $B; market-based S1+2 gives 9.7 and 10.5, location-based 11.6 for both. FY2025 (11,200) reproduces with location-based Scope 2. Footnotes 27-28 of the report, which would explain the method, were not found in the extracted text. HD's consolidation approach is not stated in the pages read.
4. **Costco figures are rounded to 0.1 Mt** in the report; Scope 3 restated for FY20 and FY23; the "CY2020 base" intensity row uses Costco FY2020 revenue.
5. UPS revenue differs between EDGAR as filed (2024: $91,070M) and the 2025 GRI (2024: $89,502M, 2020: $78,408M, restated); EDGAR as filed is used for computed ratios, so UPS 2020 and 2024 computed intensity may be off by a few percent against a restated basis.
6. Target 2025 report was read from a copy hosted by smartenergydecisions.com (the Target-hosted URL was not retrieved); Target does not state Scope 1 and 2 split in tonnes in the text read (charts only); no warehouse (distribution center) solar or fleet figures found.
7. No warehouse-specific energy intensity (kWh per sq ft) was published by any of the six; the only warehouse-level data are the solar and EV counts above. EIA CBECS 2018 warehouse intensity is in the existing Amazon environment files.
8. Walmart and Target FY2026 reports (published after Sep 2026) were not found by search; latest used: Walmart FY2025 ESG Report (Sep 2025, CY2024 data), Target 2025 report (Oct 2025, FY2024 data). Costco, Home Depot, UPS and FedEx files are 2025-2026 editions.
9. Home Depot and UPS: a few failed download stubs (HTML error pages saved as `hd2024.pdf`, `hd2026.pdf`, `ups_gri_2025.pdf`, `ups/ups_planet.html`, `ups/ups_report_page.html`, `target/t2026_page.html`) remain in the raw folder because nothing may be deleted; they contain no data. UPS pages needed the browser helper (curl returns 403).
10. Not run: location-based Scope 2 for Amazon (not in the saved tables), Scope 2 from eGRID cross-checks, any adjustment to a common GWP set (UPS uses AR6; others not checked).

## Search usage

Browser searches used: 5 of 30 (Target, Home Depot, Costco, UPS, FedEx); browser fetches: 3 (UPS pages). SEC EDGAR via curl with a generic User-Agent.
