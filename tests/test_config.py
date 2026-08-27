from __future__ import annotations

from pathlib import Path

from monarch_mcp.config import (
    configured_email,
    configured_password,
    configured_totp_secret,
    default_session_path,
    host,
    port,
    resolve_session_path,
    transport,
)


def test_default_session_path_uses_config_dir_env(monkeypatch, tmp_path) -> None:
    monkeypatch.delenv("MONARCH_SESSION_PATH", raising=False)
    monkeypatch.setenv("MONARCH_CONFIG_DIR", str(tmp_path))

    assert default_session_path() == tmp_path / "session.json"


def test_default_session_path_prefers_session_path_env(monkeypatch, tmp_path) -> None:
    configured = tmp_path / "custom.json"
    monkeypatch.setenv("MONARCH_SESSION_PATH", str(configured))

    assert default_session_path() == configured


def test_resolve_session_path_expands_explicit_path(tmp_path) -> None:
    explicit = tmp_path / "session.json"

    assert resolve_session_path(explicit) == Path(explicit)


def test_credential_getters_default_to_none(monkeypatch) -> None:
    monkeypatch.delenv("MONARCH_EMAIL", raising=False)
    monkeypatch.delenv("MONARCH_PASSWORD", raising=False)
    monkeypatch.delenv("MONARCH_TOTP_SECRET", raising=False)

    assert configured_email() is None
    assert configured_password() is None
    assert configured_totp_secret() is None


def test_credential_getters_read_environment(monkeypatch) -> None:
    monkeypatch.setenv("MONARCH_EMAIL", "user@example.com")
    monkeypatch.setenv("MONARCH_PASSWORD", "hunter2")
    monkeypatch.setenv("MONARCH_TOTP_SECRET", "JBSWY3DPEHPK3PXP")

    assert configured_email() == "user@example.com"
    assert configured_password() == "hunter2"
    assert configured_totp_secret() == "JBSWY3DPEHPK3PXP"


def test_transport_defaults_to_stdio(monkeypatch) -> None:
    monkeypatch.delenv("MCP_TRANSPORT", raising=False)

    assert transport() == "stdio"


def test_transport_reads_environment_override(monkeypatch) -> None:
    monkeypatch.setenv("MCP_TRANSPORT", "streamable-http")

    assert transport() == "streamable-http"


def test_host_and_port_defaults(monkeypatch) -> None:
    monkeypatch.delenv("MCP_HOST", raising=False)
    monkeypatch.delenv("MCP_PORT", raising=False)

    assert host() == "0.0.0.0"
    assert port() == 8000


def test_host_and_port_read_environment(monkeypatch) -> None:
    monkeypatch.setenv("MCP_HOST", "127.0.0.1")
    monkeypatch.setenv("MCP_PORT", "9001")

    assert host() == "127.0.0.1"
    assert port() == 9001
