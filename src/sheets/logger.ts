import { sheets_v4 } from 'googleapis';
import { config } from '../config.js';
import { logger } from '../utils/logger.js';
import type { ScrapeSummary } from '../scraper/orchestrator.js';

const LOG_SHEET = 'log';

/**
 * Write a summary row to the `log` sheet after each scrape cycle.
 */
export async function writeLogEntry(
  sheets: sheets_v4.Sheets,
  summary: ScrapeSummary
): Promise<void> {
  const now = new Date();
  const timestamp = now.toLocaleString('en-CA', {
    timeZone: 'Asia/Jakarta',
    hour12: false,
  }).replace(',', '');

  const values = [[
    timestamp,                          // A - Waktu selesai
    summary.totalUrls,                  // B - Total link scraped
    summary.batchesCreated,             // C - Total batch
    summary.batchesSucceeded,           // D - Batch sukses
    summary.batchesFailed,              // E - Batch gagal
    summary.resultsWritten,             // F - Row diupdate
    summary.errors.length > 0 ? summary.errors.join('; ') : 'OK', // G - Error
  ]];

  try {
    await sheets.spreadsheets.values.append({
      spreadsheetId: config.SPREADSHEET_ID,
      range: `${LOG_SHEET}!A:G`,
      valueInputOption: 'USER_ENTERED',
      insertDataOption: 'INSERT_ROWS',
      requestBody: { values },
    });
    logger.info({ timestamp, summary }, 'Log entry written to sheet');
  } catch (err) {
    logger.error({ err }, 'Failed to write log entry to sheet');
  }
}
