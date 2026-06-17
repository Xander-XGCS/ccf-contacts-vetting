from __future__ import annotations

import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path


PDF_MIME_TYPE = "application/pdf"

SUPPORTED_OCR_MIME_TYPES = {
    PDF_MIME_TYPE,
    "image/bmp",
    "image/gif",
    "image/jpeg",
    "image/png",
    "image/tiff",
    "image/webp",
}


class OcrError(RuntimeError):
    """Base OCR error."""


class OcrUnavailableError(OcrError):
    """Raised when the host does not have the needed OCR command-line tools."""


@dataclass(frozen=True)
class OcrConfig:
    tesseract_cmd: str = "tesseract"
    pdftoppm_cmd: str = "pdftoppm"
    language: str = "eng"
    dpi: int = 300
    timeout_seconds: int = 180
    max_pdf_pages: int | None = 10


def is_supported_ocr_mime_type(mime_type: str) -> bool:
    return mime_type in SUPPORTED_OCR_MIME_TYPES


def ocr_file(path: Path, mime_type: str, config: OcrConfig | None = None) -> str:
    active_config = config or OcrConfig()
    if mime_type == PDF_MIME_TYPE:
        return ocr_pdf(path, active_config)
    if is_supported_ocr_mime_type(mime_type):
        return ocr_image(path, active_config)
    raise OcrError(f"Unsupported OCR MIME type: {mime_type}")


def ocr_image(path: Path, config: OcrConfig | None = None) -> str:
    active_config = config or OcrConfig()
    _require_command(active_config.tesseract_cmd, "Tesseract OCR")
    result = _run(
        [
            active_config.tesseract_cmd,
            str(path),
            "stdout",
            "-l",
            active_config.language,
        ],
        timeout_seconds=active_config.timeout_seconds,
    )
    return result.stdout.strip()


def ocr_pdf(path: Path, config: OcrConfig | None = None) -> str:
    active_config = config or OcrConfig()
    _require_command(active_config.pdftoppm_cmd, "Poppler pdftoppm")
    _require_command(active_config.tesseract_cmd, "Tesseract OCR")

    with tempfile.TemporaryDirectory(prefix="ccf-ocr-") as temp_dir:
        output_prefix = Path(temp_dir) / "page"
        command = [
            active_config.pdftoppm_cmd,
            "-r",
            str(active_config.dpi),
            "-png",
        ]
        if active_config.max_pdf_pages is not None:
            command.extend(["-f", "1", "-l", str(active_config.max_pdf_pages)])
        command.extend([str(path), str(output_prefix)])
        _run(command, timeout_seconds=active_config.timeout_seconds)

        page_images = sorted(Path(temp_dir).glob("page-*.png"))
        if not page_images:
            raise OcrError(f"No OCR page images were rendered for {path}")

        page_text = [ocr_image(page_image, active_config) for page_image in page_images]
        return "\n\n".join(text for text in page_text if text).strip()


def _require_command(command: str, label: str) -> None:
    if shutil.which(command) is None:
        raise OcrUnavailableError(f"{label} command not found: {command}")


def _run(command: list[str], *, timeout_seconds: int) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
    except FileNotFoundError as exc:
        raise OcrUnavailableError(f"OCR command not found: {command[0]}") from exc
    except subprocess.TimeoutExpired as exc:
        raise OcrError(f"OCR command timed out: {command[0]}") from exc
    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr.strip() if exc.stderr else "no stderr"
        raise OcrError(f"OCR command failed: {command[0]}: {stderr}") from exc
