"""Audit log request: cermin JSONL lokal + (opsional) tabel DB.

Setiap request yang DIKIRIM maupun DITOLAK dicatat. Auditabilitas = syarat akademis
(PRD §3 S5). Jangan pernah mencatat secret/kredensial sebagai nilai.
"""
from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

logger = logging.getLogger("autodast.audit")

Verdict = Literal["sent", "blocked"]


@dataclass(frozen=True)
class AuditRecord:
    ts: str
    method: str
    url: str
    verdict: Verdict
    reason: str = ""
    scan_id: int | None = None


class AuditLog:
    """Tulis record audit. `sink_db` opsional dipanggil untuk persist ke tabel."""

    def __init__(self, jsonl_path: str | Path, sink_db=None) -> None:
        self.path = Path(jsonl_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._sink_db = sink_db

    def record(
        self,
        *,
        method: str,
        url: str,
        verdict: Verdict,
        reason: str = "",
        scan_id: int | None = None,
    ) -> AuditRecord:
        rec = AuditRecord(
            ts=datetime.now(timezone.utc).isoformat(),
            method=method.upper(),
            url=url,
            verdict=verdict,
            reason=reason,
            scan_id=scan_id,
        )
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(asdict(rec), ensure_ascii=False) + "\n")
        if self._sink_db is not None:
            try:
                self._sink_db(rec)
            except Exception:  # audit DB gagal tak boleh menjatuhkan scan
                logger.exception("Gagal menulis audit ke DB (JSONL tetap tersimpan)")
        return rec
