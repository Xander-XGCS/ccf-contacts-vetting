# Backlog

This backlog keeps the next useful work visible in GitHub. Issues can mirror or replace these items as the project matures.

## Phase 1

- Create the public repository and baseline scaffold.
- Add CI for schema and utility tests.
- Confirm the target Google Drive contacts folder.
- Confirm whether the first Google Sheet should be created from scratch or mapped to an existing workbook.
- Add approval-gated structure suggestion workflow.

## Phase 2

- Build Google Drive folder discovery.
- Crawl the full root folder recursively rather than relying on one fixed contact subfolder.
- Maintain a manifest keyed by stable Google Drive file ID.
- Compare manifests to detect new, modified, removed, moved, and renamed items.
- Map folders and files to people, company, deal, and source candidates.
- Write source inventory rows into the workbook.
- Write sync run rows and proposed file-structure cleanup rows.
- Add run logs and idempotent update behavior.

## Phase 3

- Add file parsing for Google Docs, PDFs, Sheets, CSVs, and plain text.
- Extract people, companies, deals, dates, emails, phone numbers, and addresses.
- Create evidence-backed relationship candidates.
- Add duplicate and identity conflict review workflow.

## Phase 4

- Add public internet research for queued entities.
- File research memos and source links back into Drive.
- Add risk flag classification and confidence scoring.
- Populate `Vetting Research` with credibility scores, score confidence, positive signals, red flags, and open questions.
- Require human review for ambiguous or sensitive findings.

## Phase 5

- Build who-should-talk-to-who recommendations.
- Score intro paths by deal relevance, relationship strength, and recency.
- Generate suggested outreach angles for human approval.
- Track outreach status and stale relationships.
