import { google, sheets_v4 } from 'googleapis';
import path from 'path';
import { config } from '../config.js';
import { logger } from '../utils/logger.js';

let sheetsInstance: sheets_v4.Sheets | null = null;

export async function getSheetsClient(): Promise<sheets_v4.Sheets> {
  if (sheetsInstance) return sheetsInstance;

  const keyFilePath = path.resolve(config.GOOGLE_SERVICE_ACCOUNT_PATH);

  const auth = new google.auth.GoogleAuth({
    keyFile: keyFilePath,
    scopes: ['https://www.googleapis.com/auth/spreadsheets'],
  });

  sheetsInstance = google.sheets({ version: 'v4', auth });
  logger.info('Google Sheets client initialized');
  return sheetsInstance;
}
