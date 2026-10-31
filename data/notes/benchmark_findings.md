# Benchmark findings: Amazon against Walmart, Target, other operators and the industry

Built from the bench_* files in `data/processed/` after the review in `data/notes/bench_review.md`. Figures were read back from the CSVs, not copied from worker summaries. Where a worker summary and a file disagree, the file is used.

## Excluded because the review flagged them
These are not headline figures and must not appear on benchmark.html. (Target injuries and the Lowe's wholesale rows, formerly listed here, were fixed on 2026-10-31 and are now in the headline; see section 1.)
- **FedEx Ground, CY2024** (TRC 20.44, 625 sites). Flagged `partial_year = True`: the filings cover about June to December 2024 (hours per employee 672 against 1,081 in CY2023), so hours and cases are not full-year. Kept in the file, `headline_comparison_ok = False`, and left out of the parcel group. CY2023 and earlier FedEx Ground rows are not flagged and may be used. The `fedex_unassigned_2024plus` rows are supplementary and stay off the chart.
- **Revenue per square foot.** It divides company-wide revenue by a narrower network.
- **Amazon share of NAICS 493 for 2019 and 2020.** The two source files disagree on 2019 and the filing coding changed. The values are now blank in the CSV and `share_usable = no`.
- **FedEx figures from before the headcount fix**: use only the corrected 172.4.

## 1. Injuries (OSHA ITA Form 300A, CY2024)
Files: `bench_injuries_peer_year.csv` (filter `scope=headline`, `year=2024`; fields `peer`, `n_valid`, `trc`, `dart`, `dafw`, `trc_share_sites_above_bls`, `bls_493110_trc`), `bench_injuries_493110_distribution.csv`. Note: `data/notes/bench_injuries.md`.

| Population (`peer`) | Valid sites | TRC | DART | DAFW |
|---|---|---|---|---|
| Amazon (`amazon`) | 1,171 | 6.00 | 5.63 | 1.18 |
| Other ITA 493110 filers (`ita_493110_ex_amazon`) | 7,395 | 3.71 | 2.96 | 1.62 |
| Walmart DCs (`walmart`) | 207 | 2.79 | 2.36 | 0.64 |
| 3PLs combined (`group_3pl`: GXO, DHL Supply Chain, Ryder) | 630 | 1.70 | 1.16 | 0.51 |
| Retailer DCs combined (`group_retailer_dcs`) | 533 | 4.39 | 3.88 | 1.85 |
| UPS (`ups`) | 1,255 | 8.22 | 6.86 | 3.83 |
| FedEx Express (`fedex_express`, supplementary) | 727 | 6.74 | 5.61 | 4.38 |
| Costco (`costco`) | 81 | 6.13 | 5.16 | 3.90 |
| Target (`target`; DCs, sortation, return, flow, receive and TFC sites) | 65 | 8.09 | 7.44 | 3.40 |
| BLS NAICS 493110 reference | | 4.9 | 4.3 | 1.6 |

- Amazon TRC is 1.6x the other 493110 filers, 2.2x Walmart DCs, 3.5x the 3PL group. It is below UPS and Target (8.09, 65 sites, now in the headline). DART gap to other filers is 1.9x. Amazon's DAFW is below the other filers, so the excess is restricted and transferred work.
- 55% of Amazon sites sit above the BLS 493110 TRC, against 23% of other filers and 14% of Walmart sites (`trc_share_sites_above_bls`).
- Site-rate percentiles for other 493110 filers (`population` ex-Amazon, `measure=trc`, 2024): p50 1.54, p75 4.54, p90 8.82, p99 24.87; p25 is 0 because many small sites report zero cases, so compare hours-weighted rates.
- Trend: Amazon to other-filer TRC ratio fell from 1.75 (2021) to 1.62 (2024).

Caveats:
- The 1.6x compares Amazon on NAICS 493 plus 492 (6.00) with peers on 493110 only. Amazon's 493-only rate is 6.19 (1.67x), so the gap is slightly understated.
- Lowe's: the 11 NAICS 423710 (wholesale-coded) site-years, including the Charlotte Pro Fulfillment Center, are now out of the headline (CY2024 Lowe's 48 sites, TRC 2.72). FedEx Ground CY2024 is flagged `partial_year` and the parcel group is UPS only in 2024; use the `headline_comparison_ok` column.
- Target matches 65 sites in CY2024 after adding sortation, return, flow and receive centers and TFC sites (10-K: 66 supply chain facilities). Its CY2021 and CY2022 rates (16.0, 17.0) include COVID cases.
- Costco, Kroger, Lowe's, Home Depot and Ryder have 15 to 110 sites a year, so their rates are thin. Show `n_valid` beside each bar.
- Walmart 2019 matching differs slightly between the script and the reviewer's recount (206 sites at 2.99 against 193 at 2.95). 2024 matches exactly in the reviewer's 2023 check, so use 2024 or 2023.
- Sam's Club DCs filed under Wal-Mart Stores cannot be separated. CY2025 is partial, and BLS 2025 is not published.
- The 1,424 UPS NAICS 484110 rows excluded from the headline are UPS building rows (package or feeder operations coded as trucking), not UPS Freight.
- Self-reported establishment data. Different recordkeeping and reporting practices affect rates.

