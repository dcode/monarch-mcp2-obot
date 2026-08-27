from __future__ import annotations

import os
from pathlib import Path
from typing import Literal, get_args

Transport = Literal["stdio", "sse", "streamable-http"]
_TRANSPORTS: tuple[Transport, ...] = get_args(Transport)

CONFIG_DIR_ENV = "MONARCH_CONFIG_DIR"
SESSION_PATH_ENV = "MONARCH_SESSION_PATH"

#: Credentials for the automatic login flow (auth_runtime.py). This server is
#: single-tenant by design: exactly one Monarch account per deployment,
#: configured once via environment variables (obot's single-user MCP server
#: model injects these as the "required"/"sensitive" fields an admin fills
#: in when enabling the server) rather than passed per tool call.
EMAIL_ENV = "MONARCH_EMAIL"
PASSWORD_ENV = "MONARCH_PASSWORD"
#: Base32 TOTP seed (the same secret an authenticator app would be enrolled
#: with) for accounts with authenticator-app MFA. Optional: without it, MFA
#: challenges still surface through the auth_login tool for a human to solve
#: interactively, or a session file can be provisioned out of band.
TOTP_SECRET_ENV = "MONARCH_TOTP_SECRET"

#: Transport selection for obot. Command/uvx-based MCP servers in obot talk
#: over stdio; obot's Docker-based deployment model instead expects a port
#: and an HTTP/SSE (streamable-http) endpoint. Default to stdio so running
#: the console script directly (uvx, a local venv) keeps working unchanged;
#: the Docker image overrides this via MCP_TRANSPORT=streamable-http.
TRANSPORT_ENV = "MCP_TRANSPORT"
HOST_ENV = "MCP_HOST"
PORT_ENV = "MCP_PORT"

DEFAULT_TRANSPORT = "stdio"
DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8000


def config_dir() -> Path:
    configured = os.environ.get(CONFIG_DIR_ENV)
    if configured:
        return Path(configured).expanduser()
    return Path.home() / ".config" / "monarch"


def default_session_path() -> Path:
    configured = os.environ.get(SESSION_PATH_ENV)
    if configured:
        return Path(configured).expanduser()
    return config_dir() / "session.json"


def resolve_session_path(session_path: str | Path | None = None) -> Path:
    if session_path is None:
        return default_session_path()
    return Path(session_path).expanduser()


def configured_email() -> str | None:
    return os.environ.get(EMAIL_ENV) or None


def configured_password() -> str | None:
    return os.environ.get(PASSWORD_ENV) or None


def configured_totp_secret() -> str | None:
    return os.environ.get(TOTP_SECRET_ENV) or None


def transport() -> Transport:
    value = os.environ.get(TRANSPORT_ENV, DEFAULT_TRANSPORT)
    if value not in _TRANSPORTS:
        raise ValueError(
            f"{TRANSPORT_ENV}={value!r} is not a supported MCP transport; "
            f"use one of {', '.join(_TRANSPORTS)}."
        )
    return value


def host() -> str:
    return os.environ.get(HOST_ENV, DEFAULT_HOST)


def port() -> int:
    return int(os.environ.get(PORT_ENV, str(DEFAULT_PORT)))
