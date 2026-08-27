from __future__ import annotations

import json

import pytest
from monarch_api import Account

from monarch_mcp.groups import accounts
from monarch_mcp.server import create_mcp


@pytest.mark.anyio
async def test_server_registers_auth_group() -> None:
    mcp = create_mcp()

    tools = await mcp.list_tools()
    resources = await mcp.list_resources()

    assert {tool.name for tool in tools} == {
        "auth_create_session",
        "auth_save_session",
        "auth_load_session",
        "auth_login",
        "auth_status",
        "accounts_list_accounts",
        "accounts_get_account",
        "accounts_get_net_worth_performance",
        "accounts_get_net_worth_breakdown",
        "accounts_get_historical_balances",
        "accounts_get_account_history",
        "accounts_create_manual_account",
        "accounts_update_account",
        "accounts_delete_account",
        "tags_list_tags",
        "tags_get_tag",
        "tags_create_tag",
        "tags_update_tag",
        "tags_delete_tag",
        "tags_reorder_tag",
        "categories_list_categories",
        "categories_list_category_groups",
        "categories_get_category_catalog",
        "categories_get_category_group",
        "categories_get_category",
        "categories_create_category",
        "categories_update_category",
        "categories_remove_category",
        "categories_reactivate_category",
        "categories_reorder_category",
        "categories_create_category_group",
        "categories_update_category_group",
        "categories_delete_category_group",
        "categories_reorder_category_group",
        "cashflow_get_cashflow_summary",
        "cashflow_get_cashflow_trends",
        "cashflow_get_cashflow_breakdown",
        "merchants_list_merchants",
        "merchants_get_merchant",
        "merchants_update_merchant",
        "merchants_delete_merchant",
        "household_get_current_user",
        "household_get_household",
        "household_get_household_member",
        "household_get_household_preferences",
        "household_list_household_members",
        "household_update_current_user",
        "household_update_household_preferences",
        "recurring_list_recurring_streams",
        "recurring_get_recurring_stream",
        "recurring_list_recurring_occurrences",
        "recurring_get_recurring_summary",
        "recurring_create_recurring_stream",
        "recurring_update_recurring_stream",
        "recurring_remove_recurring_stream",
        "investments_list_investment_accounts",
        "investments_list_holdings",
        "investments_get_holding",
        "investments_get_holding_performance",
        "investments_get_portfolio",
        "investments_get_security",
        "investments_search_securities",
        "investments_create_manual_holding",
        "investments_update_manual_holding",
        "investments_delete_manual_holding",
        "reports_get_report_data",
        "reports_list_saved_reports",
        "reports_get_saved_report",
        "reports_create_saved_report",
        "reports_update_saved_report",
        "reports_delete_saved_report",
        "goals_list_goals",
        "goals_get_goal",
        "goals_create_goal",
        "goals_update_goal",
        "goals_delete_goal",
        "goals_archive_goal",
        "goals_restore_goal",
        "goals_update_goal_priorities",
        "goals_link_goal_account_balance",
        "goals_unlink_goal_account",
        "goals_list_goal_events",
        "goals_contribute_to_goal",
        "goals_withdraw_from_goal",
        "goals_update_goal_event",
        "goals_delete_goal_event",
        "goals_get_goal_budget_amounts",
        "goals_set_goal_budget_amount",
        "budget_get_budget",
        "budget_list_budget_months",
        "budget_get_budget_settings",
        "budget_get_budget_category",
        "budget_get_flex_rollover_settings",
        "budget_set_budget_amount",
        "budget_set_budget_group_amount",
        "budget_set_flex_budget_amount",
        "budget_set_budget_category_variability",
        "budget_set_budget_group_variability",
        "budget_set_budget_category_rollover",
        "budget_set_budget_group_rollover",
        "budget_set_flex_rollover_settings",
        "budget_reset_budget_rollover",
        "budget_create_budget",
        "budget_reset_budget",
        "budget_clear_budget",
        "transactions_list_transactions",
        "transactions_get_transaction",
        "transactions_create_transaction",
        "transactions_update_transaction",
        "transactions_delete_transaction",
        "transactions_get_transaction_splits",
        "transactions_update_transaction_splits",
        "transactions_unsplit_transaction",
        "transactions_list_transaction_attachments",
        "transactions_get_transaction_attachment",
        "transactions_upload_transaction_attachment",
        "transactions_download_transaction_attachment",
        "transactions_delete_transaction_attachment",
        "receipts_list_receipts",
        "receipts_get_receipt",
        "receipts_upload_receipt",
        "receipts_delete_receipt",
        "receipts_match_receipt",
        "receipts_unmatch_receipt",
        "receipts_update_receipt",
        "receipts_get_receipt_settings",
        "receipts_update_receipt_settings",
    }
    assert {str(resource.uri) for resource in resources} == set()


@pytest.mark.anyio
async def test_server_registers_tool_metadata() -> None:
    mcp = create_mcp()

    tools = await mcp.list_tools()

    assert all(tool.description for tool in tools)
    assert all(tool.annotations for tool in tools)

    by_name = {tool.name: tool for tool in tools}
    assert by_name["accounts_list_accounts"].annotations.read_only_hint is True
    assert by_name["auth_load_session"].annotations.read_only_hint is True
    assert by_name["transactions_delete_transaction"].annotations.destructive_hint is True
    assert by_name["budget_clear_budget"].annotations.destructive_hint is True
    assert by_name["transactions_update_transaction"].annotations.read_only_hint is False


