"""Best-effort re-authentication retry for expired Monarch sessions.

monarch-api2 does not preserve the HTTP status code on request failures --
every 4xx/5xx response from Monarch is raised as a bare `MonarchError`
carrying only the parsed error message (see monarch-api2's
`functions/common.py::_parse_response`). That means this fork cannot
distinguish "session expired" from "bad request"/"not found" by exception
type alone; `looks_like_expired_session` instead matches the error message
against the wording Monarch's API is known to return for an invalid/expired
token.

When a tool call fails with what looks like an expired session *and* this
deployment has login credentials configured, `call_with_reauth` transparently
performs one fresh login and retries the call once. If credentials aren't
configured, the retry login itself fails, or the retried call fails again,
the original error propagates as it always did -- this is a best-effort
convenience, not a guarantee, and it never retries more than once per call.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

from monarch_api import MonarchError

from monarch_mcp import config
from monarch_mcp.auth_runtime import LoginError, perform_login

logger = logging.getLogger(__name__)

#: Lowercased substrings Monarch's API is known to return in the
#: `detail`/`message` field of a 401 response -- the text monarch-api2's
#: `parse_error` surfaces as the `MonarchError` message. Matched
#: case-insensitively; deliberately narrow so a genuine validation or
#: not-found error (a different 4xx) doesn't trigger a pointless re-login.
_EXPIRED_SESSION_MARKERS = (
    "authentication credentials were not provided",
    "invalid token",
    "token has expired",
    "token is invalid",
    "not authenticated",
    "unauthorized",
)

#: Tool name prefix for the auth group itself (auth_login, auth_status,
#: auth_create_session, ...). Never retried: retrying a login failure by
#: attempting another login would either recurse pointlessly or mask the
#: real error an operator needs to see to fix credentials.
_NO_REAUTH_PREFIX = "auth_"


def looks_like_expired_session(message: str) -> bool:
    lowered = message.lower()
    return any(marker in lowered for marker in _EXPIRED_SESSION_MARKERS)


def call_with_reauth(
    tool_name: str,
    function: Callable[..., Any],
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
) -> Any:
    """Call `function(*args, **kwargs)`, retrying once after a fresh login if
    it fails with what looks like an expired-session error."""
    try:
        return function(*args, **kwargs)
    except MonarchError as exc:
        if tool_name.startswith(_NO_REAUTH_PREFIX):
            raise
        if not looks_like_expired_session(str(exc)):
            raise
        if not config.configured_email() or not config.configured_password():
            raise
        logger.info(
            "%s failed with what looks like an expired session; attempting one re-login and retry.",
            tool_name,
        )
        try:
            perform_login()
        except LoginError as login_exc:
            logger.warning("Re-login attempt failed: %s", login_exc)
            raise exc from login_exc
        return function(*args, **kwargs)
