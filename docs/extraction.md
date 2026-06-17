# Extraction And Matching

The extraction layer is deterministic by default. It should make repeatable, auditable suggestions from Drive document text before any AI research agent touches the data.

## What Is Deterministic

- Drive crawling and manifest diffs use Google Drive file IDs.
- Supported text is scanned for people, companies, deal or project names, emails, phone numbers, and URLs.
- Entity IDs are stable hashes of normalized names.
- Exact email, exact normalized name, and exact alias matches are automatic matches.
- Close name variants are marked `Needs Review`, not silently merged.
- Sheet rows are generated with review statuses and evidence text.

## What Is AI Assisted

AI should be used after deterministic extraction to:

- Summarize source documents.
- Infer relationship context from surrounding text.
- Research public credibility signals.
- Draft vetting notes and open questions.
- Suggest who should talk to whom.

AI outputs should write to review-oriented tabs first, especially `Research Queue`, `Vetting Research`, `Evidence Sources`, `Intro Recommendations`, and `Human Review`.

## Approval Gates

The system should require human approval before:

- Moving or renaming Drive files or folders.
- Merging uncertain identity matches.
- Treating public web research as verified.
- Using serious risk flags in outreach decisions.
- Finalizing credibility scores that rely on conflicting evidence.

## Next Connector Step

The Drive text adapter now accepts readable text for supported Drive file records, passes it through the deterministic extractor, and builds row bundles for `People`, `Companies`, `Deals & Projects`, `Evidence Sources`, and `Research Queue`.

The parser run planner now adds a dry-run boundary around that flow. It can skip unsupported inventory rows, record fetch errors without stopping the whole run, collect rows by destination tab, and build Sheets `appendCells` requests once live sheet metadata has provided the target `sheetId` values.

The next live connector step is to fetch readable text from Google Docs, PDFs, Word documents, and plain-text files, match candidates against existing Sheet rows, and append only new or review-needed candidates.
