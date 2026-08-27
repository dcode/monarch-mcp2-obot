from __future__ import annotations

from monarch_api import InvestmentAccount

from monarch_mcp.groups import investments


def test_list_investment_accounts_loads_session(monkeypatch, tmp_path) -> None:
    session_path = tmp_path / "session.json"
    session_path.write_text(
        '{"token":"token-123","token_expiration":null,"user_id":"user-123","email":"person@example.com"}',
        encoding="utf-8",
    )

    def fake_list_investment_accounts(session):
        assert session.token == "token-123"
        return [InvestmentAccount(id="account-1", display_name="Brokerage")]

    monkeypatch.setattr(
        investments,
        "api_list_investment_accounts",
        fake_list_investment_accounts,
    )

    result = investments.list_investment_accounts(session_path=str(session_path))

    assert result[0]["id"] == "account-1"
    assert result[0]["display_name"] == "Brokerage"
