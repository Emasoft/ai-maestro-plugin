"""Tests for scripts/cpv_network_resilience.py — pure transient-error classifiers.

The retry wrappers in cpv_network_resilience are network-dependent, so we don't
test them here (they would either hit the real network or require mocks, both
of which violate this project's no-mock rule). Instead we test the two
deterministic, side-effect-free classifiers — `is_transient_subprocess_error`
and `is_transient_http_error` — that decide whether a failure should be retried.

These two functions encode the retry contract documented in
~/.claude/rules/github-timeouts.md, and a regression here means publish.py /
the pre-push hook would either silently retry permanent auth errors (wasting
the user's retry budget) or give up on transient 5xx blips (forcing the user
to re-run publish manually).
"""
from __future__ import annotations

import socket
import ssl
import sys
import urllib.error
from http.client import BadStatusLine, RemoteDisconnected
from pathlib import Path

import pytest

# Make scripts/ importable without installing the plugin as a package.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from cpv_network_resilience import (  # noqa: E402  (sys.path mutation above is intentional)
    is_transient_http_error,
    is_transient_subprocess_error,
)

# ─── is_transient_subprocess_error ────────────────────────────────────────────


class TestSubprocessErrorClassifier:
    """The subprocess classifier turns gh/git stderr into a retry/no-retry verdict."""

    def test_returncode_zero_is_never_transient(self) -> None:
        # Even a stderr that looks transient is irrelevant when the command
        # actually succeeded — there's nothing to retry.
        assert is_transient_subprocess_error("connection reset", returncode=0) is False

    def test_empty_stderr_is_never_transient(self) -> None:
        # No diagnostic text means we cannot prove the failure is transient,
        # so the safe default is "do not retry" — the caller's terminal path
        # will surface the original failure.
        assert is_transient_subprocess_error("", returncode=1) is False

    @pytest.mark.parametrize(
        "stderr",
        [
            "fatal: Could not resolve host: github.com",
            "fatal: unable to access 'https://github.com/foo/bar.git/': Failed to connect to github.com port 443: Connection refused by peer",
            "Connection timed out after 60001 milliseconds",
            "fatal: the remote end hung up unexpectedly",
            "RPC failed; HTTP 502 curl 22 The requested URL returned error: 502",
            "Recv failure: Connection reset by peer",
            "error: RPC failed; HTTP 503 curl",
            "Bad gateway",
            "Gateway Timeout (504)",
            "API rate limit exceeded for user",
            "HTTP 429 Too Many Requests",
            "The operation timed out",
            "GnuTLS_handshake() failed: Error in the pull function.",
            "OpenSSL SSL_read: Connection reset by peer, errno 54 ssl error",
            "Network is unreachable",
        ],
    )
    def test_known_transient_signatures_trigger_retry(self, stderr: str) -> None:
        # Each of these stderr fragments has been observed in real github.com
        # failures and should trigger a retry. The classifier is regex-based
        # and case-insensitive, so the exact framing must keep matching.
        assert is_transient_subprocess_error(stderr, returncode=128) is True

    @pytest.mark.parametrize(
        "stderr",
        [
            "! [rejected] main -> main (non-fast-forward)",
            "Permission denied (publickey).",
            "remote: HTTP 401",
            "remote: HTTP 403",
            "remote: HTTP 404",
            "remote: HTTP 422",
            "Authentication failed for 'https://github.com/foo/bar.git/'",
            "401 Unauthorized",
            "403 Forbidden",
            "404 Not Found",
            "name already exists on this account",
            "refusing to overwrite remote tag",
            "unable to access 'https://github.com/foo.git/': The requested URL returned error: 404",
        ],
    )
    def test_permanent_signatures_never_retry(self, stderr: str) -> None:
        # Permanent failures (auth, 4xx, non-fast-forward, name collisions)
        # should never be retried — retrying just wastes the user's budget
        # and delays the actionable error message.
        assert is_transient_subprocess_error(stderr, returncode=1) is False

    def test_permanent_wins_over_transient_when_both_match(self) -> None:
        # Real-world failures sometimes chain a transient-looking 5xx with the
        # actual cause (a 401). The permanent half must win — otherwise
        # publish.py would burn 30 retries on an unrecoverable auth error.
        chained = "HTTP 503 service unavailable; underlying cause: 401 Unauthorized"
        assert is_transient_subprocess_error(chained, returncode=1) is False

    def test_unknown_stderr_does_not_retry_by_default(self) -> None:
        # Any stderr we don't recognize is treated as permanent — we'd rather
        # surface "weird error, please look at it" than auto-retry indefinitely.
        assert (
            is_transient_subprocess_error("error: something we have never seen before", returncode=1)
            is False
        )


