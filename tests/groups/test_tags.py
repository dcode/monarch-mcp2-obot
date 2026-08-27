from __future__ import annotations

from monarch_api import Tag

from monarch_mcp.groups import tags


def test_list_tags_loads_session_and_serializes(monkeypatch, tmp_path) -> None:
    session_path = tmp_path / "session.json"
    session_path.write_text(
        '{"token":"token-123","token_expiration":null,"user_id":"user-123","email":"person@example.com"}',
        encoding="utf-8",
    )

    def fake_list_tags(
        session,
        *,
        search=None,
        limit=None,
        include_transaction_count=False,
    ):
        assert session.token == "token-123"
        assert search == "tax"
        assert limit == 10
        assert include_transaction_count is True
        return [Tag(id="tag-1", name="Tax", color="#ffffff", order=1)]

    monkeypatch.setattr(tags, "api_list_tags", fake_list_tags)

    result = tags.list_tags(
        search="tax",
        limit=10,
        include_transaction_count=True,
        session_path=str(session_path),
    )

    assert result == [
        {
            "id": "tag-1",
            "name": "Tax",
            "color": "#ffffff",
            "order": 1,
            "transaction_count": None,
        }
    ]


def test_create_tag_maps_to_api(monkeypatch, tmp_path) -> None:
    session_path = tmp_path / "session.json"
    session_path.write_text(
        '{"token":"token-123","token_expiration":null,"user_id":"user-123","email":"person@example.com"}',
        encoding="utf-8",
    )

    def fake_create_tag(session, *, name, color):
        assert session.token == "token-123"
        assert name == "Travel"
        assert color == "#123456"
        return Tag(id="tag-2", name=name, color=color)

    monkeypatch.setattr(tags, "api_create_tag", fake_create_tag)

    result = tags.create_tag(
        name="Travel",
        color="#123456",
        session_path=str(session_path),
    )

    assert result["id"] == "tag-2"
    assert result["name"] == "Travel"
