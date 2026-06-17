# OCR Fallback

Some Drive files expose no readable text even though they contain important scanned information. Seller CIS files, passports, signatures, and scanned PDFs should therefore go through OCR when native text extraction returns empty.

## Runtime Behavior

The parser now supports OCR in two ways:

1. If a Drive worker implements `fetch_ocr_text(record)`, `parse_drive_records` will call it when:
   - a supported text file returns empty text, or
   - an OCR-only image file is encountered.
2. `DriveOcrTextFetcher` can be used by that worker to download the raw Drive file into a local cache and run the same OCR pipeline:

```python
from pathlib import Path

from ccf_contact_vetting.drive_ocr_fetcher import DriveOcrTextFetcher
from ccf_contact_vetting.ocr import OcrConfig

ocr_fetcher = DriveOcrTextFetcher(
    downloader=google_drive_raw_downloader,
    cache_dir=Path("outputs/ocr-cache"),
    ocr_config=OcrConfig(max_pdf_pages=10),
)
```

The downloader is the runtime-specific piece. In Codex it can call the Google Drive connector's raw-file fetch path; in a hosted worker it can use a service-account Drive API download.

3. For local files, the CLI can OCR PDFs and images using Tesseract plus Poppler:

```powershell
$env:PYTHONPATH="src"; python -m ccf_contact_vetting.cli ocr-file --input "Seller CIS.pdf" --mime-type application/pdf --output outputs\seller-cis.txt
```

## Required Local Tools

Install these on the worker host when local OCR is needed:

- Tesseract OCR, available as `tesseract`
- Poppler, available as `pdftoppm`

On Windows, the app will also look for Tesseract in the common install locations:

- `C:\Program Files\Tesseract-OCR\tesseract.exe`
- `C:\Program Files (x86)\Tesseract-OCR\tesseract.exe`

The tool names can be overridden:

```powershell
$env:PYTHONPATH="src"; python -m ccf_contact_vetting.cli ocr-file `
  --input "Seller CIS.pdf" `
  --mime-type application/pdf `
  --tesseract-cmd "C:\path\to\tesseract.exe" `
  --pdftoppm-cmd "C:\path\to\pdftoppm.exe" `
  --output outputs\seller-cis.txt
```

## Sheet Handling

When OCR succeeds, parsed rows should use the same entity extraction and evidence flow as native text. When OCR fails or returns empty text, mark the file `Needs Review` in `File Inventory` and add a note such as `OCR/manual review required`.

For AU, `Seller CIS.pdf` should be re-run through OCR so Anslem-related identity and company details can be extracted into `People`, `Companies`, `Relationships`, `Evidence Sources`, and the relevant profile summaries.
