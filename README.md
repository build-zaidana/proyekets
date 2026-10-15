# AutoDAST-Agent

Agentic AI **Dynamic Application Security Testing (DAST)** untuk analisis kerentanan
aplikasi web secara otonom — proyek Tugas Akhir Informatika.

Agen AI (Python, LangGraph) melakukan *reconnaissance*, memilih payload uji dinamis
berdasarkan respons HTTP, memvalidasi kerentanan, lalu menulis temuan ke database.
Dashboard **Laravel** menampilkan langkah agen secara langsung dan menyusun laporan.

Dokumen: [`docs/PRD.md`](docs/PRD.md) (apa & kenapa) · [`docs/DESIGN_GUIDELINES.md`](docs/DESIGN_GUIDELINES.md) (bagaimana).

> ⚠️ **HANYA UNTUK TARGET LEGAL.** Jalankan hanya terhadap aplikasi yang Anda miliki
> atau yang mengizinkan pengujian (DVWA / OWASP Juice Shop lokal). Semua request
> dibatasi **allowlist** yang ditegakkan di level kode Python. Pengujian sistem pihak
> ketiga tanpa izin adalah ilegal.

---

## Arsitektur (dua lapis, DB sebagai kontrak)

```
web/   Laravel + Blade + Livewire + Tailwind   ── auth, kelola scan, laporan
          │  tulis scans(status='queued')
          ▼
       MySQL   ── scans · findings · agent_steps · audit_log · targets
          ▲
          │  worker polling ~2 dtk → jalankan → tulis balik
agent/ Python (LangGraph + tools ber-guardrail) ── satu-satunya yang menyentuh target
          ▼
       Target Docker (DVWA / Juice Shop)
```

Laravel tidak pernah mengirim request ke target — ia hanya menyentuh DB. Semua trafik
ke target keluar dari proses Python, lewat `send_http_request` yang ber-guardrail
(allowlist → rate limit → filter payload destruktif → audit log → kirim). Lihat
DESIGN_GUIDELINES §6.

---

## Status scaffold

| Bagian | Status |
| --- | --- |
| Guardrail (allowlist, rate limit, filter payload) | ✅ fungsional + unit test |
| Audit log, HTTP client, recon/form parser | ✅ fungsional |
| Loop ReAct + validator (SQLi error/boolean, reflected XSS) | ✅ deterministik, jalan tanpa LLM (26 unit test) |
| Integrasi LLM (narasi + remediasi) | ✅ opsional via env; pemilihan aksi penuh = TODO (`agent/core.py`) |
| Worker polling + akses DB | ✅ fungsional (butuh MySQL) |
| Dashboard Laravel | ✅ migrations, models, Livewire (index/create/show/findings), token Tailwind; chart & auth menyusul |

---

## Menjalankan

### 1. Target legal (Docker)

```bash
docker compose up -d        # DVWA :8080 · Juice Shop :3000
cp config/targets.allowlist.example config/targets.allowlist
cp config/payloads.example.yml config/payloads.yml
```

### 2. Agen Python

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r agent/requirements.txt
cp .env.example .env         # isi AGENT_DB_DSN agar sama dengan DB Laravel
pytest                       # 26 test: guardrail, http client, validator, loop
python -m agent.worker       # polling DB untuk job scan (LLM opsional via env)
```

### 3. Dashboard Laravel

Lihat [`web/README.md`](web/README.md) — cara `composer create-project` dan menaruh
file scaffold di `web/`.

---

## Struktur

```
agent/      Python: config guardrails audit db reporter tools/
            core.py (ReAct) validator.py payloads.py llm.py worker.py
web/        Laravel: app/Models app/Livewire database/migrations resources/{css,views}
config/     targets.allowlist · payloads.yml (sumber kebenaran guardrail & payload)
tests/      26 unit test: guardrail, http client, validator, loop core
docs/       PRD.md · DESIGN_GUIDELINES.md
docker-compose.yml
```

## Etika

Lihat PRD §3 dan DESIGN_GUIDELINES §5. Pengujian hanya pada sistem milik sendiri /
yang diizinkan.
