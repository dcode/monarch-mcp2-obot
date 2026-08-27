from __future__ import annotations

from monarch_mcp.output import shape_output


def test_transaction_page_summary_uses_transactions() -> None:
    result = shape_output(
        "transactions_list_transactions",
        {
            "transactions": [
                {
                    "id": "transaction-1",
                    "date": "2026-05-30",
                    "merchant_name": "Coffee",
                    "amount": 4.5,
                    "account": {"display_name": "Checking"},
                    "category": {"name": "Restaurants"},
                    "review_status": "reviewed",
                    "pending": False,
                }
            ],
            "total_count": 1,
            "limit": 100,
            "offset": 0,
        },
    )

    assert result == [
        {
            "id": "transaction-1",
            "date": "2026-05-30",
            "merchant": "Coffee",
            "amount": "$4.50",
            "account": "Checking",
            "category": "Restaurants",
            "review": "reviewed",
            "pending": "no",
        }
    ]


def test_fields_project_from_full_output() -> None:
    result = shape_output(
        "accounts_list_accounts",
        [{"id": "account-1", "raw": {"logo": "large-payload"}}],
        output_mode="raw",
        fields=["id", "raw.logo"],
    )

    assert result == [{"id": "account-1", "raw.logo": "large-payload"}]


def test_receipt_summary_includes_source() -> None:
    result = shape_output(
        "receipts_list_receipts",
        {
            "receipts": [
                {
                    "id": "receipt-1",
                    "source": "email",
                    "status": "pending_matches",
                    "order": {"merchant_name": "Store", "grand_total": 12.34},
                    "is_matched": False,
                }
            ]
        },
    )

    assert result[0]["source"] == "email"
