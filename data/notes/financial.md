# Financial domain notes (retrieved 2026-10-31)

## Sources
- SEC EDGAR, Amazon.com Inc (CIK 1018724). Filing list: https://data.sec.gov/submissions/CIK0001018724.json (+ sub_001, sub_002). 10-K / 10-K405 filings for FY1997-FY2025 downloaded to data/raw/financial/tenk/ (31 files incl. two 10-K/A, unused) and converted by scripts/html2txt.py to tenk_txt/. Publisher: SEC / Amazon.com Inc. Index: raw/financial/tenk_list.json.
- XBRL companyfacts: https://data.sec.gov/api/xbrl/companyfacts/CIK0001018724.json (raw/financial/companyfacts.json). Used only to cross-check PP&E net 2008-2019, 2024-25. Fulfillment and shipping are Amazon custom tags NOT in companyfacts, so those were transcribed from 10-K text.
- Good Jobs First Subsidy Tracker: BLOCKED (see gaps).

## Processed files (data/processed)
- amazon_income_statement_annual.csv FY1997-2025: net sales, fulfillment expense, operating income, net income (USD m). Each year taken from the 10-K whose 3-year statements cover it (latest restated), accession in column.
- amazon_shipping_costs_annual.csv: shipping revenue, outbound shipping cost, net shipping cost, gross profit from shipping (long format). Definitions changed (see note column); 2017+ in rounded $0.1bn.
- amazon_capex_annual.csv: gross purchases of PP&E; net of incentives from 2017; finance-lease and build-to-suit additions (non-cash) 2008-2025.
- amazon_ppe_year_end.csv: net (and gross where available) PP&E.
- amazon_10k_square_footage.csv (long) and amazon_10k_square_footage_by_segment.csv: Item 2 Properties by type, region, owned/leased, FY1997-FY2025. Totals for FY2012-2025 reconcile to the 10-K totals.
- amazon_subsidies_gjf_unverified.csv: aggregates only, from search snippets (superseded for row-level work by subsidies_verified.csv).
- subsidies_verified.csv (290 award rows + 41 markers; see Subsidies section), subsidies_verified_summary.csv, subsidies_context_nonlogistics.csv: see Subsidies section below.

## Caveats
- Square footage is global, all Amazon (offices, data centers, AWS, Whole Foods/physical stores included). Item 2 never splits fulfillment centers from sortation/delivery stations/data centers after FY2011; "fulfillment, data centers, and other" is one bucket. Segment table (North America) is the closest proxy for the US network but includes Canada, Mexico, stores.
- FY1997-2003 are narrative; values converted to thousands sq ft, are approximate, "US" as worded. Leased-only (company states it owned no real estate before FY2012).
- FY1997/98 fulfillment expense is embedded in Marketing and sales (FY1999 10-K MD&A), not a line item. FY1999 has two definitions (188.4 vs 237.3).
- FY1998 sales and operating loss are the poolings-restated numbers in the FY1999 10-K (609.8 vs 610.0 originally).
- Shipping cost is company-wide, not warehouse-only, and includes delivery. No state or facility breakdown exists in the filings.
- Fiscal year = calendar year.

## Subsidies (state-by-state merge 2026-10-31)

Method. Good Jobs First's Subsidy Tracker was not obtained: headless Chrome got the Cloudflare managed challenge and no bypass was attempted. Instead one researcher per state searched official records first (agency releases, IDA and council agendas, state datasets) and then press, saved the pages under data/raw/subsidies/<state>/ (with index.csv), and wrote data/processed/subsidies_by_state/<ST>.csv. Those 51 files were merged with the earlier 27-row subsidies_verified.csv into one file, data/processed/subsidies_verified.csv (217 rows: 205 award rows plus 12 "not searched" markers; backup of the earlier file: subsidies_verified.pre_merge.csv). Same award reported by several sources = one row: the strongest verification level is kept (primary over secondary over unverified; ties go to the newer state file) and the other URLs go in alt_sources. All 27 earlier rows matched a state-file row and were folded in (28 rows removed in total, including a KY duplicate); where the earlier row differed, the old value is quoted in notes (Monroe OH 3.8M vs 3.71M, South Fulton 16.0M vs 16.025M, Harris County 1.79M total vs 179,073 per year). Legacy columns (facility, type, source_kind, amount_basis_legacy) and a merged_from provenance column are kept. Levels: primary = government record or agency release; secondary = news or reprint quoting an official or a compilation (e.g. BGA/WBEZ); unverified = search snippet or unopened page.

amount_basis is never mixed. announced_max = cap or announced package; estimated_value = projected value of an abatement, PILOT or credit; realized = amount reported as actually forgone or paid; annual = per-year amount. data/processed/subsidies_verified_summary.csv groups by state x award_year x amount_basis x verification_level and has no cross-basis total. Award rows only; markers excluded.

