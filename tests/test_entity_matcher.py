import unittest

from ccf_contact_vetting.entity_extraction import TextSource, extract_text_entities
from ccf_contact_vetting.entity_matcher import EntityRecord, match_entity


class EntityMatcherTests(unittest.TestCase):
    def test_matches_by_exact_email(self) -> None:
        candidate = extract_text_entities("Richard Boxall", TextSource("source", "Source")).people[0]
        record = EntityRecord(
            entity_id="person_existing",
            entity_type="Person",
            name="R. Boxall",
            email="richard.boxall@example.com",
        )

        decision = match_entity(candidate, [record], email="richard.boxall@example.com")

        self.assertEqual(decision.match_status, "Matched")
        self.assertEqual(decision.matched_entity_id, "person_existing")
        self.assertEqual(decision.confidence, "High")

    def test_matches_by_normalized_alias(self) -> None:
        candidate = extract_text_entities("Richard Boxall", TextSource("source", "Source")).people[0]
        record = EntityRecord(
            entity_id="person_existing",
            entity_type="Person",
            name="Richard J. Boxall",
            aliases=("Richard Boxall",),
        )

        decision = match_entity(candidate, [record])

        self.assertEqual(decision.match_status, "Matched")
        self.assertEqual(decision.reason, "Exact normalized name or alias match.")

    def test_possible_overlap_requires_review(self) -> None:
        candidate = extract_text_entities("Richard Boxall", TextSource("source", "Source")).people[0]
        record = EntityRecord(entity_id="person_existing", entity_type="Person", name="Richard Boxall Jr")

        decision = match_entity(candidate, [record])

        self.assertEqual(decision.match_status, "Needs Review")
        self.assertEqual(decision.confidence, "Medium")

    def test_new_candidate_when_no_match(self) -> None:
        candidate = extract_text_entities("Carol Pepper", TextSource("source", "Source")).people[0]
        record = EntityRecord(entity_id="person_existing", entity_type="Person", name="Richard Boxall")

        decision = match_entity(candidate, [record])

        self.assertEqual(decision.match_status, "New Candidate")
        self.assertEqual(decision.matched_entity_id, "")


if __name__ == "__main__":
    unittest.main()
