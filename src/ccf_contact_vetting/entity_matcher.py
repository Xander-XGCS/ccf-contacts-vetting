from __future__ import annotations

from dataclasses import dataclass

from .entity_extraction import ExtractedEntity, normalize_name


@dataclass(frozen=True)
class EntityRecord:
    entity_id: str
    entity_type: str
    name: str
    aliases: tuple[str, ...] = ()
    email: str = ""


@dataclass(frozen=True)
class MatchDecision:
    candidate_id: str
    candidate_name: str
    entity_type: str
    match_status: str
    matched_entity_id: str = ""
    confidence: str = "Needs Review"
    reason: str = ""


def match_entity(candidate: ExtractedEntity, existing_records: list[EntityRecord], email: str = "") -> MatchDecision:
    same_type_records = [record for record in existing_records if record.entity_type == candidate.entity_type]
    email_key = email.casefold().strip()
    if email_key:
        for record in same_type_records:
            if record.email and record.email.casefold().strip() == email_key:
                return _decision(candidate, "Matched", record.entity_id, "High", "Exact email match.")

    candidate_key = normalize_name(candidate.name)
    for record in same_type_records:
        names = (record.name, *record.aliases)
        if candidate_key in {normalize_name(name) for name in names}:
            return _decision(candidate, "Matched", record.entity_id, "High", "Exact normalized name or alias match.")

    possible = _best_token_overlap(candidate_key, same_type_records)
    if possible is not None:
        record, score = possible
        return _decision(
            candidate,
            "Needs Review",
            record.entity_id,
            "Medium",
            f"Possible fuzzy name match by token overlap ({score:.2f}).",
        )

    return _decision(candidate, "New Candidate", "", candidate.confidence, "No deterministic match found.")


def match_entities(candidates: list[ExtractedEntity], existing_records: list[EntityRecord]) -> list[MatchDecision]:
    return [match_entity(candidate, existing_records) for candidate in candidates]


def _best_token_overlap(candidate_key: str, records: list[EntityRecord]) -> tuple[EntityRecord, float] | None:
    candidate_tokens = set(candidate_key.split())
    if not candidate_tokens:
        return None

    best: tuple[EntityRecord, float] | None = None
    for record in records:
        for name in (record.name, *record.aliases):
            record_tokens = set(normalize_name(name).split())
            if not record_tokens:
                continue
            score = len(candidate_tokens & record_tokens) / len(candidate_tokens | record_tokens)
            if score >= 0.66 and (best is None or score > best[1]):
                best = record, score
    return best


def _decision(
    candidate: ExtractedEntity,
    status: str,
    matched_entity_id: str,
    confidence: str,
    reason: str,
) -> MatchDecision:
    return MatchDecision(
        candidate_id=candidate.entity_id,
        candidate_name=candidate.name,
        entity_type=candidate.entity_type,
        match_status=status,
        matched_entity_id=matched_entity_id,
        confidence=confidence,
        reason=reason,
    )