## 2. Network and finance (10-K, XBRL)
Files: `bench_network_headline_comparison.csv` (fields `slug`, `fiscal_year_label`, `metric`, `value`, `unit`, `input_accessions`), `bench_network_facilities.csv`, `bench_network_definitions.csv`. Note: `bench_network_financial.md`. Revenue, capex and net PP&E for all seven companies were matched to EDGAR by the reviewer.

Revenue per employee, USD thousand (`metric=revenue_per_employee_usd_k`, 2024 column):
Costco 764.1, Amazon 410.0, Home Depot 339.3, Walmart 324.3, Target 242.2, UPS 185.9, FedEx 172.4 (corrected, company-wide headcount).
Fiscal-year labels: Walmart is the year ended Jan 2025, FedEx the year ended May 2025 (`fiscal_year_label` 2025 in the file), others calendar 2024.

Capex as share of revenue (`metric=capex_pct_revenue`): Amazon 13.01, FedEx 4.61, UPS 4.29, Walmart 3.49, Target 2.71, Home Depot 2.18, Costco 1.85.

Network footprint (`bench_network_facilities.csv`, 10-K Item 2): Walmart 192 US DCs (125 owned, 67 leased) in the latest 10-K; Amazon North America segment about 453 million sq ft (`metric=network_sqft_thousand`); Target 68.5 million sq ft (the 10-K figure, checked against filing text); Home Depot 108.3 million; UPS 90 million (US package facilities); Costco 31.9 million.

