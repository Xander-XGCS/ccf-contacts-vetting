import unittest

from ccf_contact_vetting.drive_manifest import (
    DriveItemRecord,
    diff_manifests,
    extract_drive_id,
    propose_structure_suggestions,
)


class DriveManifestTests(unittest.TestCase):
    def test_extract_drive_id_from_folder_url(self) -> None:
        url = "https://drive.google.com/drive/folders/1dDJrpLWnSLKoTSKEERInWW9iIp3Af0k1?usp=drive_link"
        self.assertEqual(extract_drive_id(url), "1dDJrpLWnSLKoTSKEERInWW9iIp3Af0k1")

    def test_diff_manifests_detects_key_changes(self) -> None:
        previous = [
            item("a", "Old Name", "Folder/Old Name", "root", modified_at="2026-01-01T00:00:00Z"),
            item("b", "Changed File", "Folder/Changed File", "folder", modified_at="2026-01-01T00:00:00Z"),
            item("c", "Removed File", "Folder/Removed File", "folder"),
        ]
        current = [
            item("a", "New Name", "Folder/New Name", "root", modified_at="2026-01-01T00:00:00Z"),
            item("b", "Changed File", "Folder/Changed File", "folder", modified_at="2026-01-02T00:00:00Z"),
            item("d", "Added File", "Folder/Added File", "folder"),
        ]

        changes = diff_manifests(previous, current)
        change_types = {change.file_id: change.change_type for change in changes}

        self.assertEqual(change_types["a"], "Moved Or Renamed")
        self.assertEqual(change_types["b"], "Modified")
        self.assertEqual(change_types["c"], "Removed")
        self.assertEqual(change_types["d"], "Added")

    def test_structure_suggestions_require_approval(self) -> None:
        records = [
            item("folder-1", "Contacts ", "Contacts ", "root", item_type="Folder"),
            item("folder-2", "contacts", "contacts", "root", item_type="Folder"),
            item("file-1", "Loose.pdf", "Loose.pdf", "root", item_type="File", mime_type="application/pdf"),
        ]

        suggestions = propose_structure_suggestions(records, root_folder_id="root")

        self.assertTrue(suggestions)
        self.assertTrue(all(suggestion.requires_approval for suggestion in suggestions))
        self.assertIn("Rename Folder", {suggestion.suggestion_type for suggestion in suggestions})
        self.assertIn("Move Root File To Intake", {suggestion.suggestion_type for suggestion in suggestions})
        self.assertIn("Review Duplicate Folder Name", {suggestion.suggestion_type for suggestion in suggestions})

    def test_structure_suggestions_can_exclude_system_files_from_intake(self) -> None:
        records = [
            item("control-sheet", "CCF Relationship Intelligence", "CCF Relationship Intelligence", "root", item_type="File"),
            item("loose-file", "Loose.pdf", "Loose.pdf", "root", item_type="File", mime_type="application/pdf"),
        ]

        suggestions = propose_structure_suggestions(records, root_folder_id="root", excluded_file_ids={"control-sheet"})

        intake_target_ids = {
            suggestion.target_file_id
            for suggestion in suggestions
            if suggestion.suggestion_type == "Move Root File To Intake"
        }
        self.assertEqual(intake_target_ids, {"loose-file"})


def item(
    file_id: str,
    name: str,
    path: str,
    parent_id: str,
    item_type: str = "File",
    mime_type: str = "application/octet-stream",
    modified_at: str = "",
) -> DriveItemRecord:
    return DriveItemRecord(
        file_id=file_id,
        name=name,
        mime_type=mime_type,
        item_type=item_type,
        current_path=path,
        parent_folder_id=parent_id,
        drive_url=f"https://drive.google.com/file/d/{file_id}/view",
        modified_at=modified_at,
    )


if __name__ == "__main__":
    unittest.main()
