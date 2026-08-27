# monarch-mcp2-obot

A single-tenant Monarch Money MCP server for self-hosting behind [obot](https://obot.ai),
forked from [erikrubstein/monarch-mcp2](https://github.com/erikrubstein/monarch-mcp2)
(itself not a fork of the more commonly-seen `robcerda/monarch-mcp-server` family —
it's an independent implementation backed by its own API client,
[monarch-api2](https://github.com/erikrubstein/monarch-api2)).

This fork exists for three reasons upstream didn't cover:

1. **Ported to MCP Python SDK v2** (`MCPServer`, not the deprecated v1 `FastMCP`).
2. **A login workflow built for obot**: credentials configured once as
   environment variables, with optional TOTP-seed support so an
   authenticator-app MFA challenge can be solved automatically — no
   browser, no OS keyring, no copying a 6-digit code by hand.
3. **Deliberately single-tenant**: exactly one Monarch account per running
   instance. No tool call can target a different account's session, even
   if a client tried to send one — see "Single-tenant, on purpose" below.

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
| `MONARCH_TOTP_SECRET` | Base32 authenticator-app seed, for automatic MFA | — |
| `MONARCH_SESSION_PATH` | Exact path to the session file | `$MONARCH_CONFIG_DIR/session.json` |
| `MONARCH_CONFIG_DIR` | Directory for the default session path | `~/.config/monarch` |
| `MCP_TRANSPORT` | `stdio` \| `sse` \| `streamable-http` | `stdio` (Dockerfile overrides to `streamable-http`) |
| `MCP_HOST` | Bind host for `sse`/`streamable-http` | `0.0.0.0` |
| `MCP_PORT` | Bind port for `sse`/`streamable-http` | `8000` |

Treat `MONARCH_PASSWORD` and `MONARCH_TOTP_SECRET` like any other secret —
obot's single-user MCP server model marks fields like these "sensitive"
when an admin configures the server; use that.

## Running it

### obot, command/uvx-based (stdio)

```bash
uvx --from git+https://<your-fork-url> monarch-mcp
```

(Once you've pushed this fork somewhere — see the note at the end of this
README about where this code currently lives.)

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
uv sync
uv run monarch-mcp
```

## Testing

```bash
uv run pytest
uv run ruff check src tests
uv run ruff format --check src tests
uv run mypy src/monarch_mcp/auth_runtime.py src/monarch_mcp/config.py \
  src/monarch_mcp/server.py src/monarch_mcp/groups/auth.py src/monarch_mcp/tool_metadata.py
```

(`mypy --strict` is scoped to the files this fork authored or substantially
changed; the inherited group modules weren't re-audited for strict typing
as part of this fork — see ROADMAP.md.)

## Where this code lives

This was built and verified locally (installed, tested, and run — both
transports — against a real MCP `initialize` handshake) but has not been
pushed to a hosted git remote as part of this work. Push it to your own
fork/remote before pointing `uvx --from git+...` at it, and update the
Docker build instructions above accordingly if you build from that remote
instead of a local checkout.

## License

MIT, inherited from upstream. See `LICENSE`.
