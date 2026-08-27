from __future__ import annotations

import json
from collections.abc import Callable, Sequence
from typing import Any, Literal

OutputMode = Literal["summary", "full", "raw"]
SummaryFn = Callable[[Any], Any]


def shape_output(
    tool_name: str,
    value: Any,
    *,
    output_mode: OutputMode = "summary",
    fields: list[str] | None = None,
) -> Any:
    if fields is not None:
        if not fields:
            raise ValueError("fields must include at least one field when provided.")
        return project_fields(value, fields)
    if output_mode == "summary":
        return summarize(tool_name, value)
    if output_mode in {"full", "raw"}:
        return value
    raise ValueError("output_mode must be one of: summary, full, raw.")


def summarize(tool_name: str, value: Any) -> Any:
    fn = SUMMARY_FUNCTIONS.get(tool_name)
    if fn is None:
        return value
    return fn(value)


def project_fields(value: Any, fields: Sequence[str]) -> Any:
    if isinstance(value, list | tuple):
        return [project_row(item, fields) for item in value]
    return project_row(value, fields)


def project_row(value: Any, fields: Sequence[str]) -> dict[str, Any]:
    return {field: value_at_path(value, field) for field in fields}


def value_at_path(value: Any, path: str) -> Any:
    parts = [part for part in path.split(".") if part]
    return _value_at_parts(value, parts)


def _value_at_parts(value: Any, parts: Sequence[str]) -> Any:
    if not parts:
        return value
    if value is None:
        return None

    part = parts[0]
    rest = parts[1:]
    if isinstance(value, dict):
        return _value_at_parts(value.get(part), rest)
    if isinstance(value, list):
        if part.isdigit():
            index = int(part)
            if index >= len(value):
                return None
            return _value_at_parts(value[index], rest)
        return [_value_at_parts(item, parts) for item in value]
    return None


def rows(row_fn: Callable[[dict[str, Any]], dict[str, Any]]) -> SummaryFn:
    return lambda value: [row_fn(item) for item in _as_list(value)]


def nested_rows(key: str, row_fn: Callable[[dict[str, Any]], dict[str, Any]]) -> SummaryFn:
    return lambda value: [row_fn(item) for item in g(value, key, [])]


def details(detail_fn: Callable[[dict[str, Any]], dict[str, Any]]) -> SummaryFn:
    return lambda value: None if value is None else detail_fn(value)


def key_result(key: str) -> SummaryFn:
    return lambda value: {key: value}


def delete_result(id_key: str) -> SummaryFn:
    return lambda value: {"deleted": value}


def success_result(key: str) -> SummaryFn:
    return lambda value: {key: True if value is None else value}


