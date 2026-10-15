"""Validator kerentanan — logika deterministik, inti anti-false-positive (PRD §7).

Sebuah temuan hanya sah bila ada BUKTI PEMBEDA, bukan sekadar status code:
  - SQLi error-based  : respons memuat signature error SQL.
  - SQLi boolean-based : respons payload 'true' berbeda nyata dari 'false'/control.
  - XSS reflected      : marker payload terefleksi tak ter-escape di body.

Modul murni: tanpa jaringan, tanpa LLM. Semua bisa diuji unit.
"""
from __future__ import annotations

import html
from dataclasses import dataclass

from agent.tools.http_client import HttpResult


@dataclass(frozen=True)
class Verdict:
    vulnerable: bool
    confidence: str  # High | Medium | Low
    reason: str


def detect_sql_error(result: HttpResult, signatures: tuple[str, ...]) -> str | None:
    """Kembalikan signature error SQL pertama yang cocok di body, atau None."""
    body = (result.body_snippet or "").lower()
    for sig in signatures:
        if sig and sig in body:
            return sig
    return None


def judge_sql_error(result: HttpResult, signatures: tuple[str, ...]) -> Verdict:
    sig = detect_sql_error(result, signatures)
    if sig:
        return Verdict(True, "High", f"Signature error SQL terdeteksi: {sig!r}")
    return Verdict(False, "Low", "Tidak ada signature error SQL.")


def judge_boolean_differential(
    true_result: HttpResult,
    false_result: HttpResult,
    *,
    min_len_delta: int = 32,
) -> Verdict:
    """Bandingkan respons payload 'true' vs 'false'.

    Beda status code, atau selisih panjang body melewati ambang, menandakan query
    terpengaruh input — indikasi SQLi boolean-based.
    """
    if not (true_result.ok and false_result.ok):
        return Verdict(False, "Low", "Salah satu request gagal/diblokir.")

    if true_result.status_code != false_result.status_code:
        return Verdict(
            True, "Medium",
            f"Status berbeda: {true_result.status_code} vs {false_result.status_code}.",
        )

    delta = abs(len(true_result.body_snippet) - len(false_result.body_snippet))
    if delta >= min_len_delta:
        return Verdict(True, "Medium", f"Selisih panjang body {delta} byte (>= {min_len_delta}).")

    return Verdict(False, "Low", "Respons true/false serupa — tidak meyakinkan.")


def judge_reflected_xss(result: HttpResult, marker: str) -> Verdict:
    """Marker terefleksi APA ADANYA (tak ter-escape) = reflected XSS.

    Kalau marker muncul tapi sudah di-escape HTML, itu BUKAN temuan (aplikasi
    meng-encode output dengan benar) — justru menekan false positive.
    """
    if not result.ok or not result.body_snippet:
        return Verdict(False, "Low", "Tidak ada body respons.")

    body = result.body_snippet
    raw_marker = f"<script>{marker}</script>"
    if raw_marker in body:
        return Verdict(True, "High", "Payload <script> terefleksi tanpa di-escape.")

    if html.escape(raw_marker) in body:
        return Verdict(False, "Low", "Marker terefleksi tapi sudah di-escape (aman).")

    return Verdict(False, "Low", "Marker tidak terefleksi.")
