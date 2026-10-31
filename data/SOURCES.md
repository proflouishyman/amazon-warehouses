# Source library

Snapshot 2026-10-31. Every file under `data/raw` and `data/private` is catalogued in a local manifest (9,744 files, 7.0 GB). The public-access files are listed one row per file in [`sources_manifest_public.csv`](sources_manifest_public.csv) (4,899 rows); subscription files are counted here but not listed. Nothing was moved or deleted to build it: files that scripts read stay where the scripts expect them, and the catalog points at them in place. 4,899 files (6.4 GB) are public sources; 4,845 files (609 MB) come from JHU subscription databases.

Both folders are gitignored (`data/raw/`, `data/private/`). This guide and the public manifest are the public record of the public sources.

## Manifest columns

`source_id` (stable: hash of the path), `title`, `publisher`, `publication_date`, `url_or_doc_id`, `access` (public, jhu_subscription, paid), `domain`, `local_path` (relative to the project root), `size_bytes`, `sha256`, `retrieved_date`, `used_by` (scripts, notes and processed files that cite the file; first 12 shown), `role`, `flags`.

`role` separates original sources (`source`, `source_image`) from derived or housekeeping files stored next to them (`derived_text`, `derived_ocr`, `extracted`, `derived_extract`, `derived_geocode`, `derived_parse`, `catalog`, `search_results`, `work_file`, `challenge_page`, `probe`, `code`, `unindexed`).
`flags` holds `orphan`, `duplicate_group_of_N` (first copy), `duplicate_of:<source_id>` (later copies), `empty_file`, `challenge_page_not_article`, `notes_mention_only`, `work_file`.

## Layout by domain and publisher (public sources)

### Facilities (513 files, 177 MB)

| Publisher | Files | Size | Where |
|---|---:|---:|---|
| MWPVL via Internet Archive (snapshots, table images, OCR) | 426 | 139 MB | `data/raw/mwpvl_wayback` |
| U.S. Census Bureau | 67 | 33 MB | `data/raw/census`, `data/raw/facilities` |
| U.S. Census Bureau Geocoder | 8 | 382 KB | `data/raw/facilities` |
| MWPVL International | 4 | 290 KB | `data/raw/facilities` |
| TaxJar | 3 | 285 KB | `data/raw/facilities` |
| Cavacopedia | 1 | 0 KB | `data/raw/facilities` |
| OSHA | 1 | 2 MB | `data/raw/facilities` |
| WarehouseGig | 1 | 59 KB | `data/raw/facilities` |
| Wikidata | 1 | 1 KB | `data/raw/facilities` |
| Wikipedia | 1 | 2 MB | `data/raw/facilities` |

### Financial (1,668 files, 976 MB)

| Publisher | Files | Size | Where |
|---|---:|---:|---|
| State and local subsidy records (50 states and DC) | 1,003 | 482 MB | `data/raw/subsidies` |
| SEC EDGAR (Amazon and peer 10-Ks, submissions, XBRL facts) | 657 | 494 MB | `data/raw/benchmark`, `data/raw/financial` |
| Project code kept beside the data (not sources) | 4 | 52 KB | `data/raw/benchmark` |
| Good Jobs First | 4 | 46 KB | `data/raw/financial`, `data/raw/facilities` |

### Labor (2,458 files, 2,841 MB)

| Publisher | Files | Size | Where |
|---|---:|---:|---|
| NLRB | 2,105 | 547 MB | `data/raw/labor`, `data/raw/benchmark` |
| U.S. BLS QCEW | 164 | 1,917 MB | `data/raw/labor` |
| SEC EDGAR (Amazon and peer 10-Ks, submissions, XBRL facts) | 159 | 361 MB | `data/raw/benchmark`, `data/raw/labor` |
| Press and company wage releases | 24 | 15 MB | `data/raw/benchmark`, `data/raw/labor` |
| Project code kept beside the data (not sources) | 4 | 7 KB | `data/raw/benchmark` |
| Housekeeping files | 2 | 0 KB | `data/raw/labor` |

### Injuries (46 files, 1,795 MB)

| Publisher | Files | Size | Where |
|---|---:|---:|---|
| OSHA | 41 | 1,707 MB | `data/raw/injuries`, `data/raw/facilities`, `data/raw/benchmark` |
| U.S. BLS | 4 | 179 KB | `data/raw/injuries` |
| OSHA / BLS | 1 | 88 MB | `data/raw/injuries` |

### Environment (86 files, 397 MB)

