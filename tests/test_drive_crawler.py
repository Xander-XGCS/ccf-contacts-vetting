import unittest

from ccf_contact_vetting.drive_crawler import DriveListItem, crawl_drive_tree
from ccf_contact_vetting.drive_manifest import FOLDER_MIME_TYPE, SHORTCUT_MIME_TYPE


class FakeLister:
    def __init__(self, children_by_folder: dict[str, list[DriveListItem]]) -> None:
        self.children_by_folder = children_by_folder
        self.calls: list[str] = []

    def list_folder(self, folder_id: str) -> list[DriveListItem]:
        self.calls.append(folder_id)
        return self.children_by_folder.get(folder_id, [])


class DriveCrawlerTests(unittest.TestCase):
    def test_crawls_nested_tree_and_keeps_paths(self) -> None:
        lister = FakeLister(
            {
                "root": [
                    folder("contacts", "Contacts", "root"),
                    file("loose", "Loose.pdf", "root"),
                ],
                "contacts": [
                    folder("person", "Person A", "contacts"),
                    shortcut("shortcut", "Pipeline Shortcut", "contacts"),
                ],
                "person": [
                    file("memo", "Memo.docx", "person"),
                ],
            }
        )

        result = crawl_drive_tree("root", lister, root_name="Root")
        paths = {item.file_id: item.current_path for item in result.items}

        self.assertEqual(paths["root"], "Root")
        self.assertEqual(paths["contacts"], "Root/Contacts")
        self.assertEqual(paths["person"], "Root/Contacts/Person A")
        self.assertEqual(paths["memo"], "Root/Contacts/Person A/Memo.docx")
        self.assertEqual(paths["shortcut"], "Root/Contacts/Pipeline Shortcut")
        self.assertEqual(result.folder_count, 3)
        self.assertEqual(result.file_count, 2)
        self.assertEqual(result.shortcut_count, 1)

    def test_does_not_follow_shortcuts_as_folders(self) -> None:
        lister = FakeLister({"root": [shortcut("shortcut", "Shortcut Folder", "root")]})

        result = crawl_drive_tree("root", lister, root_name="Root")

        self.assertEqual([item.file_id for item in result.items], ["root", "shortcut"])
        self.assertEqual(lister.calls, ["root"])

    def test_excludes_out_of_scope_folders(self) -> None:
        lister = FakeLister(
            {
                "root": [
                    folder("active", "Active", "root"),
                    folder("moved", "Moved Elsewhere", "root"),
                ],
                "active": [
                    file("active-file", "Active.pdf", "active"),
                ],
                "moved": [
                    file("moved-file", "Moved.pdf", "moved"),
                ],
            }
        )

        result = crawl_drive_tree("root", lister, root_name="Root", excluded_folder_ids={"moved"})
        item_ids = {item.file_id for item in result.items}

        self.assertIn("active", item_ids)
        self.assertIn("active-file", item_ids)
        self.assertNotIn("moved", item_ids)
        self.assertNotIn("moved-file", item_ids)
        self.assertEqual(lister.calls, ["root", "active"])

    def test_depth_limit_records_error(self) -> None:
        lister = FakeLister({"root": [folder("child", "Child", "root")]})

        result = crawl_drive_tree("root", lister, root_name="Root", max_depth=1)

        self.assertEqual([error.folder_id for error in result.errors], ["child"])
        self.assertIn("depth", result.errors[0].message.casefold())

    def test_item_limit_stops_crawl(self) -> None:
        lister = FakeLister({"root": [file("a", "A.pdf", "root"), file("b", "B.pdf", "root")]})

        result = crawl_drive_tree("root", lister, root_name="Root", max_items=2)

        self.assertEqual(len(result.items), 2)
        self.assertIn("item limit", result.errors[0].message.casefold())


def folder(file_id: str, name: str, parent_id: str) -> DriveListItem:
    return DriveListItem(
        file_id=file_id,
        name=name,
        mime_type=FOLDER_MIME_TYPE,
        url=f"https://drive.google.com/drive/folders/{file_id}",
        parent_folder_id=parent_id,
    )


def file(file_id: str, name: str, parent_id: str) -> DriveListItem:
    return DriveListItem(
        file_id=file_id,
        name=name,
        mime_type="application/pdf",
        url=f"https://drive.google.com/file/d/{file_id}/view",
        parent_folder_id=parent_id,
    )


def shortcut(file_id: str, name: str, parent_id: str) -> DriveListItem:
    return DriveListItem(
        file_id=file_id,
        name=name,
        mime_type=SHORTCUT_MIME_TYPE,
        url=f"https://drive.google.com/file/d/{file_id}/view",
        parent_folder_id=parent_id,
    )


if __name__ == "__main__":
    unittest.main()
