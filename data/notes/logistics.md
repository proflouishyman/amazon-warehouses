# Logistics domain notes (retrieved 2026-10-31)

Scripts: scripts/logistics_01_osha_site_counts.py, logistics_02_build_tables.py, logistics_03_build_tables.py (run with python3 -I).
Raw: data/raw/logistics/sec10k (26 Amazon 10-Ks, FY2000-FY2025, from SEC EDGAR; `_item2_extract.txt` is the Item 2 text), data/raw/logistics/pb (Pitney Bowes press releases 2020, 2021, 2023, 2024, 2025-Nasdaq copy). Pages read only through the web-fetch tool (MWPVL, Wikipedia, Moraine, Amazon Science, Supply Chain Dive, ChannelX, Post&Parcel, aboutamazon.com) were not saved as files; their figures are transcribed into the CSVs with URLs.
No JHU subscription sources used (Chrome login not checked or needed). Nothing in data/private.

## Datasets
| File | Source | Coverage | Key caveats |
|---|---|---|---|
| logistics_sqft_by_year.csv | Amazon 10-K Item 2 via sec.gov | FY2004-FY2025 (FY2000-03 in separate file) | Definitions change: FY2004-10 fulfillment and warehouse only; FY2011+ include data centers (AWS) and "other", so NA line overstates logistics space. NA-segment-less-stores column (FY2017+) is the cleaner proxy. Units thousand sq ft. FY1997-1999 not extracted (FY1999 10-K has no primary document in EDGAR index). |
| logistics_us_fc_counts_2000_2003.csv | 10-K text | FY2000-03 | Only true counts of fulfillment centers from a primary source. FY2000 count of 8 is my reading (7 listed + McDonough closing). |
| logistics_osha_site_counts_by_year.csv | OSHA ITA 300A via facilities-domain extract (data/raw/facilities/osha_amazon_rows.csv) | CY2016-2025 | LOWER BOUND. Distinct Amazon site codes with a filing. Only filing establishments appear; 300A has covered NAICS 4931 sites with 20+ employees since 2016 data, so growth reflects network growth and compliance (2016 data were collected late, low compliance at first), not rule changes. Type split by NAICS is unreliable before 2021 (delivery stations filed under 493110 in 2019-20). 2025 gives 1,417 vs Moraine 1,399 (same underlying filings). |
| logistics_facility_count_snapshots.csv | Moraine Research (2025), Transport Geography/MWPVL (2021), MWPVL | single dates | Moraine's per-type table is the only per-type count found; third-party, depends on OSHA+CoStar matching. Redstag "about 90 sort centers" (MWPVL Q1 2025) contradicts Moraine 162; flagged, not reconciled. |
| logistics_air_fleet.csv, logistics_air_hubs.csv | Wikipedia (Amazon Air), trade press | 2016-2025 | All secondary. Fleet totals differ by source (101 Jan 2025 vs 104 Dec 2024). The uncited 33 aircraft (June 2018) was excluded. Official Amazon/ATSG filings not retrieved. |
| logistics_dsp.csv | aboutamazon.com, ChannelX, Post&Parcel, GeekWire (summary) | 2018-2024 | Counts are global, from Amazon statements; 2023-24 values rest on a search summary of GeekWire (page blocked). 390,000 may be cumulative. No US-only van fleet count found: only the 20,000-van order (Sept 2018). A Murphy-letter figure of 3,500 "DSPs and fleet management companies" could not be verified and is excluded. |
| logistics_us_parcel_volume.csv | Pitney Bowes Parcel Shipping Index press releases | 2018-2024 | Volume basis includes B2B/B2C parcels <=70 lb; Amazon Logistics = parcels delivered by Amazon's own network. Earlier-year totals are restated between editions (2022: 21.2 -> 21.5; 2021: 21.5 -> 21.7). 2020 carrier levels were only in secondary coverage so are not recorded. 2024 shares are computed here, labelled. 2022 shares for USPS/UPS/FedEx come from a secondary report of the release. |
| logistics_timeline.csv | all of the above | 1997-2025 | Confidence column on each row. |

## Method: facility counts by type by year
No public source gives a continuous series of facility counts by type. What exists:
1. Primary, annual: 10-K square footage (NA fulfillment and other, 2004-2025) and exact FC counts for 2000-03.
2. Primary-derived, annual 2016-2025: distinct site codes in OSHA ITA filings (lower bound; type via NAICS after 2021 only; Moraine shows the site-code-to-type match is possible using Amazon's June 2025 facility list, which I did not retrieve).
3. Single-date snapshots by type: Moraine 2025 (1,399 sites).
Integrator options: (a) show sq ft and OSHA site counts as the time series and the Moraine table as a 2025 composition; (b) if a per-type history is wanted, apply the 2025 composition to OSHA counts and label it an estimate (an assumption, not a measurement; composition certainly differed in 2016-2020). I did not do (b).
MWPVL International (mwpvl.com) is the standard industry tracker but its counts sit in embedded images and a paid spreadsheet; not obtained.

## Method note: share of US population within X miles of a facility (for the integrator)
- Inputs: facility geocodes (street addresses in OSHA ITA rows -> Census Geocoder batch API, or ZIP centroid fallback; site type from Moraine/Amazon site list), Census 2020 block-group or ZCTA centroids with population (decennial P1_001N), US-only.
- Compute the great-circle (haversine) distance from each block-group centroid to the nearest facility of a type (BallTree on radians); sum population with distance <= X (e.g. 10, 25, 50, 100 miles) / total US population. Radius is straight-line, not drive time; say so.
- By year: use sites with OSHA filing in that year (a lower bound; 2016-2020 delivery stations may be unseen, so early-year shares are understated); use the decennial population nearest the year (2000, 2010, 2020), not interpolated, or label interpolation.
- Report separately for delivery stations (last mile), FCs, and same-day sites; the 2025 snapshot is the best-supported.
- Caveat: OSHA address can be a parent/ops address and many addresses are suites; geocode match rate must be reported.

## Gaps
- No continuous, cited facility count by type per year (see above).
- No official Amazon Air fleet series; fleet figures are secondary and inconsistent. Amazon's own CVG press release not retrieved.
- No US-only DSP count or current van fleet; Rivian/EV van deployment not covered.
- Prime milestone dates (2005, 2015, 2019, 2020) are from secondary summaries; Amazon press releases not retrieved. Same-day metro list not compiled.
- Pitney Bowes: 2021 edition (2020 data) carrier levels, and any pre-2018 history, not obtained; no Amazon Logistics vs UPS/FedEx/USPS data for 2024 FedEx/UPS levels (release text only names USPS and Amazon).
- Statista/ProQuest not used.
- Pitney Bowes businesswire pages returned HTTP 403; PDFs from Pitney Bowes' IR CDN were used instead.
