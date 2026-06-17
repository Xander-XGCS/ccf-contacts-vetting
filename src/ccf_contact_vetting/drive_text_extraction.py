from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .drive_manifest import DriveItemRecord
from .entity_extraction import (
    ExtractionResult,
    TextSource,
    company_sheet_row,
    deal_sheet_row,
    evidence_source_row,
    extract_text_entities,
    person_sheet_row,
    research_queue_row,
)
from .ocr import SUPPORTED_OCR_MIME_TYPES


GOOGLE_DOC_MIME_TYPE = "application/vnd.google-apps.document"

SUPPORTED_TEXT_MIME_TYPES = {
    GOOGLE_DOC_MIME_TYPE,
    "application/pdf",
    "application/rtf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
    "text/csv",
    "text/html",
    "text/markdown",
    "text/plain",
}


@dataclass(frozen=True)
class DriveTextDocument:
    file_id: str
    title: str
    text: str
    url: str = ""
    path: str = ""
    mime_type: str = ""


@dataclass(frozen=True)
class ExtractedSheetRows:
    people: tuple[list[str], ...]
    companies: tuple[list[str], ...]
    deals: tuple[list[str], ...]
    evidence_sources: tuple[list[str], ...]
    research_queue: tuple[list[str], ...]

    @property
    def row_count(self) -> int:
        return (
            len(self.people)
            + len(self.companies)
            + len(self.deals)
            + len(self.evidence_sources)
            + len(self.research_queue)
        )


def is_supported_text_record(record: DriveItemRecord) -> bool:
    return record.item_type == "File" and record.mime_type in SUPPORTED_TEXT_MIME_TYPES


def is_supported_ocr_record(record: DriveItemRecord) -> bool:
    return record.item_type == "File" and record.mime_type in SUPPORTED_OCR_MIME_TYPES


def drive_record_to_text_source(record: DriveItemRecord) -> TextSource:
    title = record.current_path or record.name
    return TextSource(source_id=record.file_id, title=title, url=record.drive_url)


def extract_drive_document(document: DriveTextDocument) -> ExtractionResult:
    source = TextSource(
        source_id=document.file_id,
        title=document.path or document.title,
        url=document.url,
    )
    return extract_text_entities(document.text, source)


def extract_drive_record_text(record: DriveItemRecord, text: str) -> ExtractionResult:
    return extract_text_entities(text, drive_record_to_text_source(record))


def extracted_sheet_rows(result: ExtractionResult) -> ExtractedSheetRows:
    research_entities = (*result.people, *result.companies)
    return ExtractedSheetRows(
        people=tuple(person_sheet_row(entity) for entity in result.people),
        companies=tuple(company_sheet_row(entity) for entity in result.companies),
        deals=tuple(deal_sheet_row(entity) for entity in result.deals),
        evidence_sources=(
            evidence_source_row(result.source, extracted_facts_summary(result)),
        ),
        research_queue=tuple(research_queue_row(entity) for entity in research_entities),
    )


def extracted_facts_summary(result: ExtractionResult) -> str:
    facts: list[str] = []
    if result.people:
        facts.append(f"People: {_join_names(entity.name for entity in result.people)}")
    if result.companies:
        facts.append(f"Companies: {_join_names(entity.name for entity in result.companies)}")
    if result.deals:
        facts.append(f"Deals/Projects: {_join_names(entity.name for entity in result.deals)}")
    if result.contact_points:
        facts.append(f"Contact points: {len(result.contact_points)}")
    return "; ".join(facts)


def _join_names(names: Iterable[str]) -> str:
    return ", ".join(str(name) for name in names)
