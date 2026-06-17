# Sheet Schema

This is the initial workbook design. The code representation lives in `src/ccf_contact_vetting/workbook_schema.py`.

## Dashboard

Purpose: High-level operating status.

Columns:

- Metric
- Value
- Owner
- Updated At
- Link

## People

Purpose: One row per known person.

Columns:

- Person ID
- Full Name
- Known Aliases
- Primary Company
- Title
- Email
- Phone
- Location
- Contact Folder
- Related Deals
- Related Companies
- Relationship Summary
- Vetting Status
- Risk Level
- Confidence
- Research Memo
- Source Links
- Last Researched At
- Next Action
- Human Review Notes

## Companies

Purpose: One row per known company.

Columns:

- Company ID
- Company Name
- Known Aliases
- Website
- Industry
- Headquarters
- Principals
- Related People
- Related Deals
- Company Folder
- Vetting Status
- Risk Level
- Confidence
- Research Memo
- Source Links
- Last Researched At
- Next Action
- Human Review Notes

## Deals Projects

Purpose: One row per deal, project, or opportunity.

Columns:

- Deal ID
- Deal Project Name
- Status
- Type
- Amount
- Location
- Borrower Sponsor
- Lender Investor
- Related People
- Related Companies
- Source Documents
- Missing Information
- Priority
- Next Action
- Owner
- Updated At

## Relationships

Purpose: Evidence-backed links between people, companies, and deals.

Columns:

- Relationship ID
- Subject Type
- Subject ID
- Subject Name
- Relationship Type
- Object Type
- Object ID
- Object Name
- Evidence Link
- Confidence
- First Seen At
- Last Confirmed At
- Notes

## Research Queue

Purpose: Work queue for agent-assisted research.

Columns:

- Queue ID
- Entity Type
- Entity ID
- Entity Name
- Priority
- Research Goal
- Status
- Assigned To
- Search Terms
- Findings Summary
- Output Folder
- Last Attempt At
- Next Attempt At
- Human Review Required

## Sources

Purpose: Source library for Drive files and public web evidence.

Columns:

- Source ID
- Source Type
- Title
- URL Or Drive Link
- Related Entity Type
- Related Entity ID
- Extracted Facts
- Accessed At
- Reliability
- Notes

## Who Should Talk To Who

Purpose: Outreach and introduction recommendations.

Columns:

- Recommendation ID
- From Person
- To Person
- Related Deal Project
- Recommendation Type
- Why
- Mutual Path
- Priority
- Suggested Angle
- Evidence Links
- Status
- Owner
- Updated At

## Review Log

Purpose: Human review trail and audit notes.

Columns:

- Review ID
- Item Type
- Item ID
- Reviewer
- Decision
- Notes
- Reviewed At
- Follow Up Required

