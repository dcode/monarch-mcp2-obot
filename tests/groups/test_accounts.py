from __future__ import annotations

from monarch_api import Account, AccountFilter

from monarch_mcp.groups import accounts


def test_account_filter_from_dict() -> None:
    result = accounts.account_filter_from_dict(
        {
            "account_ids": ["account-1"],
            "account_types": ["depository"],
            "account_subtypes": ["checking"],
            "groups": ["asset"],
            "include_hidden": True,
            "include_deleted": False,
        }
    )

    assert isinstance(result, AccountFilter)
    assert result.to_api() == {
        "ids": ["account-1"],
        "accountTypes": ["depository"],
        "accountSubtypes": ["checking"],
        "groups": ["asset"],
        "includeHidden": True,
        "includeDeleted": False,
    }


def test_list_accounts_loads_session_and_serializes(monkeypatch, tmp_path) -> None:
    session_path = tmp_path / "session.json"
    session_path.write_text(
        '{"token":"token-123","token_expiration":null,"user_id":"user-123","email":"person@example.com"}',
        encoding="utf-8",
    )

    def fake_list_accounts(session, *, filters=None):
        assert session.token == "token-123"
        assert filters.account_ids == ["account-1"]
        return [Account(id="account-1", display_name="Checking", balance=100.0)]

    monkeypatch.setattr(accounts, "api_list_accounts", fake_list_accounts)

    result = accounts.list_accounts(
        filters={"account_ids": ["account-1"]},
        session_path=str(session_path),
    )

    assert result == [
        {
            "id": "account-1",
            "display_name": "Checking",
            "balance": 100.0,
            "current_balance": None,
            "last_updated_at": None,
            "type": None,
            "subtype": None,
            "institution": None,
            "owner": None,
            "is_asset": None,
            "is_manual": None,
            "is_hidden": None,
            "sync_disabled": None,
            "include_in_net_worth": None,
            "logo_url": None,
            "icon": None,
        }
    ]
