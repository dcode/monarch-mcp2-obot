from __future__ import annotations

from pathlib import Path

from monarch_api import AuthSession, load_session, save_session

from monarch_mcp.config import resolve_session_path


def has_session(session_path: str | Path | None = None) -> bool:
    return resolve_session_path(session_path).exists()


def read_session(session_path: str | Path | None = None) -> AuthSession:
    return load_session(resolve_session_path(session_path))


def require_session(session_path: str | Path | None = None) -> AuthSession:
    path = resolve_session_path(session_path)
    if not path.exists():
        raise FileNotFoundError(f"No saved Monarch session found at {path}.")
    return load_session(path)


def write_session(
    session: AuthSession,
    session_path: str | Path | None = None,
) -> Path:
    path = resolve_session_path(session_path)
    save_session(session, path)
    return path


def delete_session(session_path: str | Path | None = None) -> bool:
    path = resolve_session_path(session_path)
    if not path.exists():
        return False
    path.unlink()
    return True
