# Retail county test: did counties that gained an Amazon fulfillment center lose more retail establishments?

Run 2026-11-01. Script: `scripts/interp_retail_county_test.py` (`python3 -I`, stdlib only; numpy, pandas and statsmodels are not installed, so the bootstrap and the fixed-effects regression are hand-written). Public data only. This is descriptive event-study evidence, not causal proof.

Outputs (all numbers below are read from these):
`data/processed/interp_retail_fc_county_map.csv` (FC to county), `interp_retail_event_study.csv`, `interp_retail_pooled_regression.csv`, `interp_retail_pretrends.csv`, `interp_retail_sample_counts.csv`.

## Hypothesis
Counties that gained an Amazon fulfillment center (FC) lost more local retail stores afterwards than similar counties that did not.

## Data
- Facilities: `data/processed/facilities_master.csv`, `facility_type == fulfillment_center` (688 rows; 658 have coordinates). Every one of the 658 was mapped to a county FIPS with the Census coordinates geocoder (Public_AR_Current, Current_Current), responses cached in `data/raw/retail_context/cbp_county/census_coordinates_cache.json`. The 30 FCs with no coordinates are not mapped (they could sit in the control pool; small contamination).
- Opening year column: `year_used`, restricted to a defensible subset: `year_basis` in {mwpvl_opening_year, epi_mwpvl2012_opening_year, press_event_year} and `year_flag` not containing `year_after_first_osha_filing` or `projection`. Rows whose year comes from `first_osha_filing` (an upper bound on opening, not an opening) are NOT used in the primary specification. A county's treatment year is its earliest such FC year. Counties with an undated or weak-basis FC that could predate the strong year are dropped from all groups (flag `county_ambiguous`). Sensitivity run 3 adds the OSHA-bound years back.
- CBP: County Business Patterns county files 2010-2023 (`cbpYYco.zip`), establishments (`est`, March of each year, all employer establishments), in `data/raw/retail_context/cbp_county/` (gitignored). Codes: 44---- retail total, 452/// general merchandise, 448/// clothing, 443/// electronics and appliance, 451/// sporting goods, hobby, book, music, placebos 4451// grocery and 722/// food services. NAICS vintage: files 2010-11 use NAICS 2007, 2012-16 NAICS 2012, 2017-23 NAICS 2017 (county files never carry NAICS 2022, so 455 and 449 do not appear). The 3-digit totals used here exist in every vintage; the 2017 break moved establishments among 4-digit and 6-digit classes inside 452 (department stores, discount stores, warehouse clubs) and may shift the 452 count slightly in 2017. Because every series is indexed to its own t-1 and compared with controls in the same calendar years, a break affects treated and controls alike.
- Population: Census county estimates `co-est2019-alldata.csv`, CENSUS2010POP, used for size bands (<10k, 10-25k, 25-50k, 50-100k, 100-250k, 250-500k, 500k-1M, 1M+) and Census region. Connecticut is dropped (CBP uses the old counties, the facilities table the new planning regions, so FIPS do not match; 7 CT planning-region FIPS).

## Method
- Treated: counties whose first strong-basis FC opened 2013-2019: 87 counties (cohorts 2013: 6, 2014: 8, 2015: 21, 2016: 21, 2017: 12, 2018: 9, 2019: 10). Event time k = year minus the opening year; each county-sector series is indexed so that the establishment count at t-1 = 100 (CBP counts March establishments, so a mid-year opening first shows in t+1; t-1 is the clean base).
- Control A, not-yet-treated: first FC 2021 or later (44 counties). Control B, never-treated: 2,648 counties with no FC and no other Amazon facility (any type) in the facilities table.
- Matching: each treated county takes all controls in the same state and 2010 population band; if none, the same Census region and band. Matched pools: never-treated 29 state-band and 32 region-band matches (61 treated counties matched), mean 4.6 controls each; not-yet-treated 15 and 49 (64 treated matched), mean 2.2 controls each. Controls get the treated county's event year as a pseudo event year. For not-yet-treated controls, observations from their own first-FC year on are dropped. A county-sector enters an index only if it has at least 5 establishments at t-1.
- Statistic: per treated county, treated index minus the mean index of its matched controls, averaged over counties, with a percentile bootstrap over treated counties (2,000 draws, seed 20261101). Units are index points (1 point = 1% of the t-1 establishment count).
- Pooled regression: ln(establishments + 1) on county FE, year FE and a post-FC indicator (year >= opening year, treated cohort 2013-2019 only), standard errors clustered by county (small-sample adjusted). A second specification replaces year FE with Census region x size band x year FE. Samples: the matched sample (treated plus the controls used) and all eligible counties. Not-yet-treated counties contribute only years before their own FC.
- Population is a covariate proxy only: 2010 Census population. CBP employment was not used.