Coverage (after the browser-pass merge and its adversarial check, 2026-10-31: 290 award rows: 90 primary, 169 secondary, 31 unverified; 41 marker rows (26 partial_search, 15 searched_none, 0 not_searched), which are excluded from all totals, as are unverified rows). Primary + secondary rows with an amount, by basis, not additive across bases and with overlaps inside packages: announced_max 110 rows, 718.4M; estimated_value 48 rows, 1008.0M; realized 16 rows, 111.5M (New York IDA exemptions reported to the state Authorities Budget Office, cumulative FY2020-24; Connecticut North Haven credits issued; Oregon enterprise zone exemptions from the state's report files, gross of the Troutdale 25% fee); annual 1 row, 179,073. CO MN MO OR WI NV SC AR CT IA KS NM OK MS NE LA NH ME VT WV ID MT ND SD WY AK HI DC were replaced by the rewritten state files (backup: subsidies_verified.pre_browser.csv; script: scripts/merge_subsidies_browser.py). The earlier MN Shakopee 6.4M downgrade to unverified (subsidies_check.md) stands: that row was superseded by a 1.2M secondary row (Amazon's own TIF share, declined, 0 realized) and a 5.7M primary road-TIF row that is not a payment to Amazon. Overlaps to watch in the new rows: OR realized vs estimate rows for Troutdale and Salem; WI Kenosha 7M vs 10.3M WEDC and Oak Creek 2.84M loan vs 16.9M TIF; KS Edgerton grant vs KDOT; SD Sioux Falls 94.4M is a park-wide TIF to a nonprofit developer (Amazon is one tenant) and the SD 1.9M is a federal EDA grant, which the Excluded line below would drop; CO Thornton 3.6M, AR 2M, KS 7M and 6M, NM 6.5M, IA RISE and WI/OK infrastructure rows are public works, not payments to Amazon. The browser-pass check (data/notes/subsidies_check.md) moved four rows to unverified: SD Sioux Falls 94.4M (park-wide TIF, Amazon not named), KS Salina 6M (notes repaid by special assessments, 1.56M reallocated), NM 6.5M (mostly recouped from Amazon fees) and WI Kenosha 7M (same WEDC award as the 10.3M row). Status key below: complete = award rows and no partial_search marker (none qualify); partial = a partial_search marker; none-found = searched_none only.

| State | Primary | Secondary | Unverified | Markers | Status |
|---|---|---|---|---|---|
| AK | 0 | 0 | 0 | partial_search | partial |
| AL | 0 | 1 | 1 | - | earlier pass, not re-labelled |
| AR | 0 | 1 | 1 | partial_search | partial |
| AZ | 0 | 1 | 2 | - | earlier pass, not re-labelled |
| CA | 2 | 1 | 0 | - | earlier pass, not re-labelled |
| CO | 0 | 2 | 0 | partial_search | partial |
| CT | 3 | 4 | 0 | partial_search, searched_none | partial |
| DC | 0 | 0 | 0 | partial_search | partial |
| DE | 4 | 1 | 0 | - | earlier pass, not re-labelled |
| FL | 1 | 12 | 2 | - | earlier pass, not re-labelled |
| GA | 3 | 5 | 3 | - | earlier pass, not re-labelled |
| HI | 0 | 0 | 0 | partial_search | partial |
| IA | 6 | 0 | 0 | partial_search, searched_none | partial |
| ID | 0 | 0 | 0 | partial_search, searched_none | partial |
| IL | 4 | 20 | 2 | - | earlier pass, not re-labelled |
| IN | 0 | 12 | 0 | - | earlier pass, not re-labelled |
| KS | 8 | 7 | 1 | partial_search | partial |
| KY | 1 | 4 | 1 | - | earlier pass, not re-labelled |
| LA | 5 | 0 | 0 | partial_search | partial |
| MA | 2 | 1 | 2 | - | earlier pass, not re-labelled |
| MD | 2 | 7 | 0 | - | earlier pass, not re-labelled |
| ME | 0 | 0 | 0 | partial_search | partial |
| MI | 6 | 1 | 0 | - | earlier pass, not re-labelled |
| MN | 1 | 1 | 0 | partial_search, searched_none | partial |
| MO | 3 | 6 | 1 | partial_search | partial |
| MS | 4 | 4 | 0 | partial_search, searched_none | partial |
| MT | 0 | 0 | 0 | partial_search, searched_none | partial |
| NC | 0 | 7 | 0 | - | earlier pass, not re-labelled |
| ND | 0 | 0 | 0 | searched_none | none-found |
| NE | 0 | 0 | 0 | searched_none | none-found |
| NH | 0 | 0 | 0 | partial_search | partial |
| NJ | 0 | 2 | 2 | - | earlier pass, not re-labelled |
| NM | 0 | 0 | 1 | partial_search, searched_none | partial |
| NV | 2 | 0 | 0 | partial_search, searched_none | partial |
| NY | 12 | 2 | 2 | - | earlier pass, not re-labelled |
| OH | 1 | 15 | 0 | - | earlier pass, not re-labelled |
| OK | 1 | 3 | 0 | partial_search | partial |
| OR | 5 | 2 | 0 | partial_search | partial |
| PA | 0 | 7 | 3 | - | earlier pass, not re-labelled |
| RI | 1 | 1 | 0 | - | earlier pass, not re-labelled |
| SC | 4 | 3 | 0 | partial_search, searched_none | partial |
| SD | 0 | 1 | 1 | partial_search | partial |
| TN | 1 | 5 | 3 | - | earlier pass, not re-labelled |
| TX | 3 | 11 | 2 | - | earlier pass, not re-labelled |
| UT | 1 | 0 | 0 | - | earlier pass, not re-labelled |
| VA | 4 | 8 | 0 | - | earlier pass, not re-labelled |
| VT | 0 | 0 | 0 | partial_search | partial |
| WA | 0 | 4 | 0 | - | earlier pass, not re-labelled |
| WI | 0 | 7 | 1 | partial_search | partial |
| WV | 0 | 0 | 0 | partial_search | partial |
| WY | 0 | 0 | 0 | partial_search | partial |


