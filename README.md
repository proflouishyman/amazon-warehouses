# Amazon US warehouse network: records and estimates

A static site for exploring Amazon's US logistics network (fulfillment centers, sortation centers, delivery stations, air hubs and related sites), 1997 to today: facilities, finance, labor, workplace injuries compared with warehousing as an industry, logistics and screening-level environmental estimates, and the share of the population living near a site.

Modeled on the `va-datacenter-generator-records` site: plain HTML pages, data embedded as `assets/data_*.js` so it works from `file://`, and every page lists its sources. Open `index.html`.

## What is real and what is an estimate
- Records (10-K figures, OSHA filings, BLS series, NLRB cases, EPA data) are copied from the cited source with the retrieval date (2026-10-31).
- Anything else is labelled an estimate with its method on the Methods page. Facility-level environmental figures are screening estimates, not measurements.
- The facility roster is a lower bound built from OSHA filings and public lists. Most sites have no known opening date.
- No personal data about individual workers is included.

## Layout
- `data/raw/<domain>/` raw downloads (large ones are gitignored). `data/processed/` CSV and JSON. `data/notes/<domain>.md` source tables, methods and gaps. `data/notes/data_globals.md` data dictionary for the generated JS.
- `scripts/` Python (run with `python3 -I`). `assets/` CSS, `common.js` (shared helpers) and generated `data_*.js`.
- `data/private/` is gitignored: nothing from subscription databases may be published except short cited facts.

## Rebuild
```
python3 -I scripts/build_master.py   # facilities_master.csv, OSHA join, environment estimates, population access
python3 -I scripts/build_data.py     # assets/data_*.js and data/notes/data_globals.md
```
Dataset sources and caveats live in `scripts/dataset_catalog.py` (rendered on `sources.html`).

Local only, never public: `scripts/serve_local.sh` builds with `--private` (gitignored `assets/private_*.js`), serves 127.0.0.1:8765 and opens extra "Local only" sections and local-file links; `scripts/stop_local.sh` stops it, and `scripts/check_public.sh` (run by the pre-commit hook) blocks private material.

## Status
Published at https://proflouishyman.github.io/amazon-warehouses/ (not indexed). Before every commit, check the diff for anything private; the pre-commit hook runs `scripts/check_public.sh`, and commits use the GitHub no-reply author address.
