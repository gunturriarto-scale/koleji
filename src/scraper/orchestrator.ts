import { getSheetsClient } from '../sheets/client.js';
import { readAllLinks } from '../sheets/reader.js';
import { writeResults } from '../sheets/writer.js';
import { writeLogEntry } from '../sheets/logger.js';
import { createBatches } from '../apify/batching.js';
import { runTikTokBatch } from '../apify/client.js';
import { mapResultsToUpdates } from './mapper.js';
import { logger } from '../utils/logger.js';

export interface ScrapeSummary {
  sheetsProcessed: number;
  totalUrls: number;
  batchesCreated: number;
  batchesSucceeded: number;
  batchesFailed: number;
  resultsWritten: number;
  errors: string[];
}

const MAX_BATCH_ATTEMPTS = 2;
const RETRY_DELAY_MS = 5000;

/**
 * Main scrape cycle:
 * 1. Read all [TT] and [YC] sheets → extract links
 * 2. Create URL batches (50/batch)
 * 3. For each batch: scrape via Apify (retrying once on failure),
 *    then map + write its results back to sheets immediately.
 *    This way a later batch failing (or the job timing out) doesn't
 *    discard results already earned by earlier batches.
 */
export async function runScrapeCycle(): Promise<ScrapeSummary> {
  const summary: ScrapeSummary = {
    sheetsProcessed: 0,
    totalUrls: 0,
    batchesCreated: 0,
    batchesSucceeded: 0,
    batchesFailed: 0,
    resultsWritten: 0,
    errors: [],
  };

  logger.info('=== Starting KOL Scrape Cycle ===');

  try {
    // Step 1: Initialize Google Sheets
    const sheets = await getSheetsClient();

    // Step 2: Read all sheet links
    const allLinks = await readAllLinks(sheets);
    summary.totalUrls = allLinks.length;
    summary.sheetsProcessed = [...new Set(allLinks.map((l) => l.sheetName))].length;

    if (allLinks.length === 0) {
      logger.warn('No URLs found to scrape. Exiting cycle.');
      return summary;
    }

    // Step 3: Create batches
    const batches = createBatches(allLinks);
    summary.batchesCreated = batches.length;

    if (batches.length === 0) {
      logger.warn('No valid batches created. Exiting cycle.');
      return summary;
    }

    // Step 4: Scrape each batch sequentially, writing results as soon as each batch is done
    for (let i = 0; i < batches.length; i++) {
      const batch = batches[i];
      let results: Awaited<ReturnType<typeof runTikTokBatch>> | null = null;
      let lastErrMsg = '';

      for (let attempt = 1; attempt <= MAX_BATCH_ATTEMPTS; attempt++) {
        try {
          logger.info(
            { batch: i + 1, total: batches.length, urls: batch.urls.length, attempt },
            'Processing batch'
          );

          results = await runTikTokBatch(batch.urls);
          break;
        } catch (err) {
          lastErrMsg = err instanceof Error ? err.message : String(err);
          logger.warn({ err, batch: i + 1, attempt }, 'Batch attempt failed');
          if (attempt < MAX_BATCH_ATTEMPTS) {
            await delay(RETRY_DELAY_MS);
          }
        }
      }

      if (results) {
        summary.batchesSucceeded++;

        const updates = mapResultsToUpdates(batch.linkRefs, results);
        await writeResults(sheets, updates);
        summary.resultsWritten += Object.values(updates).reduce(
          (sum, cells) => sum + cells.length,
          0
        );
      } else {
        summary.batchesFailed++;
        summary.errors.push(`Batch ${i + 1}: ${lastErrMsg}`);
        logger.error({ batch: i + 1, err: lastErrMsg }, 'Batch failed after retries');
      }

      // Small delay between batches to be nice to API
      if (i < batches.length - 1) {
        await delay(2000);
      }
    }

    logger.info(
      {
        ...summary,
      },
      '=== KOL Scrape Cycle Complete ==='
    );

    // Write summary to log sheet
    await writeLogEntry(sheets, summary);
  } catch (err) {
    const errMsg = err instanceof Error ? err.message : String(err);
    summary.errors.push(`Fatal: ${errMsg}`);
    logger.error({ err }, 'Scrape cycle failed with fatal error');
  }

  return summary;
}

function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
