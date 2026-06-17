import unittest

from ccf_contact_vetting.profile_refresh import ProfileEvidenceItem, profile_refresh_decision


class ProfileRefreshTests(unittest.TestCase):
    def test_requires_refresh_when_profile_missing(self) -> None:
        decision = profile_refresh_decision(
            profile_url="",
            last_refreshed_at="2026-06-17T10:00:00-07:00",
            evidence_items=[],
        )

        self.assertTrue(decision.refresh_required)
        self.assertIn("No profile document is linked.", decision.reasons)

    def test_requires_refresh_when_evidence_is_newer_than_profile(self) -> None:
        decision = profile_refresh_decision(
            profile_url="https://docs.google.com/document/d/profile/edit",
            last_refreshed_at="2026-06-17T10:00:00-07:00",
            evidence_items=[
                ProfileEvidenceItem(
                    file_id="seller-cis",
                    name="Seller CIS.pdf",
                    modified_at="2026-06-17T11:00:00-07:00",
                    parsed_status="Parsed",
                )
            ],
        )

        self.assertTrue(decision.refresh_required)
        self.assertIn("Evidence file is newer than profile: Seller CIS.pdf (seller-cis).", decision.reasons)

    def test_requires_refresh_when_ocr_review_is_unresolved(self) -> None:
        decision = profile_refresh_decision(
            profile_url="https://docs.google.com/document/d/profile/edit",
            last_refreshed_at="2026-06-17T10:00:00-07:00",
            evidence_items=[
                ProfileEvidenceItem(
                    file_id="seller-cis",
                    name="Seller CIS.pdf",
                    modified_at="2026-06-17T09:00:00-07:00",
                    parsed_status="Needs Review",
                    notes="OCR/manual review required.",
                )
            ],
        )

        self.assertTrue(decision.refresh_required)
        self.assertIn("Evidence file needs review before profile can be current: Seller CIS.pdf (seller-cis).", decision.reasons)

    def test_no_refresh_when_profile_is_current(self) -> None:
        decision = profile_refresh_decision(
            profile_url="https://docs.google.com/document/d/profile/edit",
            last_refreshed_at="2026-06-17T10:00:00-07:00",
            evidence_items=[
                ProfileEvidenceItem(
                    file_id="doc-1",
                    name="Profile Evidence.pdf",
                    modified_at="2026-06-17T09:00:00-07:00",
                    parsed_status="Parsed",
                )
            ],
        )

        self.assertFalse(decision.refresh_required)
        self.assertEqual(decision.reasons, ())


if __name__ == "__main__":
    unittest.main()