@pytest.mark.anyio
async def test_no_tool_exposes_session_path() -> None:
    """This deployment is single-tenant: exactly one Monarch account per
    server, configured once via MONARCH_SESSION_PATH/MONARCH_CONFIG_DIR. No
    tool should let a caller aim a call at a different session file."""
    mcp = create_mcp()

    tools = await mcp.list_tools()

    leaked = [t.name for t in tools if "session_path" in t.input_schema.get("properties", {})]
    assert leaked == []


@pytest.mark.anyio
async def test_server_exposes_typed_input_schemas() -> None:
    mcp = create_mcp()

    tools = await mcp.list_tools()
    by_name = {tool.name: tool for tool in tools}

    transaction_schema = by_name["transactions_list_transactions"].input_schema
    transaction_filter = transaction_schema["$defs"]["TransactionFilterInput"]
    assert transaction_filter["additionalProperties"] is False
    assert "needs_review" in transaction_filter["properties"]
    assert "review_status" not in transaction_filter["properties"]
    assert transaction_schema["properties"]["sort"]["enum"] == [
        "date",
        "inverse_date",
        "amount",
        "inverse_amount",
    ]

    merchant_schema = by_name["merchants_list_merchants"].input_schema
    assert merchant_schema["properties"]["sort"]["enum"] == [
        "NAME",
        "TRANSACTION_COUNT",
    ]

    receipt_schema = by_name["receipts_update_receipt"].input_schema
    line_item = receipt_schema["$defs"]["ReceiptLineItemUpdateInput"]
    assert line_item["additionalProperties"] is False
    assert line_item["required"] == ["line_item_id"]

    receipt_list_schema = by_name["receipts_list_receipts"].input_schema
    receipt_filter = receipt_list_schema["$defs"]["ReceiptFilterInput"]
    source_schema = receipt_filter["properties"]["source"]
    assert source_schema["anyOf"][0]["enum"] == ["upload", "email"]


@pytest.mark.anyio
async def test_server_exposes_output_controls() -> None:
    mcp = create_mcp()

    tools = await mcp.list_tools()
    by_name = {tool.name: tool for tool in tools}

    schema = by_name["accounts_list_accounts"].input_schema
    assert schema["properties"]["output_mode"]["enum"] == ["summary", "full", "raw"]
    assert schema["properties"]["output_mode"]["default"] == "summary"
    assert "fields" in schema["properties"]
    assert by_name["accounts_list_accounts"].output_schema is None


def _content_json(result) -> list:
    """MCPServer v2 emits one content block per list element rather than a
    single JSON-array block; reassemble that back into a plain list for
    assertions that don't care about wire framing."""
    return [json.loads(block.text) for block in result.content]


@pytest.mark.anyio
async def test_tool_output_modes(monkeypatch, tmp_path) -> None:
    session_path = tmp_path / "session.json"
    session_path.write_text(
        '{"token":"token-123","token_expiration":null,"user_id":"user-123","email":"person@example.com"}',
        encoding="utf-8",
    )
    monkeypatch.setenv("MONARCH_SESSION_PATH", str(session_path))

    def fake_list_accounts(session, *, filters=None):
        assert session.token == "token-123"
        return [
            Account(
                id="account-1",
                display_name="Checking",
                balance=100.0,
                raw={"logo": "large-payload"},
            )
        ]

    monkeypatch.setattr(accounts, "api_list_accounts", fake_list_accounts)
    mcp = create_mcp()

    summary = await mcp.call_tool("accounts_list_accounts", {})
    assert _content_json(summary) == [
        {
            "id": "account-1",
            "name": "Checking",
            "type": None,
            "subtype": None,
            "institution": None,
            "balance": "$100.00",
            "net_worth": "",
            "hidden": "",
        }
    ]

    full = await mcp.call_tool("accounts_list_accounts", {"output_mode": "full"})
    full_data = _content_json(full)
    assert full_data[0]["display_name"] == "Checking"
    assert "raw" not in full_data[0]

    raw = await mcp.call_tool("accounts_list_accounts", {"output_mode": "raw"})
    assert _content_json(raw)[0]["raw"] == {"logo": "large-payload"}

    projected = await mcp.call_tool(
        "accounts_list_accounts",
        {"output_mode": "raw", "fields": ["id", "raw.logo"]},
    )
    assert _content_json(projected) == [{"id": "account-1", "raw.logo": "large-payload"}]


@pytest.mark.anyio
async def test_tool_call_ignores_session_path_even_if_a_client_sends_it(
    monkeypatch, tmp_path
) -> None:
    """Belt-and-suspenders: even if a non-conforming client sends
    session_path anyway, it must not reach the underlying function, since
    that would let one call read a different account's data than the one
    this deployment is configured for."""
    session_path = tmp_path / "session.json"
    session_path.write_text(
        '{"token":"token-123","token_expiration":null,"user_id":"user-123","email":"person@example.com"}',
        encoding="utf-8",
    )
    monkeypatch.setenv("MONARCH_SESSION_PATH", str(session_path))

    seen_session_paths = []

    def fake_get_account(session, account_id):
        seen_session_paths.append(session.token)
        return Account(id=account_id, display_name="Checking", balance=1.0, raw={})

    monkeypatch.setattr(accounts, "api_get_account", fake_get_account)
    mcp = create_mcp()

    # MCPServer validates arguments against the advertised schema, so an
    # unadvertised extra field is simply dropped rather than raising.
    result = await mcp.call_tool(
        "accounts_get_account",
        {"account_id": "account-1", "session_path": "/some/other/session.json"},
    )

    assert result.is_error is not True
    assert seen_session_paths == ["token-123"]