## Results (primary specification, exact numbers from the CSVs)

Treated counties are bigger than their matched controls even within a band: 2010 mean log population 12.863 vs 12.678 (diff 0.185, CI 0.129 to 0.242); 2010 retail establishments 1,693.5 vs 1,301.0 (diff 392.5, CI 231.8 to 562.6). Population growth 2010-2019 was the same: ratio 1.0897 vs 1.0913 (diff -0.0017, CI -0.0233 to 0.0209, n=61). So in this sample the FC counties were not faster-growing than matched counties by population, even though the prior is that FCs are sited in growing suburban and exurban counties (which would bias the test toward MORE retail growth in treated counties). That bias cannot be excluded: population growth is measured only to 2019 and only on a coarse match.

Event study, difference in the retail index (treated minus matched controls), index points, 95% bootstrap CI (file `interp_retail_event_study.csv`):

| Sector | vs | k=-3 | k=-2 | k=+1 | k=+2 | k=+3 | k=+4 |
|---|---|---|---|---|---|---|---|
| Retail total | never-treated (n=61) | -0.50 [-1.25, 0.25] | -0.40 [-0.91, 0.11] | -0.08 [-0.89, 0.64] | 0.57 [-0.38, 1.51] | 1.01 [0.02, 2.02] | 1.08 [-0.08, 2.25] |
| Retail total | not-yet-treated (n=64; 56 at k=4) | 0.80 [0.10, 1.49] | 0.21 [-0.35, 0.74] | -0.02 [-0.93, 0.92] | 0.17 [-0.94, 1.31] | 0.03 [-1.23, 1.25] | -0.36 [-1.94, 1.13] |
| General merchandise | never | -1.84 [-4.81, 0.99] | -3.18 [-5.43, -0.94] | 0.18 [-2.78, 3.03] | 3.49 [-0.73, 8.71] | 3.34 [-1.42, 9.10] | 4.81 [-0.14, 10.75] |
| General merchandise | not-yet | 0.23 [-1.94, 2.36] | -0.87 [-2.33, 0.63] | 0.55 [-1.12, 2.24] | 2.29 [-1.31, 7.00] | 1.98 [-2.26, 7.72] | 0.39 [-2.80, 3.43] |
| Clothing | never | 1.72 [-0.86, 4.66] | 0.70 [-0.71, 2.41] | -2.54 [-4.92, -0.21] | -2.61 [-5.93, 0.60] | -1.67 [-5.55, 2.41] | -3.07 [-8.32, 1.70] |
| Clothing | not-yet | 2.01 [-0.84, 5.18] | 0.43 [-1.62, 2.54] | -1.43 [-4.58, 1.58] | -0.58 [-3.89, 3.18] | 0.48 [-2.96, 4.36] | 0.34 [-4.83, 5.31] |
| Electronics and appliance | never | -4.57 [-10.48, 1.11] | -4.32 [-7.22, -1.38] | -0.96 [-5.01, 2.64] | 0.54 [-4.16, 4.45] | 0.58 [-3.31, 3.93] | -1.08 [-4.54, 2.20] |
| Electronics and appliance | not-yet | 1.62 [-3.26, 6.96] | -2.68 [-5.92, 0.44] | -2.96 [-7.20, 0.61] | -3.54 [-8.06, 0.59] | -3.55 [-8.10, 0.35] | -4.42 [-8.94, -0.46] |
| Sporting, hobby, book | never | 1.20 [-2.39, 4.58] | -0.36 [-2.66, 1.80] | 0.10 [-2.89, 2.82] | -0.36 [-3.36, 2.67] | -1.05 [-3.87, 1.90] | -2.93 [-6.84, 0.74] |
| Sporting, hobby, book | not-yet | 1.04 [-2.40, 4.38] | 1.25 [-0.85, 3.35] | -0.93 [-3.54, 1.78] | -2.09 [-4.86, 0.85] | -3.96 [-7.38, -0.90] | -5.87 [-9.87, -2.19] |
| Placebo: grocery 4451 | never | 0.92 [-1.49, 3.55] | 0.39 [-1.58, 2.46] | 0.52 [-2.72, 4.08] | 1.95 [-1.52, 5.73] | 2.41 [-1.42, 6.71] | 2.80 [-1.24, 7.09] |
| Placebo: grocery 4451 | not-yet | 1.62 [-0.78, 4.07] | 1.54 [-0.34, 3.38] | 0.25 [-2.79, 3.17] | -0.68 [-4.22, 2.79] | -0.50 [-4.24, 3.94] | 0.05 [-4.71, 4.65] |
| Placebo: food services 722 | never | -0.52 [-1.44, 0.39] | 0.02 [-0.76, 0.82] | 1.13 [-0.06, 2.37] | 1.89 [0.40, 3.51] | 2.20 [0.38, 4.10] | 3.29 [1.34, 5.26] |
| Placebo: food services 722 | not-yet | -0.62 [-1.67, 0.33] | -0.09 [-0.85, 0.70] | 1.20 [-0.06, 2.40] | 0.96 [-0.60, 2.57] | 0.99 [-0.90, 3.00] | 1.40 [-0.84, 3.58] |

