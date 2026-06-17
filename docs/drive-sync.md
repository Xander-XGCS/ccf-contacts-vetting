# Drive Sync Workflow

The configured root folder is the complete operating universe. The system should crawl everything below it and classify content by evidence, not by a fixed folder layout.

## Root Folder

Store the root folder ID in local configuration:

```text
GOOGLE_DRIVE_ROOT_FOLDER_ID=<folder-id>
```

Do not commit the real folder ID or any generated manifest containing private file names to the public repository.

## Sync Modes

- `Manual`: run only when a person asks.
- `Prompted`: run when the user says things like "scan now", "update the sheet", or "refresh changed files".
- `Scheduled`: run on a recurring cadence after the workflow is trusted.
- `Full Rebuild`: ignore prior parse status and rebuild indexes from the current Drive tree.

## Incremental Algorithm

1. Recursively list all files, folders, and shortcuts below the root folder.
2. Write a Drive manifest keyed by `Drive File ID`.
3. Compare the current manifest to the previous manifest.
4. Mark items as new, modified, removed, or moved/renamed.
5. Parse only new and modified files unless the run is a full rebuild.
6. Update `File Inventory` and `Updates`.
7. Queue entity extraction and research from changed files.

## File Structure Suggestions

The AI can propose structure edits, but it cannot apply them directly.

Suggestions belong in the `Suggested Folder Changes` tab with:

- Target file ID
- Current path
- Proposed path or proposed name
- Reason
- Confidence
- Status
- Approval fields

Allowed statuses:

- `Proposed`
- `Approved`
- `Rejected`
- `Applied`
- `Superseded`

Only `Approved` rows can be applied by a future Drive update command.

## First Suggestions To Support

- Trim leading or trailing whitespace from folder names.
- Review duplicate folder names under the same parent.
- Move loose root-level files into `_Unsorted Intake`.
- Create missing `_Research Memos` folders for active people or companies.
- Split folders that mix unrelated people, companies, or deals.

## Safety Rules

- Never move, rename, delete, or merge a Drive item without explicit approval.
- Preserve original source documents.
- Prefer adding research memos and metadata over modifying originals.
- Log every applied file operation with the old path, new path, approver, and timestamp.
