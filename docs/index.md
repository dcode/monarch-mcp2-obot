# monarch-mcp2-obot

A single-tenant [Monarch Money](https://www.monarchmoney.com) MCP server for self-hosting behind
[obot](https://obot.ai), forked from [erikrubstein/monarch-mcp2](https://github.com/erikrubstein/monarch-mcp2)
(itself not a fork of the more commonly-seen `robcerda/monarch-mcp-server` family — it's an independent
implementation backed by its own API client,
[monarch-api2](https://github.com/erikrubstein/monarch-api2)).

Not affiliated with, endorsed by, or supported by Monarch Money.

## Why this fork exists

1. **Ported to MCP Python SDK v2** (`MCPServer`, not the deprecated v1 `FastMCP`).
2. **A login workflow built for obot**: credentials configured once as environment variables, with
   optional TOTP-seed support so an authenticator-app MFA challenge can be solved automatically — no
   browser, no OS keyring, no copying a 6-digit code by hand. See [Authentication](authentication.md).
3. **Deliberately single-tenant**: exactly one Monarch account per running instance. No tool call can
   target a different account's session, even if a client tried to send one.
4. **Resilient to session expiry**: tool calls that fail because the saved session expired are
   transparently retried once after a fresh login, instead of surfacing a raw 401 to the caller — see
   [Authentication](authentication.md#automatic-re-login-on-session-expiry).

## What's inherited from upstream

125 tools across 14 groups — accounts, transactions, budget, cashflow, categories, goals, household,
investments, merchants, receipts, recurring, reports, tags — unchanged from `monarch-mcp2`. See its
[tool list](https://github.com/erikrubstein/monarch-mcp2#tools) and
[design notes](https://github.com/erikrubstein/monarch-api2#design-approach) for what's covered and
what's deliberately out of scope (transaction rules and automation, provider account-connection flows,
account-admin edges). See [Tools](tools.md) for how those tools are shaped and controlled from an MCP
client.

## Where to go next

- [Installation](installation.md) — obot (uvx/stdio and Docker), local development.
- [Configuration](configuration.md) — every environment variable, transport selection, secrets management.
- [Authentication](authentication.md) — `auth_login`/`auth_status`, TOTP MFA, the reauth-on-expiry retry.
- [Tools](tools.md) — the 125+ tools, output shaping (`output_mode`/`fields`), the single-tenant guarantee.
- [Development](development.md) — running tests/lint/type-checks, pre-commit, contributing.

## License

MIT, inherited from upstream. See [LICENSE](https://github.com/dcode/monarch-mcp2-obot/blob/main/LICENSE)
and [NOTICE](https://github.com/dcode/monarch-mcp2-obot/blob/main/NOTICE.md) for the full attribution
chain.
