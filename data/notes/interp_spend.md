# INTERP SPEND: which consumer spending moved from stores to online (and to Amazon), by category, 2010-2025

Retrieved 2026-11-01. Build: `python3 -I scripts/interp_spend_build.py` (add `--download` to refetch). Raw files: `data/raw/interp_spend/` (gitignored). Outputs: `data/processed/interp_spend_*.csv`. Only public sources.
Status key: OPENED = file fetched and read/parsed here; SNIPPET ONLY = taken from a search-result summary, not verified against the source; DERIVED = computed by the script, not printed by the source. Nothing here is an estimate of Amazon's displacement effect; these are inputs.

## 0. Bottom line (for the netting model)

1. No public source gives online share by product category across ALL retailers. The best public build is: ARTS NAICS 4541 e-commerce by merchandise line (nonstore retailers only, which is where Amazon sits) + ARTS e-commerce of store-based kinds of business (own websites) + BEA PCE as the consumer-spend denominator. File: `interp_spend_online_share_combined_est.csv` (DERIVED, caveated per row).
2. Online share of all US retail (Census): 4.5% (2010) -> 10.6% (2019) -> 14.6% (2020) -> 16.4% (2025), annual sums of not-adjusted quarters (DERIVED, `interp_spend_quarterly_ecom_share.csv`). Latest quarter in the 2026-08-18 release: 17.1% adjusted (2Q 2026).
3. Categories that moved most, 2010 -> 2022 (ARTS 4541 line e-commerce over matched BEA PCE, DERIVED, a ratio not a clean share): clothing 7% -> 26% (30% with store-based websites), sporting goods 8% -> 28%, electronics about 7% -> 17% (understated, computers suppressed), drugs/health/beauty 2.5% -> 10.6%, toys/hobby 3% -> 10%, grocery/food 0.4% -> 2.6% (4.6% with store-based). Furniture and books also high but the ratios are inflated by mismatched denominators (flagged in the CSV).
4. Amazon cannot be isolated in public Census data: 4541 is all electronic shopping and mail-order houses. No public source I opened gives Amazon's share by category (see 7).
5. Trips: no public source measures store trips displaced by Amazon. Evidence is mixed: NHTS shopping-and-errand trips per person fell from 588 (2009) to 473 (2017) but the report warns of method changes; the diary data (DCPC) record payments, not trips; card-panel papers show substitution for the replaced store but complementarity for other trips (7).

## 1. Census Annual Retail Trade Survey (ARTS) and E-Stats

| Item | Detail |
|---|---|
| Files (OPENED, parsed) | `https://www2.census.gov/programs-surveys/arts/tables/2022benchmarked/ecommerce4541.xlsx` (sheet "Merchandise Lines (4541)", 1999-2022); `.../2022benchmarked/ecommerce.xlsx` (kind of business, 1998-2022); `.../2022benchmarked/sales.xlsx`; `.../2022benchmarked/supecommerce4541.xlsx`; E-Stats 2019 historic Table 5 `https://www2.census.gov/programs-surveys/e-stats/tables/2019/historic/table_5.xlsx` (merchandise lines 1999-2019, older vintage) and Table 4 (retail by kind of business, 1998-2019). ARTS 2022 benchmarked release dated 2026-08-31 per the Census ARTS page. |
| Latest year | 2022. No ARTS merchandise-line data exists for 2023-2025 (probed `arts/tables/2023|2024|2025[benchmarked]/ecommerce4541.xlsx`: HTTP 404). |
| Output | `interp_spend_arts_merch_line_online.csv` (both vintages, with S/NA flags), `interp_spend_arts_kind_of_business.csv` |

What the table is. "Electronic Shopping and Mail-Order Houses (NAICS 4541) - Total and E-commerce Sales by Merchandise Line": for the 4541 establishments only, sales of each product line, split into e-commerce and other (mail/phone order). It is NOT online sales of that line across all retail. Total row 2022 (benchmarked): 4541 total $1,062,420M, e-commerce $827,892M (77.9%).

