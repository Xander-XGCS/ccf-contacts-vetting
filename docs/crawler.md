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

The next step is a Google Drive connector adapter that maps folder-listing results into `DriveListItem` objects, then writes:

- `File Inventory`
- `Updates`
- `Suggested Folder Changes`

The adapter should keep generated manifests and private file names out of GitHub.

