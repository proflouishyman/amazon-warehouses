# Industry and trade sources for Amazon US logistics data

Compiled 2026-10-31. Every figure quoted here was seen on a fetched page or PDF unless marked LEAD (seen only in a search-result summary, not yet verified on the page). Raw files are in `data/raw/industry/`; tidy CSVs in `data/processed/industry_*.csv`.

Access note: no subscription database (ProQuest, Statista) is cited in this document, and no subscription content is reproduced. Trade-press full text (Logistics Management, Modern, Supply Chain Quarterly, Transport Topics, JOC) is therefore unassessed beyond open pages.

## Key structural finding

Almost every academic Amazon facility dataset (Zipperer & Jones/EPI, Cunningham, Schorung et al., Rodrigue, Consumer Reports) is built on one commercial source, MWPVL International. No replication package with facility-level data was found. MWPVL used to publish its full facility tables openly on its web page; the page now says it will no longer update online, and "current information available in XLSX format" is sold commercially. The fetched page (`raw/industry/mwpvl_amazon_com.html`) no longer contains the facility tables. So the facility-level gap (a) cannot be closed openly beyond the EPI 2017 list; it needs MWPVL's paid XLSX or a decision to use Wayback Machine snapshots (copyright caveat: MWPVL asserts copyright and the dashboard is public).

## Ranked sources

Rating is 1 to 5 value for this project. Gaps are (a) openings, (b) counts by type, (c) parcel volume/share, (d) robots, (e) labor, (f) industrial real estate.

| Rank | Source | Access | Gaps | Years | Format | Rating |
|---|---|---|---|---|---|---|
| 1 | Pitney Bowes Parcel Shipping Index (annual press releases) | Open (press release PDFs); full index is a download on the Pitney Bowes site, not retrieved | c | Amazon Logistics volume 2019-2024 (2016 onward for revenue CAGR) | PDF/HTML text | 5 |
| 2 | MWPVL International, "Amazon Global Supply Chain and Fulfillment Center Network" | Paid (XLSX, commercial terms). Open page is now narrative only | a, b, f (sq ft) | 1997 to present (Q1 2025 per page) | Was HTML tables; now XLSX | 5 for content, 1 for openness |
| 3 | EPI, Zipperer and Jones, "Unfulfilled promises" (2018), Appendix Table 3 | Open | a, partly b | FC openings 1997-2017 (95 FCs) | PDF table, state/county/quarter | 4 |
| 4 | Amazon annual reports / SEC filings via The Real Deal and Commercial Observer | Open (articles); primary 10-K is open | f | 2015, 2018, 2020-2022 leased sq ft | Article text | 3 (10-K itself is the better primary) |
| 5 | Avison Young "U.S. industrial bulk leasing trends" (Jul 2024-Jul 2026) | Open PDF | f | trailing 24 months only | PDF | 3 |
| 6 | Amazon / aboutamazon.com plus Business Insider for robot counts | Open | d | 2014, 2021, 2023, 2025 (gaps in between) | Prose | 3 |
| 7 | Schorung, Lecourt and Dablanc (2024), Journal of Transport and Land Use 17(1) | Open access | a, b (figures only) | openings 1997 to planned 2024, snapshot Sept 2021 (264 facilities, 106 planned in MWPVL sample per text) | PDF, figures from MWPVL | 3 |
| 8 | Cunningham, UMN PhD dissertation (2023) | Open (UMN Conservancy) | a (Figure 1 only, bar chart 2005-2021) | 2005-2021 | Text, charts | 2 |
| 9 | Rodrigue (2020), J. Transport Geography 88; transportgeography.org summaries | Journal paywalled (library access likely); web summary open | b | 2021: "more than 935 facilities" in US; EFC median 855,000 sq ft | Prose | 2 |
| 10 | CompStak industrial reports | Open blog, registration for data | f | Q1 2024 average Amazon lease size 819,000 sq ft | Blog | 2 |
| 11 | CSCMP State of Logistics Report (Kearney) | Paid ($299 non-member per search result, LEAD); summaries open via DC Velocity, SupplyChainXchange | context (national logistics cost) | annual, 1980s on | PDF | 2 |
| 12 | NELP "A Good Living" (2024) | Open PDF | e | county warehouse earnings gap | PDF | 2 (advocacy, not fetched in full) |

