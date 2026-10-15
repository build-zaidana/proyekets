# web/ — Dashboard Laravel

Lapisan web AutoDAST-Agent: **Laravel 13 + Livewire 4 + Tailwind (Vite)**. Repo ini
sudah membawa aplikasi Laravel lengkap (kecuali `vendor/` & `node_modules/` yang
di-install lokal). Default DB **SQLite** agar cepat dijalankan; ganti ke MySQL untuk
produksi sesuai DESIGN_GUIDELINES §6.

## Setup

```bash
cd web
composer install
npm install && npm run build       # atau: npm run dev (hot reload)
cp .env.example .env               # jika .env belum ada
php artisan key:generate

# DB: SQLite (default, zero-config)
touch database/database.sqlite
php artisan migrate
php artisan db:seed --class=Database\\Seeders\\TargetSeeder

php artisan serve                  # http://localhost:8000
```

### Memakai MySQL (produksi / sesuai desain)

Samakan DB dengan `AGENT_DB_DSN` di `../.env` (dibaca worker Python), lalu di `web/.env`:

```
DB_CONNECTION=mysql
DB_DATABASE=autodast
DB_USERNAME=autodast
DB_PASSWORD=secret
```

Jalankan `php artisan migrate` lagi. Skema identik; SQL aplikasi portabel (tanpa
fungsi khusus MySQL).

## Halaman

| Rute | Komponen | Fungsi |
| --- | --- | --- |
| `/` | `Dashboard` | Stat tiles + chart distribusi severity + scan terbaru |
| `/scans` | `ScanIndex` | Daftar scan (polling saat ada yang berjalan) |
| `/scans/create` | `ScanCreate` | Form New scan (pilih target dari DB, bukan URL bebas — §5.2) |
| `/scans/{scan}` | `ScanShow` | Feed ReAct + temuan, polling 2 dtk |
| `/scans/{scan}/report` | `ReportController` | Laporan HTML (ringkasan, temuan, audit) |
| `/findings` | `FindingsIndex` | Tabel temuan, filter severity |
| `/targets` | `TargetsIndex` | Daftar target (read-only) |
| `/audit` | `AuditIndex` | Audit log request |

## Test

```bash
php artisan test --filter=ScanFlowTest   # alur create-scan + render halaman
```

## Alur dengan worker Python

Laravel menulis `scans(status='queued')`; **worker Python** (`python -m agent.worker`
dari root repo) yang menjalankan scan dan menulis `agent_steps`/`findings`/`audit_log`.
Dashboard membaca DB. Laravel **tidak pernah** mengirim request ke target.

## Catatan

- `vite.config.js` sengaja tidak memakai plugin font build-time (Bunny); font dimuat
  via `<link>` Google Fonts di layout agar build tidak butuh jaringan eksternal.
- Token desain ada di `resources/css/app.css` (CSS variables, §2 DESIGN_GUIDELINES).
- Auth (Laravel Breeze/Fortify) belum dipasang — opsional untuk lab lokal.
