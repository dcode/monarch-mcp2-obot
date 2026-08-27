# Tools

127 tools total: 125 inherited unchanged from
[erikrubstein/monarch-mcp2](https://github.com/erikrubstein/monarch-mcp2), plus this fork's
`auth_login` and `auth_status` (see [Authentication](authentication.md)).

## Groups

Each tool is named `<group>_<action>`, e.g. `transactions_list_transactions`,
`budget_set_budget_amount`. The 14 groups:

`accounts`, `auth`, `budget`, `cashflow`, `categories`, `goals`, `household`, `investments`,
`merchants`, `receipts`, `recurring`, `reports`, `tags`, `transactions`.

See upstream's [tool list](https://github.com/erikrubstein/monarch-mcp2#tools) and
[design notes](https://github.com/erikrubstein/monarch-api2#design-approach) for what's covered
inside each group and what's deliberately out of scope (transaction rules and automation, provider
account-connection flows, account-admin edges).

## Output shaping: `output_mode` and `fields`

Every tool accepts two extra keyword arguments beyond its own, added uniformly by this fork's tool
registration layer:

- **`output_mode`** (`"summary"` | `"full"` | `"raw"`, default `"summary"`) — `summary` returns a
  compact, CLI-style projection of the result (the shape most tools need most of the time); `full`
  returns the complete structured data without raw upstream payloads; `raw` includes those raw
  payloads too.
- **`fields`** (list of dotted paths, optional) — when given, returns only those fields from the
  result instead of a mode-shaped projection, e.g. `["id", "merchant.name", "category.name"]`.

This exists so an MCP client (or the model driving it) can ask for exactly as much data as it needs
per call, instead of always paying for — and reading through — the full upstream response shape.

## Tool annotations

Every tool is annotated with MCP's standard hints, inferred from its name:

- **Read-only** (`download_`, `get_`, `list_`, `load_`, `search_` prefixes) — marked
  `read_only_hint=True`, `idempotent_hint=True`.
- **Destructive** (`clear_`, `delete_`, `remove_`, `reset_` prefixes) — marked
  `destructive_hint=True`, and their description notes they may delete, clear, reset, or otherwise
  remove data.
- Everything else that looks like a write (`create_`, `update_`, `save_`, `set_`, ... — see
  `tool_metadata.py::WRITE_PREFIXES`) has its description note that it may create or update Monarch
  data.

## Single-tenant, on purpose

`session_path` exists on every underlying function (a monarch-api2 convention) but is stripped from
every tool's public schema before it's exposed to an MCP client. One deployment, one Monarch account,
one session file, chosen once via `MONARCH_SESSION_PATH` / `MONARCH_CONFIG_DIR` (see
[Configuration](configuration.md)). No tool call can override it per-request, by design, even if a
client sent one anyway.

## Automatic re-login on expiry

Tool calls that fail because the saved session expired are retried once, transparently, after a
fresh login — see [Authentication](authentication.md#automatic-re-login-on-session-expiry) for the
full behavior and its limits.
