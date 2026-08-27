from __future__ import annotations

from typing import Any

from mcp.server.mcpserver import MCPServer
from monarch_api import (
    create_saved_report as api_create_saved_report,
)
from monarch_api import (
    delete_saved_report as api_delete_saved_report,
)
from monarch_api import (
    get_report_data as api_get_report_data,
)
from monarch_api import (
    get_saved_report as api_get_saved_report,
)
from monarch_api import (
    list_saved_reports as api_list_saved_reports,
)
from monarch_api import (
    update_saved_report as api_update_saved_report,
)

from monarch_mcp.converters import (
    report_groups,
    report_sort,
    report_timeframe,
    transaction_filter,
)
from monarch_mcp.schemas import (
    ReportGroupValue,
    ReportSortValue,
    ReportTimeframeValue,
    TransactionFilterInput,
)
from monarch_mcp.serialization import to_jsonable
from monarch_mcp.session import require_session
from monarch_mcp.tool_metadata import register_api_tool


def get_report_data(
    *,
    filters: TransactionFilterInput | None = None,
    group_by: ReportGroupValue | list[ReportGroupValue] | None = "category",
    timeframe: ReportTimeframeValue | None = None,
    sort_by: ReportSortValue | None = None,
    fill_empty_values: bool = True,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(
        api_get_report_data(
            require_session(session_path),
            filters=transaction_filter(filters),
            group_by=report_groups(group_by),
            timeframe=report_timeframe(timeframe),
            sort_by=report_sort(sort_by),
            fill_empty_values=fill_empty_values,
        )
    )


def list_saved_reports(*, session_path: str | None = None) -> Any:
    return to_jsonable(api_list_saved_reports(require_session(session_path)))


def get_saved_report(report_id: str, *, session_path: str | None = None) -> Any:
    return to_jsonable(api_get_saved_report(require_session(session_path), report_id))


def create_saved_report(
    name: str,
    *,
    filters: TransactionFilterInput | None = None,
    group_by: ReportGroupValue | list[ReportGroupValue] | None = "category",
    timeframe: ReportTimeframeValue | None = None,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(
        api_create_saved_report(
            require_session(session_path),
            name,
            filters=transaction_filter(filters),
            group_by=report_groups(group_by),
            timeframe=report_timeframe(timeframe),
        )
    )


def update_saved_report(
    report_id: str,
    *,
    name: str,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(api_update_saved_report(require_session(session_path), report_id, name=name))


def delete_saved_report(report_id: str, *, session_path: str | None = None) -> Any:
    return to_jsonable(api_delete_saved_report(require_session(session_path), report_id))


def register(mcp: MCPServer) -> None:
    register_api_tool(mcp, "reports", "get_report_data", get_report_data)
    register_api_tool(mcp, "reports", "list_saved_reports", list_saved_reports)
    register_api_tool(mcp, "reports", "get_saved_report", get_saved_report)
    register_api_tool(mcp, "reports", "create_saved_report", create_saved_report)
    register_api_tool(mcp, "reports", "update_saved_report", update_saved_report)
    register_api_tool(mcp, "reports", "delete_saved_report", delete_saved_report)
