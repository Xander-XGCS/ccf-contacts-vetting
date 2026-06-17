from __future__ import annotations

import csv
import hashlib
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from urllib.parse import urlparse


FOLDER_MIME_TYPE = "application/vnd.google-apps.folder"
SHORTCUT_MIME_TYPE = "application/vnd.google-apps.shortcut"

DRIVE_ID_RE = re.compile(r"^[A-Za-z0-9_-]{10,}$")
FOLDER_URL_RE = re.compile(r"/folders/([A-Za-z0-9_-]+)")
FILE_URL_RE = re.compile(r"/(?:file|document|spreadsheets|presentation)/d/([A-Za-z0-9_-]+)")
OPEN_URL_RE = re.compile(r"[?&]id=([A-Za-z0-9_-]+)")


@dataclass(frozen=True)
class DriveItemRecord:
    file_id: str
    name: str
    mime_type: str
    item_type: str
    current_path: str
    parent_folder_id: str
    drive_url: str
    created_at: str = ""
    modified_at: str = ""
    last_seen_at: str = ""
    content_fingerprint: str = ""


@dataclass(frozen=True)
class ManifestChange:
    change_id: str
    change_type: str
    file_id: str
    name: str
    previous_path: str
    current_path: str
    reason: str


@dataclass(frozen=True)
class StructureSuggestion:
    suggestion_id: str
    suggestion_type: str
    target_file_id: str
    target_name: str
    current_path: str
    proposed_path: str
    proposed_name: str
    reason: str
    confidence: str
    status: str = "Proposed"
    requires_approval: bool = True


def extract_drive_id(value: str) -> str:
    candidate = value.strip()
    if DRIVE_ID_RE.fullmatch(candidate):
        return candidate

    parsed = urlparse(candidate)
    searchable = parsed.path + ("?" + parsed.query if parsed.query else "")
    for pattern in (FOLDER_URL_RE, FILE_URL_RE, OPEN_URL_RE):
        match = pattern.search(searchable)
        if match:
            return match.group(1)

    raise ValueError(f"Could not extract a Google Drive ID from: {value}")


def item_type_for_mime(mime_type: str) -> str:
    if mime_type == FOLDER_MIME_TYPE:
        return "Folder"
    if mime_type == SHORTCUT_MIME_TYPE:
        return "Shortcut"
    if mime_type:
        return "File"
    return "Unknown"


def load_manifest(path: Path) -> list[DriveItemRecord]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    items = payload["items"] if isinstance(payload, dict) and "items" in payload else payload
    return [DriveItemRecord(**item) for item in items]


def write_changes_csv(changes: list[ManifestChange], output_path: Path) -> None:
    _write_dataclass_csv(changes, output_path, ManifestChange)


def write_suggestions_csv(suggestions: list[StructureSuggestion], output_path: Path) -> None:
    _write_dataclass_csv(suggestions, output_path, StructureSuggestion)


def diff_manifests(previous: list[DriveItemRecord], current: list[DriveItemRecord]) -> list[ManifestChange]:
    previous_by_id = {item.file_id: item for item in previous}
    current_by_id = {item.file_id: item for item in current}
    changes: list[ManifestChange] = []

    for file_id, item in sorted(current_by_id.items()):
        prior = previous_by_id.get(file_id)
        if prior is None:
            changes.append(_change("Added", item, "", item.current_path, "Item was not present in the previous manifest."))
            continue
        if _location_signature(prior) != _location_signature(item):
            changes.append(
                _change(
                    "Moved Or Renamed",
                    item,
                    prior.current_path,
                    item.current_path,
                    "Item name, path, or parent folder changed.",
                )
            )
            continue
        if _content_signature(prior) != _content_signature(item):
            changes.append(
                _change("Modified", item, prior.current_path, item.current_path, "Item metadata or content fingerprint changed.")
            )

    for file_id, item in sorted(previous_by_id.items()):
        if file_id not in current_by_id:
            changes.append(_change("Removed", item, item.current_path, "", "Item was present before and was not seen in the current manifest."))

    return changes


