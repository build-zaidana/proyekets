# Design Guidelines — AutoDAST-Agent

Panduan desain tunggal untuk proyek: tampilan (dashboard web + laporan), format output
laporan, dan konvensi kode. Semua keputusan di sini mengikat; kalau sebuah PR
melanggar, itu alasan sah untuk revisi.

| | |
| --- | --- |
| **Versi** | 0.2 |
| **Tanggal** | 2026-10-15 |
| **Stack web** | Laravel 11 + Blade + Livewire + Tailwind CSS (Vite) |
| **Stack agen** | Python 3.11+ (LangGraph), worker polling |
| **Integrasi** | MySQL sebagai kontrak (lihat §6) — tanpa Redis/broker/websocket |

Dokumen terkait: [`PRD.md`](PRD.md) (apa & kenapa). Dokumen ini: **bagaimana**.

---

## 1. Prinsip

Lima prinsip yang memutus perselisihan desain:

1. **Keamanan sebelum estetika.** Guardrail (allowlist, rate limit, filter payload)
   berjalan di level kode, bukan di prompt dan bukan di UI. UI boleh menampilkan
   status guardrail; UI tidak boleh jadi satu-satunya yang menegakkannya.
2. **Bukti, bukan klaim.** Setiap temuan menampilkan request dan response yang
   membuktikannya. Tidak ada severity tanpa evidence yang bisa dibuka pengguna.
3. **Satu kanal tidak pernah sendirian.** Severity dibedakan lewat warna *dan* ikon
   *dan* teks. Status scan begitu juga. Pengguna buta warna membaca dashboard yang
   sama lengkapnya.
4. **Agen itu kaca, bukan kotak hitam.** Langkah ReAct (Thought → Action →
   Observation) terlihat saat berjalan. Penguji sidang harus bisa menelusuri kenapa
   agen menyimpulkan sesuatu.
5. **Tenang saat idle, jelas saat penting.** Chrome dashboard netral dan diam. Warna
   severity hanya muncul pada data severity, tidak pada tombol atau navigasi.

---

## 2. Design Tokens

Token adalah sumber kebenaran. Komponen memakai token, bukan nilai mentah. Di React,
token hidup sebagai CSS custom properties di `:root` dan dipetakan ke `tailwind.config`.

### 2.1 Warna — chrome (netral + aksen)

Chrome dashboard pakai satu skala abu dingin dan satu aksen. Aksen = indigo, sengaja
dipilih beda dari biru severity "Low" supaya tombol tidak pernah terbaca sebagai
level severity.

| Token | Light | Dark | Pemakaian |
| --- | --- | --- | --- |
| `--bg` | `#FCFCFB` | `#1A1A19` | Latar halaman |
| `--surface` | `#FFFFFF` | `#232322` | Kartu, panel, tabel |
| `--surface-2` | `#F4F4F2` | `#2C2C2A` | Baris zebra, header tabel |
| `--border` | `#E4E4E1` | `#383835` | Garis pembatas |
| `--ink` | `#1C1C1A` | `#F2F2EF` | Teks utama |
| `--ink-2` | `#55554F` | `#B6B6AF` | Teks sekunder |
| `--ink-muted` | `#8A8A82` | `#83837B` | Label, placeholder |
| `--accent` | `#5B57D6` | `#8683E8` | Aksi primer, link, fokus |
| `--accent-ink` | `#FFFFFF` | `#17171F` | Teks di atas aksen |

Aturan: teks selalu pakai token `--ink*`, tidak pernah warna severity. Warna severity
hanya untuk mark data dan badge severity.

### 2.2 Warna — severity (skala status)

Severity adalah skala status berurutan, bukan palet kategorikal. Itu mengubah cara
kita memvalidasinya dan cara kita memakainya.

| Level | Light | Dark | Ikon | Bobot |
| --- | --- | --- | --- | --- |
| Critical | `#C0271E` | `#E5484D` | ⛔ / `shield-alert` | 4 |
| High | `#E8590C` | `#FF802B` | ▲ / `alert-triangle` | 3 |
| Medium | `#A6820A` | `#D9A400` | ◆ / `alert-circle` | 2 |
| Low | `#1F5AA6` | `#5A9CF0` | ● / `info` | 1 |
| Info | `#6B7685` | `#9AA4B2` | ○ / `circle` | 0 |

