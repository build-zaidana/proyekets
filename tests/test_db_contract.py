"""Uji kontrak DB antara worker Python dan Laravel (DESIGN_GUIDELINES §6.3).

Membuat SQLite dengan skema yang SAMA seperti migration Laravel, lalu memastikan
agent/db.py dapat: mengklaim scan 'queued', menulis step/finding/audit, dan set status.
Ini menjaga agar kedua lapis tetap sepakat pada skema.
"""
import pytest

pytest.importorskip("sqlalchemy")
from sqlalchemy import create_engine, text  # noqa: E402

from agent.db import Database  # noqa: E402

# Skema minimal, cermin migration Laravel (web/database/migrations/*).
_SCHEMA = [
    "CREATE TABLE targets (id INTEGER PRIMARY KEY, name TEXT, base_url TEXT, is_active INT)",
    "CREATE TABLE scans (id INTEGER PRIMARY KEY, target_id INT, status TEXT, "
    "totals TEXT, started_at TEXT, finished_at TEXT, created_at TEXT, updated_at TEXT)",
    "CREATE TABLE agent_steps (id INTEGER PRIMARY KEY, scan_id INT, seq INT, "
    "phase TEXT, content TEXT, created_at TEXT)",
    "CREATE TABLE findings (id INTEGER PRIMARY KEY, scan_id INT, severity TEXT, "
    "confidence TEXT, vuln_type TEXT, cwe TEXT, location TEXT, evidence TEXT, "
    "remediation TEXT, created_at TEXT)",
    "CREATE TABLE audit_log (id INTEGER PRIMARY KEY, scan_id INT, ts TEXT, "
    "method TEXT, url TEXT, verdict TEXT, reason TEXT)",
]


def _make_db(tmp_path):
    dsn = f"sqlite:///{tmp_path/'contract.sqlite'}"
    eng = create_engine(dsn)
    with eng.begin() as c:
        for stmt in _SCHEMA:
            c.execute(text(stmt))
        c.execute(text("INSERT INTO targets (id,name,base_url,is_active) "
                       "VALUES (1,'DVWA','http://localhost:8080',1)"))
        c.execute(text("INSERT INTO scans (id,target_id,status) VALUES (1,1,'queued')"))
    return Database(dsn)


def test_worker_claims_scan_written_by_web(tmp_path):
    db = _make_db(tmp_path)
    scan = db.claim_queued_scan()
    assert scan == {"id": 1, "base_url": "http://localhost:8080"}
    # Klaim kedua tidak mengembalikan scan yang sama (sudah 'running').
    assert db.claim_queued_scan() is None


def test_worker_writes_are_readable(tmp_path):
    db = _make_db(tmp_path)
    scan = db.claim_queued_scan()
    db.insert_step(scan["id"], 1, "thought", "mulai")
    db.insert_finding(scan["id"], {
        "severity": "High", "confidence": "High", "vuln_type": "SQL Injection",
        "cwe": "CWE-89", "location": "GET /x", "evidence": {"reason": "sig"},
        "remediation": "prepared statement",
    })
    db.set_scan_status(scan["id"], "done")

    from sqlalchemy import create_engine, text
    eng = create_engine(f"sqlite:///{tmp_path/'contract.sqlite'}")
    with eng.connect() as c:
        assert c.execute(text("SELECT status FROM scans WHERE id=1")).scalar() == "done"
        assert c.execute(text("SELECT count(*) FROM agent_steps")).scalar() == 1
        sev = c.execute(text("SELECT severity FROM findings")).scalar()
        assert sev == "High"
