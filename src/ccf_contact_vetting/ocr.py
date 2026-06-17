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

DEFAULT_TESSERACT_PATHS = (
    Path("C:/Program Files/Tesseract-OCR/tesseract.exe"),
    Path("C:/Program Files (x86)/Tesseract-OCR/tesseract.exe"),
)


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
    tesseract_cmd = _resolve_command(
        active_config.tesseract_cmd,
        "Tesseract OCR",
        default_candidates=DEFAULT_TESSERACT_PATHS,
    )
    result = _run(
        [
            tesseract_cmd,
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
    pdftoppm_cmd = _resolve_command(active_config.pdftoppm_cmd, "Poppler pdftoppm")
    tesseract_cmd = _resolve_command(
        active_config.tesseract_cmd,
        "Tesseract OCR",
        default_candidates=DEFAULT_TESSERACT_PATHS,
    )
    resolved_config = OcrConfig(
        tesseract_cmd=tesseract_cmd,
        pdftoppm_cmd=pdftoppm_cmd,
        language=active_config.language,
        dpi=active_config.dpi,
        timeout_seconds=active_config.timeout_seconds,
        max_pdf_pages=active_config.max_pdf_pages,
    )

    with tempfile.TemporaryDirectory(prefix="ccf-ocr-") as temp_dir:
        output_prefix = Path(temp_dir) / "page"
        command = [
            resolved_config.pdftoppm_cmd,
            "-r",
            str(resolved_config.dpi),
            "-png",
        ]
        if resolved_config.max_pdf_pages is not None:
            command.extend(["-f", "1", "-l", str(resolved_config.max_pdf_pages)])
        command.extend([str(path), str(output_prefix)])
        _run(command, timeout_seconds=resolved_config.timeout_seconds)

        page_images = sorted(Path(temp_dir).glob("page-*.png"))
        if not page_images:
            raise OcrError(f"No OCR page images were rendered for {path}")

        page_text = [ocr_image(page_image, resolved_config) for page_image in page_images]
        return "\n\n".join(text for text in page_text if text).strip()


def _resolve_command(command: str, label: str, *, default_candidates: tuple[Path, ...] = ()) -> str:
    if shutil.which(command) is not None:
        return command

    command_path = Path(command)
    if (command_path.is_absolute() or command_path.parent != Path(".")) and command_path.exists():
        return str(command_path)

    for candidate in default_candidates:
        if candidate.exists():
            return str(candidate)

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