**Validasi (dijalankan, bukan dikira-kira).** `scripts/validate_palette.js` dari skill
dataviz menyatakan kelima warna light mode **PASS kontras ≥3:1** terhadap surface.
Uji *CVD separation* dan *normal-vision floor* milik validator ber-scope palet
**kategorikal**; severity bukan kategorikal, jadi uji itu tidak berlaku langsung.
Yang berlaku: kontras per warna (lolos) plus aturan di bawah.

**Aturan pemakaian severity — wajib:**

- **Tidak pernah warna sendirian.** Setiap indikator severity = ikon + label teks +
  warna. Merah/oranye/amber memang berdekatan untuk mata deuteranopia; ikon dan teks
  yang membedakan, bukan warna. Ini bukan kompromi, ini syarat WCAG 1.4.1.
- **Badge** pakai latar tinted (warna severity 12% opacity) + teks warna severity
  versi gelap + ikon. Bukan blok warna penuh.
- **Chart distribusi severity** (satu-satunya tempat warna severity berdampingan
  sebagai mark): wajib label angka langsung di tiap segmen + gap 2px antar segmen.
  Label langsung = secondary encoding, jadi warna bukan satu-satunya pembeda.
- **Dark mode punya langkah sendiri** (kolom "Dark" di atas), bukan hasil flip
  otomatis. Keduanya lolos kontras terhadap surface masing-masing.

### 2.3 Warna — status scan

Status run scan (berbeda dari severity temuan):

| Status | Token | Light | Ikon |
| --- | --- | --- | --- |
| Running | `--run-active` | `#5B57D6` | spinner |
| Passed/Clean | `--run-ok` | `#2F7D4F` | `check` |
| Blocked (guardrail) | `--run-blocked` | `#A6820A` | `lock` |
| Error | `--run-error` | `#C0271E` | `x-octagon` |

### 2.4 Tipografi

Dua keluarga font. Keduanya gratis di Google Fonts.

| Peran | Font | Catatan |
| --- | --- | --- |
| UI & prosa | Inter | fallback: system-ui, sans-serif |
| Kode, payload, HTTP, URL | JetBrains Mono | fallback: ui-monospace, monospace |

Payload, potongan request/response, header HTTP, dan URL **selalu** monospace. Itu
data teknis yang spasinya bermakna.

Skala tipe (ukuran / line-height):

| Token | Size | Line | Pemakaian |
| --- | --- | --- | --- |
| `text-xs` | 12px | 16px | Meta, timestamp, caption |
| `text-sm` | 14px | 20px | Body tabel, label |
| `text-base` | 16px | 24px | Body default |
| `text-lg` | 20px | 28px | Judul kartu |
| `text-xl` | 24px | 32px | Judul halaman |
| `text-2xl` | 30px | 38px | Angka hero (ringkasan) |

Bobot: 400 (body), 500 (label/judul kartu), 600 (judul halaman, angka hero). Tidak
pakai 700+ — terlalu berat untuk layar data padat.

### 2.5 Spacing, radius, elevation

Spacing kelipatan 4px: `4 · 8 · 12 · 16 · 24 · 32 · 48 · 64`. Padding kartu 24px,
gap antar field form 16px, padding sel tabel 12px vertikal / 16px horizontal.

Radius: `6px` default (input, tombol), `10px` kartu & panel, `9999px` badge pill.

Elevation — hemat. Permukaan dibedakan oleh border, bukan bayangan. Satu bayangan
saja: `--shadow-pop` (`0 4px 16px rgba(0,0,0,.12)`) untuk modal, popover, toast.
Kartu diam tidak berbayang.

---

## 3. UI — Dashboard

### 3.1 App shell

