# -*- coding: utf-8 -*-
"""Generate KOL Scraper handover documentation PDF (English)."""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, Preformatted
)

OUT = "docs/KOL-Scraper-Handover.pdf"

# ---------- palette ----------
NAVY = colors.HexColor("#1a2b4a")
BLUE = colors.HexColor("#2563eb")
LIGHT = colors.HexColor("#eef2ff")
GREY = colors.HexColor("#f4f5f7")
CODEBG = colors.HexColor("#1e293b")
CODEFG = colors.HexColor("#e2e8f0")
RED = colors.HexColor("#b91c1c")
REDBG = colors.HexColor("#fef2f2")
BORDER = colors.HexColor("#cbd5e1")

styles = getSampleStyleSheet()

def S(name, **kw):
    styles.add(ParagraphStyle(name, parent=styles['Normal'], **kw))

S('xCover', fontName='Helvetica-Bold', fontSize=30, textColor=NAVY, leading=36, spaceAfter=6)
S('xCoverSub', fontName='Helvetica', fontSize=13, textColor=colors.HexColor("#475569"), leading=18)
S('xH1', fontName='Helvetica-Bold', fontSize=17, textColor=NAVY, spaceBefore=18, spaceAfter=6, leading=21)
S('xH2', fontName='Helvetica-Bold', fontSize=13, textColor=BLUE, spaceBefore=12, spaceAfter=4, leading=16)
S('xBody', fontName='Helvetica', fontSize=10, textColor=colors.HexColor("#1f2937"), leading=15, spaceAfter=6)
S('xSmall', fontName='Helvetica', fontSize=8.5, textColor=colors.HexColor("#6b7280"), leading=12)
S('xCell', fontName='Helvetica', fontSize=9, leading=12)
S('xCellB', fontName='Helvetica-Bold', fontSize=9, leading=12)
S('xCellMono', fontName='Courier', fontSize=8.5, leading=11)
S('xCode', fontName='Courier', fontSize=8.5, textColor=CODEFG, leading=12)
S('xWarn', fontName='Helvetica', fontSize=9.5, textColor=colors.HexColor("#7f1d1d"), leading=14)

story = []

def code_block(txt):
    p = Preformatted(txt, styles['xCode'])
    t = Table([[p]], colWidths=[16.4*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), CODEBG),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('ROUNDEDCORNERS', [4,4,4,4]),
    ]))
    return t

def warn_box(title, body):
    inner = [
        Paragraph(f"<b>&#9888; {title}</b>", ParagraphStyle('wt', parent=styles['xWarn'], fontName='Helvetica-Bold', fontSize=10)),
        Spacer(1, 3),
        Paragraph(body, styles['xWarn']),
    ]
    t = Table([[inner]], colWidths=[16.4*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), REDBG),
        ('BOX', (0,0), (-1,-1), 0.5, RED),
        ('LINEBEFORE', (0,0), (0,-1), 3, RED),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    return t

def info_box(rows):
    data = []
    for k, v in rows:
        data.append([Paragraph(k, styles['xCellB']), Paragraph(v, styles['xCell'])])
    t = Table(data, colWidths=[4.2*cm, 12.2*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), LIGHT),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    return t

def data_table(header, rows, col_widths, mono_cols=()):
    data = [[Paragraph(h, ParagraphStyle('th', parent=styles['xCellB'], textColor=colors.white)) for h in header]]
    for r in rows:
        cells = []
        for ci, c in enumerate(r):
            st = styles['xCellMono'] if ci in mono_cols else styles['xCell']
            cells.append(Paragraph(str(c), st))
        data.append(cells)
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), NAVY),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, GREY]),
    ]))
    return t

def bullets(items):
    out = []
    for it in items:
        out.append(Paragraph(f"&#8226;&nbsp;&nbsp;{it}", ParagraphStyle('b', parent=styles['xBody'], leftIndent=10, spaceAfter=3)))
    return out

