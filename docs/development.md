# Development

```bash
uv sync --extra dev
```

## Tests

```bash
uv run pytest --cov=src --cov-report=term-missing
```

CI enforces a coverage floor (`fail_under` in `pyproject.toml`'s `[tool.coverage.report]`) set below
the current baseline — see the comment there for why 100% isn't the target yet.

## Lint and format

```bash
uv run ruff check .
uv run ruff format --check .   # add --check-less: `ruff format .` to apply
```

## Type checking

```bash
uv run mypy src
```

`mypy --strict` runs across the entire `src/` tree, including the 13 group modules inherited
unchanged from upstream — not just the files this fork authored.

## Pre-commit

```bash
uv run pre-commit install
uv run pre-commit run --all-files
```

Runs the same ruff/mypy/pytest checks as CI, plus basic hygiene hooks (trailing whitespace,
end-of-file, YAML/TOML validity, merge-conflict markers), before each commit.

## Building the docs locally

```bash
uv sync --extra docs
uv run zensical serve
```

`zensical serve` builds and serves the site with live reload at `http://127.0.0.1:8000` by default.
`zensical build --clean` (used by the `docs` GitHub Actions workflow) produces the static site under
`site/`.

## Project layout

- `src/monarch_mcp/server.py` — `MCPServer` construction, transport selection, startup login.
- `src/monarch_mcp/config.py` — every environment variable this server reads.
- `src/monarch_mcp/auth_runtime.py` — the automatic login flow (env-configured credentials, TOTP MFA
  retry).
- `src/monarch_mcp/reauth.py` — the re-login-and-retry wrapper applied to every tool call.
- `src/monarch_mcp/tool_metadata.py` — tool registration: naming, descriptions, annotations,
  `output_mode`/`fields`, the single-tenant `session_path` hiding.
- `src/monarch_mcp/groups/` — one module per tool group (14 inherited from upstream, plus `auth.py`
  rewritten for this fork).
- `src/monarch_mcp/output.py`, `serialization.py`, `converters.py`, `schemas.py` — response shaping,
  JSON-safe serialization, filter/enum conversion, and Pydantic input models — all inherited from
  upstream.
- `tests/` — mirrors `src/monarch_mcp/`, plus `tests/groups/` for the per-group tool tests.

See `ROADMAP.md` in the repository root for what's done, what's a known gap, and what's a deliberately
deferred next step.