```
┌───────────────────────────────────────────────┐
│  Topbar: logo · target aktif · status run · ⚙ │
├──────────┬────────────────────────────────────┤
│ Sidebar  │  Konten                            │
│ Scans    │                                    │
│ Findings │                                    │
│ Targets  │  (maks lebar konten 1200px,        │
│ Reports  │   gutter 16px di layar sempit)     │
│ Audit    │                                    │
└──────────┴────────────────────────────────────┘
```

Sidebar bisa menciut jadi ikon di bawah 1024px. Topbar selalu menampilkan target
aktif dan status run — dua hal yang paling sering ditanya pengguna.

### 3.2 Halaman inti

1. **Scans** — daftar run + tombol "New scan" (pilih target dari allowlist, bukan
   input bebas; lihat §5.2). Baris run menampilkan target, waktu, durasi, hitungan
   temuan per severity, status.
2. **Scan detail** — dua kolom: kiri **agent activity feed** (langkah ReAct streaming),
   kanan **temuan masuk** real-time. Lihat §3.4.
3. **Findings** — tabel temuan semua scan, bisa difilter per severity / tipe / target.
4. **Finding detail** — judul, klasifikasi (OWASP/CWE), severity, confidence, lokasi,
   **evidence** (request & response), remediasi.
5. **Targets** — tampilkan isi allowlist (read-only dari UI; diubah lewat file config,
   lihat §5.2).
6. **Audit** — tabel audit log request (timestamp, method, URL, verdict guardrail).

### 3.3 Komponen

Setiap komponen punya lima state wajib: **default, hover, focus, disabled, loading**.
Plus untuk kontainer data: **empty, error**.

| Komponen | Aturan |
| --- | --- |
| **Button** | Primer = aksen solid. Sekunder = border + ink. Destruktif (mis. stop scan) = border merah + ink merah, bukan fill merah. Tinggi 40px, radius 6px. |
| **Severity badge** | Pill, latar tinted 12%, ikon + label. Lihat §2.2. |
| **Card** | Surface, border 1px, radius 10px, padding 24px. Tanpa bayangan. |
| **Table (findings)** | Header `surface-2`, baris zebra, sticky header saat scroll. Kolom severity paling kiri, bisa sort by bobot severity. Baris diklik → finding detail. |
| **Evidence block** | Monospace, `surface-2`, nomor baris, tombol copy. Payload yang relevan di-highlight (lihat §4.3). Scroll horizontal, tidak wrap. |
| **Modal** | Maks lebar 560px, overlay `rgba(0,0,0,.4)`, `--shadow-pop`, fokus terjebak, Esc menutup. |
| **Toast** | Pojok kanan bawah, auto-dismiss 5s kecuali error (manual). Ikon + teks. |
| **Progress / step** | Lihat §3.4. |

### 3.4 Agent activity feed (pembeda proyek ini)

Loop ReAct ditampilkan sebagai timeline streaming, satu entri per langkah:

```
● Thought   Form login ditemukan di /login. Coba SQLi error-based di `username`.
│ Action    send_http_request  POST /login  payload: ' OR '1'='1
│ Observ.   HTTP 500 · "You have an error in your SQL syntax"      [lihat evidence]
●
```

- **Thought** ink sekunder, italic. **Action** monospace dengan nama tool + argumen
  ringkas. **Observation** monospace dengan status code berwarna status + ringkasan.
- Komponen **Livewire polling** tiap ~2 dtk membaca tabel `agent_steps` (§6.3) dan
  menambah entri baru di bawah, auto-scroll kecuali pengguna menggulir ke atas. Tanpa
  websocket/SSE — worker Python menulis step ke DB, dashboard membacanya.
- Setiap Observation yang jadi dasar temuan punya link ke evidence block.
- Guardrail yang menolak request muncul sebagai entri `Blocked` warna
  `--run-blocked` dengan alasan — supaya pengguna lihat guardrail bekerja.

### 3.5 Loading, empty, error

- **Loading:** skeleton abu untuk tabel/kartu, spinner hanya untuk aksi (<2s). Scan
  yang berjalan bukan "loading" — itu state aktif dengan feed §3.4.
