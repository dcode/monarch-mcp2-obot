from __future__ import annotations

from typing import Any

from mcp.server.mcpserver import MCPServer
from monarch_api import (
    get_current_user as api_get_current_user,
)
from monarch_api import (
    get_household as api_get_household,
)
from monarch_api import (
    get_household_member as api_get_household_member,
)
from monarch_api import (
    get_household_preferences as api_get_household_preferences,
)
from monarch_api import (
    list_household_members as api_list_household_members,
)
from monarch_api import (
    update_current_user as api_update_current_user,
)
from monarch_api import (
    update_household_preferences as api_update_household_preferences,
)

from monarch_mcp.serialization import to_jsonable
from monarch_mcp.session import require_session
from monarch_mcp.tool_metadata import register_api_tool


def get_current_user(*, session_path: str | None = None) -> Any:
    return to_jsonable(api_get_current_user(require_session(session_path)))


def get_household(*, session_path: str | None = None) -> Any:
    return to_jsonable(api_get_household(require_session(session_path)))


def list_household_members(*, session_path: str | None = None) -> Any:
    return to_jsonable(api_list_household_members(require_session(session_path)))


def get_household_member(member_id: str, *, session_path: str | None = None) -> Any:
    return to_jsonable(api_get_household_member(require_session(session_path), member_id))


def get_household_preferences(*, session_path: str | None = None) -> Any:
    return to_jsonable(api_get_household_preferences(require_session(session_path)))


def update_current_user(
    *,
    display_name: str | None = None,
    timezone: str | None = None,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(
        api_update_current_user(
            require_session(session_path),
            display_name=display_name,
            timezone=timezone,
        )
    )


def update_household_preferences(
    *,
    new_transactions_need_review: bool | None = None,
    uncategorized_transactions_need_review: bool | None = None,
    pending_transactions_can_be_edited: bool | None = None,
    hidden_transactions_beta_enabled: bool | None = None,
    exclude_business_from_budget: bool | None = None,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(
        api_update_household_preferences(
            require_session(session_path),
            new_transactions_need_review=new_transactions_need_review,
            uncategorized_transactions_need_review=uncategorized_transactions_need_review,
            pending_transactions_can_be_edited=pending_transactions_can_be_edited,
            hidden_transactions_beta_enabled=hidden_transactions_beta_enabled,
            exclude_business_from_budget=exclude_business_from_budget,
        )
    )


def register(mcp: MCPServer) -> None:
    register_api_tool(mcp, "household", "get_current_user", get_current_user)
    register_api_tool(mcp, "household", "get_household", get_household)
    register_api_tool(
        mcp,
        "household",
        "get_household_member",
        get_household_member,
    )
    register_api_tool(
        mcp,
        "household",
        "get_household_preferences",
        get_household_preferences,
    )
    register_api_tool(
        mcp,
        "household",
        "list_household_members",
        list_household_members,
    )
    register_api_tool(mcp, "household", "update_current_user", update_current_user)
    register_api_tool(
        mcp,
        "household",
        "update_household_preferences",
        update_household_preferences,
    )
