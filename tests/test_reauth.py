from __future__ import annotations

import pytest
from monarch_api import MonarchError

from monarch_mcp import reauth
from monarch_mcp.auth_runtime import LoginError


def test_looks_like_expired_session_matches_known_markers() -> None:
    assert reauth.looks_like_expired_session("Invalid token.")
    assert reauth.looks_like_expired_session("Authentication credentials were not provided.")
    assert reauth.looks_like_expired_session("UNAUTHORIZED")


def test_looks_like_expired_session_rejects_unrelated_errors() -> None:
    assert not reauth.looks_like_expired_session("Account not found.")
    assert not reauth.looks_like_expired_session("Amount must be positive.")


def test_call_with_reauth_returns_result_on_success(monkeypatch) -> None:
    def fn(x: int) -> int:
        return x * 2

    assert reauth.call_with_reauth("accounts_list_accounts", fn, (3,), {}) == 6


def test_call_with_reauth_reraises_non_expired_errors(monkeypatch) -> None:
    monkeypatch.setenv("MONARCH_EMAIL", "user@example.com")
    monkeypatch.setenv("MONARCH_PASSWORD", "hunter2")

    def fn() -> None:
        raise MonarchError("Account not found.")

    with pytest.raises(MonarchError, match="Account not found"):
        reauth.call_with_reauth("accounts_get_account", fn, (), {})


def test_call_with_reauth_skips_auth_group_tools(monkeypatch) -> None:
    monkeypatch.setenv("MONARCH_EMAIL", "user@example.com")
    monkeypatch.setenv("MONARCH_PASSWORD", "hunter2")

    def fn() -> None:
        raise MonarchError("Invalid token.")

    login_calls = []
    monkeypatch.setattr(
        reauth,
        "perform_login",
        lambda **kwargs: login_calls.append(kwargs),
    )

    with pytest.raises(MonarchError, match="Invalid token"):
        reauth.call_with_reauth("auth_status", fn, (), {})
    assert login_calls == []


def test_call_with_reauth_skips_when_no_credentials_configured(monkeypatch) -> None:
    monkeypatch.delenv("MONARCH_EMAIL", raising=False)
    monkeypatch.delenv("MONARCH_PASSWORD", raising=False)

    def fn() -> None:
        raise MonarchError("Invalid token.")

    with pytest.raises(MonarchError, match="Invalid token"):
        reauth.call_with_reauth("accounts_list_accounts", fn, (), {})


def test_call_with_reauth_retries_once_after_successful_relogin(monkeypatch) -> None:
    monkeypatch.setenv("MONARCH_EMAIL", "user@example.com")
    monkeypatch.setenv("MONARCH_PASSWORD", "hunter2")
    monkeypatch.setattr(reauth, "perform_login", lambda **kwargs: None)

    calls = {"count": 0}

    def fn() -> str:
        calls["count"] += 1
        if calls["count"] == 1:
            raise MonarchError("Token has expired.")
        return "ok"

    assert reauth.call_with_reauth("accounts_list_accounts", fn, (), {}) == "ok"
    assert calls["count"] == 2


def test_call_with_reauth_raises_original_error_if_relogin_fails(monkeypatch) -> None:
    monkeypatch.setenv("MONARCH_EMAIL", "user@example.com")
    monkeypatch.setenv("MONARCH_PASSWORD", "hunter2")

    def fake_perform_login(**kwargs):
        raise LoginError("Monarch login failed: bad password")

    monkeypatch.setattr(reauth, "perform_login", fake_perform_login)

    def fn() -> None:
        raise MonarchError("Token has expired.")

    with pytest.raises(MonarchError, match="Token has expired"):
        reauth.call_with_reauth("accounts_list_accounts", fn, (), {})


def test_call_with_reauth_propagates_error_from_second_failed_attempt(monkeypatch) -> None:
    monkeypatch.setenv("MONARCH_EMAIL", "user@example.com")
    monkeypatch.setenv("MONARCH_PASSWORD", "hunter2")
    monkeypatch.setattr(reauth, "perform_login", lambda **kwargs: None)

    def fn() -> None:
        raise MonarchError("Token has expired.")

    with pytest.raises(MonarchError, match="Token has expired"):
        reauth.call_with_reauth("accounts_list_accounts", fn, (), {})