- **Empty:** satu kalimat + satu aksi. "Belum ada scan. Mulai dari target di
  allowlist." + tombol New scan. Tanpa ilustrasi.
- **Error:** apa yang gagal + apa yang bisa dilakukan pengguna. Pesan error API
  ditampilkan apa adanya, tidak ditelan.

### 3.6 Chart

Satu chart dipakai di ringkasan: **distribusi temuan per severity** (bar horizontal
atau donut). Aturan (dari skill dataviz):

- Satu sumbu. Tidak pernah dua skala-y.
- Label angka langsung di tiap segmen (bukan hanya legend).
- Gap 2px antar segmen, ujung bar radius 4px menempel baseline.
- Urutan severity tetap: Critical → Info (bukan urut besaran nilai).
- Warna dari §2.2; karena ada label langsung, warna jadi kanal sekunder.
- Sediakan tampilan tabel sebagai alternatif chart.

Grid dan axis recessive (`--border`). Hover memperlihatkan hitungan + persentase.

### 3.7 Aksesibilitas (WCAG 2.1 AA)

- Kontras teks ≥ 4.5:1 (normal), ≥ 3:1 (≥20px). Token ink sudah memenuhi di kedua mode.
- Severity & status tidak pernah warna sendirian (§2.2, §1.3).
- Fokus terlihat: ring 2px `--accent` offset 2px pada semua elemen interaktif.
- Semua aksi bisa keyboard. Modal menjebak fokus, Esc menutup.
- Target sentuh ≥ 44×44px di layar sempit.
- Feed §3.4 pakai `aria-live="polite"` supaya screen reader membaca langkah baru.

### 3.8 Dark mode

Diaktifkan lewat `data-theme` di `<html>`, default ikut `prefers-color-scheme`. Dark
mode pakai kolom "Dark" di §2.1–2.2, bukan filter CSS. Setiap warna baru wajib punya
pasangan dark yang lolos kontras terhadap `--bg` dark.

---

## 4. Desain Laporan (output)

Laporan dihasilkan dalam dua format dari satu sumber data: **Markdown** (untuk
lampiran skripsi / repo) dan **HTML** (untuk dibaca / cetak PDF). Keduanya memakai
struktur dan urutan yang sama.

### 4.1 Struktur

1. **Sampul** — target, waktu scan, durasi, versi alat, pernyataan legal (§5.1).
2. **Ringkasan eksekutif** — tabel hitungan per severity + satu paragraf temuan
   terpenting. Tanpa jargon.
3. **Daftar temuan** — diurutkan severity menurun, lalu confidence.
4. **Lampiran** — audit log lengkap request yang dikirim agen.

### 4.2 Anatomi satu temuan

Urutan tetap, supaya pembaca tahu di mana mencari:

```
### [SEVERITY] Judul temuan
Klasifikasi : OWASP A03:2021 / CWE-89
Lokasi      : POST http://localhost:8080/login  (param: username)
Severity    : High          Confidence: High
Evidence    : <request & response yang membuktikan>
Remediasi   : <perbaikan tingkat kode, full-stack>
```

### 4.3 Format evidence

- Request dan response ditampilkan utuh tapi dipotong pada `RESPONSE_BODY_MAX_BYTES`;
  pemotongan ditandai `… [dipotong, N byte]`.
- Payload dan baris pembukti (mis. pesan error SQL) di-highlight. Di Markdown pakai
  komentar penanda; di HTML pakai `<mark>`.
- Setiap temuan menyertakan **minimal dua request** bila klaimnya berbasis perbedaan
  perilaku (payload uji vs payload kontrol) — sesuai kriteria anti–false-positive PRD §7.
- Secret/kredensial tidak pernah masuk laporan dalam bentuk nilai; tunjuk lokasinya.

### 4.4 Remediasi

Tiap remediasi menyebut perbaikan konkret di tingkat kode, bukan nasihat umum.
"Gunakan prepared statement; jangan rangkai query dengan string" + contoh kode, bukan
"terapkan validasi input yang baik". Sebut sisi mana (frontend/backend/DB) yang diubah.

