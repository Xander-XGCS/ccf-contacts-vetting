from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Protocol

from .drive_manifest import FOLDER_MIME_TYPE, DriveItemRecord, item_type_for_mime


@dataclass(frozen=True)
class DriveListItem:
    file_id: str
    name: str
    mime_type: str
    url: str
    created_at: str = ""
    modified_at: str = ""
    parent_folder_id: str = ""


@dataclass(frozen=True)
class CrawlError:
    folder_id: str
    path: str
    message: str


@dataclass(frozen=True)
class CrawlResult:
    items: tuple[DriveItemRecord, ...]
    errors: tuple[CrawlError, ...] = field(default_factory=tuple)

    @property
    def file_count(self) -> int:
        return sum(1 for item in self.items if item.item_type == "File")

    @property
    def folder_count(self) -> int:
        return sum(1 for item in self.items if item.item_type == "Folder")

    @property
    def shortcut_count(self) -> int:
        return sum(1 for item in self.items if item.item_type == "Shortcut")


class DriveFolderLister(Protocol):
    def list_folder(self, folder_id: str) -> list[DriveListItem]:
        """Return direct children for a Drive folder ID."""


def folder_url(folder_id: str) -> str:
    return f"https://drive.google.com/drive/folders/{folder_id}"


def crawl_drive_tree(
    root_folder_id: str,
    lister: DriveFolderLister,
    *,
    root_name: str = "Complete Capital Funding",
    max_depth: int = 25,
    max_items: int = 25_000,
) -> CrawlResult:
    if max_depth < 0:
        raise ValueError("max_depth must be zero or greater")
    if max_items < 1:
        raise ValueError("max_items must be at least one")

    root = DriveItemRecord(
        file_id=root_folder_id,
        name=root_name,
        mime_type=FOLDER_MIME_TYPE,
        item_type="Folder",
        current_path=root_name,
        parent_folder_id="",
        drive_url=folder_url(root_folder_id),
    )
    records: list[DriveItemRecord] = [root]
    errors: list[CrawlError] = []
    queue: deque[tuple[str, str, int]] = deque([(root_folder_id, root_name, 0)])
    visited_folders: set[str] = set()

    while queue:
        folder_id, folder_path, depth = queue.popleft()
        if folder_id in visited_folders:
            continue
        visited_folders.add(folder_id)

        if depth >= max_depth:
            errors.append(CrawlError(folder_id=folder_id, path=folder_path, message="Maximum crawl depth reached."))
            continue

        try:
            children = lister.list_folder(folder_id)
        except Exception as exc:  # pragma: no cover - exact connector exceptions vary.
            errors.append(CrawlError(folder_id=folder_id, path=folder_path, message=str(exc)))
            continue

        for child in sorted(children, key=_sort_key):
            if len(records) >= max_items:
                errors.append(CrawlError(folder_id=folder_id, path=folder_path, message="Maximum item limit reached."))
                return CrawlResult(items=tuple(records), errors=tuple(errors))

            child_path = f"{folder_path}/{child.name}"
            record = DriveItemRecord(
                file_id=child.file_id,
                name=child.name,
                mime_type=child.mime_type,
                item_type=item_type_for_mime(child.mime_type),
                current_path=child_path,
                parent_folder_id=child.parent_folder_id or folder_id,
                drive_url=child.url,
                created_at=child.created_at,
                modified_at=child.modified_at,
            )
            records.append(record)

            if child.mime_type == FOLDER_MIME_TYPE:
                queue.append((child.file_id, child_path, depth + 1))

    return CrawlResult(items=tuple(records), errors=tuple(errors))


def _sort_key(item: DriveListItem) -> tuple[int, str, str]:
    item_rank = 0 if item.mime_type == FOLDER_MIME_TYPE else 1
    return item_rank, item.name.casefold(), item.file_id

