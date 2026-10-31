# BENCHMARK: the warehousing industry as a whole (NAICS 493)

Retrieved 2026-10-31. Scripts: `data/raw/benchmark/warehousing_industry/_scripts/` (run with `python3 -I`; `build_qcew_cbp_ec.py`, `build_ec.py`, `build_oews.py`, `build_share_oews.py`, `parse_cbp.py`; `browser_download.py` fetches BLS files through the debug Chrome request context because bls.gov returns 403 to curl). No WebSearch and no search-engine queries were used (0 of 30 browser searches). The JHU databases were not touched. Reused existing files: `bls_qcew_naics49x_national_state_annual.csv`, `osha_ita_aggregates_by_year.csv`, `osha_ita_amazon_establishments.csv`, `amazon_employees_by_year.csv`, `logistics_osha_site_counts_by_year.csv`.

## Files (all in data/processed/, every row carries `source`/`source_url`)
| File | Rows | Content |
|---|---|---|
| bench_warehousing_industry_qcew_national_annual.csv | 455 | QCEW national annual averages 2001-2025, NAICS 493/4931/493110/492/4921/4922, all ownership codes: establishments, employment, wages, weekly wage, annual pay. Copied from the labor-domain file (US000 rows) with titles and source URLs. |
| bench_warehousing_industry_qcew_size_class_q1.csv | 645 | QCEW national private employment and establishments by ESTABLISHMENT SIZE CLASS (<5 ... 1000+), Q1 only, 2014-2025, same NAICS list. New download (https://data.bls.gov/cew/data/api/{year}/1/size/{code}.csv). Size data before 2014 are not on that API (gap). |
| bench_warehousing_industry_cbp_size_class.csv | 1,380 | Census County Business Patterns, national, NAICS 493/4931/493110/492/4921/4922 by employment-size class, 2001-2023 (mid-March employment, establishments, payroll). 2024 file not published at retrieval. |
| bench_warehousing_industry_economic_census.csv | 389 | Economic Census 2017 and 2022, national: NAICS 493 (and 4931, 49311, 493110, 49312-49319 detail) plus 492; basic statistics and by establishment employment size (firms, establishments, receipts, payroll, employees). |
| bench_warehousing_industry_oews_wages.csv | 206 | BLS OEWS national May estimates 2003-2025: warehousing (493000), couriers (492000), all industries private (000001, 2009-2025): occupations 00-0000 (all), 53-7062, 53-7064, 53-7065 (employment, RSE, mean/median wages). Occupation 53-7051 was extracted to raw only. |
| bench_warehousing_industry_oews_premium.csv | 76 | Derived: warehousing mean hourly wage vs all-industries private, ratio, and warehousing share of national occupation employment (2009-2025). |
| bench_warehousing_industry_amazon_share_493.csv | 10 | Amazon (OSHA ITA estimate) as share of QCEW NAICS 493 employment, 2016-2025, with sensitivities. Share columns are named `*_pct_estimate` (renamed from `*_lower_bound` on 2026-10-31); `share_usable` is `no` for 2016, 2019 and 2020, and the 2019-2020 share values are blank. |
| bench_warehousing_industry_amazon_vs_qcew_size.csv | 54 | Amazon 493110 ITA sites by size class vs QCEW 493 establishments by size class, 2017-2025; `usable` is `no` and the two share columns are blank for 2019 and 2020. |

Raw: `data/raw/benchmark/warehousing_industry/` (172 MB: CBP zips and unzipped txt, Economic Census zips and dats, `qcew_size/`, `oews/oews_national_extract_2007_2025.csv` plus two BLS HTML pages). Recommend gitignoring `cbp/x_*`, `cbp/*.zip`, `cbp/*.txt`, `econ_census/x*`, `econ_census/*.zip`. The 23 OEWS zips (about 400 MB) were kept in the session scratchpad, not the repo; the extract and the zip URLs are recorded. A stray `oews/oesm24nat.zip` is a small test download (kept; nothing deleted).

## Headline industry baseline (QCEW, private, national)
- NAICS 493: 510,640 employees and 12,769 establishments (2001) to 1,901,976 and 23,345 (2025). Average annual pay $32,094 to $56,706 (nominal). 493110 is 1,764,202 of the 2025 total (93%). 4931 equals 493 in every year (4931 is the only 4-digit industry in 493).
- Growth is concentrated after 2019: 1,249,145 (2019) to 1,905,515 (2022), +53%, then flat (1,860,591 in 2023; 1,901,976 in 2025). 
- NAICS 492 (couriers): 596,899 (2001), 564,346 (2014), 818,088 (2019), 1,120,618 (2025).
- Concentration by establishment size (Q1, private 493, `qcew_size_class_q1`): establishments with 1,000+ employees held 10.1% of employment in 2014 (44 establishments) and 41.9% in 2025 (351 establishments, about 797,000 employees). Establishments with 250+ held 51.0% to 73.0%.
- Weekly wage by size in Q1 2025: 1,000+ establishments $924 versus $1,438 for establishments under 5 employees and $1,091 for the 493 annual average. (2019: $627 for 1,000+.) Large-site pay is lower; Q1, part-time mix and the size-class definition are not controlled.
- CBP and Economic Census give lower levels than QCEW for 493: CBP/QCEW employment ratio 0.99 (2005), 1.02 (2012), 0.90 (2017), 0.82 (2019), 0.68 (2022), then 0.89 (2023, CBP jumps from 1.295M to 1.649M while QCEW falls). Economic Census employees: 921,320 (2017; QCEW 1,018,613) and 1,353,169 (2022; QCEW 1,905,515). Cause of the 2017-2022 gap is not established here; a plausible, UNVERIFIED reading is that Census assigns some very large multi-establishment employers to other industries. Treat CBP/EC denominators as a sensitivity, not as a correction. EC 2022 250+ establishments: 604 (250-499) plus 608 (500+, 633,598 employees); EC 2017 250+: 842 establishments, 510,599 employees.
- CBP 2001-2002 NAICS 493 employment (145,266; 149,409) is a fraction of 2003 (543,330); flagged as a break in the file, do not trend through it.

## OEWS wages (May, national)
- Warehousing 53-7062 laborers/movers mean hourly: $13.70 (2010), $16.16 (2019), $19.55 (2022), $21.82 (2025). All-industries private: $12.31, $15.42, $18.02, $20.30. Warehousing premium ratio 1.11 (2010), 1.05 (2019), 1.09 (2022), 1.08 (2025).
- 53-7065 stockers/order fillers 2025: $22.09 warehousing vs $18.96 all private (ratio 1.17); 53-7064 hand packers: $20.97 vs $18.04 (1.16). Warehousing employment 2025: 53-7062 433,060; 53-7065 457,740; 53-7064 74,380.
- Warehousing share of national employment in the occupation rose: 53-7062 7.6% (2010) to 14.9% (2025); 53-7065 16.3% (2025).
- All-occupations mean hourly: warehousing $17.17 vs all-industries private $20.73 (2010, ratio 0.83) and $25.81 vs $33.14 (2025, 0.78): the industry is a lower-paying mix overall but pays a premium for the same hand-labor occupations.
- OEWS 493000 total employment 1,963,680 (2025) vs QCEW private 1,901,976 (OEWS includes government and is a 3-year-panel estimate; not the same measure).
- Caveats: OEWS is a survey with relative standard errors (columns kept); wages are straight-time hourly, exclude benefits and many bonuses; NAICS vintage changed (2012 to 2017) but 493 is unchanged; occupations are SOC 2010 to 2018; 2003-2008 have no cross-industry comparator in the extract (the national-owner file starts 2009 in my parse).

## Amazon share of NAICS 493 employment: method and uncertainty
Estimate = sum of OSHA ITA Form 300A annual average employees over Amazon-classified establishments filed under NAICS 493110 (deduped per establishment-year, `osha_ita_aggregates_by_year.csv`) divided by QCEW private NAICS 493 annual average employment.
This is an ESTIMATE of Amazon's US warehouse employment, not a strict bound. It is probably low for these reasons: Amazon does not disclose US logistics headcount (10-K gives worldwide total only, kept as a reference column, 1,576,000 in FY2025); ITA covers only filing establishments (warehousing sites with 20+ employees must file; compliance was low in 2016-2018); sites filed under non-Amazon names are missed; staffing-agency workers are employed by agencies (QCEW 5613) and are not in the numerator or the denominator.
It is not a strict lower bound on the share, because the numerator may include sites that QCEW does not code to 493 (see size check), which pushes the other way. The columns were named `_lower_bound` until 2026-10-31 and are now `_estimate`.

Results (`amazon_share_493`, share of QCEW 493 private, estimate; 2019 and 2020 are unusable and their shares are blank in the CSV; the 2019-2020 numerator values below are shown only to explain why):
| Year | ITA 493110 | Share | Combined 493110+492110 vs QCEW 493+492 |
|---|---|---|---|
| 2017 | 189,217 | 18.6% | 11.2% |
| 2018 | 232,290 | 20.3% | 12.5% |
| 2019 | 506,227 | unusable (was 40.5%) | unusable (was 24.5%) |
| 2020 | 570,873 | unusable (was 38.8%) | unusable (was 23.4%) |
| 2021 | 376,775 | 22.2% | 20.1% |
| 2022 | 510,349 | 26.8% | 23.8% |
| 2023 | 546,960 | 29.4% | 25.6% |
| 2024 | 611,272 | 32.3% | 27.8% |
| 2025 | 637,242 | 33.5% | 28.3% |
- Use only 2017, 2018 and 2021 onward (2019 and 2020 are withheld). The combined column is steadier: in 2019-2020 delivery stations were filed under 493110, which inflates the 493110 line (2019-2020 about 39-41%), and in 2021 they moved to 492110 (182,132 employees in 2021), which produces the 2021 drop. 2016 (1 site) is unusable; 2017-2018 are understated by low ITA compliance.
- The two project files disagree for 2019: aggregates 506,227 (268 sites) vs `logistics_osha_site_counts_by_year.csv` 634,441 (358 sites). Both are in the share CSV (`alt_project_file_...`). The reviewer's recount from the establishment file gives 639,067, which supports the larger figure, so 2019 is unusable under either number.
- Sensitivity to the denominator: with CBP NAICS 493 March employment the 2023 share is 33.2% (2022: 39.4%; CBP is lower than QCEW so shares are higher; shown for 2016-2023 only).
- ITA coverage check: all ITA 493110 filers (Amazon plus others) over QCEW 493 is 70-80% in 2021-2025 (96% in 2019, inflated by delivery stations). Roughly, ITA captures most of the industry, but this also counts non-493 sites, so it is not a pure coverage rate.
- Size check (`amazon_vs_qcew_size`): in 2025 Amazon 493110 ITA sites with 1,000+ average employees number 204 (489,529 employees) versus 351 QCEW 493 establishments of that size (797,083 employees), i.e. 58% of establishments and 61% of employment in that class. In 2019 the ITA count (250 sites, 571,613 employees) EXCEEDS the QCEW class (169 establishments, 312,932), and 2020 is 98%. A ratio over 100% proves part of the ITA numerator is not in QCEW 493 (or its size is measured differently: ITA is a calendar-year average by site, QCEW class is Q1 by establishment). So treat 2019-2020 as not comparable, and read 2025 shares as indicative: the Amazon share of 493 employment is more likely in the low 30s percent than near 50%, but the true figure is not identified.
- Statements not supported: the share of ALL warehousing capacity (square feet) or of establishments; Amazon's share of establishments is small (about 500 of 23,000 sites, 2%) while large sites dominate employment.

## Gaps
- QCEW size classes before 2014; QCEW by size for 2001-2013 exists only in the large annual files (not downloaded).
- Economic Census 2012 and earlier by size (2017 and 2022 only); CBP 2024+.
- OEWS 2003-2008 cross-industry comparator; OEWS by-industry detail below 3-digit NAICS (493110) was not extracted (the 4-digit file exists in the same zips).
- Census API needs a key (not requested); static files used instead.
- No independent Amazon US headcount, so no upper bound; the share cannot be bracketed from above.
- Cause of the CBP/EC vs QCEW divergence (2017-2022) and the CBP 2023 jump is not established.
- Temporary-agency workers (NAICS 5613) in warehouses are excluded throughout.