---

## 5. Keamanan & Etika dalam produk

Ini bagian desain, bukan sekadar catatan hukum. Lihat PRD §3 untuk dasarnya.

### 5.1 Pernyataan legal

Sampul laporan dan footer dashboard memuat: "Pengujian dilakukan pada sistem milik
sendiri atau yang diizinkan. Penggunaan terhadap sistem pihak ketiga tanpa izin
adalah ilegal."

### 5.2 Allowlist di UI

Form "New scan" tidak menerima URL bebas. Pengguna memilih dari target yang ada di
`config/targets.allowlist`. Kalau mau menambah target, pengguna mengedit file config —
keputusan sadar di luar UI. Ini mencegah salah-ketik mengarahkan agen ke host asing.
Backend tetap menolak di level tool meski UI dilewati (§5.3).

### 5.3 Pembagian tanggung jawab guardrail

| Lapis | Tanggung jawab |
| --- | --- |
| Laravel (web) | Menampilkan status guardrail, membatasi pilihan target ke allowlist, hanya menulis job `queued` ke DB |
| Worker Python | Memvalidasi ulang target terhadap allowlist sebelum menjalankan scan |
| **Tool `send_http_request`** | **Penegak sebenarnya:** allowlist → rate limit → filter payload destruktif → audit log → kirim |

Laravel dan worker boleh gagal/dilewati; tool tidak boleh. Penegakan ada di titik
paling dekat dengan jaringan, di dalam proses Python. Laravel tidak pernah mengirim
request ke target — ia hanya menyentuh DB.

---

## 6. Arsitektur & Konvensi Kode

### 6.1 Dua lapis, satu kontrak

Laravel adalah wajib dari tugas; agen wajib Python. Keduanya dihubungkan oleh **MySQL
sebagai kontrak** — bukan HTTP langsung, bukan broker. Pilihan paling sedikit bagian
bergerak, sengaja, karena developer masih belajar kedua stack.

```
web/   Laravel 11 + Blade + Livewire + Tailwind   ← auth, kelola scan/target, laporan
         │  tulis scans(status='queued')
         ▼
       MySQL   ← kontrak: scans · findings · agent_steps · audit_log · targets
         ▲
         │  worker polling ~2 dtk: klaim scan 'queued' → jalankan → tulis balik
agent/ Python (LangGraph + tools ber-guardrail)    ← satu-satunya yang menyentuh target
         ▼
       Target Docker (DVWA / Juice Shop)
```

**Aturan ketergantungan yang mengikat:**

- **Laravel tidak pernah mengirim request ke target.** Ia hanya membaca/menulis DB.
  Semua trafik ke target keluar dari proses Python.
- **Agen Python tidak mengimpor atau memanggil Laravel.** Ia membaca job dari DB dan
  menulis hasil ke DB.
- Satu-satunya hal yang mereka bagi adalah skema tabel di §6.3.

### 6.2 Alur satu scan

1. Pengguna pilih target (dari allowlist) di Laravel → `INSERT scans(status='queued')`.
2. Worker Python polling → klaim satu scan `queued` secara atomik (update bersyarat
   `status='queued' → 'running'`), tolak jalan kalau targetnya tidak ada di allowlist.
3. Tiap langkah ReAct → `INSERT agent_steps`. Tiap request → `INSERT audit_log`. Tiap
   temuan tervalidasi → `INSERT findings`.
4. Selesai → `UPDATE scans SET status='done'` (atau `'error'`/`'blocked'`).
5. Livewire polling membaca `agent_steps`/`findings` → UI update tanpa websocket.

Klaim atomik mencegah dua worker mengambil scan yang sama. Status scan: `queued →
running → done | error | blocked`.

### 6.3 Skema tabel (kontrak antar-lapis)

Didefinisikan sebagai migration Laravel; worker Python membacanya apa adanya.

