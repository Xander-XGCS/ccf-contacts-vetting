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

const TAB_STYLES = {
  "Start Here": { fill: "#00727F" },
  "File Inventory": { fill: "#E6F0FA" },
  Updates: { fill: "#E8F4EA" },
  "Suggested Folder Changes": { fill: "#FFF0CF" },
  People: { fill: "#E6F0FA" },
  Companies: { fill: "#E6F0FA" },
  "Deals & Projects": { fill: "#EFE8FA" },
  Relationships: { fill: "#EEF2F5" },
  "Research Queue": { fill: "#E8F4EA" },
  "Vetting Research": { fill: "#F0E6FA" },
  "Evidence Sources": { fill: "#EEF2F5" },
  "Intro Recommendations": { fill: "#FDEBE4" },
  "Human Review": { fill: "#FBE2E2" },
};

function widthFor(header) {
  for (const [needle, width] of commonWidths.entries()) {
    if (header.includes(needle)) return width;
  }
  return Math.max(110, Math.min(220, header.length * 9 + 30));
}

for (const tab of schema.tabs) {
  const sheet = workbook.worksheets.add(tab.name);
  sheet.showGridLines = true;

  if (tab.name === "Start Here") {
    buildStartHere(sheet);
    continue;
  }

  const headers = tab.columns.map((column) => column.name);
  const headerRange = sheet.getRangeByIndexes(0, 0, 1, headers.length);
  headerRange.values = [headers];
  headerRange.format = {
    fill: TAB_STYLES[tab.name]?.fill || "#F3F4F6",
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

  hideAutomationColumns(sheet, tab.name);
}

function buildStartHere(sheet) {
  sheet.getRange("A1:F1").merge();
  sheet.getRange("A2:F2").merge();
  sheet.getRange("A4:F4").merge();
  sheet.getRange("A13:F13").merge();

  sheet.getRange("A1:F27").values = [
    ["CCF Relationship Intelligence", "", "", "", "", ""],
    ["A plain-English view of people, companies, deals, evidence, research, and recommended introductions.", "", "", "", "", ""],
    ["", "", "", "", "", ""],
    ["Current snapshot", "", "", "", "", ""],
    ["Metric", "Value", "What it means", "Next action", "Owner", "Link"],
    [
      "Folder connected",
      "Complete Capital Funding",
      "Main Drive folder this workbook watches",
      "Crawler will scan this folder recursively",
      "",
      "https://drive.google.com/drive/folders/1dDJrpLWnSLKoTSKEERInWW9iIp3Af0k1",
    ],
    ["Last update", "Not scanned yet", "Latest crawler run status", "Run a scan when new files are added", "", ""],
    ["Files tracked", 0, "Files and folders seen by the crawler", "Review the File Inventory tab after scans", "", ""],
    ["Pending folder suggestions", 0, "AI-proposed cleanup items awaiting approval", "Approve or reject before anything is moved", "", ""],
    ["Research queue", 0, "People or companies waiting for research", "Prioritize high-value or urgent items", "", ""],
    ["Needs human review", 0, "Items that should not be treated as final yet", "Open Human Review before outreach decisions", "", ""],
    ["", "", "", "", "", ""],
    ["Tab guide", "", "", "", "", ""],
    ["Tab", "Use it for", "Who uses it", "Notes", "", ""],
    ["People", "Contacts, roles, risk level, confidence, research memo, and next action.", "Anyone reviewing relationships", "Start here when asking: who is this person?", "", ""],
    ["Companies", "Company profiles, principals, related people, related deals, and evidence.", "Deal team and research reviewers", "Use with People and Deals & Projects.", "", ""],
    ["Deals & Projects", "Deal/project status, parties, missing info, priority, owner, and next action.", "Operators and originators", "This becomes the deal map.", "", ""],
    ["Intro Recommendations", "Who should talk to whom, why, mutual path, suggested angle, and status.", "Outreach owner", "Treat suggestions as drafts until approved.", "", ""],
    ["Research Queue", "Research tasks for people and companies, priority, status, findings, and review flag.", "Research agent and reviewer", "This drives agentic internet research.", "", ""],
    ["Vetting Research", "Detailed credibility scoring, evidence, red flags, open questions, and reviewer status.", "Research reviewer", "People shows the summary score; this tab holds the reasoning.", "", ""],
    ["Suggested Folder Changes", "AI suggestions for folder cleanup, renames, and moves.", "Xander / approver", "Nothing is applied until approved.", "", ""],
    ["File Inventory", "Every Drive file/folder seen by the crawler, current path, status, and links.", "System and reviewers", "Useful for audit and troubleshooting.", "", ""],
    ["Evidence Sources", "Drive files and web sources used to support facts.", "Reviewer", "Every important claim should point here.", "", ""],
    ["Human Review", "Approval log for uncertain identity matches, risk flags, and sensitive decisions.", "Reviewer", "Keeps the agent honest.", "", ""],
    ["Updates", "Crawler run history and counts of new/changed/removed files.", "System and reviewer", "Check this when a refresh seems off.", "", ""],
    ["Relationships", "Evidence-backed links between people, companies, and deals.", "System and advanced reviewers", "This powers the relationship graph.", "", ""],
    ["", "", "", "", "", ""],
  ];

  sheet.getRange("A1:F1").format = {
    fill: "#00727F",
    font: { bold: true, color: "#FFFFFF", size: 16 },
    verticalAlignment: "middle",
  };
  sheet.getRange("A2:F2").format = {
    fill: "#E6F7F7",
    font: { color: "#24313D" },
    wrapText: true,
  };
  sheet.getRange("A4:F4").format = sectionFormat();
  sheet.getRange("A13:F13").format = sectionFormat();
  sheet.getRange("A5:F5").format = headerFormat();
  sheet.getRange("A14:D14").format = headerFormat();
  sheet.getRange("A6:F11").format = bodyFormat();
  sheet.getRange("A15:D26").format = bodyFormat();

  const widths = [210, 155, 260, 270, 120, 260];
  for (let col = 0; col < widths.length; col += 1) {
    sheet.getRangeByIndexes(0, col, 80, 1).format.columnWidthPx = widths[col];
  }
}

function sectionFormat() {
  return {
    fill: "#214F6B",
    font: { bold: true, color: "#FFFFFF" },
    verticalAlignment: "middle",
  };
}

function headerFormat() {
  return {
    fill: "#EEF2F5",
    font: { bold: true, color: "#1B1F24" },
    wrapText: true,
    verticalAlignment: "middle",
  };
}

function bodyFormat() {
  return {
    borders: { preset: "inside", style: "thin", color: "#E3E7EB" },
    wrapText: true,
    verticalAlignment: "top",
  };
}

function hideAutomationColumns(sheet, tabName) {
  const indexes = {
    "File Inventory": [0, 5, 12],
    Updates: [0, 2],
    "Suggested Folder Changes": [0, 2],
    People: [0],
    Companies: [0],
    "Deals & Projects": [0],
    Relationships: [0],
    "Research Queue": [0],
    "Vetting Research": [0, 2],
    "Evidence Sources": [0],
    "Intro Recommendations": [0],
    "Human Review": [0],
  }[tabName] || [];
  for (const colIndex of indexes) {
    sheet.getRangeByIndexes(0, colIndex, 120, 1).format.columnWidthPx = 24;
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
