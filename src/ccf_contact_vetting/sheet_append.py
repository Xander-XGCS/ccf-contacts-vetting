from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .drive_text_extraction import ExtractedSheetRows


TAB_NAMES = {
    "people": "People",
    "companies": "Companies",
    "deals": "Deals & Projects",
    "evidence_sources": "Evidence Sources",
    "research_queue": "Research Queue",
}


@dataclass(frozen=True)
class AppendTarget:
    tab_name: str
    rows: tuple[list[str], ...]


def append_targets(rows: ExtractedSheetRows) -> tuple[AppendTarget, ...]:
    targets = (
        AppendTarget(TAB_NAMES["people"], rows.people),
        AppendTarget(TAB_NAMES["companies"], rows.companies),
        AppendTarget(TAB_NAMES["deals"], rows.deals),
        AppendTarget(TAB_NAMES["evidence_sources"], rows.evidence_sources),
        AppendTarget(TAB_NAMES["research_queue"], rows.research_queue),
    )
    return tuple(target for target in targets if target.rows)


def append_cells_requests(
    rows_by_tab: dict[str, list[list[Any]]],
    sheet_ids_by_title: dict[str, int],
) -> list[dict[str, Any]]:
    requests: list[dict[str, Any]] = []
    for tab_name, rows in rows_by_tab.items():
        if not rows:
            continue
        if tab_name not in sheet_ids_by_title:
            raise KeyError(f"Missing sheetId for tab: {tab_name}")
        requests.append(
            {
                "appendCells": {
                    "sheetId": sheet_ids_by_title[tab_name],
                    "rows": [_row_data(row) for row in rows],
                    "fields": "userEnteredValue",
                }
            }
        )
    return requests


def collect_rows_by_tab(row_bundles: list[ExtractedSheetRows]) -> dict[str, list[list[Any]]]:
    rows_by_tab: dict[str, list[list[Any]]] = {tab_name: [] for tab_name in TAB_NAMES.values()}
    for bundle in row_bundles:
        for target in append_targets(bundle):
            rows_by_tab[target.tab_name].extend(target.rows)
    return {tab_name: rows for tab_name, rows in rows_by_tab.items() if rows}


def sheet_ids_from_metadata(metadata: dict[str, Any]) -> dict[str, int]:
    sheet_ids: dict[str, int] = {}
    for sheet in metadata.get("sheets", []):
        properties = sheet.get("properties", {})
        title = properties.get("title")
        sheet_id = properties.get("sheetId")
        if isinstance(title, str) and isinstance(sheet_id, int):
            sheet_ids[title] = sheet_id
    return sheet_ids


def _row_data(row: list[Any]) -> dict[str, Any]:
    return {"values": [_cell_data(value) for value in row]}


def _cell_data(value: Any) -> dict[str, Any]:
    if isinstance(value, bool):
        return {"userEnteredValue": {"boolValue": value}}
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return {"userEnteredValue": {"numberValue": value}}
    return {"userEnteredValue": {"stringValue": "" if value is None else str(value)}}
