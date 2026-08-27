from __future__ import annotations

from monarch_api import BudgetSettings

from monarch_mcp.groups import budget


def test_get_budget_settings_loads_session(monkeypatch, tmp_path) -> None:
    session_path = tmp_path / "session.json"
    session_path.write_text(
        '{"token":"token-123","token_expiration":null,"user_id":"user-123","email":"person@example.com"}',
        encoding="utf-8",
    )

    def fake_get_budget_settings(session):
        assert session.token == "token-123"
        return BudgetSettings(apply_to_future_months_default=True)

    monkeypatch.setattr(budget, "api_get_budget_settings", fake_get_budget_settings)

    result = budget.get_budget_settings(session_path=str(session_path))

    assert result["apply_to_future_months_default"] is True