def _as_list(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    return []


def g(value: dict[str, Any] | None, key: str, default: Any = None) -> Any:
    if not isinstance(value, dict):
        return default
    return value.get(key, default)


def path(value: dict[str, Any] | None, *parts: str) -> Any:
    current: Any = value
    for part in parts:
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


def enum_value(value: Any) -> Any:
    if isinstance(value, dict):
        return value.get("value") or value.get("name") or value.get("display_name")
    return value


def display_name(value: Any) -> Any:
    if isinstance(value, dict):
        return value.get("display_name") or value.get("name")
    return value


def name(value: Any) -> Any:
    if isinstance(value, dict):
        return value.get("name")
    return value


def format_money(value: Any) -> str:
    if value is None:
        return ""
    try:
        amount = float(value)
    except (TypeError, ValueError):
        return str(value)
    return f"${amount:,.2f}"


def format_bool(value: Any) -> str:
    if value is None:
        return ""
    return "yes" if bool(value) else "no"


def format_bytes(value: Any) -> str:
    if value is None:
        return ""
    try:
        size = int(value)
    except (TypeError, ValueError):
        return str(value)
    units = ["B", "KB", "MB", "GB"]
    amount = float(size)
    for unit in units:
        if amount < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{int(amount)} {unit}"
            return f"{amount:.1f} {unit}"
        amount /= 1024
    return str(size)


def format_percent(value: Any) -> str:
    if value is None:
        return ""
    try:
        return f"{float(value):.1%}"
    except (TypeError, ValueError):
        return str(value)


def format_json(value: Any) -> str:
    return json.dumps(value, separators=(",", ":"))


def account_row(account: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": g(account, "id"),
        "name": g(account, "display_name"),
        "type": display_name(g(account, "type")),
        "subtype": display_name(g(account, "subtype")),
        "institution": name(g(account, "institution")),
        "balance": format_money(g(account, "balance")),
        "net_worth": format_bool(g(account, "include_in_net_worth")),
        "hidden": format_bool(g(account, "is_hidden")),
    }


def account_details(account: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": g(account, "id"),
        "name": g(account, "display_name"),
        "balance": format_money(g(account, "balance")),
        "current_balance": format_money(g(account, "current_balance")),
        "type": display_name(g(account, "type")),
        "subtype": display_name(g(account, "subtype")),
        "institution": name(g(account, "institution")),
        "owner": display_name(g(account, "owner")),
        "asset": format_bool(g(account, "is_asset")),
        "manual": format_bool(g(account, "is_manual")),
        "hidden": format_bool(g(account, "is_hidden")),
        "sync_disabled": format_bool(g(account, "sync_disabled")),
        "include_in_net_worth": format_bool(g(account, "include_in_net_worth")),
        "last_updated_at": g(account, "last_updated_at"),
    }


def tag_details(tag: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": g(tag, "id"),
        "name": g(tag, "name"),
        "color": g(tag, "color"),
        "order": g(tag, "order"),
        "transactions": g(tag, "transaction_count"),
    }


def category_row(category: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": g(category, "id"),
        "name": g(category, "name"),
        "group": name(g(category, "group")),
        "type": enum_value(g(category, "type")),
        "order": g(category, "order"),
        "disabled": format_bool(g(category, "is_disabled")),
        "budget": g(category, "budget_variability"),
    }


def category_details(category: dict[str, Any]) -> dict[str, Any]:
    return {
        **category_row(category),
        "icon": g(category, "icon"),
        "group_id": path(category, "group", "id"),
        "system": format_bool(g(category, "is_system")),
        "protected": format_bool(g(category, "is_protected")),
        "exclude_from_budget": format_bool(g(category, "exclude_from_budget")),
        "budget_variability": g(category, "budget_variability"),
    }


def category_group_row(group: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": g(group, "id"),
        "name": g(group, "name"),
        "type": enum_value(g(group, "type")),
        "order": g(group, "order"),
        "budgeting": format_bool(g(group, "group_level_budgeting_enabled")),
    }


def category_group_details(group: dict[str, Any]) -> dict[str, Any]:
    return {
        **category_group_row(group),
        "color": g(group, "color"),
        "group_level_budgeting_enabled": format_bool(g(group, "group_level_budgeting_enabled")),
        "budget_variability": g(group, "budget_variability"),
    }


def transaction_row(transaction: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": g(transaction, "id"),
        "date": g(transaction, "date"),
        "merchant": g(transaction, "merchant_name"),
        "amount": format_money(g(transaction, "amount")),
        "account": display_name(g(transaction, "account")),
        "category": name(g(transaction, "category")),
        "review": enum_value(g(transaction, "review_status")),
        "pending": format_bool(g(transaction, "pending")),
    }


def transaction_details(transaction: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": g(transaction, "id"),
        "date": g(transaction, "date"),
        "amount": format_money(g(transaction, "amount")),
        "merchant": g(transaction, "merchant_name"),
        "account": display_name(g(transaction, "account")),
        "category": name(g(transaction, "category")),
        "tags": ", ".join(name(tag) or "" for tag in g(transaction, "tags", [])),
        "notes": g(transaction, "notes"),
        "review_status": enum_value(g(transaction, "review_status")),
        "needs_review": format_bool(g(transaction, "needs_review")),
        "pending": format_bool(g(transaction, "pending")),
        "hide_from_reports": format_bool(g(transaction, "hide_from_reports")),
        "split": format_bool(g(transaction, "is_split")),
        "has_splits": format_bool(g(transaction, "has_splits")),
        "recurring": format_bool(g(transaction, "is_recurring")),
        "goal": name(g(transaction, "goal")),
        "attachments": g(transaction, "attachment_count"),
        "owner": display_name(g(transaction, "owner")),
        "updated_at": g(transaction, "updated_at"),
    }


def attachment_row(attachment: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": g(attachment, "id"),
        "filename": g(attachment, "filename"),
        "extension": g(attachment, "extension"),
        "size": format_bytes(g(attachment, "size_bytes")),
        "public_id": g(attachment, "public_id"),
    }


def attachment_details(attachment: dict[str, Any]) -> dict[str, Any]:
    return {**attachment_row(attachment), "url": g(attachment, "original_asset_url")}


def receipt_row(receipt: dict[str, Any]) -> dict[str, Any]:
    order = g(receipt, "order")
    return {
        "id": g(receipt, "id"),
        "status": enum_value(g(receipt, "status")),
        "source": enum_value(g(receipt, "source")),
        "merchant": g(order, "merchant_name"),
        "date": g(order, "date"),
        "total": format_money(g(order, "grand_total")),
        "matched": format_bool(g(receipt, "is_matched")),
        "transaction_id": g(receipt, "transaction_id"),
        "attachment": path(receipt, "attachment", "filename"),
    }


def receipt_details(receipt: dict[str, Any]) -> dict[str, Any]:
    order = g(receipt, "order")
    attachment = g(receipt, "attachment")
    return {
        "id": g(receipt, "id"),
        "status": enum_value(g(receipt, "status")),
        "source": enum_value(g(receipt, "source")),
        "merchant": g(order, "merchant_name"),
        "date": g(order, "date"),
        "total_before_tax": format_money(g(order, "total_before_tax")),
        "tax": format_money(g(order, "tax")),
        "tip": format_money(g(order, "tip")),
        "grand_total": format_money(g(order, "grand_total")),
        "matched": format_bool(g(receipt, "is_matched")),
        "transaction_id": g(receipt, "transaction_id"),
        "attachment": g(attachment, "filename"),
        "attachment_size": format_bytes(g(attachment, "size_bytes")),
        "created_at": g(receipt, "created_at"),
        "updated_at": g(receipt, "updated_at"),
    }


def line_item_row(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": g(item, "id"),
        "title": g(item, "title"),
        "quantity": g(item, "quantity"),
        "price": format_money(g(item, "price")),
        "total": format_money(g(item, "total")),
        "category": name(g(item, "category")),
    }


def merchant_details(merchant: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": g(merchant, "id"),
        "name": g(merchant, "name"),
        "transactions": g(merchant, "transaction_count"),
        "rules": g(merchant, "rule_count"),
        "deletable": format_bool(g(merchant, "can_be_deleted")),
        "recurring_id": g(merchant, "recurring_id"),
        "created_at": g(merchant, "created_at"),
        "logo_url": g(merchant, "logo_url"),
    }


def merchant_row(merchant: dict[str, Any]) -> dict[str, Any]:
    row = merchant_details(merchant)
    row.pop("created_at", None)
    row.pop("logo_url", None)
    return row


def household_details(household: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": g(household, "id"),
        "name": g(household, "name"),
        "address": g(household, "address"),
        "city": g(household, "city"),
        "state": g(household, "state"),
        "zip_code": g(household, "zip_code"),
        "country": g(household, "country"),
    }


def member_row(member: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": g(member, "id"),
        "display_name": g(member, "display_name") or g(member, "name"),
        "email": g(member, "email"),
        "role": enum_value(g(member, "role")),
        "mfa": format_bool(g(member, "has_mfa_on")),
    }


def member_details(member: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": g(member, "id"),
        "name": g(member, "name"),
        "display_name": g(member, "display_name"),
        "email": g(member, "email"),
        "role": enum_value(g(member, "role")),
        "mfa": format_bool(g(member, "has_mfa_on")),
        "profile_picture_url": g(member, "profile_picture_url"),
    }


def user_details(user: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": g(user, "id"),
        "email": g(user, "email"),
        "name": g(user, "name"),
        "display_name": g(user, "display_name"),
        "timezone": g(user, "timezone"),
        "role": enum_value(g(user, "household_role")),
        "password": format_bool(g(user, "has_password")),
        "mfa": format_bool(g(user, "has_mfa_on")),
        "created_at": g(user, "created_at"),
        "pending_email_update": g(user, "pending_email_update"),
    }


def preferences_details(preferences: dict[str, Any]) -> dict[str, Any]:
    return {
        "new_transactions_need_review": format_bool(g(preferences, "new_transactions_need_review")),
        "uncategorized_transactions_need_review": format_bool(
            g(preferences, "uncategorized_transactions_need_review")
        ),
        "pending_transactions_can_be_edited": format_bool(
            g(preferences, "pending_transactions_can_be_edited")
        ),
        "budget_apply_to_future_months_default": format_bool(
            g(preferences, "budget_apply_to_future_months_default")
        ),
        "hidden_transactions_beta_enabled": format_bool(
            g(preferences, "hidden_transactions_beta_enabled")
        ),
        "exclude_business_from_budget": format_bool(g(preferences, "exclude_business_from_budget")),
        "budget_system": g(preferences, "budget_system"),
    }


def cashflow_summary(summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "start_date": g(summary, "start_date"),
        "end_date": g(summary, "end_date"),
        "income": format_money(g(summary, "income")),
        "expenses": format_money(g(summary, "expenses")),
        "savings": format_money(g(summary, "savings")),
        "savings_rate": format_percent(g(summary, "savings_rate")),
    }


def cashflow_breakdown_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": g(row, "id"),
        "name": g(row, "name"),
        "amount": format_money(g(row, "amount")),
        "percent": format_percent(g(row, "percent")),
        "transactions": g(row, "transaction_count"),
    }