Selected 4541 e-commerce by line, $M (Table "Merchandise Lines (4541)", 2022 benchmarked; line total in brackets): 2010 -> 2022
- Books: 7,332 -> 20,174 [8,746 -> 21,325]
- Clothing and accessories (incl. footwear): 23,179 -> 129,809 [30,985 -> 135,987]
- Electronics and appliances: 17,631 -> 81,616 [21,453 -> 85,445]
- Furniture and home furnishings: 11,006 -> 124,643 [14,331 -> 128,432]
- Sporting goods: 4,351 -> 31,921 [6,354 -> 36,617]
- Toys, hobby goods, games: 4,412 -> 27,342 [5,945 -> 28,686]
- Drugs, health aids, beauty aids: 10,811 -> 80,219 [74,350 -> 261,485] (4541 line includes mail-order pharmacy, so e-commerce is only 14.5% -> 30.7% of the line)
- Food, beer, wine: 3,329 -> 36,592 [5,199 -> 38,347]
- Computer and peripheral equipment: 11,924 (2010), suppressed (S) 2017-2022; software suppressed 2022. Jewelry, office equipment: suppressed in some years.
Within 4541 the e-commerce share of line sales is already 54% in 2010 and 78% in 2022 (all lines), so most of the movement is growth of 4541 line sales, not conversion of mail-order.

Kind of business (ARTS "ecommerce.xlsx", all retail, e-commerce as % of kind-of-business sales, DERIVED from printed totals): 2010 -> 2022
- Total retail: 4.46% -> 13.90% (ARTS basis; Census quarterly basis differs, see 2)
- 454 Nonstore retailers: 43.9% -> 72.7%; 4541: 54.3% -> 77.9%
- 448 Clothing stores: 0.86% -> 7.04%; 442 Furniture stores: 0.39% -> 3.38%; 443 Electronics/appliance stores: 1.17% -> 2.99%; 451 Sporting/hobby/music/book stores: 1.90% -> 5.98%; 445 Food and beverage stores: 0.11% -> 2.89%
- 452 General merchandise stores (department, discount, warehouse clubs, supercenters): suppressed (S or D) in most years; 0.02% in 2012 and 0.05% in 2015 only. This is the key gap for the department and general-merchandise store types.
- 446 Health and personal care stores, 447, 441: mostly D or S.

The supplemental table "4541 by primary business activity" (supecommerce4541.xlsx) is not merchandise lines: it reallocates 4541 sales by the primary 3-digit NAICS of the company. In 2022 benchmarked, e-commerce of companies whose primary activity is clothing stores (448) is $48,074M, vs $129,809M in the clothing merchandise line, i.e. most clothing sold through 4541 comes from companies whose main business is something else. Use the merchandise-line table for category questions.

### Denominator, 2012 (Economic Census Product Lines, EC1244SLLS1)
OPENED. `https://www2.census.gov/programs-surveys/economic-census/data/2012/sector44/EC1244SLLS1.zip`, NAICS 44-45, RCPTOT by PSCODE2012 = sales of each line by all retail establishments (sector total $4,219,821M). Output `interp_spend_line_denominator_2012.csv` (DERIVED; crosswalk of ARTS lines to EC product-line codes is mine and approximate). 2012 nonstore (4541) line sales as % of all-retail line sales, and 4541 e-commerce as % of all-retail line sales: books 66% / 59%; clothing 12.0% / 10.0%; electronics and appliances 22% / 19%; furniture and home furnishings 10.8% / 8.8%; jewelry 12.3% / 9.0%; sporting goods 18.3% / 13.6%; drugs/health/beauty 20% / 3.5%; food, beer, wine 1.0% / 0.7%; toys 24.5% / 19%. Numerator excludes store-based e-commerce, so these understate online share.
Not obtained: 2017 and 2022 Economic Census product-line (NAPCS) denominators. The Census API now answers "Missing Key" without an API key (tested `ecnnapcsprd` 2017 and 2022, `ecnflspace` 2017) and I did not locate static NAPCS downloads. So the line-level all-retail denominator exists only for 2012; BEA PCE is used for other years.

### Floor space (useful for the conversion)
2017 Economic Census floor space `EC1744FLSPACE.zip` (OPENED, `interp_spend_floorspace.csv`) publishes only four retail industries: department stores 4,334 establishments, 494.4M sq ft total, 387.7M selling, sales $66,633M, $170 per sq ft; supermarkets and grocery 1,112.8M sq ft ($749 per sq ft); convenience stores 47.0M sq ft ($671); warehouse clubs and supercenters 1,202.6M sq ft ($485). The 2022 first-look floor-space file (`EC2244BASIC_FL`) has no floor space columns (sales, payroll, employment only).

## 2. Census quarterly retail e-commerce report

