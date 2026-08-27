from __future__ import annotations

from typing import Any

from mcp.server.mcpserver import MCPServer
from monarch_api import (
    archive_goal as api_archive_goal,
)
from monarch_api import (
    contribute_to_goal as api_contribute_to_goal,
)
from monarch_api import (
    create_goal as api_create_goal,
)
from monarch_api import (
    delete_goal as api_delete_goal,
)
from monarch_api import (
    delete_goal_event as api_delete_goal_event,
)
from monarch_api import (
    get_goal as api_get_goal,
)
from monarch_api import (
    get_goal_budget_amounts as api_get_goal_budget_amounts,
)
from monarch_api import (
    link_goal_account_balance as api_link_goal_account_balance,
)
from monarch_api import (
    list_goal_events as api_list_goal_events,
)
from monarch_api import (
    list_goals as api_list_goals,
)
from monarch_api import (
    restore_goal as api_restore_goal,
)
from monarch_api import (
    set_goal_budget_amount as api_set_goal_budget_amount,
)
from monarch_api import (
    unlink_goal_account as api_unlink_goal_account,
)
from monarch_api import (
    update_goal as api_update_goal,
)
from monarch_api import (
    update_goal_event as api_update_goal_event,
)
from monarch_api import (
    update_goal_priorities as api_update_goal_priorities,
)
from monarch_api import (
    withdraw_from_goal as api_withdraw_from_goal,
)

from monarch_mcp.schemas import GoalStatusValue, GoalTypeValue
from monarch_mcp.serialization import to_jsonable
from monarch_mcp.session import require_session
from monarch_mcp.tool_metadata import register_api_tool