def cashflow_trend_row(point: dict[str, Any]) -> dict[str, Any]:
    return {
        "label": g(point, "label"),
        "start_date": g(point, "start_date"),
        "end_date": g(point, "end_date"),
        "income": format_money(g(point, "income")),
        "expenses": format_money(g(point, "expenses")),
        "savings": format_money(g(point, "savings")),
        "savings_rate": format_percent(g(point, "savings_rate")),
    }


def goal_row(goal: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": g(goal, "id"),
        "name": g(goal, "name"),
        "type": enum_value(g(goal, "type")),
        "status": enum_value(g(goal, "status")),
        "current": format_money(g(goal, "current_balance")),
        "target": format_money(g(goal, "target_amount")),
        "target_date": g(goal, "target_date"),
        "priority": g(goal, "priority"),
    }


def goal_details(goal: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": g(goal, "id"),
        "name": g(goal, "name"),
        "type": enum_value(g(goal, "type")),
        "status": enum_value(g(goal, "status")),
        "progress": format_percent(g(goal, "progress")),
        "current_balance": format_money(g(goal, "current_balance")),
        "target_amount": format_money(g(goal, "target_amount")),
        "target_date": g(goal, "target_date"),
        "planned_monthly_contribution": format_money(g(goal, "planned_monthly_contribution")),
        "current_month_planned_contribution": format_money(
            g(goal, "current_month_planned_contribution_amount")
        ),
        "spending_total": format_money(g(goal, "spending_total")),
        "net_contribution": format_money(g(goal, "net_contribution")),
        "estimated_months_until_completion": g(goal, "estimated_months_until_completion"),
        "forecasted_completion_date": g(goal, "forecasted_completion_date"),
        "sinking_fund": format_bool(g(goal, "is_sinking_fund")),
        "priority": g(goal, "priority"),
        "created_at": g(goal, "created_at"),
        "archived_at": g(goal, "archived_at"),
        "completed_at": g(goal, "completed_at"),
    }


