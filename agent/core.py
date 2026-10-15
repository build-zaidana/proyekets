"""Reasoning loop ReAct.

Loop deteksi berjalan DETERMINISTIK (bisa didemokan tanpa LLM): recon -> untuk tiap
form & field teks, kirim probe via tool ber-guardrail -> validator mengonfirmasi lewat
bukti pembeda -> catat temuan. Payload berasal dari katalog (data), bukan hardcode.

LLM (opsional) menambah lapisan penalaran: narasi 'Thought' dan remediasi kontekstual.
Loop tetap benar tanpa LLM.

TODO(agentic): pemilihan aksi berbasis LLM penuh — LLM memutuskan parameter & urutan
uji dari respons sebelumnya (PRD §7). Seam di `llm.propose_focus` (belum ada).
"""
from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from agent.payloads import PayloadCatalog
from agent.tools.http_client import HttpClient, HttpResult
from agent.tools.recon import Form, extract_endpoints
from agent import validator

logger = logging.getLogger("autodast.core")


@dataclass
class Step:
    seq: int
    phase: str  # thought | action | observation | blocked
    content: str


@dataclass
class Finding:
    severity: str
    confidence: str
    vuln_type: str
    location: str
    evidence: dict[str, Any] = field(default_factory=dict)
    remediation: str = ""
    cwe: str = ""


@dataclass
class ScanResult:
    steps: list[Step] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)


StepSink = Callable[[Step], None]

_SEVERITY_BY_CONFIDENCE = {"High": "High", "Medium": "Medium", "Low": "Low"}


def run_scan(
    client: HttpClient,
    target_url: str,
    *,
    catalog: PayloadCatalog,
    max_steps: int,
    on_step: StepSink | None = None,
    llm=None,
) -> ScanResult:
    result = ScanResult()

    def emit(phase: str, content: str) -> None:
        step = Step(seq=len(result.steps) + 1, phase=phase, content=content)
        result.steps.append(step)
        if on_step:
            on_step(step)

    def thought(ctx: str) -> None:
        emit("thought", _narrate(llm, ctx))

    thought(f"Mulai recon pada {target_url}.")
    page = extract_endpoints(client, target_url)
    emit("observation", f"Ditemukan {len(page.links)} link, {len(page.forms)} form.")

    forms = page.forms or []
    if not forms:
        thought("Tidak ada form untuk diuji. Selesai.")
        return result

    for form in forms:
        for fld in _text_fields(form):
            if len(result.steps) >= max_steps:
                emit("thought", f"Batas {max_steps} langkah tercapai. Berhenti.")
                return result
            _probe_field(client, catalog, form, fld, result, emit, thought, llm)

    thought(f"Selesai. {len(result.findings)} temuan tervalidasi.")
    return result


def _probe_field(client, catalog, form: Form, field_name, result, emit, thought, llm):
    loc = f"{form.method} {form.action} (param: {field_name})"

    # --- SQL injection: error-based lalu boolean-based diferensial ---
    thought(f"Uji SQLi error-based pada {field_name} di {form.action}.")
    sqli = catalog.sql_injection
    r_err = _send(client, form, field_name, sqli["error_probe"], catalog)
    emit("observation", _obs(r_err))
    verdict = validator.judge_sql_error(r_err, catalog.sql_error_signatures)

    if not verdict.vulnerable and not r_err.blocked:
        thought(f"Belum pasti. Uji boolean-based (true vs false) pada {field_name}.")
        r_true = _send(client, form, field_name, sqli["boolean_true"], catalog)
        r_false = _send(client, form, field_name, sqli["boolean_false"], catalog)
        emit("observation", f"true: {_obs(r_true)} | false: {_obs(r_false)}")
        verdict = validator.judge_boolean_differential(r_true, r_false)
        evidence = {"true": _ev(r_true), "false": _ev(r_false)}
    else:
        evidence = {"probe": _ev(r_err)}

    if verdict.vulnerable:
        result.findings.append(_finding(
            "SQL Injection", sqli.get("cwe", "CWE-89"), loc, verdict, evidence, llm,
        ))
        emit("observation", f"TEMUAN SQLi — {verdict.reason}")

    # --- Reflected XSS ---
    thought(f"Uji reflected XSS pada {field_name} di {form.action}.")
    xss = catalog.xss_reflected
    r_xss = _send(client, form, field_name, xss["probe"], catalog)
    emit("observation", _obs(r_xss))
    vx = validator.judge_reflected_xss(r_xss, xss["marker"])
    if vx.vulnerable:
        result.findings.append(_finding(
            "Reflected XSS", xss.get("cwe", "CWE-79"), loc, vx, {"probe": _ev(r_xss)}, llm,
        ))
        emit("observation", f"TEMUAN XSS — {vx.reason}")


def _send(client: HttpClient, form: Form, field_name, payload, catalog) -> HttpResult:
    """Kirim satu request: field sasaran = payload, field lain = nilai kontrol jinak."""
    control = catalog.sql_injection.get("control", "test")
    data = {f.name: control for f in form.fields if f.name}
    data[field_name] = payload
    if form.method.upper() == "POST":
        return client.send_http_request("POST", form.action, data=data)
    return client.send_http_request("GET", form.action, params=data)


def _finding(vuln_type, cwe, loc, verdict, evidence, llm) -> Finding:
    severity = {"SQL Injection": "High", "Reflected XSS": "Medium"}.get(vuln_type, "Low")
    return Finding(
        severity=severity,
        confidence=_SEVERITY_BY_CONFIDENCE.get(verdict.confidence, "Low"),
        vuln_type=vuln_type,
        location=loc,
        evidence={"reason": verdict.reason, **evidence},
        remediation=_remediation(llm, vuln_type, loc),
        cwe=cwe,
    )


def _text_fields(form: Form):
    skip = {"submit", "button", "hidden", "file", "image", "reset"}
    return [f.name for f in form.fields if f.name and f.type.lower() not in skip]


def _obs(r: HttpResult) -> str:
    if r.blocked:
        return f"DIBLOKIR guardrail: {r.error}"
    if not r.ok:
        return f"gagal: {r.error}"
    return f"HTTP {r.status_code}, {len(r.body_snippet)} byte"


def _ev(r: HttpResult) -> dict:
    return {
        "status": r.status_code,
        "blocked": r.blocked,
        "body_snippet": r.body_snippet[:512],
    }


def _narrate(llm, ctx: str) -> str:
    if llm is None:
        return ctx
    try:
        return llm.narrate(ctx) or ctx
    except Exception:  # LLM gagal tak boleh menjatuhkan scan
        logger.warning("LLM narrate gagal; pakai teks default", exc_info=True)
        return ctx


def _remediation(llm, vuln_type: str, loc: str) -> str:
    default = {
        "SQL Injection": (
            "Gunakan prepared statement / parameterized query; jangan rangkai query "
            "dengan string. Validasi & escape input di backend."
        ),
        "Reflected XSS": (
            "Escape/encode output sesuai konteks (HTML/attr/JS) di sisi server; "
            "terapkan Content-Security-Policy; sanitasi input di backend."
        ),
    }.get(vuln_type, "Terapkan validasi input dan output encoding yang tepat.")
    if llm is None:
        return default
    try:
        return llm.remediation(vuln_type, loc) or default
    except Exception:
        logger.warning("LLM remediation gagal; pakai teks default", exc_info=True)
        return default
