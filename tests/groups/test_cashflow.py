from __future__ import annotations

from monarch_api import CashflowSummary

from monarch_mcp.groups import cashflow


def test_get_cashflow_summary_maps_filter(monkeypatch, tmp_path) -> None:
    session_path = tmp_path / "session.json"
    session_path.write_text(
        '{"token":"token-123","token_expiration":null,"user_id":"user-123","email":"person@example.com"}',
        encoding="utf-8",
    )

    def fake_get_cashflow_summary(session, start_date, end_date, *, filters=None):
        assert session.token == "token-123"
        assert start_date == "2026-01-01"
        assert end_date == "2026-01-31"
        assert filters.account_ids == ["account-1"]
        return CashflowSummary(
            start_date=start_date,
            end_date=end_date,
            income=100.0,
            expenses=50.0,
            savings=50.0,
        )

    monkeypatch.setattr(
        cashflow,
        "api_get_cashflow_summary",
        fake_get_cashflow_summary,
    )

    result = cashflow.get_cashflow_summary(
        "2026-01-01",
        "2026-01-31",
        filters={"account_ids": ["account-1"]},
        session_path=str(session_path),
    )

    assert result["income"] == 100.0
    assert result["expenses"] == 50.0