# ─── is_transient_http_error ──────────────────────────────────────────────────


class TestHttpErrorClassifier:
    """The HTTP classifier turns urllib exceptions into a retry/no-retry verdict."""

    def test_none_is_not_transient(self) -> None:
        # urllib sometimes propagates a None reason (e.g. URLError with no
        # underlying cause). Defaulting to "permanent" is the safe choice.
        assert is_transient_http_error(None) is False

    def test_socket_timeout_is_transient(self) -> None:
        assert is_transient_http_error(socket.timeout("read timed out")) is True

    def test_builtin_timeout_is_transient(self) -> None:
        # Python 3.10+ aliases socket.timeout to TimeoutError; we accept both.
        assert is_transient_http_error(TimeoutError("connect timed out")) is True

    def test_ssl_error_is_transient(self) -> None:
        # SSL handshake failures are usually transient (network-layer hiccups,
        # MITM proxies dropping a packet). Retry is the right default.
        assert is_transient_http_error(ssl.SSLError("handshake failure")) is True

    def test_remote_disconnected_is_transient(self) -> None:
        assert is_transient_http_error(RemoteDisconnected("Remote end closed connection")) is True

    def test_bad_status_line_is_transient(self) -> None:
        assert is_transient_http_error(BadStatusLine("''")) is True

    def test_connection_error_is_transient(self) -> None:
        assert is_transient_http_error(ConnectionError("connection reset")) is True

    @pytest.mark.parametrize("code", [408, 429, 500, 502, 503, 504])
    def test_transient_http_codes_trigger_retry(self, code: int) -> None:
        # 408 Request Timeout, 429 Too Many Requests, and 5xx server errors
        # are the canonical "try again later" responses per RFC 7231 §6.6 and
        # github.com's documented rate-limit retry semantics.
        exc = urllib.error.HTTPError(
            url="https://github.com",
            code=code,
            msg="transient",
            hdrs=None,  # type: ignore[arg-type]
            fp=None,
        )
        assert is_transient_http_error(exc) is True

    @pytest.mark.parametrize("code", [400, 401, 403, 404, 422])
    def test_permanent_http_codes_never_retry(self, code: int) -> None:
        # 4xx (client error) means the request itself is wrong — retrying
        # without changing it produces the same error.
        exc = urllib.error.HTTPError(
            url="https://github.com",
            code=code,
            msg="permanent",
            hdrs=None,  # type: ignore[arg-type]
            fp=None,
        )
        assert is_transient_http_error(exc) is False

    def test_url_error_unwraps_underlying_reason(self) -> None:
        # urllib raises URLError(reason=<inner exc>) when a low-level network
        # primitive fails. The classifier must follow the chain to make the
        # right decision — wrapping a TimeoutError in URLError must still
        # retry, wrapping a ValueError must not.
        wrapped_transient = urllib.error.URLError(socket.timeout("inner timeout"))
        wrapped_permanent = urllib.error.URLError("plain string reason — unknown")
        assert is_transient_http_error(wrapped_transient) is True
        assert is_transient_http_error(wrapped_permanent) is False

    def test_unrelated_exception_is_not_transient(self) -> None:
        # ValueErrors, KeyErrors etc. are not network failures — they're
        # programming bugs, and retrying would just paper over them.
        assert is_transient_http_error(ValueError("bad input")) is False
        assert is_transient_http_error(RuntimeError("something else")) is False