### Sources named in the brief but not usefully assessed

Homepages for Supply Chain Dive, DC Velocity, Logistics Management, Marketplace Pulse, ShipMatrix returned HTTP 200; ShipMatrix, Marketplace Pulse, Digital Commerce 360, Supply Chain Dive and DC Velocity have open articles that quote the same Pitney Bowes and MWPVL numbers rather than adding independent series (search results; no independent dataset found). Specific leads:
- Digital Commerce 360, 2025-07-01, "Amazon closing parcel delivery gap with USPS" (secondary to Pitney Bowes).
- DC Velocity and The Supply Chain Xchange cover the CSCMP report annually (open summary, paid report).
- Modern Materials Handling / Logistics Management top-warehouse and automation surveys, Supply Chain Quarterly, Material Handling & Logistics, Transport Topics, Journal of Commerce, FreightWaves: not examined in depth; archive full text would need a library database. Full text would need a library login.
- CBRE, JLL, Cushman and Wakefield, Prologis: no national annual "Amazon share of industrial leasing" series found openly. Search results offered only regional or single-quarter shares (LEAD, unverified on page): CompStak Phoenix 4.8% of leased sq ft 2019-2023 and 68.2% in Q1 2024; Cushman and Wakefield Inland Empire mid-2024, three Amazon leases about 18.5% of 17.3 million sq ft; CoStar Houston 2020, 11.8%. Those need a fetch of the originals before use.
- Ontheseams Substack analysis of MWPVL snapshots Q1 2024 vs Q1 2025 (about 35 million sq ft added in 2024, LEAD, https://ontheseams.substack.com/p/amazons-retail-footprint-in-2024 appeared in search; not fetched).
- Elmer Li, "E-commerce and Regional Inequality" (2025), https://elmerli.github.io/ecommerce.pdf: uses "new data on Amazon sales, retailers, and facilities"; data source not confirmed (LEAD).
- Fried and Goodchild (2023) J. Transport Geography 112:103692; Dubie et al. (2020) J. Transport Geography 88: logistics sprawl papers; no data release found.
- Italian studies (Tramontano, Cirillo, Guarascio; GLO DP 1798) are Italy-only; out of scope.

## Source detail

### 1. Pitney Bowes Parcel Shipping Index
- Route: open. Press releases hosted on s203.q4cdn.com (2023, 2024, 2025 PDFs saved in raw). Business Wire returns HTTP 403 to scripted fetches; 2019-2021 vintages were taken from trade-press reproductions (MH&L News, FreightWaves, Post and Parcel).
- Series extracted (`industry_pitney_bowes_parcel_index.csv`, 106 rows): volume by carrier, volume share, revenue by carrier, revenue share, 2019-2024. Amazon Logistics volume (billion parcels): 2019 1.9, 2020 4.2, 2021 4.8, 2022 4.8, 2023 5.9, 2024 6.3. Share of US volume: 2019 13%, 2020 21%, 2021 22%, 2023 27%, 2024 28%.
- Caveats: each release restates earlier years (e.g. 2022 total is 21.2 in the 2023 release and 21.5 in the 2024 release; 2019 Amazon is 1.9 in 2020-21 releases and "2B" in the 2024 release). 2022 shares by volume are not in the saved text, so omitted. The 2021 UPS/FedEx/USPS volumes are not in the FreightWaves text (only shares); omitted. Pre-2019 US carrier detail (Amazon was excluded or not broken out) was not found.
- Citation: Pitney Bowes Inc., Parcel Shipping Index, press release 2025-06-30 (data year 2024); 2024-04-17 (2023); 2023-03-28 (2022); 2022-05-23 (2021); 2021-09-14 (2020); 2020-10-12 (2019). Dates for 2021 to 2024 releases taken from search results and URLs; the 2020 and 2021 dates are from Business Wire URLs and not independently seen on a page.
- Full index (global, 13 countries, 2012 on) can be downloaded from Pitney Bowes ("can be viewed and downloaded here" in the 2025 release); not retrieved.

### 2. MWPVL International
- Route: paid. Page text states: "in future we will no longer be updating this information online due to the high rates of plagiarism... If there is an interest in obtaining current information available in XLSX format then please contact us ... commercial terms." Latest status on the page: "As of 2025 Q1". It reports 123+ buildings closed, canceled or delayed in 2022-2023.
- Fields (per Schorung et al. 2024 methods, and Cunningham): facility code (3 letters and 1 digit), state, address (approximate for planned sites), function and type, square feet (excluding mezzanine), opening year, status (open/closed/planned), co-located facilities. Types include fulfillment centers, sortation centers, delivery stations, air hubs, Fresh/Whole Foods DCs, Prime Now hubs.
- Schorung et al. say the inventory is "authorized for use for purposes of research" and that they OCR-transcribed it. Citation form: MWPVL International, "Amazon Global Supply Chain and Fulfillment Center Network", https://www.mwpvl.com/html/amazon_com.html, accessed date.
- Open item: decide whether to buy the XLSX (best for gap a and b, and the site codes) or ask MWPVL for a research licence.

### 3. EPI Appendix Table 3
- https://files.epi.org/pdf/138921.pdf. 95 FC openings by state, county and quarter, 1997 Q4 to 2017 Q4, compiled from Avalara, Guided Imports and MWPVL (accessed 2017). Report states 69, 91, 95 cumulative by end of 2015, 2016, 2017; parsed rows reproduce exactly 69/91/95. Updated MWPVL data (Feb 2018) gives 75, 100, 120. Files: `industry_epi_fc_openings_2017.csv` (95 rows), `industry_epi_fc_cumulative_counts.csv` (6 rows).
- Limits: no site code, square footage or street address; FC type only; the extra 25 openings from the 2018 update are not itemized. No replication files published.
- Citation: Zipperer, Ben and Janelle Jones (2018). "Unfulfilled promises: Amazon warehouses do not generate broad-based employment growth." Economic Policy Institute.

### 4 and 5. Industrial real estate (gap f)
`industry_amazon_leased_sqft.csv` (10 rows). Series: leased space 58 million sq ft (2015, US distribution centers), 154 (Dec 2018), 286 (2020, North America), 370 (2021), 392 (2022); owned 16.6 to 22 million. Prologis Q3 2021: Amazon 31 million sq ft, analyst says 4.8% of rent. Avison Young Jul 2024-Jul 2026: Amazon 29,513,879 sq ft in 31 bulk deals, of 397.1 msf in 512 deals (the report says "roughly 7%"; the arithmetic is 7.4%).
- The 10-K "Properties" table is the primary source for 2020-2022 and is already covered in `amazon_10k_square_footage*.csv`, so the press figures are cross-checks only. Definitions differ across rows (US vs North America; leased vs total; fulfillment-only vs all industrial).
- No open annual national "Amazon share of industrial leasing" series. CBRE, JLL, Cushman and Wakefield and CoStar publish it in client reports. Needs a paid or registered account.

### 6. Robots (gap d)
`industry_amazon_robot_counts.csv` (7 rows). Only five distinct points are verified on a page: 15,000+ (holiday 2014), about 350,000 (2021), 750,000 (mid-2023 by BI's "last June" wording, inferred), 1,000,000+ (July 2025, Amazon's own page), plus 200,000+ (June 2019) via Wikipedia citing the Washington Post (WaPo not read).
- LEADs not on any page I saw: about 30,000 (2015), 45,000 (2016, Deutsche Bank via manufacturing.net and inddist.com, which returned 403 to scripted fetches), 100,000 (2017, appears only in LinkedIn posts in search results, no primary), 520,000 (2022, secondary). Treat these as unverified until fetched from the original articles.
- Defintional caution: Kiva-era counts are drive units; later counts include all robot types (Sequoia, Proteus, Sparrow, Vulcan).
- A cleaner route: Amazon "Delivering the Future" posts and Amazon Robotics blog for each year (not fetched).

### 7 to 9. Academic
- Schorung, Lecourt and Dablanc (2024), "Assessing the spatial footprint of e-commerce logistics differentiating the types of warehouses: The case of Amazon in the United States", JTLU 17(1), doi:10.5198/jtlu.2024.2438. PDF saved (`jtlu_2438.pdf`). Reports the MWPVL sample at Sept 2021: 264 facilities and 106 planned (as stated in the text; the scope of "facilities" in that sentence is unclear without reading the whole paper). No dataset deposited; Table 1 and 2 give distances by metro and warehouse type.
- Cunningham (2023), "The Local Economic Impacts of Amazon: Evidence from Fulfillment Centers and Lessons for Local Economic Development", PhD dissertation, University of Minnesota. Text saved (`cunningham_umn_dissertation.txt`). Uses MWPVL address, opening date, size and type, 2005-2021; says openings reached about 8 to 10 FCs per year after 2010 and about 25 per year from 2016. No public replication data found.
- Rodrigue (2020) J. Transport Geography 88 is summarized at transportgeography.org (saved). Gives median EFC footprint 855,000 sq ft and, for 2021, "more than 935 facilities" in the US.

### 10 to 12. Context sources
Not extracted. CSCMP: 2025 edition headline of $2.58 trillion is LEAD (search results disagree on 8.7% vs 8.8% of GDP). NELP: LEAD that Amazon-county warehouse earnings are 12% below non-Amazon counties (18% in high-earnings counties), per Vice summary; fetch the NELP PDF before use.

## Open items

1. MWPVL XLSX purchase or research licence (gap a, b, f at facility level, site codes, square feet, planned/closed status). This is the single highest-value item.
2. Library database access (ABI/INFORM, Trade and Industry) for Modern Materials Handling, Logistics Management, Supply Chain Quarterly, Transport Topics, JOC full text.
3. CSCMP State of Logistics (a library may hold it, or about $299), CBRE/JLL/Cushman/CoStar leasing reports (registration or client access) for the Amazon leasing share.
4. Decision on Wayback Machine snapshots of the old MWPVL tables (copyright and public-dashboard risk).
5. Business Wire, manufacturing.net, inddist.com, therealdeal.com and avisonyoung via WebFetch return 403; curl with a browser user agent worked for most. The Business Wire releases for 2019-2022 still need a browser fetch to confirm numbers taken from reproductions.


## Trade-press openings (industry_trade_press_openings.csv)

203 rows of what trade and local press reported about Amazon sites (type, city, stated opening or announcement date, publication, article URL, a short quote, a confidence grade, and a match to a roster site code with a quality of exact, probable or none).

- Used for the roster: only exact and probable matches (73 rows) whose roster state equals the press state, and only a stated opening year of 2026 or earlier, set `press_opening_year` and `press_source_url` in facilities_master.csv (scripts/build_trade_press.py). Where several rows match one site, exact beats probable, then higher confidence, then a public article URL, then the earliest year. `opening_year` (MWPVL) is never overwritten.
- `year_basis` per site: `opening_year` (MWPVL/EPI) over `press_opening_year` over `first_osha_filing` ("operating by": an upper bound on the opening date).
- Limits: the list is what was found, not a census. 35 rows are low confidence; 25 rest on search snippets and 10 on ProQuest result titles only. Dates later than 2026 are planned openings and are not used. Two press dates (BOS3 2024, DET6 2023) fall after the site's first OSHA filing. Source conflicts: Loveland CO (CBS 3.5M sq ft vs 9News 823,000) and Wilmington NC (WECT 650,000 vs WilmingtonBiz more than 3 million).
- Map positions of unmatched rows are Census 2020 Gazetteer place, county-subdivision or county centroids (data/raw/census/gaz_*), marked approximate.