| Tabel | Kolom inti |
| --- | --- |
| `targets` | id, name, base_url, is_active — cermin allowlist, read-only dari UI |
| `scans` | id, target_id, status, started_at, finished_at, totals (json per severity) |
| `agent_steps` | id, scan_id, seq, phase (`thought`/`action`/`observation`/`blocked`), content, created_at |
| `findings` | id, scan_id, severity, confidence, vuln_type, cwe, location, evidence (json), remediation |
| `audit_log` | id, scan_id, ts, method, url, verdict (`sent`/`blocked`), reason |

`targets` adalah cermin `config/targets.allowlist`; allowlist file tetap sumber
kebenaran untuk guardrail (§5), tabel hanya untuk pilihan di UI.

### 6.4 Kontrak tool (pola wajib — sisi Python)

Setiap tool yang dipanggil agen mengikuti pola sama:

```python
def send_http_request(method: str, url: str, *, data: dict | None = None) -> HttpResult:
    """Satu-satunya pintu keluar jaringan. Ber-guardrail.

    Guardrail dijalankan BERURUTAN dan gagal-tertutup (fail closed):
    allowlist -> rate limit -> filter payload -> audit log -> kirim.
    """
```

- Tool mengembalikan objek hasil terstruktur (dataclass), bukan string mentah.
- Tool **gagal-tertutup**: input ragu atau cek gagal → tolak, jangan kirim.
- `requests` hanya diimpor di `agent/tools/http_client.py`. Tidak ada jalur jaringan
  lain di seluruh paket `agent/`.

### 6.5 Struktur direktori

```
web/        Laravel (app/Models, app/Livewire, database/migrations, resources/views)
agent/      Python: config.py guardrails.py audit.py db.py reporter.py
            tools/http_client.py recon.py forms.py   core.py (ReAct)   worker.py
config/     targets.allowlist   (dibaca agen; sumber kebenaran guardrail)
docker-compose.yml   target uji (DVWA / Juice Shop)
tests/      unit test guardrail & http client (Python)
```

### 6.6 Penamaan

- PHP/Laravel: `PascalCase` kelas/model/komponen Livewire, `camelCase` method,
  migration `snake_case`, tabel jamak `snake_case`.
- Python: `snake_case` fungsi/variabel, `PascalCase` kelas, modul `snake_case`.
- Nama menyebut maksud, bukan tipe: `allowed_hosts`, bukan `host_list`.

### 6.7 Error handling & logging

- Python melempar exception bertipe (`GuardrailError`, `TargetNotAllowed`); worker
  menangkapnya, tulis `scans.status='error'`/`'blocked'` + alasan ke DB, lanjut hidup.
- Logging pakai `logging` stdlib, bukan `print`. Audit request ditulis ke tabel
  `audit_log` (dan cermin JSONL lokal), terpisah dari log aplikasi.
- Jangan telan exception diam-diam. Jangan log secret.

### 6.8 Testing

- Guardrail wajib ada unit test: host di luar allowlist ditolak, rate limit menahan,
  payload destruktif difilter. Keamanan-kritis — tanpa test, tidak di-merge.
- Tool HTTP diuji dengan mock, tanpa jaringan nyata.
- Laravel: feature test untuk pembuatan scan menulis baris `queued` yang benar.

### 6.9 Commit & PR

- Commit kecil dan deskriptif, present tense: `feat: add allowlist guardrail`.
- Prefix: `feat` · `fix` · `docs` · `test` · `refactor` · `chore`.
- PR menyebut apa yang diubah dan bukti ujinya (output test ditempel bila relevan).

---

## 7. Yang tidak boleh

- Severity atau status dibedakan hanya dengan warna.
- Input URL bebas di form scan.
- `requests` atau socket di luar `agent/tools/http_client.py`.
- Laravel mengirim request ke target (ia hanya menyentuh DB).
- Guardrail yang hanya ada di prompt atau UI.
- Secret di laporan, log, kode, atau commit.
- Dark mode hasil filter CSS otomatis alih-alih token sendiri.
- Bayangan untuk membedakan permukaan diam (pakai border).
- Payload/HTTP ditampilkan dengan font proporsional.

---

*Perubahan token atau aturan di sini lewat PR yang memperbarui dokumen ini lebih dulu.*
