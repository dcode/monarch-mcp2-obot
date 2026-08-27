from __future__ import annotations

from typing import Any

from mcp.server.mcpserver import MCPServer
from monarch_api import (
    create_transaction as api_create_transaction,
)
from monarch_api import (
    delete_transaction as api_delete_transaction,
)
from monarch_api import (
    delete_transaction_attachment as api_delete_transaction_attachment,
)
from monarch_api import (
    download_transaction_attachment as api_download_transaction_attachment,
)
from monarch_api import (
    get_transaction as api_get_transaction,
)
from monarch_api import (
    get_transaction_attachment as api_get_transaction_attachment,
)
from monarch_api import (
    get_transaction_splits as api_get_transaction_splits,
)
from monarch_api import (
    list_transaction_attachments as api_list_transaction_attachments,
)
from monarch_api import (
    list_transactions as api_list_transactions,
)
from monarch_api import (
    unsplit_transaction as api_unsplit_transaction,
)
from monarch_api import (
    update_transaction as api_update_transaction,
)
from monarch_api import (
    update_transaction_splits as api_update_transaction_splits,
)
from monarch_api import (
    upload_transaction_attachment as api_upload_transaction_attachment,
)

from monarch_mcp.converters import (
    review_status,
    transaction_filter,
    transaction_sort,
    transaction_split_drafts,
)
from monarch_mcp.schemas import (
    TransactionFilterInput,
    TransactionReviewStatusValue,
    TransactionSortValue,
    TransactionSplitDraftInput,
)
from monarch_mcp.serialization import to_jsonable
from monarch_mcp.session import require_session
from monarch_mcp.tool_metadata import register_api_tool


def list_transactions(
    *,
    filters: TransactionFilterInput | None = None,
    limit: int = 100,
    offset: int = 0,
    sort: TransactionSortValue = "date",
    session_path: str | None = None,
) -> Any:
    return to_jsonable(
        api_list_transactions(
            require_session(session_path),
            filters=transaction_filter(filters),
            limit=limit,
            offset=offset,
            sort=transaction_sort(sort),
        )
    )


def get_transaction(
    transaction_id: str,
    *,
    redirect_posted: bool = True,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(
        api_get_transaction(
            require_session(session_path),
            transaction_id,
            redirect_posted=redirect_posted,
        )
    )


def create_transaction(
    *,
    account_id: str,
    amount: float,
    date: str,
    merchant_name: str,
    category_id: str,
    notes: str | None = None,
    owner_user_id: str | None = None,
    should_update_balance: bool | None = None,
    goal_id: str | None = None,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(
        api_create_transaction(
            require_session(session_path),
            account_id=account_id,
            amount=amount,
            date=date,
            merchant_name=merchant_name,
            category_id=category_id,
            notes=notes,
            owner_user_id=owner_user_id,
            should_update_balance=should_update_balance,
            goal_id=goal_id,
        )
    )


def update_transaction(
    transaction_id: str,
    *,
    date: str | None = None,
    amount: float | None = None,
    account_id: str | None = None,
    merchant_name: str | None = None,
    category_id: str | None = None,
    notes: str | None = None,
    hide_from_reports: bool | None = None,
    review_status: TransactionReviewStatusValue | None = None,
    needs_review_by_user_id: str | None = None,
    owner_user_id: str | None = None,
    tag_ids: list[str] | None = None,
    goal_id: str | None = None,
    clear_goal: bool = False,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(
        api_update_transaction(
            require_session(session_path),
            transaction_id,
            date=date,
            amount=amount,
            account_id=account_id,
            merchant_name=merchant_name,
            category_id=category_id,
            notes=notes,
            hide_from_reports=hide_from_reports,
            review_status=review_status_(review_status),
            needs_review_by_user_id=needs_review_by_user_id,
            owner_user_id=owner_user_id,
            tag_ids=tag_ids,
            goal_id=goal_id,
            clear_goal=clear_goal,
        )
    )


def review_status_(value: str | None):
    return review_status(value)


def delete_transaction(
    transaction_id: str,
    *,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(api_delete_transaction(require_session(session_path), transaction_id))


def get_transaction_splits(
    transaction_id: str,
    *,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(api_get_transaction_splits(require_session(session_path), transaction_id))


def update_transaction_splits(
    transaction_id: str,
    splits: list[TransactionSplitDraftInput],
    *,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(
        api_update_transaction_splits(
            require_session(session_path),
            transaction_id,
            transaction_split_drafts(splits),
        )
    )


def unsplit_transaction(
    transaction_id: str,
    *,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(api_unsplit_transaction(require_session(session_path), transaction_id))


def list_transaction_attachments(
    transaction_id: str,
    *,
    redirect_posted: bool = True,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(
        api_list_transaction_attachments(
            require_session(session_path),
            transaction_id,
            redirect_posted=redirect_posted,
        )
    )


def get_transaction_attachment(
    attachment_id: str,
    *,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(api_get_transaction_attachment(require_session(session_path), attachment_id))


def upload_transaction_attachment(
    transaction_id: str,
    file_path: str,
    *,
    filename: str | None = None,
    content_type: str | None = None,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(
        api_upload_transaction_attachment(
            require_session(session_path),
            transaction_id,
            file_path,
            filename=filename,
            content_type=content_type,
        )
    )


def download_transaction_attachment(
    attachment_id: str,
    path: str | None = None,
    *,
    session_path: str | None = None,
) -> Any:
    data = api_download_transaction_attachment(
        require_session(session_path),
        attachment_id,
        path,
    )
    return {
        "attachment_id": attachment_id,
        "path": path,
        "size_bytes": len(data),
        "content_base64": to_jsonable(data),
    }


def delete_transaction_attachment(
    attachment_id: str,
    *,
    session_path: str | None = None,
) -> Any:
    return to_jsonable(
        api_delete_transaction_attachment(require_session(session_path), attachment_id)
    )


def register(mcp: MCPServer) -> None:
    register_api_tool(mcp, "transactions", "list_transactions", list_transactions)
    register_api_tool(mcp, "transactions", "get_transaction", get_transaction)
    register_api_tool(mcp, "transactions", "create_transaction", create_transaction)
    register_api_tool(mcp, "transactions", "update_transaction", update_transaction)
    register_api_tool(mcp, "transactions", "delete_transaction", delete_transaction)
    register_api_tool(
        mcp,
        "transactions",
        "get_transaction_splits",
        get_transaction_splits,
    )
    register_api_tool(
        mcp,
        "transactions",
        "update_transaction_splits",
        update_transaction_splits,
    )
    register_api_tool(mcp, "transactions", "unsplit_transaction", unsplit_transaction)
    register_api_tool(
        mcp,
        "transactions",
        "list_transaction_attachments",
        list_transaction_attachments,
    )
    register_api_tool(
        mcp,
        "transactions",
        "get_transaction_attachment",
        get_transaction_attachment,
    )
    register_api_tool(
        mcp,
        "transactions",
        "upload_transaction_attachment",
        upload_transaction_attachment,
    )
    register_api_tool(
        mcp,
        "transactions",
        "download_transaction_attachment",
        download_transaction_attachment,
    )
    register_api_tool(
        mcp,
        "transactions",
        "delete_transaction_attachment",
        delete_transaction_attachment,
    )