def propose_structure_suggestions(
    items: list[DriveItemRecord],
    root_folder_id: str,
    *,
    excluded_file_ids: set[str] | None = None,
) -> list[StructureSuggestion]:
    excluded_file_ids = excluded_file_ids or set()
    suggestions: list[StructureSuggestion] = []
    suggestions.extend(_suggest_trimmed_folder_names(items))
    suggestions.extend(_suggest_duplicate_folder_review(items))
    suggestions.extend(_suggest_root_file_intake(items, root_folder_id, excluded_file_ids))
    return sorted(suggestions, key=lambda suggestion: (suggestion.suggestion_type, suggestion.current_path, suggestion.target_file_id))


def write_json_dataclasses(records: list[object], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = [asdict(record) for record in records]
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _suggest_trimmed_folder_names(items: list[DriveItemRecord]) -> list[StructureSuggestion]:
    suggestions: list[StructureSuggestion] = []
    for item in items:
        if item.item_type != "Folder":
            continue
        trimmed = item.name.strip()
        if trimmed and trimmed != item.name:
            suggestions.append(
                _suggestion(
                    "Rename Folder",
                    item,
                    proposed_name=trimmed,
                    reason="Folder name has leading or trailing whitespace.",
                    confidence="High",
                )
            )
    return suggestions


def _suggest_duplicate_folder_review(items: list[DriveItemRecord]) -> list[StructureSuggestion]:
    folders_by_parent_and_name: dict[tuple[str, str], list[DriveItemRecord]] = {}
    for item in items:
        if item.item_type != "Folder":
            continue
        key = (item.parent_folder_id, _normalize_name(item.name))
        folders_by_parent_and_name.setdefault(key, []).append(item)

    suggestions: list[StructureSuggestion] = []
    for duplicates in folders_by_parent_and_name.values():
        if len(duplicates) < 2:
            continue
        for item in duplicates:
            suggestions.append(
                _suggestion(
                    "Review Duplicate Folder Name",
                    item,
                    reason="Multiple folders under the same parent normalize to the same name.",
                    confidence="Medium",
                )
            )
    return suggestions


def _suggest_root_file_intake(
    items: list[DriveItemRecord],
    root_folder_id: str,
    excluded_file_ids: set[str],
) -> list[StructureSuggestion]:
    suggestions: list[StructureSuggestion] = []
    for item in items:
        if item.file_id in excluded_file_ids:
            continue
        if item.parent_folder_id != root_folder_id or item.item_type not in {"File", "Shortcut"}:
            continue
        suggestions.append(
            _suggestion(
                "Move Root File To Intake",
                item,
                proposed_path=f"_Unsorted Intake/{item.name}",
                reason="Loose root-level files should be reviewed and classified before parsing.",
                confidence="Medium",
            )
        )
    return suggestions


def _normalize_name(name: str) -> str:
    return " ".join(name.strip().casefold().split())


def _location_signature(item: DriveItemRecord) -> tuple[str, str, str]:
    return item.name, item.parent_folder_id, item.current_path


def _content_signature(item: DriveItemRecord) -> tuple[str, str, str]:
    return item.mime_type, item.modified_at, item.content_fingerprint


def _change(change_type: str, item: DriveItemRecord, previous_path: str, current_path: str, reason: str) -> ManifestChange:
    seed = "|".join((change_type, item.file_id, previous_path, current_path, item.modified_at))
    return ManifestChange(
        change_id=_stable_id("chg", seed),
        change_type=change_type,
        file_id=item.file_id,
        name=item.name,
        previous_path=previous_path,
        current_path=current_path,
        reason=reason,
    )


def _suggestion(
    suggestion_type: str,
    item: DriveItemRecord,
    reason: str,
    confidence: str,
    proposed_path: str = "",
    proposed_name: str = "",
) -> StructureSuggestion:
    seed = "|".join((suggestion_type, item.file_id, item.current_path, proposed_path, proposed_name))
    return StructureSuggestion(
        suggestion_id=_stable_id("sg", seed),
        suggestion_type=suggestion_type,
        target_file_id=item.file_id,
        target_name=item.name,
        current_path=item.current_path,
        proposed_path=proposed_path,
        proposed_name=proposed_name,
        reason=reason,
        confidence=confidence,
    )


def _stable_id(prefix: str, seed: str) -> str:
    digest = hashlib.sha1(seed.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}_{digest}"


def _write_dataclass_csv(records: list[object], output_path: Path, record_type: type) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(record_type.__dataclass_fields__.keys())
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow(asdict(record))