# =========================================================
# COVER
# =========================================================
story.append(Spacer(1, 3.2*cm))
story.append(Paragraph("KOL Scraper Automation", styles['xCover']))
story.append(Paragraph("Handover &amp; Technical Reference Documentation", styles['xCoverSub']))
story.append(Spacer(1, 0.6*cm))
story.append(HRFlowable(width="100%", thickness=2, color=BLUE))
story.append(Spacer(1, 0.6*cm))
story.append(info_box([
    ("Project", "kol-scraper v1.0.0"),
    ("Description", "Auto-scrapes TikTok post metrics from a Google Spreadsheet via Apify, then writes the results back to the sheet."),
    ("Stack", "Node.js 22 &bull; TypeScript (ESM) &bull; Apify REST API &bull; Google Sheets API v4"),
    ("Document type", "Technical handover"),
    ("Date created", "13 July 2026"),
    ("Prepared and made by", "<b>Guntur Riarto Adhyatma</b>"),
    ("Contact", "0881080301088"),
]))
story.append(Spacer(1, 0.8*cm))
story.append(Paragraph(
    "This document describes the architecture, logic flow, configuration, how to run, and important notes "
    "(including potential issues) of the KOL Scraper project. It is intended for whoever will take over and "
    "operate this project after the handover.", styles['xBody']))
story.append(PageBreak())

# =========================================================
# 1. OVERVIEW
# =========================================================
story.append(Paragraph("1. Project Overview", styles['xH1']))
story.append(Paragraph(
    "KOL Scraper is an automated service that reads a list of TikTok post links from a Google Spreadsheet "
    "(the \"KOL Mastersheet\"), scrapes each post's metrics through the Apify TikTok Scraper, then writes the "
    "resulting metrics (impression, view, likes, share, comment, save, timestamp) back into the same row of the sheet.",
    styles['xBody']))
story.append(Paragraph(
    "The service can run once (<b>--once</b> mode, for testing/manual runs) or as a <b>cron job</b> that runs "
    "automatically on a schedule.", styles['xBody']))

story.append(Paragraph("Flow at a glance", styles['xH2']))
story.append(code_block(
"Google Sheet (14 tabs)\n"
"      |  read column H (Link Post), filter by date (column O, last 30 days)\n"
"      v\n"
"  Batching  --> split into groups of <= BATCH_SIZE URLs\n"
"      v\n"
"  Apify TikTok Scraper  (clockworks~tiktok-scraper)  --> poll until SUCCEEDED\n"
"      v\n"
"  Mapper  --> match results back to rows via URL / video ID\n"
"      v\n"
"  Google Sheet  --> write columns I..O per row"))

story.append(Paragraph("Data scope", styles['xH2']))
for b in bullets([
    "<b>14 sheets</b>: 2 platforms <b>[TT]</b> &amp; <b>[YC]</b> &times; 7 categories.",
    "7 categories: Bodycare, Skincare, Mattedorable, Next Level, NCO, FYNE, Eomma.",
    "<b>[IG]</b> sheets are skipped (not processed).",
    "Only valid TikTok URLs are scraped (tiktok.com, vt.tiktok.com, vm.tiktok.com).",
]):
    story.append(b)

# =========================================================
# 2. STACK & DEPENDENCIES
# =========================================================
story.append(Paragraph("2. Technology &amp; Dependencies", styles['xH1']))
story.append(data_table(
    ["Package", "Version", "Purpose"],
    [
        ["googleapis", "^140.0.0", "Service-account auth + read/write Google Sheets API v4"],
        ["apify-client", "^2.9.0", "Installed as a dependency, BUT the actual code uses raw fetch to the REST API (see notes)"],
        ["node-cron", "^3.0.3", "Scheduler for cron mode"],
        ["dotenv", "^16.4.5", "Loads variables from the .env file"],
        ["zod", "^3.23.8", "Environment schema validation &amp; parsing"],
        ["pino", "^9.1.0", "Structured logging to stdout"],
        ["typescript / tsx", "^5.5.3 / ^4.16.2", "Compiler + dev runner (dev tooling)"],
    ],
    [3.6*cm, 3.0*cm, 9.8*cm]))
