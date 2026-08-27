from __future__ import annotations

from typing import Any

from mcp.server.mcpserver import MCPServer
from monarch_api import (
    MerchantSort,
)
from monarch_api import (
    delete_merchant as api_delete_merchant,
)
from monarch_api import (
    get_merchant as api_get_merchant,
)
from monarch_api import (
    list_merchants as api_list_merchants,
)
from monarch_api import (
    update_merchant as api_update_merchant,
)

from monarch_mcp.schemas import MerchantSortValue
from monarch_mcp.serialization import to_jsonable
from monarch_mcp.session import require_session
from monarch_mcp.tool_metadata import register_api_tool


def list_merchants(
    *,
    search: str | None = None,
    limit: int | None = None,
    offset: int | None = None,
    sort: MerchantSortValue = "TRANSACTION_COUNT",
    session_path: str | None = None,
) -> Any:
    return to_jsonable(
        api_list_merchants(
            require_session(session_path),
            search=search,
            limit=limit,
            offset=offset,
            sort=MerchantSort(sort),
        )
    )


def get_merchant(merchant_id: str, *, session_path: str | None = None) -> Any:
    return to_jsonable(api_get_merchant(require_session(session_path), merchant_id))


def update_merchant(
    merchant_id: str,
    *,
    name: str | None = None,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(api_update_merchant(require_session(session_path), merchant_id, name=name))


def delete_merchant(
    merchant_id: str,
    *,
    move_to_merchant_id: str | None = None,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(
        api_delete_merchant(
            require_session(session_path),
            merchant_id,
            move_to_merchant_id=move_to_merchant_id,
        )
    )


def register(mcp: MCPServer) -> None:
    register_api_tool(mcp, "merchants", "list_merchants", list_merchants)
    register_api_tool(mcp, "merchants", "get_merchant", get_merchant)
    register_api_tool(mcp, "merchants", "update_merchant", update_merchant)
    register_api_tool(mcp, "merchants", "delete_merchant", delete_merchant)
