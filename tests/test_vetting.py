import unittest

from ccf_contact_vetting.vetting import (
    VettingRecord,
    credibility_grade,
    human_review_row,
    stable_vetting_id,
    vetting_sheet_row,
)


class VettingTests(unittest.TestCase):
    def test_stable_vetting_id_is_deterministic(self) -> None:
        first = stable_vetting_id("Person", "person_123")
        second = stable_vetting_id("person", "PERSON_123")

        self.assertEqual(first, second)
        self.assertTrue(first.startswith("vet_"))

    def test_credibility_grade_bands_and_review_cap(self) -> None:
        self.assertEqual(credibility_grade(90), "A")
        self.assertEqual(credibility_grade(75), "B")
        self.assertEqual(credibility_grade(55), "C")
        self.assertEqual(credibility_grade(40), "D")
        self.assertEqual(credibility_grade(90, needs_review=True), "Needs Review")
        self.assertEqual(credibility_grade(None), "Needs Review")

    def test_vetting_row_matches_sheet_width(self) -> None:
        record = VettingRecord(
            entity_type="Person",
            entity_id="person_123",
            entity_name="Carol Pepper",
            research_status="Reviewed",
            credibility_score=72,
            credibility_grade="B",
            score_confidence="Medium",
            identity_confidence="Medium",
            source_quality="Medium",
            professional_track_record="Moderate",
            deal_relevance="Strong",
            risk_flag_severity="Needs Review",
            positive_signals="Public profile found.",
            red_flags="None found in reviewed sources.",
            open_questions="Confirm identity.",
            evidence_links="https://example.com",
            last_researched_at="2026-06-17T00:00:00Z",
        )

        row = vetting_sheet_row(record)

        self.assertEqual(len(row), 21)
        self.assertEqual(row[0], record.vetting_id)
        self.assertTrue(row[19])

    def test_human_review_row_matches_sheet_width(self) -> None:
        row = human_review_row(item_type="Person", item_id="person_123", notes="Confirm identity.")

        self.assertEqual(len(row), 8)
        self.assertTrue(row[0].startswith("review_"))
        self.assertEqual(row[4], "Needs Follow Up")


if __name__ == "__main__":
    unittest.main()
