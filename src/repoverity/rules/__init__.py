"""Built-in rule analyzer registry."""

from __future__ import annotations

from collections.abc import Callable

from repoverity.models import Finding
from repoverity.rules import (
    abstraction,
    comments,
    dead_surface,
    dependency,
    naming,
    release,
    tests_map,
)
from repoverity.rules.base import AnalysisContext

Analyzer = Callable[[AnalysisContext], list[Finding]]

ANALYZERS: tuple[Analyzer, ...] = (
    dependency.analyze,
    abstraction.analyze,
    naming.analyze,
    comments.analyze,
    dead_surface.analyze,
    tests_map.analyze,
    release.analyze,
)

__all__ = ["ANALYZERS", "AnalysisContext"]