def goal_with_links(goal: dict[str, Any]) -> dict[str, Any]:
    return {
        "goal": goal_details(goal),
        "linked_accounts": [goal_link_row(link) for link in g(goal, "account_balance_links", [])],
    }


def goal_link_row(link: dict[str, Any]) -> dict[str, Any]:
    return {
        "account_id": path(link, "account", "id") or g(link, "id"),
        "account": path(link, "account", "display_name") or "",
        "amount": format_money(g(link, "amount")),
        "current": format_money(g(link, "current_amount")),
        "entire_balance": format_bool(g(link, "use_entire_balance")),
    }


def goal_event_row(event: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": g(event, "id"),
        "date": g(event, "date"),
        "type": enum_value(g(event, "type")),
        "amount": format_money(g(event, "amount")),
        "account": path(event, "account", "display_name") or "",
        "budget": format_bool(g(event, "include_in_budget")),
        "notes": g(event, "notes"),
    }


def goal_budget_row(amount: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": g(amount, "id"),
        "month": g(amount, "month"),
        "planned": format_money(g(amount, "planned_amount")),
        "actual": format_money(g(amount, "actual_amount")),
        "remaining": format_money(g(amount, "remaining_amount")),
        "total_planned": format_money(g(amount, "total_planned_amount")),
    }


def recurring_stream_row(stream: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": g(stream, "id"),
        "name": g(stream, "name"),
        "amount": format_money(g(stream, "amount")),
        "next_date": g(stream, "next_date"),
        "next_amount": format_money(g(stream, "next_amount")),
        "frequency": g(stream, "frequency"),
        "type": enum_value(g(stream, "recurring_type")),
        "status": enum_value(g(stream, "status")),
        "account": path(stream, "account", "display_name") or "",
        "category": path(stream, "category", "name") or "",
    }


def recurring_stream_details(stream: dict[str, Any]) -> dict[str, Any]:
    return {
        **recurring_stream_row(stream),
        "base_date": g(stream, "base_date"),
        "day_of_month": g(stream, "day_of_month"),
        "active": format_bool(g(stream, "is_active")),
        "approximate": format_bool(g(stream, "is_approximate")),
        "merchant": path(stream, "merchant", "name") or "",
        "merchant_id": path(stream, "merchant", "id") or "",
        "account_id": path(stream, "account", "id") or "",
        "category_id": path(stream, "category", "id") or "",
        "liability_account_id": g(stream, "liability_account_id"),
    }


def recurring_occurrence_row(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "recurring_id": g(item, "recurring_id"),
        "date": g(item, "date"),
        "name": g(item, "name"),
        "amount": format_money(g(item, "amount")),
        "completed": format_bool(g(item, "is_completed")),
        "late": format_bool(g(item, "is_late")),
        "account": path(item, "account", "display_name") or "",
        "category": path(item, "category", "name") or "",
        "transaction_id": g(item, "transaction_id"),
    }


def recurring_summary_rows(summary: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        recurring_summary_row("expense", g(summary, "expense")),
        recurring_summary_row("income", g(summary, "income")),
        recurring_summary_row("credit_card", g(summary, "credit_card")),
    ]


def recurring_summary_row(name_: str, bucket: dict[str, Any] | None) -> dict[str, Any]:
    return {
        "type": name_,
        "completed": format_money(g(bucket, "completed")),
        "remaining": format_money(g(bucket, "remaining")),
        "total": format_money(g(bucket, "total")),
        "count": g(bucket, "count"),
        "pending_amounts": g(bucket, "pending_amount_count"),
    }


def investment_account_row(account: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": g(account, "id"),
        "name": g(account, "display_name"),
        "subtype": g(account, "subtype_display"),
        "taxable": format_bool(g(account, "is_taxable")),
        "net_worth": format_bool(g(account, "include_in_net_worth")),
        "sync_disabled": format_bool(g(account, "sync_disabled")),
    }


