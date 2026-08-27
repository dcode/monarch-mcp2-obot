from __future__ import annotations

from monarch_api import TransactionPage, TransactionSort

from monarch_mcp.groups import transactions


def test_list_transactions_maps_filter_and_sort(monkeypatch, tmp_path) -> None:
    session_path = tmp_path / "session.json"
    session_path.write_text(
        '{"token":"token-123","token_expiration":null,"user_id":"user-123","email":"person@example.com"}',
        encoding="utf-8",
    )

    def fake_list_transactions(
        session,
        *,
        filters=None,
        limit=100,
        offset=0,
        sort=None,
    ):
        assert session.token == "token-123"
        assert filters.account_ids == ["account-1"]
        assert limit == 25
        assert offset == 5
        assert sort is TransactionSort.AMOUNT_DESCENDING
        return TransactionPage(transactions=[], total_count=0, limit=limit, offset=offset)

    monkeypatch.setattr(
        transactions,
        "api_list_transactions",
        fake_list_transactions,
    )

    result = transactions.list_transactions(
        filters={"account_ids": ["account-1"]},
        limit=25,
        offset=5,
        sort="amount",
        session_path=str(session_path),
    )

    assert result["total_count"] == 0
    assert result["limit"] == 25


def test_download_transaction_attachment_serializes_bytes(monkeypatch, tmp_path) -> None:
    session_path = tmp_path / "session.json"
    session_path.write_text(
        '{"token":"token-123","token_expiration":null,"user_id":"user-123","email":"person@example.com"}',
        encoding="utf-8",
    )

    def fake_download_transaction_attachment(session, attachment_id, path=None):
        assert session.token == "token-123"
        assert attachment_id == "attachment-1"
        assert path is None
        return b"hello"

    monkeypatch.setattr(
        transactions,
        "api_download_transaction_attachment",
        fake_download_transaction_attachment,
    )

    result = transactions.download_transaction_attachment(
        "attachment-1",
        session_path=str(session_path),
    )

    assert result["size_bytes"] == 5
    assert result["content_base64"] == "aGVsbG8="
