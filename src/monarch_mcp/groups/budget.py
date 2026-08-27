from __future__ import annotations

from typing import Any

from mcp.server.mcpserver import MCPServer
from monarch_api import (
    clear_budget as api_clear_budget,
)
from monarch_api import (
    create_budget as api_create_budget,
)
from monarch_api import (
    get_budget as api_get_budget,
)
from monarch_api import (
    get_budget_category as api_get_budget_category,
)
from monarch_api import (
    get_budget_settings as api_get_budget_settings,
)
from monarch_api import (
    get_flex_rollover_settings as api_get_flex_rollover_settings,
)
from monarch_api import (
    list_budget_months as api_list_budget_months,
)
from monarch_api import (
    reset_budget as api_reset_budget,
)
from monarch_api import (
    reset_budget_rollover as api_reset_budget_rollover,
)
from monarch_api import (
    set_budget_amount as api_set_budget_amount,
)
from monarch_api import (
    set_budget_category_rollover as api_set_budget_category_rollover,
)
from monarch_api import (
    set_budget_category_variability as api_set_budget_category_variability,
)
from monarch_api import (
    set_budget_group_amount as api_set_budget_group_amount,
)
from monarch_api import (
    set_budget_group_rollover as api_set_budget_group_rollover,
)
from monarch_api import (
    set_budget_group_variability as api_set_budget_group_variability,
)
from monarch_api import (
    set_flex_budget_amount as api_set_flex_budget_amount,
)
from monarch_api import (
    set_flex_rollover_settings as api_set_flex_rollover_settings,
)

from monarch_mcp.schemas import (
    BudgetRolloverFrequencyValue,
    BudgetRolloverTypeValue,
    BudgetVariabilityValue,
    CategoryTypeValue,
)
from monarch_mcp.serialization import to_jsonable
from monarch_mcp.session import require_session
from monarch_mcp.tool_metadata import register_api_tool


def get_budget(month: str, *, session_path: str | None = None) -> Any:
    return to_jsonable(api_get_budget(require_session(session_path), month))


