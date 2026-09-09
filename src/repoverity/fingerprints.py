"""Stable finding fingerprints for baselines and regression gating."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping
from typing import Any

_DIGIT_RUN = re.compile(r"\b\d+\b")
_WHITESPACE = re.compile(r"\s+")


def _normalize_anchor(text: str) -> str:
    """Normalize incidental formatting while retaining semantic identifiers."""
    compact = _WHITESPACE.sub(" ", text.strip())
    return _DIGIT_RUN.sub("#", compact)


def make_fingerprint(
    rule_id: str,
    path: str,
    *,
    symbol: str | None = None,
    anchor: str = "",
    extra: Mapping[str, Any] | None = None,
) -> str:
    """Return a line-number-independent SHA-256 fingerprint.

    The relative path and semantic symbol are intentionally retained. Moving a finding within
    the same symbol should preserve the fingerprint; renaming/moving the symbol should not.
    """
    payload: dict[str, Any] = {
        "rule_id": rule_id,
        "path": path.replace("\\", "/"),
        "symbol": symbol or "",
        "anchor": _normalize_anchor(anchor),
    }
    if extra:
        payload["extra"] = {key: extra[key] for key in sorted(extra)}
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()
