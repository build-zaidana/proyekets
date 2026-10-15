"""send_http_request — satu-satunya pintu keluar jaringan, ber-guardrail.

Urutan gagal-tertutup: allowlist -> rate limit -> filter payload -> audit -> kirim.
`requests` HANYA diimpor di modul ini (DESIGN_GUIDELINES §6.4).
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field

import requests

from agent.audit import AuditLog
from agent.guardrails import (
    GuardrailError,
    RateLimiter,
    check_allowlist,
    check_payload_safe,
)

logger = logging.getLogger("autodast.http")


@dataclass
class HttpResult:
    """Hasil terstruktur — dibaca agen maupun ditulis ke DB (bukan string mentah)."""

    ok: bool
    status_code: int | None = None
    headers: dict[str, str] = field(default_factory=dict)
    body_snippet: str = ""
    elapsed_ms: float | None = None
    blocked: bool = False
    error: str = ""


class HttpClient:
    def __init__(
        self,
        *,
        allowed_hosts: frozenset[str],
        rate_limiter: RateLimiter,
        audit: AuditLog,
        timeout_seconds: int,
        body_max_bytes: int,
        scan_id: int | None = None,
    ) -> None:
        self._allowed = allowed_hosts
        self._rate = rate_limiter
        self._audit = audit
        self._timeout = timeout_seconds
        self._body_max = body_max_bytes
        self._scan_id = scan_id
        self._session = requests.Session()

    def send_http_request(
        self,
        method: str,
        url: str,
        *,
        params: dict | None = None,
        data: dict | None = None,
        headers: dict | None = None,
    ) -> HttpResult:
        """Kirim satu request HTTP setelah lolos semua guardrail.

        Guardrail yang gagal -> request TIDAK dikirim, dicatat sebagai 'blocked',
        dan hasil ber-`blocked=True` dikembalikan (bukan exception yang menjatuhkan
        loop agen — agen boleh menalar dari penolakan itu).
        """
        payload_str = _stringify_payload(params, data)
        try:
            check_allowlist(url, self._allowed)
            check_payload_safe(payload_str)
        except GuardrailError as exc:
            self._audit.record(
                method=method, url=url, verdict="blocked",
                reason=str(exc), scan_id=self._scan_id,
            )
            return HttpResult(ok=False, blocked=True, error=str(exc))

        self._rate.acquire()
        self._audit.record(
            method=method, url=url, verdict="sent", scan_id=self._scan_id,
        )
        try:
            resp = self._session.request(
                method=method.upper(), url=url, params=params, data=data,
                headers=headers, timeout=self._timeout, allow_redirects=False,
            )
        except requests.RequestException as exc:
            logger.warning("Request gagal: %s", exc)
            return HttpResult(ok=False, error=str(exc))

        body = resp.text[: self._body_max]
        if len(resp.text) > self._body_max:
            body += f"\n... [dipotong, {len(resp.text)} byte]"
        return HttpResult(
            ok=True,
            status_code=resp.status_code,
            headers=dict(resp.headers),
            body_snippet=body,
            elapsed_ms=resp.elapsed.total_seconds() * 1000,
        )


def _stringify_payload(params: dict | None, data: dict | None) -> str:
    parts = []
    for d in (params, data):
        if d:
            parts.extend(str(v) for v in d.values())
    return " ".join(parts)
