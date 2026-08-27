from __future__ import annotations

import pyotp
import pytest
from monarch_api import MfaRequiredError, MonarchAuthError

from monarch_mcp import auth_runtime


class _FakeSession:
    def to_dict(self) -> dict:
        return {"token": "fake-token"}


# RFC 6238's well-known test seed.
TEST_SEED = "JBSWY3DPEHPK3PXP"


def test_perform_login_succeeds_without_mfa(monkeypatch, tmp_path) -> None:
    calls = []

    def fake_create_session(
        email, password, *, mfa_code=None, session_path=None, trusted_device=True
    ):
        calls.append((email, password, mfa_code))
        return _FakeSession()

    monkeypatch.setattr(auth_runtime, "create_session", fake_create_session)

    result = auth_runtime.perform_login(
        email="user@example.com",
        password="hunter2",
        session_path=tmp_path / "session.json",
    )

    assert result.used_totp is False
    assert calls == [("user@example.com", "hunter2", None)]


def test_perform_login_retries_with_totp_code_on_mfa_challenge(monkeypatch, tmp_path) -> None:
    calls = []

    def fake_create_session(
        email, password, *, mfa_code=None, session_path=None, trusted_device=True
    ):
        calls.append(mfa_code)
        if mfa_code is None:
            raise MfaRequiredError("mfa required")
        assert mfa_code == pyotp.TOTP(TEST_SEED).now()
        return _FakeSession()

    monkeypatch.setattr(auth_runtime, "create_session", fake_create_session)

    result = auth_runtime.perform_login(
        email="user@example.com",
        password="hunter2",
        totp_secret=TEST_SEED,
        session_path=tmp_path / "session.json",
    )

    assert result.used_totp is True
    assert len(calls) == 2
    assert calls[0] is None
    assert calls[1] is not None


def test_perform_login_accepts_totp_seed_with_spaces(monkeypatch, tmp_path) -> None:
    spaced_seed = " ".join(TEST_SEED[i : i + 4] for i in range(0, len(TEST_SEED), 4))

    def fake_create_session(
        email, password, *, mfa_code=None, session_path=None, trusted_device=True
    ):
        if mfa_code is None:
            raise MfaRequiredError("mfa required")
        assert mfa_code == pyotp.TOTP(TEST_SEED).now()
        return _FakeSession()

    monkeypatch.setattr(auth_runtime, "create_session", fake_create_session)

    result = auth_runtime.perform_login(
        email="user@example.com",
        password="hunter2",
        totp_secret=spaced_seed,
        session_path=tmp_path / "session.json",
    )

    assert result.used_totp is True


def test_perform_login_raises_when_mfa_required_and_no_totp_secret(monkeypatch, tmp_path) -> None:
    def fake_create_session(*args, **kwargs):
        raise MfaRequiredError("mfa required")

    monkeypatch.setattr(auth_runtime, "create_session", fake_create_session)

    with pytest.raises(auth_runtime.LoginError, match="MONARCH_TOTP_SECRET"):
        auth_runtime.perform_login(
            email="user@example.com",
            password="hunter2",
            session_path=tmp_path / "session.json",
        )


def test_perform_login_raises_clear_error_on_wrong_explicit_mfa_code(monkeypatch, tmp_path) -> None:
    def fake_create_session(*args, mfa_code=None, **kwargs):
        raise MfaRequiredError("mfa required")

    monkeypatch.setattr(auth_runtime, "create_session", fake_create_session)

    with pytest.raises(auth_runtime.LoginError, match="rejected the MFA code"):
        auth_runtime.perform_login(
            email="user@example.com",
            password="hunter2",
            mfa_code="000000",
            session_path=tmp_path / "session.json",
        )


def test_perform_login_raises_when_credentials_missing(tmp_path) -> None:
    with pytest.raises(auth_runtime.LoginError, match="No credentials available"):
        auth_runtime.perform_login(password="only-password", session_path=tmp_path / "session.json")


def test_perform_login_wraps_auth_errors(monkeypatch, tmp_path) -> None:
    def fake_create_session(*args, **kwargs):
        raise MonarchAuthError("invalid credentials")

    monkeypatch.setattr(auth_runtime, "create_session", fake_create_session)

    with pytest.raises(auth_runtime.LoginError, match="invalid credentials"):
        auth_runtime.perform_login(
            email="user@example.com",
            password="wrong",
            session_path=tmp_path / "session.json",
        )


def test_perform_login_reads_credentials_from_environment(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("MONARCH_EMAIL", "env-user@example.com")
    monkeypatch.setenv("MONARCH_PASSWORD", "env-password")

    calls = []

    def fake_create_session(
        email, password, *, mfa_code=None, session_path=None, trusted_device=True
    ):
        calls.append((email, password))
        return _FakeSession()

    monkeypatch.setattr(auth_runtime, "create_session", fake_create_session)

    auth_runtime.perform_login(session_path=tmp_path / "session.json")

    assert calls == [("env-user@example.com", "env-password")]


def test_ensure_authenticated_skips_login_when_valid_session_exists(monkeypatch, tmp_path) -> None:
    session_path = tmp_path / "session.json"
    session_path.write_text(
        '{"token":"t","token_expiration":null,"user_id":"u","email":"e@example.com"}',
        encoding="utf-8",
    )

    def fail_if_called(*args, **kwargs):
        raise AssertionError("perform_login should not be called")

    monkeypatch.setattr(auth_runtime, "perform_login", fail_if_called)

    result = auth_runtime.ensure_authenticated(session_path=session_path)

    assert result is None


def test_ensure_authenticated_skips_login_when_no_credentials_configured(
    monkeypatch, tmp_path
) -> None:
    monkeypatch.delenv("MONARCH_EMAIL", raising=False)
    monkeypatch.delenv("MONARCH_PASSWORD", raising=False)

    result = auth_runtime.ensure_authenticated(session_path=tmp_path / "missing.json")

    assert result is None


def test_ensure_authenticated_never_raises_on_login_failure(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("MONARCH_EMAIL", "user@example.com")
    monkeypatch.setenv("MONARCH_PASSWORD", "hunter2")

    def fake_create_session(*args, **kwargs):
        raise MonarchAuthError("boom")

    monkeypatch.setattr(auth_runtime, "create_session", fake_create_session)

    result = auth_runtime.ensure_authenticated(session_path=tmp_path / "missing.json")

    assert result is None