def holding_row(holding: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": g(holding, "id"),
        "ticker": g(holding, "ticker"),
        "name": g(holding, "name"),
        "account": path(holding, "account", "display_name") or "",
        "quantity": g(holding, "quantity"),
        "value": format_money(g(holding, "value")),
        "cost_basis": format_money(g(holding, "cost_basis")),
        "manual": format_bool(g(holding, "is_manual")),
    }


def holding_details(holding: dict[str, Any]) -> dict[str, Any]:
    return {
        **holding_row(holding),
        "aggregate_id": g(holding, "aggregate_id"),
        "type": g(holding, "type_display") or g(holding, "type"),
        "account_id": path(holding, "account", "id") or "",
        "security": path(holding, "security", "name") or "",
        "security_id": path(holding, "security", "id") or "",
        "user_cost_basis": format_money(g(holding, "user_cost_basis")),
        "closing_price": format_money(g(holding, "closing_price")),
        "last_synced_at": g(holding, "last_synced_at"),
        "tax_lots": [tax_lot_row(lot) for lot in g(holding, "tax_lots", [])],
    }


def security_row(security: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": g(security, "id"),
        "ticker": g(security, "ticker"),
        "name": g(security, "name"),
        "type": g(security, "type_display") or g(security, "type"),
        "price": format_money(g(security, "current_price") or g(security, "closing_price")),
        "one_day": format_percent(g(security, "one_day_change_percent")),
    }


def security_details(security: dict[str, Any]) -> dict[str, Any]:
    return {
        **security_row(security),
        "current_price": format_money(g(security, "current_price")),
        "current_price_updated_at": g(security, "current_price_updated_at"),
        "closing_price": format_money(g(security, "closing_price")),
        "closing_price_updated_at": g(security, "closing_price_updated_at"),
        "one_day_change": format_money(g(security, "one_day_change_dollars")),
        "one_day_change_percent": format_percent(g(security, "one_day_change_percent")),
        "category_group": g(security, "category_group"),
        "broad_asset_class": g(security, "broad_asset_class"),
        "morningstar_category": g(security, "morningstar_category"),
    }


def portfolio_summary(portfolio: dict[str, Any]) -> dict[str, Any]:
    summary = g(portfolio, "summary")
    return {
        "summary": {
            "total_value": format_money(g(summary, "total_value")),
            "total_change": format_money(g(summary, "total_change_dollars")),
            "total_change_percent": format_percent(g(summary, "total_change_percent")),
            "one_day_change": format_money(g(summary, "one_day_change_dollars")),
            "one_day_change_percent": format_percent(g(summary, "one_day_change_percent")),
            "holdings": g(summary, "holdings_count"),
        },
        "allocations": [allocation_row(item) for item in g(portfolio, "allocations", [])],
        "holdings": [holding_row(item) for item in g(portfolio, "holdings", [])],
    }


def allocation_row(allocation: dict[str, Any]) -> dict[str, Any]:
    return {
        "label": g(allocation, "label"),
        "value": format_money(g(allocation, "value")),
        "percent": format_percent(g(allocation, "percent_of_portfolio")),
    }


def performance_row(point: dict[str, Any]) -> dict[str, Any]:
    return {
        "date": g(point, "date"),
        "value": format_money(g(point, "value")),
        "return": format_percent(g(point, "return_percent")),
    }


def performance_summary(performance: dict[str, Any]) -> dict[str, Any]:
    return {"points": [performance_row(item) for item in g(performance, "points", [])]}


def tax_lot_row(lot: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": g(lot, "id"),
        "acquisition_date": g(lot, "acquisition_date"),
        "quantity": g(lot, "acquisition_quantity"),
        "cost_basis_per_unit": format_money(g(lot, "cost_basis_per_unit")),
    }


def report_data_summary(result: dict[str, Any]) -> dict[str, Any]:
    summary = g(result, "summary")
    return {
        "summary": {
            "total": format_money(g(summary, "total")),
            "income": format_money(g(summary, "income")),
            "expenses": format_money(g(summary, "expenses")),
            "savings": format_money(g(summary, "savings")),
            "count": g(summary, "count"),
            "average": format_money(g(summary, "average")),
            "first_date": g(summary, "first_date"),
            "last_date": g(summary, "last_date"),
        },
        "rows": [report_row(item) for item in g(result, "rows", [])],
    }


def report_row(row: dict[str, Any]) -> dict[str, Any]:
    summary = g(row, "summary")
    return {
        "group": path(row, "group", "label"),
        "total": format_money(g(summary, "total")),
        "income": format_money(g(summary, "income")),
        "expenses": format_money(g(summary, "expenses")),
        "count": g(summary, "count"),
        "average": format_money(g(summary, "average")),
    }


def saved_report_details(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": g(report, "id"),
        "name": g(report, "name"),
        "group_by": [enum_value(item) for item in g(report, "group_by", [])],
        "timeframe": enum_value(g(report, "timeframe")),
    }


