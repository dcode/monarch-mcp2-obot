from __future__ import annotations

from monarch_api import Goal

from monarch_mcp.groups import goals


def test_list_goals_loads_session(monkeypatch, tmp_path) -> None:
    session_path = tmp_path / "session.json"
    session_path.write_text(
        '{"token":"token-123","token_expiration":null,"user_id":"user-123","email":"person@example.com"}',
        encoding="utf-8",
    )

    def fake_list_goals(session, *, include_archived=False):
        assert session.token == "token-123"
        assert include_archived is True
        return [Goal(id="goal-1", name="Emergency")]

    monkeypatch.setattr(goals, "api_list_goals", fake_list_goals)

    result = goals.list_goals(
        include_archived=True,
        session_path=str(session_path),
    )

    assert result[0]["id"] == "goal-1"
    assert result[0]["name"] == "Emergency"
