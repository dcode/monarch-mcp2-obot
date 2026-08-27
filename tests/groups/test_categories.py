from __future__ import annotations

from monarch_api import Category, CategoryFilter, CategoryGroup, CategoryType

from monarch_mcp.groups import categories


def test_category_filter_from_dict() -> None:
    result = categories.category_filter_from_dict({"group_ids": ["group-1"], "types": ["expense"]})

    assert isinstance(result, CategoryFilter)
    assert result.group_ids == ["group-1"]
    assert result.types == [CategoryType.EXPENSE]


def test_list_categories_loads_session_and_serializes(monkeypatch, tmp_path) -> None:
    session_path = tmp_path / "session.json"
    session_path.write_text(
        '{"token":"token-123","token_expiration":null,"user_id":"user-123","email":"person@example.com"}',
        encoding="utf-8",
    )

    def fake_list_categories(session, *, filters=None, include_disabled=False):
        assert session.token == "token-123"
        assert filters.group_ids == ["group-1"]
        assert include_disabled is True
        return [Category(id="category-1", name="Groceries", icon="food")]

    monkeypatch.setattr(categories, "api_list_categories", fake_list_categories)

    result = categories.list_categories(
        filters={"group_ids": ["group-1"]},
        include_disabled=True,
        session_path=str(session_path),
    )

    assert result[0]["id"] == "category-1"
    assert result[0]["name"] == "Groceries"
    assert result[0]["icon"] == "food"


def test_create_category_group_maps_type(monkeypatch, tmp_path) -> None:
    session_path = tmp_path / "session.json"
    session_path.write_text(
        '{"token":"token-123","token_expiration":null,"user_id":"user-123","email":"person@example.com"}',
        encoding="utf-8",
    )

    def fake_create_category_group(session, *, name, type):
        assert session.token == "token-123"
        assert name == "Bills"
        assert type is CategoryType.EXPENSE
        return CategoryGroup(id="group-1", name=name, type=type)

    monkeypatch.setattr(
        categories,
        "api_create_category_group",
        fake_create_category_group,
    )

    result = categories.create_category_group(
        name="Bills",
        type="expense",
        session_path=str(session_path),
    )

    assert result["id"] == "group-1"
    assert result["type"] == "expense"
