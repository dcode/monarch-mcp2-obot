from __future__ import annotations

from typing import Any

from mcp.server.mcpserver import MCPServer
from monarch_api import AuthSession, MonarchError
from monarch_api import create_session as api_create_session
from monarch_api import get_current_user as api_get_current_user
from monarch_api import load_session as api_load_session
from monarch_api import save_session as api_save_session

from monarch_mcp.auth_runtime import LoginError, perform_login
from monarch_mcp.config import resolve_session_path
from monarch_mcp.schemas import AuthSessionInput
from monarch_mcp.serialization import to_jsonable
from monarch_mcp.tool_metadata import register_api_tool

REDACTED_TOKEN = "<redacted>"


def session_to_dict(
    session: AuthSession,
    *,
    include_token: bool = False,
) -> dict[str, Any]:
    data = session.to_dict()
    if not include_token:
        data["token"] = REDACTED_TOKEN
    return to_jsonable(data)  # type: ignore[return-value]


def session_from_dict(data: AuthSessionInput | dict[str, Any]) -> AuthSession:
    if isinstance(data, AuthSessionInput):
        data = data.model_dump()
    return AuthSession.from_dict(data)


def create_session(
    email: str,
    password: str,
    *,
    mfa_code: str | None = None,
    trusted_device: bool = True,
    include_token: bool = False,
) -> dict[str, Any]:
    """Log in with an email/password (and, if challenged, an MFA code) and
    save the result to this deployment's configured session file.

    Prefer `auth_login` for day-to-day use: it reads MONARCH_EMAIL /
    MONARCH_PASSWORD / MONARCH_TOTP_SECRET from the server's environment and
    handles the MFA retry automatically. This tool remains for a fully
    manual, one-shot login (e.g. from a fresh authenticator code) without
    touching server configuration.
    """
    session = api_create_session(
        email,
        password,
        mfa_code=mfa_code,
        trusted_device=trusted_device,
        session_path=resolve_session_path(),
    )
    return session_to_dict(session, include_token=include_token)


def save_session(session: AuthSessionInput) -> None:
    """Install a session file produced elsewhere (e.g. copied from another
    trusted monarch-api2-based tool) as this deployment's active session."""
    api_save_session(session_from_dict(session), resolve_session_path())


def load_session(*, include_token: bool = False) -> dict[str, Any]:
    session = api_load_session(resolve_session_path())
    return session_to_dict(session, include_token=include_token)


def auth_login(
    *,
    email: str | None = None,
    password: str | None = None,
    totp_secret: str | None = None,
    mfa_code: str | None = None,
) -> dict[str, Any]:
    """Log in to Monarch, the way a human operating obot would use it: no
    arguments needed if MONARCH_EMAIL / MONARCH_PASSWORD (and, for
    authenticator-app MFA, MONARCH_TOTP_SECRET) are already configured on
    the server — this just runs the login and reports the outcome. Pass
    email/password/totp_secret explicitly to log in with different
    credentials without changing server configuration, or pass mfa_code
    directly if you're reading a code off an authenticator app by hand
    instead of configuring a TOTP seed.
    """
    try:
        result = perform_login(
            email=email,
            password=password,
            totp_secret=totp_secret,
            mfa_code=mfa_code,
        )
    except LoginError as exc:
        return {"success": False, "error": str(exc)}

    return {
        "success": True,
        "session_path": str(result.session_path),
        "used_totp": result.used_totp,
    }


def auth_status(*, validate: bool = True) -> dict[str, Any]:
    """Report whether this deployment has a usable Monarch session, without
    ever returning the session token. With validate=True (the default) this
    makes one lightweight API call to confirm the session is actually
    accepted by Monarch, not just present on disk — a session file can exist
    and still be expired or revoked.
    """
    path = resolve_session_path()
    if not path.exists():
        return {"session_exists": False, "session_path": str(path), "valid": None}

    try:
        session = api_load_session(path)
    except Exception as exc:  # noqa: BLE001 - unreadable/corrupt file
        return {
            "session_exists": True,
            "session_path": str(path),
            "valid": False,
            "error": f"Session file is unreadable: {exc}",
        }

    result: dict[str, Any] = {"session_exists": True, "session_path": str(path)}
    if not validate:
        result["valid"] = None
        return result

    try:
        user = api_get_current_user(session)
    except MonarchError as exc:
        result["valid"] = False
        result["error"] = str(exc)
        return result

    result["valid"] = True
    result["user"] = to_jsonable(user)
    return result


def register(mcp: MCPServer) -> None:
    register_api_tool(mcp, "auth", "create_session", create_session)
    register_api_tool(mcp, "auth", "save_session", save_session)
    register_api_tool(mcp, "auth", "load_session", load_session)
    register_api_tool(mcp, "auth", "login", auth_login)
    register_api_tool(mcp, "auth", "status", auth_status)
