# PRD — Agentic AI DAST untuk Analisis Kerentanan Aplikasi Web Secara Otonom

| | |
| --- | --- |
| **Nama Produk** | AutoDAST-Agent (nama kerja) |
| **Jenis** | Tugas Akhir / Final Project Informatika |
| **Versi Dokumen** | 0.1 (Draf PRD) |
| **Tanggal** | 2026-10-13 |
| **Penulis** | build.zaidana |
| **Status** | Draft — MVP scoping |

---

## 1. Latar Belakang & Masalah

Pengujian keamanan web konvensional (DAST berbasis *rule*, misalnya varian gratis Burp Suite / ZAP) memiliki tiga kelemahan utama:

1. **False positive tinggi** — payload dikirim membabi-buta tanpa memahami konteks respons.
2. **Buta terhadap logika bisnis** — *rule* statis tidak bisa menalar alur multi-langkah (mis. IDOR, broken access control antar-peran).
3. **Tidak adaptif** — keputusan payload berikutnya tidak dipengaruhi oleh respons sebelumnya.

Pentester manusia mengatasi ini dengan *intuisi*: membaca respons, membentuk hipotesis, lalu menyesuaikan serangan. Proyek ini mereproduksi pola pikir tersebut menggunakan **Agentic AI** — LLM yang dibekali *tools* eksekusi dan beroperasi dalam *reasoning loop* (ReAct).

### Pernyataan Masalah
> Bagaimana membangun agen AI otonom yang dapat memetakan aplikasi web, memilih payload uji secara dinamis berdasarkan respons HTTP, memvalidasi kerentanan dengan tingkat false positive rendah, dan menghasilkan laporan remediasi yang kontekstual?

---

## 2. Tujuan & Non-Tujuan

### 2.1 Tujuan (Goals)
- **G1** — Agen melakukan *reconnaissance* (crawling URL, parameter, form, header) secara mandiri.
- **G2** — Mengintegrasikan *tools* keamanan kustom berbasis Python ke dalam *reasoning loop* LLM via *function calling*.
- **G3** — Mendeteksi & memvalidasi minimal 2 kelas kerentanan OWASP (SQLi & XSS) pada target uji dengan bukti (evidence) yang dapat diverifikasi.
- **G4** — Menghasilkan laporan temuan + rekomendasi remediasi tingkat kode (full-stack).

### 2.2 Non-Tujuan (Non-Goals) — untuk MVP
- Bukan pengganti Burp Suite penuh; tidak menargetkan semua kelas kerentanan.
- Tidak melakukan eksploitasi destruktif (DROP, data exfiltration, RCE penuh) — hanya **deteksi & pembuktian** non-destruktif.
- Tidak diarahkan ke target publik/pihak ketiga — **hanya target legal lokal**.
- Tidak melakukan bypass WAF/anti-deteksi tingkat lanjut.

---

## 3. Batasan Etis, Legal & Keamanan (WAJIB)

> Komponen ini bersifat *hard requirement*, bukan opsional. Tanpa ini, proyek tidak boleh dijalankan.

- **S1 — Allowlist target.** Agen hanya boleh mengirim request ke host yang terdaftar eksplisit pada file konfigurasi (`targets.allowlist`). Request ke host di luar daftar **ditolak di level tool**, bukan hanya di prompt.
- **S2 — Target legal saja.** Pengujian dilakukan terhadap aplikasi yang memang dirancang untuk diserang (DVWA, OWASP Juice Shop) yang berjalan **lokal di Docker** (`localhost`/`127.0.0.1`/jaringan Docker internal).
- **S3 — Non-destruktif.** Payload dibatasi pada pembuktian kerentanan (mis. `' OR '1'='1`, `<script>alert(1)</script>`). Operasi merusak (DELETE/DROP/UPDATE massal, shell) dilarang dan di-filter.
- **S4 — Rate limiting.** Tool HTTP membatasi laju request (mis. maks N req/detik) untuk mencegah DoS tak disengaja.
- **S5 — Audit log.** Setiap request yang dikirim agen dicatat (timestamp, method, URL, payload, respons) untuk auditabilitas & reproduksibilitas akademis.
- **S6 — Persetujuan.** Dokumentasi menyertakan pernyataan bahwa semua pengujian dilakukan pada sistem milik sendiri / yang diizinkan.

---

## 4. Persona & Pengguna

| Persona | Kebutuhan |
| --- | --- |
| **Mahasiswa/Peneliti (primary)** | Menguji aplikasi lab sendiri, mempelajari alur agen, mengumpulkan data eksperimen untuk skripsi. |
| **Dosen Penguji** | Melihat laporan terstruktur, bukti deteksi, dan metrik akurasi (TP/FP). |
| **Developer (konsumen laporan)** | Mendapat rekomendasi remediasi tingkat kode yang actionable. |

