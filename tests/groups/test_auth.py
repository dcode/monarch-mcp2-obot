from __future__ import annotations

from monarch_api import AuthSession

from monarch_mcp import auth_runtime
from monarch_mcp.groups import auth


def test_create_session_maps_to_api_and_redacts_token(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("MONARCH_SESSION_PATH", str(tmp_path / "session.json"))

    def fake_create_session(*args, **kwargs) -> AuthSession:
        return AuthSession(
            token="token-123",
            token_expiration="2030-01-01T00:00:00Z",
            user_id="user-123",
            email="person@example.com",
        )

    monkeypatch.setattr(auth, "api_create_session", fake_create_session)

    result = auth.create_session("person@example.com", "secret", mfa_code="123456")

    assert result == {
        "token": "<redacted>",
        "token_expiration": "2030-01-01T00:00:00Z",
        "user_id": "user-123",
        "email": "person@example.com",
    }


def test_create_session_can_return_token_when_explicit(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("MONARCH_SESSION_PATH", str(tmp_path / "session.json"))

    def fake_create_session(*args, **kwargs) -> AuthSession:
        return AuthSession(
            token="token-123",
            token_expiration="2030-01-01T00:00:00Z",
            user_id="user-123",
            email="person@example.com",
        )

    monkeypatch.setattr(auth, "api_create_session", fake_create_session)

    result = auth.create_session("person@example.com", "secret", include_token=True)

    assert result["token"] == "token-123"
    assert result["email"] == "person@example.com"


def test_save_and_load_session_map_to_api(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("MONARCH_SESSION_PATH", str(tmp_path / "session.json"))
    session = {
        "token": "token-123",
        "token_expiration": "2030-01-01T00:00:00Z",
        "user_id": "user-123",
        "email": "person@example.com",
    }

    auth.save_session(session)
    redacted = auth.load_session()
    unredacted = auth.load_session(include_token=True)

    assert redacted == {
        "token": "<redacted>",
        "token_expiration": "2030-01-01T00:00:00Z",
        "user_id": "user-123",
        "email": "person@example.com",
    }
    assert unredacted["token"] == "token-123"


def test_auth_login_delegates_to_auth_runtime_and_redacts_errors(monkeypatch) -> None:
    captured = {}

    def fake_perform_login(**kwargs):
        captured.update(kwargs)
        return auth_runtime.LoginResult(
            session=AuthSession(
                token="t",
                token_expiration=None,
                user_id="u",
                email="person@example.com",
            ),
            session_path=kwargs.get("session_path") or "/config/session.json",
            used_totp=True,
        )

    monkeypatch.setattr(auth, "perform_login", fake_perform_login)

    result = auth.auth_login(email="person@example.com", password="hunter2")

    assert result["success"] is True
    assert result["used_totp"] is True
    assert "token" not in result
    assert captured["email"] == "person@example.com"
    assert captured["password"] == "hunter2"


def test_auth_login_reports_failure_without_raising(monkeypatch) -> None:
    def fake_perform_login(**kwargs):
        raise auth_runtime.LoginError("no credentials configured")

    monkeypatch.setattr(auth, "perform_login", fake_perform_login)

    result = auth.auth_login()

    assert result == {"success": False, "error": "no credentials configured"}


def test_auth_status_reports_missing_session(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("MONARCH_SESSION_PATH", str(tmp_path / "nope.json"))

    result = auth.auth_status()

    assert result["session_exists"] is False
    assert result["valid"] is None


def test_auth_status_validates_existing_session(monkeypatch, tmp_path) -> None:
    session_path = tmp_path / "session.json"
    session_path.write_text(
        '{"token":"t","token_expiration":null,"user_id":"u","email":"person@example.com"}',
        encoding="utf-8",
    )
    monkeypatch.setenv("MONARCH_SESSION_PATH", str(session_path))
    monkeypatch.setattr(
        auth, "api_get_current_user", lambda session: {"id": "u", "email": session.email}
    )

    result = auth.auth_status()

    assert result["session_exists"] is True
    assert result["valid"] is True
    assert result["user"]["email"] == "person@example.com"
    assert "token" not in str(result)


def test_auth_status_reports_invalid_session_without_raising(monkeypatch, tmp_path) -> None:
    from monarch_api import MonarchError

    session_path = tmp_path / "session.json"
    session_path.write_text(
        '{"token":"t","token_expiration":null,"user_id":"u","email":"person@example.com"}',
        encoding="utf-8",
    )
    monkeypatch.setenv("MONARCH_SESSION_PATH", str(session_path))

    def raise_expired(session):
        raise MonarchError("session expired")

    monkeypatch.setattr(auth, "api_get_current_user", raise_expired)

    result = auth.auth_status()

    assert result["valid"] is False
    assert "expired" in result["error"]