Raw retail-total indexes at k=+4: treated (matched to never-treated) 98.40 [97.19, 99.47], never-treated controls 97.32 [96.28, 98.43]; treated (matched to not-yet-treated) 98.19 [96.99, 99.37], not-yet-treated controls 98.54 [97.18, 99.94]. Total retail establishments fell about 1.6 to 1.8% in treated counties over the four years after opening, but they fell about as much, or more, in the comparison counties (national retail establishment counts were flat to falling over the period).

Pooled regression, coefficient on post-FC in ln(establishments+1), cluster-robust by county (file `interp_retail_pooled_regression.csv`; 87 treated counties in each):

| Sector | Matched sample, county+year FE | Matched, region x band x year FE | All eligible counties, region x band x year FE |
|---|---|---|---|
| Retail total | 0.0027 (se 0.0076), +0.27% | 0.0062 (0.0082), +0.62% | 0.0076 (0.0081), +0.76% |
| General merchandise | -0.0273 (0.0150), -2.69% | 0.0371 (0.0161), +3.78% | 0.0351 (0.0159), +3.57% |
| Clothing | -0.0530 (0.0211), -5.16% | -0.0499 (0.0342), -4.86% | -0.0426 (0.0339), -4.17% |
| Electronics and appliance (83 treated) | -0.0681 (0.0240), -6.58% | -0.0557 (0.0353), -5.42% | -0.0553 (0.0355), -5.38% |
| Sporting, hobby, book (82 treated) | -0.0511 (0.0147), -4.98% | -0.0379 (0.0189), -3.72% | -0.0377 (0.0189), -3.70% |
| Placebo: grocery 4451 (86) | 0.0225 (0.0169), +2.27% | 0.0205 (0.0172), +2.07% | 0.0284 (0.0180), +2.88% |
| Placebo: food services 722 | 0.0139 (0.0097), +1.40% | 0.0210 (0.0113), +2.12% | 0.0233 (0.0116), +2.36% |

The all-eligible-counties specification with only county and year FE gives large positive coefficients for retail total (+3.35%) and for both placebos (+13.5% grocery, +9.4% food services); that is the "FC counties are growing, large and suburban" bias in plain view, and the region x band x year FE removes most of it. 

Sensitivity (file `interp_retail_event_study.csv`, k=+4, retail total, difference vs never-treated / vs not-yet-treated): allowing counties with other Amazon sites into the never-treated pool 0.53 [-0.43, 1.43] (n=82) / -0.36 [-1.86, 1.07]; adding OSHA-bound opening years 1.22 [0.05, 2.36] (n=63) / 0.09 [-1.35, 1.49].

