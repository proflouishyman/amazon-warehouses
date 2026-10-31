# bench_network_financial: network and financial benchmarks from 10-Ks

Built 2026-10-31. Companies: Walmart (incl. Sam's Club), Target, Home Depot, Costco, UPS, FedEx; Amazon reused from existing series. Scripts and raw (10-K text, Item 2 extracts, companyfacts and submissions JSON) in `data/raw/benchmark/network_financial/` (`build_facilities.py`, `extract_facts.py`, `build_compare.py`).

## Files (data/processed, long format, every row has accession and source_url)
| file | rows | content |
|---|---|---|
| bench_network_facilities.csv | 558 | Item 2 counts and square feet by facility type, geography, tenure. Walmart FY1999-2025, Costco 2003-2026, Target 2005-2025, Home Depot 2000-2025, UPS 2000-2025, FedEx 2001-2025 (cal_year_approx) |
| bench_network_financial_xbrl.csv | 966 | companyfacts: revenue_total, net_sales_ex_membership, cost_of_revenue, sga_expense, operating_income, capex_ppe, ppe_gross, ppe_net (and incl finance-lease ROU), total_costs_and_expenses; FY2007-2026, 7 companies incl. Amazon. Latest-filed 10-K value per period (restated where revised) |
| bench_network_employees_ecom.csv | 302 | employees (10-K Item 1) and e-commerce disclosures (Walmart e-comm net sales, Home Depot online share FY2013-25, Target digitally originated share, Costco e-commerce/digital share) |
| bench_network_amazon_ref.csv | 111 | Amazon employees, Item 2 square feet, fulfillment expense, reused from existing data/processed series |
| bench_network_filings_index.csv | 187 | every 10-K located (1994-2026) with accession, URL, local raw path |
| bench_network_definitions.csv | 24 | fiscal year ends, what counts as a DC, e-commerce treatment, scope per company |
| bench_network_headline_comparison.csv | 104 | derived 2019 vs 2024 comparison (inputs listed in input_accessions) |

## Headline comparisons (cal_year_approx 2024; bench_network_headline_comparison.csv)
- Revenue per employee (USD k): Costco 764, Amazon 410, Home Depot 339, Walmart 324 (FY ended Jan 2025), Target 242, UPS 186, FedEx 172 (FY ended May 2025; company-wide 510,000 permanent employees, corrected 2026-10-31 from the Federal Express segment's 440,000, see bench_review.md).
- Capex as % revenue: Amazon 13.0 (includes AWS data centers, not a logistics figure), UPS 4.3, FedEx 4.6, Walmart 3.5, Target 2.7, Home Depot 2.2, Costco 1.9.
- Network square feet (thousand) and revenue per sq ft: Amazon 453,163 (NA segment excl. stores and AWS; USD 1,408 per sq ft), Home Depot 108,300 (1,473), UPS US package facilities 90,000 (1,012), Target supply chain 68,500 (1,556), Costco 31,900 (7,977). Walmart and FedEx disclose no comparable warehouse square footage (FedEx one row only).
- Walmart DCs (facilities, Item 2, FY ended Jan 2026): 192 US DCs (125 owned, 67 leased), 179 international; earlier year 195 US incl. 29 Walmart US e-commerce fulfillment centers and 14 Sam's e-commerce centers. See facilities file.
- Target supply chain facilities: 66 (39 owned, 25 leased in count rows), 68.5M sq ft.
- Home Depot: about 500 distribution, fulfillment and warehouse facilities (lower bound), 108.3M sq ft.

## Definitional cautions (full text in bench_network_definitions.csv)
- Fiscal year ends differ (Walmart Jan 31 labelled by end year; Target and Home Depot labelled by start year; Costco late Aug; FedEx May; UPS and Amazon Dec). Use cal_year_approx and period_end, not fiscal_year_label, to align.
- Counts are not comparable: Walmart counts regional DCs, return centers and e-commerce FCs; Target widened to sortation centers from FY2022 (48 to 66 is partly definitional); Costco counts cross-dock depots, and from FY2020 reports only total distribution and logistics sq ft (11.0M depots in FY2019 vs 28.0M FY2020 is a definition change); UPS and FedEx count package sort and delivery buildings, not warehouses. Square feet is the only near-common unit.
- E-commerce: only Walmart gives dollars; Home Depot, Target, Costco give rounded shares with differing labels; UPS and FedEx give none. Target fulfils about 97 percent of sales from stores, Walmart and Home Depot also fulfil from stores, so DC counts do not equal e-commerce capacity.
- FedEx headcount before FY2022 includes contractors; FY2022 onward is the derived sum of company-wide permanent full-time and part-time employees (FY2024-FY2026 corrected 2026-10-31; previously the Federal Express segment figure). Use the basis column. UPS and FedEx XBRL have no SG&A line (total_costs_and_expenses given instead); Amazon fulfillment expense is a custom tag taken from the existing series.
- Latest-filed values are used for XBRL, so early years can reflect restatements (e.g. Target FY2017 revenue reclassification).

## Gaps
- No DC square footage for Walmart or FedEx; Home Depot facility counts only FY2006-2016 and lower bounds after; Home Depot pre-FY2006 retail supply chain not disclosed.
- XBRL starts about FY2007, so pre-2007 financials are not in the XBRL file; pre-2007 facilities and employees come from filing text only.
- SG&A not comparable for UPS, FedEx; no like-for-like "fulfillment cost" outside Amazon.
- UPS and FedEx e-commerce revenue not disclosed; UPS B2C share not found in 10-K text.
- Headline file covers only 2019 and 2024; the full series are in the base files. Costco FY2026 and Walmart FY ended Jan 2026 filings exist in EDGAR as of the build date.
- Not verified here: individual Item 2 numbers beyond spot checks (Target 68.5M sq ft matches filing text, Amazon capex share and employees recomputed). Other Item 2 parses are script-extracted from filing text.
