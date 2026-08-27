from __future__ import annotations

from typing import Literal, TypeAlias

from pydantic import BaseModel, ConfigDict

CategoryTypeValue: TypeAlias = Literal["expense", "income", "transfer"]
CashflowIntervalValue: TypeAlias = Literal["month", "quarter", "year"]
CashflowDirectionValue: TypeAlias = Literal["income", "expenses"]
CashflowBreakdownGroupValue: TypeAlias = Literal[
    "category",
    "category_group",
    "merchant",
]
MerchantSortValue: TypeAlias = Literal["NAME", "TRANSACTION_COUNT"]
ReportGroupValue: TypeAlias = Literal["category", "category_group", "merchant"]
ReportTimeframeValue: TypeAlias = Literal["day", "week", "month", "quarter", "year"]
ReportSortValue: TypeAlias = Literal["sum", "sum_income", "sum_expense", "count", "avg", "max"]
TransactionSortValue: TypeAlias = Literal["date", "inverse_date", "amount", "inverse_amount"]
TransactionReviewStatusValue: TypeAlias = Literal["reviewed", "needs_review"]
TransactionVisibilityValue: TypeAlias = Literal[
    "all_transactions",
    "non_hidden_transactions_only",
    "hidden_transactions_only",
]
ReceiptStatusValue: TypeAlias = Literal[
    "completed",
    "failed",
    "in_progress",
    "pending",
    "pending_matches",
]
ReceiptSourceValue: TypeAlias = Literal["upload", "email"]
RecurringFrequencyValue: TypeAlias = Literal[
    "weekly",
    "every_two_weeks",
    "twice_a_month",
    "monthly",
    "every_two_months",
    "quarterly",
    "every_six_months",
    "yearly",
]
RecurringTypeValue: TypeAlias = Literal["expense", "income", "transfer", "credit_card"]
BudgetVariabilityValue: TypeAlias = Literal["fixed", "flexible", "non_monthly"]
BudgetRolloverFrequencyValue: TypeAlias = Literal[
    "monthly",
    "variable",
    "every_2_months",
    "every_3_months",
    "every_4_months",
    "every_5_months",
    "every_6_months",
    "every_7_months",
    "every_8_months",
    "every_9_months",
    "every_10_months",
    "every_11_months",
    "every_12_months",
]
BudgetRolloverTypeValue: TypeAlias = Literal["monthly", "non_monthly", "one_time"]
GoalTypeValue: TypeAlias = Literal[
    "custom",
    "savings",
    "debt",
    "asset",
    "emergency_fund",
    "home",
    "retirement",
    "education",
    "vehicle",
    "vacation",
    "large_purchase",
]
GoalStatusValue: TypeAlias = Literal[
    "ahead",
    "archived",
    "at_risk",
    "completed",
    "incomplete",
    "on_track",
]


class MonarchInput(BaseModel):
    model_config = ConfigDict(extra="forbid")


class AuthSessionInput(MonarchInput):
    token: str
    token_expiration: str | None = None
    user_id: str | None = None
    email: str | None = None


class AccountFilterInput(MonarchInput):
    account_ids: list[str] | None = None
    account_types: list[str] | None = None
    account_subtypes: list[str] | None = None
    groups: list[str] | None = None
    include_hidden: bool | None = None
    include_deleted: bool | None = None


class CategoryFilterInput(MonarchInput):
    group_ids: list[str] | None = None
    types: list[CategoryTypeValue] | None = None


class CashflowFilterInput(MonarchInput):
    account_ids: list[str] | None = None
    category_ids: list[str] | None = None
    category_group_ids: list[str] | None = None
    merchant_ids: list[str] | None = None
    tag_ids: list[str] | None = None
    include_hidden: bool = False


class TransactionFilterInput(MonarchInput):
    start_date: str | None = None
    end_date: str | None = None
    search: str | None = None
    transaction_ids: list[str] | None = None
    account_ids: list[str] | None = None
    category_ids: list[str] | None = None
    category_group_ids: list[str] | None = None
    merchant_ids: list[str] | None = None
    tag_ids: list[str] | None = None
    goal_ids: list[str] | None = None
    min_absolute_amount: float | None = None
    max_absolute_amount: float | None = None
    category_type: CategoryTypeValue | None = None
    credits_only: bool | None = None
    debits_only: bool | None = None
    is_pending: bool | None = None
    is_recurring: bool | None = None
    is_split: bool | None = None
    is_uncategorized: bool | None = None
    is_untagged: bool | None = None
    has_notes: bool | None = None
    has_attachments: bool | None = None
    hide_from_reports: bool | None = None
    needs_review: bool | None = None
    needs_review_by_user_id: str | None = None
    needs_review_unassigned: bool | None = None
    synced_from_institution: bool | None = None
    imported_from_mint: bool | None = None
    transaction_visibility: TransactionVisibilityValue | None = None


class RecurringFilterInput(MonarchInput):
    account_ids: list[str] | None = None
    category_ids: list[str] | None = None
    merchant_ids: list[str] | None = None
    recurring_ids: list[str] | None = None
    frequencies: list[RecurringFrequencyValue] | None = None
    recurring_types: list[RecurringTypeValue] | None = None
    is_completed: bool | None = None


class ReceiptFilterInput(MonarchInput):
    status: ReceiptStatusValue | None = None
    source: ReceiptSourceValue | None = None


class ReceiptLineItemUpdateInput(MonarchInput):
    line_item_id: str
    title: str | None = None
    category_id: str | None = None
    price: float | None = None
    quantity: int | None = None


class TransactionSplitDraftInput(MonarchInput):
    amount: float
    id: str | None = None
    date: str | None = None
    merchant_name: str | None = None
    category_id: str | None = None
    notes: str | None = None
    hide_from_reports: bool | None = None
    review_status: TransactionReviewStatusValue | None = None
    needs_review: bool | None = None
    needs_review_by_user_id: str | None = None
    owner_user_id: str | None = None
    tag_ids: list[str] | None = None
    goal_id: str | None = None
