# Tutorial Menjalankan AutoDAST-Agent di Komputer Sendiri

Panduan lengkap dari clone sampai scan berjalan. Jalur tercepat memakai **SQLite**
(tanpa setup database). Untuk MySQL, lihat bagian akhir.

Komponen yang akan kamu jalankan bersamaan:

1. **Target uji** — DVWA / Juice Shop (lewat Docker)
2. **Dashboard Laravel** — `php artisan serve`
3. **Worker Python** — `python -m agent.worker`

Ketiganya berbagi satu database. Laravel menulis job scan; worker mengerjakannya.

---

## 0. Prasyarat

Pastikan terpasang (cek versinya):

```bash
git --version
php --version          # butuh PHP 8.2+ (disarankan 8.3)
composer --version
node --version         # butuh Node 18+
npm --version
python3 --version      # butuh Python 3.11+
docker --version       # untuk target uji (opsional tapi disarankan)
```

Ekstensi PHP yang wajib aktif: `pdo_sqlite` (untuk SQLite) atau `pdo_mysql` (MySQL),
`mbstring`, `openssl`, `tokenizer`, `xml`. Cek: `php -m | grep -i -E 'sqlite|mysql|mbstring'`.

> **Windows:** jalankan perintah di bawah lewat WSL2 (Ubuntu) atau Git Bash agar
> konsisten. Laragon/XAMPP juga bisa, tapi WSL2 paling mulus.

---

## 1. Clone repo

```bash
git clone https://github.com/build-zaidana/proyekets.git
cd proyekets
git checkout ccr-f79fee3f-hveogn      # branch pengembangan
```

Struktur yang relevan:

```
proyekets/
├── agent/      # worker Python + agen
├── web/        # aplikasi Laravel (dashboard)
├── config/     # targets.allowlist, payloads.yml
├── docker-compose.yml
└── docs/
```

---

## 2. Jalankan target uji (Docker)

Target harus aplikasi yang memang untuk dilatih-serang. Jangan arahkan ke situs lain.

```bash
docker compose up -d
```

Cek jalan:

| Target | URL | Catatan |
| --- | --- | --- |
| DVWA | http://localhost:8080 | buka sekali di browser, klik "Create / Reset Database", lalu login `admin` / `password`; set DVWA Security = Low |
| OWASP Juice Shop | http://localhost:3000 | langsung jalan |

Salin konfigurasi (file asli di-gitignore, jadi dibuat dari contoh):

```bash
cp config/targets.allowlist.example config/targets.allowlist
cp config/payloads.example.yml config/payloads.yml
```

`config/targets.allowlist` sudah memuat `localhost:8080` dan `localhost:3000`. Host di
luar daftar ini akan **ditolak** worker (fail closed).

> Tidak punya Docker? Boleh pakai aplikasi rentan lokal lain, tapi tambahkan host-nya
> ke `config/targets.allowlist` dan ke tabel `targets` (lihat §5).

---

## 3. Setup dashboard Laravel

```bash
cd web

composer install
npm install
npm run build                 # build asset (CSS/JS). Untuk live-reload saat ngoding: npm run dev

# .env
cp .env.example .env          # jika .env belum ada
php artisan key:generate

# Database SQLite (default, tanpa server DB)
touch database/database.sqlite
php artisan migrate
php artisan db:seed --class=Database\\Seeders\\TargetSeeder

php artisan serve             # http://localhost:8000
```

Buka **http://localhost:8000** — dashboard tampil. Biarkan terminal ini jalan.

> `.env` bawaan sudah `DB_CONNECTION=sqlite`. Tidak perlu diubah untuk jalur SQLite.

---

## 4. Setup worker Python

Buka terminal **baru**, kembali ke root repo (`cd proyekets`):

```bash
python3 -m venv .venv
source .venv/bin/activate              # Windows: .venv\Scripts\activate
pip install -r agent/requirements.txt

cp .env.example .env                   # .env untuk agen (TERPISAH dari web/.env)
pytest                                 # 28 test harus lolos
```

### ⚠️ Langkah paling penting: arahkan worker ke DB yang SAMA dengan Laravel

Edit `.env` (di root repo), set `AGENT_DB_DSN` ke file SQLite milik Laravel. Dijalankan
dari root repo, pakai path relatif (SQLAlchemy, perhatikan **tiga** garis miring):

```
AGENT_DB_DSN=sqlite:///web/database/database.sqlite
```

Atau path absolut (empat garis miring + path penuh):

```
AGENT_DB_DSN=sqlite:////home/kamu/proyekets/web/database/database.sqlite
```

Kalau DSN ini salah/menunjuk DB lain, worker tidak akan melihat scan yang dibuat dari
dashboard. Ini penyebab #1 "scan diam di queued".

Jalankan worker:

```bash
python -m agent.worker
```

Output yang benar:

```
Worker siap. Polling tiap 2s. LLM: nonaktif (mode deterministik).
```

