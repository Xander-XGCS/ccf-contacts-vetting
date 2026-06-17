# CCF Contacts Vetting

Automation and operating docs for building a Google Drive and Google Sheets based relationship intelligence system for Complete Capital Funding contacts, deals, projects, and research evidence.

GitHub is the source of truth for the system design, code, schemas, prompts, and runbooks. Google Drive remains the operational home for contact folders, source documents, research memos, and the live Google Sheet.

## What This Project Builds

The first production target is a smart Google Sheet backed by Drive folders and agent-assisted research.

The system should:

- Inventory the full Complete Capital Funding Google Drive folder recursively, even when the folder structure changes.
- Extract people, companies, deals, projects, contact details, and relationship evidence.
- Detect new, modified, removed, moved, and renamed Drive files across repeat runs.
- Normalize duplicates and uncertain identity matches.
- Research people and companies using public internet sources.
- File research notes and source links back into the right Drive folders.
- Update a Google Sheet with structured data, evidence links, confidence levels, and review status.
- Suggest Drive file or folder cleanup actions, while requiring explicit approval before anything is moved or renamed.
- Recommend who should talk to whom based on relationship paths, deal relevance, and outreach priority.

## Source Of Truth

GitHub owns:

- Application code
- Sheet schemas
- Research policies and prompts
- Drive folder conventions
- Tests and fixtures
- Change history for automation behavior

Google Drive owns:

- Live contact folders
- Original documents
- Research memos
- Web source exports when appropriate
- The operational Google Sheet

Do not commit private contacts, deal documents, research artifacts, credentials, exports, or downloaded source material to this repository.

## Initial Tabs

- `Start Here`
- `File Inventory`
- `Updates`
- `Suggested Folder Changes`
- `People`
- `Companies`
- `Deals & Projects`
- `Relationships`
- `Research Queue`
- `Vetting Research`
- `Evidence Sources`
- `Intro Recommendations`
- `Human Review`

See [docs/sheet-schema.md](docs/sheet-schema.md) for the initial workbook design.

## Local Development

This scaffold uses only the Python standard library at the start.

```powershell
python -m unittest discover -s tests
```

Generate a Markdown view of the workbook schema:

```powershell
$env:PYTHONPATH="src"; python -m ccf_contact_vetting.cli schema --format markdown
```

Extract a Drive ID from a folder URL:

```powershell
$env:PYTHONPATH="src"; python -m ccf_contact_vetting.cli drive-id --url "https://drive.google.com/drive/folders/..."
```

Inventory a locally synced/exported folder:

```powershell
$env:PYTHONPATH="src"; python -m ccf_contact_vetting.cli inventory-local --root "C:\path\to\folder" --output outputs\inventory.csv
```

Generate approval-gated file structure suggestions from a Drive manifest:

```powershell
$env:PYTHONPATH="src"; python -m ccf_contact_vetting.cli structure-suggestions --manifest outputs\drive_manifest.json --root-id "<folder-id>" --output outputs\structure_suggestions.csv
```

Extract entity candidates from a local text file:

```powershell
$env:PYTHONPATH="src"; python -m ccf_contact_vetting.cli extract-text --input outputs\sample.txt --source-id "<drive-file-id>" --title "Sample Source"
```

See [docs/extraction.md](docs/extraction.md) for how deterministic extraction, duplicate matching, and AI-assisted vetting are separated.

The Drive text extraction bridge converts readable Drive file text into Sheet-ready candidate rows for review tabs.
The parser run planner supports dry-run summaries before any live Sheet append.
The vetting helper creates consistent credibility and human-review rows for researched people and companies.
OCR fallback supports scanned PDFs/images when native text extraction returns empty; see [docs/ocr.md](docs/ocr.md).
Profile summaries should refresh when entity evidence changes; see [docs/profile-refresh.md](docs/profile-refresh.md).

Spreadsheet-triggered research can be added with a bound Apps Script menu; see [docs/spreadsheet-trigger.md](docs/spreadsheet-trigger.md).

## Roadmap

1. Define the workbook schema and Drive evidence model.
2. Build local and Google Drive inventory with incremental change detection.
3. Add Google Drive and Google Sheets connector integration.
4. Add entity extraction and relationship graph generation.
5. Add public internet research runs with source capture.
6. Add human review, risk flags, and who-should-talk-to-who recommendations.
