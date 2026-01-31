# Yahoo Auctions KPI Toolkit

This repository contains a lightweight toolkit for extracting and transforming
wheel listing data from Yahoo Auctions into structured outputs. The toolkit is
split across four KPI modules that can be composed into a processing pipeline.

## Project layout

```
src/
  helpers.py             # shared utilities (HTTP fetching, cleaning helpers)
  kpi1_extract.py        # Yahoo Auction URL -> listing metadata
  kpi2_parse_specs.py    # listing metadata -> normalized specifications
  kpi3_title_generate.py # specifications -> structured title
  kpi4_desc_generate.py  # specifications + raw description -> HTML section
  schema.json            # JSON schema describing the spec payload

tests/
  kpi1_smoke_test.py     # minimal smoke test for KPI1
  sample_urls.txt        # placeholder for manual testing

requirements.txt         # runtime dependencies
```

## Usage

All KPI modules expose pure functions that return JSON-serializable payloads:

- `src.kpi1_extract.extract_listing(url)` fetches a listing and returns a
  dictionary with the title, price, shipping, description HTML, and photo URLs.
- `src.kpi2_parse_specs.parse_specs(listing)` parses brand, model, and other
  wheel dimensions from the listing dictionary.
- `src.kpi3_title_generate.generate_title(specs)` produces a structured title
  string using the parsed specs.
- `src.kpi4_desc_generate.generate_description(specs, raw_description)`
  generates an HTML section for downstream use.

Values that cannot be determined are represented by the literal `"不明"`.

## Development

Install dependencies:

```bash
pip install -r requirements.txt
pip install pytest  # optional for running the included tests
```

Run the smoke test:

```bash
pytest
```

Populate `tests/sample_urls.txt` with URLs for manual experimentation. The
provided helper functions use a desktop user agent and retry logic to avoid
transient failures.