story.append(Spacer(1, 6))
story.append(Paragraph(
    "Runtime: <b>Node.js 22.x</b> (compile target ES2022, ESM modules &mdash; <code>\"type\": \"module\"</code>). "
    "Practical minimum Node 18+, recommended 20/22.", styles['xBody']))

# =========================================================
# 3. PREREQUISITES
# =========================================================
story.append(Paragraph("3. Prerequisites to Run", styles['xH1']))
story.append(Paragraph("Mandatory checklist before running:", styles['xBody']))
story.append(data_table(
    ["#", "Item", "Notes"],
    [
        ["1", "Node.js 18+ (20/22 recommended) &amp; npm", "Check: <font face='Courier'>node -v</font>"],
        ["2", "Dependencies installed", "Run <font face='Courier'>npm install</font>"],
        ["3", "<font face='Courier'>.env</font> file", "Contains SPREADSHEET_ID &amp; APIFY_API_TOKEN (see section 4)"],
        ["4", "Google Service Account JSON", "Stored at <font face='Courier'>keys/service-account.json</font>"],
        ["5", "Spreadsheet shared with the service account", "Role <b>Editor</b>, using the <font face='Courier'>client_email</font> from the JSON"],
        ["6", "Google Sheets API enabled", "Enable it in Google Cloud Console for the service account's project"],
        ["7", "Apify account + API token", "Actor <font face='Courier'>clockworks/tiktok-scraper</font> (paid per usage)"],
        ["8", "Sheet tabs named correctly", "14 tabs: <font face='Courier'>[TT] &lt;Category&gt;</font> &amp; <font face='Courier'>[YC] &lt;Category&gt;</font>"],
    ],
    [0.8*cm, 5.2*cm, 10.4*cm]))

story.append(Paragraph("Google Service Account setup (brief)", styles['xH2']))
for b in bullets([
    "Open Google Cloud Console &rarr; create/select a project.",
    "Enable <b>Google Sheets API</b>.",
    "IAM &amp; Admin &rarr; Service Accounts &rarr; create a service account &rarr; download the JSON key.",
    "Save the JSON to <font face='Courier'>keys/service-account.json</font>.",
    "Open the target spreadsheet &rarr; Share &rarr; add the <font face='Courier'>client_email</font> from the JSON &rarr; set to <b>Editor</b>.",
]):
    story.append(b)

# =========================================================
# 4. ENV CONFIG
# =========================================================
story.append(Paragraph("4. Environment Configuration (.env)", styles['xH1']))
story.append(Paragraph(
    "All configuration is validated by zod in <font face='Courier'>src/config.ts</font>. "
    "If a required variable is empty, the app crashes immediately on start (fail-fast).", styles['xBody']))
story.append(data_table(
    ["Variable", "Required?", "Default", "Notes"],
    [
        ["SPREADSHEET_ID", "Yes", "&mdash;", "Spreadsheet ID (from the sheet URL)"],
        ["APIFY_API_TOKEN", "Yes", "&mdash;", "Apify API token"],
        ["GOOGLE_SERVICE_ACCOUNT_PATH", "No", "./keys/service-account.json", "Path to the JSON key file"],
        ["BATCH_SIZE", "No", "400", "Number of URLs per batch (max 500)"],
        ["APIFY_POLL_INTERVAL_MS", "No", "5000", "Run-status polling interval (ms)"],
        ["APIFY_POLL_TIMEOUT_MS", "No", "600000", "Polling timeout per batch (10 minutes)"],
        ["LOG_LEVEL", "No", "info", "trace|debug|info|warn|error|fatal"],
    ],
    [5.4*cm, 1.6*cm, 4.0*cm, 5.4*cm], mono_cols=(0,)))
story.append(Spacer(1, 6))
story.append(Paragraph("Example <font face='Courier'>.env</font> contents:", styles['xBody']))
story.append(code_block(
"SPREADSHEET_ID=1AbC...spreadsheet_id_here\n"
"APIFY_API_TOKEN=apify_api_xxxxxxxxxxxxxxxxx\n"
"GOOGLE_SERVICE_ACCOUNT_PATH=./keys/service-account.json\n"
"BATCH_SIZE=400\n"
"LOG_LEVEL=info"))
story.append(Spacer(1, 6))
story.append(warn_box("Credentials &amp; security",
    "The <font face='Courier'>.env</font> file and the <font face='Courier'>keys/</font> folder contain secrets and "
    "are already in <font face='Courier'>.gitignore</font> &mdash; <b>do not</b> commit them or send them over "
    "insecure channels. During handover, transfer both files separately and securely. Rotate the Apify token and "
    "re-generate the service-account key if needed."))

