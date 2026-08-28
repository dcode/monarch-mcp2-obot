# monarch-mcp2-obot

[![Lint](https://github.com/dcode/monarch-mcp2-obot/actions/workflows/lint.yml/badge.svg)](https://github.com/dcode/monarch-mcp2-obot/actions/workflows/lint.yml)
[![Tests](https://github.com/dcode/monarch-mcp2-obot/actions/workflows/test.yml/badge.svg)](https://github.com/dcode/monarch-mcp2-obot/actions/workflows/test.yml)
[![Documentation](https://github.com/dcode/monarch-mcp2-obot/actions/workflows/docs.yml/badge.svg)](https://dcode.github.io/monarch-mcp2-obot/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A single-tenant Monarch Money MCP server for self-hosting behind [obot](https://obot.ai),
forked from [erikrubstein/monarch-mcp2](https://github.com/erikrubstein/monarch-mcp2)
(itself not a fork of the more commonly-seen `robcerda/monarch-mcp-server` family —
it's an independent implementation backed by its own API client,
[monarch-api2](https://github.com/erikrubstein/monarch-api2)).

**Full documentation:** <https://dcode.github.io/monarch-mcp2-obot/>

This fork exists for four reasons upstream didn't cover:

1. **Ported to MCP Python SDK v2** (`MCPServer`, not the deprecated v1 `FastMCP`).
2. **A login workflow built for obot**: credentials configured once as
   environment variables, with optional TOTP-seed support so an
   authenticator-app MFA challenge can be solved automatically — no
   browser, no OS keyring, no copying a 6-digit code by hand.
3. **Deliberately single-tenant**: exactly one Monarch account per running
   instance. No tool call can target a different account's session, even
   if a client tried to send one — see "Single-tenant, on purpose" below.
4. **Resilient to session expiry**: a tool call that fails because the saved
   session expired is retried once, transparently, after a fresh login — see
   "Automatic re-login on session expiry" below.

Not affiliated with, endorsed by, or supported by Monarch Money.

## What's inherited from upstream

125 tools across 14 groups — accounts, transactions, budget, cashflow,
categories, goals, household, investments, merchants, receipts, recurring,
reports, tags — unchanged from `monarch-mcp2`. See its
[tool list](https://github.com/erikrubstein/monarch-mcp2#tools) and
[design notes](https://github.com/erikrubstein/monarch-api2#design-approach)
for what's covered and what's deliberately out of scope (transaction rules
and automation, provider account-connection flows, account-admin edges).

## What's different here

### Auth: `auth_login`, `auth_status`

Two new tools, on top of upstream's `auth_create_session` / `auth_save_session`
/ `auth_load_session` (which still work, for a fully manual one-shot login):

- **`auth_login`** — no arguments needed if the server's environment has
  `MONARCH_EMAIL` / `MONARCH_PASSWORD` (and, for authenticator-app MFA,
  `MONARCH_TOTP_SECRET`) configured. Handles an MFA challenge automatically
  by computing the current code from the seed. Pass `email` / `password` /
  `totp_secret` / `mfa_code` explicitly to override for a one-off login
  without touching server config.
- **`auth_status`** — reports whether a session exists and is currently
  valid (one lightweight API call by default), without ever returning the
  session token.

The server also attempts this login automatically at startup if credentials
are configured — best-effort, non-fatal, so a wrong password or a down
network doesn't prevent the server from starting; `auth_status` and
`auth_login` remain available to diagnose and retry.

**TOTP seed**: the same base32 secret an authenticator app would be
enrolled with (what you'd scan as a QR code). Monarch shows this once when
you enable authenticator-app MFA — save it there, or you'll need to
disable and re-enable MFA to get a fresh one. This only applies if your
account's MFA method is an authenticator app; email-code MFA isn't
automatable this way (there's no seed to compute a code from) and still
needs a human to relay a fresh code via `auth_login`'s `mfa_code` argument.

### Automatic re-login on session expiry

If a saved session expires mid-use, every tool call now goes through a
re-login retry (`reauth.py`): a failure that looks like an expired/invalid
session (matched against the wording Monarch's API is known to return for a
401) triggers one fresh login and one retry of the original call, if
credentials are configured. `auth_*` tools are exempt (retrying a login
failure by logging in again would just mask the real error), and this never
retries more than once — see the docs' [Authentication
page](https://dcode.github.io/monarch-mcp2-obot/authentication/#automatic-re-login-on-session-expiry)
for the exact matching rules and limits.

### Single-tenant, on purpose

`session_path` exists on every underlying function (a monarch-api2
convention) but is stripped from every tool's public schema before it's
exposed to an MCP client — see `tool_metadata.py`. One deployment, one
Monarch account, one session file, chosen once via `MONARCH_SESSION_PATH` /
`MONARCH_CONFIG_DIR`. This isn't just a config default: no tool call can
override it per-request, by design, even if a client sent one anyway (see
`tests/test_server.py::test_tool_call_ignores_session_path_even_if_a_client_sends_it`).

### Transport selection for obot's two deployment models

obot supports MCP servers two ways relevant here: command/`uvx`-based
(stdio) and Docker-based (a port plus a streamable-http endpoint). Both are
supported via `MCP_TRANSPORT` (default `stdio`); the Docker image sets it
to `streamable-http` by default. See `config.py` / `server.py`.

## Environment variables

| Variable | Purpose | Default |
| --- | --- | --- |
| `MONARCH_EMAIL` | Monarch account email, for automatic login | — |
| `MONARCH_PASSWORD` | Monarch account password | — |
| `MONARCH_PASSWORD_FILE` | Read the password from this file instead (Docker/Kubernetes secret mounts) | — |
| `MONARCH_TOTP_SECRET` | Base32 authenticator-app seed, for automatic MFA | — |
| `MONARCH_TOTP_SECRET_FILE` | Read the TOTP seed from this file instead | — |
| `MONARCH_SESSION_PATH` | Exact path to the session file | `$MONARCH_CONFIG_DIR/session.json` |
| `MONARCH_CONFIG_DIR` | Directory for the default session path | `~/.config/monarch` |
| `MCP_TRANSPORT` | `stdio` \| `sse` \| `streamable-http` | `stdio` (Dockerfile overrides to `streamable-http`) |
| `MCP_HOST` | Bind host for `sse`/`streamable-http` | `0.0.0.0` |
| `MCP_PORT` | Bind port for `sse`/`streamable-http` | `8000` |

Treat `MONARCH_PASSWORD` and `MONARCH_TOTP_SECRET` like any other secret.
obot's single-user MCP server model marks fields like these "sensitive"
when an admin configures the server, which covers the most common obot
deployment path; the `_FILE` variants above are for deployments layering
obot on top of Docker/Kubernetes secret mounts instead of putting the
value directly in the environment. See the docs'
[Configuration page](https://dcode.github.io/monarch-mcp2-obot/configuration/)
for details.

## Running it

### obot, command/uvx-based (stdio)

```bash
uvx --from git+https://github.com/dcode/monarch-mcp2-obot monarch-mcp
```

### obot, Docker-based (streamable-http)

```bash
docker build -t monarch-mcp2-obot:local .
docker volume create monarch-session

docker run -d --rm \
  -p 8000:8000 \
  -v monarch-session:/data \
  -e MONARCH_EMAIL=you@example.com \
  -e MONARCH_PASSWORD=... \
  -e MONARCH_TOTP_SECRET=...  `# omit if your account doesn't use authenticator-app MFA` \
  monarch-mcp2-obot:local
```

Point obot's Docker-based MCP server config at this container's
`streamable-http` endpoint on port 8000. Session state lives in the
`monarch-session` volume, so it survives container restarts and re-deploys
without a re-login.

### Local development (stdio, no Docker)

```bash
uv sync --extra dev
uv run monarch-mcp
```

## Testing

```bash
uv run pytest --cov=src --cov-report=term-missing
uv run ruff check src tests
uv run ruff format --check src tests
uv run mypy src
```

`mypy --strict` runs across the entire `src/` tree, including the 13 group
modules inherited from upstream. Install pre-commit hooks to run the same
checks automatically before each commit:

```bash
uv run pre-commit install
```

See [Development](https://dcode.github.io/monarch-mcp2-obot/development/) for more, and
`ROADMAP.md` for what's done, known gaps, and deliberately deferred next steps.

## Releases

Until a PyPI release is possible (see below), install a specific version from its
[GitHub release](https://github.com/dcode/monarch-mcp2-obot/releases) — semantic-versioned tags,
with the built wheel/sdist attached as immutable release assets:

```bash
pip install https://github.com/dcode/monarch-mcp2-obot/releases/download/vX.Y.Z/monarch_mcp2_obot-X.Y.Z-py3-none-any.whl
```

## Publishing to PyPI

The package metadata (classifiers, license, URLs, a `py.typed` marker) is ready for PyPI, but an
actual upload isn't yet possible: this project depends on `monarch-api2` via a direct GitHub
reference (no PyPI release of that package exists), and PyPI rejects any package whose metadata
contains a direct/VCS dependency. See "Publishing to PyPI" in the
[Installation docs](https://dcode.github.io/monarch-mcp2-obot/installation/#publishing-to-pypi) and
in `ROADMAP.md` for what would need to change first.

## License

MIT, inherited from upstream, with this fork's own additions also under MIT. See `LICENSE` and
`NOTICE.md` for the full attribution.