Caveats.
- Almost every amount is an announced cap, estimate or compilation figure, not a realized payout. Realized amounts: New York (net exemptions after PILOT payments), Connecticut North Haven (credits issued), Oregon (gross exemptions from state report files) and one NM county spending row; none is the value of a payment to Amazon.
- Do not add rows from one package: IL Markham (Class 8 abatement 220M, TIF 102M, CMAP) and University Park/Markham/Matteson come from one BGA/WBEZ table; GA Gwinnett (5 rows, about 19.7M package); MD Broening Hwy (5 rows, about 40-43M); PA 2016 (3 rows, 22.25M); DE Middletown 2012; FL Jacksonville Project Rex (4 rows); TN statewide aggregates (30M, 14.9M) overlap the site rows; NY Woodmere and Syosset have a realized row and a secondary announced row for the same project; Jeffersonville IN rows overlap.
- Some amounts are derived, not stated: Monroe OH 3.71M (rate x payroll), NJ Hamilton about 100M (taxes without PILOT minus PILOT payments). Some rows are not payments to Amazon (Pflugerville 3.8M paid to the city for roads; WA Geiger Boulevard 30.4M public road money; Smithfield NC 1.25M to the town; VA Governor's Opportunity Fund grants went to counties).
- Many primary rows carry no dollar value (DCEO redacts EDGE amounts; most abatements). They are in the file but excluded from totals.
- Conflicts left open: Fayetteville NC (WRAL says Amazon declined the original offer; grants approved later), Alcoa TN (FastTrack grant vs "no incentives"), Joliet IL (71.5M vs a later 42M), Chattanooga TN (GJF snippet vs EDGE). Site codes are matched on city and street only (site_code_match); several are probable only.
- Excluded: HQ2, offices, data centers (OH New Albany, GA Butts, VA Stafford, PA) and customer service sites (subsidies_context_nonlogistics.csv); federal grants; the 2012 Texas Comptroller sales-tax settlement is kept as a row with no amount.
- A shared 200-call web-search budget ran out during the run, so later states and the tail of many states were not searched. Absence of rows is "not checked", not "no subsidy", except where a source says so (IL Romeoville, El Paso, Richmond, Buda and Kyle TX, Detroit fairgrounds MI, Tucson AZ, Spokane Valley WA: no incentive reported).
- Do not publish unverified rows. Next step: the Good Jobs First export in a normal browser, then local agendas for the unsearched states.

Browser-pass labels for the 28 re-searched states: none-found (2): NE, ND (searched_none on secondary evidence; not a proven zero). Partial (26): CO, MN, MO, OR, WI, NV, SC, AR, CT, IA, KS, NM, OK, MS, LA, NH, ME, VT, WV, ID, MT, SD, WY, AK, HI, DC. Complete: none. States among the 28 with no award row (12): NE, NH, ME, VT, WV, ID, MT, ND, WY, AK, HI, DC; of these NH, ME, VT, WV, WY, AK, HI, DC carry only a partial_search marker and ID, MT also a secondary searched_none for Nampa and Missoula. Searching was limited to about 40 queries per state and several official sites (OEDIT, KRQE, Aurora CO records) returned 403, so no state is labelled complete.

## Gaps
- Subsidy row-level data (amount, year, state, location, program) NOT obtained: subsidytracker.goodjobsfirst.org and goodjobsfirst.org return a Cloudflare 403 challenge to curl and WebFetch. No bypass attempted. The 9 rows in the unverified CSV come from search-result snippets and need checking. Next step: obtain the tracker export in a browser and verify before publishing any subsidy figure. Status 2026-10-31: the unverified snippet figures were removed from financial.html and from the public data assets; the CSV is gitignored.
- No labor/headcount (not requested here). Property incentives (e.g. PP&E incentives) not itemized by site.
