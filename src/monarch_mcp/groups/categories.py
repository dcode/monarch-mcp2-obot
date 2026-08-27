from __future__ import annotations

from typing import Any

from mcp.server.mcpserver import MCPServer
from monarch_api import (
    CategoryFilter,
    CategoryType,
)
from monarch_api import (
    create_category as api_create_category,
)
from monarch_api import (
    create_category_group as api_create_category_group,
)
from monarch_api import (
    delete_category_group as api_delete_category_group,
)
from monarch_api import (
    get_category as api_get_category,
)
from monarch_api import (
    get_category_catalog as api_get_category_catalog,
)
from monarch_api import (
    get_category_group as api_get_category_group,
)
from monarch_api import (
    list_categories as api_list_categories,
)
from monarch_api import (
    list_category_groups as api_list_category_groups,
)
from monarch_api import (
    reactivate_category as api_reactivate_category,
)
from monarch_api import (
    remove_category as api_remove_category,
)
from monarch_api import (
    reorder_category as api_reorder_category,
)
from monarch_api import (
    reorder_category_group as api_reorder_category_group,
)
from monarch_api import (
    update_category as api_update_category,
)
from monarch_api import (
    update_category_group as api_update_category_group,
)

from monarch_mcp.schemas import CategoryFilterInput, CategoryTypeValue
from monarch_mcp.serialization import to_jsonable
from monarch_mcp.session import require_session
from monarch_mcp.tool_metadata import register_api_tool


def category_type_from_str(value: str | None) -> CategoryType | None:
    if value is None:
        return None
    return CategoryType(value)


def category_filter_from_dict(
    filters: CategoryFilterInput | dict[str, Any] | None,
) -> CategoryFilter | None:
    if filters is None:
        return None
    if isinstance(filters, CategoryFilterInput):
        filters = filters.model_dump(exclude_none=True)
    types = filters.get("types")
    return CategoryFilter(
        group_ids=filters.get("group_ids"),
        types=[CategoryType(type_) for type_ in types] if types is not None else None,
    )


def list_categories(
    *,
    filters: CategoryFilterInput | None = None,
    include_disabled: bool = False,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(
        api_list_categories(
            require_session(session_path),
            filters=category_filter_from_dict(filters),
            include_disabled=include_disabled,
        )
    )


def list_category_groups(*, session_path: str | None = None) -> Any:
    return to_jsonable(api_list_category_groups(require_session(session_path)))


def get_category_catalog(
    *,
    include_disabled: bool = False,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(
        api_get_category_catalog(
            require_session(session_path),
            include_disabled=include_disabled,
        )
    )


def get_category_group(group_id: str, *, session_path: str | None = None) -> Any:
    return to_jsonable(api_get_category_group(require_session(session_path), group_id))


def get_category(category_id: str, *, session_path: str | None = None) -> Any:
    return to_jsonable(api_get_category(require_session(session_path), category_id))


def create_category(
    *,
    name: str,
    group_id: str,
    icon: str,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(
        api_create_category(
            require_session(session_path),
            name=name,
            group_id=group_id,
            icon=icon,
        )
    )


def update_category(
    category_id: str,
    *,
    name: str | None = None,
    group_id: str | None = None,
    icon: str | None = None,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(
        api_update_category(
            require_session(session_path),
            category_id,
            name=name,
            group_id=group_id,
            icon=icon,
        )
    )


def remove_category(
    category_id: str,
    *,
    move_to_category_id: str | None = None,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(
        api_remove_category(
            require_session(session_path),
            category_id,
            move_to_category_id=move_to_category_id,
        )
    )


def reactivate_category(category_id: str, *, session_path: str | None = None) -> Any:
    return to_jsonable(api_reactivate_category(require_session(session_path), category_id))


def reorder_category(
    category_id: str,
    *,
    group_id: str,
    order: int,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(
        api_reorder_category(
            require_session(session_path),
            category_id,
            group_id=group_id,
            order=order,
        )
    )


def create_category_group(
    *,
    name: str,
    type: CategoryTypeValue,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(
        api_create_category_group(
            require_session(session_path),
            name=name,
            type=CategoryType(type),
        )
    )


def update_category_group(
    group_id: str,
    *,
    name: str | None = None,
    type: CategoryTypeValue | None = None,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(
        api_update_category_group(
            require_session(session_path),
            group_id,
            name=name,
            type=category_type_from_str(type),
        )
    )


def delete_category_group(
    group_id: str,
    *,
    move_to_group_id: str | None = None,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(
        api_delete_category_group(
            require_session(session_path),
            group_id,
            move_to_group_id=move_to_group_id,
        )
    )


def reorder_category_group(
    group_id: str,
    *,
    order: int,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(
        api_reorder_category_group(
            require_session(session_path),
            group_id,
            order=order,
        )
    )


def register(mcp: MCPServer) -> None:
    register_api_tool(mcp, "categories", "list_categories", list_categories)
    register_api_tool(
        mcp,
        "categories",
        "list_category_groups",
        list_category_groups,
    )
    register_api_tool(
        mcp,
        "categories",
        "get_category_catalog",
        get_category_catalog,
    )
    register_api_tool(mcp, "categories", "get_category_group", get_category_group)
    register_api_tool(mcp, "categories", "get_category", get_category)
    register_api_tool(mcp, "categories", "create_category", create_category)
    register_api_tool(mcp, "categories", "update_category", update_category)
    register_api_tool(mcp, "categories", "remove_category", remove_category)
    register_api_tool(mcp, "categories", "reactivate_category", reactivate_category)
    register_api_tool(mcp, "categories", "reorder_category", reorder_category)
    register_api_tool(
        mcp,
        "categories",
        "create_category_group",
        create_category_group,
    )
    register_api_tool(
        mcp,
        "categories",
        "update_category_group",
        update_category_group,
    )
    register_api_tool(
        mcp,
        "categories",
        "delete_category_group",
        delete_category_group,
    )
    register_api_tool(
        mcp,
        "categories",
        "reorder_category_group",
        reorder_category_group,
    )