| Publisher | Files | Size | Where |
|---|---:|---:|---|
| U.S. EPA | 22 | 199 MB | `data/raw/environment` |
| UPS | 10 | 2 MB | `data/raw/benchmark` |
| U.S. EIA | 9 | 555 KB | `data/raw/environment` |
| SEC EDGAR (Amazon and peer 10-Ks, submissions, XBRL facts) | 7 | 27 MB | `data/raw/benchmark` |
| Target | 7 | 30 MB | `data/raw/benchmark` |
| Amazon | 5 | 26 MB | `data/raw/environment` |
| South Coast AQMD | 5 | 13 MB | `data/raw/environment` |
| FedEx | 4 | 34 MB | `data/raw/benchmark` |
| The Home Depot | 4 | 29 MB | `data/raw/benchmark` |
| Walmart | 4 | 23 MB | `data/raw/benchmark` |
| U.S. EPA ECHO | 3 | 224 KB | `data/raw/environment` |
| Project code kept beside the data (not sources) | 2 | 40 KB | `data/raw/benchmark` |
| Costco | 2 | 12 MB | `data/raw/benchmark` |
| U.S. Census Bureau | 1 | 4 KB | `data/raw/environment` |
| U.S. Court of Appeals, Ninth Circuit | 1 | 239 KB | `data/raw/environment` |

### Logistics (35 files, 47 MB)

| Publisher | Files | Size | Where |
|---|---:|---:|---|
| SEC EDGAR (Amazon and peer 10-Ks, submissions, XBRL facts) | 29 | 47 MB | `data/raw/logistics` |
| Pitney Bowes | 5 | 523 KB | `data/raw/logistics` |
| Senator Chris Murphy / Amazon | 1 | 1 KB | `data/raw/logistics` |

### Industry (93 files, 196 MB)

| Publisher | Files | Size | Where |
|---|---:|---:|---|
| U.S. Census Bureau | 55 | 175 MB | `data/raw/benchmark` |
| Project code kept beside the data (not sources) | 8 | 29 KB | `data/raw/benchmark` |
| Pitney Bowes | 6 | 797 KB | `data/raw/industry` |
| U.S. BLS OEWS | 4 | 6 MB | `data/raw/benchmark` |
| Economic Policy Institute | 3 | 535 KB | `data/raw/industry` |
| Journal of Transport and Land Use | 2 | 10 MB | `data/raw/industry` |
| The Real Deal | 2 | 314 KB | `data/raw/industry` |
| The Geography of Transport Systems | 2 | 332 KB | `data/raw/industry` |
| U.S. BLS QCEW | 1 | 69 KB | `data/raw/benchmark` |
| University of Minnesota | 1 | 198 KB | `data/raw/industry` |
| Avison Young | 1 | 948 KB | `data/raw/industry` |
| Commercial Observer | 1 | 181 KB | `data/raw/industry` |
| CompStak | 1 | 170 KB | `data/raw/industry` |
| MWPVL International | 1 | 80 KB | `data/raw/industry` |
| Christian Science Monitor | 1 | 82 KB | `data/raw/industry` |
| Entrepreneur | 1 | 223 KB | `data/raw/industry` |
| Toronto Star | 1 | 383 KB | `data/raw/industry` |
| Yahoo / Business Insider | 1 | 520 KB | `data/raw/industry` |
| Wikipedia | 1 | 18 KB | `data/raw/industry` |

Note on `data/raw/benchmark/`: it holds the peer-company comparison inputs (Costco, FedEx, Home Depot, Target, UPS, Walmart) for the environment, injuries, labor, network/financial and warehousing-industry benchmarks. Its 10-K copies overlap the Amazon 10-K folders (`financial/tenk`, `labor/10k`, `logistics/sec10k`), which is where most duplicates come from.

## Public and subscription-only

**Public** (`access = public`): government and agency data (SEC, BLS, Census, OSHA, EPA, NLRB, state and local records), company reports, the MWPVL Wayback snapshots, press pages and academic papers. Third-party pages and PDFs are kept locally for provenance but the raw folder is not published (some are copyrighted); rebuild with `scripts/`.

**Subscription-only** (`access = jhu_subscription`): everything under `data/private/`, fetched through the JHU Sheridan Libraries licence. Never publish the files, text, extracts or quotes from them. This guide gives counts only for these rows. Facts drawn from them appear on the pages cited as publication, date, title (via database), with no long quotations and no proxy links; the citations are listed in `data/processed/bibliography_subscription.csv`.

