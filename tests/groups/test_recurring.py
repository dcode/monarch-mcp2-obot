from __future__ import annotations

from monarch_api import RecurringStream

from monarch_mcp.groups import recurring


def test_list_recurring_streams_maps_filter(monkeypatch, tmp_path) -> None:
    session_path = tmp_path / "session.json"
    session_path.write_text(
        '{"token":"token-123","token_expiration":null,"user_id":"user-123","email":"person@example.com"}',
        encoding="utf-8",
    )

    def fake_list_recurring_streams(
        session,
        *,
        filters=None,
        include_pending=True,
        include_liabilities=True,
    ):
        assert session.token == "token-123"
        assert filters.merchant_ids == ["merchant-1"]
        assert include_pending is False
        assert include_liabilities is True
        return [RecurringStream(id="recurring-1", name="Rent")]

    monkeypatch.setattr(
        recurring,
        "api_list_recurring_streams",
        fake_list_recurring_streams,
    )

    result = recurring.list_recurring_streams(
        filters={"merchant_ids": ["merchant-1"]},
        include_pending=False,
        session_path=str(session_path),
    )

    assert result[0]["id"] == "recurring-1"
    assert result[0]["name"] == "Rent"
