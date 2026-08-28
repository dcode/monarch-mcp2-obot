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

## Status: done in this session (2026-08-27 — professionalization pass)

Also verified by actually running things — mypy/ruff/pytest output pasted
into this session, `zensical build --clean --strict` run against the docs,
`pre-commit run --all-files` run against the whole repo.

- [x] **`mypy --strict` extended to the entire `src/` tree** (26 files, up
      from the 5 this fork originally touched). Fixed the real typing gaps
      this surfaced rather than carving out more exclusions:
      `converters.py`'s filter/enum helpers now take a proper
      `Mapping[str, Any] | BaseModel` union (`InputMapping`) instead of an
      untyped `data`, `output.py::details()` takes `Callable[[Any], Any]`
      instead of a too-narrow `dict`-only signature, `report_groups` takes
      `Sequence[str]` instead of `list[str]` (the original was invariant
      and rejected `list[Literal[...]]`), and a couple of missing return
      annotations (`review_status_`) got filled in. `monarch_api.*`'s
      missing-stubs override was widened from `monarch_api` to
      `monarch_api.*` so it actually covers the submodules being imported.
- [x] **Re-auth-on-401 wrapper**, addressing the gap noted below:
      `reauth.py::call_with_reauth` wraps every non-`auth_*` tool call.
      Since monarch-api2 doesn't preserve HTTP status codes on failures
      (see its `functions/common.py::_parse_response` — every 4xx/5xx
      becomes a bare `MonarchError` with only the parsed message), this
      matches the error message against known expired-session wording
      rather than a status code. One retry max; only fires when
      `MONARCH_EMAIL`/`MONARCH_PASSWORD` are configured; never masks a
      genuine error. See docs/authentication.md for the exact rules.