OPENED. `https://www.census.gov/retail/mrts/www/data/excel/tsnotadjustedsales.xlsx` and `tsadjustedsales.xlsx`; release PDF `https://www.census.gov/retail/mrts/www/data/pdf/ec_current.pdf` (2Q 2026, released 2026-08-18; table 1). Coverage 4Q 1999 - 2Q 2026. Output `interp_spend_quarterly_ecom_share.csv`.
Annual e-commerce share of retail (sum of four not-adjusted quarters, DERIVED), %: 2010 4.46; 2012 5.39; 2015 7.15; 2017 8.80; 2019 10.58; 2020 14.60; 2021 14.63; 2022 14.42; 2023 15.37; 2024 16.11; 2025 16.41. Adjusted 2Q 2026: 17.1% ($340,244M of $1,986,488M). Print check: 4Q 2025 adjusted 16.7% matches.
Caveats: (a) Census note: estimates cover businesses with paid employees; before the April 2025 benchmark they included nonemployers, so the series was revised and differs from the ARTS kind-of-business total (13.9% in 2022 vs 14.4% here). (b) E-commerce is defined as orders placed online regardless of payment channel; includes services. (c) Share of total retail includes autos and gasoline.

## 3. Atlanta Fed / Boston Fed Diary of Consumer Payment Choice (DCPC)

OPENED and computed from public microdata, 2020-2025: zips at `https://www.atlantafed.org/-/media/Project/Atlanta/FRBA/Documents/research-and-data/surveys/consumer-payments/survey-diary-consumer-payment-choice/<year>/<year>-diary-of-consumer-payment-choice.zip` (2020 sits under `diary-of-consumer-payment-choice/2020/`; 2025 under `.../2025/dcpc-2025-public-csv.zip`, codebook `dcpc-2025-data-codebook.pdf`, tables `dcpc2025-tables-for-web.xlsx`, report `2025-SDCPC-results-report.pdf`). Three-day diary in October; 2025 transaction file N = 30,391, individual file N = 6,073. Output `interp_spend_dcpc_remote_by_merchant.csv`.
Method: purchases = `bill`==0 and `payment`==1, diary day 0 excluded (Atlanta Fed guidance: day weights not appropriate for day 0), `in_person` variable (0 = remote), transaction weighted by its day's `dow_weight` joined on (id, diary_day). Transactions without a matching weight (oversample and others) are dropped (about 12% in 2025, counts in the CSV).
Findings:
- Remote share of all purchases by number (DERIVED): 19.8% (2020), 18.9% (2021), 18.9% (2022), 21.7% (2023), 23.5% (2024), 23.9% (2025). Check: 2025 published Table 10 gives 8.88 remote of 37.18 purchases per consumer per month = 23.9%, and the 2025 report text says remote purchases were 24% of all purchases (OPENED). The Atlanta Fed 2022 summary says remote share stayed about 20% in 2020-2022 and was double the 2019 share (SNIPPET ONLY); the 2019 figure is therefore about 10% by inference, not opened.
- By value, published Table 10 (2025): remote $941 of $2,437 per consumer per month = 38.6%. My microdata computation gives 45.4%; I did NOT reconcile this (the published tables use different weights, per-consumer averaging and amount cleaning). Treat the by-value columns in the CSV as unreliable, and by-merchant by-value shares as noisy (small cells, large single payments).
- Merchant-type cut is coarse. Code 5 = "General merchandise stores, department stores, other stores, online shopping" (codebook 2025, variable `merch`): online and store shopping are NOT separate categories, and groceries/pharmacies are code 1, restaurants 3 and 4, gas 2. Remote share of code 5 purchases by number: 35.7% (2020), 35.9% (2021), 35.9% (2022), 40.2% (2023), 41.7% (2024), 44.7% (2025). Code 1 (grocery, convenience, pharmacy): 6.2%, 5.3%, 6.7%, 8.1%, 7.3%, 9.0%. These count payments, so small online payments weigh more than in dollar-based Census shares.
- The diary does not record trips, store type within code 5, or product category. It is the closest public diary but it cannot give category shifts finer than grocery vs everything else.
2015-2019 public microdata were not downloaded (URL pattern not located); Boston Fed 2022 working paper "Payments evolution from paper to electronic payments by merchant type" exists (SNIPPET ONLY, from the Atlanta Fed page link list).

## 4. BLS Consumer Expenditure Survey (CE)

