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
2. Compare the current Drive manifest against the prior manifest.
3. Record new, modified, removed, moved, and renamed items.
4. Extract entities and contact points from changed or unprocessed files using deterministic rules.
5. Normalize duplicates and route uncertain identity matches to review.
6. Update the workbook with structured rows.
7. Queue entities for research.
8. Research public sources and capture evidence.
9. File research memos into Drive.
10. Update the workbook with summaries, links, confidence, and review status.
11. Recommend outreach paths and next best actions.

## Incremental Sync

The folder tree is expected to change. The system should therefore treat Google Drive file IDs as stable primary keys and folder paths as mutable metadata.

Each sync run should:

- Crawl the configured root folder recursively.
- Store a manifest row for every file, folder, and shortcut.
- Compare file IDs against the prior manifest.
- Detect new, modified, removed, moved, and renamed items.
- Re-parse only new or changed files unless a full rebuild is requested.
- Write a summary to the `Updates` tab.

## Structure Suggestions

The system may propose folder cleanup, but it must not move or rename Drive files automatically.

Examples of proposed actions:

- Rename folders with trailing whitespace.
- Review duplicate folder names under the same parent.
- Move root-level loose files into an intake folder.
- Create missing research memo folders.
- Split mixed deal/contact folders when evidence supports it.

Every suggestion should include a reason, target file ID, current path, proposed path or name, confidence, and status in `Suggested Folder Changes`. Only approved suggestions should be applied.

## Human Review

The automation should flag uncertainty rather than bury it. Human review is required for:

- Low-confidence identity matches
- Serious risk flags
- Conflicting source information
- Recommended outreach involving sensitive relationships
- Any conclusion that depends on private or non-public information
- Any proposed Drive file move, folder move, or rename

## Deterministic Versus AI-Assisted

Deterministic code owns crawling, manifest diffing, stable IDs, sheet row construction, exact matching, and review queue creation.

AI-assisted steps should sit behind those rails. They can summarize documents, interpret relationship context, perform public web vetting, draft credibility notes, and recommend introductions, but their outputs should retain source links, confidence levels, and review statuses.
