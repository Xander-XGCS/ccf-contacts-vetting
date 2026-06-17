from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from .drive_manifest import (
    diff_manifests,
    extract_drive_id,
    load_manifest,
    propose_structure_suggestions,
    write_changes_csv,
    write_json_dataclasses,
    write_suggestions_csv,
)
from .entity_extraction import TextSource, extract_text_entities
from .local_inventory import inventory_path, write_inventory_csv
from .ocr import OcrConfig, ocr_file
from .workbook_schema import schema_as_json, schema_as_markdown


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "schema":
        content = schema_as_json() if args.format == "json" else schema_as_markdown()
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(content, encoding="utf-8")
        else:
            sys.stdout.write(content)
        return 0

    if args.command == "inventory-local":
        records = inventory_path(args.root)
        write_inventory_csv(records, args.output)
        print(f"Wrote {len(records)} file records to {args.output}")
        return 0

    if args.command == "drive-id":
        print(extract_drive_id(args.url))
        return 0

    if args.command == "diff-manifests":
        previous = load_manifest(args.previous)
        current = load_manifest(args.current)
        changes = diff_manifests(previous, current)
        if args.format == "json":
            write_json_dataclasses(changes, args.output)
        else:
            write_changes_csv(changes, args.output)
        print(f"Wrote {len(changes)} manifest changes to {args.output}")
        return 0

    if args.command == "structure-suggestions":
        items = load_manifest(args.manifest)
        suggestions = propose_structure_suggestions(items, args.root_id)
        if args.format == "json":
            write_json_dataclasses(suggestions, args.output)
        else:
            write_suggestions_csv(suggestions, args.output)
        print(f"Wrote {len(suggestions)} structure suggestions to {args.output}")
        return 0

    if args.command == "extract-text":
        text = args.input.read_text(encoding="utf-8")
        source = TextSource(source_id=args.source_id, title=args.title or args.input.stem, url=args.url or "")
        result = extract_text_entities(text, source)
        content = json.dumps(asdict(result), indent=2)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(content, encoding="utf-8")
        else:
            sys.stdout.write(content)
        return 0

    if args.command == "ocr-file":
        text = ocr_file(
            args.input,
            args.mime_type,
            OcrConfig(
                tesseract_cmd=args.tesseract_cmd,
                pdftoppm_cmd=args.pdftoppm_cmd,
                language=args.language,
                dpi=args.dpi,
                max_pdf_pages=args.max_pdf_pages,
            ),
        )
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(text, encoding="utf-8")
        else:
            sys.stdout.write(text)
        return 0

    parser.print_help()
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ccf-vetting",
        description="CCF contacts vetting automation utilities.",
    )
    subparsers = parser.add_subparsers(dest="command")

    schema = subparsers.add_parser("schema", help="Render the workbook schema.")
    schema.add_argument("--format", choices=("markdown", "json"), default="markdown")
    schema.add_argument("--output", type=Path)

    inventory = subparsers.add_parser("inventory-local", help="Inventory a local or synced Drive folder.")
    inventory.add_argument("--root", type=Path, required=True, help="Folder to inventory.")
    inventory.add_argument("--output", type=Path, required=True, help="CSV output path.")

    drive_id = subparsers.add_parser("drive-id", help="Extract a Google Drive file or folder ID from a URL.")
    drive_id.add_argument("--url", required=True, help="Google Drive URL or raw ID.")

    diff = subparsers.add_parser("diff-manifests", help="Compare two Drive manifest JSON files.")
    diff.add_argument("--previous", type=Path, required=True)
    diff.add_argument("--current", type=Path, required=True)
    diff.add_argument("--output", type=Path, required=True)
    diff.add_argument("--format", choices=("csv", "json"), default="csv")

    suggestions = subparsers.add_parser("structure-suggestions", help="Create approval-gated Drive structure suggestions.")
    suggestions.add_argument("--manifest", type=Path, required=True)
    suggestions.add_argument("--root-id", required=True)
    suggestions.add_argument("--output", type=Path, required=True)
    suggestions.add_argument("--format", choices=("csv", "json"), default="csv")

    extract = subparsers.add_parser("extract-text", help="Extract entity candidates from a UTF-8 text file.")
    extract.add_argument("--input", type=Path, required=True)
    extract.add_argument("--source-id", required=True)
    extract.add_argument("--title")
    extract.add_argument("--url")
    extract.add_argument("--output", type=Path)

    ocr = subparsers.add_parser("ocr-file", help="OCR a local PDF or image file into UTF-8 text.")
    ocr.add_argument("--input", type=Path, required=True)
    ocr.add_argument("--mime-type", required=True, help="MIME type, e.g. application/pdf or image/png.")
    ocr.add_argument("--output", type=Path)
    ocr.add_argument("--tesseract-cmd", default="tesseract")
    ocr.add_argument("--pdftoppm-cmd", default="pdftoppm")
    ocr.add_argument("--language", default="eng")
    ocr.add_argument("--dpi", type=int, default=300)
    ocr.add_argument("--max-pdf-pages", type=int, default=10)

    return parser


if __name__ == "__main__":
    raise SystemExit(main())
