from __future__ import annotations

import hashlib
from dataclasses import dataclass


@dataclass(frozen=True)
class VettingRecord:
    entity_type: str
    entity_id: str
    entity_name: str
    research_status: str
    credibility_score: int | None
    credibility_grade: str
    score_confidence: str
    identity_confidence: str
    source_quality: str
    professional_track_record: str
    deal_relevance: str
    risk_flag_severity: str
    positive_signals: str
    red_flags: str
    open_questions: str
    evidence_links: str
    last_researched_at: str
    reviewer: str = ""
    human_review_required: bool = True
    notes: str = ""

    @property
    def vetting_id(self) -> str:
        return stable_vetting_id(self.entity_type, self.entity_id)


def stable_vetting_id(entity_type: str, entity_id: str) -> str:
    seed = f"{entity_type}|{entity_id}".casefold()
    digest = hashlib.sha1(seed.encode("utf-8")).hexdigest()[:12]
    return f"vet_{digest}"


def credibility_grade(score: int | None, *, needs_review: bool = False) -> str:
    if score is None or needs_review:
        return "Needs Review"
    if score >= 85:
        return "A"
    if score >= 70:
        return "B"
    if score >= 50:
        return "C"
    return "D"


def vetting_sheet_row(record: VettingRecord) -> list[object]:
    return [
        record.vetting_id,
        record.entity_type,
        record.entity_id,
        record.entity_name,
        record.research_status,
        "" if record.credibility_score is None else record.credibility_score,
        record.credibility_grade,
        record.score_confidence,
        record.identity_confidence,
        record.source_quality,
        record.professional_track_record,
        record.deal_relevance,
        record.risk_flag_severity,
        record.positive_signals,
        record.red_flags,
        record.open_questions,
        record.evidence_links,
        record.last_researched_at,
        record.reviewer,
        record.human_review_required,
        record.notes,
    ]


def human_review_row(
    *,
    item_type: str,
    item_id: str,
    notes: str,
    reviewed_at: str = "",
    decision: str = "Needs Follow Up",
    reviewer: str = "",
    follow_up_required: bool = True,
) -> list[object]:
    review_id = _stable_review_id(item_type, item_id, notes)
    return [
        review_id,
        item_type,
        item_id,
        reviewer,
        decision,
        notes,
        reviewed_at,
        follow_up_required,
    ]


def _stable_review_id(item_type: str, item_id: str, notes: str) -> str:
    seed = f"{item_type}|{item_id}|{notes}".casefold()
    digest = hashlib.sha1(seed.encode("utf-8")).hexdigest()[:12]
    return f"review_{digest}"
