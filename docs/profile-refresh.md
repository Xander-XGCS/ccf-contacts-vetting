# Profile Refresh Workflow

Profile summaries are generated artifacts. They should stay synchronized with the evidence in each entity folder instead of becoming static one-off memos.

## Refresh Triggers

Refresh an entity profile when any of these occur:

- A new file is added to the entity folder.
- An existing file changes.
- OCR produces new text for a previously empty scan.
- Public vetting research adds a new reliable source.
- The spreadsheet row for the entity changes materially, such as score, status, related people, or open questions.

## Update Behavior

For each affected person or company:

1. Rebuild the source bundle from:
   - entity folder files
   - parsed email context
   - related deal documents
   - public research evidence
   - current Sheet rows
2. Regenerate the profile sections:
   - snapshot
   - overall summary
   - involved deals
   - related people and companies
   - verified facts
   - unresolved questions
   - recommended next action
   - linked sources
3. Update the existing profile Google Doc when one exists.
4. Create a profile only when no existing profile is linked.
5. Update `People` or `Companies` with the profile link and `Last Researched At`.
6. Add or update the profile source row in `Evidence Sources`.

## Staleness Rules

If new evidence is found but the profile cannot be regenerated in the same run, mark the profile as stale:

- `Research Queue.Status`: `Queued` or `Review`
- `People/Companies.Next Action`: `Refresh profile from new evidence.`
- `Human Review Notes`: include the file ID or source that made the profile stale.

## Human Review

Profile refreshes may update summaries and citations automatically, but they should not silently clear risk. Any lower risk score, improved grade, or stronger claim of authority requires human review when the entity is tied to high-risk categories such as gold, SCOs, bank instruments, seller mandates, or identity documents.