# =========================================================
# 5. HOW TO RUN
# =========================================================
story.append(Paragraph("5. How to Run", styles['xH1']))
story.append(code_block(
"# 1. Install dependencies\n"
"npm install\n\n"
"# 2. Prepare configuration\n"
"cp .env.example .env      # then edit .env\n"
"#    make sure keys/service-account.json exists\n\n"
"# 3a. Run once (test/manual) -- uses tsx, no build\n"
"npm run dev               # = tsx src/index.ts --once\n\n"
"# 3b. Build then run once from the compiled output\n"
"npm run build             # tsc -> dist/ folder\n"
"npm run start:once        # node dist/index.js --once\n\n"
"# 3c. Cron mode (runs continuously in background/on a server)\n"
"npm run build && npm start # node dist/index.js"))
story.append(Spacer(1, 6))
story.append(data_table(
    ["Script", "Command", "Purpose"],
    [
        ["dev", "tsx src/index.ts --once", "Run once directly from TS (development/test)"],
        ["build", "tsc", "Compile TS &rarr; dist/"],
        ["start:once", "node dist/index.js --once", "Run once from the build output"],
        ["start", "node dist/index.js", "Cron mode (daemon, runs continuously)"],
    ],
    [2.6*cm, 6.2*cm, 7.6*cm], mono_cols=(1,)))
story.append(Spacer(1, 6))
story.append(Paragraph(
    "For production, cron mode should run under a process manager (e.g. <b>pm2</b>, <b>systemd</b>, or "
    "<b>screen/tmux</b>) so it stays alive and auto-restarts. Example: "
    "<font face='Courier'>pm2 start dist/index.js --name kol-scraper</font>.", styles['xBody']))

# =========================================================
# 6. FILE STRUCTURE
# =========================================================
story.append(Paragraph("6. File Structure &amp; Responsibilities", styles['xH1']))
story.append(data_table(
    ["File", "Responsibility"],
    [
        ["src/index.ts", "Entry point. Detects --once vs cron flag. Registers the cron job. Handles unhandledRejection / uncaughtException."],
        ["src/config.ts", "Env validation (zod). Defines CATEGORIES, PLATFORMS_TO_SCRAPE, &amp; getTargetSheetNames() (the 14 sheet names)."],
        ["src/scraper/orchestrator.ts", "The brain of the flow: read &rarr; batch &rarr; scrape &rarr; map &rarr; write. Builds the ScrapeSummary."],
        ["src/scraper/mapper.ts", "Matches Apify results to sheet rows (via URL / video ID) &rarr; assembles column I..O values."],
        ["src/sheets/client.ts", "GoogleAuth service-account auth (spreadsheets scope). Singleton client."],
        ["src/sheets/reader.ts", "Reads the 14 sheets, picks column H (link), filters by 30-day date (column O). Multi-format date parsing."],
        ["src/sheets/writer.ts", "Batch-updates columns I:O per row via values.batchUpdate."],
        ["src/apify/client.ts", "Calls the Apify REST API: start run, poll status, fetch dataset items, normalize results."],
        ["src/apify/batching.ts", "Filters valid TikTok URLs + splits them into batches by BATCH_SIZE."],
        ["src/utils/logger.ts", "The pino logger instance (stdout)."],
        ["src/utils/date.ts", "getWIBTimestamp() &mdash; Asia/Jakarta timestamp, format YYYY-MM-DD HH:mm:ss."],
    ],
    [4.8*cm, 11.6*cm], mono_cols=(0,)))

# =========================================================
# 7. LOGIC DETAIL
# =========================================================
story.append(PageBreak())
story.append(Paragraph("7. Per-Module Logic Detail", styles['xH1']))

