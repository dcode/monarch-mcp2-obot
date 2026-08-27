from __future__ import annotations

from typing import Any

from monarch_api.types.cashflow import CashflowFilter
from monarch_api.types.categories import CategoryType
from monarch_api.types.receipts import (
    ReceiptFilter,
    ReceiptLineItemUpdate,
    ReceiptSource,
    ReceiptStatus,
)
from monarch_api.types.recurring import RecurringFilter
from monarch_api.types.reports import ReportGroup, ReportSort, ReportTimeframe
from monarch_api.types.transactions import (
    TransactionFilter,
    TransactionReviewStatus,
    TransactionSort,
    TransactionSplitDraft,
    TransactionVisibility,
)
from pydantic import BaseModel


def input_dict(data):
    if isinstance(data, BaseModel):
        return data.model_dump(exclude_none=True)
    return data


def category_type(value: str | None) -> CategoryType | None:
    return CategoryType(value) if value is not None else None


def cashflow_filter(data: dict[str, Any] | None) -> CashflowFilter | None:
    data = input_dict(data)
    if data is None:
        return None
    return CashflowFilter(
        account_ids=data.get("account_ids"),
        category_ids=data.get("category_ids"),
        category_group_ids=data.get("category_group_ids"),
        merchant_ids=data.get("merchant_ids"),
        tag_ids=data.get("tag_ids"),
        include_hidden=data.get("include_hidden", False),
    )


def transaction_filter(data: dict[str, Any] | None) -> TransactionFilter | None:
    data = input_dict(data)
    if data is None:
        return None
    return TransactionFilter(
        start_date=data.get("start_date"),
        end_date=data.get("end_date"),
        search=data.get("search"),
        transaction_ids=data.get("transaction_ids"),
        account_ids=data.get("account_ids"),
        category_ids=data.get("category_ids"),
        category_group_ids=data.get("category_group_ids"),
        merchant_ids=data.get("merchant_ids"),
        tag_ids=data.get("tag_ids"),
        goal_ids=data.get("goal_ids"),
        min_absolute_amount=data.get("min_absolute_amount"),
        max_absolute_amount=data.get("max_absolute_amount"),
        category_type=category_type(data.get("category_type")),
        credits_only=data.get("credits_only"),
        debits_only=data.get("debits_only"),
        is_pending=data.get("is_pending"),
        is_recurring=data.get("is_recurring"),
        is_split=data.get("is_split"),
        is_uncategorized=data.get("is_uncategorized"),
        is_untagged=data.get("is_untagged"),
        has_notes=data.get("has_notes"),
        has_attachments=data.get("has_attachments"),
        hide_from_reports=data.get("hide_from_reports"),
        needs_review=data.get("needs_review"),
        needs_review_by_user_id=data.get("needs_review_by_user_id"),
        needs_review_unassigned=data.get("needs_review_unassigned"),
        synced_from_institution=data.get("synced_from_institution"),
        imported_from_mint=data.get("imported_from_mint"),
        transaction_visibility=enum_or_none(
            TransactionVisibility,
            data.get("transaction_visibility"),
        ),
    )


def recurring_filter(data: dict[str, Any] | None) -> RecurringFilter | None:
    data = input_dict(data)
    if data is None:
        return None
    return RecurringFilter(
        account_ids=data.get("account_ids"),
        category_ids=data.get("category_ids"),
        merchant_ids=data.get("merchant_ids"),
        recurring_ids=data.get("recurring_ids"),
        frequencies=data.get("frequencies"),
        recurring_types=data.get("recurring_types"),
        is_completed=data.get("is_completed"),
    )


def receipt_filter(data: dict[str, Any] | None) -> ReceiptFilter | None:
    data = input_dict(data)
    if data is None:
        return None
    status = data.get("status")
    source = data.get("source")
    return ReceiptFilter(
        status=ReceiptStatus(status) if status is not None else None,
        source=ReceiptSource(source) if source is not None else None,
    )


def receipt_line_items(
    values: list[dict[str, Any]] | None,
) -> list[ReceiptLineItemUpdate] | None:
    if values is None:
        return None
    values = [input_dict(item) for item in values]
    return [
        ReceiptLineItemUpdate(
            line_item_id=str(item["line_item_id"]),
            title=item.get("title"),
            category_id=item.get("category_id"),
            price=item.get("price"),
            quantity=item.get("quantity"),
        )
        for item in values
    ]


def transaction_split_drafts(
    values: list[dict[str, Any]],
) -> list[TransactionSplitDraft]:
    values = [input_dict(item) for item in values]
    return [
        TransactionSplitDraft(
            amount=item["amount"],
            id=item.get("id"),
            date=item.get("date"),
            merchant_name=item.get("merchant_name"),
            category_id=item.get("category_id"),
            notes=item.get("notes"),
            hide_from_reports=item.get("hide_from_reports"),
            review_status=enum_or_none(
                TransactionReviewStatus,
                item.get("review_status"),
            ),
            needs_review=item.get("needs_review"),
            needs_review_by_user_id=item.get("needs_review_by_user_id"),
            owner_user_id=item.get("owner_user_id"),
            tag_ids=item.get("tag_ids"),
            goal_id=item.get("goal_id"),
        )
        for item in values
    ]


def report_group(value: str | None) -> ReportGroup | None:
    return ReportGroup(value) if value is not None else None


def report_groups(value: str | list[str] | None) -> ReportGroup | list[ReportGroup] | None:
    if value is None:
        return None
    if isinstance(value, str):
        return ReportGroup(value)
    return [ReportGroup(item) for item in value]


def report_timeframe(value: str | None) -> ReportTimeframe | None:
    return ReportTimeframe(value) if value is not None else None


def report_sort(value: str | None) -> ReportSort | None:
    return ReportSort(value) if value is not None else None


def transaction_sort(value: str | None) -> TransactionSort:
    return TransactionSort(value) if value is not None else TransactionSort.DATE_DESCENDING


def review_status(value: str | None) -> TransactionReviewStatus | None:
    return enum_or_none(TransactionReviewStatus, value)


def enum_or_none(enum_type, value):
    if value is None:
        return None
    return enum_type(value)