## Verdict
**Not supported for retail as a whole; cannot tell for specific store types.**
- Retail total: the establishment count in FC counties did not fall relative to matched counties. At t+4 the difference is +1.08 index points vs never-treated (CI -0.08 to +2.25) and -0.36 vs not-yet-treated (CI -1.94 to +1.13); the pooled coefficient is +0.27% to +0.76%. The CIs rule out a relative decline larger than about 2 percent of establishments.
- General merchandise: not negative (positive in most specifications).
- Clothing, electronics, sporting/book goods point negative (pooled -3.7% to -6.6%; not-yet-treated event study at t+4: electronics -4.42, sporting/book -5.87), the pattern that e-commerce displacement would predict. But these are weakly supported: the never-treated comparison is mostly inside the CIs, the clothing and electronics pooled estimates lose significance with the finer fixed effects, electronics shows a gap of -4.32 already at k=-2 (a pre-trend), and the signs flip across comparison groups in general merchandise. Fifteen-plus sector-by-group-by-horizon comparisons were made without correction.
- Placebo: food services rose relative to never-treated counties (+3.29 at t+4, CI 1.34 to 5.26) and grocery moved the same way (+2.80, CI -1.24 to 7.09). The placebo sector does not show a flat line, it shows relative growth. That fits FC counties growing in ways the matching does not capture, or Amazon payroll spending (Chava et al. also report food-service job gains), and it means any retail comparison is biased toward finding less loss than would exist with a clean control.

## Comparison with Chava, Oettl, Singh, Zeng (NBER w30077, "Creative Destruction? Impact of E-Commerce on the Retail Sector", May 2022; Management Science 2024)
From the NBER abstract page (opened 2026-11-01; the full paper and its design details were not read): store-level data on 3.2 million stores find sales at nearby stores fall about 4% and store employment about 2.1%, with store exits up (especially young and small stores) and entry down; payroll records for 2.6 million retail workers show a 2.4% income fall in proximate counties; about 938 retail jobs lost per county per quarter, offset by +256 in transportation and warehousing and +143 in food services. How this test differs: (1) their outcomes are sales, employment and exit and entry flows measured at store or worker level; this test uses stock counts of establishments, which move only when a store opens or closes, so a 4% sales fall can happen with no change in the count; (2) their exposure is "proximate counties" to FC rollout with an e-commerce firm's staggered openings; this test uses the county that hosts the FC, so neighbors that lose shoppers are in the control group (spillover bias toward zero); (3) they use proprietary store and payroll panels; this test uses public CBP; (4) their exits are net of entry; CBP nets entry and exit, and their finding of both more exits and fewer entries implies small net count changes. This test therefore does not contradict their result; it shows no retail-wide fall in the establishment count in the host county, with weak signs of fewer clothing, electronics and sporting/book stores.

## Limits
- Facility openings: the opening year comes from MWPVL, EPI and press records (563 FC rows via MWPVL, 3 press, 2 EPI of 688; 102 FC rows rest only on a first OSHA filing year, an upper bound, and are excluded from the primary run). Some MWPVL years are flagged as conflicting (`mwpvl_year_conflict`, kept). Timing errors blur event time.
- 87 treated counties (61 to 64 matched) is small; sector CIs are wide.
- Establishment counts are a stock and a weak proxy for sales; small shops, chains' closures and openings net out. CBP excludes non-employers and the self-employed.
- Host county only: no spillovers to neighboring counties; the FC may also be in a county adjacent to a larger retail market.
- Matching is on state or region, size band and nothing else (no pre-trend or income matching). Treated counties are larger than their matches within a band. Pre-trends are not flat in some sectors (electronics, general merchandise vs never-treated at k=-2).
- 2020-2023 span COVID and the post-2020 closure and delivery surge; the pseudo event years in controls share the same calendar, but cohorts 2018 and 2019 reach t+4 in 2022 and 2023.
- Not-yet-treated controls are few (44, mean 2.2 per treated county) and themselves chosen because they were next in line for an FC, a selection that helps comparability but may share unobserved shocks.
- Other Amazon facilities (delivery stations, sort centers) in treated counties are not separated out; the primary controls exclude counties with any Amazon facility in the table, but the table is a lower bound (see `facilities.md`). 30 FCs have no coordinates; Connecticut is excluded.
- Descriptive, not causal: no instrument or randomization, and the placebo result shows the comparison is imperfect.