def list_budget_months(
    start_month: str,
    end_month: str,
    *,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(
        api_list_budget_months(require_session(session_path), start_month, end_month)
    )


def get_budget_settings(*, session_path: str | None = None) -> Any:
    return to_jsonable(api_get_budget_settings(require_session(session_path)))


def get_budget_category(
    month: str,
    category_id: str,
    *,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(api_get_budget_category(require_session(session_path), month, category_id))


def get_flex_rollover_settings(*, session_path: str | None = None) -> Any:
    return to_jsonable(api_get_flex_rollover_settings(require_session(session_path)))


def set_budget_amount(
    month: str,
    category_id: str,
    amount: float,
    *,
    apply_to_future: bool = False,
    default_amount: float | None = None,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(
        api_set_budget_amount(
            require_session(session_path),
            month,
            category_id,
            amount,
            apply_to_future=apply_to_future,
            default_amount=default_amount,
        )
    )


def set_budget_group_amount(
    month: str,
    category_group_id: str,
    amount: float,
    *,
    apply_to_future: bool = False,
    default_amount: float | None = None,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(
        api_set_budget_group_amount(
            require_session(session_path),
            month,
            category_group_id,
            amount,
            apply_to_future=apply_to_future,
            default_amount=default_amount,
        )
    )


def set_flex_budget_amount(
    month: str,
    amount: float,
    *,
    apply_to_future: bool = False,
    default_amount: float | None = None,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(
        api_set_flex_budget_amount(
            require_session(session_path),
            month,
            amount,
            apply_to_future=apply_to_future,
            default_amount=default_amount,
        )
    )


def set_budget_category_variability(
    category_id: str,
    variability: BudgetVariabilityValue,
    *,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(
        api_set_budget_category_variability(
            require_session(session_path),
            category_id,
            variability,
        )
    )


def set_budget_group_variability(
    category_group_id: str,
    variability: BudgetVariabilityValue,
    *,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(
        api_set_budget_group_variability(
            require_session(session_path),
            category_group_id,
            variability,
        )
    )


def set_budget_category_rollover(
    category_id: str,
    *,
    enabled: bool,
    start_month: str | None = None,
    starting_balance: float | None = None,
    frequency: BudgetRolloverFrequencyValue | None = None,
    target_amount: float | None = None,
    rollover_type: BudgetRolloverTypeValue | None = None,
    apply_to_future: bool | None = None,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(
        api_set_budget_category_rollover(
            require_session(session_path),
            category_id,
            enabled=enabled,
            start_month=start_month,
            starting_balance=starting_balance,
            frequency=frequency,
            target_amount=target_amount,
            rollover_type=rollover_type,
            apply_to_future=apply_to_future,
        )
    )


def set_budget_group_rollover(
    category_group_id: str,
    *,
    enabled: bool,
    start_month: str | None = None,
    starting_balance: float | None = None,
    rollover_type: BudgetRolloverTypeValue | None = None,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(
        api_set_budget_group_rollover(
            require_session(session_path),
            category_group_id,
            enabled=enabled,
            start_month=start_month,
            starting_balance=starting_balance,
            rollover_type=rollover_type,
        )
    )


def set_flex_rollover_settings(
    *,
    enabled: bool,
    start_month: str | None = None,
    starting_balance: float | None = None,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(
        api_set_flex_rollover_settings(
            require_session(session_path),
            enabled=enabled,
            start_month=start_month,
            starting_balance=starting_balance,
        )
    )


def reset_budget_rollover(
    month: str,
    *,
    category_id: str | None = None,
    category_group_id: str | None = None,
    starting_balance: float | None = None,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(
        api_reset_budget_rollover(
            require_session(session_path),
            month,
            category_id=category_id,
            category_group_id=category_group_id,
            starting_balance=starting_balance,
        )
    )


def create_budget(month: str, *, session_path: str | None = None) -> Any:
    return to_jsonable(api_create_budget(require_session(session_path), month))


def reset_budget(
    month: str,
    *,
    category_ids: list[str] | None = None,
    category_type: CategoryTypeValue | None = None,
    budget_variability: BudgetVariabilityValue | None = None,
    overwrite_existing: bool = False,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(
        api_reset_budget(
            require_session(session_path),
            month,
            category_ids=category_ids,
            category_type=category_type,
            budget_variability=budget_variability,
            overwrite_existing=overwrite_existing,
        )
    )


def clear_budget(
    month: str,
    *,
    confirm: bool = False,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(api_clear_budget(require_session(session_path), month, confirm=confirm))


def register(mcp: MCPServer) -> None:
    register_api_tool(mcp, "budget", "get_budget", get_budget)
    register_api_tool(mcp, "budget", "list_budget_months", list_budget_months)
    register_api_tool(mcp, "budget", "get_budget_settings", get_budget_settings)
    register_api_tool(mcp, "budget", "get_budget_category", get_budget_category)
    register_api_tool(
        mcp,
        "budget",
        "get_flex_rollover_settings",
        get_flex_rollover_settings,
    )
    register_api_tool(mcp, "budget", "set_budget_amount", set_budget_amount)
    register_api_tool(
        mcp,
        "budget",
        "set_budget_group_amount",
        set_budget_group_amount,
    )
    register_api_tool(mcp, "budget", "set_flex_budget_amount", set_flex_budget_amount)
    register_api_tool(
        mcp,
        "budget",
        "set_budget_category_variability",
        set_budget_category_variability,
    )
    register_api_tool(
        mcp,
        "budget",
        "set_budget_group_variability",
        set_budget_group_variability,
    )
    register_api_tool(
        mcp,
        "budget",
        "set_budget_category_rollover",
        set_budget_category_rollover,
    )
    register_api_tool(
        mcp,
        "budget",
        "set_budget_group_rollover",
        set_budget_group_rollover,
    )
    register_api_tool(
        mcp,
        "budget",
        "set_flex_rollover_settings",
        set_flex_rollover_settings,
    )
    register_api_tool(mcp, "budget", "reset_budget_rollover", reset_budget_rollover)
    register_api_tool(mcp, "budget", "create_budget", create_budget)
    register_api_tool(mcp, "budget", "reset_budget", reset_budget)
    register_api_tool(mcp, "budget", "clear_budget", clear_budget)
