# Roadmap / working notes

Purpose of this file: pick this project back up after a few days away
without having to re-derive context. Update it as things change — it's
working documentation, not a changelog.

## Where this came from

Forked from [erikrubstein/monarch-mcp2](https://github.com/erikrubstein/monarch-mcp2)
at commit `f4d47eeddea4dda3efc99a092a2e39b2a441264d` (2026-08-19, "Add
receipt source filtering"). That project is itself pinned to
`monarch-api2` tag `v0.2.0`. If you pull upstream changes later, re-check
both pins and re-read this file's "Known gaps" section — some of it exists
because of exactly-that-version behavior.

## Status: done in this session

All verified by actually running things, not just reading code — see the
"How things were verified" section below for the specific checks.

- [x] Ported `FastMCP` (v1) → `MCPServer` (v2) across `server.py`,
      `tool_metadata.py`, and all 14 `groups/*.py` files. Mechanical
      rename; `@mcp.tool()` decorator usage was unaffected.
- [x] `ToolAnnotations` kwargs switched from camelCase to snake_case
      (`read_only_hint` etc.) — v2 accepts both via alias, snake_case
      matches the SDK's own attribute names going forward.
- [x] Single-tenant enforcement: `session_path` stripped from every tool's
      public schema in `tool_metadata.py` (`_HIDDEN_PARAMETERS`). Verified
      against the *live* registered tool set, not just the functions that
      were hand-edited — all 127 tools, zero leaks.
- [x] `groups/auth.py` rewritten: `create_session` / `save_session` /
      `load_session` no longer take a path argument at all (always use the
      one configured path); added `auth_login` and `auth_status`.
- [x] `auth_runtime.py`: env-var-driven login (`MONARCH_EMAIL` /
      `MONARCH_PASSWORD` / `MONARCH_TOTP_SECRET`), with TOTP-seed-based
      automatic MFA retry via `pyotp`. Best-effort startup hook in
      `server.py::main()`.
- [x] Transport selection (`MCP_TRANSPORT` / `MCP_HOST` / `MCP_PORT`) for
      obot's two deployment models — stdio (command/uvx) and
      streamable-http (Docker). `config.transport()` validates the env var
      and raises a clear error on typos rather than an opaque SDK error.
- [x] Test suite: rewrote `tests/test_server.py` and
      `tests/groups/test_auth.py` for the v2 API (snake_case fields,
      `input_schema` not `inputSchema`, public `mcp.call_tool()` instead of
      the private `_tool_manager`); added `tests/test_auth_runtime.py`
      (TOTP retry, wrong-code, no-seed-configured, missing-credentials
      branches) and config env-var tests. 57/57 passing.
- [x] `ruff check` / `ruff format` clean. `mypy --strict` clean on the 5
      files this fork authored or substantially changed (see "Known gaps"
      for what that excludes).
- [x] Dockerfile, defaulting to `streamable-http` + `EXPOSE 8000` for
      obot's Docker deployment model, non-root user, `/data` volume for
      the session file.

## How things were verified

Not aspirational — each of these was actually run during this session:

- `uv pip install .` / `uv sync` succeed from a clean venv.
- The `monarch-mcp` console script starts cleanly on stdio (no traceback,
  correct "no credentials configured" log line).
- The streamable-http transport binds to a port and answers a real MCP
  `initialize` JSON-RPC request with a correct capabilities response —
  tested both directly and via a Dockerfile-equivalent build simulated
  locally (no Docker daemon was available in the sandbox this was built
  in; the steps were run by hand in the same order the Dockerfile runs
  them, not skipped).
- `perform_login`'s TOTP branch computes a real code via `pyotp` against
  the RFC 6238 test seed and correctly retries `create_session` with it
  after the first call raises `MfaRequiredError`.
- `mcp.list_tools()` on the live, fully-constructed server confirms 127
  tools (125 inherited + `auth_login` + `auth_status`), zero of which
  expose `session_path`.

## Known gaps / deliberately deferred

- **Not pushed to a git remote.** This was built and verified in a local
  checkout. Push it wherever you want it to live, then update the README's
  "Running it" section (the `uvx --from git+...` URL is a placeholder).
- **`mypy --strict` was scoped to the 5 files this fork touched**
  (`auth_runtime.py`, `config.py`, `server.py`, `groups/auth.py`,
  `tool_metadata.py`), not the 13 inherited group modules or
  `schemas.py`/`output.py`/`serialization.py`/`converters.py`. Those came
  from upstream as-is; running strict mypy across the whole tree is a
  reasonable next step if you want the whole codebase held to that bar,
  but budget time for it — there's a real behavioral trap in there (see
  next bullet).
- **`schemas.py` intentionally does NOT use PEP 695 `type X = ...`
  aliases**, even though `ruff --fix` will offer to convert them and it
  looks like a harmless modernization. It isn't: a `type` statement
  produces a lazy `TypeAliasType`, and Pydantic does not inline that into a
  tool's JSON Schema `enum` the way it inlines a plain
  `X: TypeAlias = Literal[...]` assignment — every affected tool silently
  lost its `enum` constraint when this was tried. It's suppressed via a
  `per-file-ignores` entry in `pyproject.toml` with the reasoning inline.
  If a future Pydantic version changes this, the suppression can go — but
  verify against `test_server_exposes_typed_input_schemas` first, don't
  just trust ruff.
- **TOTP secret handling is minimal.** It's read from an env var and used
  in-memory; nothing here encrypts it at rest beyond whatever obot/Docker
  secret handling you configure. If that's not sufficient for your threat
  model, consider a secrets manager reference instead of a raw env var —
  that's a deployment-layer decision, not something this fork enforces.
- **Email-code MFA has no automation path.** Only authenticator-app
  (TOTP-seed) MFA can be fully unattended. If Monarch challenges with an
  emailed code instead, `auth_login` still works but needs a human to
  relay the code via its `mfa_code` argument each time.
- **No re-auth-on-401 wrapper around the 125 inherited tools.** If a
  session expires mid-use, individual tool calls will fail with whatever
  error `monarch-api2` raises (surfaces as an MCP tool execution error,
  not a silent `is_error` result — v2 propagates handler exceptions
  directly, unlike v1). `auth_status` can confirm this; nothing currently
  auto-retries a failed call after a fresh login. Worth adding if expired
  sessions turn out to be a frequent annoyance in practice.
- **List-shaped tool results changed shape under v2**, independent of
  anything this fork did: MCPServer v2 emits one `TextContent` block per
  list element instead of one block containing a JSON array (v1's
  behavior, going by how upstream's now-removed `_tool_manager` test
  double assumed a single array). MCP clients generally handle multiple
  content blocks fine, but if something downstream assumes "one JSON
  blob per tool call," it'll need to handle multiple blocks instead.
- **No CI configured.** `pyproject.toml` has ruff/mypy/pytest ready to
  run; wiring them into GitHub Actions (or wherever this ends up hosted)
  wasn't part of this session's scope.

## Possible next steps (not started)

- Re-auth-on-401 wrapper (see above) if it turns out to matter in
  practice, rather than pre-building it speculatively.
- Extend `mypy --strict` to the rest of the tree.
- CI workflow (lint + typecheck + test on push).
- Decide on and document a secrets-manager story for
  `MONARCH_PASSWORD`/`MONARCH_TOTP_SECRET` if the plain-env-var approach
  isn't sufficient for how this gets deployed.
