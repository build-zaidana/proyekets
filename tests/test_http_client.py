"""Unit test HttpClient — guardrail terpasang, tanpa jaringan nyata."""
import responses

from agent.audit import AuditLog
from agent.guardrails import RateLimiter
from agent.tools.http_client import HttpClient

ALLOW = frozenset({"localhost:8080"})


def _client(tmp_path, scan_id=1):
    audit = AuditLog(tmp_path / "audit.jsonl")
    return HttpClient(
        allowed_hosts=ALLOW,
        rate_limiter=RateLimiter(max_per_second=1000),
        audit=audit,
        timeout_seconds=5,
        body_max_bytes=100,
        scan_id=scan_id,
    )


@responses.activate
def test_sends_to_allowed_host(tmp_path):
    responses.add(responses.GET, "http://localhost:8080/", body="ok", status=200)
    res = _client(tmp_path).send_http_request("GET", "http://localhost:8080/")
    assert res.ok and res.status_code == 200
    assert res.blocked is False


def test_blocks_host_outside_allowlist(tmp_path):
    res = _client(tmp_path).send_http_request("GET", "http://evil.example.com/")
    assert res.blocked is True and res.ok is False


def test_blocks_destructive_payload_before_send(tmp_path):
    # Tidak ada responses.add -> kalau request terkirim, akan error koneksi.
    res = _client(tmp_path).send_http_request(
        "POST", "http://localhost:8080/x", data={"q": "1; DROP TABLE t"}
    )
    assert res.blocked is True


@responses.activate
def test_body_is_truncated(tmp_path):
    responses.add(responses.GET, "http://localhost:8080/big", body="A" * 500, status=200)
    res = _client(tmp_path).send_http_request("GET", "http://localhost:8080/big")
    assert "dipotong" in res.body_snippet


def test_blocked_request_is_audited(tmp_path):
    path = tmp_path / "audit.jsonl"
    audit = AuditLog(path)
    client = HttpClient(
        allowed_hosts=ALLOW, rate_limiter=RateLimiter(1000), audit=audit,
        timeout_seconds=5, body_max_bytes=100,
    )
    client.send_http_request("GET", "http://evil.example.com/")
    assert "blocked" in path.read_text()
