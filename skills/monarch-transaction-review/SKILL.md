---
name: monarch-transaction-review
description: Prepare and review Monarch Money transactions with the Monarch MCP server while learning the user's merchant, category, tag, note, receipt, and recurring spending preferences. Use when the user asks Codex to prepare, review, categorize, tag, annotate, correct, or learn from Monarch transactions, especially unreviewed transactions or transactions tagged for AI preparation/human review.
---

# Monarch Transaction Review

## Core Rule

Never mark a transaction reviewed during AI preparation. Only mark a transaction reviewed during the human review stage after the user explicitly says to mark it reviewed.

Use the Monarch MCP server tools. Match the tool group to the user's request:

- Transaction preparation or human review queues: use `transactions_*` plus `tags_*`.
- Cashflow summaries, trends, or breakdowns: use `cashflow_*`.
- Report-style grouped spending/income analysis: use `reports_*`.
- Budgets, budget months, budget category amounts, or rollover settings: use `budget_*`.
- Recurring bills, subscriptions, income, or expected payment schedules: use `recurring_*`.
- Accounts, balances, net worth, or account history: use `accounts_*`.
- Receipts, receipt matching, or receipt settings: use `receipts_*`.
- Merchants, categories, tags, household, goals, or investments: use the matching group.

Do not list transactions merely to answer an aggregate request when a purpose-built Monarch tool exists. For example, answer "cashflow breakdown for last month" with `cashflow_get_cashflow_breakdown`, not `transactions_list_transactions`, unless the user asks to inspect the underlying transactions.

If the request is not about transaction preparation or human review, do not add workflow tags, update transaction review status, or update memory unless the user explicitly provides a reusable preference or correction.

## Private Memory

Read the private memory file before reviewing transactions:

```text
~/.config/monarch/transaction-review-memory.md
```

If it does not exist, create it from `references/memory-template.md` or run:

```bash
python scripts/init_memory.py
```

Do not store personal transaction memory in this skill folder or in a public repo. The memory file should capture:

- merchant cleanup preferences
- category choices
- tag rules
- note-writing style
- receipt expectations
- recurring bills, obligations, subscriptions, and normal spending rhythms
- account-specific or household context
- corrections learned from the user
- open questions the agent should ask about

Only update memory from explicit user corrections, user-provided preferences, or strong repeated patterns. Mark uncertain inferences as tentative.

## Tags

Use these review workflow tags:

- `AI Prepared` (`#3B82F6`): AI prepared the transaction and it is waiting for human review.
- `AI Needs Context` (`#F59E0B`): AI could not confidently decide what to do.

Create missing tags when needed. Preserve unrelated user tags.

## Prepare Transactions

When the user asks to review or prepare transactions:

1. Load memory.
2. Find unreviewed transactions, usually with `filters.needs_review=true`.
3. Inspect enough context to decide safely. Use `output_mode="full"` when summary output lacks needed fields.
4. Apply high-confidence updates to merchant, category, tags, notes, or other editable fields.
5. Add `AI Prepared` when updated or confidently left unchanged for human review.
6. Add `AI Needs Context` when the transaction needs user clarification.
7. Do not set `review_status="reviewed"` in this phase.
8. Summarize actions as: transaction id, merchant/date/amount, changes made, confidence, and questions.

If confidence is low, prefer tagging `AI Needs Context` over guessing.

## Human Review Loop

When the user asks to review, audit, or manually review AI-prepared transactions:

1. Fetch transactions tagged `AI Prepared`, one at a time unless the user asks for a batch.
2. Show the transaction, the current proposed state, and why the agent thinks it is correct.
3. Ask for one of: mark reviewed, correct, needs context, skip.
4. On mark reviewed:
   - remove `AI Prepared`
   - set `review_status="reviewed"`
5. On correct:
   - apply the correction
   - update memory with the lesson
   - ask whether to mark reviewed now
6. On needs context:
   - replace `AI Prepared` with `AI Needs Context`
   - add the open question to memory
7. On skip:
   - leave the transaction unchanged

## Retry Needs Context

When the user asks to retry, revisit, or check transactions that need context:

1. Fetch transactions tagged `AI Needs Context`.
2. Focus first on transactions that now have notes or other new context.
3. Treat newly added notes as likely user clarification, but still inspect the transaction.
4. Re-attempt preparation using memory, notes, merchant, amount, account, date, and tags.
5. If the new context is enough:
   - apply the prepared updates
   - replace `AI Needs Context` with `AI Prepared`
   - do not set `review_status="reviewed"`
6. If context is still lacking:
   - keep `AI Needs Context`
   - summarize what is still missing
   - update memory only if the user provided a reusable preference or correction

Do not assume any note is permission to mark reviewed. Notes are clarification for preparation, not human review approval.

## Match Receipts

When the user asks to match receipts:

1. Use `receipts_list_receipts` to find receipts, then identify unmatched receipts from full output fields such as `is_matched` and `transaction_id`. The default includes uploaded and emailed receipts; filter by `source` only when useful. Filter by receipt `status` when useful, but do not assume status alone means matched or unmatched.
2. For each unmatched receipt, search candidate transactions with `transactions_list_transactions` using date, amount, merchant, and account context.
3. Match only when confidence is high, such as matching date, amount, and merchant or a clear user note.
4. Use `receipts_match_receipt` for high-confidence matches.
5. Leave ambiguous receipts unmatched and summarize the candidates or missing context.
6. Do not alter transaction review status as part of receipt matching unless the user explicitly asks.

When receipt matching reveals a durable user preference or spending habit, add it to memory. For example, "gas receipts are often absent" belongs in memory; a one-off receipt match usually does not.

## Learning Rules

Update memory in concise, durable rules. Prefer rules that will help future transactions:

- Good: "If merchant is Shell and account is checking, categorize as Auto & Transport / Gas unless transaction notes indicate convenience-store purchase."
- Good: "Rent is expected monthly around the first week and usually does not have a receipt."
- Good: "For reimbursable work expenses, tag `Work Reimbursement` and write notes as `Reimbursable: <short reason>`."
- Weak: "Changed transaction abc123 to Gas." Put isolated facts in a correction log only if no general rule is clear.

Record spending habits as context, not as automatic proof. A recurring pattern can raise confidence, but it should not override a conflicting merchant, amount, date, note, or user correction.

## Output Controls

Use compact output by default. Request larger output only when needed:

- `output_mode="summary"` for queues and quick scans
- `output_mode="full"` for editing decisions
- `output_mode="raw"` only when raw API fields are necessary
- `fields=[...]` to limit large responses

## Safety

Treat all financial data as sensitive. Do not print raw payloads, tokens, full account details, or long transaction histories unless necessary. Never delete transactions or make destructive changes as part of review unless the user explicitly asks.
