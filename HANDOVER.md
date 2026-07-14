# Handover Guide — KOL TikTok Scraper Automation

## 1. Prasyarat

```bash
# Cek Node.js sudah terinstall (minimal v18)
node -v

# Cek npm
npm -v

# Install PM2 (proses manager)
npm install -g pm2
```

## 2. Setup Folder & Dependencies

```bash
# Pindah ke folder project
cd /Users/mgrmediaads/Documents/vibe\ coding/EJI\ ::\ KOL

# Install semua dependency
npm install

# Build TypeScript
npx tsc
```

## 3. File Penting

| File | Fungsi | Wajib? |
|------|--------|--------|
| `.env` | Config: API token, Spreadsheet ID, dll | ✅ WAJIB |
| `keys/service-account.json` | Google Service Account key | ✅ WAJIB |
| `src/index.ts` | Entry point + cron scheduler | — |
| `src/scraper/orchestrator.ts` | Logic utama scrape cycle | — |
| `package.json` | Daftar dependency & scripts | — |

### Isi `.env` (sudah ada, jangan dishare):
```
SPREADSHEET_ID=isi_dari_google_sheet
APIFY_API_TOKEN=isi_dari_apify
GOOGLE_SERVICE_ACCOUNT_PATH=./keys/service-account.json
BATCH_SIZE=400
LOG_LEVEL=info
```

## 4. Google Service Account

File `keys/service-account.json` berisi key dari Google Cloud. Email service account:
```
kol-scrape@kol-scrape.iam.gserviceaccount.com
```
Email ini harus punya akses **Editor** ke spreadsheet. Udah di-share.

**Kalo perlu bikin ulang dari awal:**
1. Buka https://console.cloud.google.com/
2. Cari project `kol-scrape` atau buat baru
3. Enable **Google Sheets API**
4. IAM & Admin → Service Accounts → pilih `kol-scrape`
5. Keys → Add Key → JSON → download
6. Simpan ke `keys/service-account.json`

## 5. Cara Jalanin

### Test sekali jalan (manual):
```bash
npm run dev
```
Nge-scrape semua link ≤ 30 hari dari 14 sheet, tulis hasil ke kolom I-O.

### Production (PM2 — auto cron):
```bash
npm run build
pm2 start dist/index.js --name kol-scraper
pm2 save
```

### Biar auto startup walau Mac di-restart:
```bash
pm2 startup
```
Jalanin perintah yang muncul (perlu password sudo).

## 6. Jadwal

| Waktu | Zona | Keterangan |
|-------|------|------------|
| 23:00 WIB | Asia/Jakarta | Setiap 3 hari (10, 13, 16, 19... tiap bulan) |

Cron expression: `0 16 */3 * *` (16:00 UTC = 23:00 WIB)

## 7. Monitoring

```bash
# Cek status PM2
pm2 status

# Lihat log realtime
pm2 logs kol-scraper

# Lihat log terakhir
pm2 logs kol-scraper --lines 50

# atau dari file
tail -50 /tmp/kol-scraper-run.log

# Stop / Restart
pm2 stop kol-scraper
pm2 restart kol-scraper
```

## 8. Output — Hasil Scrape

| Kolom | Isi | Sumber |
|-------|-----|--------|
| H | Link Post TikTok | Input (manual / dari form) |
| I | Impression = View | Apify `playCount` |
| J | View = View | Apify `playCount` (sama) |
| K | Likes | Apify `diggCount` |
| L | Share | Apify `shareCount` |
| M | Comment | Apify `commentCount` |
| N | Save | Apify `collectCount` |
| O | Timestamp WIB | Waktu scrape |

### Log Sheet
Setiap selesai cycle, summary ditulis ke sheet **log**:
- A = Waktu selesai
- B = Total link di-scrape
- C = Total batch
- D = Batch sukses
- E = Batch gagal
- F = Row di-update
- G = Error (kalo ada)

## 9. Filter Scope

| Filter | Detail |
|--------|--------|
| **Platform** | Hanya `[TT]` dan `[YC]` (skip IG) |
| **Tanggal** | Kolom O (Date Posting) ≤ 30 hari terakhir |
| **Batch size** | 400 URL per panggilan API |
| **Scrape strategi** | Semua ulang tiap cycle (overwrite) |
| **Total estimate** | ~3,000-5,000 link per cycle |

## 10. Biaya Apify

| Item | Biaya |
|------|-------|
| Per video/post | $0.003 |
| Free per query | 0 (karena pake `postURLs` — flat $0.003) |
| Estimate per cycle | ~$9-15 (3,000-5,000 video) |

## 11. Troubleshooting

**Q: Kok gak ada hasil di sheet?**
Cek log: `pm2 logs kol-scraper --lines 50`. Mungkin API token expired atau service account gak punya akses.

**Q: Mau jalanin manual tanpa cron?**
```bash
npm run dev
```

**Q: Service account key ilang / ganti?**
Download ulang dari Google Cloud Console, simpan ke `keys/service-account.json` (nama file harus sama).

**Q: Ganti API token Apify?**
Edit `.env` → ganti `APIFY_API_TOKEN` → `pm2 restart kol-scraper`

**Q: Mau nambah sheet kategori baru?**
Edit `src/config.ts` → tambah ke array `CATEGORIES` → `npm run build` → `pm2 restart kol-scraper`
