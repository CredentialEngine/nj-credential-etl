# NJ Credential ETL

Scripts for extracting and transforming credential, course, and competency
data from New Jersey community college websites and PDF catalogs, and
producing "BU" (bulk-upload) files formatted for Credential Engine's
Credential Registry.

## Structure

Each college has its own top-level folder, generally split into `credentials/`
(or `credential/`), `courses/` (or `course/`), and `noncredit/` subfolders
(sometimes further split by term/year, e.g. `2024-2025/`, `2026/`). A few
colleges also have a nested `ed2go/` folder for that vendor's course catalog.

```
<college>/
├── credentials/   # credit credential (degree/certificate) pipeline
├── courses/       # credit course pipeline
└── noncredit/     # noncredit programs and courses, incl. ed2go/ subfolder
```

`aggregate/` holds cross-college scripts that run after the per-college
pipelines to roll everything up (counts, combined credential BU output,
CSV-to-Excel consolidation).

## Pipeline convention

Within each subfolder, scripts are numbered in the order they're meant to
run. The exact steps vary a bit by college/source, but the general pattern
is:

1. **Parse / get links** — pull program or course URLs out of a saved
   catalog page (or hit a JSON API, e.g. Coursedog) to build a list of
   pages to fetch.
2. **Download** — fetch each linked HTML page or PDF to disk.
3. **Parse** — extract structured fields (name, description, credential
   type, competencies, etc.) from the downloaded HTML/PDF into CSV/JSON.
4. **Join / combine** — merge multiple intermediate CSV/JSON files together.
5. **Produce BU** — reshape the combined data into Credential Engine's bulk
   upload column format, generating a `CTID` (a public UUID identifier, not
   a secret) per row where one doesn't already exist.

Where a step has multiple numbered variants (e.g. `3ParseHTML2.py`,
`3ParseHTML3.py`), those are iterations on the same step, kept for
reference — not all variants are meant to be run.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Some scripts drive a real browser via Selenium for JavaScript-rendered
pages; those need a matching chromedriver, handled automatically by
`webdriver_manager`.

### Credentials

`middlesex/credential/review/upload/OrgCredentialsAll.py` calls the
Credential Engine Assistant Search API and expects an API token in the
environment:

```bash
export CE_ASSISTANT_API_TOKEN=your-token-here
```

## ⚠️ Known limitation: hardcoded local paths

These scripts were written for one-off runs against a specific local
folder layout and **most of them (191 of 221) hardcode absolute Windows
paths**, e.g.:

```python
file_path = r"C:\text\NJ\Atlantic Cape\credentials\Degrees and Certificates _ Atlantic Cape Community College.html"
```

They are not portable as-is — running one on another machine (or even a
different drive letter) requires editing its input/output paths first.
This repo intentionally contains only the scripts, not the scraped
HTML/PDF/image data they read from or write to, so treat each script as a
reference implementation for its pipeline step rather than a
run-anywhere tool.

## What's not here

Only `.py` files were pulled into this repo. The source folder also
contains the scraped HTML pages, downloaded PDFs, images, and generated
CSV/JSON/Excel outputs for every college — left out both for size and
because most of it is copyrighted or scraped third-party content.
