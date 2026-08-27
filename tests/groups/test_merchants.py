from __future__ import annotations

from monarch_api import Merchant, MerchantSort

from monarch_mcp.groups import merchants


def test_list_merchants_maps_sort(monkeypatch, tmp_path) -> None:
    session_path = tmp_path / "session.json"
    session_path.write_text(
        '{"token":"token-123","token_expiration":null,"user_id":"user-123","email":"person@example.com"}',
        encoding="utf-8",
    )

    def fake_list_merchants(session, *, search=None, limit=None, offset=None, sort=None):
        assert session.token == "token-123"
        assert search == "coffee"
        assert limit == 5
        assert offset == 1
        assert sort is MerchantSort.NAME
        return [Merchant(id="merchant-1", name="Coffee")]

    monkeypatch.setattr(merchants, "api_list_merchants", fake_list_merchants)

    result = merchants.list_merchants(
        search="coffee",
        limit=5,
        offset=1,
        sort="NAME",
        session_path=str(session_path),
    )

    assert result[0]["id"] == "merchant-1"
    assert result[0]["name"] == "Coffee"
