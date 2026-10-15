"""Adapter LLM provider-agnostik (PRD: OpenAI/Gemini).

Dipakai sebagai lapisan PENALARAN opsional di atas loop deteksi deterministik
(agent/core.py): menarasikan 'Thought' dan menyusun teks remediasi kontekstual.
Loop tetap jalan tanpa LLM (llm=None) untuk demo lab tanpa biaya token.

Seam untuk pengembangan lanjut: strategi pemilihan aksi berbasis LLM (memilih
parameter & urutan uji dari respons sebelumnya) diisi di `propose_focus`.
"""
from __future__ import annotations

from typing import Protocol


class LLMAdapter(Protocol):
    """Antarmuka minimal. Implementasi konkret membungkus SDK provider."""

    def narrate(self, context: str) -> str:
        """Satu kalimat 'Thought' manusiawi dari konteks langkah saat ini."""

    def remediation(self, vuln_type: str, location: str) -> str:
        """Saran remediasi tingkat kode, full-stack (DESIGN_GUIDELINES §4.4)."""


class OpenAICompatibleAdapter:
    """Referensi adapter untuk API bergaya OpenAI (chat completions).

    Banyak provider (termasuk gateway Gemini bergaya OpenAI) kompatibel. Impor SDK
    bersifat lokal/opsional agar paket tetap bisa diuji tanpa dependensi LLM.
    """

    _SYSTEM = (
        "You are a senior web security engineer assisting an AUTHORIZED, LOCAL "
        "penetration test against an intentionally vulnerable lab target. Respond "
        "concisely and factually. Never suggest destructive actions."
    )

    def __init__(self, model: str, api_key: str, base_url: str | None = None) -> None:
        from openai import OpenAI  # dependensi opsional

        self._model = model
        self._client = OpenAI(api_key=api_key, base_url=base_url)

    def _ask(self, prompt: str) -> str:
        resp = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": self._SYSTEM},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
        return (resp.choices[0].message.content or "").strip()

    def narrate(self, context: str) -> str:
        return self._ask(f"Dalam satu kalimat, jelaskan langkah uji berikut: {context}")

    def remediation(self, vuln_type: str, location: str) -> str:
        return self._ask(
            f"Beri remediasi tingkat kode (full-stack) yang spesifik untuk {vuln_type} "
            f"pada {location}. Sebut perbaikan backend/DB/frontend yang relevan, ringkas."
        )


def build_from_env(settings) -> LLMAdapter | None:
    """Bangun adapter dari env, atau None bila tidak dikonfigurasi (mode deterministik)."""
    import os

    provider = os.getenv("LLM_PROVIDER", "").lower()
    model = os.getenv("LLM_MODEL", "")
    if provider in {"openai", "gemini"} and model:
        key = os.getenv("OPENAI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""
        if not key:
            return None
        base = os.getenv("LLM_BASE_URL") or None
        try:
            return OpenAICompatibleAdapter(model=model, api_key=key, base_url=base)
        except ImportError:
            return None
    return None
