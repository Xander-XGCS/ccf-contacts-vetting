from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


SKIP_DIR_NAMES = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
    ".venv",
    "venv",
    "env",
}


@dataclass(frozen=True)
class FileRecord:
    path: str
    name: str
    extension: str
    size_bytes: int
    modified_at: str
    depth: int


def inventory_path(root: Path) -> list[FileRecord]:
    root = root.expanduser().resolve()
    if not root.exists():
        raise FileNotFoundError(f"Folder does not exist: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Path is not a folder: {root}")

    records: list[FileRecord] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or _has_skipped_parent(path, root):
            continue

        stat = path.stat()
        modified = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()
        relative = path.relative_to(root)
        records.append(
            FileRecord(
                path=str(relative),
                name=path.name,
                extension=path.suffix.lower().lstrip("."),
                size_bytes=stat.st_size,
                modified_at=modified,
                depth=len(relative.parts) - 1,
            )
        )
    return records


def write_inventory_csv(records: list[FileRecord], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(FileRecord.__dataclass_fields__.keys()))
        writer.writeheader()
        for record in records:
            writer.writerow(asdict(record))


def _has_skipped_parent(path: Path, root: Path) -> bool:
    try:
        relative = path.relative_to(root)
    except ValueError:
        return True
    return any(part in SKIP_DIR_NAMES for part in relative.parts)

