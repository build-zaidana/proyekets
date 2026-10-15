"""Akses DB — kontrak antara worker Python dan Laravel (DESIGN_GUIDELINES §6.3).

Worker membaca job dari `scans` dan menulis `agent_steps`, `findings`, `audit_log`.
Skema dimiliki oleh migration Laravel; di sini hanya query.

Pakai SQLAlchemy Core (tanpa ORM) agar ringan. Butuh DSN di env AGENT_DB_DSN, mis:
  mysql+mysqlconnector://user:pass@127.0.0.1:3306/autodast
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger("autodast.db")


def _now() -> str:
    """Timestamp UTC sebagai string — portabel MySQL & SQLite (hindari NOW())."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


class Database:
    def __init__(self, dsn: str) -> None:
        if not dsn:
            raise ValueError(
                "AGENT_DB_DSN kosong. Set DSN MySQL agar worker bisa jalan."
            )
        from sqlalchemy import create_engine  # impor lokal: dependensi opsional

        self._engine = create_engine(dsn, pool_pre_ping=True, future=True)

    def claim_queued_scan(self) -> dict[str, Any] | None:
        """Klaim satu scan 'queued' secara atomik -> 'running'. None bila tak ada.

        Update bersyarat mencegah dua worker mengambil scan yang sama.
        """
        from sqlalchemy import text

        with self._engine.begin() as conn:
            row = conn.execute(
                text(
                    "SELECT s.id, t.base_url FROM scans s "
                    "JOIN targets t ON t.id = s.target_id "
                    "WHERE s.status = 'queued' ORDER BY s.id LIMIT 1"
                )
            ).mappings().first()
            if row is None:
                return None
            updated = conn.execute(
                text(
                    "UPDATE scans SET status='running', started_at=:ts "
                    "WHERE id=:id AND status='queued'"
                ),
                {"id": row["id"], "ts": _now()},
            )
            if updated.rowcount != 1:
                return None  # worker lain mendahului
            return {"id": row["id"], "base_url": row["base_url"]}

    def insert_step(self, scan_id: int, seq: int, phase: str, content: str) -> None:
        from sqlalchemy import text

        with self._engine.begin() as conn:
            conn.execute(
                text(
                    "INSERT INTO agent_steps (scan_id, seq, phase, content, created_at) "
                    "VALUES (:scan_id, :seq, :phase, :content, :ts)"
                ),
                {"scan_id": scan_id, "seq": seq, "phase": phase,
                 "content": content, "ts": _now()},
            )

    def insert_finding(self, scan_id: int, finding: dict[str, Any]) -> None:
        from sqlalchemy import text

        with self._engine.begin() as conn:
            conn.execute(
                text(
                    "INSERT INTO findings "
                    "(scan_id, severity, confidence, vuln_type, cwe, location, "
                    " evidence, remediation, created_at) VALUES "
                    "(:scan_id, :severity, :confidence, :vuln_type, :cwe, :location, "
                    " :evidence, :remediation, :ts)"
                ),
                {
                    "scan_id": scan_id,
                    "ts": _now(),
                    "evidence": json.dumps(finding.get("evidence", {})),
                    **{
                        k: finding.get(k, "")
                        for k in ("severity", "confidence", "vuln_type", "cwe",
                                  "location", "remediation")
                    },
                },
            )

    def insert_audit(self, rec) -> None:
        from sqlalchemy import text

        with self._engine.begin() as conn:
            conn.execute(
                text(
                    "INSERT INTO audit_log (scan_id, ts, method, url, verdict, reason) "
                    "VALUES (:scan_id, :ts, :method, :url, :verdict, :reason)"
                ),
                {
                    "scan_id": rec.scan_id, "ts": rec.ts, "method": rec.method,
                    "url": rec.url, "verdict": rec.verdict, "reason": rec.reason,
                },
            )

    def set_scan_status(self, scan_id: int, status: str, reason: str = "") -> None:
        from sqlalchemy import text

        with self._engine.begin() as conn:
            conn.execute(
                text(
                    "UPDATE scans SET status=:status, finished_at=:ts WHERE id=:id"
                ),
                {"status": status, "id": scan_id, "ts": _now()},
            )
            if reason:
                logger.info("Scan %s -> %s (%s)", scan_id, status, reason)
