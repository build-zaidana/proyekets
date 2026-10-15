"""Pemuatan konfigurasi: environment + allowlist target.

Allowlist file adalah sumber kebenaran untuk guardrail (DESIGN_GUIDELINES §5).
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # dotenv opsional di produksi
    pass


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def load_allowlist(path: str | Path) -> frozenset[str]:
    """Baca allowlist host. Baris kosong & diawali '#' diabaikan.

    Mengembalikan set host ter-normalisasi (lowercase, tanpa spasi). Kalau file tidak
    ada, kembalikan set kosong — guardrail akan menolak semua (fail closed).
    """
    p = Path(path)
    if not p.is_file():
        return frozenset()
    hosts = set()
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        hosts.add(line.lower())
    return frozenset(hosts)


@dataclass(frozen=True)
class Settings:
    allowlist_path: str = os.getenv("ALLOWLIST_PATH", "config/targets.allowlist")
    max_requests_per_second: int = _env_int("MAX_REQUESTS_PER_SECOND", 3)
    max_agent_steps: int = _env_int("MAX_AGENT_STEPS", 25)
    http_timeout_seconds: int = _env_int("HTTP_TIMEOUT_SECONDS", 10)
    response_body_max_bytes: int = _env_int("RESPONSE_BODY_MAX_BYTES", 4096)
    audit_log_path: str = os.getenv("AUDIT_LOG_PATH", "audit/requests.jsonl")
    # DB (kontrak dengan Laravel). DSN SQLAlchemy, mis.
    # mysql+mysqlconnector://user:pass@127.0.0.1:3306/autodast
    db_dsn: str = os.getenv("AGENT_DB_DSN", "")
    poll_interval_seconds: int = _env_int("WORKER_POLL_INTERVAL", 2)

    allowed_hosts: frozenset[str] = field(default_factory=frozenset)

    @classmethod
    def load(cls) -> "Settings":
        base = cls()
        return cls(
            allowlist_path=base.allowlist_path,
            max_requests_per_second=base.max_requests_per_second,
            max_agent_steps=base.max_agent_steps,
            http_timeout_seconds=base.http_timeout_seconds,
            response_body_max_bytes=base.response_body_max_bytes,
            audit_log_path=base.audit_log_path,
            db_dsn=base.db_dsn,
            poll_interval_seconds=base.poll_interval_seconds,
            allowed_hosts=load_allowlist(base.allowlist_path),
        )
