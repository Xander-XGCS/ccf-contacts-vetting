from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .local_inventory import inventory_path, write_inventory_csv
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

    return parser


if __name__ == "__main__":
    raise SystemExit(main())

