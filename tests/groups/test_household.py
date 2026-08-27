from __future__ import annotations

from monarch_api import UserProfile

from monarch_mcp.groups import household


def test_get_current_user_loads_session_and_serializes(monkeypatch, tmp_path) -> None:
    session_path = tmp_path / "session.json"
    session_path.write_text(
        '{"token":"token-123","token_expiration":null,"user_id":"user-123","email":"person@example.com"}',
        encoding="utf-8",
    )

    def fake_get_current_user(session):
        assert session.token == "token-123"
        return UserProfile(id="user-123", email="person@example.com")

    monkeypatch.setattr(household, "api_get_current_user", fake_get_current_user)

    result = household.get_current_user(session_path=str(session_path))

    assert result["id"] == "user-123"
    assert result["email"] == "person@example.com"
