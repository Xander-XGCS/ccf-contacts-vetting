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

The next integration step is to fetch readable text from supported Drive file types, pass that text through the deterministic extractor, match candidates against existing Sheet rows, and append new candidates to the review tabs.
