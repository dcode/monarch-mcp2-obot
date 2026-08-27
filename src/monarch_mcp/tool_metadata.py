from __future__ import annotations

import inspect
from collections.abc import Callable
from functools import wraps
from typing import Annotated, Any

from mcp.server.mcpserver import MCPServer
from mcp.types import ToolAnnotations
from pydantic import Field

from monarch_mcp.output import OutputMode, shape_output
from monarch_mcp.reauth import call_with_reauth
from monarch_mcp.serialization import raw_output

READ_PREFIXES = ("download_", "get_", "list_", "load_", "search_")
WRITE_PREFIXES = (
    "archive_",
    "clear_",
    "contribute_",
    "create_",
    "link_",
    "match_",
    "reactivate_",
    "reorder_",
    "reset_",
    "restore_",
    "save_",
    "set_",
    "unmatch_",
    "unlink_",
    "unsplit_",
    "update_",
    "upload_",
    "withdraw_",
)
DESTRUCTIVE_PREFIXES = ("clear_", "delete_", "remove_", "reset_")
SPECIAL_DESCRIPTIONS = {
    "list_receipts": (
        "List uploaded and emailed receipts, optionally filtered by source or status."
    ),
    "login": (
        "Log in to Monarch using the server's configured credentials (or explicit "
        "overrides), handling an authenticator-app MFA challenge automatically if "
        "MONARCH_TOTP_SECRET is configured. Saves the resulting session for this "
        "deployment's single Monarch account."
    ),
    "status": (
        "Report whether this deployment has a usable, currently-valid Monarch "
        "session, without exposing the session token."
    ),
}


def register_api_tool(
    mcp: MCPServer,
    group: str,
    function_name: str,
    function: Callable[..., Any],
) -> None:
    tool_name = f"{group}_{function_name}"
    wrapped = _with_output_controls(tool_name, function)
    mcp.tool(
        name=tool_name,
        title=_title(group, function_name),
        description=_description(function_name),
        annotations=_annotations(function_name),
    )(wrapped)


def _with_output_controls(tool_name: str, function: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(function)
    def wrapped(
        *args: Any,
        output_mode: OutputMode = "summary",
        fields: list[str] | None = None,
        **kwargs: Any,
    ) -> Any:
        with raw_output(output_mode == "raw"):
            result = call_with_reauth(tool_name, function, args, kwargs)
        return shape_output(tool_name, result, output_mode=output_mode, fields=fields)

    wrapped.__signature__ = _signature_with_output_controls(function)  # type: ignore[attr-defined]
    wrapped.__annotations__ = {
        "output_mode": OutputMode,
        "fields": list[str] | None,
        "return": Any,
    }
    return wrapped


#: Parameters stripped from every tool's public schema before it's exposed to
#: an MCP client. `session_path` exists on the underlying group functions so
#: tests and library callers can point at an arbitrary session file, but this
#: server is deliberately single-tenant: one deployment == one Monarch
#: account == one session file, chosen once via MONARCH_SESSION_PATH /
#: MONARCH_CONFIG_DIR (see config.py). Hiding the parameter here means no
#: tool call an agent makes can ever target a different account's session —
#: the underlying function's own `session_path=None` default still resolves
#: to the single configured path, so behavior is unchanged for every caller
#: that never had a reason to pass it in the first place.
_HIDDEN_PARAMETERS = frozenset({"session_path"})


def _signature_with_output_controls(function: Callable[..., Any]) -> inspect.Signature:
    signature = inspect.signature(function, eval_str=True)
    parameters = [
        parameter
        for parameter in signature.parameters.values()
        if parameter.name not in _HIDDEN_PARAMETERS
    ]
    parameters.extend(
        [
            inspect.Parameter(
                "output_mode",
                inspect.Parameter.KEYWORD_ONLY,
                default="summary",
                annotation=Annotated[
                    OutputMode,
                    Field(
                        description=(
                            "Output shape to return. Use summary for compact CLI-style "
                            "defaults, full for complete structured data without raw, "
                            "and raw for complete structured data including raw payloads."
                        )
                    ),
                ],
            ),
            inspect.Parameter(
                "fields",
                inspect.Parameter.KEYWORD_ONLY,
                default=None,
                annotation=Annotated[
                    list[str] | None,
                    Field(
                        description=(
                            "Optional dotted output field paths to return, such as "
                            "['id', 'merchant.name', 'category.name']."
                        )
                    ),
                ],
            ),
        ]
    )
    return signature.replace(parameters=parameters, return_annotation=Any)


def _description(function_name: str) -> str:
    if function_name in SPECIAL_DESCRIPTIONS:
        return SPECIAL_DESCRIPTIONS[function_name]
    action = function_name.replace("_", " ")
    description = f"{action.capitalize()}."
    if function_name.startswith(DESTRUCTIVE_PREFIXES):
        description += " This may delete, clear, reset, or otherwise remove data."
    elif function_name.startswith(WRITE_PREFIXES):
        description += " This may create or update Monarch data."
    return description


def _annotations(function_name: str) -> ToolAnnotations:
    read_only = function_name.startswith(READ_PREFIXES)
    destructive = function_name.startswith(DESTRUCTIVE_PREFIXES)
    return ToolAnnotations(
        title=_title("", function_name).strip(),
        read_only_hint=read_only,
        destructive_hint=destructive,
        idempotent_hint=read_only,
        open_world_hint=True,
    )


def _title(group: str, function_name: str) -> str:
    words = [word.capitalize() for word in f"{group} {function_name}".replace("_", " ").split()]
    return " ".join(word for word in words if word)
