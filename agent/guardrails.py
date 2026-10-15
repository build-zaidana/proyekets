"""Guardrail keamanan-kritis. Fungsional penuh, tanpa dependensi eksternal.

Tiga penjaga, dijalankan berurutan dan GAGAL-TERTUTUP (fail closed):
  1. allowlist  — host target harus terdaftar
  2. rate limit — batasi laju request agar tidak membebani target
  3. payload    — tolak payload yang berpotensi merusak (non-destruktif saja)

Lihat DESIGN_GUIDELINES §5 & §6.4. Modul ini tidak menyentuh jaringan.
"""
from __future__ import annotations

import re
import threading
import time
from urllib.parse import urlsplit


class GuardrailError(Exception):
    """Dasar semua penolakan guardrail."""


class TargetNotAllowed(GuardrailError):
    """Host target tidak ada di allowlist."""


class RateLimited(GuardrailError):
    """Laju request melewati batas."""


class DestructivePayloadBlocked(GuardrailError):
    """Payload berpotensi merusak data/sistem target."""


def host_of(url: str) -> str:
    """Ambil 'host' atau 'host:port' dari URL, lowercase. '' kalau tak terbaca."""
    parts = urlsplit(url.strip())
    if not parts.hostname:
        return ""
    host = parts.hostname.lower()
    if parts.port:
        return f"{host}:{parts.port}"
    return host


def check_allowlist(url: str, allowed_hosts: frozenset[str]) -> None:
    """Loloskan hanya jika host (atau host:port) ada di allowlist.

    Mencocokkan dua bentuk: dengan dan tanpa port, supaya 'localhost' di allowlist
    menerima 'localhost:8080' bila ditulis demikian — tapi kecocokan harus eksplisit.
    """
    host = host_of(url)
    if not host:
        raise TargetNotAllowed(f"URL tidak punya host yang valid: {url!r}")
    bare = host.split(":", 1)[0]
    if host in allowed_hosts or bare in allowed_hosts:
        return
    raise TargetNotAllowed(
        f"Host {host!r} tidak ada di allowlist. Tambahkan lewat config/targets.allowlist."
    )


class RateLimiter:
    """Token-bucket sederhana, aman untuk banyak thread.

    `acquire()` memblokir sampai sebuah slot tersedia, menjamin laju rata-rata tidak
    melebihi `max_per_second`.
    """

    def __init__(self, max_per_second: int) -> None:
        self.min_interval = 1.0 / max(1, max_per_second)
        self._lock = threading.Lock()
        self._next_at = 0.0

    def acquire(self) -> None:
        with self._lock:
            now = time.monotonic()
            wait = self._next_at - now
            if wait > 0:
                time.sleep(wait)
                now = time.monotonic()
            self._next_at = now + self.min_interval


# Pola yang menandakan operasi berpotensi merusak DATA atau SISTEM target.
# MVP ini bersifat deteksi non-destruktif (PRD §2 Non-Goals): kita MEMBUKTIKAN
# kerentanan, tidak mengeksekusi perusakan. Payload uji agen harus lolos filter ini.
_DESTRUCTIVE_PATTERNS = [
    re.compile(p, re.IGNORECASE)
    for p in (
        r"\bdrop\s+table\b",
        r"\bdrop\s+database\b",
        r"\btruncate\s+table\b",
        r"\bdelete\s+from\b",
        r"\bupdate\s+\w+\s+set\b",
        r"\binsert\s+into\b",
        r"\bshutdown\b",
        r"\bxp_cmdshell\b",
        r";\s*rm\s+-rf",
        r"\bmkfs\b",
    )
]


def check_payload_safe(payload: str | None) -> None:
    """Tolak payload yang cocok pola merusak. `None`/kosong selalu lolos."""
    if not payload:
        return
    for pat in _DESTRUCTIVE_PATTERNS:
        if pat.search(payload):
            raise DestructivePayloadBlocked(
                f"Payload ditolak: cocok pola merusak {pat.pattern!r}. "
                "Alat ini hanya deteksi non-destruktif."
            )
