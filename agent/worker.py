"""Worker: polling DB, jalankan scan, tulis hasil balik. `python -m agent.worker`.

Loop: klaim scan 'queued' -> validasi target vs allowlist -> jalankan core.run_scan,
streaming tiap langkah ke agent_steps -> tulis findings -> set status akhir.

Guardrail asli tetap di dalam tool (§5). Worker hanya menegakkan ulang allowlist lebih
awal agar scan ilegal tidak pernah dimulai.
"""
from __future__ import annotations

import logging
import time

from agent import llm as llm_mod
from agent.audit import AuditLog
from agent.config import Settings
from agent.core import run_scan
from agent.db import Database
from agent.guardrails import RateLimiter, TargetNotAllowed, check_allowlist
from agent.payloads import PayloadCatalog
from agent.tools.http_client import HttpClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")
logger = logging.getLogger("autodast.worker")


def process_one(
    settings: Settings, db: Database, scan: dict, catalog: PayloadCatalog, llm
) -> None:
    scan_id, target = scan["id"], scan["base_url"]

    try:
        check_allowlist(target, settings.allowed_hosts)
    except TargetNotAllowed as exc:
        db.set_scan_status(scan_id, "blocked", str(exc))
        return

    audit = AuditLog(settings.audit_log_path, sink_db=db.insert_audit)
    client = HttpClient(
        allowed_hosts=settings.allowed_hosts,
        rate_limiter=RateLimiter(settings.max_requests_per_second),
        audit=audit,
        timeout_seconds=settings.http_timeout_seconds,
        body_max_bytes=settings.response_body_max_bytes,
        scan_id=scan_id,
    )

    def on_step(step) -> None:
        db.insert_step(scan_id, step.seq, step.phase, step.content)

    try:
        result = run_scan(
            client, target, catalog=catalog,
            max_steps=settings.max_agent_steps, on_step=on_step, llm=llm,
        )
        for f in result.findings:
            db.insert_finding(scan_id, f.__dict__)
        db.set_scan_status(scan_id, "done")
    except Exception as exc:  # noqa: BLE001 - worker harus tetap hidup
        logger.exception("Scan %s gagal", scan_id)
        db.set_scan_status(scan_id, "error", str(exc))


def main() -> None:
    settings = Settings.load()
    if not settings.allowed_hosts:
        logger.warning("Allowlist kosong — semua target akan ditolak (fail closed).")
    db = Database(settings.db_dsn)
    catalog = PayloadCatalog.load()
    llm = llm_mod.build_from_env(settings)
    logger.info(
        "Worker siap. Polling tiap %ss. LLM: %s.",
        settings.poll_interval_seconds, "aktif" if llm else "nonaktif (mode deterministik)",
    )
    while True:
        scan = db.claim_queued_scan()
        if scan is None:
            time.sleep(settings.poll_interval_seconds)
            continue
        logger.info("Mengerjakan scan %s -> %s", scan["id"], scan["base_url"])
        process_one(settings, db, scan, catalog, llm)


if __name__ == "__main__":
    main()
