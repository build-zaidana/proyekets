"""Unit test guardrail — keamanan-kritis (DESIGN_GUIDELINES §6.8)."""
import time

import pytest

from agent.guardrails import (
    DestructivePayloadBlocked,
    RateLimiter,
    TargetNotAllowed,
    check_allowlist,
    check_payload_safe,
    host_of,
)

ALLOW = frozenset({"localhost:8080", "127.0.0.1:8080", "localhost"})


def test_host_of_variants():
    assert host_of("http://localhost:8080/login") == "localhost:8080"
    assert host_of("https://127.0.0.1/a") == "127.0.0.1"
    assert host_of("not a url") == ""


def test_allowlist_accepts_listed_host():
    check_allowlist("http://localhost:8080/login", ALLOW)  # tidak melempar


def test_allowlist_accepts_bare_when_listed():
    check_allowlist("http://localhost/anything", ALLOW)


def test_allowlist_rejects_unknown_host():
    with pytest.raises(TargetNotAllowed):
        check_allowlist("http://evil.example.com/", ALLOW)


def test_allowlist_rejects_empty_allowlist():
    with pytest.raises(TargetNotAllowed):
        check_allowlist("http://localhost:8080/", frozenset())


def test_allowlist_rejects_invalid_url():
    with pytest.raises(TargetNotAllowed):
        check_allowlist("garbage", ALLOW)


def test_payload_filter_blocks_destructive():
    with pytest.raises(DestructivePayloadBlocked):
        check_payload_safe("1; DROP TABLE users")


def test_payload_filter_blocks_delete():
    with pytest.raises(DestructivePayloadBlocked):
        check_payload_safe("x DELETE FROM accounts WHERE 1=1")


def test_payload_filter_allows_benign_and_empty():
    check_payload_safe(None)
    check_payload_safe("")
    check_payload_safe("harmless search term")


def test_rate_limiter_spaces_requests():
    rl = RateLimiter(max_per_second=10)  # min interval 0.1s
    start = time.monotonic()
    for _ in range(3):
        rl.acquire()
    assert time.monotonic() - start >= 0.2  # dua jeda di antara tiga acquire