---

## 5. Arsitektur & Modul (MVP)

```
                 ┌──────────────────────────────────────┐
                 │            Orchestrator (Agent)        │
                 │     LLM + ReAct Reasoning Loop         │
                 │  System prompt: "Senior Web Sec Eng"   │
                 └───────┬───────────────────────┬────────┘
                         │ function calling       │
         ┌───────────────┴──────┐        ┌────────┴───────────┐
         ▼                      ▼        ▼                    ▼
  ┌─────────────┐      ┌──────────────┐ ┌───────────────┐ ┌──────────────┐
  │ Recon Agent │      │ Scanner Tools│ │ Analyzer Logic│ │  Reporter    │
  │ extract_    │      │ send_http_   │ │ (di dalam LLM │ │  (LLM →      │
  │ endpoints   │      │ request      │ │  reasoning)   │ │  Markdown)   │
  │ analyze_form│      │ (allowlisted)│ │               │ │              │
  └─────────────┘      └──────────────┘ └───────────────┘ └──────────────┘
                         │
                         ▼
                 ┌──────────────┐        ┌─────────────────────────┐
                 │ Target Legal │        │ Audit Log + Evidence DB │
                 │ (Docker/DVWA)│        │   (JSON / SQLite)        │
                 └──────────────┘        └─────────────────────────┘
```

| Modul | Peran | Stack |
| --- | --- | --- |
| **Recon Agent** | Mengumpulkan URL, parameter form, header dari target. | Python `requests`, `BeautifulSoup`, Playwright (jika butuh render JS) |
| **Scanner Tools** | Fungsi Python terkontrol yang dipanggil agen untuk mengirim request modifikasi (GET/POST). | `requests` + wrapper allowlist/rate-limit |
| **Analyzer (reasoning)** | "Otak" — membaca respons HTTP/HTML, membentuk hipotesis, menyimpulkan kerentanan. | LangChain / LangGraph + LLM |
| **Reporter** | Menerjemahkan temuan teknis → laporan + remediasi full-stack. | LLM → template Markdown/HTML |

---

## 6. Spesifikasi Tools (Function Calling)

### 6.1 `extract_endpoints(url: str) -> list[Endpoint]`
- **Input:** URL dalam allowlist.
- **Output:** daftar link, path, parameter query yang ditemukan.
- **Catatan:** batasi kedalaman crawl (mis. depth ≤ 2) untuk MVP.

### 6.2 `analyze_form(url: str) -> list[Form]`
- **Output:** metode (GET/POST), action, daftar field input beserta tipe & nama.
- Digunakan agen untuk menentukan titik injeksi.

### 6.3 `send_http_request(method, url, params|data, headers) -> HttpResponse`
- **Output:** `status_code`, `headers`, cuplikan `body` (dipotong, mis. 4 KB), `elapsed_ms`.
- **Guardrail:** cek allowlist → cek rate limit → cek blacklist payload destruktif → log → kirim.
- Satu-satunya pintu keluar jaringan agen.

> Prinsip desain: LLM **tidak** memegang socket/jaringan langsung. Semua I/O jaringan melewati tool yang di-*guardrail*.

---

## 7. Reasoning Loop (ReAct) — Contoh Alur

```
Thought:      Ditemukan form login dengan field `username`, `password` (POST).
              Coba deteksi SQLi error-based pada `username`.
Action:       send_http_request(POST, /login, {username: "' OR '1'='1", password: "x"})
Observation:  HTTP 500 — body memuat "You have an error in your SQL syntax"
Thought:      Pesan error SQL bocor → indikasi kuat SQLi error-based.
              Validasi dengan payload pembeda (true vs false).
Action:       send_http_request(... username: "x' AND '1'='2")   // kontrol
Observation:  HTTP 200, tidak ada error → perilaku berbeda terkonfirmasi.
Conclusion:   VULN: SQL Injection (error-based) di param `username` /login.
              Confidence: High. Evidence: 2 request/response tersimpan.
```

Kriteria validasi untuk menekan false positive: kerentanan hanya dilaporkan bila ada **sinyal pembeda** (differential response, error signature, atau refleksi payload yang ter-render), bukan sekadar status code.

---

## 8. Output / Laporan

Format laporan (Markdown + opsional HTML):

