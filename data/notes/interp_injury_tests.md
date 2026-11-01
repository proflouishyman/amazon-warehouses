# Injury interpretation: hypothesis tests

Question: "Is Amazon a more dangerous employer, why, and how can we tell?" Script: `scripts/interp_inj_tests.py` (run `python3 -I scripts/interp_inj_tests.py`, about 45 s, stdlib only). Every number below is read from a `data/processed/interp_inj_*.csv` file named beside it. Retrieval: OSHA ITA files as already in `data/raw/injuries` (CY2025 is partial and not used); OSHA Severe Injury Reports file `January2015toNovember2025.zip` (https://www.osha.gov/severe-injury-reports, downloaded 2026-11-01 to `data/raw/injuries/severe_injury/`).

Method shared by H1, H2, H5: same raw scan, dedupe and validity filter as `scripts/build_injury_tables.py` (rate_valid: hours >= 1000, employees >= 1, 300 <= hours per employee <= 4500, all case counts present); Amazon vs non-Amazon by `scripts/amazon_names.py`; rates are hours-weighted (cases x 200,000 / hours). `interp_inj_reconcile.csv` shows my Amazon and non-Amazon counts and hours for NAICS 493110+492110 equal `osha_ita_aggregates_by_year.csv` in every year 2016-2024 (match = True). Size band = annual average employees: <250, 250-499, 500-999, 1000+. "Size-matched" = indirect standardisation: Amazon cases divided by the cases Amazon would have had at the non-Amazon rate in each band, so the Amazon hours mix across bands is held fixed. Intervals are 95% percentile intervals from a site-level bootstrap (400 draws, fixed seed): they capture site sampling noise only, not under-recording or selection into the ITA.

Which comparator: segment `493110` (warehousing, where Amazon fulfilment and sort sites sit) and segment `492110` (couriers, where Amazon delivery stations sit since 2021) behave very differently. Non-Amazon 492110 rates (TRC 10.09 in 2024, `interp_inj_h1_matched.csv`) are about three times non-Amazon 493110 rates (3.71). The combined segment `both` is a mix of the two and moves with the mix. Every test is therefore shown for 493110 first. Note that Amazon sites coded 493110 were 685 in 2020 and 317 in 2021 while 492110 went to 573 (`interp_inj_amazon_naics_mix.csv`): delivery stations moved from warehousing codes to courier codes in 2021. The 6-digit codes exist in both NAICS vintages (the `naics_year_field` column in that file shows 2012 and 2022 vintages in the 2024 filings), so this looks like a change in how Amazon coded sites, not a redefinition of the codes; the cause is not established here.

---

## H1 SIZE: "Amazon's higher rate is because its sites are big"

Test: non-Amazon peers by size band; Amazon vs peers in the same band; size-matched ratio.

COURIER CAVEAT (applies to every comparison with 492110 or `both` in H1, H3, H4 and H5): Amazon's courier-coded sites exclude its contracted DSP drivers, who work for other employers, while UPS and FedEx hours and reports include their drivers. Courier comparisons are therefore not like for like.

Result (493110; files `interp_inj_h1_size_bands.csv`, `interp_inj_h1_within_band_ratios.csv`, `interp_inj_h1_matched.csv`):
- Peer rates barely rise with size. 2024 non-Amazon TRC by band: 3.088 (<250, 6,517 sites), 4.224 (250-499, 564), 4.334 (500-999, 300), 4.013 (1000+, 83). Amazon 2024: 5.283, 5.324, 7.715, 6.017 (84, 115, 109, 193 sites).
- Amazon is above peers in the same band in every band of 2024: TRC ratios 1.711, 1.26, 1.78, 1.499; DART ratios 2.02, 1.43, 2.087, 1.654 (`interp_inj_h1_within_band_ratios.csv`). The same holds in 1000+ in every year 2017-2024: TRC ratio 1.774, 1.733, 2.381, 1.559, 1.444, 1.572, 1.646, 1.499.
- Size-matched ratio 2024: TRC 1.526 (95% interval 1.32 to 1.786) vs crude 1.668 (peer all-size TRC 3.707, size-matched peer 4.053, Amazon 6.185). DART 1.702 (1.465 to 2.03) vs crude 1.975. So size accounts for a small part of the gap (crude 1.668 to matched 1.526). Amazon is concentrated in big sites (1000+ is 79.9% of its 2024 hours vs 10.9% of peers' hours) but big sites are not much more dangerous in this peer group.
- Matched DAFW ratio 2024 is 0.573 (0.43 to 0.814): this is the H2 shift from days-away to restricted/transferred cases, not separate evidence of lower severity or fewer lost-time injuries.
- Non-Amazon 1000+ sites (493110): 58 (2017), 67, 72, 87, 109, 128 (2022), 86, 83 (2024); hours 180,366,698 in 2024 (`interp_inj_h1_matched.csv` `peer_sites_1000plus`, `interp_inj_h1_size_bands.csv`). Small n: the 1000+ peer rate rests on 83 to 128 sites, mostly not comparable fulfilment operations (the ITA has no site-function field).
- Segment 492110: Amazon is below size-matched peers (2024 TRC ratio matched 0.52 (0.488 to 0.556)), i.e. against couriers and delivery-partner filers Amazon delivery stations look safer (courier caveat: not like for like). Segment `both` 2024 matched TRC ratio 0.883 (0.815 to 0.952), roughly equal to peers and sensitive to banding (see check below).

Verdict: NOT SUPPORTED as the explanation (against warehousing peers). Size explains little of the 493110 gap.

Banding check (`interp_inj_h1_matched_fte_band.csv`): Amazon's reported employees look like a headcount in 2019 (879 hours per employee vs 1,681 in 2024), which puts 198 of 268 sites in 1000+ by reported employees but 76 by FTE (hours/2000). Re-banding by FTE changes the 493110 matched TRC ratio from 2.359 to 2.3 (2019) and from 1.526 to 1.53 (2024), so the 493110 result holds; the `both` segment is more sensitive (2024 TRC 0.883 to 0.97).

Replication of the Senate and NELP size figures (`interp_inj_nelp_senate_replication.csv`): in 2023 Amazon is 168 of 254 valid 493110 sites with 1000+ employees (66.1%) and 78.6% of those sites' hours (736,449,138 of 937,026,216); in 2024, 193 of 276 sites and 82.0% of hours. Our data reproduce the published pattern that Amazon dominates the large-warehouse peer group.

Limits: peers are ITA filers only (establishments with 20+ employees in designated industries). Employee count is an annual average, so a seasonal-heavy site is in a band that understates its peak. Peer 493110 includes self-reported rates from 3PL and contractor sites and cannot be split by function (a retail DC and a cold-storage warehouse are different work). Matching on size does not match on work type, pace, tenure, or the share of new hires. 2017-2019 Amazon filings are fewer and less complete (see injuries.md).

---

## H2 LIGHT-DUTY SUBSTITUTION: "Amazon converts days-away cases into restricted/transfer cases"

Test: DAFW share of DART cases (dafw_cases / dart_cases); days per case. Days are capped at 180 per case at site level (OSHA's Form 300 counting limit; sites over the cap are counted in `sites_days_capped` in `interp_inj_h2_substitution.csv`, because one 2018 peer filing otherwise produced 137.97 djtr days per case in 493110, and the capped value is 42.52).

Result (493110; `interp_inj_h2_substitution.csv`, `interp_inj_h2_change_2019_2024.csv`; "size-matched peers" weight each band's peer value by Amazon's cases in that band):

| 493110, 2019 to 2024 | Amazon | non-Amazon, all sizes | non-Amazon, size-matched |
|---|---|---|---|
| DAFW share of DART | 0.6434 to 0.1732 | 0.4819 to 0.5486 | 0.4304 to 0.5166 |
| DJTR days per DJTR case | 72.5 to 58.57 | 42.9 to 47.92 | 47.62 to 52.19 |
| DAFW days per DAFW case | 52.24 to 25.61 | 41.96 to 46.06 | 47.01 to 52.63 |

- Amazon change in DAFW share, 2019 to 2024: -0.4702 (95% interval -0.5121 to -0.418). Peers: +0.0667 (0.0356 to 0.0949). Segment `both`: Amazon 0.6434 to 0.2085, peers 0.5232 to 0.5409.
- Underlying rates (segment `both`, 2019 to 2024): Amazon DAFW rate 4.989 to 1.175; DJTR rate 2.765 to 4.459; DART rate 7.755 to 5.634. Peers' DAFW 2.355 to 2.755, DJTR 2.146 to 2.338 (`interp_inj_h2_substitution.csv`).
- Amazon's lower DAFW rate relative to peers (matched DAFW ratio 0.573, H1) is this same shift, not separate evidence of lower severity.
- Timing: Amazon 493110 DAFW share 0.7795 (2017), 0.7947 (2018), 0.6434 (2019), 0.4422 (2020), 0.2514 (2021), 0.1685 (2022), 0.1725 (2023), 0.1732 (2024); peers stayed 0.45 to 0.55 throughout.
- Amazon's days per DAFW case also fell (52.24 to 25.61), the opposite of peers.

Verdict: SUPPORTED as a description (a large mix shift from days-away to restricted/transferred cases, 2019 to 2022, not seen in peers, and not explained by size). CANNOT TELL the mechanism: relabelling an injury as light duty (substitution), a genuine shift to earlier return-to-work programmes, or a change in injury severity all produce this pattern.

Limits: ITA gives counts and days only, no case-level detail (the 300/301 case files were not used). The shift pairs a fall in DAFW with a rise in DJTR; the data cannot separate a benefit to workers (earlier return to work) from lower recorded days away. Days per case are employer-reported.

---

## H3 FACILITY TYPE

Test: hours-weighted rates by type from `facilities.csv` and `facility_osha_by_year.csv` (valid facility-years only); `interp_inj_h3_type_year.csv`, `interp_inj_h3_type_band_2021_2024.csv`, `interp_inj_h3_typing_quality.csv`.

HEURISTIC TYPING FLAG: types come from `facilities_03_build_roster.py`. Only some rows are typed from a label or a list (Amazon's own "Fulfillment Centers" or "AMZL" label, TaxJar lists). Share of valid facility-years typed by heuristic: delivery_station 0.431, fulfillment_center 0.253, sort_center 0.475, other_logistics 0.998, air_hub 0.0. The label-or-list subset is reported separately (`subset` column).

Result, TRC / DART / DAFW:
- 2024: delivery station 6.897 / 6.276 / 2.573 (442 facility-years, average 226 employees, 58.4% heuristic; label-typed subset 7.059, 184 facility-years); fulfillment centre 6.115 / 5.796 / 0.997 (458, average 1,206 employees; label subset 5.838); sort centre 5.257 / 4.857 / 0.999 (137, 67.2% heuristic; label subset 3.316, 45 facility-years); air hub 5.79 (7); other_logistics 3.107 (133, all heuristic).
- 2021: delivery station 10.909, fulfillment centre 7.495, sort centre 5.948 (label subset 5.633). 2019: delivery station 14.368 (65 facility-years), fulfillment centre 8.669, sort centre 5.475 (the 2019 delivery-station group is small and early).
- Within the same size band, 2021-2024 pooled (`interp_inj_h3_type_band_2021_2024.csv`): delivery station <250: 8.845 vs fulfillment centre <250: 6.426; 250-499: 8.383 vs 6.573; 500-999: 7.842 vs 8.557; 1000+ delivery stations n = 5 only. Fulfilment 1000+ is 6.397 (625 facility-years), sort 1000+ 5.899 (label subset 4.773).
- Rates by type fell between 2019/2021 and 2024 for every type (for example delivery station 10.909 to 6.897, fulfillment centre 7.495 to 6.115).
- Against peers (courier caveat applies: Amazon delivery-station hours exclude its DSP drivers, UPS and FedEx hours include theirs): Amazon delivery stations (6.897 in 2024) are below non-Amazon 492110 (10.085, `interp_inj_h1_matched.csv`); Amazon fulfilment centres (6.115) are above non-Amazon 493110 (3.707).

Verdict: SUPPORTED that types differ (delivery stations highest, fulfilment next, sort and other lower), and it holds in the label-typed subset and within the size bands where both types exist. NOT robust for the sort-centre level (5.257 vs 3.316 depending on typing). The result does not say delivery stations are more dangerous than the courier industry; they are below it, but that comparison is not like for like.

Limits: heuristics (prefix letters and NAICS), TaxJar lists dated 2025, no "returns centre" or "cross dock" types; facility-years not facilities; the 2021 coding move between 493110 and 492110 changes which sites sit in which type from 2021. Sites change function over time and the roster types a site once.

---

## H4 SEVERE INJURIES (harder to under-record)

Test: OSHA Severe Injury Reports (SIR), events 2017-2024 (2016 not used: Amazon has 1 valid ITA establishment in 2016 against 8 SIR reports, `interp_inj_h4_severe_by_year.csv`). Amazon numerator = employer name contains "Amazon" excluding Fresh, Web Services, Go, Environmental, Amazone (contractors and DSPs without "Amazon" in the employer name are excluded; the 150 Amazon rows for 2016-2024, 142 of them in 2017-2024, are in `interp_inj_h4_amazon_sir_rows.csv`, employer name, state, NAICS and counts only). Peers = SIR primary NAICS 493110 or 492110, not Amazon. Denominator = valid ITA hours of Amazon and non-Amazon 493110/492110 filers outside state-plan states.

State plans excluded (`interp_inj_h4_state_plan_list.csv`): AK AZ CA HI IN IA KY MD MI MN NV NM NC OR PR SC TN UT VT VA WA WY, the 22 plans covering private-sector workers (source https://www.osha.gov/stateplans, retrieved 2026-11-01); the report file's own FederalState = 0 flag marks the same 22. CT, IL, ME, MA, NJ, NY and VI are public-sector-only plans, so their private workplaces are federal OSHA and are included.

**Headline method (matched).** A report counts only if its address (ZIP, street number, first three letters of street name) matches a VALID ITA filer in the SAME year and the same comparison set (Amazon valid 493110/492110 filers; non-Amazon 493110 filers; non-Amazon 492110 filers). The numerator and the hours denominator then describe the same sites, and the rule is identical for Amazon and peers. (An earlier version of this test matched Amazon reports to any Amazon address of any year or NAICS and peers to any year, an operator-precedence bug in the script; it is fixed.) Reviewer finding adopted.

**Result** (`interp_inj_h4_pooled.csv`, rows with `is_headline` True and the matched rows), per 100 million hours, 2017-2024:
- Reports, both peer groups: Amazon 78 matched reports, 2.28 per 100M; peers 567, 5.08 per 100M. Rate ratio **0.449 (exact 95% interval 0.35 to 0.57)**.
- Warehousing peers only (493110): 362 reports, 5.55 per 100M; ratio 0.411 (0.318 to 0.527). Courier peers only (492110): 205 reports, 4.42 per 100M; ratio 0.516 (0.393 to 0.673).
- Amputations (both): 10 vs 108 reports-persons; ratio 0.302 (0.141 to 0.578).
- By window, matched, both peer groups: 2017-2019 ratio 0.88 (0.562 to 1.325), not distinguishable from 1 (26 Amazon reports); 2020-2022 0.39 (0.26 to 0.567); 2021-2024 0.409 (0.291 to 0.563). 2017-2019 is unreliable in either direction because Amazon's 2017-2018 ITA hours are incomplete (early compliance), so it should not be cited as evidence either way.
- The unmatched all-report ratio, 0.28 (0.234 to 0.333; 493110 only 0.235, 492110 only 0.383), is kept in the same CSV (`numerator_set` = "BIASED LOW") but is not a headline: peer SIR reports include establishments that never file with the ITA, so peers' numerator is inflated relative to their hours. The earlier "below peers in every window" claim was wrong and is withdrawn (2017-2019 matched ratio 0.88, interval spans 1).
- Hazard mix (`interp_inj_h4_hazard_mix.csv`, 2016-2024, keyword grouping of the SIR `EventTitle`; the labels are my keyword rules): Amazon reports are 46.7% falls, slips and trips (70) and 28.7% vehicle, truck, forklift and pedestrian-struck events (43). Non-Amazon 493110 reports are 60.9% vehicle events (766) and 20.0% falls (251). Non-Amazon 492110 reports are 29.7% falls (163), 22.3% vehicle (122) and 21.0% heat, cold or environmental (115). So the peers' severe reports are dominated by forklift and vehicle events (warehousing) and by heat and driving exposure (couriers), hazards that differ from Amazon's. Part of the ratio is hazard mix, not only a difference in safety.

Verdict: SUPPORTED as a caveated observation that Amazon's severe-injury reports per hour were about 0.45 times those of peers in 2017-2024 (about 0.41 to 0.52 across comparator choices); NOT SUPPORTED that Amazon is more dangerous on this measure. Do not read it as "Amazon is safer": it does not test Amazon's documented strain and sprain pattern, which rarely leads to hospitalization or amputation.

Limits: (1) Courier comparison is not like for like (see the courier caveat below): Amazon's courier-coded sites exclude its contracted DSP drivers, while UPS and FedEx hours and severe reports include their drivers. (2) Address matching is a heuristic; unmatched Amazon reports (64 of 142 in 2017-2024: 142 all vs 78 matched) include sites coded in other NAICS or at non-filing addresses. (3) Amazon's 2017-2018 ITA hours are incomplete, inflating early Amazon rates. (4) SIR is employer-reported; Amazon rows are matched by name only. (5) 78 Amazon reports means wide year-level intervals. (6) Peer firm clustering (UPS, FedEx and other large firms) is not modelled. (7) Amazon's lower days-away rate in H2 is the DAFW-to-DJTR shift, not separate evidence of lower severity, so the `interp_inj_h4_ita_same_pool.csv` line (Amazon DAFW 2.234 vs peers 2.495, 2017-2024) must not be shown as corroboration.

Companion (`interp_inj_h4_ita_same_pool.csv`, same federal-state pool, ITA 2017-2024): Amazon TRC 6.599, DART 6.023; non-Amazon TRC 5.943, DART 4.696.

---

## H5 TREND: "Has the gap closed?"

Test: Amazon / non-Amazon ratio per year, crude and size-matched (`interp_inj_h5_ratio_by_year.csv`, `interp_inj_h5_trend_summary.csv`).

Result (493110, size-matched TRC ratio with 95% interval): 2017 1.824 (1.547 to 2.142), 2018 1.799 (1.551 to 2.05), 2019 2.359 (2.028 to 2.77), 2020 1.608 (1.424 to 1.81), 2021 1.553 (1.315 to 1.836), 2022 1.632 (1.396 to 1.914), 2023 1.685 (1.461 to 1.943), 2024 1.526 (1.32 to 1.786).
- Change 2019 to 2024: TRC -0.833 (interval -1.314 to -0.386); DART 2.512 to 1.702 (change -0.81, -1.375 to -0.308); DAFW 3.748 to 0.573 (change -3.175, -4.45 to -2.233). OLS slope 2018 to 2024: TRC -0.0765 per year, driven by the 2019 peak.
- Crude 493110 ratios: TRC 2.138 (2019) to 1.668 (2024); DART 2.422 to 1.975.
- Segment `both` (includes couriers): matched TRC ratio 1.661 (2019) to 0.883 (2024), DART 1.968 to 0.994, DAFW 2.415 to 0.425.

Verdict: the ratio is FLAT at about 1.5 to 1.7 since 2020 (493110 matched TRC 1.526 to 1.685, intervals overlap). The 2019 peak (2.359) is real, and the "decline" is measured from that peak (change 2019 to 2024 -0.833, interval -1.314 to -0.386); 2024 (1.526, 1.32 to 1.786) overlaps 2017-2018 (1.824 and 1.799, about 1.8). So the gap has not closed against warehousing peers. In the combined warehousing-plus-courier segment the matched TRC ratio is ROUGHLY EQUAL to 1 in 2024: 0.883 with banding by reported employees and 0.97 with banding by FTE (hours/2000); DART 0.994 and 1.103 (`interp_inj_h1_matched.csv`, `interp_inj_h1_matched_fte_band.csv`). This is a comparator effect (couriers have much higher rates and include drivers), not evidence that Amazon workers are as safe as warehouse workers. The collapse in the DAFW ratio (3.748 to 0.573) is the H2 mix shift, not separate evidence of lower severity.

Limits: 2019 was the highest year (Amazon 268 valid 493110 sites, 198 of them 1000+, `interp_inj_h1_matched.csv`); the 2017 to 2019 growth in Amazon filers means the 2017-2019 mix changed. COVID years 2020-2022: peer rates rose (non-Amazon `both` TRC 5.888 in 2019, 6.665 in 2020, `interp_inj_reconcile.csv`), which lowers the 2020 ratio; the ITA totals were not split into injuries vs illnesses here, so COVID cases are not separated. 2021 recoding of Amazon delivery stations from 493110 to 492110 (see Method) changes the 493110 and 492110 Amazon site sets between 2020 and 2021 (685 to 317 sites in 493110, `interp_inj_amazon_naics_mix.csv`); the within-1000+-band ratio (`interp_inj_h1_within_band_ratios.csv`) is the least affected by that move and shows the same shape (TRC 2.381 in 2019, 1.559 in 2020, 1.499 in 2024).

---

## Hypotheses this data CANNOT test

| Hypothesis | Why not | Data that would test it |
|---|---|---|
| Pace / rate quotas (rate of work, Time Off Task) | ITA has no work-pace field | Amazon rate or TOT data by site; state or federal inspection files (OSHA inspections at Amazon sites, Washington L&I, Senate HELP); site-level throughput (units per hour) |
| Turnover, tenure and new-hire share | ITA has hours and an annual average headcount, not who is injured | Site-level turnover (WARN or state UI wage records, Amazon filings), BLS injury tables by tenure, Form 301 case detail with hire date |
| Contractors and temp staff | ITA counts the filing employer; DSP drivers and staffing-agency workers file separately or not at all | DSP/agency filings by name (partial in ITA), OSHA inspection records with contractor name, state workers' compensation claims by employer |
| Peak season (Prime Day, Q4) | ITA is annual | Form 300 case-level dates (the 2023 rule's case-detail file for large filers), workers' comp claims by month |
| Injury type and body part (strain vs fracture) | The 300A has no case detail | ITA case-detail files (Form 300 and 301) for 2023 onward |
| Under-recording or over-recording | ITA is self-reported | Audit studies, workers' compensation claims matched to the OSHA log |
| Cause of the DAFW to DJTR shift (H2 mechanism) | Counts only | Case-level days away and return-to-work dates; Amazon's workers' comp claims |
| Severe injury rate with a matched denominator (H4) | SIR covers non-filers | BLS CFOI/SOII severity tables by size; SIR joined to employer establishment lists |

## Reproduce
`python3 -I scripts/interp_inj_tests.py` writes the 20 `interp_inj_*.csv` files in `data/processed/`. The SIR zip and extracted CSV are in `data/raw/injuries/severe_injury/` (`RETRIEVED.txt` has the date).
