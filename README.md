# KOL Scraper Automation

Auto-scrape TikTok post metrics dari Google Spreadsheet pake Apify TikTok Scraper, tulis balik hasilnya.

## Setup

### 1. Google Service Account
1. Buka [Google Cloud Console](https://console.cloud.google.com/)
2. Buat project / pilih existing
3. Enable **Google Sheets API**
4. Go to **IAM & Admin → Service Accounts**
5. Create service account → Download JSON key
6. Simpan JSON key ke `keys/service-account.json`
7. Share spreadsheet lo dengan email service account (role: Editor)

### 2. Config
```bash
cp .env.example .env
# Edit .env — isi SPREADSHEET_ID dan pastikan path service account bener
```

### 3. Run
```bash
# Satu kali (test)
npm run dev

# Build + run
npm run build && npm run start:once

# Cron mode (setiap 3 hari jam 11PM WIB)
npm run build && npm start
```

## Struktur
```
src/
├── index.ts              # Entry point + cron
├── config.ts             # Env config
├── sheets/
│   ├── client.ts         # Google Sheets auth
│   ├── reader.ts         # Baca link dari sheet
│   └── writer.ts         # Tulis hasil ke sheet
├── apify/
│   ├── client.ts         # Apify API wrapper
│   └── batching.ts       # URL batching
├── scraper/
│   ├── orchestrator.ts   # Main flow
│   └── mapper.ts         # Map hasil → kolom
└── utils/
    ├── logger.ts
    └── date.ts
```

## Scope
- 14 sheets: `[TT]` + `[YC]` × 7 kategori (Bodycare, Skincare, Mattedorable, Next Level, NCO, FYNE, Eomma)
- Skip `[IG]`
- Kolom H (Link Post) → scrape → tulis di I-O
- Jadwal: setiap 3 hari, 23:00 WIB