def list_goals(
    *,
    include_archived: bool = False,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(
        api_list_goals(
            require_session(session_path),
            include_archived=include_archived,
        )
    )


def get_goal(goal_id: str, *, session_path: str | None = None) -> Any:
    return to_jsonable(api_get_goal(require_session(session_path), goal_id))


def create_goal(
    *,
    name: str,
    goal_type: GoalTypeValue = "custom",
    target_amount: float | None = None,
    target_date: str | None = None,
    planned_monthly_contribution: float | None = None,
    is_sinking_fund: bool | None = None,
    priority: int | None = None,
    image_storage_provider: str | None = None,
    image_storage_provider_id: str | None = None,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(
        api_create_goal(
            require_session(session_path),
            name=name,
            goal_type=goal_type,
            target_amount=target_amount,
            target_date=target_date,
            planned_monthly_contribution=planned_monthly_contribution,
            is_sinking_fund=is_sinking_fund,
            priority=priority,
            image_storage_provider=image_storage_provider,
            image_storage_provider_id=image_storage_provider_id,
        )
    )


def update_goal(
    goal_id: str,
    *,
    name: str | None = None,
    goal_type: GoalTypeValue | None = None,
    target_amount: float | None = None,
    target_date: str | None = None,
    planned_monthly_contribution: float | None = None,
    is_sinking_fund: bool | None = None,
    priority: int | None = None,
    image_storage_provider: str | None = None,
    image_storage_provider_id: str | None = None,
    status: GoalStatusValue | None = None,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(
        api_update_goal(
            require_session(session_path),
            goal_id,
            name=name,
            goal_type=goal_type,
            target_amount=target_amount,
            target_date=target_date,
            planned_monthly_contribution=planned_monthly_contribution,
            is_sinking_fund=is_sinking_fund,
            priority=priority,
            image_storage_provider=image_storage_provider,
            image_storage_provider_id=image_storage_provider_id,
            status=status,
        )
    )


def delete_goal(goal_id: str, *, session_path: str | None = None) -> Any:
    return to_jsonable(api_delete_goal(require_session(session_path), goal_id))


def archive_goal(goal_id: str, *, session_path: str | None = None) -> Any:
    return to_jsonable(api_archive_goal(require_session(session_path), goal_id))


def restore_goal(goal_id: str, *, session_path: str | None = None) -> Any:
    return to_jsonable(api_restore_goal(require_session(session_path), goal_id))


def update_goal_priorities(
    goal_ids: list[str],
    *,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(api_update_goal_priorities(require_session(session_path), goal_ids))


def link_goal_account_balance(
    goal_id: str,
    account_id: str,
    *,
    use_entire_balance: bool = True,
    amount: float | None = None,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(
        api_link_goal_account_balance(
            require_session(session_path),
            goal_id,
            account_id,
            use_entire_balance=use_entire_balance,
            amount=amount,
        )
    )


def unlink_goal_account(
    goal_id: str,
    account_id: str,
    *,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(api_unlink_goal_account(require_session(session_path), goal_id, account_id))


def list_goal_events(goal_id: str, *, session_path: str | None = None) -> Any:
    return to_jsonable(api_list_goal_events(require_session(session_path), goal_id))


def contribute_to_goal(
    goal_id: str,
    account_id: str,
    *,
    amount: float,
    date: str | None = None,
    include_in_budget: bool | None = None,
    notes: str | None = None,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(
        api_contribute_to_goal(
            require_session(session_path),
            goal_id,
            account_id,
            amount=amount,
            date=date,
            include_in_budget=include_in_budget,
            notes=notes,
        )
    )


def withdraw_from_goal(
    goal_id: str,
    account_id: str,
    *,
    amount: float,
    date: str | None = None,
    include_in_budget: bool | None = None,
    notes: str | None = None,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(
        api_withdraw_from_goal(
            require_session(session_path),
            goal_id,
            account_id,
            amount=amount,
            date=date,
            include_in_budget=include_in_budget,
            notes=notes,
        )
    )


def update_goal_event(
    event_id: str,
    *,
    date: str | None = None,
    include_in_budget: bool | None = None,
    notes: str | None = None,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(
        api_update_goal_event(
            require_session(session_path),
            event_id,
            date=date,
            include_in_budget=include_in_budget,
            notes=notes,
        )
    )


def delete_goal_event(event_id: str, *, session_path: str | None = None) -> Any:
    return to_jsonable(api_delete_goal_event(require_session(session_path), event_id))


def get_goal_budget_amounts(
    goal_id: str,
    start_month: str,
    end_month: str,
    *,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(
        api_get_goal_budget_amounts(
            require_session(session_path),
            goal_id,
            start_month,
            end_month,
        )
    )


def set_goal_budget_amount(
    goal_id: str,
    month: str,
    amount: float,
    *,
    apply_to_future: bool = False,
    account_id: str | None = None,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(
        api_set_goal_budget_amount(
            require_session(session_path),
            goal_id,
            month,
            amount,
            apply_to_future=apply_to_future,
            account_id=account_id,
        )
    )


def register(mcp: MCPServer) -> None:
    register_api_tool(mcp, "goals", "list_goals", list_goals)
    register_api_tool(mcp, "goals", "get_goal", get_goal)
    register_api_tool(mcp, "goals", "create_goal", create_goal)
    register_api_tool(mcp, "goals", "update_goal", update_goal)
    register_api_tool(mcp, "goals", "delete_goal", delete_goal)
    register_api_tool(mcp, "goals", "archive_goal", archive_goal)
    register_api_tool(mcp, "goals", "restore_goal", restore_goal)
    register_api_tool(
        mcp,
        "goals",
        "update_goal_priorities",
        update_goal_priorities,
    )
    register_api_tool(
        mcp,
        "goals",
        "link_goal_account_balance",
        link_goal_account_balance,
    )
    register_api_tool(mcp, "goals", "unlink_goal_account", unlink_goal_account)
    register_api_tool(mcp, "goals", "list_goal_events", list_goal_events)
    register_api_tool(mcp, "goals", "contribute_to_goal", contribute_to_goal)
    register_api_tool(mcp, "goals", "withdraw_from_goal", withdraw_from_goal)
    register_api_tool(mcp, "goals", "update_goal_event", update_goal_event)
    register_api_tool(mcp, "goals", "delete_goal_event", delete_goal_event)
    register_api_tool(
        mcp,
        "goals",
        "get_goal_budget_amounts",
        get_goal_budget_amounts,
    )
    register_api_tool(
        mcp,
        "goals",
        "set_goal_budget_amount",
        set_goal_budget_amount,
    )
