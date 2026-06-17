# CCF Contacts Vetting

Automation and operating docs for building a Google Drive and Google Sheets based relationship intelligence system for Complete Capital Funding contacts, deals, projects, and research evidence.

GitHub is the source of truth for the system design, code, schemas, prompts, and runbooks. Google Drive remains the operational home for contact folders, source documents, research memos, and the live Google Sheet.

## What This Project Builds

The first production target is a smart Google Sheet backed by Drive folders and agent-assisted research.

The system should:

- Inventory contact folders and source files in Google Drive.
- Extract people, companies, deals, projects, contact details, and relationship evidence.
- Normalize duplicates and uncertain identity matches.
- Research people and companies using public internet sources.
- File research notes and source links back into the right Drive folders.
- Update a Google Sheet with structured data, evidence links, confidence levels, and review status.
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

- `Dashboard`
- `People`
- `Companies`
- `Deals Projects`
- `Relationships`
- `Research Queue`
- `Sources`
- `Who Should Talk To Who`
- `Review Log`

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

Inventory a locally synced/exported folder:

```powershell
$env:PYTHONPATH="src"; python -m ccf_contact_vetting.cli inventory-local --root "C:\path\to\folder" --output outputs\inventory.csv
```

## Roadmap

1. Define the workbook schema and Drive evidence model.
2. Build local folder inventory and parsing for exported/synced Drive content.
3. Add Google Drive and Google Sheets connector integration.
4. Add entity extraction and relationship graph generation.
5. Add public internet research runs with source capture.
6. Add human review, risk flags, and who-should-talk-to-who recommendations.