Does the CE record online vs in-store? No evidence that the production CE does. State of knowledge: (a) The public-use microdata "Getting Started Guide" page (fetched via the fetch tool, summary only) mentions no outlet or purchase-mode variable. I could not open the data dictionary (bls.gov returns HTTP 403 to scripted clients), so "no such variable" is NOT verified against the dictionary. (b) BLS ran a test: CE Interview final wave Jul 2017 - Mar 2018, 1,100 test households, with outlet questions (store name, location, and "Was this purchase online or in-person?") in 10 sections (Lee and Abdirizak, AAPOR 2019 slides, OPENED; saved `raw/interp_spend/bls/lee_outlet.pdf`); only 224 households answered the purchase-mode question and the deck reports no online share. A 2010 test plan (OMB filing, OPENED) proposed asking the last purchase channel (personal visit, internet, phone/catalog) for groceries, clothing, music, restaurant meals and electronics; there is no result in the file. (c) A 2018 BLS slide deck on the redesigned online diary lists "introduction of outlet question for recording business where item was purchased/consumed" in the large-scale feasibility test, again the business name, not channel (OPENED).
So CE cannot give channel-by-category. It gives the weight of each category in household budgets.
Output `interp_spend_ce_shares.csv`: tables "Income before taxes: annual expenditure means, shares", All consumer units column, from PDFs 2012 (Table 1202), 2015, 2019, 2022 (Table 1203) and xlsx 2024, 2025 (Table 1203), saved from `https://www.bls.gov/cex/tables/calendar-year/mean-item-share-average-standard-error/cu-income-before-taxes-<year>.pdf|xlsx`. The files were retrieved through the interactive fetch tool and parsed by the script; 2010 and 2011 tables were not found under this name (404). Share of total average annual expenditures, %: Apparel and services 3.4 (2012), 3.0 (2019), 2.5 (2025), mean $1,736 -> $2,010 while total expenditures rose $51,442 -> $81,905 (+59%); Food at home 7.6 -> 7.9; Food away from home 5.2 -> 5.1; Entertainment 5.1 -> 5.0; Household furnishings and equipment 3.1 -> 2.9 (peak 3.6 in 2022); Personal care 1.2; Reading 0.2 -> 0.1; Housekeeping supplies 1.2 -> 1.0; Alcoholic beverages 0.9 -> 0.8. Apparel includes services (alterations, cleaning); entertainment includes toys, hobbies, pets, admissions. The CE total includes housing, health and transport, so shares are not shares of goods.

## 5. BEA Personal Consumption Expenditures by product (denominator)

OPENED. `https://apps.bea.gov/national/Release/XLS/Survey/Section2All_xls.xlsx`, sheet T20405-A, NIPA Table 2.4.5 "Personal Consumption Expenditures by Type of Product", annual 1929-2025, data published 2026-10-29. Output `interp_spend_pce_goods.csv` (2010-2025, $M current dollars, % of total PCE, % of goods PCE).
Selected (2010 -> 2025, $B; share of total PCE): total PCE 10,260 -> 20,870; goods 3,318 -> 6,489 (32.3% -> 31.1%); food and beverages for off-premises 787 -> 1,524 (7.7% -> 7.3%); clothing and footwear 317 -> 560 (3.09% -> 2.68%); video, audio, photographic, information processing equipment and media 183 -> 425 (1.8% -> 2.0%); furniture and furnishings 141 -> 292; sporting equipment 53 -> 127; recreational books 23 -> 33; recreational items 130 -> 333; pharmaceutical and other medical products 326 -> 729; jewelry and watches 61 -> 106. The goods share of consumer spending is flat; the story is channel, not category share. PCE is in purchasers' prices for consumers only, so ratios against ARTS (which includes some business buyers and different category boundaries) are approximate: `interp_spend_line_vs_pce.csv` carries a caveat per line.

## 6. Diaries and similar

- US Financial Diaries (Morduch and Schneider, 2012-13): SNIPPET ONLY. 235 households in four communities (California, Mississippi, New York, Ohio-Kentucky border), every financial transaction for a year, non-representative. Search results gave no channel field and no category-level spend; built for income volatility and borrowing. Cannot help: too small, one year, no evidence of a channel field (not confirmed absent).
- Atlanta/Boston Fed DCPC: see 3 (does record in-person vs remote).
- BLS CE diary: see 4 (channel not recorded in production as far as can be verified).
- NHTS (travel diary) is the one US diary with trip counts by purpose: FHWA "Summary of Travel Trends: 2017 NHTS" Table 10a (OPENED, `interp_spend_trips_nhts.csv`): shopping and errands person trips per person per year 579 (1990), 668 (1995), 608 (2001), 588 (2009), 473 (2017). The report says the drop "may be affected by increases in online shopping" and cautions that 2017 used an address-based, web-reporting sample that may under-report incidental stops; it does not measure online shopping.

