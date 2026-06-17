import unittest

from ccf_contact_vetting.drive_manifest import DriveItemRecord, StructureSuggestion
from ccf_contact_vetting.google_drive_connector import (
    connector_file_to_drive_item,
    connector_listing_to_drive_items,
    file_inventory_row,
    structure_suggestion_row,
    update_run_row,
)


class GoogleDriveConnectorTests(unittest.TestCase):
    def test_connector_file_to_drive_item_maps_plugin_shape(self) -> None:
        item = connector_file_to_drive_item(
            {
                "id": "abc123",
                "title": "Contacts",
                "mime_type": "application/vnd.google-apps.folder",
                "url": "https://drive.google.com/drive/folders/abc123",
                "created_time": "2026-01-01T00:00:00Z",
                "modified_time": "2026-01-02T00:00:00Z",
            },
            fallback_parent_id="root",
        )

        self.assertEqual(item.file_id, "abc123")
        self.assertEqual(item.name, "Contacts")
        self.assertEqual(item.parent_folder_id, "root")

    def test_connector_listing_to_drive_items_requires_files_list(self) -> None:
        with self.assertRaises(ValueError):
            connector_listing_to_drive_items({"files": "not-a-list"})

    def test_file_inventory_row_matches_sheet_columns(self) -> None:
        row = file_inventory_row(
            DriveItemRecord(
                file_id="file-1",
                name="Memo.pdf",
                mime_type="application/pdf",
                item_type="File",
                current_path="Root/Memo.pdf",
                parent_folder_id="root",
                drive_url="https://drive.google.com/file/d/file-1/view",
                created_at="2026-01-01T00:00:00Z",
                modified_at="2026-01-02T00:00:00Z",
                last_seen_at="2026-01-03T00:00:00Z",
            )
        )

        self.assertEqual(len(row), 14)
        self.assertEqual(row[0], "file-1")
        self.assertEqual(row[10], "Not Parsed")

    def test_structure_suggestion_row_matches_sheet_columns(self) -> None:
        row = structure_suggestion_row(
            StructureSuggestion(
                suggestion_id="sg_1",
                suggestion_type="Rename Folder",
                target_file_id="folder-1",
                target_name="Contacts ",
                current_path="Root/Contacts ",
                proposed_path="",
                proposed_name="Contacts",
                reason="Trailing whitespace.",
                confidence="High",
            )
        )

        self.assertEqual(len(row), 14)
        self.assertEqual(row[9], "Proposed")

    def test_update_run_row_matches_sheet_columns(self) -> None:
        row = update_run_row(
            run_id="run-1",
            trigger="Manual",
            root_folder_id="root",
            started_at="2026-01-01T00:00:00Z",
            completed_at="2026-01-01T00:01:00Z",
            status="Complete",
            items_scanned=10,
            new_items=10,
            modified_items=0,
            removed_items=0,
            moved_or_renamed_items=0,
            error_count=0,
            notes="ok",
        )

        self.assertEqual(len(row), 13)
        self.assertEqual(row[5], "Complete")


if __name__ == "__main__":
    unittest.main()

