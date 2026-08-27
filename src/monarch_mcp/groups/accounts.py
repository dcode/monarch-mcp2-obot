from __future__ import annotations

from typing import Any

from mcp.server.mcpserver import MCPServer
from monarch_api import (
    AccountFilter,
)
from monarch_api import (
    create_manual_account as api_create_manual_account,
)
from monarch_api import (
    delete_account as api_delete_account,
)
from monarch_api import (
    get_account as api_get_account,
)
from monarch_api import (
    get_account_history as api_get_account_history,
)
from monarch_api import (
    get_historical_balances as api_get_historical_balances,
)
from monarch_api import (
    get_net_worth_breakdown as api_get_net_worth_breakdown,
)
from monarch_api import (
    get_net_worth_performance as api_get_net_worth_performance,
)
from monarch_api import (
    list_accounts as api_list_accounts,
)
from monarch_api import (
    update_account as api_update_account,
)

from monarch_mcp.schemas import AccountFilterInput
from monarch_mcp.serialization import to_jsonable
from monarch_mcp.session import require_session
from monarch_mcp.tool_metadata import register_api_tool


def account_filter_from_dict(filters: dict[str, Any] | None) -> AccountFilter | None:
    if filters is None:
        return None
    if isinstance(filters, AccountFilterInput):
        filters = filters.model_dump(exclude_none=True)
    return AccountFilter(
        account_ids=filters.get("account_ids"),
        account_types=filters.get("account_types"),
        account_subtypes=filters.get("account_subtypes"),
        groups=filters.get("groups"),
        include_hidden=filters.get("include_hidden"),
        include_deleted=filters.get("include_deleted"),
    )


def list_accounts(
    *,
    filters: AccountFilterInput | None = None,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(
        api_list_accounts(
            require_session(session_path),
            filters=account_filter_from_dict(filters),
        )
    )


def get_account(account_id: str, *, session_path: str | None = None) -> Any:
    return to_jsonable(api_get_account(require_session(session_path), account_id))


def get_net_worth_performance(
    *,
    start_date: str | None = None,
    end_date: str | None = None,
    filters: AccountFilterInput | None = None,
    use_adaptive_granularity: bool | None = None,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(
        api_get_net_worth_performance(
            require_session(session_path),
            start_date=start_date,
            end_date=end_date,
            filters=account_filter_from_dict(filters),
            use_adaptive_granularity=use_adaptive_granularity,
        )
    )


def get_net_worth_breakdown(
    start_date: str,
    timeframe: str,
    *,
    filters: AccountFilterInput | None = None,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(
        api_get_net_worth_breakdown(
            require_session(session_path),
            start_date,
            timeframe,
            filters=account_filter_from_dict(filters),
        )
    )


def get_historical_balances(
    balance_date: str,
    *,
    filters: AccountFilterInput | None = None,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(
        api_get_historical_balances(
            require_session(session_path),
            balance_date,
            filters=account_filter_from_dict(filters),
        )
    )


def get_account_history(account_id: str, *, session_path: str | None = None) -> Any:
    return to_jsonable(api_get_account_history(require_session(session_path), account_id))


def create_manual_account(
    *,
    name: str,
    type: str,
    subtype: str,
    balance: float | None = None,
    include_in_net_worth: bool = True,
    owner_user_id: str | None = None,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(
        api_create_manual_account(
            require_session(session_path),
            name=name,
            type=type,
            subtype=subtype,
            balance=balance,
            include_in_net_worth=include_in_net_worth,
            owner_user_id=owner_user_id,
        )
    )


def update_account(
    account_id: str,
    *,
    name: str | None = None,
    type: str | None = None,
    subtype: str | None = None,
    balance: float | None = None,
    include_in_net_worth: bool | None = None,
    hide_from_list: bool | None = None,
    hide_transactions_from_reports: bool | None = None,
    owner_user_id: str | None = None,
    deactivated_at: str | None = None,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(
        api_update_account(
            require_session(session_path),
            account_id,
            name=name,
            type=type,
            subtype=subtype,
            balance=balance,
            include_in_net_worth=include_in_net_worth,
            hide_from_list=hide_from_list,
            hide_transactions_from_reports=hide_transactions_from_reports,
            owner_user_id=owner_user_id,
            deactivated_at=deactivated_at,
        )
    )


def delete_account(account_id: str, *, session_path: str | None = None) -> Any:
    return to_jsonable(api_delete_account(require_session(session_path), account_id))


def register(mcp: MCPServer) -> None:
    register_api_tool(mcp, "accounts", "list_accounts", list_accounts)
    register_api_tool(mcp, "accounts", "get_account", get_account)
    register_api_tool(
        mcp,
        "accounts",
        "get_net_worth_performance",
        get_net_worth_performance,
    )
    register_api_tool(
        mcp,
        "accounts",
        "get_net_worth_breakdown",
        get_net_worth_breakdown,
    )
    register_api_tool(
        mcp,
        "accounts",
        "get_historical_balances",
        get_historical_balances,
    )
    register_api_tool(mcp, "accounts", "get_account_history", get_account_history)
    register_api_tool(mcp, "accounts", "create_manual_account", create_manual_account)
    register_api_tool(mcp, "accounts", "update_account", update_account)
    register_api_tool(mcp, "accounts", "delete_account", delete_account)
