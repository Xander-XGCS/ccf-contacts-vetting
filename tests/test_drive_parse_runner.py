import unittest

from ccf_contact_vetting.drive_manifest import DriveItemRecord, FOLDER_MIME_TYPE
from ccf_contact_vetting.drive_parse_runner import parse_drive_records


class FakeFetcher:
    def __init__(self, text_by_file_id: dict[str, str], failing_file_ids: set[str] | None = None) -> None:
        self.text_by_file_id = text_by_file_id
        self.failing_file_ids = failing_file_ids or set()
        self.calls: list[str] = []

    def fetch_text(self, record: DriveItemRecord) -> str:
        self.calls.append(record.file_id)
        if record.file_id in self.failing_file_ids:
            raise RuntimeError("fetch failed")
        return self.text_by_file_id.get(record.file_id, "")


class DriveParseRunnerTests(unittest.TestCase):
    def test_parses_supported_records_and_groups_sheet_rows(self) -> None:
        records = [
            record("doc-1", "Memo.txt", "text/plain"),
            record("image-1", "Photo.png", "image/png"),
            record("folder-1", "Contacts", FOLDER_MIME_TYPE, item_type="Folder"),
        ]
        fetcher = FakeFetcher({"doc-1": "Carol Pepper introduced Richard Boxall."})

        result = parse_drive_records(records, fetcher)

        self.assertEqual(fetcher.calls, ["doc-1"])
        self.assertEqual(result.parsed_count, 1)
        self.assertEqual(result.skipped_count, 2)
        self.assertEqual(result.error_count, 0)
        self.assertIn("People", result.rows_by_tab)
        self.assertIn("Research Queue", result.rows_by_tab)

    def test_records_fetch_errors_without_stopping_run(self) -> None:
        records = [
            record("doc-1", "Memo.txt", "text/plain"),
            record("doc-2", "Other.txt", "text/plain"),
        ]
        fetcher = FakeFetcher(
            {"doc-2": "Richard Boxall works with Infinity Global Resource Group."},
            failing_file_ids={"doc-1"},
        )

        result = parse_drive_records(records, fetcher)

        self.assertEqual(result.parsed_count, 1)
        self.assertEqual(result.error_count, 1)
        self.assertEqual(result.errors[0].file_id, "doc-1")

    def test_limit_caps_candidate_fetches(self) -> None:
        records = [
            record("doc-1", "One.txt", "text/plain"),
            record("doc-2", "Two.txt", "text/plain"),
        ]
        fetcher = FakeFetcher({"doc-1": "Carol Pepper", "doc-2": "Richard Boxall"})

        result = parse_drive_records(records, fetcher, limit=1)

        self.assertEqual(fetcher.calls, ["doc-1"])
        self.assertEqual(result.skipped_count, 1)


def record(
    file_id: str,
    name: str,
    mime_type: str,
    *,
    item_type: str = "File",
) -> DriveItemRecord:
    return DriveItemRecord(
        file_id=file_id,
        name=name,
        mime_type=mime_type,
        item_type=item_type,
        current_path=f"Root/{name}",
        parent_folder_id="root",
        drive_url=f"https://drive.google.com/file/d/{file_id}/view",
    )


if __name__ == "__main__":
    unittest.main()
