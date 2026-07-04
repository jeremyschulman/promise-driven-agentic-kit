"""Structured refusals — the shape of a declined promise (see the clinic example
for the rationale). A service declines by returning a refusal, never by raising.
"""

from __future__ import annotations

from typing import Any


def refusal(code: str, unmet: str, message: str, **extra: Any) -> dict[str, Any]:
    return {"ok": False, "refusal": code, "unmet": unmet, "message": message, **extra}


def ok(**data: Any) -> dict[str, Any]:
    return {"ok": True, **data}