story.append(Paragraph("7.1 Entry &amp; Scheduling (index.ts)", styles['xH2']))
for b in bullets([
    "If the arguments include <font face='Courier'>--once</font> &rarr; run <font face='Courier'>runScrapeCycle()</font> once. Exit code 1 if there are errors, 0 if clean.",
    "If no flag &rarr; register a cron with expression <font face='Courier'>0 16 */3 * *</font>, timezone <font face='Courier'>Asia/Jakarta</font>.",
    "The process stays alive waiting for the next cron trigger.",
]):
    story.append(b)
story.append(warn_box("Schedule mismatch (needs clarification)",
    "The code comments &amp; README state a schedule of <b>23:00 WIB</b> (assuming 16:00 UTC). "
    "However the cron is set to <font face='Courier'>0 16 */3 * *</font> with <b>timezone Asia/Jakarta</b>, so it "
    "actually triggers at <b>16:00 WIB</b> every 3 days, <b>not</b> 23:00 WIB. "
    "If 23:00 WIB is intended, change it to <font face='Courier'>0 23 */3 * *</font> (keep timezone Asia/Jakarta). "
    "Confirm which one is correct before operating it."))

story.append(Paragraph("7.2 Orchestrator (orchestrator.ts)", styles['xH2']))
story.append(Paragraph("Steps in <font face='Courier'>runScrapeCycle()</font>:", styles['xBody']))
for b in bullets([
    "Initialize the Google Sheets client.",
    "<font face='Courier'>readAllLinks()</font> &rarr; collect all valid links from the 14 sheets.",
    "<font face='Courier'>createBatches()</font> &rarr; split into batches. If 0 links/batches, exit early.",
    "Loop over each batch <b>sequentially</b>: <font face='Courier'>runTikTokBatch()</font>, with a 2-second pause between batches. Per-batch errors are caught &amp; recorded, and the cycle continues.",
    "<font face='Courier'>mapResultsToUpdates()</font> merges all results &rarr; <font face='Courier'>writeResults()</font> writes to the sheets.",
    "Returns a <font face='Courier'>ScrapeSummary</font> (sheetsProcessed, totalUrls, batchesCreated/Succeeded/Failed, resultsWritten, errors[]).",
]):
    story.append(b)

story.append(Paragraph("7.3 Reader (sheets/reader.ts)", styles['xH2']))
for b in bullets([
    "Reads the range <font face='Courier'>&lt;sheet&gt;!A:O</font> with <font face='Courier'>FORMATTED_VALUE</font>.",
    "Skips row 1 (the \"KOL Mastersheet\" header).",
    "Takes <b>column H</b> (index 7) as the <b>Link Post</b>; rows without a link are skipped.",
    "Takes <b>column O</b> (index 14) as the <b>Date Posting</b> for filtering: only posts from the <b>last 30 days</b>.",
    "The date parser supports 3 formats: <font face='Courier'>M/D/YYYY</font>, <font face='Courier'>DD-Mon-YYYY</font>, <font face='Courier'>DD Mon YYYY</font>. Years outside 2025&ndash;2027 or unparseable &rarr; skipped.",
    "Per-sheet read errors are caught &rarr; return an empty array for that sheet (does not fail the other sheets).",
]):
    story.append(b)

story.append(Paragraph("7.4 Batching (apify/batching.ts)", styles['xH2']))
for b in bullets([
    "Keeps only hosts tiktok.com / vt.tiktok.com / vm.tiktok.com; the rest are dropped &amp; logged.",
    "Splits into chunks of <font face='Courier'>BATCH_SIZE</font> (default 400).",
    "Each batch keeps <font face='Courier'>urls[]</font> + <font face='Courier'>linkRefs[]</font> (a back-reference to sheet+row for mapping).",
]):
    story.append(b)

