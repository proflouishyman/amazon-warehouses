# LABOR domain notes

All retrieval dates 2026-10-31. Scripts in scripts/ (run with `python3 -I`). Raw downloads in data/raw/labor/. No JHU subscription sources used (no ProQuest/Statista). No data/private files written. No individual worker data; NLRB participant tables (names of lawyers, charging parties) were deliberately not extracted.

## 1. Amazon employees by year (10-K)
- File: data/processed/amazon_employees_by_year.csv (29 rows, FY1997-FY2025). Built by scripts/build_employees.py from the 10-K text in data/raw/labor/10k/.
- Source: SEC EDGAR, Amazon.com Inc. (CIK 1018724) annual reports, "Employees"/"Human Capital" section. Each row has accession number, URL and the quoted sentence.
- Coverage: year-end headcount, WORLDWIDE, full-time and part-time (FY1997 is full-time only). Excludes independent contractors and temporary/seasonal personnel (Amazon says it uses these in addition). FY1997 = 614; FY2025 = 1,576,000 (10-K filed 2026-02-06).
- Caveats: not US-only, not warehouse-only. Amazon rounds to the nearest hundred or thousand. The 2000-09 and 2011-02 10-K/A filings were skipped.

## 2. Announced wages (company announcements)
- File: data/processed/amazon_wage_announcements.csv (9 rows, 2018-2025). Built by scripts/build_wages.py; the page text was fetched and checked against the quoted wording (raw HTML in data/raw/labor/wages/).
- Sources: Amazon press releases / aboutamazon.com (URLs per row). Metric definitions DIFFER by year (minimum wage 2018; average starting pay 2021-2022; average hourly/base pay 2023-2025; total compensation incl. elected benefits 2024-2025). Values are the "more than X" floor Amazon states. Do not chart as one clean series without labelling the changes.
- The Sept 2021 "$18" row is taken from the Sept 2022 release ("increasing from $18 to more than $19"); the Sept 2021 announcement itself was not retrieved. The May 2021 "$17 plus up to $1,000 sign-on" row is primary.
- Gaps: 2019-2020 (COVID +$2/hr temporary premium in 2020 was seen only in an April 2020 blog and is not tabulated), pre-2018 starting wages, and any 2026 announcement (none found).

## 3. BLS QCEW, NAICS 493 / 4931 / 493110 and 492 / 4921 / 4922
- Files:
  - data/processed/bls_qcew_naics49x_national_state_annual.csv (11,672 rows): national (US000) and 50 states + DC (+PR), all ownership codes, annual averages.
  - data/processed/bls_qcew_naics49x_county_private_annual.csv (243,114 rows): county level, PRIVATE ownership (code 5) only.
  - Columns: year, area_fips, area_title, geo_level, state_fips, naics, ownership, establishments, avg_employment, total_annual_wages, avg_weekly_wage, avg_annual_pay, disclosure_code.
