# Installation

obot supports MCP servers two ways, and this project supports both.

## obot, command/uvx-based (stdio)

```bash
uvx --from git+https://github.com/dcode/monarch-mcp2-obot monarch-mcp
```

Point obot's command-based MCP server configuration at that command. Configure
`MONARCH_EMAIL` / `MONARCH_PASSWORD` (and, if your account uses authenticator-app MFA,
`MONARCH_TOTP_SECRET`) as the server's environment — see [Configuration](configuration.md).

## obot, Docker-based (streamable-http)

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

Point obot's Docker-based MCP server config at this container's `streamable-http` endpoint on port
8000. Session state lives in the `monarch-session` volume, so it survives container restarts and
re-deploys without a re-login.

The image runs as a non-root `monarch` user and defaults `MCP_TRANSPORT` to `streamable-http` —
obot's Docker deployment model expects a port and an HTTP/SSE endpoint, not stdio.

## Local development (stdio, no Docker)

```bash
uv sync --extra dev
uv run monarch-mcp
```

See [Development](development.md) for running the test suite, linters, and type checker.

## Installing a specific version

Until a PyPI release is possible (see below), a released wheel/sdist is available from each
[GitHub release](https://github.com/dcode/monarch-mcp2-obot/releases) as a downloadable asset,
giving semantic-versioned tags and immutable, content-addressed artifacts without needing PyPI:

```bash
pip install https://github.com/dcode/monarch-mcp2-obot/releases/download/vX.Y.Z/monarch_mcp2_obot-X.Y.Z-py3-none-any.whl
```

## Publishing to PyPI

This package is prepared for PyPI (classifiers, license, URLs, a `py.typed` marker) but currently
**cannot** be uploaded there as-is: it depends on `monarch-api2` via a direct GitHub reference (no
PyPI release of that package exists yet), and PyPI's upload validation rejects any package whose
metadata contains a direct/VCS dependency. `uv build` still produces installable wheels/sdists
locally or in CI. The `publish` GitHub Actions workflow has two independent jobs:

- **Release**: on a pushed `vX.Y.Z` tag, builds the wheel/sdist and turns the tag into a GitHub
  release with those files attached — the primary distribution path for now. GitHub releases are
  immutable once published (assets can only be uploaded *before* publishing), so this creates the
  release as a draft with the files already attached, then publishes it — never reacts to an
  already-published release, since by then it's too late to attach anything.
- **Publish to PyPI** via [Trusted Publishing](https://docs.pypi.org/trusted-publishers/) (OIDC,
  no stored token) against the `pypi` environment — `workflow_dispatch` only, not automatic on a
  tag push, since it will fail until `monarch-api2` has its own PyPI release to depend on instead.
  Re-pin the dependency, then consider making this automatic too.