1. **Ringkasan Eksekutif** — jumlah temuan per severity.
2. **Daftar Temuan**, per item:
   - Judul & klasifikasi (OWASP Top 10 / CWE).
   - Lokasi (URL + parameter).
   - Severity & confidence.
   - **Evidence** — request & response yang membuktikan.
   - **Remediasi full-stack** — perbaikan di tingkat kode (mis. *prepared statement*, *output encoding*, *input validation*) + sisi frontend/backend.
3. **Lampiran** — audit log lengkap request yang dikirim.

---

## 9. Scope Kerentanan MVP

| Kelas | MVP? | Metode deteksi |
| --- | --- | --- |
| SQL Injection (error/boolean-based) | ✅ | Error signature + differential response |
| Reflected XSS | ✅ | Refleksi payload tak ter-escape di body respons |
| Security misconfiguration (header hilang) | ✅ (ringan) | Cek absennya CSP/X-Frame-Options/HSTS |
| Stored XSS, CSRF, IDOR, SSRF | ❌ (future) | — |

---

## 10. Metrik Keberhasilan

- **M1 — Akurasi deteksi:** TP/FP diukur terhadap *ground truth* DVWA (yang kerentanannya sudah diketahui). Target MVP: recall ≥ 70% untuk SQLi & reflected XSS pada level "low/medium" DVWA.
- **M2 — False positive rate** < 30% pada MVP.
- **M3 — Otonomi:** agen menyelesaikan siklus recon→scan→report tanpa intervensi manual untuk satu target.
- **M4 — Kualitas laporan:** setiap temuan menyertakan evidence + remediasi yang benar secara teknis (dinilai kualitatif oleh penguji).

---

## 11. Rencana Pengembangan (Milestone)

| Fase | Deliverable | Perkiraan |
| --- | --- | --- |
| **F0 — Setup** | Env Python, framework agentic (LangChain/LangGraph), koneksi LLM, Docker DVWA/Juice Shop, allowlist config. | Minggu 1–2 |
| **F1 — Tools dasar** | `extract_endpoints`, `analyze_form`, `send_http_request` + guardrail + audit log. | Minggu 3–4 |
| **F2 — Reasoning loop** | Integrasi ReAct, system prompt, deteksi SQLi. | Minggu 5–6 |
| **F3 — Perluasan deteksi** | Reflected XSS + header check + logika validasi false positive. | Minggu 7–8 |
| **F4 — Reporter** | Generator laporan + remediasi full-stack. | Minggu 9 |
| **F5 — Evaluasi** | Eksperimen akurasi (TP/FP) pada DVWA, penyusunan bab hasil. | Minggu 10–11 |
| **F6 — Dokumentasi** | Penulisan laporan skripsi, demo, revisi. | Minggu 12 |

---

## 12. Stack Teknologi

- **Bahasa:** Python 3.11+
- **Agentic framework:** LangChain atau LangGraph (disarankan LangGraph untuk kontrol state loop yang eksplisit).
- **LLM:** provider API (OpenAI / Gemini) — konfigurasi via `.env`, model dapat ditukar.
- **HTTP & parsing:** `requests`, `BeautifulSoup`, `Playwright` (opsional, untuk SPA ber-JS).
- **Target uji:** DVWA / OWASP Juice Shop via Docker Compose.
- **Penyimpanan evidence/log:** JSON atau SQLite.

---

## 13. Risiko & Mitigasi

| Risiko | Dampak | Mitigasi |
| --- | --- | --- |
| LLM berhalusinasi menyimpulkan vuln palsu | FP tinggi | Wajibkan evidence + validasi diferensial sebelum dilaporkan. |
| Biaya token LLM membengkak | Budget | Potong body respons, batasi iterasi loop (maks N langkah), cache. |
| Agen keluar dari allowlist | Legal/etis | Enforcement di level tool (hard block), bukan hanya prompt. |
| Crawl tak terbatas | DoS tak sengaja | Batas depth + rate limit. |
| Playwright berat untuk MVP | Kompleksitas | Mulai dengan `requests`/`BeautifulSoup`; Playwright hanya jika target butuh render JS. |

---

## 14. Pertanyaan Terbuka

1. Satu agen monolitik vs multi-agen (recon / scanner / reporter terpisah)? → MVP: satu orchestrator, tools terpisah.
2. Perlukah fine-tuning atau cukup prompting? → MVP: cukup prompting + few-shot.
3. Target evaluasi tambahan selain DVWA (mis. bWAPP, WebGoat)? → opsional pasca-MVP.

---

*Dokumen ini adalah draf PRD untuk keperluan akademis. Semua pengujian keamanan dilakukan secara eksklusif pada target lab legal milik sendiri.*
