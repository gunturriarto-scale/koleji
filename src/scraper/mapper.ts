import { SheetLink } from '../sheets/reader.js';
import { SheetUpdates } from '../sheets/writer.js';
import { ApifyTikTokResult } from '../apify/client.js';
import { logger } from '../utils/logger.js';

/**
 * Map Apify scrape results back to sheet updates.
 *
 * Rules:
 * - I = Impression = playCount
 * - J = View = playCount (same as I)
 * - K = Likes = diggCount
 * - L = Share = shareCount
 * - M = Comment = commentCount
 * - N = Save = collectCount
 *
 * Column O (Date Posting) is entered manually and is never written here.
 * Matches results to linkRefs by normalized URL.
 */
export function mapResultsToUpdates(
  linkRefs: SheetLink[],
  results: ApifyTikTokResult[]
): SheetUpdates {
  const updates: SheetUpdates = {};

  // Build URL lookup from results
  const resultMap = new Map<string, ApifyTikTokResult>();
  for (const r of results) {
    resultMap.set(r.url, r);
  }

  let matchedCount = 0;
  let unmatchedCount = 0;

  for (const link of linkRefs) {
    const result = findMatchingResult(link.url, resultMap);

    if (!result) {
      unmatchedCount++;
      logger.warn({ url: link.url, sheet: link.sheetName, row: link.rowNumber }, 'No match found for URL');
      // Still write row but with 0 values
      writeToUpdate(updates, link.sheetName, link.rowNumber, {
        playCount: 0,
        diggCount: 0,
        shareCount: 0,
        commentCount: 0,
        collectCount: 0,
      });
      continue;
    }

    matchedCount++;
    writeToUpdate(updates, link.sheetName, link.rowNumber, result);
  }

  logger.info({ matchedCount, unmatchedCount }, 'Mapped Apify results to sheet updates');
  return updates;
}

function writeToUpdate(
  updates: SheetUpdates,
  sheetName: string,
  rowNumber: number,
  result: { playCount: number; diggCount: number; shareCount: number; commentCount: number; collectCount: number }
): void {
  if (!updates[sheetName]) {
    updates[sheetName] = [];
  }

  updates[sheetName].push({
    rowNumber,
    values: [
      result.playCount,    // I - Impression
      result.playCount,    // J - View (same)
      result.diggCount,    // K - Likes
      result.shareCount,   // L - Share
      result.commentCount, // M - Comment
      result.collectCount, // N - Save
    ],
  });
}

/**
 * Try to find a matching Apify result for a given URL.
 * Tries exact match first, then normalized match.
 */
function findMatchingResult(
  url: string,
  resultMap: Map<string, ApifyTikTokResult>
): ApifyTikTokResult | null {
  // Direct match
  const normalized = normalizeUrl(url);
  const direct = resultMap.get(normalized);
  if (direct) return direct;

  // Try matching by video ID
  const videoId = extractVideoId(url);
  if (!videoId) return null;

  for (const [, result] of resultMap) {
    const resultVideoId = extractVideoId(result.url);
    if (resultVideoId === videoId) return result;
  }

  return null;
}

function normalizeUrl(url: string): string {
  try {
    const u = new URL(url);
    u.search = '';
    u.hash = '';
    return u.href.replace(/\/$/, '').toLowerCase();
  } catch {
    return url.toLowerCase().trim();
  }
}

function extractVideoId(url: string): string | null {
  // TikTok video IDs are typically in the path like /video/1234567890
  const match = url.match(/\/video\/(\d+)/);
  return match ? match[1] : null;
}
