import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch

from ccf_contact_vetting.ocr import OcrConfig, OcrError, OcrUnavailableError, ocr_file, ocr_image


class OcrTests(unittest.TestCase):
    def test_ocr_image_uses_tesseract_stdout(self) -> None:
        config = OcrConfig(tesseract_cmd="tesseract-test", language="eng", timeout_seconds=12)
        completed = subprocess.CompletedProcess(
            args=["tesseract-test"],
            returncode=0,
            stdout="Anslem N. Gbemudu\n",
            stderr="",
        )

        with patch("ccf_contact_vetting.ocr.shutil.which", return_value="/bin/tesseract-test"):
            with patch("ccf_contact_vetting.ocr.subprocess.run", return_value=completed) as run:
                text = ocr_image(Path("seller.png"), config)

        self.assertEqual(text, "Anslem N. Gbemudu")
        run.assert_called_once_with(
            ["tesseract-test", "seller.png", "stdout", "-l", "eng"],
            check=True,
            capture_output=True,
            text=True,
            timeout=12,
        )

    def test_missing_tesseract_raises_unavailable(self) -> None:
        with patch("ccf_contact_vetting.ocr.shutil.which", return_value=None):
            with patch("ccf_contact_vetting.ocr.Path.exists", return_value=False):
                with self.assertRaises(OcrUnavailableError):
                    ocr_image(Path("seller.png"))

    def test_default_tesseract_uses_common_windows_install_path(self) -> None:
        completed = subprocess.CompletedProcess(
            args=["tesseract"],
            returncode=0,
            stdout="Anslem N. Gbemudu\n",
            stderr="",
        )

        with patch("ccf_contact_vetting.ocr.shutil.which", return_value=None):
            with patch("ccf_contact_vetting.ocr.Path.exists", return_value=True):
                with patch("ccf_contact_vetting.ocr.subprocess.run", return_value=completed) as run:
                    text = ocr_image(Path("seller.png"))

        self.assertEqual(text, "Anslem N. Gbemudu")
        self.assertEqual(run.call_args.args[0][0], "C:\\Program Files\\Tesseract-OCR\\tesseract.exe")

    def test_unsupported_mime_type_raises_error(self) -> None:
        with self.assertRaises(OcrError):
            ocr_file(Path("seller.xlsx"), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


if __name__ == "__main__":
    unittest.main()
