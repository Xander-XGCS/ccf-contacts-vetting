# Spreadsheet-Triggered Research

The live Google Sheet can trigger agentic research through a small bound Apps Script menu. The script does not run the crawler itself. It sends a structured request to a private webhook, and the backend worker performs the Drive crawl, public research, memo filing, and Sheet updates.

## User Flow

1. Open the live CCF Relationship Intelligence Sheet.
2. Use `CCF Research > Request research for selected row` on a `Research Queue`, `People`, `Companies`, or `Vetting Research` row.
3. Or use `CCF Research > Request queued research` to send all `Queued` / `Requested` queue rows.
4. The worker updates `Updates`, `Research Queue`, `Vetting Research`, `Evidence Sources`, and profile memo links as it runs.

## Apps Script Setup

1. Open the Sheet, then go to `Extensions > Apps Script`.
2. Paste `apps-script/research-trigger.gs` into the bound Apps Script project.
3. Set Script Properties:
   - `CCF_RESEARCH_WEBHOOK_URL`: private HTTPS endpoint for the research worker.
   - `CCF_RESEARCH_WEBHOOK_SECRET`: bearer token expected by the worker.
4. Reload the spreadsheet and use the `CCF Research` menu.

## Backend Contract

The webhook receives JSON shaped like:

```json
{
  "trigger": "selected_row",
  "rows": [
    {
      "spreadsheetId": "sheet-id",
      "sheetName": "Research Queue",
      "rowNumber": 8,
      "data": {
        "Entity Type": "Person",
        "Entity Name": "Example Person",
        "Research Goal": "Verify identity and credibility."
      },
      "requestedAt": "2026-06-17T17:54:26.000Z",
      "requestedBy": "user@example.com"
    }
  ]
}
```

The backend should authenticate the bearer token, create an `Updates` row, process only approved scopes, write profile memos to Drive, and write result links back to the Sheet.

## Safety Rules

- Keep webhook URLs and secrets out of GitHub.
- Treat spreadsheet requests as job requests, not permission to move or rename Drive files.
- Use the `Suggested Folder Changes` approval flow for any structure edits.
- Preserve source documents; add memos and metadata instead of modifying originals.
- Record every run in `Updates`.
