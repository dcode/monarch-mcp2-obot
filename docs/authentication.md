# Authentication

## `auth_login`, `auth_status`

Two tools on top of upstream's `auth_create_session` / `auth_save_session` / `auth_load_session`
(which still work, for a fully manual one-shot login):

- **`auth_login`** — no arguments needed if the server's environment has `MONARCH_EMAIL` /
  `MONARCH_PASSWORD` (and, for authenticator-app MFA, `MONARCH_TOTP_SECRET`) configured. Handles an
  MFA challenge automatically by computing the current code from the seed. Pass `email` / `password`
  / `totp_secret` / `mfa_code` explicitly to override for a one-off login without touching server
  config.
- **`auth_status`** — reports whether a session exists and is currently valid (one lightweight API
  call by default), without ever returning the session token.

The server also attempts this login automatically at startup if credentials are configured —
best-effort, non-fatal, so a wrong password or a down network doesn't prevent the server from
starting; `auth_status` and `auth_login` remain available to diagnose and retry.

**TOTP seed**: the same base32 secret an authenticator app would be enrolled with (what you'd scan
as a QR code). Monarch shows this once when you enable authenticator-app MFA — save it there, or
you'll need to disable and re-enable MFA to get a fresh one. This only applies if your account's MFA
method is an authenticator app; email-code MFA isn't automatable this way (there's no seed to compute
a code from) and still needs a human to relay a fresh code via `auth_login`'s `mfa_code` argument.

## Automatic re-login on session expiry

If a saved session expires mid-use, individual tool calls used to fail outright with whatever error
`monarch-api2` raised, leaving the caller to notice and manually call `auth_login` again. Every tool
call now goes through a re-login retry: if a call fails with an error that looks like an expired or
invalid session (matched against the wording Monarch's API is known to return for a 401 — e.g.
"invalid token", "token has expired", "authentication credentials were not provided"), and this
deployment has `MONARCH_EMAIL`/`MONARCH_PASSWORD` configured, the server performs one fresh login and
retries the call once before giving up.

This is deliberately narrow:

- Only tool calls **outside** the `auth_*` group are retried — retrying a login failure by attempting
  another login would either recurse pointlessly or mask the real error an operator needs to see
  (e.g. a wrong password).
- Only errors that *look like* an expired session trigger a retry. `monarch-api2` doesn't preserve
  the HTTP status code on failures (every 4xx/5xx becomes a bare exception carrying only the parsed
  error message), so this is message-based pattern matching, not a guarantee — a genuine validation
  or not-found error won't trigger a pointless re-login, but an unusually-worded 401 from Monarch's
  API could in principle slip past the match and still surface as a plain error, exactly as it always
  did.
- At most one retry per call. If the re-login itself fails (e.g. credentials are stale), or the
  retried call fails again, the original error is raised — this never turns a real failure into a
  silent no-op.

If your account's session is expiring more often than you'd expect, `auth_status` (with
`validate=True`, the default) is the fastest way to confirm whether the *stored* session is valid
right now, independent of any particular tool call.

## Single-tenant, on purpose

`session_path` exists on every underlying function (a monarch-api2 convention) but is stripped from
every tool's public schema before it's exposed to an MCP client. One deployment, one Monarch account,
one session file, chosen once via `MONARCH_SESSION_PATH` / `MONARCH_CONFIG_DIR`. This isn't just a
config default: no tool call can override it per-request, by design, even if a client sent one
anyway.
