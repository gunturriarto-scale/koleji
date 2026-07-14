import dotenv from 'dotenv';
import { z } from 'zod';

dotenv.config();

const envSchema = z.object({
  SPREADSHEET_ID: z.string().min(1),
  APIFY_API_TOKEN: z.string().min(1),
  GOOGLE_SERVICE_ACCOUNT_PATH: z.string().default('./keys/service-account.json'),
  BATCH_SIZE: z.coerce.number().positive().max(500).default(400),
  APIFY_POLL_INTERVAL_MS: z.coerce.number().positive().default(5000),
  APIFY_POLL_TIMEOUT_MS: z.coerce.number().positive().default(600000),
  LOG_LEVEL: z.enum(['trace', 'debug', 'info', 'warn', 'error', 'fatal']).default('info'),
});

export type Config = z.infer<typeof envSchema>;

export const config = envSchema.parse(process.env);

export const CATEGORIES = [
  'Bodycare',
  'Skincare',
  'Mattedorable',
  'Next Level',
  'NCO',
  'FYNE',
  'Eomma',
] as const;

export const PLATFORMS_TO_SCRAPE = ['TT', 'YC'] as const;

export function getTargetSheetNames(): string[] {
  const sheets: string[] = [];
  for (const cat of CATEGORIES) {
    for (const plat of PLATFORMS_TO_SCRAPE) {
      sheets.push(`[${plat}] ${cat}`);
    }
  }
  return sheets;
}
