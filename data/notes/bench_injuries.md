# Benchmark: injuries (Amazon vs retail and logistics peers, OSHA ITA 300A)

Retrieval and build date: 2026-10-31. Script: `scripts/bench_injuries.py` (run `python3 -I scripts/bench_injuries.py` from the project root, about 1 minute). No web searches or downloads were used; every number comes from the local OSHA ITA files in `data/raw/facilities/osha_ita/` (CY2016 to CY2025, https://www.osha.gov/Establishment-Specific-Injury-and-Illness-Data) and the BLS SOII 493110 series already in `data/processed/bls_soii_rates.csv`. Input hashes and row counts: `data/raw/benchmark/injuries/ita_inputs_manifest.json`.

## Files
| File | Rows | Content |
|---|---|---|
| `data/processed/bench_injuries_establishments.csv` | 43,262 | One row per matched peer or Amazon establishment-year inside the logistics scope (rates, rule, OSHA submission id, source) |
| `data/processed/bench_injuries_peer_year.csv` | 446 | Peer x scope x year: establishments, hours, TRC, DART, DAFW (hours-weighted), site median, p25, p75, share of sites above BLS 493110, BLS reference columns |
| `data/processed/bench_injuries_493110_distribution.csv` | 90 | ITA NAICS 493110 site-rate percentiles (p05 to p99) by year and measure, excluding Amazon; also excluding Amazon and all peers; also Amazon 493110 sites alone |
| `data/processed/bench_injuries_name_audit.csv` | 17,835 | Every matched establishment name by peer and NAICS (in-scope rows) with company names, match rules, years, states |
| `data/processed/bench_injuries_match_audit.csv` | 3,338 | Every matched company name x EIN x NAICS with status (included, or the reason for exclusion); raw rows before dedupe |
| `data/raw/benchmark/injuries/ita_inputs_manifest.json` | 1 | Provenance of the inputs |

## Method (identical to the Amazon series, `data/notes/injuries.md`)
- TRC = (DAFW + DJTR + other recordable) x 200,000 / hours; DART = (DAFW + DJTR) x 200,000 / hours; DAFW = DAFW cases x 200,000 / hours. `rate_valid` = hours >= 1,000, employees >= 1, 300 <= hours per employee <= 4,500, all case counts present. Aggregates sum cases and hours over valid sites. Site median, p25 and p75 use valid sites; percentiles are linear-interpolated.
- Dedupe: first the Amazon rule (year, street, city, state, establishment name; keep highest submission id). Added for this workstream: a second pass that drops rows with the same year, address, hours, employees and all case counts (654 rows over all peers and NAICS 493; zero Amazon rows). Reason: Costco (and some Lowe's and FedEx sites) resubmitted the same site under a re-punctuated name (for example "0260 - TOLLESON AZ (WET) DEPOT" and "0260   TOLLESON AZ (WET) DEPOT") and were counted two or three times. This moves ex-Amazon 493110 by at most 0.01 against `injury_comparison_by_year.csv` (2023: 6,905 sites at 3.764 TRC against 6,943 at 3.76).
- Amazon reproduced: NAICS 493 + 492 sites give 1,171 sites and TRC 5.999 in 2024 and 890 and 7.846 in 2021, matching `injury_comparison_by_year.csv` (which uses 493110 + 492110 only; 2019 differs by one site).
- BLS reference is NAICS 493110 (total recordable, DART, days away) for every peer, including parcel carriers, so the "share of sites above BLS" is one yardstick for all. BLS 2025 is not published, so 2025 shares are blank. BLS rates include Amazon.
- Spot check: an independent recomputation from the raw 2024 file gives Walmart 207 sites at 2.787 and GXO 178 at 1.107 against the script's 207 / 2.787 and 177 / 1.109 (one fewer GXO site after the second dedupe pass); Home Depot 83 sites at 3.985 in 493 only against the script's 86 / 3.73, because the script adds 3 retail-coded DC sites.

## Matching rules (one row per peer; code is in `PEERS` in the script)
A row matches when the company name matches the anchored regex (contractors working at a peer site, filed under their own name, never match), or the company is blank and the EIN or establishment name matches, or the EIN is one of the peer's EINs under another company name AND the NAICS is a logistics code (this picks up Kroger "Ruler Logistics", Ryder client-named sites, FedEx Supply Chain client-named sites). Scope: NAICS 493* and 492* count in the headline for every peer. NAICS 42* counts only for 3PL and carrier peers, or for retailers when the establishment name looks like a DC; other retailer 42* rows (Lowe's 423710 names 2807-xxxx and 2807-xxxM, Costco "CW Trading" 423940, Home Depot "THD Pro" 423850) are kept in `scope_group = 42x` with `in_headline = False` because their function is not documented. Stores (445, 444, 452, 455), trucking (484), maintenance (811) and offices (551, 561) are excluded. Where DCs are coded to retail NAICS, a name rule keeps them (`scope_group = retail_coded_dc`): Target 452110/452112/452210 names with DC, FDC, UDC, Fulfillment Center, TFC, Sortation Center, Return Center, Flow Center or Receive Center (the last five added on the 2026-10-31 bench review: CY2024 valid sites 43 to 65, TRC 8.63 to 8.09, DART 7.99 to 7.44; the 65 agrees with the 66 supply chain facilities in the 10-K; all 22 added sites checked by name, none is a store); Home Depot 444110 RDC/MDC/SDC/DC; Lowe's 444190 flatbed distribution and RDC/DFC/ADC; Costco 452311/455211 DDC, MDO, Depot. Rows with state DC are not kept by the name rule (Washington DC stores).

| Peer id | Company rule | Headline NAICS found | Notes |
|---|---|---|---|
| walmart | `^Wal-Mart`/`Walmart` (Wal-Mart Stores East LP, Stores Texas, Walmart Inc., Puerto Rico), `Sam's West/East/Club`, and units filed as "X (Walmart Stores, Inc.)" (Jet.com, Hayneedle, ModCloth, Moosejaw); EINs 71-0862119, 71-0415188, 74-3019386, 71-0794414, 71-0794412, 66-0475164 | 493110 (about 200 DCs a year) | No "Wal-Mart Associates" filer exists in the files. 484 (about 100 a year, private fleet) excluded; Sam's DCs filed under Wal-Mart Stores are not separable. McKesson "Pharma Wal-Mart central fill" excluded |
| target | `^Target$`, EIN 41-0215170 | retail_coded_dc 452xxx: DCs plus, since 2026-10-31, sortation, return, flow and receive centers and Target.com TFC sites (valid sites: 38 in CY2019, 2 in CY2020, 39 to 65 a year from CY2021 to CY2025) | The 887 "D###/G###/R### Office" rows (NAICS 551114, median 5 employees) are store-district offices, excluded |
| home_depot | `^The Home Depot`, EIN 58-1853319 | 493110 RDC/MDO (CY2022 to CY2024 only) + 444110 DC/MDC | No 493 filings before CY2022 |
| lowes | `^Lowe's`, `^Lowes` (not Lowes Foods), EINs 56-0578072, 56-0748358 | 493110 RDC/DFC/ADC + 444190 flatbed DCs | 423710 rows reported as retailer_42x |
| costco | `^Costco`, EINs 91-1223280, 84-4917236 | 493110 depots and MDOs | duplicates removed (see method) |
| kroger | `^Kroger` and banners (Fred Meyer, Dillons, Roundy's, Smith's, Harris Teeter, Ralphs Grocery, King Soopers, Fry's, QFC, City Market, Pick n Save, Mariano's, Baker's), Kroger EINs when under a site name and NAICS 493 | 493110 | 311 dairies, 445 stores excluded |
| ups | `^United Parcel Service`, `^UPS` (not The UPS Store, UPS Flight Forward), EIN 58-2480149 | 492110 package centers and hubs; 493110 Supply Chain Solutions | Worldwide Flight Services (filed under a UPS EIN, 488) and Jetstream excluded |
| fedex_ground | `^FedEx Ground`, EINs 34-1441019, 62-1721435 | 492110 | See gap on CY2024+ |
| gxo | `^GXO`; XPO supply chain predecessor (2017 to 2021) when EIN is a GXO EIN, blank, or the name says Supply Chain; EINs 56-2237457, 42-1399841, 94-3130689, 11-2874859, 86-2098312 | 493110 | match_rule `xpo_supply_chain_predecessor` marks 796 pre-spin rows. Last Mile, freight, express excluded |
| dhl_supply_chain | `^DHL Supply Chain`, `^Exel`, `DHL Continental`, `DHL -`, EIN 04-2801160 | 493110 (+ 422/424 for a few sites) | No filer is named Exel in these files |
| ryder | `^Ryder`, EINs 59-1506958, 87-2620504 | 493110 | 484 fleet and 811 shops excluded |
| fedex_express, fedex_supply_chain, dhl_express_ecom | supplementary peers | 492110 / 493110 / 492110 | Not requested; included because they are the carriers' other logistics arms |
| group_retailer_dcs, group_3pl, group_parcel_carriers | combinations of the primary peers | | Retailer DCs = Walmart, Target, Home Depot, Lowe's, Costco, Kroger; 3PL = GXO, DHL Supply Chain, Ryder; Parcel = UPS, FedEx Ground |
| ita_493_ex_amazon, ita_493110_ex_amazon, ita_493110_ex_amazon_ex_peers | NAICS 493 / 493110 filers with Amazon removed (and peers removed) | | Warehousing as a whole |

Audit: `bench_injuries_name_audit.csv` lists establishment names by peer and NAICS; filter `scope_group` and `match_rules`. `bench_injuries_match_audit.csv` shows every company name that was matched and either included or excluded for a NAICS reason, and XPO rows not matched.

## Headline comparisons, CY2024 (the last complete year; BLS 493110 TRC 4.9, DART 4.3, DAFW 1.6)
Source for every number: `bench_injuries_peer_year.csv`, rows with `scope = headline` and `year = 2024`. "Above BLS" is the share of valid sites whose TRC exceeds 4.9.

| Peer | Valid sites | TRC | DART | DAFW | Site median TRC (IQR) | Sites above BLS TRC |
|---|---|---|---|---|---|---|
| Amazon (493 + 492) | 1,171 | 6.00 | 5.63 | 1.18 | 5.31 (3.11 to 8.00) | 55% |
| Walmart | 207 | 2.79 | 2.36 | 0.64 | 2.57 (1.44 to 3.76) | 14% |
| Target (DCs, sortation, return, flow, receive and TFC sites) | 65 | 8.09 | 7.44 | 3.40 | 5.72 (3.28 to 8.18) | 55% |
| Home Depot | 86 | 3.73 | 3.26 | 1.63 | 4.01 (2.52 to 7.05) | 37% |
| Lowe's (wholesale-coded 423710 rows moved out) | 48 | 2.72 | 2.35 | 1.99 | 3.09 (0.90 to 4.50) | 21% |
| Costco | 81 | 6.13 | 5.16 | 3.90 | 5.85 (3.63 to 9.07) | 63% |
| Kroger | 46 | 5.83 | 5.27 | 4.18 | 4.92 (3.29 to 7.30) | 50% |
| UPS | 1,255 | 8.22 | 6.86 | 3.83 | 7.30 (4.25 to 11.02) | 71% |
| FedEx Ground (CY2024 inferred; `partial_year`, June to December only, NOT a headline comparison) | 625 | 20.44 | 17.61 | 4.53 | 17.85 (10.67 to 24.58) | 90% |
| GXO | 177 | 1.11 | 0.78 | 0.46 | 0.11 (0.0 to 1.64) | 4% |
| DHL Supply Chain | 349 | 1.84 | 1.23 | 0.54 | 0.71 (0.0 to 2.20) | 10% |
| Ryder | 104 | 2.52 | 1.72 | 0.52 | 1.71 (0.0 to 3.57) | 13% |
| Retailer DCs combined | 533 | 4.39 | 3.88 | 1.85 | 3.49 (1.93 to 6.13) | 34% |
| 3PL combined | 630 | 1.70 | 1.16 | 0.51 | 0.85 (0.0 to 2.30) | 9% |
| Parcel carriers combined (UPS only in 2024: FedEx Ground CY2024 excluded as partial_year) | 1,255 | 8.22 | 6.86 | 3.83 | 7.30 (4.25 to 11.02) | 71% |
| ITA NAICS 493 excluding Amazon | 9,094 | 3.69 | 2.97 | 1.57 | 1.51 (0.0 to 4.47) | 23% |
| ITA NAICS 493110 excluding Amazon | 7,395 | 3.71 | 2.96 | 1.62 | 1.54 (0.0 to 4.54) | 23% |

What this shows (all from the table above and the CSVs):
- Amazon's total recordable rate (6.00) is about 1.6 times the ITA 493110 non-Amazon rate (3.71) and 1.2 times the BLS rate; its DART (5.63) is 1.9 times the non-Amazon DART (2.96). Its days-away rate (1.18) is below the non-Amazon rate (1.62): Amazon's excess is restricted and transferred work, not lost time.
- Against Walmart's DCs Amazon is 2.2 times higher on TRC (6.00 against 2.79) and 2.4 times on DART. Against the 3PL operators (GXO, DHL Supply Chain, Ryder) Amazon is 3.5 times the combined rate (1.70). Home Depot, Lowe's and the retailer DCs combined (4.37) sit between.
- Amazon is not the highest. UPS (8.22) is higher on TRC, and FedEx Ground was higher in CY2023 (19.71, full year; its CY2024 figure of 20.44 covers about seven months and is not used), as are Target's supply-chain sites (8.09) and Costco's depots (6.13) on a smaller base; Amazon's days-away rate (1.18) is the lowest of the retailer and parcel group except Walmart (0.64). Within Amazon, the 493 sites (TRC 6.19) and the 492 delivery-station type sites (5.32) differ (`scope = 493` and `492`, same file); UPS 492 is 8.33 and UPS 493 (Supply Chain Solutions, 68 sites) is 3.36.
- Dispersion: 55% of Amazon sites exceed the BLS 4.9, against 23% of non-Amazon 493110 filers. The ex-Amazon median is 1.54 because at least a quarter of the (mostly small) sites report zero cases (p25 = 0); compare means and the hours-weighted rate, not the median, across populations with very different site sizes. Amazon sites are far larger (about 1.12 million hours per valid site against about 0.22 million for 493110 ex-Amazon).
- The ITA 493110 ex-Amazon distribution for 2024 (`bench_injuries_493110_distribution.csv`, `measure = trc`): p25 0.0, p50 1.54, p75 4.54, p90 8.82, p95 12.47, p99 24.87 (7,395 valid sites). Amazon 493110 sites alone: p25 3.32, p50 5.31, p75 7.74, p90 11.00 (501 sites).
- Trend: Amazon fell from 7.85 (2021) to 6.00 (2024); the non-Amazon ITA 493110 rate fell from 4.49 to 3.71; the gap narrowed from 1.75 to 1.62 times on TRC (both from `bench_injuries_peer_year.csv`; CY2025 is partial: Amazon 5.00 against 3.61).

## Caveats
- Self-reported, unaudited ITA data; under-recording differs by employer and cannot be corrected here. Establishment sizes differ sharply (see above) and rates vary with size.
- CY2025 holds only submissions received through 2026-08-31; CY2016 is the first collection year with low compliance. Do not read year-to-year changes in establishment counts as network growth.
- CY2021 and CY2022 recordables include COVID-19 cases at many employers, which inflates Walmart (4.70 in 2021 against 2.33 in 2023), Target and others in those years. Target's CY2021 and CY2022 (TRC 16.0 and 17.0; DAFW 8.7 and 13.1 after the wider match) are as filed and could not be reconciled here.
- Target sites are matched by establishment name (DC, FDC, UDC, fulfillment, TFC, sortation, return, flow and receive center); a supply-chain site filed under another name would be missed. Target filed 2 sites in CY2020.
- Kroger, Lowe's, Home Depot and Ryder have small samples (15 to 110 sites); `low_n_flag` marks site-years with fewer than 10 valid sites.
- XPO rows before the August 2021 spin are matched by name, not by corporate lineage; some may not have become GXO sites.
- NAICS is as filed, and carrier "NAICS 492" sites (hubs, sort centers) are not warehouses in the BLS 493110 sense; the BLS 493110 yardstick is used for all peers for comparability only. BLS 4921 (couriers) is in `bls_soii_rates.csv` for a courier comparison (UPS, FedEx Ground, Amazon 492 sites).

## Gaps
- FedEx Ground CY2024 and CY2025: FedEx merged Ground into Federal Express Corporation in June 2024, so no filing carries the Ground name after CY2023. CY2024+ Ground rows are inferred from address continuity with CY2016 to CY2023 Ground filings (625 sites in 2024, 263 in 2025); 64 (2024) and 586 (2025) Federal Express Corporation rows could not be assigned and sit in `fedex_unassigned_2024plus`. FedEx Express 2024+ is the same inference. Treat the CY2024 Ground figure as approximate and CY2025 as incomplete. Since 2026-10-31 the CY2024 Ground rows carry `partial_year = True`: for the same 585 sites in CY2023 and CY2024, hours fell to 0.62 of the prior year and median hours per employee from 1,048 to 645, so the filings cover about June to December 2024 (after the merger), and 2024 hours, cases and `hours_per_valid_site` are not full-year. The rate (20.44) is roughly preserved because cases and hours fall together, but the row is kept out of headline comparisons (`headline_comparison_ok = False` in `bench_injuries_peer_year.csv`) and out of `group_parcel_carriers` (UPS only in 2024). CY2023 and earlier Ground rows are unflagged and usable. The FedEx Express and unassigned 2024+ rows are full-year by the same test (about 1,600 and 1,530 hours per employee).
- Home Depot has no 493 filings before CY2022; Target is thin in CY2016 to CY2018 and CY2020.
- No Wal-Mart Associates, Exel or Sam's Club DC rows separable from the Walmart company rows. Sam's Club clubs themselves (stores) are excluded.
- Peer wholesale-coded rows (Lowe's 423710, including its 11 DC-named rows in CY2023 to CY2025: Pro Fulfillment Center, 3PL-FC, BDC and ADC; Costco CW Trading, Home Depot THD Pro) are not in the headline; Walmart 484 private fleet, UPS 484 rows and Ryder 484 trucking are excluded by design (the 1,424 UPS 484110 rows are filed as United Parcel Service with SLIC-coded building names, that is UPS package or feeder operations coded as trucking, not UPS Freight; 412 UPS 488xxx rows, air gateways and SCS customs brokerage, are also excluded; FedEx Freight 484 is excluded as trucking) (no trucking comparison was requested).
- Not covered: BLS size-matched rates (BLS access issue noted in `injuries.md`), state-level benchmarks, case-detail (Form 301) data, and 2025 BLS.

## Changes made on 2026-10-31 (bench review fixes)
Backups of every overwritten file are next to the originals as `<name>.pre_final.<ext>`.
- Target matching widened to sortation, return, Target.com fulfillment (TFC), flow and receive centers. CY2024: 43 to 65 valid sites, TRC 8.625 to 8.087, DART 7.989 to 7.443 (matches the reviewer's 65 and 8.09). CY2023: 41 to 61 sites, TRC 6.60 to 6.18. The 22 added CY2024 sites are 11 sortation centers, 2 return centers, 6 TFC sites, 2 flow centers and 1 receive center, all NAICS 452112 or 452210. Detroit Sortation and Hampton GA Flow Center are in the rule's output but not on the reviewer's list.
- FedEx Ground CY2024 flagged `partial_year` (new column in the establishments and peer-year files), out of headline comparisons and groups.
- Lowe's NAICS 423710 rows moved out of the headline (`scope_group = 42x`, `in_headline = False`). The review called these 11 rows "Pro Fulfillment Center"; in fact only the Charlotte Pro Fulfillment Center (3 site-years) has that name. The 11 headline Lowe's 423710 site-years also include 3PL-FC (Denton, Shippensburg), BDC and ADC sites. All 11 are moved because they share the filing code that the note already keeps out. Lowe's CY2024 headline: 52 to 48 sites, TRC 2.68 to 2.72.
- UPS 484 exclusion relabelled (see Gaps). Note text only; no rows changed.
- Group rows: `group_retailer_dcs` 2024 515 to 533 sites (TRC 4.37 to 4.39); `group_parcel_carriers` 2024 1,880 to 1,255 sites (UPS only, TRC 10.36 to 8.22).
- No other peer, Amazon or ex-Amazon row changed (compared against the `.pre_final` file).