| Database | Files | Size |
|---|---:|---:|
| `ebsco_regional_business_news` | 771 | 9 MB |
| `ebsco_business_source_ultimate` | 748 | 8 MB |
| `newsbank_access_world_news` | 670 | 20 MB |
| `proquest_central` | 481 | 4 MB |
| `nexis_uni` | 397 | 5 MB |
| `wsj_proquest` | 394 | 5 MB |
| `sp_capital_iq_netadvantage` | 219 | 88 MB |
| `mergent_archives` | 173 | 298 MB |
| `ibisworld` | 169 | 4 MB |
| `proquest_us_newsstream` | 140 | 5 MB |
| `proquest_business_market_research` | 109 | 80 MB |
| `mergent_market_atlas` | 95 | 2 MB |
| `hoovers_avention` | 73 | 18 MB |
| `value_line` | 67 | 3 MB |
| `proquest_abi_inform` | 66 | 9 MB |
| `ft_com` | 61 | 566 KB |
| `statista` | 48 | 21 MB |
| `industry` | 41 | 693 KB |
| `_access_probe_2026-10-31` | 33 | 21 MB |
| `marketresearch_com_academic` | 27 | 1 MB |
| `eiu_data` | 21 | 403 KB |
| `mergent_intellect` | 20 | 5 MB |
| `gale_directory_library` | 17 | 934 KB |
| `sage_business` | 5 | 109 KB |

By domain (subscription files): facilities 1,836, financial 297, labor 731, injuries 0, environment 0, logistics 719, industry 1,262.

No `paid` (one-off purchase) sources are held. The manifest `domain` for subscription articles comes from the database folder or the topic recorded at fetch time.

## Duplicates

251 groups of identical files (same sha256) hold 354 redundant copies, about 1,359 MB. Nothing was deleted. The first copy in path order is the group head; later copies are flagged `duplicate_of:<head source_id>`.

Main duplicate families (copies, by folder pair):

- 123 copies: `data/raw/benchmark/labor` and `data/raw/benchmark/network_financial`
- 51 copies: `data/raw/mwpvl_wayback/ocr_local/Unlimited-OCR-2-4bit`
- 31 copies: `data/raw/financial/tenk` and `data/raw/labor/10k`
- 26 copies: `data/raw/financial/tenk` and `data/raw/logistics/sec10k`
- 15 copies: `data/private/mergent_market_atlas/peer_financials/_failed_lookups`
- 11 copies: `data/raw/mwpvl_wayback/images/2026`
- 8 copies: `data/raw/mwpvl_wayback/images/2019`
- 8 copies: `data/raw/mwpvl_wayback/images/2020`

Typical causes: peer and Amazon 10-Ks fetched into several folders; OSHA ITA zips kept in both `facilities/osha_ita` and `injuries`; identical MWPVL Wayback snapshots; repeated image crops; empty `item2` extracts (28 empty files, flagged `empty_file`).

## Orphans

An orphan is a file that no script, note, page or processed file cites by filename, document id or accession, and whose directory no script or note names. 3,330 files are flagged: 2 public and 3,328 subscription.

- `data/raw/labor/nlrb/case_sample.html`: Amazon.com Services LLC | National Labor Relations Board
- `data/raw/labor/nlrb/search1.html`: Case Search | National Labor Relations Board

The subscription orphans are saved full-text articles, search-result dumps, screenshots and probe files from which no fact row has been extracted yet (they are kept, not discarded). Largest groups: `ebsco_business_source_ultimate/facilities` 463, `newsbank_access_world_news/facility_events` 353, `ebsco_regional_business_news/labor` 264, `newsbank_access_world_news/_searches` 190, `proquest_central/facilities_openings` 131. Citation matching depends on `data/processed/jhu_*.csv` as of the snapshot; parallel extraction runs may cite more of them later. Rerun the build script to refresh.

**ProQuest challenge pages**: 179 saved ProQuest pages are robot-challenge pages, not articles (role `challenge_page`): 168 in `proquest_central`, listed in `blocked_pending_fulltext.csv` for re-fetch once a person clears the challenge in the browser, and 11 in `proquest_abi_inform/_challenge_pages`. Their titles in the manifest are the article titles the page was meant to load, not content.

## Rebuild

`python3 scripts/build_sources_manifest.py` rewrites the local manifest (read-only on the sources, about 10 seconds); `python3 scripts/build_sources_public.py` writes the public manifest and rewrites this file from it.
