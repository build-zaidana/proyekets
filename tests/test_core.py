"""Smoke test loop ReAct deterministik (tanpa LLM), dengan HTTP di-mock."""
import responses

from agent.audit import AuditLog
from agent.core import run_scan
from agent.guardrails import RateLimiter
from agent.payloads import PayloadCatalog
from agent.tools.http_client import HttpClient

ALLOW = frozenset({"localhost:8080"})

_HTML_FORM = (
    '<html><body><form method="get" action="/search">'
    '<input name="q" type="text"></form></body></html>'
)


def _client(tmp_path):
    return HttpClient(
        allowed_hosts=ALLOW,
        rate_limiter=RateLimiter(max_per_second=1000),
        audit=AuditLog(tmp_path / "a.jsonl"),
        timeout_seconds=5,
        body_max_bytes=2048,
    )


@responses.activate
def test_loop_finds_reflected_xss(tmp_path):
    responses.add(responses.GET, "http://localhost:8080/", body=_HTML_FORM, status=200)
    # Endpoint merefleksikan marker apa adanya -> XSS terkonfirmasi validator.
    responses.add(
        responses.GET, "http://localhost:8080/search",
        body="hasil: <script>__dastmark__</script>", status=200,
    )

    steps = []
    result = run_scan(
        _client(tmp_path), "http://localhost:8080/",
        catalog=PayloadCatalog.load(), max_steps=50, on_step=steps.append,
    )

    assert steps, "harus ada langkah ReAct yang ter-emit"
    assert any(f.vuln_type == "Reflected XSS" for f in result.findings)


@responses.activate
def test_loop_no_finding_on_clean_app(tmp_path):
    responses.add(responses.GET, "http://localhost:8080/", body=_HTML_FORM, status=200)
    # Aplikasi 'bersih': tidak ada error SQL, tidak ada refleksi.
    responses.add(
        responses.GET, "http://localhost:8080/search",
        body="hasil pencarian aman", status=200,
    )
    result = run_scan(
        _client(tmp_path), "http://localhost:8080/",
        catalog=PayloadCatalog.load(), max_steps=50,
    )
    assert result.findings == []