Caveats:
- Amazon capex includes AWS data centers, so it is not a logistics figure. Revenue and headcount are company-wide.
- Square-foot figures use different definitions (Amazon segment excluding stores and AWS; UPS package facilities not warehouses; Costco's definition changed in FY2020). Show them as counts of space, never as productivity.
- Walmart discloses no DC square footage. Target's rise from 48 to 66 facilities is partly a wider definition. Home Depot's about 500 sites is a lower bound.
- Item 2 figures were script-parsed; the reviewer confirmed only Target, Home Depot, UPS, Costco and Walmart facility and area counts.
- Target's facility count from the 10-K (66) is a reported figure and is fine to show. It is the injury match that is incomplete.

## 3. Labor
Files: `bench_labor_announced_vs_qcew493.csv`, `bench_labor_employees_by_year.csv`, `bench_labor_nlrb_counts_by_year.csv`, `bench_labor_union_representation.csv`, `bench_labor_qcew493_wage_series.csv`, `bench_labor_announced_wages.csv`. Industry pay: `bench_warehousing_industry_oews_premium.csv`. Note: `bench_labor.md`.

- **Pay.** Amazon's announced $23 average (Sept 2025) is 84% of the QCEW NAICS 493 40-hour equivalent of $27.27; its $30 total compensation is 110%. Walmart supply chain $27.50 is 101%. Costco "more than $31" is 114%. UPS part-time $21-23 is 84%. Target's and Home Depot's $15 floors are 55% and 60% (fields `announced_low_as_pct_of_qcew_493`, `announced_high_as_pct_of_qcew_493`).
- **Same-job pay (OEWS, 2025).** Laborers and movers (53-7062) earn $21.82 in warehousing against $20.30 across private industry (about 8% premium); stockers and order fillers (53-7065) $22.09 against $18.96 (about 17%) (`warehousing_493_mean_hourly_usd`, `all_industries_private_mean_hourly_usd`).
- **Headcount (10-K).** Amazon 798,000 (2019) to 1,576,000 (2025). Latest peers: Walmart 1.6M US, UPS 370,000 US, Costco 232,000 US, Home Depot 472,400, Target 415,000.
- **Unions.** UPS says nearly 80% of US employees are under Teamsters agreements; Costco about 5% worldwide. Walmart, Target, Home Depot and FedEx give no figure.
- **NLRB, filed 2024** (`year_filed=2024`; use `ca_ulp_charges_vs_employer` and `ca_per_10k_employees`): ULP charges against the employer (CA) UPS 385 and 7.86 per 10,000 employees; Amazon 194 and 1.25; Costco 46 and 1.38; Walmart 22 and 0.10; Target 5 and 0.11; Home Depot 3 and 0.06; FedEx 10, no rate. `all_cases` (UPS 559, Amazon 238, Costco 50) adds charges against unions (CB), representation petitions and other types; it is supplementary.

Caveats:
- Announced starting wages and QCEW averages are not like-for-like. The QCEW baseline includes Amazon itself (about a third of NAICS 493).
- Costco and UPS wage rows come from news reports and a Teamsters release. Walmart's two rows come from an undated page.
- NLRB counts match case names only, so subsidiary-named cases are missed. UPS includes charges filed against unions that name UPS. 2026 is partial. Per-10,000 rates use worldwide headcount from the 10-K.
- Reconciled 2026-10-31: the collector's 194 (Amazon) and 385 (UPS) are the CA counts; the file's 238 and 559 are `all_cases` (CA + CB + representation + other). Both are in the file. CA is the count used (it is the numerator of the per-10,000 rate); see `bench_labor.md`.
- FedEx has a company-wide headcount in the 10-Ks after FY2021 (the labor note says it does not). A FedEx rate could be computed but is not in the file, so show FedEx cases only.
- Kroger, Lowe's, GXO, DHL Supply Chain and Ryder are not covered for labor.

## 4. Industry context
Files: `bench_warehousing_industry_qcew_national_annual.csv`, `bench_warehousing_industry_amazon_share_493.csv`, `bench_warehousing_industry_amazon_vs_qcew_size.csv`, `bench_warehousing_industry_qcew_size_class_q1.csv`. Note: `bench_warehousing_industry.md`.

- Private NAICS 493 employment rose from 510,640 (2001) to 1,901,976 (2025), with 23,345 establishments in 2025 (`avg_employment`, `establishments`). Couriers (492) reached 1,120,618.
- Amazon's estimated share of NAICS 493 employment (`amazon_share_of_qcew_493_pct_estimate`): 18.6% (2017), 26.8% (2022), 29.4% (2023), 32.3% (2024), 33.5% (2025). The combined 493110 plus 492110 series against 493 plus 492 (`amazon_493110_plus_492110_share_of_qcew_493_plus_492_pct_estimate`) is steadier: 11.2% (2017), 23.8% (2022), 27.8% (2024), 28.3% (2025). Use years 2017, 2018 and 2021 onward only.
- In 2025 Amazon holds an estimated 58% of the 351 establishments with 1,000 or more employees and 61% of their employment (`amazon_vs_qcew_size`). Sites that size held 41.9% of 493 employment in 2025, against 10.1% in 2014.

Caveats:
- The share columns were renamed from `_lower_bound` to `_estimate` on 2026-10-31 because the figure is not a strict bound: the numerator may include sites QCEW does not code to 493. Chart label reads "estimate". (`reported_lower_bound` in the network files is a different thing: a 10-K "more than N" qualifier, unchanged.)
- Amazon's 2019 workforce is counted differently in two project files (506,227 and 634,441), and the reviewer recount supports the larger figure, so 2019 and 2020 are excluded (blank in the CSV, `share_usable = no`; the same two years are blank and `usable = no` in `bench_warehousing_industry_amazon_vs_qcew_size.csv`).
- Early ITA coverage is low, so 2017 and 2018 are understated. Temp-agency workers (NAICS 5613) are excluded throughout.
- CBP and Economic Census denominators run below QCEW and are not used for the headline.

## 5. Environment
Files: `bench_environment_intensity.csv` (fields `company`, `period`, `s12_market_g_per_usd`, `scope3_comparable`, `reported_intensity`), `bench_environment_emissions.csv`, `bench_environment_renewables_fleet.csv`, `bench_environment_boundaries.csv`. Note: `bench_environment.md`. The reviewer confirmed sampled Walmart, Home Depot, Costco, UPS and FedEx figures against the cited pages.

Scope 1+2 market-based, g CO2e per dollar of revenue, latest year:
UPS 174.1 (2025), FedEx 170.2 (FY2025), Amazon 26.7 (2025), Walmart 23.0 (CY2024), Target 14.1 (FY2024), Costco 10.2 (FY2024), Home Depot 9.4 (FY2025).
Trend: Amazon 31.3 (2022) to 26.7 (2025); Walmart 24.9 (2022) to 23.0 (2024). Amazon's 2025 absolute Scope 1+2 is 19.11 Mt.

Caveats:
- Scope 3 is not comparable (every row is marked so). Do not chart it across companies.
- Amazon's Scope 2 includes AWS data centers (Scope 2 rose 34% in 2025). Walmart's private fleet is in Scope 1. UPS and FedEx are delivery operators, so their intensity is not like-for-like with retailers.
- Target's value is derived from percent changes against a 2,567,880-tonne baseline (41.3% reduction), not printed tonnes.
- Home Depot's FY2023 and FY2024 computed values (9.7 and 10.5) do not match its reported 10,800 and 10,900 t per $B. Prefer the FY2025 figure, with the mismatch noted.
- Renewable shares use different yardsticks (Amazon 100% matched by purchases; Walmart 48.5% incl. grid mix; Target 76% incl. RECs; Costco 28%; UPS 27.4%). Show as a table, not a ranking.
- EV fleet counts exist only for Amazon (52,700 electric vans, 2025), FedEx (9,446) and UPS (580+).
- Amazon's rooftop MW figure is unusable (42 MW against 454,000 MWh). CDP data were not used.

---

# benchmark.html specification (for the integrator; not built)

Single page, charts built from the CSVs listed. Load CSVs as static files from `data/processed/`; no remote data. Use the `dataviz` and `artifact-design` guidance. Amazon is the highlighted series in every chart; peers in one neutral colour family. Each chart has a title stating the finding, a one-line caveat under it, and the source file name in small text. Phone width: one chart per row, horizontal bars.

Page order and charts:

1. **Injury rate by operator (horizontal bars, CY2024).** File `bench_injuries_peer_year.csv`, rows `scope=headline`, `year=2024`, `peer` in: amazon, ita_493110_ex_amazon, walmart, target, group_3pl, group_retailer_dcs, costco, ups, fedex_express. Fields `trc`, `dart` (toggle), label with `n_valid`. Add a dashed line at `bls_493110_trc` (4.9; `bls_493110_dart` for DART). Exclude `fedex_ground` (2024 is `partial_year`) and `fedex_unassigned_2024plus`; keep only rows with `headline_comparison_ok = True`. Caveat text: "Total recordable cases per 100 full-time workers, as filed with OSHA. Amazon is on NAICS 493 plus 492; others on 493110. FedEx Ground is left out because its 2024 filings cover only part of the year. Sites with few filings give noisy rates."
2. **Amazon against other warehouses over time (line).** Same file, `scope=headline`, peers amazon, ita_493110_ex_amazon, walmart, group_3pl, years 2017 to 2024 (omit 2025), field `trc`. Caveat: "2019 Walmart matching is approximate. 2025 is partial and omitted."
3. **Share of sites above the industry rate (bars, 2024).** Same file, field `trc_share_sites_above_bls`, peers amazon, ita_493110_ex_amazon, walmart, group_3pl, group_retailer_dcs, ups. Caveat: "Share of sites whose own rate exceeds the BLS 493110 rate for the year."
4. **Distribution of site rates, other 493110 filers (percentile strip).** `bench_injuries_493110_distribution.csv`, `year=2024`, `measure=trc`, fields p25, p50, p75, p90, p99, `hours_weighted_rate`. Caveat: "Many small sites report zero cases; read hours-weighted rates, not medians."
5. **Productivity and investment (two bar charts).** `bench_network_headline_comparison.csv`, `cal_year_approx=2024`, `metric=revenue_per_employee_usd_k` and `metric=capex_pct_revenue`, field `value`, label with `fiscal_year_label`. Caveat: "Company-wide revenue and headcount, including AWS and international for Amazon and Walmart. Amazon capex includes AWS data centers. Walmart is the year ended Jan 2025; FedEx the year ended May 2025."
6. **Network footprint (table, no ranking).** `bench_network_facilities.csv` and `metric=network_sqft_thousand` in the headline file; show counts and area as disclosed, with the definition from `bench_network_definitions.csv`. Caveat: "Each company defines its network differently. Revenue per square foot is not shown because the denominators are not comparable."
7. **Pay against the industry (dot or range bars).** `bench_labor_announced_vs_qcew493.csv`, fields `company`, `announce_date`, `metric`, `announced_low_as_pct_of_qcew_493`, `announced_high_as_pct_of_qcew_493`, `warehouse_dc_specific`; latest row per company. Add the OEWS premium as two small bars from `bench_warehousing_industry_oews_premium.csv`, `year=2025`, occupations 53-7062 and 53-7065, fields `warehousing_493_mean_hourly_usd`, `all_industries_private_mean_hourly_usd`. Caveat: "Announced starting or average wages compared with the QCEW industry average (which includes Amazon). Not like-for-like. Several peer figures come from news reports."
8. **Labor conflict (bars, 2024).** `bench_labor_nlrb_counts_by_year.csv`, `year_filed=2024`, fields `ca_ulp_charges_vs_employer` and `ca_per_10k_employees` (not `all_cases`); FedEx shows cases only. Caveat: "Cases matched by company name only; subsidiaries are missed. Rates use worldwide headcount. UPS counts include charges against unions that name UPS."
9. **Amazon's share of warehousing employment (line).** `bench_warehousing_industry_amazon_share_493.csv`, years 2017, 2018, 2021 to 2025, fields `amazon_share_of_qcew_493_pct_estimate` and the combined 493+492 column; skip rows with `share_usable = no`. Label the series "estimate". Caveat: "Sum of Amazon's OSHA-reported average employees against QCEW employment. Not a strict bound; 2019 and 2020 are omitted because the filing coding changed."
10. **Large-site concentration (bars, 2025).** `bench_warehousing_industry_amazon_vs_qcew_size.csv`, `year=2025`, size class 1,000 or more; fields `amazon_share_of_qcew_establishments_pct`, `amazon_share_of_qcew_employment_pct`. Same caveat as chart 9.
11. **Emissions intensity (bars, latest year).** `bench_environment_intensity.csv`, one row per company at the latest period (Amazon CY2025, Walmart CY2024, Target FY2024, Home Depot FY2025, Costco FY2024, UPS 2025, FedEx FY2025), field `s12_market_g_per_usd`. Mark Target "derived". Group UPS and FedEx separately as delivery operators. Caveat: "Scope 1 and 2 only, market-based. Scope 3 is not comparable across these companies and is not shown. Amazon includes AWS data centers."
12. **Clean-energy and fleet table.** `bench_environment_renewables_fleet.csv` (fields `company`, `period`, `metric`, `value`, `unit`, `definition`, `source_url`, `page_ref`). Show the definition column next to every share. Do not use Amazon's rooftop MW row. Caveat: "Renewable shares use different definitions and are not ranked."

Page-level text:
- Intro line: "Amazon set against Walmart, Target, the other warehouse and parcel operators and the industry, from public filings and government data."
- Footer caveat: "Figures come from OSHA, BLS, NLRB, SEC filings and company sustainability reports. Companies report on different bases; the note under each chart gives the main limit. Full method and files are in data/notes/benchmark_findings.md and the bench_*.md notes."
- Each chart links to its CSV.

Open items before the integrator ships (not blockers for the page above):
- Done 2026-10-31: Target matching rebuilt (in chart 1), FedEx Ground 2024 flagged `partial_year` (a full-year Ground figure cannot be built from the files, so it stays flagged), `_lower_bound` share columns renamed, NLRB totals reconciled.
- Decide whether to add a FedEx NLRB rate from the company-wide 10-K headcount.