## 7. Panel and card-data studies: substitution or complementarity

Full table: `interp_spend_substitution_studies.csv` (one row per study with data, access, verification status, finding, numbers, caveats). Summary:

| Study | Access / status | Result |
|---|---|---|
| Dolfen, Einav, Klenow, Klopack, Levin, Levin, Best, "Assessing the Gains from E-Commerce", NBER WP 25610 (2019), AEJ: Macro 15(1) 2023 (the Einav/Klenow paper and "Dolfen et al." are the same paper) | Visa data restricted; WP OPENED | Online about 5% of consumption 2007 -> about 8% 2017. Online share of Visa spend by NAICS 2007 -> 2017 (Table 2): electronics 42 -> 51%, furniture 35 -> 43%, clothing 22 -> 37%, general merchandise 8 -> 15%, food 5 -> 6%, nonstore 90 -> 96%. Substitution: convenience gain <= 0.4% of consumption; most gain is variety (switching to online-only merchants). Elasticity of substitution between online and offline merchants 3.4 (electronics) to 7.7 (building materials) (Table 9). Visa categories are merchant-classified, so "clothing 37% online" includes online-only specialist merchants; not comparable with Census kind-of-business shares. |
| Relihan (2022), CEP DP 1836 | JPMorgan Chase Institute data restricted; paper OPENED | Online-grocery early adopters: grocery-store trips -0.5 days/month (6.8 -> 6.3, -7.4%), local ground transport spend +12.3%, more trips to coffee shops (+1.3 days/yr), restaurants (+2.3), personal care (+0.7), leisure (+0.5), pharmacies (+0.9); no increase for clothing, general goods, home goods. Verdict: substitutes the replaced store trip, complements time-intensive service trips; not Amazon-specific, groceries only. |
| Chava, Oettl, Singh, Zeng, NBER WP 30077 (2022), Mgmt Science 70(4) 2024 | payroll and store data restricted; paper OPENED | Fulfillment-center rollout of a major e-commerce firm (unnamed in text; first center 1997, 90+ by 2016) cuts nearby store sales 4% and employment 2.1%; exit probability +3 points. Substitution at the store level. |
| Pozzi, RAND J. Econ 44(3) 2013 (WP Oct 2012) | one chain's household scanner data; WP OPENED | Online grocery crowds out under 40 cents per $1 of the chain's own in-store spend; chain revenue +13% in zip code (a snippet of another version says 45 cents; published number not verified). Largely complementary for the retailer, partly share-stealing from rivals. |
| Forman, Ghose, Goldfarb, Mgmt Sci 55(1) 2009 | SNIPPET ONLY | Amazon book purchasing falls when a local big-box or bookstore opens nearby: substitutes at the margin. |
| Zhou and Wang, Transp. Res. A 70 (2014), 2009 NHTS | SNIPPET ONLY | Online shopping associated with more shopping trips (complementarity); more trips associated with less online shopping. Cross-section, causality not identified. |
| NielsenIQ Homescan via Kilts | RESTRICTED (data-use agreement), not downloaded | A search-result summary of an AEA working paper says the panel shows a growing online share; a Fed discussion deck (SNIPPET ONLY) notes weak compliance for frequent small online purchases. No public category-level online share found. |
| Numerator | RESTRICTED (commercial) | Only a company survey press release (SNIPPET ONLY): online share of 1-2 item baskets 16% -> 32% and of stock-up baskets 3% -> 12% since 2019; not verified. |
| Card-panel microdata generally (Visa, JPMCI, Facteus, etc.) | RESTRICTED | Only the papers' published tables are usable. |

Net read: category-level evidence says substitution is real but concentrated in the product-line you are replacing (books, apparel, electronics, grocery trips for online grocery users); complementarity shows up in other trips (coffee, services, restaurants) and in overall trip counts that do not fall one-for-one. A one-for-one "dollar online = trip avoided" assumption is not supported; Pozzi's 40 cents per dollar and Relihan's -7.4% grocery trips are the two quantitative anchors, both grocery-only.

