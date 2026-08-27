"""Automatic, headless login for this single-tenant deployment.

Designed for obot: the operator configures MONARCH_EMAIL / MONARCH_PASSWORD
(and, optionally, MONARCH_TOTP_SECRET) once as the server's environment —
obot's single-user MCP server model presents these as the "required" /
"sensitive" fields an admin fills in when enabling the server — and the
server logs itself in without any further interaction. No browser, no OS
keyring, no copy-pasting a 6-digit code: if the account's MFA method is a
TOTP authenticator app, MONARCH_TOTP_SECRET is the same base32 seed that
app was enrolled with, and pyotp computes the current code at the moment
it's needed.

If MONARCH_TOTP_SECRET isn't set and the account still challenges for MFA,
login stops with a clear, actionable error rather than guessing — call the
`auth_login` tool with an explicit `mfa_code` once you have one, or set the
env var so this becomes fully unattended going forward.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import pyotp
from monarch_api import (
    AuthSession,
    MfaRequiredError,
    MonarchAuthError,
    create_session,
    load_session,
)

from monarch_mcp import config

logger = logging.getLogger(__name__)


class LoginError(RuntimeError):
    """Raised when automatic login cannot complete and needs operator input."""


@dataclass(frozen=True, slots=True)
class LoginResult:
    session: AuthSession
    session_path: Path
    used_totp: bool


def _totp_code(seed: str) -> str:
    # `pyotp.TOTP` accepts base32 seeds with or without spaces/dashes as
    # commonly displayed by authenticator enrollment screens.
    cleaned = seed.replace(" ", "").replace("-", "")
    return pyotp.TOTP(cleaned).now()


def perform_login(
    *,
    email: str | None = None,
    password: str | None = None,
    totp_secret: str | None = None,
    mfa_code: str | None = None,
    session_path: str | Path | None = None,
) -> LoginResult:
    """Log in to Monarch and persist the resulting session.

    Falls back to the MONARCH_EMAIL / MONARCH_PASSWORD / MONARCH_TOTP_SECRET
    environment variables for any argument left as None, matching this
    server's single-tenant, env-configured design. Raises LoginError with a
    specific, actionable message on any failure — including MFA required
    with no code or seed available — rather than a bare exception from the
    underlying API client.
    """
    email = email or config.configured_email()
    password = password or config.configured_password()
    totp_secret = totp_secret or config.configured_totp_secret()
    resolved_path = config.resolve_session_path(session_path)

    if not email or not password:
        raise LoginError(
            "No credentials available. Set MONARCH_EMAIL and MONARCH_PASSWORD "
            "(and, if the account uses an authenticator app, MONARCH_TOTP_SECRET) "
            "in the server's environment, or call auth_login with email/password "
            "explicitly."
        )

    used_totp = False
    try:
        session = create_session(
            email,
            password,
            mfa_code=mfa_code,
            session_path=resolved_path,
        )
    except MfaRequiredError:
        if mfa_code:
            # An explicit but wrong/expired code was already tried above.
            raise LoginError(
                "Monarch rejected the MFA code. Codes are time-limited — "
                "try again with a fresh one."
            ) from None
        if not totp_secret:
            raise LoginError(
                "Monarch requires an MFA code and no MONARCH_TOTP_SECRET is "
                "configured. Set it to the account's authenticator seed for "
                "unattended login, or call auth_login again with an explicit "
                "mfa_code from your authenticator app."
            ) from None
        used_totp = True
        try:
            session = create_session(
                email,
                password,
                mfa_code=_totp_code(totp_secret),
                session_path=resolved_path,
            )
        except MfaRequiredError as exc:
            raise LoginError(
                "Monarch rejected the TOTP code generated from MONARCH_TOTP_SECRET. "
                "Double-check the seed was copied correctly and that the server's "
                "clock is accurate — TOTP codes are time-window based."
            ) from exc
        except MonarchAuthError as exc:
            raise LoginError(f"Monarch login failed after TOTP: {exc}") from exc
    except MonarchAuthError as exc:
        raise LoginError(f"Monarch login failed: {exc}") from exc

    logger.info("Monarch login succeeded (session saved to %s)", resolved_path)
    return LoginResult(session=session, session_path=resolved_path, used_totp=used_totp)


def ensure_authenticated(*, session_path: str | Path | None = None) -> LoginResult | None:
    """Best-effort startup hook: reuse an existing session, or log in if
    credentials are configured. Never raises — a failure here should not
    prevent the server from starting, since auth_login/auth_status remain
    available as tools to diagnose and retry. Returns None if nothing was
    done (a valid session already exists, or no credentials are configured
    to attempt a fresh login).
    """
    resolved_path = config.resolve_session_path(session_path)
    if resolved_path.exists():
        try:
            load_session(resolved_path)
            logger.info("Reusing existing Monarch session at %s", resolved_path)
            return None
        except Exception:  # noqa: BLE001 - corrupt/unreadable session file
            logger.warning(
                "Existing session file at %s is unreadable; attempting fresh login",
                resolved_path,
            )

    if not config.configured_email() or not config.configured_password():
        logger.info(
            "No MONARCH_EMAIL/MONARCH_PASSWORD configured; skipping startup login. "
            "Call the auth_login tool once credentials or a session file are available."
        )
        return None

    try:
        return perform_login(session_path=resolved_path)
    except LoginError as exc:
        logger.warning("Startup login did not complete: %s", exc)
        return None