story.append(Paragraph("7.5 Apify Client (apify/client.ts)", styles['xH2']))
for b in bullets([
    "POST to <font face='Courier'>/v2/acts/clockworks~tiktok-scraper/runs</font> with input: postURLs, resultsPerPage=1, no comments/videos/covers, proxyCountryCode=None.",
    "Poll <font face='Courier'>/v2/actor-runs/&lt;runId&gt;</font> every 5s until status <font face='Courier'>SUCCEEDED</font> (or FAILED/ABORTED/TIMED-OUT &rarr; throw).",
    "Total timeout per batch is 10 minutes (APIFY_POLL_TIMEOUT_MS).",
    "Fetch dataset items &rarr; map to: url, playCount, diggCount, shareCount, commentCount, collectCount (default 0 if empty).",
    "URLs are cleaned (<font face='Courier'>cleanUrl</font>): strip query, hash, trailing slash.",
]):
    story.append(b)

story.append(Paragraph("7.6 Mapper (scraper/mapper.ts)", styles['xH2']))
for b in bullets([
    "Builds a result lookup keyed by URL, then matches each link: <b>direct match</b> (normalized URL) &rarr; fallback <b>video-ID match</b> (pattern <font face='Courier'>/video/&lt;id&gt;</font>).",
    "If no match is found: the row is still written with value <b>0</b> + timestamp (see the risk note).",
    "Assembles column I..O values per row.",
]):
    story.append(b)

story.append(Paragraph("7.7 Writer (sheets/writer.ts)", styles['xH2']))
for b in bullets([
    "Groups updates per sheet, sorts by row number.",
    "<font face='Courier'>values.batchUpdate</font> with <font face='Courier'>valueInputOption: USER_ENTERED</font>, per-row range <font face='Courier'>&lt;sheet&gt;!I&lt;row&gt;:O&lt;row&gt;</font>.",
    "Per-sheet write errors are caught &amp; logged (does not stop the other sheets).",
]):
    story.append(b)

# =========================================================
# 8. COLUMN MAPPING
# =========================================================
story.append(Paragraph("8. Spreadsheet Column Mapping", styles['xH1']))
story.append(Paragraph("Columns read as input:", styles['xBody']))
story.append(data_table(
    ["Column", "Index (0-based)", "Name", "Role"],
    [
        ["H", "7", "Link Post", "The TikTok URL to scrape"],
        ["O", "14", "Date Posting", "Used to filter to the last 30 days"],
    ],
    [2.0*cm, 3.2*cm, 4.4*cm, 6.8*cm], mono_cols=(0,)))
story.append(Spacer(1, 8))
story.append(Paragraph("Columns written as output (I through O):", styles['xBody']))
story.append(data_table(
    ["Column", "Field", "Apify source"],
    [
        ["I", "Impression", "playCount"],
        ["J", "View", "playCount (same as I)"],
        ["K", "Likes", "diggCount"],
        ["L", "Share", "shareCount"],
        ["M", "Comment", "commentCount"],
        ["N", "Save", "collectCount"],
        ["O", "Update timestamp", "getWIBTimestamp() (Asia/Jakarta)"],
    ],
    [2.0*cm, 5.0*cm, 9.4*cm], mono_cols=(0,)))
story.append(Spacer(1, 8))
story.append(warn_box("Column O conflict (MUST be checked against the real sheet layout)",
    "Column <b>O</b> is read as the <b>Date Posting</b> (30-day filter) in the reader, BUT it is also <b>written</b> "
    "as the <b>update timestamp</b> by the writer. This means after the first run, column O may become the scrape "
    "timestamp, so the date filter on the next run reads the scrape timestamp &mdash; not the real posting date. "
    "Likely causes: (a) the actual sheet layout has more/different columns, or (b) it is genuinely a mapping bug. "
    "<b>Verify the column order in the real spreadsheet</b> before running in production."))

