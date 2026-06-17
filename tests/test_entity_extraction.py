import unittest

from ccf_contact_vetting.entity_extraction import (
    TextSource,
    company_sheet_row,
    deal_sheet_row,
    evidence_source_row,
    extract_text_entities,
    person_sheet_row,
    research_queue_row,
    stable_entity_id,
)


class EntityExtractionTests(unittest.TestCase):
    def test_extracts_core_entities_and_contact_points(self) -> None:
        source = TextSource(
            source_id="drive-file-1",
            title="Boxall Email 6-15-26",
            url="https://drive.google.com/file/d/drive-file-1/view",
        )
        result = extract_text_entities(
            """
            Dr. Carol Pepper introduced Richard Boxall to Complete Capital Funding.
            Richard Boxall works with Infinity Global Resource Group.
            The Ogden Mountain Project needs follow-up.
            Contact richard.boxall@example.com or +1 (555) 222-3333.
            See https://example.com/profile.
            """,
            source,
        )

        self.assertIn("Carol Pepper", {person.name for person in result.people})
        self.assertIn("Richard Boxall", {person.name for person in result.people})
        self.assertIn("Infinity Global Resource Group", {company.name for company in result.companies})
        self.assertIn("Ogden Mountain Project", {deal.name for deal in result.deals})
        self.assertIn("richard.boxall@example.com", {point.value for point in result.contact_points})
        self.assertIn("+1 (555) 222-3333", {point.value for point in result.contact_points})
        self.assertIn("https://example.com/profile", {point.value for point in result.contact_points})

    def test_stable_entity_id_is_deterministic(self) -> None:
        first = stable_entity_id("Person", "Richard Boxall")
        second = stable_entity_id("Person", "  richard   boxall ")

        self.assertEqual(first, second)
        self.assertTrue(first.startswith("person_"))

    def test_sheet_rows_match_workbook_schema_widths(self) -> None:
        source = TextSource(source_id="source", title="Source Title", url="https://example.com/source")
        result = extract_text_entities(
            "Carol Pepper at Pepper International LLC discussed Ogden Mountain Project.",
            source,
        )

        self.assertEqual(len(person_sheet_row(result.people[0])), 23)
        self.assertEqual(len(company_sheet_row(result.companies[0])), 18)
        self.assertEqual(len(deal_sheet_row(result.deals[0])), 16)
        self.assertEqual(len(evidence_source_row(source, "facts")), 10)
        self.assertEqual(len(research_queue_row(result.people[0])), 14)


if __name__ == "__main__":
    unittest.main()
