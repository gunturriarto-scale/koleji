import { sheets_v4 } from 'googleapis';
import { config } from '../config.js';
import { logger } from '../utils/logger.js';

export interface CellUpdate {
  rowNumber: number;
  values: (string | number)[];
}

export interface SheetUpdates {
  [sheetName: string]: CellUpdate[];
}

/**
 * Write scrape results back to sheets.
 * For each sheet, batch-update columns I-N (indices 8-13, 0-based).
 * Column O (Date Posting) is entered manually and must never be overwritten here.
 *
 * @param sheets - Google Sheets client
 * @param updates - Map of sheetName → array of { rowNumber, values }
 */
export async function writeResults(
  sheets: sheets_v4.Sheets,
  updates: SheetUpdates
): Promise<void> {
  const sheetNames = Object.keys(updates);

  for (const sheetName of sheetNames) {
    const cells = updates[sheetName];
    if (cells.length === 0) continue;

    // Sort by row number ascending
    cells.sort((a, b) => a.rowNumber - b.rowNumber);

    const requests = cells.map((cell) => ({
      range: `${sheetName}!I${cell.rowNumber}:N${cell.rowNumber}`,
      values: [cell.values],
    }));

    try {
      await sheets.spreadsheets.values.batchUpdate({
        spreadsheetId: config.SPREADSHEET_ID,
        requestBody: {
          valueInputOption: 'USER_ENTERED',
          data: requests,
        },
      });
      logger.debug({ sheetName, updatedRows: cells.length }, 'Wrote results to sheet');
    } catch (err) {
      logger.error({ err, sheetName }, 'Failed to write to sheet');
    }
  }
}