def budget_details(budget: dict[str, Any]) -> dict[str, Any]:
    return {
        "summary": {
            "start_month": g(budget, "start_month"),
            "end_month": g(budget, "end_month"),
            "budget_system": enum_value(g(budget, "budget_system")),
            "has_budget": format_bool(path(budget, "status", "has_budget")),
            "has_transactions": format_bool(path(budget, "status", "has_transactions")),
            "groups": len(g(budget, "groups", [])),
            "categories": len(g(budget, "categories", [])),
        },
        "totals": [budget_total_row(item) for item in g(budget, "totals_by_month", [])],
        "groups": [budget_group_row(item) for item in g(budget, "groups", [])],
        "categories": [budget_category_row(item) for item in g(budget, "categories", [])],
    }


def budget_settings_details(settings: dict[str, Any]) -> dict[str, Any]:
    return {
        "budget_system": enum_value(g(settings, "budget_system")),
        "apply_to_future_months_default": format_bool(
            g(settings, "apply_to_future_months_default")
        ),
        "has_budget": format_bool(path(settings, "status", "has_budget")),
        "has_transactions": format_bool(path(settings, "status", "has_transactions")),
        **rollover_details(g(settings, "flex_rollover")),
    }


def budget_month_row(budget: dict[str, Any]) -> dict[str, Any]:
    totals = g(budget, "totals_by_month", [])
    return budget_total_row(totals[0]) if totals else {"month": g(budget, "start_month")}


def budget_total_row(total: dict[str, Any]) -> dict[str, Any]:
    return {
        "month": g(total, "month"),
        "income_planned": format_money(path(total, "income", "planned_amount")),
        "income_actual": format_money(path(total, "income", "actual_amount")),
        "expenses_planned": format_money(path(total, "expenses", "planned_amount")),
        "expenses_actual": format_money(path(total, "expenses", "actual_amount")),
        "expenses_remaining": format_money(path(total, "expenses", "remaining_amount")),
    }


def budget_group_row(row: dict[str, Any]) -> dict[str, Any]:
    amount = g(row, "amount")
    group = g(row, "group")
    return {
        "id": g(group, "id"),
        "name": g(group, "name"),
        "planned": format_money(g(amount, "planned_amount")),
        "actual": format_money(g(amount, "actual_amount")),
        "remaining": format_money(g(amount, "remaining_amount")),
        "variability": enum_value(g(group, "budget_variability")),
        "rollover": format_bool(g(group, "rollover_period") is not None),
    }


def budget_category_row(row: dict[str, Any]) -> dict[str, Any]:
    amount = g(row, "amount")
    category = g(row, "category")
    return {
        "id": g(category, "id"),
        "name": g(category, "name"),
        "group_id": g(category, "group_id"),
        "planned": format_money(g(amount, "planned_amount")),
        "actual": format_money(g(amount, "actual_amount")),
        "remaining": format_money(g(amount, "remaining_amount")),
        "variability": enum_value(g(category, "budget_variability")),
        "rollover": format_bool(g(category, "rollover_period") is not None),
    }


def budget_category_details(row: dict[str, Any] | None) -> dict[str, Any] | None:
    if row is None:
        return None
    amount = g(row, "amount")
    category = g(row, "category", row)
    return {
        "id": g(category, "id"),
        "name": g(category, "name"),
        "group_id": g(category, "group_id"),
        "type": enum_value(g(category, "type")),
        "budget_variability": enum_value(g(category, "budget_variability")),
        "exclude_from_budget": format_bool(g(category, "exclude_from_budget")),
        "planned": format_money(g(amount, "planned_amount")),
        "actual": format_money(g(amount, "actual_amount")),
        "remaining": format_money(g(amount, "remaining_amount")),
        **rollover_details(g(category, "rollover_period")),
    }


def budget_group_details(row: dict[str, Any] | None) -> dict[str, Any] | None:
    if row is None:
        return None
    amount = g(row, "amount")
    group = g(row, "group", row)
    return {
        "id": g(group, "id"),
        "name": g(group, "name"),
        "type": enum_value(g(group, "type")),
        "budget_variability": enum_value(g(group, "budget_variability")),
        "group_level_budgeting": format_bool(g(group, "group_level_budgeting_enabled")),
        "planned": format_money(g(amount, "planned_amount")),
        "actual": format_money(g(amount, "actual_amount")),
        "remaining": format_money(g(amount, "remaining_amount")),
        **rollover_details(g(group, "rollover_period")),
    }


def budget_flex_details(row: dict[str, Any]) -> dict[str, Any]:
    amount = g(row, "amount")
    return {
        "budget_variability": enum_value(g(row, "budget_variability")),
        "planned": format_money(g(amount, "planned_amount")),
        "actual": format_money(g(amount, "actual_amount")),
        "remaining": format_money(g(amount, "remaining_amount")),
        "rollover_type": g(amount, "rollover_type"),
        "rollover_target": format_money(g(amount, "rollover_target_amount")),
    }


