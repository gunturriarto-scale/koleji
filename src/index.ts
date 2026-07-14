import cron from 'node-cron';
import { config } from './config.js';
import { logger } from './utils/logger.js';
import { runScrapeCycle } from './scraper/orchestrator.js';

/**
 * Check if --once flag was passed (for manual/test runs).
 */
const isOnceMode = process.argv.includes('--once');

async function main() {
  logger.info('=== KOL Scraper Starting ===');
  logger.info({ mode: isOnceMode ? 'once' : 'cron' }, 'Running mode');

  if (isOnceMode) {
    // Run once and exit
    const summary = await runScrapeCycle();
    logger.info({ summary }, 'One-time run completed');

    if (summary.errors.length > 0) {
      process.exit(1);
    }
    process.exit(0);
  }

  // Cron mode: every 3 days at 23:00 WIB (16:00 UTC)
  // 0 16 */3 * * = minute 0, hour 16 (UTC), every 3 days
  const cronExpression = '0 16 */3 * *';

  logger.info({ cronExpression, timezone: 'Asia/Jakarta (23:00 WIB)' }, 'Registering cron job');

  cron.schedule(
    cronExpression,
    async () => {
      logger.info('Cron triggered — starting scrape cycle');
      const summary = await runScrapeCycle();
      logger.info({ summary }, 'Cron cycle completed');
    },
    {
      timezone: 'Asia/Jakarta',
    }
  );

  logger.info('Cron scheduler running. Waiting for next trigger...');
}

// Handle unhandled rejections
process.on('unhandledRejection', (reason) => {
  logger.error({ err: reason }, 'Unhandled rejection');
});

process.on('uncaughtException', (err) => {
  logger.error({ err }, 'Uncaught exception');
  process.exit(1);
});

main();
