"""Unit test validator — inti anti-false-positive (logika murni)."""
from agent.tools.http_client import HttpResult
from agent import validator

SIGS = ("you have an error in your sql syntax", "warning: mysql")


def _res(status=200, body="", ok=True, blocked=False):
    return HttpResult(ok=ok, status_code=status, body_snippet=body, blocked=blocked)


def test_sql_error_detected():
    r = _res(body="Error: You have an error in your SQL syntax near '''")
    v = validator.judge_sql_error(r, SIGS)
    assert v.vulnerable and v.confidence == "High"


def test_sql_error_absent():
    assert not validator.judge_sql_error(_res(body="halaman normal"), SIGS).vulnerable


def test_boolean_differential_by_status():
    v = validator.judge_boolean_differential(_res(status=200, body="x"), _res(status=500, body="x"))
    assert v.vulnerable


def test_boolean_differential_by_length():
    v = validator.judge_boolean_differential(
        _res(body="A" * 200), _res(body="A" * 10)
    )
    assert v.vulnerable


def test_boolean_similar_is_not_vulnerable():
    v = validator.judge_boolean_differential(_res(body="A" * 100), _res(body="A" * 100))
    assert not v.vulnerable


def test_boolean_blocked_is_not_vulnerable():
    v = validator.judge_boolean_differential(_res(ok=False, blocked=True), _res(body="x"))
    assert not v.vulnerable


def test_reflected_xss_unescaped():
    r = _res(body="hasil: <script>__dastmark__</script> selesai")
    assert validator.judge_reflected_xss(r, "__dastmark__").vulnerable


def test_reflected_xss_escaped_is_safe():
    r = _res(body="hasil: &lt;script&gt;__dastmark__&lt;/script&gt;")
    assert not validator.judge_reflected_xss(r, "__dastmark__").vulnerable


def test_reflected_xss_not_reflected():
    assert not validator.judge_reflected_xss(_res(body="tidak ada"), "__dastmark__").vulnerable