def rollover_details(period: dict[str, Any] | None) -> dict[str, Any]:
    return {
        "rollover_id": g(period, "id"),
        "rollover_start_month": g(period, "start_month"),
        "rollover_end_month": g(period, "end_month"),
        "rollover_starting_balance": format_money(g(period, "starting_balance")),
        "rollover_target_amount": format_money(g(period, "target_amount")),
        "rollover_frequency": g(period, "frequency"),
    }


def category_catalog(catalog: dict[str, Any]) -> dict[str, Any]:
    return {
        "groups": [category_group_row(item) for item in g(catalog, "groups", [])],
        "categories": [category_row(item) for item in g(catalog, "categories", [])],
    }


def receipt_with_items(receipt: dict[str, Any]) -> dict[str, Any]:
    return {
        "receipt": receipt_details(receipt),
        "line_items": [line_item_row(item) for item in path(receipt, "order", "line_items") or []],
    }


SUMMARY_FUNCTIONS: dict[str, SummaryFn] = {
    "auth_create_session": lambda session: session,
    "auth_save_session": success_result("saved"),
    "auth_load_session": lambda session: session,
    "accounts_list_accounts": rows(account_row),
    "accounts_get_account": details(account_details),
    "accounts_get_net_worth_performance": rows(
        lambda point: {
            "date": g(point, "date"),
            "net_worth": format_money(g(point, "net_worth")),
            "assets": format_money(g(point, "assets_balance")),
            "liabilities": format_money(g(point, "liabilities_balance")),
        }
    ),
    "accounts_get_net_worth_breakdown": rows(
        lambda point: {
            "date": g(point, "date"),
            "account_type": g(point, "account_type"),
            "account_group": g(point, "account_group"),
            "balance": format_money(g(point, "balance")),
        }
    ),
    "accounts_get_historical_balances": rows(
        lambda balance: {
            "account_id": g(balance, "account_id"),
            "account_type": g(balance, "account_type"),
            "balance": format_money(g(balance, "balance")),
            "net_worth": format_bool(g(balance, "include_in_net_worth")),
        }
    ),
    "accounts_get_account_history": rows(
        lambda point: {"date": g(point, "date"), "balance": format_money(g(point, "balance"))}
    ),
    "accounts_create_manual_account": key_result("account_id"),
    "accounts_update_account": details(account_details),
    "accounts_delete_account": delete_result("account_id"),
    "tags_list_tags": rows(tag_details),
    "tags_get_tag": details(tag_details),
    "tags_create_tag": details(tag_details),
    "tags_update_tag": details(tag_details),
    "tags_reorder_tag": rows(tag_details),
    "tags_delete_tag": delete_result("tag_id"),
    "categories_list_categories": rows(category_row),
    "categories_list_category_groups": rows(category_group_row),
    "categories_get_category_catalog": details(category_catalog),
    "categories_get_category_group": details(category_group_details),
    "categories_get_category": details(category_details),
    "categories_create_category": details(category_details),
    "categories_update_category": details(category_details),
    "categories_remove_category": delete_result("category_id"),
    "categories_reactivate_category": details(category_details),
    "categories_reorder_category": rows(category_row),
    "categories_create_category_group": details(category_group_details),
    "categories_update_category_group": details(category_group_details),
    "categories_delete_category_group": delete_result("category_group_id"),
    "categories_reorder_category_group": rows(category_group_row),
    "cashflow_get_cashflow_summary": details(cashflow_summary),
    "cashflow_get_cashflow_trends": rows(cashflow_trend_row),
    "cashflow_get_cashflow_breakdown": nested_rows("rows", cashflow_breakdown_row),
    "merchants_list_merchants": rows(merchant_row),
    "merchants_get_merchant": details(merchant_details),
    "merchants_update_merchant": details(merchant_details),
    "merchants_delete_merchant": delete_result("merchant_id"),
    "household_get_current_user": details(user_details),
    "household_get_household": details(household_details),
    "household_list_household_members": rows(member_row),
    "household_get_household_member": details(member_details),
    "household_get_household_preferences": details(preferences_details),
    "household_update_current_user": details(user_details),
    "household_update_household_preferences": details(preferences_details),
    "recurring_list_recurring_streams": rows(recurring_stream_row),
    "recurring_get_recurring_stream": details(recurring_stream_details),
    "recurring_list_recurring_occurrences": rows(recurring_occurrence_row),
    "recurring_get_recurring_summary": details(recurring_summary_rows),
    "recurring_create_recurring_stream": details(recurring_stream_details),
    "recurring_update_recurring_stream": details(recurring_stream_details),
    "recurring_remove_recurring_stream": delete_result("recurring_id"),
    "investments_list_investment_accounts": rows(investment_account_row),
    "investments_list_holdings": rows(holding_row),
    "investments_get_holding": details(holding_details),
    "investments_get_holding_performance": details(performance_summary),
    "investments_get_portfolio": details(portfolio_summary),
    "investments_get_security": details(security_details),
    "investments_search_securities": rows(security_row),
    "investments_create_manual_holding": details(holding_details),
    "investments_update_manual_holding": details(holding_details),
    "investments_delete_manual_holding": delete_result("holding_id"),
    "reports_get_report_data": details(report_data_summary),
    "reports_list_saved_reports": rows(saved_report_details),
    "reports_get_saved_report": details(saved_report_details),
    "reports_create_saved_report": details(saved_report_details),
    "reports_update_saved_report": details(saved_report_details),
    "reports_delete_saved_report": delete_result("report_id"),
    "goals_list_goals": rows(goal_row),
    "goals_get_goal": details(goal_with_links),
    "goals_create_goal": details(goal_details),
    "goals_update_goal": details(goal_details),
    "goals_delete_goal": delete_result("goal_id"),
    "goals_archive_goal": details(goal_details),
    "goals_restore_goal": details(goal_details),
    "goals_update_goal_priorities": rows(goal_row),
    "goals_link_goal_account_balance": details(goal_with_links),
    "goals_unlink_goal_account": details(goal_with_links),
    "goals_list_goal_events": rows(goal_event_row),
    "goals_contribute_to_goal": details(goal_event_row),
    "goals_withdraw_from_goal": details(goal_event_row),
    "goals_update_goal_event": details(goal_event_row),
    "goals_delete_goal_event": delete_result("event_id"),
    "goals_get_goal_budget_amounts": rows(goal_budget_row),
    "goals_set_goal_budget_amount": details(goal_budget_row),
    "budget_get_budget": details(budget_details),
    "budget_list_budget_months": rows(budget_month_row),
    "budget_get_budget_settings": details(budget_settings_details),
    "budget_get_budget_category": details(budget_category_details),
    "budget_get_flex_rollover_settings": details(
        lambda settings: {
            "budget_system": enum_value(g(settings, "budget_system")),
            **rollover_details(g(settings, "rollover_period")),
        }
    ),
    "budget_set_budget_amount": details(budget_category_details),
    "budget_set_budget_group_amount": details(budget_group_details),
    "budget_set_flex_budget_amount": details(budget_flex_details),
    "budget_set_budget_category_variability": details(budget_category_details),
    "budget_set_budget_group_variability": details(budget_group_details),
    "budget_set_budget_category_rollover": details(budget_category_details),
    "budget_set_budget_group_rollover": details(budget_group_details),
    "budget_set_flex_rollover_settings": details(
        lambda settings: {
            "budget_system": enum_value(g(settings, "budget_system")),
            **rollover_details(g(settings, "rollover_period")),
        }
    ),
    "budget_reset_budget_rollover": details(budget_details),
    "budget_create_budget": details(budget_details),
    "budget_reset_budget": details(budget_details),
    "budget_clear_budget": details(budget_details),
    "transactions_list_transactions": nested_rows("transactions", transaction_row),
    "transactions_get_transaction": details(transaction_details),
    "transactions_create_transaction": details(transaction_details),
    "transactions_update_transaction": details(transaction_details),
    "transactions_delete_transaction": delete_result("transaction_id"),
    "transactions_get_transaction_splits": details(
        lambda details_: {"splits": [transaction_row(item) for item in g(details_, "splits", [])]}
    ),
    "transactions_update_transaction_splits": details(
        lambda details_: {"splits": [transaction_row(item) for item in g(details_, "splits", [])]}
    ),
    "transactions_unsplit_transaction": details(
        lambda details_: {"splits": [transaction_row(item) for item in g(details_, "splits", [])]}
    ),
    "transactions_list_transaction_attachments": rows(attachment_row),
    "transactions_get_transaction_attachment": details(attachment_details),
    "transactions_upload_transaction_attachment": details(attachment_details),
    "transactions_download_transaction_attachment": details(
        lambda item: {
            "attachment_id": g(item, "attachment_id"),
            "path": g(item, "path"),
            "size": format_bytes(g(item, "size_bytes")),
        }
    ),
    "transactions_delete_transaction_attachment": delete_result("attachment_id"),
    "receipts_list_receipts": nested_rows("receipts", receipt_row),
    "receipts_get_receipt": details(receipt_with_items),
    "receipts_upload_receipt": details(receipt_with_items),
    "receipts_delete_receipt": delete_result("receipt_id"),
    "receipts_match_receipt": details(receipt_with_items),
    "receipts_unmatch_receipt": details(receipt_with_items),
    "receipts_update_receipt": details(receipt_with_items),
    "receipts_get_receipt_settings": details(
        lambda settings: {
            "auto_categorize": format_bool(g(settings, "auto_categorize")),
            "update_transaction_notes": format_bool(g(settings, "update_transaction_notes")),
        }
    ),
    "receipts_update_receipt_settings": details(
        lambda settings: {
            "auto_categorize": format_bool(g(settings, "auto_categorize")),
            "update_transaction_notes": format_bool(g(settings, "update_transaction_notes")),
        }
    ),
}
