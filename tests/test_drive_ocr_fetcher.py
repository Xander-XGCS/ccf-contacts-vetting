import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from ccf_contact_vetting.drive_manifest import DriveItemRecord
from ccf_contact_vetting.drive_ocr_fetcher import DriveOcrTextFetcher
from ccf_contact_vetting.ocr import OcrError


class FakeDownloader:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.calls: list[tuple[str, Path]] = []

    def download_raw_file(self, record: DriveItemRecord, output_dir: Path) -> Path:
        self.calls.append((record.file_id, output_dir))
        return self.path


class DriveOcrTextFetcherTests(unittest.TestCase):
    def test_downloads_raw_file_then_runs_ocr(self) -> None:
        with TemporaryDirectory() as temp_dir:
            cache_dir = Path(temp_dir) / "ocr-cache"
            local_file = Path(temp_dir) / "seller.pdf"
            downloader = FakeDownloader(local_file)
            fetcher = DriveOcrTextFetcher(downloader=downloader, cache_dir=cache_dir)

            with patch("ccf_contact_vetting.drive_ocr_fetcher.ocr_file", return_value="Anslem N. Gbemudu") as ocr:
                text = fetcher.fetch_ocr_text(record("seller-cis", "Seller CIS.pdf", "application/pdf"))

        self.assertEqual(text, "Anslem N. Gbemudu")
        self.assertEqual(downloader.calls, [("seller-cis", cache_dir)])
        ocr.assert_called_once()
        self.assertEqual(ocr.call_args.args[0], local_file)
        self.assertEqual(ocr.call_args.args[1], "application/pdf")

    def test_rejects_unsupported_drive_file_type(self) -> None:
        with TemporaryDirectory() as temp_dir:
            fetcher = DriveOcrTextFetcher(
                downloader=FakeDownloader(Path(temp_dir) / "memo.txt"),
                cache_dir=Path(temp_dir),
            )

            with self.assertRaises(OcrError):
                fetcher.fetch_ocr_text(record("memo", "Memo.txt", "text/plain"))


def record(file_id: str, name: str, mime_type: str) -> DriveItemRecord:
    return DriveItemRecord(
        file_id=file_id,
        name=name,
        mime_type=mime_type,
        item_type="File",
        current_path=f"Root/{name}",
        parent_folder_id="root",
        drive_url=f"https://drive.google.com/file/d/{file_id}/view",
    )


if __name__ == "__main__":
    unittest.main()
