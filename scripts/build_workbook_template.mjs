import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(scriptDir, "..");
const schemaPath = process.argv[2] ? path.resolve(process.argv[2]) : path.join(repoRoot, "schemas", "workbook_schema.json");
const outputDir = process.argv[3] ? path.resolve(process.argv[3]) : path.join(repoRoot, "outputs", "workbook-template");
const workbookTitle = process.argv[4] || "CCF Relationship Intelligence";

await fs.mkdir(outputDir, { recursive: true });

const schema = JSON.parse(await fs.readFile(schemaPath, "utf8"));
const workbook = Workbook.create();

const commonWidths = new Map([
  ["ID", 145],
  ["Metric", 220],
  ["Name", 190],
  ["Status", 125],
  ["Notes", 240],
  ["Reason", 260],
  ["Why", 260],
  ["Source Links", 260],
  ["Evidence Links", 260],
  ["Current Path", 260],
  ["Proposed Path", 260],
  ["Drive URL", 250],
  ["URL Or Drive Link", 250],
  ["Contact Folder", 220],
  ["Company Folder", 220],
  ["Research Memo", 220],
  ["Human Review Notes", 260],
  ["Relationship Summary", 260],
  ["Findings Summary", 280],
  ["Extracted Facts", 280],
  ["Next Action", 220],
]);

function widthFor(header) {
  for (const [needle, width] of commonWidths.entries()) {
    if (header.includes(needle)) return width;
  }
  return Math.max(110, Math.min(220, header.length * 9 + 30));
}

for (const tab of schema.tabs) {
  const sheet = workbook.worksheets.add(tab.name);
  sheet.showGridLines = true;

  const headers = tab.columns.map((column) => column.name);
  const headerRange = sheet.getRangeByIndexes(0, 0, 1, headers.length);
  headerRange.values = [headers];
  headerRange.format = {
    fill: "#F3F4F6",
    font: { bold: true, color: "#111827" },
    borders: { preset: "all", style: "thin", color: "#D1D5DB" },
    wrapText: true,
  };

  sheet.freezePanes.freezeRows(1);

  for (let col = 0; col < headers.length; col += 1) {
    const colRange = sheet.getRangeByIndexes(0, col, 120, 1);
    colRange.format.columnWidthPx = widthFor(headers[col]);
  }

  const dataRange = sheet.getRangeByIndexes(1, 0, 119, headers.length);
  dataRange.format = {
    borders: { preset: "inside", style: "thin", color: "#E5E7EB" },
    wrapText: true,
  };

  if (tab.name === "Dashboard") {
    sheet.getRangeByIndexes(1, 0, 6, headers.length).values = [
      ["Root Folder ID", "", "", "", ""],
      ["Last Sync Status", "", "", "", ""],
      ["Items Scanned", "", "", "", ""],
      ["Pending Structure Suggestions", "", "", "", ""],
      ["Research Queue Pending", "", "", "", ""],
      ["Human Review Required", "", "", "", ""],
    ];
  }
}

const overview = await workbook.inspect({ kind: "sheet", include: "id,name", maxChars: 4000 });
console.log(overview.ndjson);

for (const tab of schema.tabs) {
  const preview = await workbook.render({ sheetName: tab.name, autoCrop: "all", scale: 1, format: "png" });
  const bytes = new Uint8Array(await preview.arrayBuffer());
  const previewName = `${tab.name.replace(/[^A-Za-z0-9]+/g, "_")}.png`;
  await fs.writeFile(path.join(outputDir, previewName), bytes);
}

const errors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 300 },
  summary: "formula error scan",
  maxChars: 4000,
});
console.log(errors.ndjson);

const xlsx = await SpreadsheetFile.exportXlsx(workbook);
const outputPath = path.join(outputDir, `${workbookTitle}.xlsx`);
await xlsx.save(outputPath);

console.log(JSON.stringify({ outputPath }, null, 2));
