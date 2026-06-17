# Roadmap

## Phase 1: Foundation

- Create the public GitHub repository.
- Define the initial Google Sheet schema.
- Create research memo templates.
- Add a local folder inventory command.
- Add Drive manifest diffing and structure suggestion models.
- Add tests for schema consistency.

## Phase 2: Drive And Sheets MVP

- Connect to the target Google Drive contacts folder.
- Recursively list files, folders, and shortcuts from the configured root folder.
- Maintain a Drive manifest keyed by stable file ID.
- Detect new, modified, removed, moved, and renamed items between runs.
- Create or update the native Google Sheet.
- Write Drive folder links and source inventory rows.
- Write sync summaries and approval-gated structure suggestions.
- Add run logging and retry-safe updates.

## Phase 3: Extraction

- Parse supported file types.
- Extract people, companies, emails, phone numbers, addresses, deal names, and dates.
- Create relationship candidates with evidence links.
- Add duplicate detection and confidence scoring.

## Phase 4: Research

- Add public web research for queued people and companies.
- Store source URLs, summaries, and accessed dates.
- Write research memos into the appropriate Drive folders.
- Add red flag and open question classification.

## Phase 5: Recommendations

- Build the who-should-talk-to-who tab.
- Score intro paths by deal relevance, relationship strength, and recency.
- Generate suggested outreach angles for human approval.
- Add stale-contact refresh workflows.

## Phase 6: Operations

- Add scheduled or manual run modes.
- Add prompted update mode for "scan now", "scan changed files", and "full rebuild".
- Add audit logs.
- Add owner/reviewer assignments.
- Add release workflow and documentation for nontechnical operators.
