from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from .drive_manifest import DriveItemRecord
from .drive_text_extraction import is_supported_ocr_record
from .ocr import OcrConfig, OcrError, ocr_file


class RawDriveFileDownloader(Protocol):
    def download_raw_file(self, record: DriveItemRecord, output_dir: Path) -> Path:
        """Download a non-native Drive file and return its local path."""


@dataclass(frozen=True)
class DriveOcrTextFetcher:
    downloader: RawDriveFileDownloader
    cache_dir: Path
    ocr_config: OcrConfig = OcrConfig()

    def fetch_ocr_text(self, record: DriveItemRecord) -> str:
        if not is_supported_ocr_record(record):
            raise OcrError(f"Unsupported Drive OCR file type: {record.mime_type}")

        self.cache_dir.mkdir(parents=True, exist_ok=True)
        local_path = self.downloader.download_raw_file(record, self.cache_dir)
        return ocr_file(local_path, record.mime_type, self.ocr_config)