- [x] **`_FILE`-suffixed secrets support**
      (`MONARCH_PASSWORD_FILE`/`MONARCH_TOTP_SECRET_FILE`) in `config.py`,
      following the `POSTGRES_PASSWORD_FILE`-style convention Docker's
      official images use — lets a deployment mount a secret as a file
      (Docker/Kubernetes secret mounts) instead of putting the value
      directly in the process environment. Partial answer to the "TOTP
      secret handling is minimal" gap below; still no at-rest encryption
      layered on top by this fork itself, by design (a deployment-layer
      concern, not this server's).
- [x] **GitHub Actions**: `lint.yml` (ruff check + format + mypy),
      `test.yml` (pytest + coverage, 3.12/3.13 matrix), `docs.yml` (zensical
      build → GitHub Pages on push to `main`), `publish.yml` (build, then two
      independent paths: attach the wheel/sdist to the GitHub release
      automatically on `release: published` — the primary distribution path
      for now — and, separately, PyPI publish via
      [Trusted Publishing](https://docs.pypi.org/trusted-publishers/) against
      the `pypi` environment on manual `workflow_dispatch` only; see
      "Publishing to PyPI" below for why PyPI isn't wired to the release
      trigger yet).
- [x] **Pre-commit** (`.pre-commit-config.yaml`): the pre-commit-hooks
      hygiene set, ruff + ruff-format, and local mypy/pytest hooks —
      mirrors CI so failures surface before a push, not after.
- [x] **Docs site** (Zensical, `zensical.toml` + `docs/`): Overview,
      Installation, Configuration, Authentication, Tools, Development.
      Builds clean under `zensical build --clean --strict` (zero warnings).
      Deployed via `docs.yml` to GitHub Pages.
- [x] **`pyproject.toml` filled out for PyPI**: `dynamic` version sourced
      from `__init__.py` (single source of truth, was duplicated before),
      `authors`, `keywords`, full `classifiers`, `project.urls`
      (Homepage/Documentation/Repository/Issues/Changelog), a `docs` extra,
      `py.typed` marker added to the package. See "Publishing to PyPI"
      below for the one thing that still blocks an actual upload.
- [x] **Coverage gate** added (`pytest-cov`, `[tool.coverage]` in
      `pyproject.toml`, `fail_under = 78`, current baseline ~80%) — catches
      regressions without pretending the inherited-code baseline is 100%.
- [x] **`LICENSE` updated** with a second copyright line for this fork's
      own additions; **`NOTICE.md` added**, spelling out exactly which
      pieces come from upstream (Erik Rubstein) vs. this fork (Derek
      Ditch).
- [x] Pushed to a real remote: `https://github.com/dcode/monarch-mcp2-obot`
      (the README's `uvx --from git+...` placeholder is now the real URL).

## Distribution: GitHub Releases for now, PyPI later

The metadata is ready, but an actual `pypi-publish` will fail: this project
depends on `monarch-api2` via a direct GitHub reference (`@ git+https://...`
in `dependencies`, `allow-direct-references = true` in
`[tool.hatch.metadata]`), because `monarch-api2` has no PyPI release to
depend on instead. PyPI's upload validation rejects any package whose
metadata contains a direct/VCS `Requires-Dist` line — this isn't a bug in
this fork's setup, it's PyPI's policy.

A `monarch-api` package also exists on PyPI under the same author
(erikrubstein) and the same `monarch_api` import name, but it's not a
drop-in replacement: a full audit of this fork's 127 tools against its
actual client surface found ~28% coverage — entire groups this fork
exposes (receipts, most of budget, most of goals, categories CRUD, tags
CRUD, investment holdings, saved reports, transaction splits) have no
equivalent there. Not pursuing that path unless/until it changes; a GitHub
issue was opened upstream to ask about the relationship between the two
packages.

So for now, **GitHub Releases are the primary distribution path**:
`publish.yml`'s `attach-release-assets` job builds the wheel/sdist and
attaches them to the release automatically on `release: published`, giving
semantic-versioned tags and immutable, downloadable artifacts without
depending on PyPI at all — see "Releases" in the README. The `publish` job
(actual PyPI upload via Trusted Publishing) stays on manual
`workflow_dispatch` only, so it doesn't silently fail on every tagged
release. Two ways to actually unblock a PyPI upload, neither of which is
this fork's call to make unilaterally: get `monarch-api2` published to
PyPI (upstream, `erikrubstein/monarch-api2`) and re-pin the dependency to
that; or vendor/fork `monarch-api2` under this project's own namespace and
publish that instead. Once either happens, re-pin the dependency, drop
`allow-direct-references`, and switch the `publish` job back to the
`release: published` trigger.

## Known gaps / deliberately deferred

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
- **TOTP secret handling has no at-rest encryption.** The `_FILE` variants
  above avoid putting the raw value in the process environment, but
  whatever's on the other end of that file (or the env var, if you're not
  using `_FILE`) is still this fork's problem only up to "read it and use
  it in-memory" — actual secrets-manager integration (Vault, age/sops,
  cloud KMS-backed mounts, ...) is a deployment-layer decision this fork
  deliberately doesn't own.
- **Email-code MFA has no automation path.** Only authenticator-app
  (TOTP-seed) MFA can be fully unattended. If Monarch challenges with an
  emailed code instead, `auth_login` still works but needs a human to
  relay the code via its `mfa_code` argument each time.
- **The re-auth-on-401 wrapper is message-based, not status-code-based**
  (see "Status: done in this session" above for why — monarch-api2 doesn't
  preserve status codes). An unusually-worded 401 from Monarch's API could
  in principle not match `reauth.py`'s known-marker list and fall through
  to the old plain-error behavior. Widen `_EXPIRED_SESSION_MARKERS` if a
  real 401 message is observed that doesn't match.
- **List-shaped tool results changed shape under v2**, independent of
  anything this fork did: MCPServer v2 emits one `TextContent` block per
  list element instead of one block containing a JSON array (v1's
  behavior, going by how upstream's now-removed `_tool_manager` test
  double assumed a single array). MCP clients generally handle multiple
  content blocks fine, but if something downstream assumes "one JSON
  blob per tool call," it'll need to handle multiple blocks instead.
- **Coverage floor is 78%, not 100%.** The inherited group modules and
  `output.py`'s long tail of per-tool summary shapers weren't written with
  100%-coverage testing in mind; closing that gap is real test-writing
  effort, not a config change.
- **PyPI publish is blocked** on `monarch-api2` getting its own PyPI
  release — see "Publishing to PyPI" above.

## Possible next steps (not started)

- Close the coverage gap on `output.py` (55% today, the biggest single
  contributor to the 80%-not-100% baseline) and the inherited group
  modules, then raise `fail_under` to match.
- If `monarch-api2` gets a PyPI release, re-pin `dependencies` to it,
  drop `allow-direct-references`, and switch `publish.yml` back to
  `release: published`.
- If a real Monarch 401 message is ever observed that
  `reauth.py::_EXPIRED_SESSION_MARKERS` doesn't match, add it — this is
  meant to grow from observed behavior, not be guessed exhaustively
  up front.
- A secrets-manager integration beyond the `_FILE` convention (Vault,
  cloud KMS, ...) if plain file-mounted secrets aren't sufficient for a
  given deployment's threat model.
