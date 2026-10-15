# web/ — Dashboard Laravel

Lapisan web AutoDAST-Agent: Laravel 11 + Blade + Livewire + Tailwind. Repo ini berisi
**file khusus aplikasi** (migrations, models, komponen Livewire, view). Kerangka
Laravel penuh (`vendor/`, dll) dibuat lewat `composer create-project` lalu file di
sini di-drop ke atasnya.

## Setup pertama kali

```bash
# dari root repo
composer create-project laravel/laravel web-tmp
rsync -a web-tmp/ web/            # kerangka Laravel ke web/
rm -rf web-tmp
cd web

composer require livewire/livewire

# file scaffold (app/, database/, resources/) sudah ada di web/ dari repo ini.
# Aktifkan rute contoh:
cat routes/web.php.example >> routes/web.php

# DB: samakan dengan AGENT_DB_DSN di ../.env
#   .env Laravel: DB_CONNECTION=mysql DB_DATABASE=autodast DB_USERNAME=... DB_PASSWORD=...
php artisan migrate
php artisan db:seed --class=Database\\Seeders\\TargetSeeder

npm install && npm run dev       # Tailwind via Vite
php artisan serve                # http://localhost:8000
```

## File yang disediakan scaffold

| Path | Isi |
| --- | --- |
| `database/migrations/*` | 5 tabel: targets, scans, agent_steps, findings, audit_log |
| `app/Models/*` | Scan, Target, AgentStep, Finding |
| `app/Livewire/ScanShow.php` | Feed ReAct + temuan, polling 2 dtk (DESIGN_GUIDELINES §3.4) |
| `resources/views/livewire/scan-show.blade.php` | View komponen di atas |
| `resources/views/components/severity-icon.blade.php` | Ikon severity (kanal kedua, §2.2) |
| `database/seeders/TargetSeeder.php` | Isi targets dari daftar lab default |
| `routes/web.php.example` | Rute contoh untuk disalin ke routes/web.php |

## Belum dibuat (TODO)

- Design token (§2) sebagai CSS variables di `resources/css/app.css` + `tailwind.config.js`.
- Halaman: index scans, findings, targets, audit, laporan (§3.2).
- Form "New scan" yang menulis `scans(status='queued')` — pilihan target dari tabel
  `targets`, **bukan input URL bebas** (§5.2).
- Auth (Laravel Breeze).

## Penting

Laravel **tidak pernah** mengirim request ke target. Ia hanya menulis job ke DB; worker
Python yang menjalankan scan. Jangan menambah HTTP client ke target dari sisi PHP.
