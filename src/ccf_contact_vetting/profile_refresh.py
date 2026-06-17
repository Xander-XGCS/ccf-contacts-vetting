from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ProfileEvidenceItem:
    file_id: str
    name: str
    modified_at: str = ""
    parsed_status: str = ""
    notes: str = ""


@dataclass(frozen=True)
class ProfileRefreshDecision:
    refresh_required: bool
    reasons: tuple[str, ...]


def profile_refresh_decision(
    *,
    profile_url: str,
    last_refreshed_at: str,
    evidence_items: list[ProfileEvidenceItem],
) -> ProfileRefreshDecision:
    reasons: list[str] = []
    last_refresh = _parse_datetime(last_refreshed_at)

    if not profile_url.strip():
        reasons.append("No profile document is linked.")
    if last_refresh is None:
        reasons.append("Profile refresh timestamp is missing or invalid.")

    for item in evidence_items:
        modified_at = _parse_datetime(item.modified_at)
        if last_refresh is not None and modified_at is not None and modified_at > last_refresh:
            reasons.append(f"Evidence file is newer than profile: {item.name} ({item.file_id}).")
        if item.parsed_status == "Needs Review":
            reasons.append(f"Evidence file needs review before profile can be current: {item.name} ({item.file_id}).")
        if "ocr" in item.notes.casefold() and item.parsed_status != "Parsed":
            reasons.append(f"OCR/manual review is unresolved for: {item.name} ({item.file_id}).")

    return ProfileRefreshDecision(refresh_required=bool(reasons), reasons=tuple(reasons))


def _parse_datetime(value: str) -> datetime | None:
    cleaned = value.strip()
    if not cleaned:
        return None
    if cleaned.endswith("Z"):
        cleaned = cleaned[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(cleaned)
    except ValueError:
        return None
