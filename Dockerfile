# syntax=docker/dockerfile:1
#
# monarch-mcp2-obot — single-tenant Monarch Money MCP server for obot,
# forked from erikrubstein/monarch-mcp2 and ported to MCP Python SDK v2.
#
# Defaults to obot's Docker-deployment model: a port plus a
# streamable-http endpoint (obot's uvx/command-based deployment path talks
# stdio instead — run the `monarch-mcp` console script directly for that,
# no container needed). Override with MCP_TRANSPORT=stdio if you want to
# run this image itself over stdio (`docker run -i`).

FROM python:3.12-slim AS base

LABEL org.opencontainers.image.title="monarch-mcp2-obot" \
      org.opencontainers.image.description="Single-tenant Monarch Money MCP server for self-hosting behind obot" \
      org.opencontainers.image.source="https://github.com/dcode/monarch-mcp2-obot" \
      org.opencontainers.image.licenses="MIT"

COPY --from=ghcr.io/astral-sh/uv:0.8.17 /uv /uvx /usr/local/bin/

WORKDIR /app

# Build from this repo's own source — unlike the upstream repos surveyed
# earlier in this project, there's no separate git history to pin here;
# COPY captures exactly the commit you're building from. LICENSE/NOTICE.md
# are included so hatchling's license-files auto-detection actually finds
# them and bundles them into the installed wheel's dist-info, same as a
# local `uv build` does.
COPY pyproject.toml README.md LICENSE NOTICE.md ./
COPY src ./src

# monarch-api2 is still fetched from its own repo at build time (pinned to
# a tag in pyproject.toml's dependency spec) — bump that pin deliberately,
# not by floating to its default branch.
RUN uv venv && uv pip install .

ENV MONARCH_SESSION_PATH=/data/session.json \
    MCP_TRANSPORT=streamable-http \
    MCP_HOST=0.0.0.0 \
    MCP_PORT=8000

RUN useradd --create-home --home-dir /home/monarch --shell /bin/bash monarch \
    && mkdir -p /data \
    && chown -R monarch:monarch /data /app
USER monarch
VOLUME ["/data"]
EXPOSE 8000

ENTRYPOINT ["/app/.venv/bin/monarch-mcp"]