# =========================================================
# 9. NOTES / KNOWN ISSUES
# =========================================================
story.append(PageBreak())
story.append(Paragraph("9. Important Notes &amp; Potential Issues", styles['xH1']))
story.append(Paragraph("The following points should be verified/fixed by whoever takes over the project:", styles['xBody']))
story.append(data_table(
    ["#", "Issue", "Impact / Recommendation"],
    [
        ["1", "Cron schedule 16:00 vs 23:00 WIB",
         "Comments/README say 23:00 WIB but the code triggers at 16:00 WIB. Confirm &amp; adjust the expression."],
        ["2", "Column O has a dual role (Date Posting &amp; Timestamp)",
         "Can break the date filter on the next run. Check the real sheet column layout."],
        ["3", "Unmatched URLs are written as 0",
         "If Apify fails/misses a URL, old metrics get overwritten with 0. Consider skipping the write when unmatched."],
        ["4", "BATCH_SIZE default 400 vs comment '50/batch'",
         "The orchestrator/README comments mention 50; the effective value is 400. Align the docs/value."],
        ["5", "apify-client installed but unused",
         "The code uses raw fetch. It can be removed from dependencies, or migrated to the official SDK."],
        ["6", "Apify cost",
         "The actor is paid per usage. Large batches + scheduled runs = cost. Monitor the Apify quota/credit."],
        ["7", "No retry on failed batches",
         "A FAILED batch is only recorded in summary.errors; it is not retried automatically."],
        ["8", "No automated tests",
         "There are no unit/integration tests yet. Logic changes risk regressions."],
    ],
    [0.8*cm, 5.6*cm, 10.0*cm]))

# =========================================================
# 10. TROUBLESHOOTING
# =========================================================
story.append(Paragraph("10. Quick Troubleshooting", styles['xH1']))
story.append(data_table(
    ["Symptom", "Likely cause &amp; fix"],
    [
        ["Crash on start, zod / env error",
         "SPREADSHEET_ID or APIFY_API_TOKEN is empty in .env. Fill both in."],
        ["403 / permission error when reading-writing the sheet",
         "The spreadsheet hasn't been shared with the service account's client_email as Editor, or the Sheets API isn't enabled."],
        ["'No URLs found to scrape'",
         "All rows were filtered out (date &gt;30 days / unrecognized date format / empty column H). Check columns H &amp; O."],
        ["Apify run FAILED / TIMED-OUT",
         "Wrong token/quota exhausted, invalid URLs, or batch too large. Check the Apify dashboard &amp; lower BATCH_SIZE."],
        ["Many rows become 0",
         "URLs did not match the scrape results (broken URL / vt/vm redirect). Check the 'No match found for URL' log."],
        ["Sheet name not found",
         "Tabs must be exactly '[TT] &lt;Category&gt;' / '[YC] &lt;Category&gt;'. Check spelling &amp; the spaces in the category."],
    ],
    [5.4*cm, 11.0*cm]))
story.append(Spacer(1, 8))
story.append(Paragraph(
    "All activity is logged via pino to stdout. For detailed debugging, set <font face='Courier'>LOG_LEVEL=debug</font> "
    "in .env to see per-sheet details (row counts, skippedByDate, etc.).", styles['xBody']))

story.append(Spacer(1, 18))
story.append(HRFlowable(width="100%", thickness=1, color=BORDER))
story.append(Spacer(1, 6))
story.append(Paragraph(
    "<b>Prepared and made by Guntur Riarto Adhyatma &mdash; 0881080301088.</b>", styles['xBody']))
story.append(Paragraph(
    "This handover document was generated from a direct reading of the project's source code "
    "(<font face='Courier'>kol-scraper v1.0.0</font>) as of 13 July 2026. "
    "For implementation details, refer directly to the files in the <font face='Courier'>src/</font> folder.",
    styles['xSmall']))

# ---------- footer page numbers ----------
def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.HexColor("#94a3b8"))
    canvas.drawString(2*cm, 1.1*cm, "KOL Scraper — Handover Documentation")
    canvas.drawRightString(A4[0]-2*cm, 1.1*cm, f"Page {doc.page}")
    canvas.setStrokeColor(BORDER)
    canvas.line(2*cm, 1.4*cm, A4[0]-2*cm, 1.4*cm)
    canvas.restoreState()

doc = SimpleDocTemplate(OUT, pagesize=A4,
                        leftMargin=2*cm, rightMargin=2*cm,
                        topMargin=1.8*cm, bottomMargin=1.8*cm,
                        title="KOL Scraper - Handover Documentation",
                        author="Guntur Riarto Adhyatma")
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print("OK ->", OUT)
