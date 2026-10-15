"""Reasoning loop ReAct — SKELETON.

Di sinilah LLM memutuskan langkah uji berdasarkan respons sebelumnya (PRD §7).
Fungsi di bawah sengaja belum lengkap: ia mendefinisikan KONTRAK dan ALUR, bukan
implementasi LLM. Isi bagian ber-TODO saat mengintegrasikan provider (LangGraph).

Prinsip yang HARUS dijaga saat mengisi:
  - Setiap request keluar WAJIB lewat HttpClient.send_http_request (ber-guardrail).
  - Katalog payload uji di-load dari konfigurasi/berkas, BUKAN di-hardcode di sini.
  - Sebuah temuan hanya dicatat bila ada bukti pembeda (differential/signature),
    bukan sekadar status code (kriteria anti-false-positive, PRD §7).
"""
from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from agent.tools.http_client import HttpClient
from agent.tools.recon import extract_endpoints

logger = logging.getLogger("autodast.core")


@dataclass
class Step:
    """Satu langkah ReAct yang akan ditulis ke tabel agent_steps."""

    seq: int
    phase: str  # 'thought' | 'action' | 'observation' | 'blocked'
    content: str


@dataclass
class Finding:
    """Temuan tervalidasi yang akan ditulis ke tabel findings."""

    severity: str  # Critical | High | Medium | Low | Info
    confidence: str  # High | Medium | Low
    vuln_type: str
    location: str
    evidence: dict[str, Any] = field(default_factory=dict)
    remediation: str = ""
    cwe: str = ""


@dataclass
class ScanResult:
    steps: list[Step] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)


# StepSink: callback yang menulis tiap langkah ke DB saat terjadi (streaming ke UI).
StepSink = Callable[[Step], None]


def run_scan(
    client: HttpClient,
    target_url: str,
    *,
    max_steps: int,
    on_step: StepSink | None = None,
    llm=None,
) -> ScanResult:
    """Jalankan satu siklus recon -> reason -> validate pada target.

    Parameter `llm` adalah adaptor provider-agnostik (lihat `LLMAdapter`). Saat masih
    None, fungsi hanya melakukan recon dan berhenti — cukup untuk menguji pipa DB/UI
    tanpa biaya token.
    """
    result = ScanResult()

    def emit(phase: str, content: str) -> None:
        step = Step(seq=len(result.steps) + 1, phase=phase, content=content)
        result.steps.append(step)
        if on_step is not None:
            on_step(step)

    emit("thought", f"Mulai recon pada {target_url}.")
    page = extract_endpoints(client, target_url)
    emit(
        "observation",
        f"Ditemukan {len(page.links)} link, {len(page.forms)} form.",
    )

    if llm is None:
        emit("thought", "LLM belum dikonfigurasi — berhenti setelah recon (mode dry).")
        return result

    # TODO(core): loop ReAct sebenarnya.
    #   for _ in range(max_steps):
    #       thought = llm.next_thought(context)         # apa yang diuji berikutnya
    #       action  = llm.choose_action(thought)        # tool + argumen (payload dari katalog)
    #       observation = dispatch(client, action)      # WAJIB lewat client ber-guardrail
    #       if validator.is_vulnerable(action, observation, control_run):
    #           result.findings.append(build_finding(...))  # hanya bila ada bukti pembeda
    #       if llm.is_done(context): break
    raise NotImplementedError(
        "Loop ReAct belum diimplementasikan. Lihat TODO(core) dan DESIGN_GUIDELINES §6."
    )


class LLMAdapter:
    """Antarmuka provider-agnostik (OpenAI/Gemini/dll). Diisi saat integrasi.

    Memisahkan loop ReAct dari SDK provider agar mudah ditukar & diuji.
    """

    def next_thought(self, context: dict) -> str:  # pragma: no cover - skeleton
        raise NotImplementedError

    def choose_action(self, thought: str) -> dict:  # pragma: no cover - skeleton
        raise NotImplementedError

    def is_done(self, context: dict) -> bool:  # pragma: no cover - skeleton
        raise NotImplementedError