## 8. Proposed mapping: merchandise line -> store type -> NAICS -> CBECS

File: `interp_spend_store_type_mapping.csv`. The six requested store types:

| Model store type | ARTS 4541 lines | Store NAICS (ARTS kind of business) | CBECS 2018 principal building activity | 2012 EC product-line codes | Confidence |
|---|---|---|---|---|---|
| clothing | Clothing and clothing accessories (incl. footwear) | 448 | Retail (other than mall) [350k bldgs, 5,193M sq ft]; Enclosed and strip malls [167k bldgs, 5,588M sq ft] | 20200, 20220, 20240, 20250, 20260 | medium |
| electronics | Electronics and appliances; Computer and peripheral; Computer software; Audio and video recordings | 443 | Retail (other than mall) | 20300, 20310, 20320, 20330, 20370, 20440 | medium |
| books_hobby | Books; Sporting goods; Toys, hobby goods, games | 451 (+ part of 453) | Retail (other than mall); strip centers | 20420, 20530, 20460 | medium |
| grocery | Food, beer, and wine; (food-like part of drugs) | 445 | Food sales [163k bldgs, 1,006M sq ft] | 20100, 20140 | high |
| general_merchandise | Other merchandise; Office equipment and supplies | 452 (department, warehouse clubs, supercenters), 453 | Retail (other than mall) / big box; Enclosed mall anchors | 20850, 29810 | low |
| department | none (line-level) | 4522 / 452210 | Enclosed mall anchors or Retail (other than mall); 2017 floor space 494M sq ft total (EC1744FLSPACE) | none | low |
| (extra) furniture_home | Furniture and home furnishings | 442 | Retail (other than mall); Mercantile | 20340, 20360, 20380, 20280 | medium |
| (extra) pharmacy | Drugs, health aids, beauty aids | 446 | Food sales or Retail store | 20160 | low |

Conversion path suggested for the netting model (DERIVED idea, not a result):
1. Online dollars shifted in line L, year t = (online share_t - online share_2010) x category PCE_t. Use `interp_spend_online_share_combined_est.csv` for clothing, furniture, grocery, books/hobby, electronics; state the caveat column.
2. Convert dollars to store floor space with sales per sq ft: available from public data only for department stores ($170 total sq ft, 2017), supermarkets ($749), convenience ($671), warehouse clubs/supercenters ($485) (`interp_spend_floorspace.csv`). For clothing, electronics, books/hobby use CBECS mean floorspace per building and CBECS retail sales per sq ft from another source (not obtained here; retail_context.md has CBECS 2018 floorspace and energy but no sales).
3. Closures lag and are lumpy: displaced demand does not equal vacated floor space one-for-one. National retail floor space by year was not found in public form (see `data/notes/retail_context.md`).
4. Apply a trip-substitution factor (section 7) separately from the dollar shift; do not set it to 1.

Departments and general merchandise: ARTS kind-of-business e-commerce is suppressed for 452, and no ARTS line corresponds to department-store assortments. Fall-back anchors: Dolfen Table 2 general merchandise online 8% (2007) -> 15% (2017) of Visa spend (merchant-classified); 4541 "Other merchandise" line e-commerce $17,310M (2010) -> $125,457M (2022).

## 9. Caveats and gaps (summary)

- ARTS merchandise-line data ends 2022; 2023-2025 shares rest on the Census quarterly total only.
- Store-based retailers' own e-commerce is in ARTS only at kind-of-business level (not by line) and is suppressed for department and general-merchandise stores, so "online share by category" is understated for the store types the model most cares about.
- Amazon share by category: no public source found. Marketplace and 3P sales by Amazon sellers appear in Amazon's financials and in 4541 only at aggregate.
- The 4541 "Total" for a line includes mail-order and phone sales; e-commerce also includes sales to businesses.
- DCPC counts payments, not trips or dollars of product category; merchant code 5 mixes store and online shopping. The by-value remote shares do not reconcile with Atlanta Fed Table 10.
- CE channel question: test only; production microdata dictionary not verified (bls.gov blocks scripted access).
- Store-trip substitution: no public national estimate; NHTS trend is confounded by method change.
- 2017 and 2022 Economic Census product-line denominators not obtained (API key required); 2012 only.
- Not opened (SNIPPET ONLY): Forman-Ghose-Goldfarb, Zhou-Wang, US Financial Diaries, NielsenIQ and Numerator summaries, DCPC 2019 remote share.
