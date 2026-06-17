# Crawler

The crawler walks the configured Google Drive root folder recursively and produces manifest rows for the `File Inventory` tab.

## Design

- Use stable Google Drive file IDs as primary keys.
- Treat folder paths and names as mutable metadata.
- Walk folders breadth-first for predictable progress.
- Record files, folders, and shortcuts.
- Do not follow shortcuts automatically.
- Stop safely at configured depth and item limits.
- Return crawl errors as data instead of crashing the whole run.

## Current Implementation

The first implementation lives in `src/ccf_contact_vetting/drive_crawler.py`.

It is connector-agnostic. Any Drive adapter only needs to implement:

```python
def list_folder(folder_id: str) -> list[DriveListItem]:
    ...
```

That keeps the crawler testable without live Drive access and lets the runtime-specific Google Drive connector be added as a thin adapter.

## Next Adapter Step

The Google Drive connector adapter maps folder-listing results into `DriveListItem` objects, then writes:

- `File Inventory`
- `Updates`
- `Suggested Folder Changes`

The adapter should keep generated manifests and private file names out of GitHub.

The current adapter helpers live in `src/ccf_contact_vetting/google_drive_connector.py`. They normalize connector file dictionaries and provide row builders for the live Google Sheet tabs.

Structure suggestions can exclude known system artifacts, such as the relationship-intelligence workbook itself, so the crawler does not propose moving its own control spreadsheet into intake. Production Sheet writes should use the row builders with structured cell updates. Plain paste-style smoke writes are useful for proving the connector path, but Google Sheets may trim trailing whitespace in displayed cell values.
