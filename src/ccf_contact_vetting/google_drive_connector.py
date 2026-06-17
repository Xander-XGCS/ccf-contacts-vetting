from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any

from .drive_crawler import DriveListItem
from .drive_manifest import DriveItemRecord, StructureSuggestion


def connector_file_to_drive_item(file_payload: dict[str, Any], fallback_parent_id: str = "") -> DriveListItem:
    return DriveListItem(
        file_id=str(file_payload.get("id") or ""),
        name=str(file_payload.get("title") or file_payload.get("name") or ""),
        mime_type=str(file_payload.get("mime_type") or file_payload.get("mimeType") or ""),
        url=str(file_payload.get("url") or file_payload.get("webViewLink") or ""),
        created_at=str(file_payload.get("created_time") or file_payload.get("createdTime") or ""),
        modified_at=str(file_payload.get("modified_time") or file_payload.get("modifiedTime") or ""),
        parent_folder_id=_first_parent_id(file_payload) or fallback_parent_id,
    )


def connector_listing_to_drive_items(listing_payload: dict[str, Any], fallback_parent_id: str = "") -> list[DriveListItem]:
    files = listing_payload.get("files", [])
    if not isinstance(files, list):
        raise ValueError("Connector listing payload must contain a list under 'files'.")
    return [connector_file_to_drive_item(file_payload, fallback_parent_id=fallback_parent_id) for file_payload in files]


def file_inventory_row(record: DriveItemRecord) -> list[Any]:
    return [
        record.file_id,
        record.name,
        record.mime_type,
        record.item_type,
        record.current_path,
        record.parent_folder_id,
        record.drive_url,
        record.created_at,
        record.modified_at,
        record.last_seen_at,
        "Not Parsed",
        "",
        record.content_fingerprint,
        "",
    ]


def structure_suggestion_row(suggestion: StructureSuggestion) -> list[Any]:
    return [
        suggestion.suggestion_id,
        suggestion.suggestion_type,
        suggestion.target_file_id,
        suggestion.target_name,
        suggestion.current_path,
        suggestion.proposed_path,
        suggestion.proposed_name,
        suggestion.reason,
        suggestion.confidence,
        suggestion.status,
        "",
        "",
        "",
        "",
    ]


def update_run_row(
    *,
    run_id: str,
    trigger: str,
    root_folder_id: str,
    started_at: str,
    completed_at: str,
    status: str,
    items_scanned: int,
    new_items: int,
    modified_items: int,
    removed_items: int,
    moved_or_renamed_items: int,
    error_count: int,
    notes: str = "",
) -> list[Any]:
    return [
        run_id,
        trigger,
        root_folder_id,
        started_at,
        completed_at,
        status,
        items_scanned,
        new_items,
        modified_items,
        removed_items,
        moved_or_renamed_items,
        error_count,
        notes,
    ]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def as_plain_dicts(records: list[Any]) -> list[dict[str, Any]]:
    return [asdict(record) for record in records]


def _first_parent_id(file_payload: dict[str, Any]) -> str:
    parent_ids = file_payload.get("parent_ids") or file_payload.get("parents") or []
    if isinstance(parent_ids, list) and parent_ids:
        return str(parent_ids[0])
    if isinstance(parent_ids, str):
        return parent_ids
    return ""

