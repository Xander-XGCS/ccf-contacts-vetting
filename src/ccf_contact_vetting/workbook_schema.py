from __future__ import annotations

import json
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Column:
    name: str
    description: str
    kind: str = "text"
    required: bool = False


@dataclass(frozen=True)
class Tab:
    name: str
    purpose: str
    columns: tuple[Column, ...]


WORKBOOK_SCHEMA: tuple[Tab, ...] = (
    Tab(
        name="Dashboard",
        purpose="High-level operating status.",
        columns=(
            Column("Metric", "Status metric name.", required=True),
            Column("Value", "Current metric value."),
            Column("Owner", "Person responsible for the metric."),
            Column("Updated At", "Last update timestamp.", kind="datetime"),
            Column("Link", "Optional supporting Drive or Sheet link.", kind="url"),
        ),
    ),
    Tab(
        name="People",
        purpose="One row per known person.",
        columns=(
            Column("Person ID", "Stable person identifier.", required=True),
            Column("Full Name", "Best known full name.", required=True),
            Column("Known Aliases", "Alternate names, spellings, or initials."),
            Column("Primary Company", "Current or most relevant company."),
            Column("Title", "Known title or role."),
            Column("Email", "Known email address.", kind="email"),
            Column("Phone", "Known phone number."),
            Column("Location", "Known city, state, or region."),
            Column("Contact Folder", "Drive folder for the person.", kind="url"),
            Column("Related Deals", "Deal or project identifiers."),
            Column("Related Companies", "Company identifiers."),
            Column("Relationship Summary", "Plain-English relationship summary."),
            Column("Vetting Status", "Not Started, In Progress, Reviewed, or Blocked."),
            Column("Risk Level", "None, Low, Medium, High, or Needs Review."),
            Column("Confidence", "High, Medium, Low, or Needs Review."),
            Column("Research Memo", "Drive link to research memo.", kind="url"),
            Column("Source Links", "Evidence links supporting the row."),
            Column("Last Researched At", "Last research timestamp.", kind="datetime"),
            Column("Next Action", "Recommended next action."),
            Column("Human Review Notes", "Reviewer notes and unresolved questions."),
        ),
    ),
    Tab(
        name="Companies",
        purpose="One row per known company.",
        columns=(
            Column("Company ID", "Stable company identifier.", required=True),
            Column("Company Name", "Best known company name.", required=True),
            Column("Known Aliases", "Alternate names or DBA names."),
            Column("Website", "Company website.", kind="url"),
            Column("Industry", "Industry or operating category."),
            Column("Headquarters", "Known headquarters or principal location."),
            Column("Principals", "Known principals or key people."),
            Column("Related People", "Person identifiers."),
            Column("Related Deals", "Deal or project identifiers."),
            Column("Company Folder", "Drive folder for the company.", kind="url"),
            Column("Vetting Status", "Not Started, In Progress, Reviewed, or Blocked."),
            Column("Risk Level", "None, Low, Medium, High, or Needs Review."),
            Column("Confidence", "High, Medium, Low, or Needs Review."),
            Column("Research Memo", "Drive link to research memo.", kind="url"),
            Column("Source Links", "Evidence links supporting the row."),
            Column("Last Researched At", "Last research timestamp.", kind="datetime"),
            Column("Next Action", "Recommended next action."),
            Column("Human Review Notes", "Reviewer notes and unresolved questions."),
        ),
    ),
    Tab(
        name="Deals Projects",
        purpose="One row per deal, project, or opportunity.",
        columns=(
            Column("Deal ID", "Stable deal or project identifier.", required=True),
            Column("Deal Project Name", "Name of the deal, project, or opportunity.", required=True),
            Column("Status", "Current status."),
            Column("Type", "Deal, project, opportunity, referral, or other type."),
            Column("Amount", "Known dollar amount.", kind="currency"),
            Column("Location", "Project or collateral location."),
            Column("Borrower Sponsor", "Known borrower, sponsor, or principal."),
            Column("Lender Investor", "Known lender, investor, or capital source."),
            Column("Related People", "Person identifiers."),
            Column("Related Companies", "Company identifiers."),
            Column("Source Documents", "Drive links for source documents."),
            Column("Missing Information", "Known gaps."),
            Column("Priority", "Operating priority."),
            Column("Next Action", "Recommended next action."),
            Column("Owner", "Internal owner."),
            Column("Updated At", "Last update timestamp.", kind="datetime"),
        ),
    ),
    Tab(
        name="Relationships",
        purpose="Evidence-backed links between people, companies, and deals.",
        columns=(
            Column("Relationship ID", "Stable relationship identifier.", required=True),
            Column("Subject Type", "Person, Company, or Deal Project.", required=True),
            Column("Subject ID", "Stable subject identifier.", required=True),
            Column("Subject Name", "Human-readable subject name."),
            Column("Relationship Type", "Role or relationship type.", required=True),
            Column("Object Type", "Person, Company, or Deal Project.", required=True),
            Column("Object ID", "Stable object identifier.", required=True),
            Column("Object Name", "Human-readable object name."),
            Column("Evidence Link", "Source evidence link.", kind="url"),
            Column("Confidence", "High, Medium, Low, or Needs Review."),
            Column("First Seen At", "First observed timestamp.", kind="datetime"),
            Column("Last Confirmed At", "Last confirmed timestamp.", kind="datetime"),
            Column("Notes", "Relationship notes."),
        ),
    ),
    Tab(
        name="Research Queue",
        purpose="Work queue for agent-assisted research.",
        columns=(
            Column("Queue ID", "Stable queue item identifier.", required=True),
            Column("Entity Type", "Person or Company.", required=True),
            Column("Entity ID", "Stable entity identifier.", required=True),
            Column("Entity Name", "Human-readable entity name.", required=True),
            Column("Priority", "Research priority."),
            Column("Research Goal", "Question the research run should answer."),
            Column("Status", "Queued, In Progress, Complete, Blocked, or Review."),
            Column("Assigned To", "Agent or person assigned."),
            Column("Search Terms", "Search terms to use or audit."),
            Column("Findings Summary", "Concise result summary."),
            Column("Output Folder", "Drive folder for filed research.", kind="url"),
            Column("Last Attempt At", "Last research attempt timestamp.", kind="datetime"),
            Column("Next Attempt At", "Next scheduled attempt timestamp.", kind="datetime"),
            Column("Human Review Required", "Whether a human must review.", kind="boolean"),
        ),
    ),
    Tab(
        name="Sources",
        purpose="Source library for Drive files and public web evidence.",
        columns=(
            Column("Source ID", "Stable source identifier.", required=True),
            Column("Source Type", "Drive File, Web Page, Registry, News, Court, or Other."),
            Column("Title", "Source title.", required=True),
            Column("URL Or Drive Link", "Source URL or Drive link.", kind="url"),
            Column("Related Entity Type", "Person, Company, Deal Project, or Relationship."),
            Column("Related Entity ID", "Stable related entity identifier."),
            Column("Extracted Facts", "Facts supported by this source."),
            Column("Accessed At", "Access timestamp.", kind="datetime"),
            Column("Reliability", "High, Medium, Low, or Needs Review."),
            Column("Notes", "Source notes."),
        ),
    ),
    Tab(
        name="Who Should Talk To Who",
        purpose="Outreach and introduction recommendations.",
        columns=(
            Column("Recommendation ID", "Stable recommendation identifier.", required=True),
            Column("From Person", "Recommended sender or introducer.", required=True),
            Column("To Person", "Recommended recipient.", required=True),
            Column("Related Deal Project", "Relevant deal or project."),
            Column("Recommendation Type", "Intro, follow-up, diligence, or relationship warm-up."),
            Column("Why", "Reason for the recommendation."),
            Column("Mutual Path", "Known relationship path."),
            Column("Priority", "Outreach priority."),
            Column("Suggested Angle", "Suggested outreach angle for human review."),
            Column("Evidence Links", "Supporting evidence links."),
            Column("Status", "Proposed, Approved, Sent, Snoozed, or Declined."),
            Column("Owner", "Internal owner."),
            Column("Updated At", "Last update timestamp.", kind="datetime"),
        ),
    ),
    Tab(
        name="Review Log",
        purpose="Human review trail and audit notes.",
        columns=(
            Column("Review ID", "Stable review identifier.", required=True),
            Column("Item Type", "Person, Company, Deal Project, Relationship, or Source."),
            Column("Item ID", "Stable item identifier."),
            Column("Reviewer", "Human reviewer."),
            Column("Decision", "Approved, Corrected, Rejected, Needs Follow Up, or Deferred."),
            Column("Notes", "Review notes."),
            Column("Reviewed At", "Review timestamp.", kind="datetime"),
            Column("Follow Up Required", "Whether follow up is needed.", kind="boolean"),
        ),
    ),
)


def schema_as_dict() -> dict[str, object]:
    return {"tabs": [asdict(tab) for tab in WORKBOOK_SCHEMA]}


def schema_as_json(indent: int = 2) -> str:
    return json.dumps(schema_as_dict(), indent=indent)


def schema_as_markdown() -> str:
    lines: list[str] = ["# Workbook Schema", ""]
    for tab in WORKBOOK_SCHEMA:
        lines.extend([f"## {tab.name}", "", tab.purpose, "", "| Column | Kind | Required | Description |", "| --- | --- | --- | --- |"])
        for column in tab.columns:
            required = "yes" if column.required else "no"
            lines.append(f"| {column.name} | {column.kind} | {required} | {column.description} |")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"

