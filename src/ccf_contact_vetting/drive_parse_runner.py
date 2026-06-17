from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

from .drive_manifest import DriveItemRecord
from .drive_text_extraction import (
    ExtractedSheetRows,
    extracted_sheet_rows,
    extract_drive_record_text,
    is_supported_ocr_record,
    is_supported_text_record,
)
from .sheet_append import collect_rows_by_tab


class DriveTextFetcher(Protocol):
    def fetch_text(self, record: DriveItemRecord) -> str:
        """Return readable text for a Drive file record."""


@runtime_checkable
class DriveOcrFetcher(Protocol):
    def fetch_ocr_text(self, record: DriveItemRecord) -> str:
        """Return OCR text for a Drive file record."""


@dataclass(frozen=True)
class ParseError:
    file_id: str
    name: str
    path: str
    message: str


@dataclass(frozen=True)
class ParsedDriveFile:
    file_id: str
    name: str
    path: str
    entity_count: int
    row_count: int
    text_source: str = "native"


@dataclass(frozen=True)
class ParseRunResult:
    parsed_files: tuple[ParsedDriveFile, ...]
    skipped_file_ids: tuple[str, ...]
    errors: tuple[ParseError, ...] = field(default_factory=tuple)
    row_bundles: tuple[ExtractedSheetRows, ...] = field(default_factory=tuple)

    @property
    def parsed_count(self) -> int:
        return len(self.parsed_files)

    @property
    def skipped_count(self) -> int:
        return len(self.skipped_file_ids)

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def rows_by_tab(self) -> dict[str, list[list[str]]]:
        return collect_rows_by_tab(list(self.row_bundles))


def parse_drive_records(
    records: list[DriveItemRecord],
    fetcher: DriveTextFetcher,
    *,
    limit: int | None = None,
) -> ParseRunResult:
    parsed: list[ParsedDriveFile] = []
    skipped: list[str] = []
    errors: list[ParseError] = []
    bundles: list[ExtractedSheetRows] = []

    ocr_enabled = isinstance(fetcher, DriveOcrFetcher)
    candidates = [
        record
        for record in records
        if is_supported_text_record(record) or (ocr_enabled and is_supported_ocr_record(record))
    ]
    if limit is not None:
        candidates = candidates[:limit]

    candidate_ids = {record.file_id for record in candidates}
    skipped.extend(record.file_id for record in records if record.file_id not in candidate_ids)

    for record in candidates:
        try:
            if is_supported_text_record(record):
                text = fetcher.fetch_text(record)
                text_source = "native"
            else:
                text = ""
                text_source = "ocr"
        except Exception as exc:  # pragma: no cover - exact connector exceptions vary.
            errors.append(ParseError(record.file_id, record.name, record.current_path, str(exc)))
            continue

        if not text.strip() and ocr_enabled and is_supported_ocr_record(record):
            try:
                text = fetcher.fetch_ocr_text(record)
                text_source = "ocr"
            except Exception as exc:  # pragma: no cover - exact OCR exceptions vary.
                errors.append(ParseError(record.file_id, record.name, record.current_path, f"OCR failed: {exc}"))
                continue

        if not text.strip():
            skipped.append(record.file_id)
            continue

        result = extract_drive_record_text(record, text)
        rows = extracted_sheet_rows(result)
        bundles.append(rows)
        parsed.append(
            ParsedDriveFile(
                file_id=record.file_id,
                name=record.name,
                path=record.current_path,
                entity_count=result.entity_count,
                row_count=rows.row_count,
                text_source=text_source,
            )
        )

    return ParseRunResult(
        parsed_files=tuple(parsed),
        skipped_file_ids=tuple(skipped),
        errors=tuple(errors),
        row_bundles=tuple(bundles),
    )
