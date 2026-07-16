import { SheetLink } from '../sheets/reader.js';
import { config } from '../config.js';
import { logger } from '../utils/logger.js';

export interface Batch {
  urls: string[];
  linkRefs: SheetLink[]; // reference back to sheet + row for mapping
}

/**
 * Filter valid TikTok URLs and split into batches.
 * Accepts tiktok.com, vt.tiktok.com, vm.tiktok.com URLs.
 */
function isValidTikTokUrl(url: string): boolean {
  try {
    const u = new URL(url);
    return /(tiktok\.com|vt\.tiktok\.com|vm\.tiktok\.com)$/i.test(u.hostname);
  } catch {
    return false;
  }
}

/**
 * TikTok redirects /<username>/video/<id> (missing the @ handle) to a
 * generic /foryou page instead of the post, which the Apify actor can't
 * resolve. Insert the @ if it's missing so the actor gets a real post URL.
 * Short links (vt.tiktok.com / vm.tiktok.com) have no username segment
 * and are left untouched.
 */
function ensureUsernameHandle(url: string): string {
  try {
    const u = new URL(url);
    const hostname = u.hostname.toLowerCase();
    if (hostname === 'vt.tiktok.com' || hostname === 'vm.tiktok.com') {
      return url;
    }
    const parts = u.pathname.split('/');
    if (parts.length > 1 && parts[1] && !parts[1].startsWith('@')) {
      parts[1] = '@' + parts[1];
      u.pathname = parts.join('/');
      return u.toString();
    }
    return url;
  } catch {
    return url;
  }
}

/**
 * Create batches of URLs for Apify scraping.
 * Each batch = BATCH_SIZE URLs max, grouped by platform (TikTok only for now).
 */
export function createBatches(links: SheetLink[]): Batch[] {
  const validLinks = links.filter((l) => isValidTikTokUrl(l.url));
  const skippedCount = links.length - validLinks.length;

  if (skippedCount > 0) {
    logger.warn({ skippedCount }, 'Skipped invalid/non-TikTok URLs');
  }

  if (validLinks.length === 0) {
    logger.warn('No valid TikTok URLs found to scrape');
    return [];
  }

  const batchSize = config.BATCH_SIZE;
  const batches: Batch[] = [];

  for (let i = 0; i < validLinks.length; i += batchSize) {
    const chunk = validLinks.slice(i, i + batchSize);
    batches.push({
      urls: chunk.map((l) => ensureUsernameHandle(l.url)),
      linkRefs: chunk,
    });
  }

  logger.info({ totalBatches: batches.length, batchSize }, 'Created URL batches');
  return batches;
}
