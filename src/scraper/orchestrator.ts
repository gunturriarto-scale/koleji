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

/**
 * Main scrape cycle:
 * 1. Read all [TT] and [YC] sheets → extract links
 * 2. Create URL batches (50/batch)
 * 3. Scrape each batch via Apify
 * 4. Map results → sheet updates
 * 5. Write results back to sheets
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

    // Step 4: Scrape each batch sequentially
    const allResults: Array<{ linkRefs: typeof allLinks; results: any[] }> = [];

    for (let i = 0; i < batches.length; i++) {
      const batch = batches[i];

      try {
        logger.info(
          { batch: i + 1, total: batches.length, urls: batch.urls.length },
          'Processing batch'
        );

        const results = await runTikTokBatch(batch.urls);
        allResults.push({ linkRefs: batch.linkRefs, results });
        summary.batchesSucceeded++;

        // Small delay between batches to be nice to API
        if (i < batches.length - 1) {
          await delay(2000);
        }
      } catch (err) {
        summary.batchesFailed++;
        const errMsg = err instanceof Error ? err.message : String(err);
        summary.errors.push(`Batch ${i + 1}: ${errMsg}`);
        logger.error({ err, batch: i + 1 }, 'Batch failed');
      }
    }

    // Step 5: Map & write results
    const allLinkRefs = allResults.flatMap((r) => r.linkRefs);
    const allApiResults = allResults.flatMap((r) => r.results);

    const updates = mapResultsToUpdates(allLinkRefs, allApiResults);
    await writeResults(sheets, updates);

    summary.resultsWritten = Object.values(updates).reduce(
      (sum, cells) => sum + cells.length,
      0
    );

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