Biarkan terminal ini jalan juga.

---

## 5. Jalankan scan pertama

Sekarang tiga hal jalan: target (Docker), dashboard (`:8000`), worker (polling).

1. Buka **http://localhost:8000**.
2. Menu **Scans → New scan**.
3. Pilih target (mis. *DVWA (lokal)*) dari dropdown — **bukan** ketik URL bebas.
4. Klik **Mulai scan**. Kamu diarahkan ke halaman detail scan.
5. Dalam ~2 detik, worker mengambil job: status berubah `queued → running`, **feed
   langkah ReAct** mengalir (Thought / Action / Observation), temuan muncul di kanan.
6. Selesai → status `done`. Klik **Laporan** untuk laporan HTML (bisa di-print ke PDF).
7. Menu **Audit** memperlihatkan tiap request yang dikirim/ditolak worker.

Target bersih (atau DVWA Security = High) wajar menghasilkan sedikit/0 temuan — itu
justru tanda validasi anti–false-positive bekerja.

---

## 6. (Opsional) Nyalakan penalaran LLM

Loop berjalan deterministik tanpa LLM. Untuk narasi "Thought" + remediasi kontekstual,
isi di `.env` root repo, lalu restart worker:

```
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=sk-...
# provider bergaya OpenAI lain: set LLM_BASE_URL juga
```

Install SDK: `pip install openai`. Restart `python -m agent.worker` → log akan
berkata `LLM: aktif`.

---

## 7. (Opsional) Pakai MySQL, bukan SQLite

Sesuai arsitektur produksi. Buat database dulu:

```sql
CREATE DATABASE autodast CHARACTER SET utf8mb4;
CREATE USER 'autodast'@'localhost' IDENTIFIED BY 'secret';
GRANT ALL PRIVILEGES ON autodast.* TO 'autodast'@'localhost';
```

**web/.env:**

```
DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=autodast
DB_USERNAME=autodast
DB_PASSWORD=secret
```

**.env (root, untuk worker):**

```
AGENT_DB_DSN=mysql+mysqlconnector://autodast:secret@127.0.0.1:3306/autodast
```

Lalu dari `web/`: `php artisan migrate && php artisan db:seed --class=Database\\Seeders\\TargetSeeder`.
Skema identik; SQL aplikasi portabel.

---

## 8. Ringkasan: tiga terminal

| Terminal | Perintah | Lokasi |
| --- | --- | --- |
| 1 — target | `docker compose up` (atau `-d`) | root repo |
| 2 — dashboard | `cd web && php artisan serve` | `web/` |
| 3 — worker | `source .venv/bin/activate && python -m agent.worker` | root repo |

Hentikan: `Ctrl+C` di tiap terminal; `docker compose down` untuk target.

---

## 9. Troubleshooting

| Gejala | Penyebab & solusi |
| --- | --- |
| Scan diam di `queued` | `AGENT_DB_DSN` tidak menunjuk DB yang sama dengan Laravel, atau worker tidak jalan. Cek §4. |
| `Worker ... Allowlist kosong` | `config/targets.allowlist` belum dibuat. `cp` dari `.example` (§2). |
| Scan jadi `blocked` | Target tidak ada di allowlist. Tambahkan host-nya ke `config/targets.allowlist`. |
| `could not find driver` (PHP) | Aktifkan `pdo_sqlite`/`pdo_mysql` di `php.ini`. |
| `Vite manifest not found` | Belum `npm run build` (atau jalankan `npm run dev`). |
| `npm run build` gagal ambil font | Sudah ditangani: `vite.config.js` tidak memakai font build-time; pastikan pakai versi di repo. |
| `php artisan key:generate` minta APP_KEY | Pastikan `.env` ada (`cp .env.example .env`). |
| `Please provide a valid cache path` saat `composer install` | Folder `web/storage/framework/views` tidak ada (Git tidak menyimpan folder kosong). Sudah diperbaiki di repo: `git pull`. Darurat: `mkdir web\storage\framework\views` (Windows) atau `mkdir -p web/storage/framework/views`, lalu `composer install` / `php artisan package:discover` lagi. |
| `docker ... dockerDesktopLinuxEngine ... cannot find the file` (Windows) | Docker Desktop belum jalan. Buka Docker Desktop, tunggu "Engine running", cek `docker ps`, ulangi `docker compose up -d`. Tanpa Docker: jalankan Juice Shop langsung (`git clone juice-shop`, `npm install`, `npm start`). |
| Port bentrok (8000/8080/3000) | Ganti port: `php artisan serve --port=8001`, atau edit `docker-compose.yml`. |
| Worker: `No module named sqlalchemy` | `pip install -r agent/requirements.txt` di venv yang aktif. |

---

## Etika & legal

Alat ini hanya untuk sistem milik sendiri atau yang mengizinkan pengujian. Jangan
arahkan ke sistem pihak ketiga. Lihat PRD §3 dan DESIGN_GUIDELINES §5.
