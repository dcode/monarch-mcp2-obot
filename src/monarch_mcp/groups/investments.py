from __future__ import annotations

from typing import Any

from mcp.server.mcpserver import MCPServer
from monarch_api import (
    create_manual_holding as api_create_manual_holding,
)
from monarch_api import (
    delete_manual_holding as api_delete_manual_holding,
)
from monarch_api import (
    get_holding as api_get_holding,
)
from monarch_api import (
    get_holding_performance as api_get_holding_performance,
)
from monarch_api import (
    get_portfolio as api_get_portfolio,
)
from monarch_api import (
    get_security as api_get_security,
)
from monarch_api import (
    list_holdings as api_list_holdings,
)
from monarch_api import (
    list_investment_accounts as api_list_investment_accounts,
)
from monarch_api import (
    search_securities as api_search_securities,
)
from monarch_api import (
    update_manual_holding as api_update_manual_holding,
)

from monarch_mcp.serialization import to_jsonable
from monarch_mcp.session import require_session
from monarch_mcp.tool_metadata import register_api_tool


def list_investment_accounts(*, session_path: str | None = None) -> Any:
    return to_jsonable(api_list_investment_accounts(require_session(session_path)))


def list_holdings(
    *,
    account_ids: list[str] | None = None,
    include_hidden_holdings: bool | None = None,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(
        api_list_holdings(
            require_session(session_path),
            account_ids=account_ids,
            include_hidden_holdings=include_hidden_holdings,
        )
    )


def get_holding(holding_id: str, *, session_path: str | None = None) -> Any:
    return to_jsonable(api_get_holding(require_session(session_path), holding_id))


def get_holding_performance(
    holding_id: str,
    *,
    start_date: str | None = None,
    end_date: str | None = None,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(
        api_get_holding_performance(
            require_session(session_path),
            holding_id,
            start_date=start_date,
            end_date=end_date,
        )
    )


def get_portfolio(
    *,
    account_ids: list[str] | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    include_hidden_holdings: bool | None = None,
    top_movers_limit: int | None = None,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(
        api_get_portfolio(
            require_session(session_path),
            account_ids=account_ids,
            start_date=start_date,
            end_date=end_date,
            include_hidden_holdings=include_hidden_holdings,
            top_movers_limit=top_movers_limit,
        )
    )


def get_security(security_id: str, *, session_path: str | None = None) -> Any:
    return to_jsonable(api_get_security(require_session(session_path), security_id))


def search_securities(
    query: str,
    *,
    limit: int = 20,
    order_by_popularity: bool = True,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(
        api_search_securities(
            require_session(session_path),
            query,
            limit=limit,
            order_by_popularity=order_by_popularity,
        )
    )


def create_manual_holding(
    *,
    account_id: str,
    security_id: str,
    quantity: float,
    cost_basis: float | None = None,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(
        api_create_manual_holding(
            require_session(session_path),
            account_id=account_id,
            security_id=security_id,
            quantity=quantity,
            cost_basis=cost_basis,
        )
    )


def update_manual_holding(
    holding_id: str,
    *,
    quantity: float | None = None,
    cost_basis: float | None = None,
    security_type: str | None = None,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(
        api_update_manual_holding(
            require_session(session_path),
            holding_id,
            quantity=quantity,
            cost_basis=cost_basis,
            security_type=security_type,
        )
    )


def delete_manual_holding(
    holding_id: str,
    *,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(api_delete_manual_holding(require_session(session_path), holding_id))


def register(mcp: MCPServer) -> None:
    register_api_tool(
        mcp,
        "investments",
        "list_investment_accounts",
        list_investment_accounts,
    )
    register_api_tool(mcp, "investments", "list_holdings", list_holdings)
    register_api_tool(mcp, "investments", "get_holding", get_holding)
    register_api_tool(
        mcp,
        "investments",
        "get_holding_performance",
        get_holding_performance,
    )
    register_api_tool(mcp, "investments", "get_portfolio", get_portfolio)
    register_api_tool(mcp, "investments", "get_security", get_security)
    register_api_tool(mcp, "investments", "search_securities", search_securities)
    register_api_tool(
        mcp,
        "investments",
        "create_manual_holding",
        create_manual_holding,
    )
    register_api_tool(
        mcp,
        "investments",
        "update_manual_holding",
        update_manual_holding,
    )
    register_api_tool(
        mcp,
        "investments",
        "delete_manual_holding",
        delete_manual_holding,
    )