- Source: BLS Quarterly Census of Employment and Wages. 2014-2025 from the CEW Open Data API (https://data.bls.gov/cew/data/api/{year}/a/industry/{naics}.csv); 2001-2013 from the annual-by-industry zips (https://data.bls.gov/cew/data/files/{year}/csv/{year}_annual_by_industry.zip). Area titles: https://data.bls.gov/cew/doc/titles/area/area_titles.csv. Built by scripts/build_qcew.py.
- Coverage: 2001-2025, annual. NAICS 493 US private: 510,640 employees in 2001 -> 1,901,976 in 2025; avg weekly wage $617 -> $1,091. NAICS 492 US private: 564,346 (2014) -> 1,120,618 (2025).
- Caveats: (a) NAICS 493 is all warehousing, NOT Amazon only; Amazon is a large but unknown share and QCEW does not identify employers. (b) County cells with disclosure_code N are suppressed (employment 0 in file); do not read them as zero. (c) 2024 and 2025 are the latest BLS releases and may be revised. (d) QCEW does not identify employers, so the 493 series describes the whole industry and cannot be read as Amazon employment. (An earlier draft claimed many Amazon FCs are coded outside NAICS 493; that claim had no source and was removed. Amazon's own OSHA filings are mostly 493110 and, from 2021, 492110.) (e) Pre-2001 (SIC-based) not included. (f) Temp-agency workers staffed to warehouses are in NAICS 5613, not 493.
- 13 raw zip files (2001-2013, about 1.8 GB) in data/raw/labor/*.zip are too large for the public repo; gitignore data/raw/labor/*.zip and data/raw/labor/cew_extract/.

## 4. County warehouse employment in counties with Amazon sites
- Files: data/processed/amazon_site_counties_naics493_annual.csv (county-year rows for NAICS 493/4931/493110, with number of listed sites by type), amazon_site_counties_naics493_summary.csv (year totals), amazon_site_county_match_unmatched.csv.
- Method: scripts/build_site_county_qcew.py joins data/processed/facilities.csv (county name + state; produced by the facilities domain, low-confidence rows included, e.g. TaxJar-list rows) to QCEW county FIPS by normalised name. 476 counties matched; 44 facility rows unmatched (29 with no county, one apparent data error "Pulaski, AZ"). Rerun after facilities.csv is finalised.
- Caveats: descriptive only. A county "with a site" is a county with a currently listed site, whatever its opening year (earliest listed opening year is carried where known), so no causal reading of employment change is supported. Disclosed-county sums cover roughly 66-76% of US private NAICS 493 employment (summary file shows suppressed counts).

## 5. NLRB cases involving Amazon
- Files: data/processed/nlrb_amazon_cases_search_index.csv (984 cases from the search listing), nlrb_amazon_cases.csv (same 984 with detail-page fields), nlrb_amazon_election_tallies.csv (7 tallies in 6 RC cases).
- Source: NLRB public case search, https://www.nlrb.gov/search/case/amazon (list pages 0-98) and each https://www.nlrb.gov/case/{number} page. Raw HTML in data/raw/labor/nlrb/. Scripts: nlrb_list_crawl.py, nlrb_parse_list.py, nlrb_detail_crawl.py, nlrb_parse_detail.py.
- Contents: 916 CA (unfair labor practice charges against employer), 55 CB (charges against unions, mostly cases naming a union and Amazon), 13 RC (representation petitions; 6 with tallies). Fields: number, name, filed date, status (Open/Closed), city/state location, region, allegation categories, latest docket item and keyword-inferred disposition.
- Elections tallied (ballots for union / against, eligible voters): JFK8 Staten Island 2022-04-01 2,654 / 2,131 of 8,325 (ALU won, certified); LDJ5 Staten Island 2022-05-02 380 / 618 of 1,633; ALB1 Castleton-on-Hudson 2022-10-18 206 / 406 of 949; Bessemer AL 2021-04-09 738 / 1,798 of 5,867 and rerun 2022-03-31 875 / 993 of 6,153 (challenged ballots, outcome not final in this field set); Garner NC (CAUSE) 2025-02-15 829 / 2,447 of 4,738; Middletown DE 2014-01-15 (IAM) 6 / 21 of 30.
- Caveats: (a) the NLRB site holds filed-case data from about 2009 onward. (b) Matching is by keyword "amazon" in the case name, so it misses cases filed under delivery-service-partner names, Whole Foods or other subsidiaries, and includes 11 AWS/data-center cases (entity_class flags them) and charges where Amazon is not the respondent. (c) The search returns at most about 98 pages; the listing ended naturally (page 98 held 4 results) but completeness is not independently verified. (d) Case outcomes for CA cases are NOT a structured field: the disposition column comes from keywords in the docket entries displayed (the first 10 docket rows only), so it is partial and heuristic; "Closed" status plus "withdrawal" or "dismissal" matches most closures. (e) 2026 cases are included to the retrieval date and mostly open. (f) The RC "reason closed" field is blank for the Bessemer cases. (g) Case counts per year reflect filing volume, not merit.
- Participants (lawyers, charging parties) were not collected.

## 6. Turnover (published, cited)
- File: data/processed/amazon_turnover_published_estimates.csv (3 rows). All SECONDARY: the NYT (June 2021) analysis reported roughly 150% annualised turnover for hourly staff (about 3% per week); WSJ/NELP reported roughly 100% for warehouses. The NYT, WSJ and NELP originals were not retrieved; the URLs given are summaries (Verdict, Popular Science). Treat as reported estimates from leaked/internal data, not Amazon-published numbers. No industry-baseline turnover was added.

## Gaps
- No Amazon-only wages or hours by site; no BLS JOLTS turnover (not Amazon specific) was collected; no pre-2001 QCEW; no state-level NLRB roll-up beyond what can be computed from the location field; no ProQuest/Statista data (not attempted); county series cover only NAICS 49x.
