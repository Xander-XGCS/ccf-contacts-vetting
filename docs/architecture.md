# Architecture

## Principle

The live business workflow belongs in Google Drive and Google Sheets. The repeatable system that maintains it belongs in GitHub.

## Components

### Google Drive

Drive stores contact folders, original documents, research memos, source files, and review artifacts.

Each contact or company folder should eventually contain:

- Original source documents
- A dated research memo
- Links to public sources
- Extracted profile summary
- Open questions and human review notes

### Google Sheets

The Sheet is the operational control surface. It should be easy to filter, review, correct, and use for outreach planning.

The Sheet should not hide uncertainty. Columns for evidence, confidence, status, and human review are core system features.

### GitHub

GitHub stores:

- Code that scans and updates the system
- Workbook schemas
- Prompt and research policy versions
- Tests
- Runbooks
- Release notes

GitHub should never store private contacts, confidential deal files, or raw research exports.

## Pipeline

1. Inventory source folders and files.
2. Extract entities and relationship hints.
3. Normalize duplicates and uncertain identities.
4. Update the workbook with structured rows.
5. Queue entities for research.
6. Research public sources and capture evidence.
7. File research memos into Drive.
8. Update the workbook with summaries, links, confidence, and review status.
9. Recommend outreach paths and next best actions.

## Human Review

The automation should flag uncertainty rather than bury it. Human review is required for:

- Low-confidence identity matches
- Serious risk flags
- Conflicting source information
- Recommended outreach involving sensitive relationships
- Any conclusion that depends on private or non-public information

