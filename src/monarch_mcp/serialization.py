from __future__ import annotations

import base64
from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import fields, is_dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Any

JsonValue = None | bool | int | float | str | list["JsonValue"] | dict[str, "JsonValue"]
_include_raw: ContextVar[bool] = ContextVar("include_raw", default=False)


@contextmanager
def raw_output(enabled: bool) -> Iterator[None]:
    token = _include_raw.set(enabled)
    try:
        yield
    finally:
        _include_raw.reset(token)


def to_jsonable(value: Any) -> JsonValue:
    if value is None or isinstance(value, bool | int | float | str):
        return value
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, bytes):
        return base64.b64encode(value).decode("ascii")
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, datetime | date):
        return value.isoformat()
    if isinstance(value, Enum):
        return to_jsonable(value.value)
    if is_dataclass(value) and not isinstance(value, type):
        return {
            field.name: to_jsonable(getattr(value, field.name))
            for field in fields(value)
            if _include_raw.get() or field.name != "raw"
        }
    if isinstance(value, dict):
        return {
            str(key): to_jsonable(item)
            for key, item in value.items()
            if _include_raw.get() or key != "raw"
        }
    if isinstance(value, tuple | list | set):
        return [to_jsonable(item) for item in value]
    return str(value)
