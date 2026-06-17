from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field


EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
PHONE_RE = re.compile(r"(?:\+?1[\s.-]?)?(?:\(?\d{3}\)?[\s.-]?)\d{3}[\s.-]?\d{4}\b")
URL_RE = re.compile(r"https?://[^\s<>)\"']+", re.IGNORECASE)

PERSON_RE = re.compile(
    r"\b(?:Dr\.|Mr\.|Ms\.|Mrs\.)?[ \t]*"
    r"([A-Z][a-z]+(?:[-'][A-Z][a-z]+)?(?:[ \t]+[A-Z][a-z]+(?:[-'][A-Z][a-z]+)?){1,3})\b"
)
COMPANY_RE = re.compile(
    r"\b([A-Z][A-Za-z0-9&.,' -]{1,90}?\s+"
    r"(?:LLC|L\.L\.C\.|Inc\.?|Incorporated|Corp\.?|Corporation|Ltd\.?|Limited|Holdings|Group|Capital|Funding|Partners|Ventures|Bank|Fund))\b"
)
DEAL_HINT_RE = re.compile(
    r"\b([A-Z][A-Za-z0-9&,' -]{2,80}?\s+"
    r"(?:Project|Deal|Transaction|Opportunity|Program|Dossier|Asset|Purchase|Offering))\b"
)

ORG_WORDS = {
    "capital",
    "company",
    "corp",
    "corporation",
    "fund",
    "funding",
    "global",
    "group",
    "holdings",
    "inc",
    "limited",
    "llc",
    "partners",
    "ventures",
}

PERSON_STOP_PHRASES = {
    "Business Capital",
    "Complete Capital",
    "Drive File",
    "Google Drive",
    "Human Review",
    "Private Placement",
    "Relationship Intelligence",
    "Source Documents",
}


@dataclass(frozen=True)
class TextSource:
    source_id: str
    title: str
    url: str = ""


@dataclass(frozen=True)
class ExtractedEntity:
    entity_type: str
    name: str
    entity_id: str
    confidence: str
    evidence_text: str
    source_id: str
    source_title: str
    source_url: str = ""


@dataclass(frozen=True)
class ExtractedContactPoint:
    contact_type: str
    value: str
    source_id: str
    source_title: str
    source_url: str = ""


@dataclass(frozen=True)
class ExtractionResult:
    source: TextSource
    people: tuple[ExtractedEntity, ...] = field(default_factory=tuple)
    companies: tuple[ExtractedEntity, ...] = field(default_factory=tuple)
    deals: tuple[ExtractedEntity, ...] = field(default_factory=tuple)
    contact_points: tuple[ExtractedContactPoint, ...] = field(default_factory=tuple)

    @property
    def entity_count(self) -> int:
        return len(self.people) + len(self.companies) + len(self.deals)


def extract_text_entities(text: str, source: TextSource) -> ExtractionResult:
    searchable = "\n".join(part for part in (source.title, text) if part)
    companies = _extract_companies(searchable, source)
    company_names = {entity.name for entity in companies}
    people = _extract_people(searchable, source, company_names)
    deals = _extract_deal_hints(searchable, source)
    contact_points = _extract_contact_points(searchable, source)
    return ExtractionResult(
        source=source,
        people=tuple(people),
        companies=tuple(companies),
        deals=tuple(deals),
        contact_points=tuple(contact_points),
    )


def person_sheet_row(entity: ExtractedEntity) -> list[str]:
    return [
        entity.entity_id,
        entity.name,
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        f"Mentioned in {entity.source_title}",
        "Not Started",
        "Needs Review",
        entity.confidence,
        "",
        "",
        "",
        "",
        entity.source_url,
        "",
        "Review extracted identity candidate.",
        entity.evidence_text,
    ]


def company_sheet_row(entity: ExtractedEntity) -> list[str]:
    return [
        entity.entity_id,
        entity.name,
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "Not Started",
        "Needs Review",
        entity.confidence,
        "",
        entity.source_url,
        "",
        "Review extracted company candidate.",
        entity.evidence_text,
    ]


def deal_sheet_row(entity: ExtractedEntity) -> list[str]:
    return [
        entity.entity_id,
        entity.name,
        "",
        "Needs Classification",
        "",
        "",
        "",
        "",
        "",
        "",
        entity.source_url,
        "Review extracted deal or project candidate.",
        "",
        "Review source evidence.",
        "",
        "",
    ]


