import unittest

from ccf_contact_vetting.drive_manifest import DriveItemRecord, FOLDER_MIME_TYPE
from ccf_contact_vetting.drive_text_extraction import (
    DriveTextDocument,
    extracted_facts_summary,
    extracted_sheet_rows,
    extract_drive_document,
    extract_drive_record_text,
    is_supported_text_record,
)


class DriveTextExtractionTests(unittest.TestCase):
    def test_supported_text_record_requires_file_and_supported_mime_type(self) -> None:
        self.assertTrue(is_supported_text_record(record("file-1", "Memo.pdf", "application/pdf")))
        self.assertFalse(is_supported_text_record(record("folder-1", "Contacts", FOLDER_MIME_TYPE, item_type="Folder")))
        self.assertFalse(is_supported_text_record(record("image-1", "Photo.png", "image/png")))

    def test_extract_drive_record_text_uses_drive_path_as_source_title(self) -> None:
        result = extract_drive_record_text(
            record("doc-1", "Memo", "text/plain", current_path="Root/Richard Boxall/Memo.txt"),
            "Richard Boxall works with Infinity Global Resource Group.",
        )

        self.assertEqual(result.source.title, "Root/Richard Boxall/Memo.txt")
        self.assertIn("Richard Boxall", {person.name for person in result.people})
        self.assertIn("Infinity Global Resource Group", {company.name for company in result.companies})

    def test_extract_drive_document_and_rows_bundle_sheet_targets(self) -> None:
        result = extract_drive_document(
            DriveTextDocument(
                file_id="doc-1",
                title="Source",
                path="Root/Carol Pepper/Note",
                url="https://drive.google.com/file/d/doc-1/view",
                text="Carol Pepper introduced Richard Boxall to the Ogden Mountain Project.",
            )
        )

        rows = extracted_sheet_rows(result)

        self.assertEqual(len(rows.people), 2)
        self.assertEqual(len(rows.deals), 1)
        self.assertEqual(len(rows.evidence_sources), 1)
        self.assertEqual(len(rows.research_queue), 2)
        self.assertGreater(rows.row_count, 0)
        self.assertIn("People: Carol Pepper, Richard Boxall", extracted_facts_summary(result))
        self.assertIn("Deals/Projects: Ogden Mountain Project", extracted_facts_summary(result))


def record(
    file_id: str,
    name: str,
    mime_type: str,
    *,
    item_type: str = "File",
    current_path: str = "",
) -> DriveItemRecord:
    return DriveItemRecord(
        file_id=file_id,
        name=name,
        mime_type=mime_type,
        item_type=item_type,
        current_path=current_path or f"Root/{name}",
        parent_folder_id="root",
        drive_url=f"https://drive.google.com/file/d/{file_id}/view",
    )


if __name__ == "__main__":
    unittest.main()
