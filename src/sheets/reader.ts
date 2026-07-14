import { sheets_v4 } from 'googleapis';
import { config, getTargetSheetNames } from '../config.js';
import { logger } from '../utils/logger.js';

export interface SheetLink {
  sheetName: string;
  rowNumber: number; // 1-based (row 1 = header)
  url: string;
}

export interface SheetRow {
  rowNumber: number;
  values: string[];
}

export async function readAllLinks(sheets: sheets_v4.Sheets): Promise<SheetLink[]> {
  const targetSheets = getTargetSheetNames();
  const allLinks: SheetLink[] = [];

  for (const sheetName of targetSheets) {
    const links = await readSheetLinks(sheets, sheetName);
    allLinks.push(...links);
  }

  logger.info({ totalLinks: allLinks.length }, 'Finished reading all sheet links');
  return allLinks;
}

/**
 * Try to parse a date string from the sheet into a Date object.
 * Handles multiple formats found in the sheets:
 *   - "1/1/2026" (M/D/YYYY)
 *   - "1-Jan-2026" (DD-Mon-YYYY)
 *   - "21 May 2026" (DD Mon YYYY)
 */
function parseDateCell(value: string | undefined): Date | null {
  if (!value) return null;
  const trimmed = value.trim();
  if (!trimmed) return null;

  // Try M/D/YYYY (e.g. "1/1/2026", "5/28/2026")
  const slashMatch = trimmed.match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})$/);
  if (slashMatch) {
    return new Date(parseInt(slashMatch[3]), parseInt(slashMatch[1]) - 1, parseInt(slashMatch[2]));
  }

  // Try "DD-Mon-YYYY" (e.g. "1-Jan-2026", "4-Apr-2026")
  const dashMatch = trimmed.match(/^(\d{1,2})-(\w{3})-(\d{4})$/);
  if (dashMatch) {
    const months: Record<string, number> = {
      jan: 0, feb: 1, mar: 2, apr: 3, may: 4, jun: 5,
      jul: 6, aug: 7, sep: 8, oct: 9, nov: 10, dec: 11,
    };
    const month = months[dashMatch[2].toLowerCase()];
    if (month !== undefined) return new Date(parseInt(dashMatch[3]), month, parseInt(dashMatch[1]));
  }

  // Try "DD Mon YYYY" (e.g. "21 May 2026", "18 May 2026")
  const spaceMatch = trimmed.match(/^(\d{1,2})\s+(\w{3,4})\s+(\d{4})$/);
  if (spaceMatch) {
    const months: Record<string, number> = {
      jan: 0, january: 0,
      feb: 1, february: 1,
      mar: 2, march: 2,
      apr: 3, april: 3,
      may: 4,
      jun: 5, june: 5,
      jul: 6, july: 6,
      aug: 7, august: 7,
      sep: 8, september: 8,
      oct: 9, october: 9,
      nov: 10, november: 10,
      dec: 11, december: 11,
    };
    const month = months[spaceMatch[2].toLowerCase()];
    if (month !== undefined) return new Date(parseInt(spaceMatch[3]), month, parseInt(spaceMatch[1]));
  }

  return null;
}

/**
 * Read a single sheet, find all rows with non-empty column H (Link Post).
 * Only includes posts from the last 30 days (filtered by column O = Date Posting).
 * Returns { sheetName, rowNumber, url } for each valid row.
 * Skips row 1 (header row — "KOL Mastersheet" title).
 */
async function readSheetLinks(sheets: sheets_v4.Sheets, sheetName: string): Promise<SheetLink[]> {
  try {
    const response = await sheets.spreadsheets.values.get({
      spreadsheetId: config.SPREADSHEET_ID,
      range: `${sheetName}!A:O`,
      valueRenderOption: 'FORMATTED_VALUE',
    });

    const rows = response.data.values;
    if (!rows || rows.length === 0) {
      logger.debug({ sheetName }, 'Sheet is empty');
      return [];
    }

    const links: SheetLink[] = [];
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - 30);
    let skippedByDate = 0;
    let skippedEmptyLink = 0;

    for (let i = 0; i < rows.length; i++) {
      const row = rows[i];
      const rowNumber = i + 1; // 1-based

      // Skip header rows (row 1 has "KOL Mastersheet" title)
      if (rowNumber === 1) continue;

      // Column H = index 7 (Link Post)
      const url = (row[7] !== undefined ? String(row[7]) : '').trim();
      if (!url) {
        skippedEmptyLink++;
        continue;
      }

      // Column O = index 14 (Date Posting)
      // Filter: hanya post dalam 30 hari terakhir
      const dateStr = row[14] !== undefined ? String(row[14]) : '';
      const postDate = parseDateCell(dateStr);

      if (postDate && !isNaN(postDate.getTime())) {
        // Skip if date is absurdly far in future or past (before 2025)
        if (postDate.getFullYear() > 2027 || postDate.getFullYear() < 2025) {
          skippedByDate++;
          continue;
        }
        if (postDate < cutoffDate) {
          skippedByDate++;
          continue;
        }
      } else {
        // No valid date → skip (assume it's old or garbage data)
        skippedByDate++;
        continue;
      }

      links.push({ sheetName, rowNumber, url });
    }

    logger.debug({
      sheetName,
      totalRows: rows.length - 1,
      withLinks: links.length,
      skippedByDate,
      skippedEmptyLink,
    }, 'Read sheet links');
    return links;
  } catch (err) {
    logger.error({ err, sheetName }, 'Failed to read sheet');
    return [];
  }
}