def evidence_source_row(source: TextSource, extracted_facts: str = "") -> list[str]:
    return [
        stable_id("src", source.source_id),
        "Drive File",
        source.title,
        source.url,
        "",
        "",
        extracted_facts,
        "",
        "Medium",
        "Extracted by deterministic parser.",
    ]


def research_queue_row(entity: ExtractedEntity, priority: str = "Medium") -> list[str]:
    return [
        stable_id("rq", f"{entity.entity_type}|{entity.entity_id}"),
        entity.entity_type,
        entity.entity_id,
        entity.name,
        priority,
        "Verify identity, credibility, role, and deal relevance using public sources.",
        "Queued",
        "AI",
        entity.name,
        "",
        "",
        "",
        "",
        "TRUE",
    ]


def stable_entity_id(entity_type: str, name: str) -> str:
    prefix = {"Person": "person", "Company": "company", "Deal Project": "deal"}.get(entity_type, "entity")
    return stable_id(prefix, normalize_name(name))


def stable_id(prefix: str, seed: str) -> str:
    digest = hashlib.sha1(seed.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}_{digest}"


def normalize_name(name: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", " ", name.casefold()).strip()
    return " ".join(normalized.split())


def _extract_companies(text: str, source: TextSource) -> list[ExtractedEntity]:
    seen: set[str] = set()
    companies: list[ExtractedEntity] = []
    for match in COMPANY_RE.finditer(text):
        name = _trim_company_name(_clean_entity_name(match.group(1)))
        key = normalize_name(name)
        if not key or key in seen:
            continue
        seen.add(key)
        companies.append(_entity("Company", name, "Medium", match.group(0), source))
    return companies


def _extract_people(text: str, source: TextSource, company_names: set[str]) -> list[ExtractedEntity]:
    seen: set[str] = set()
    people: list[ExtractedEntity] = []
    company_keys = {normalize_name(name) for name in company_names}
    for match in PERSON_RE.finditer(text):
        name = _clean_entity_name(match.group(1))
        if not _looks_like_person(name, company_keys):
            continue
        key = normalize_name(name)
        if key in seen:
            continue
        seen.add(key)
        people.append(_entity("Person", name, "Low", match.group(0), source))
    return people


def _extract_deal_hints(text: str, source: TextSource) -> list[ExtractedEntity]:
    seen: set[str] = set()
    deals: list[ExtractedEntity] = []
    for match in DEAL_HINT_RE.finditer(text):
        name = _trim_deal_name(_clean_entity_name(match.group(1)))
        key = normalize_name(name)
        if not key or key in seen:
            continue
        seen.add(key)
        deals.append(_entity("Deal Project", name, "Low", match.group(0), source))
    return deals


def _extract_contact_points(text: str, source: TextSource) -> list[ExtractedContactPoint]:
    contact_points: list[ExtractedContactPoint] = []
    for contact_type, pattern in (("Email", EMAIL_RE), ("Phone", PHONE_RE), ("URL", URL_RE)):
        seen: set[str] = set()
        for match in pattern.finditer(text):
            value = match.group(0).rstrip(".,;")
            key = value.casefold()
            if key in seen:
                continue
            seen.add(key)
            contact_points.append(
                ExtractedContactPoint(
                    contact_type=contact_type,
                    value=value,
                    source_id=source.source_id,
                    source_title=source.title,
                    source_url=source.url,
                )
            )
    return contact_points


def _entity(entity_type: str, name: str, confidence: str, evidence_text: str, source: TextSource) -> ExtractedEntity:
    return ExtractedEntity(
        entity_type=entity_type,
        name=name,
        entity_id=stable_entity_id(entity_type, name),
        confidence=confidence,
        evidence_text=evidence_text.strip(),
        source_id=source.source_id,
        source_title=source.title,
        source_url=source.url,
    )


def _clean_entity_name(name: str) -> str:
    return re.sub(r"\s+", " ", name.strip(" \t\n\r.,;:()[]{}")).strip()


def _trim_company_name(name: str) -> str:
    parts = re.split(r"\b(?:at|by|for|from|into|through|to|with)\s+", name, flags=re.IGNORECASE)
    return parts[-1].strip() if parts else name


def _trim_deal_name(name: str) -> str:
    return re.sub(r"^(?:A|An|The)\s+", "", name).strip()


def _looks_like_person(name: str, company_keys: set[str]) -> bool:
    if name in PERSON_STOP_PHRASES:
        return False
    key = normalize_name(name)
    if key in company_keys:
        return False
    words = key.split()
    if len(words) < 2 or len(words) > 4:
        return False
    if any(word in ORG_WORDS for word in words):
        return False
    return all(len(word) > 1 for word in words)
