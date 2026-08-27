# Configuration

Everything is configured via environment variables — there is no config file, and no per-tool-call
argument can override any of this (see [Tools](tools.md#single-tenant-on-purpose)).

## Credentials

| Variable | Purpose | Default |
| --- | --- | --- |
| `MONARCH_EMAIL` | Monarch account email, for automatic login | — |
| `MONARCH_PASSWORD` | Monarch account password | — |
| `MONARCH_TOTP_SECRET` | Base32 authenticator-app seed, for automatic MFA | — |

The server attempts login automatically at startup if `MONARCH_EMAIL`/`MONARCH_PASSWORD` are
configured — best-effort and non-fatal, so a wrong password or a down network doesn't prevent the
server from starting. `auth_status` and `auth_login` remain available to diagnose and retry. See
[Authentication](authentication.md) for the full login flow, including TOTP MFA and what happens
when a session expires mid-use.

### Secrets from files (`_FILE` variants)

Putting a secret's *value* directly in the process environment means it can leak through
`docker inspect`, `/proc/<pid>/environ`, or a crash dump that captures env state. For deployments
that mount secrets as files instead (Docker/Kubernetes secrets, an age/sops-decrypted path, etc.),
point one of these at the file instead:

| Variable | Reads the secret from |
| --- | --- |
| `MONARCH_PASSWORD_FILE` | A file containing the password |
| `MONARCH_TOTP_SECRET_FILE` | A file containing the TOTP seed |

If both a `_FILE` variable and its plain counterpart are set, the file wins. The file's contents are
stripped of surrounding whitespace; an empty file raises a clear startup error rather than silently
treating the credential as unset.

!!! tip "obot's own secret handling"
    obot's single-user MCP server model already marks fields like `MONARCH_PASSWORD` /
    `MONARCH_TOTP_SECRET` as "sensitive" when an admin configures the server, which covers the most
    common obot deployment path. The `_FILE` variables above are for deployments layering obot on top
    of Docker/Kubernetes secret mounts, or otherwise preferring not to put secret values directly in
    the container's environment.

## Session storage

| Variable | Purpose | Default |
| --- | --- | --- |
| `MONARCH_SESSION_PATH` | Exact path to the session file | `$MONARCH_CONFIG_DIR/session.json` |
| `MONARCH_CONFIG_DIR` | Directory for the default session path | `~/.config/monarch` |

Mount a persistent volume at whichever of these resolves to your session file's directory (the
Docker image already does this at `/data`, via `MONARCH_SESSION_PATH=/data/session.json`) so a
container restart or redeploy doesn't force a re-login.

## Transport

| Variable | Purpose | Default |
| --- | --- | --- |
| `MCP_TRANSPORT` | `stdio` \| `sse` \| `streamable-http` | `stdio` (the Dockerfile overrides this to `streamable-http`) |
| `MCP_HOST` | Bind host for `sse`/`streamable-http` | `0.0.0.0` |
| `MCP_PORT` | Bind port for `sse`/`streamable-http` | `8000` |

obot supports MCP servers two ways: command/`uvx`-based (stdio) and Docker-based (a port plus a
streamable-http endpoint). `MCP_TRANSPORT` picks between them — see [Installation](installation.md)
for both deployment paths.
