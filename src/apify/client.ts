import { config } from '../config.js';
import { logger } from '../utils/logger.js';

export interface ApifyTikTokResult {
  url: string;
  playCount: number;
  diggCount: number;
  shareCount: number;
  commentCount: number;
  collectCount: number;
}

/**
 * Run the Apify TikTok scraper actor with a batch of post URLs.
 * Polls until completion, then fetches results from dataset.
 */
export async function runTikTokBatch(urls: string[]): Promise<ApifyTikTokResult[]> {
  const actorId = 'clockworks~tiktok-scraper';
  const baseUrl = 'https://api.apify.com/v2';
  const token = config.APIFY_API_TOKEN;

  logger.info({ batchSize: urls.length }, 'Starting Apify TikTok scrape batch');

  // Step 1: Run the actor
  const runInput = {
    postURLs: urls,
    resultsPerPage: 1,
    scrapeRelatedVideos: false,
    scrapeAdditionalAuthorMeta: false,
    commentsPerPost: 0,
    topLevelCommentsPerPost: 0,
    maxRepliesPerComment: 0,
    shouldDownloadVideos: false,
    shouldDownloadCovers: false,
    proxyCountryCode: 'None',
  };

  const runResponse = await fetch(
    `${baseUrl}/acts/${actorId}/runs?token=${token}`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(runInput),
    }
  );

  if (!runResponse.ok) {
    const errBody = await runResponse.text();
    throw new Error(`Apify run failed: ${runResponse.status} — ${errBody}`);
  }

  const runData = await runResponse.json();
  const runId: string = runData.data.id;
  logger.info({ runId, batchSize: urls.length }, 'Apify run started');

  // Step 2: Poll until completed or timeout
  const pollInterval = config.APIFY_POLL_INTERVAL_MS;
  const timeout = config.APIFY_POLL_TIMEOUT_MS;
  const startTime = Date.now();

  while (Date.now() - startTime < timeout) {
    await delay(pollInterval);

    const statusResponse = await fetch(
      `${baseUrl}/actor-runs/${runId}?token=${token}`
    );

    if (!statusResponse.ok) continue;

    const statusData = await statusResponse.json();
    const status: string = statusData.data.status;

    if (status === 'SUCCEEDED') {
      logger.info({ runId }, 'Apify run succeeded');
      return fetchResults(runId, token, baseUrl, urls.length);
    }

    if (['FAILED', 'ABORTED', 'TIMED-OUT'].includes(status)) {
      throw new Error(`Apify run ${status}: ${runId}`);
    }

    logger.debug({ runId, status }, 'Apify run still in progress...');
  }

  throw new Error(`Apify run timed out after ${timeout}ms: ${runId}`);
}

/**
 * Fetch dataset items from a completed Apify run.
 */
async function fetchResults(
  runId: string,
  token: string,
  baseUrl: string,
  expectedCount: number
): Promise<ApifyTikTokResult[]> {
  const datasetResponse = await fetch(
    `${baseUrl}/actor-runs/${runId}/dataset/items?token=${token}&format=json`
  );

  if (!datasetResponse.ok) {
    throw new Error(`Failed to fetch dataset: ${datasetResponse.status}`);
  }

  const items: any[] = await datasetResponse.json();

  const results: ApifyTikTokResult[] = items.map((item) => ({
    url: cleanUrl(item.webVideoUrl || item.url || ''),
    playCount: Number(item.playCount) || 0,
    diggCount: Number(item.diggCount) || 0,
    shareCount: Number(item.shareCount) || 0,
    commentCount: Number(item.commentCount) || 0,
    collectCount: Number(item.collectCount) || 0,
  }));

  logger.info(
    { returnedCount: results.length, expectedCount },
    'Fetched Apify dataset items'
  );

  return results;
}

/**
 * Normalize URL for matching — strip trailing slash, query params, etc.
 */
function cleanUrl(url: string): string {
  try {
    const u = new URL(url);
    u.search = '';   // remove query params
    u.hash = '';     // remove hash
    return u.href.replace(/\/$/, ''); // remove trailing slash
  } catch {
    return url;
  }
}

function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
