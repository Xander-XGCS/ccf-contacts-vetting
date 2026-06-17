import unittest

from ccf_contact_vetting.drive_text_extraction import DriveTextDocument, extracted_sheet_rows, extract_drive_document
from ccf_contact_vetting.sheet_append import append_cells_requests, collect_rows_by_tab, sheet_ids_from_metadata


class SheetAppendTests(unittest.TestCase):
    def test_collects_extracted_rows_by_target_tab(self) -> None:
        result = extract_drive_document(
            DriveTextDocument(
                file_id="doc-1",
                title="Source",
                text="Carol Pepper introduced Richard Boxall to Infinity Global Resource Group.",
            )
        )
        rows = collect_rows_by_tab([extracted_sheet_rows(result)])

        self.assertIn("People", rows)
        self.assertIn("Companies", rows)
        self.assertIn("Evidence Sources", rows)
        self.assertIn("Research Queue", rows)
        self.assertEqual(len(rows["People"]), 2)

    def test_builds_append_cells_requests_from_sheet_metadata(self) -> None:
        sheet_ids = sheet_ids_from_metadata(
            {
                "sheets": [
                    {"properties": {"title": "People", "sheetId": 101}},
                    {"properties": {"title": "Research Queue", "sheetId": 202}},
                ]
            }
        )

        requests = append_cells_requests(
            {
                "People": [["person_1", "Carol Pepper"]],
                "Research Queue": [["rq_1", "Person", "person_1", "Carol Pepper", "Medium"]],
            },
            sheet_ids,
        )

        self.assertEqual(len(requests), 2)
        self.assertEqual(requests[0]["appendCells"]["sheetId"], 101)
        self.assertEqual(
            requests[0]["appendCells"]["rows"][0]["values"][1]["userEnteredValue"]["stringValue"],
            "Carol Pepper",
        )
        self.assertEqual(requests[0]["appendCells"]["fields"], "userEnteredValue")

    def test_append_requests_require_known_sheet_id(self) -> None:
        with self.assertRaises(KeyError):
            append_cells_requests({"People": [["person_1"]]}, {})


if __name__ == "__main__":
    unittest.main()
