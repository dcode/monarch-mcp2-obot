from __future__ import annotations

from typing import Any

from mcp.server.mcpserver import MCPServer
from monarch_api import (
    create_recurring_stream as api_create_recurring_stream,
)
from monarch_api import (
    get_recurring_stream as api_get_recurring_stream,
)
from monarch_api import (
    get_recurring_summary as api_get_recurring_summary,
)
from monarch_api import (
    list_recurring_occurrences as api_list_recurring_occurrences,
)
from monarch_api import (
    list_recurring_streams as api_list_recurring_streams,
)
from monarch_api import (
    remove_recurring_stream as api_remove_recurring_stream,
)
from monarch_api import (
    update_recurring_stream as api_update_recurring_stream,
)

from monarch_mcp.converters import recurring_filter
from monarch_mcp.schemas import RecurringFilterInput, RecurringFrequencyValue
from monarch_mcp.serialization import to_jsonable
from monarch_mcp.session import require_session
from monarch_mcp.tool_metadata import register_api_tool


def list_recurring_streams(
    *,
    filters: RecurringFilterInput | None = None,
    include_pending: bool = True,
    include_liabilities: bool = True,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(
        api_list_recurring_streams(
            require_session(session_path),
            filters=recurring_filter(filters),
            include_pending=include_pending,
            include_liabilities=include_liabilities,
        )
    )


def get_recurring_stream(
    recurring_id: str,
    *,
    include_liabilities: bool = True,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(
        api_get_recurring_stream(
            require_session(session_path),
            recurring_id,
            include_liabilities=include_liabilities,
        )
    )


def list_recurring_occurrences(
    start_date: str,
    end_date: str,
    *,
    filters: RecurringFilterInput | None = None,
    include_liabilities: bool = True,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(
        api_list_recurring_occurrences(
            require_session(session_path),
            start_date,
            end_date,
            filters=recurring_filter(filters),
            include_liabilities=include_liabilities,
        )
    )


def get_recurring_summary(
    start_date: str,
    end_date: str,
    *,
    filters: RecurringFilterInput | None = None,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(
        api_get_recurring_summary(
            require_session(session_path),
            start_date,
            end_date,
            filters=recurring_filter(filters),
        )
    )


def create_recurring_stream(
    merchant_id: str,
    *,
    frequency: RecurringFrequencyValue,
    amount: float,
    base_date: str,
    is_active: bool = True,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(
        api_create_recurring_stream(
            require_session(session_path),
            merchant_id,
            frequency=frequency,
            amount=amount,
            base_date=base_date,
            is_active=is_active,
        )
    )


def update_recurring_stream(
    recurring_id: str,
    *,
    frequency: RecurringFrequencyValue | None = None,
    amount: float | None = None,
    base_date: str | None = None,
    is_active: bool | None = None,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(
        api_update_recurring_stream(
            require_session(session_path),
            recurring_id,
            frequency=frequency,
            amount=amount,
            base_date=base_date,
            is_active=is_active,
        )
    )


def remove_recurring_stream(
    recurring_id: str,
    *,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(api_remove_recurring_stream(require_session(session_path), recurring_id))


def register(mcp: MCPServer) -> None:
    register_api_tool(
        mcp,
        "recurring",
        "list_recurring_streams",
        list_recurring_streams,
    )
    register_api_tool(
        mcp,
        "recurring",
        "get_recurring_stream",
        get_recurring_stream,
    )
    register_api_tool(
        mcp,
        "recurring",
        "list_recurring_occurrences",
        list_recurring_occurrences,
    )
    register_api_tool(
        mcp,
        "recurring",
        "get_recurring_summary",
        get_recurring_summary,
    )
    register_api_tool(
        mcp,
        "recurring",
        "create_recurring_stream",
        create_recurring_stream,
    )
    register_api_tool(
        mcp,
        "recurring",
        "update_recurring_stream",
        update_recurring_stream,
    )
    register_api_tool(
        mcp,
        "recurring",
        "remove_recurring_stream",
        remove_recurring_stream,
    )
