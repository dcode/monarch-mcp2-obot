# Notice

This project, `monarch-mcp2-obot`, is a fork of
[erikrubstein/monarch-mcp2](https://github.com/erikrubstein/monarch-mcp2), which is itself an
independent implementation (not derived from the more commonly-seen `robcerda/monarch-mcp-server`
family) backed by its own API client,
[erikrubstein/monarch-api2](https://github.com/erikrubstein/monarch-api2).

Both upstream projects, and this fork, are licensed under the MIT License — see `LICENSE`.

## Attribution

- **Original work**: Copyright (c) 2026 Erik Rubstein
  ([erikrubstein/monarch-mcp2](https://github.com/erikrubstein/monarch-mcp2)). The 125 Monarch Money
  tools across 14 groups (accounts, transactions, budget, cashflow, categories, goals, household,
  investments, merchants, receipts, recurring, reports, tags), and their supporting
  serialization/output/schema layer, originate there.
- **This fork's additions and modifications**: Copyright (c) 2026 Derek Ditch
  ([dcode/monarch-mcp2-obot](https://github.com/dcode/monarch-mcp2-obot)):
  - Porting `FastMCP` (MCP Python SDK v1) to `MCPServer` (v2) across the server and every tool group.
  - The obot-oriented login workflow: environment-variable-configured credentials, automatic
    TOTP-based MFA (`auth_runtime.py`), the `auth_login`/`auth_status` tools, and best-effort
    startup login.
  - Single-tenant enforcement: hiding `session_path` from every tool's public schema
    (`tool_metadata.py`), so no MCP client can target a different account's session.
  - Transport selection (`stdio` / `sse` / `streamable-http`) for obot's two deployment models.
  - The automatic re-login-and-retry wrapper for expired sessions (`reauth.py`).
  - `_FILE`-suffixed secrets support (`MONARCH_PASSWORD_FILE`, `MONARCH_TOTP_SECRET_FILE`) for
    Docker/Kubernetes secret-mount deployments.
  - The Dockerfile, GitHub Actions workflows, pre-commit configuration, and this documentation site.

## Third-party dependencies

This project depends on [monarch-api2](https://github.com/erikrubstein/monarch-api2)
(Copyright (c) 2026 Erik Rubstein, MIT License) and the packages listed in `pyproject.toml`, each
under their own respective licenses.

## Disclaimer

Not affiliated with, endorsed by, or supported by Monarch Money.
