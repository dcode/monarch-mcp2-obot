from __future__ import annotations

import logging

from mcp.server.mcpserver import MCPServer
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from monarch_mcp import config
from monarch_mcp.auth_runtime import ensure_authenticated
from monarch_mcp.groups import (
    accounts,
    auth,
    budget,
    cashflow,
    categories,
    goals,
    household,
    investments,
    merchants,
    receipts,
    recurring,
    reports,
    tags,
    transactions,
)

logger = logging.getLogger(__name__)


def create_mcp() -> MCPServer:
    mcp = MCPServer("monarch")
    auth.register(mcp)
    accounts.register(mcp)
    tags.register(mcp)
    categories.register(mcp)
    cashflow.register(mcp)
    merchants.register(mcp)
    household.register(mcp)
    recurring.register(mcp)
    investments.register(mcp)
    reports.register(mcp)
    goals.register(mcp)
    budget.register(mcp)
    transactions.register(mcp)
    receipts.register(mcp)

    # Plain liveness probe for container orchestrators (obot's Docker-based
    # deployment model asks for a `healthz` path in the catalog entry). This
    # deliberately does *not* check Monarch session/auth state -- a stale or
    # missing session shouldn't make the orchestrator restart an otherwise
    # healthy process, and auth_status is already the right tool for that.
    # mcp.server.mcpserver.MCPServer.custom_route has no return type
    # annotation of its own, so mypy --strict can't see that the closure
    # it hands back is fully typed and flags every use as an untyped
    # decorator. Nothing we can fix on our side short of re-typing
    # upstream.
    @mcp.custom_route("/health", methods=["GET"], include_in_schema=False)  # type: ignore[untyped-decorator]
    async def health(_request: Request) -> Response:
        return JSONResponse({"status": "ok"})

    return mcp


mcp = create_mcp()


def main() -> None:
    logging.basicConfig(level=logging.INFO)

    # Best-effort: reuse an existing session, or log in automatically if
    # MONARCH_EMAIL/MONARCH_PASSWORD are configured. Never blocks startup —
    # a failure here just means auth_login/auth_status are the next stop.
    ensure_authenticated()

    selected_transport = config.transport()
    if selected_transport == "stdio":
        # The path obot's command/uvx-based MCP servers use.
        mcp.run(transport="stdio")
    else:
        # streamable-http (or sse): the path obot's Docker-based MCP server
        # deployment model expects — a port plus an HTTP/SSE endpoint.
        mcp.run(transport=selected_transport, host=config.host(), port=config.port())


if __name__ == "__main__":
    main()
