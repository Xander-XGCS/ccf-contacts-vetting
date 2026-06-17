const MENU_NAME = 'CCF Research';
const STATUS_REQUESTED = 'Requested';

function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu(MENU_NAME)
    .addItem('Request research for selected row', 'requestResearchForSelectedRow')
    .addItem('Request queued research', 'requestQueuedResearch')
    .addToUi();
}

function requestResearchForSelectedRow() {
  const sheet = SpreadsheetApp.getActiveSheet();
  const range = sheet.getActiveRange();
  if (!range) {
    SpreadsheetApp.getUi().alert('Select a row in Research Queue, People, Companies, or Vetting Research first.');
    return;
  }

  const row = range.getRow();
  const payload = payloadForRow_(sheet, row);
  if (!payload) {
    SpreadsheetApp.getUi().alert('This tab is not configured for research requests.');
    return;
  }

  postResearchRequest_({
    trigger: 'selected_row',
    rows: [payload],
  });
  SpreadsheetApp.getUi().alert('Research request sent.');
}

function requestQueuedResearch() {
  const spreadsheet = SpreadsheetApp.getActive();
  const sheet = spreadsheet.getSheetByName('Research Queue');
  if (!sheet) {
    SpreadsheetApp.getUi().alert('Research Queue tab was not found.');
    return;
  }

  const values = sheet.getDataRange().getValues();
  if (values.length < 2) {
    SpreadsheetApp.getUi().alert('Research Queue has no rows.');
    return;
  }

  const headers = values[0];
  const statusIndex = headers.indexOf('Status');
  const rows = [];
  for (let index = 1; index < values.length; index += 1) {
    const status = String(values[index][statusIndex] || '').trim();
    if (status === 'Queued' || status === STATUS_REQUESTED) {
      rows.push(rowObject_(headers, values[index], index + 1, sheet.getName()));
    }
  }

  if (!rows.length) {
    SpreadsheetApp.getUi().alert('No queued research rows found.');
    return;
  }

  postResearchRequest_({
    trigger: 'queued_rows',
    rows,
  });
  SpreadsheetApp.getUi().alert(`Research request sent for ${rows.length} row(s).`);
}

function payloadForRow_(sheet, row) {
  const supportedTabs = ['Research Queue', 'People', 'Companies', 'Vetting Research'];
  if (!supportedTabs.includes(sheet.getName())) {
    return null;
  }

  const width = sheet.getLastColumn();
  const headers = sheet.getRange(1, 1, 1, width).getValues()[0];
  const values = sheet.getRange(row, 1, 1, width).getValues()[0];
  return rowObject_(headers, values, row, sheet.getName());
}

function rowObject_(headers, values, rowNumber, sheetName) {
  const data = {};
  headers.forEach((header, index) => {
    if (header) {
      data[String(header)] = values[index];
    }
  });
  return {
    spreadsheetId: SpreadsheetApp.getActive().getId(),
    sheetName,
    rowNumber,
    data,
    requestedAt: new Date().toISOString(),
    requestedBy: Session.getActiveUser().getEmail(),
  };
}

function postResearchRequest_(payload) {
  const properties = PropertiesService.getScriptProperties();
  const webhookUrl = properties.getProperty('CCF_RESEARCH_WEBHOOK_URL');
  const webhookSecret = properties.getProperty('CCF_RESEARCH_WEBHOOK_SECRET');

  if (!webhookUrl) {
    throw new Error('Missing Script Property: CCF_RESEARCH_WEBHOOK_URL');
  }

  const response = UrlFetchApp.fetch(webhookUrl, {
    method: 'post',
    contentType: 'application/json',
    muteHttpExceptions: true,
    headers: webhookSecret ? { Authorization: `Bearer ${webhookSecret}` } : {},
    payload: JSON.stringify(payload),
  });

  const status = response.getResponseCode();
  if (status < 200 || status > 299) {
    throw new Error(`Research webhook failed with HTTP ${status}: ${response.getContentText()}`);
  }
}
