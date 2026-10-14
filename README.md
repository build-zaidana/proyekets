# AutoDAST-Agent

Agentic AI **Dynamic Application Security Testing (DAST)** untuk analisis kerentanan
aplikasi web secara otonom — proyek Tugas Akhir Informatika.

Agen AI (LLM + *reasoning loop* ReAct) melakukan *reconnaissance*, memilih payload
uji secara dinamis berdasarkan respons HTTP, memvalidasi kerentanan, dan menghasilkan
laporan remediasi. Lihat [`docs/PRD.md`](docs/PRD.md) untuk spesifikasi lengkap.

> ⚠️ **HANYA UNTUK TARGET LEGAL.** Alat ini hanya boleh dijalankan terhadap aplikasi
> yang Anda miliki atau yang secara eksplisit mengizinkan pengujian (mis. DVWA /
> OWASP Juice Shop lokal). Semua request dibatasi oleh **allowlist** yang di-*enforce*
> di level kode. Penggunaan terhadap sistem pihak ketiga tanpa izin adalah ilegal.

---

## Arsitektur singkat

```
Orchestrator (LLM + ReAct)
   │  function calling
   ├─ recon         : extract_endpoints, analyze_form   (crawling pasif)
   ├─ scanner tool  : send_http_request                  (satu-satunya pintu jaringan)
   └─ reporter      : temuan → laporan Markdown + remediasi
         │
         ├─ Guardrails : allowlist ⇒ rate-limit ⇒ filter payload destruktif ⇒ audit log
         └─ Target legal (Docker: DVWA / Juice Shop)
```

Prinsip: **LLM tidak pernah memegang jaringan langsung.** Semua I/O keluar melewati
`send_http_request` yang di-*guardrail*.

---

## Setup

### 1. Environment Python

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Konfigurasi

```bash
cp .env.example .env                                  # isi API key LLM
cp config/targets.allowlist.example config/targets.allowlist
```

Edit `config/targets.allowlist` — satu host per baris. Host yang **tidak** terdaftar
akan ditolak oleh guardrail sebelum request terkirim.

### 3. Jalankan target legal (Docker)

```bash
docker compose up -d
```

| Target | URL |
| --- | --- |
| DVWA | http://localhost:8080 |
| OWASP Juice Shop | http://localhost:3000 |

### 4. Jalankan agen

```bash
python -m autodast --target http://localhost:8080 --out reports/
# cek guardrail tanpa kirim request nyata:
python -m autodast --target http://localhost:8080 --dry-run
```

---

## Struktur proyek

```
src/autodast/
  config.py          # pemuatan .env + allowlist
  guardrails.py      # allowlist, rate limiter, filter payload destruktif
  audit.py           # audit log JSONL semua request
  tools/
    http_client.py   # send_http_request (ber-guardrail) — satu pintu jaringan
    recon.py         # extract_endpoints (crawl dangkal)
    forms.py         # analyze_form
  agent.py           # ReAct reasoning loop (skeleton, provider-agnostik)
  reporter.py        # generator laporan Markdown
tests/               # unit test guardrail & http client
docs/PRD.md          # Product Requirements Document
```

## Status

Scaffold MVP. Bagian keamanan-kritis (guardrail, audit log, recon/form parsing)
sudah fungsional; loop agen LLM berupa skeleton yang siap diisi — lihat `TODO` di
`src/autodast/agent.py`.

## Lisensi & Etika

Lihat [`docs/PRD.md`](docs/PRD.md) §3 (Batasan Etis, Legal & Keamanan). Pengujian hanya
pada sistem milik sendiri / yang diizinkan.
