from __future__ import annotations

from monarch_api import ReceiptPage

from monarch_mcp.groups import receipts


def test_list_receipts_maps_filter(monkeypatch, tmp_path) -> None:
    session_path = tmp_path / "session.json"
    session_path.write_text(
        '{"token":"token-123","token_expiration":null,"user_id":"user-123","email":"person@example.com"}',
        encoding="utf-8",
    )

    def fake_list_receipts(session, *, filters=None, limit=100, offset=0):
        assert session.token == "token-123"
        assert filters.status.value == "completed"
        assert filters.source.value == "email"
        assert limit == 25
        assert offset == 5
        return ReceiptPage(receipts=[], total_count=0, limit=limit, offset=offset)

    monkeypatch.setattr(receipts, "api_list_receipts", fake_list_receipts)

    result = receipts.list_receipts(
        filters={"status": "completed", "source": "email"},
        limit=25,
        offset=5,
        session_path=str(session_path),
    )

    assert result["total_count"] == 0
    assert result["limit"] == 25


def test_update_receipt_converts_line_items(monkeypatch, tmp_path) -> None:
    session_path = tmp_path / "session.json"
    session_path.write_text(
        '{"token":"token-123","token_expiration":null,"user_id":"user-123","email":"person@example.com"}',
        encoding="utf-8",
    )

    def fake_update_receipt(session, receipt_id, **kwargs):
        assert session.token == "token-123"
        assert receipt_id == "receipt-1"
        assert kwargs["line_items"][0].line_item_id == "line-1"
        assert kwargs["line_items"][0].category_id == "category-1"
        return None

    monkeypatch.setattr(receipts, "api_update_receipt", fake_update_receipt)

    result = receipts.update_receipt(
        "receipt-1",
        line_items=[{"line_item_id": "line-1", "category_id": "category-1"}],
        session_path=str(session_path),
    )

    assert result is None
