"""Project configuration loading and precedence helpers."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Mapping
import tomllib

from repoverity.models import Severity


DEFAULT_EXCLUDE_PATTERNS: tuple[str, ...] = (
    ".venv/**",
    "venv/**",
    ".git/**",
    ".hg/**",
    ".svn/**",
    "node_modules/**",
    "build/**",
    "dist/**",
    ".tox/**",
    ".nox/**",
    ".pytest_cache/**",
    ".mypy_cache/**",
    ".ruff_cache/**",
    "__pycache__/**",
    "site-packages/**",
    "vendor/**",
)

RULE_SETTING_VALUES = {"off", "info", "low", "medium", "high", "critical", "warn"}
FAIL_ON_VALUES = {"none", "medium", "high", "critical"}


class ConfigError(ValueError):
    """Raised for invalid RepoVerity project configuration."""


@dataclass(frozen=True, slots=True)
class Config:
    exclude: tuple[str, ...] = DEFAULT_EXCLUDE_PATTERNS
    rule_settings: Mapping[str, str] = field(default_factory=dict)
    baseline: str | None = None
    fail_on: str = "none"

    def with_cli_exclude(self, pattern: str | None) -> Config:
        if pattern is None:
            return self
        return replace(self, exclude=(*self.exclude, pattern))

    def with_fail_on(self, fail_on: str | None) -> Config:
        if fail_on is None:
            return self
        if fail_on not in FAIL_ON_VALUES:
            raise ConfigError(f"invalid fail threshold: {fail_on}")
        return replace(self, fail_on=fail_on)

    def with_baseline(self, baseline: str | None) -> Config:
        return replace(self, baseline=baseline if baseline is not None else self.baseline)


def load_config(root: Path) -> Config:
    pyproject = root / "pyproject.toml"
    if not pyproject.is_file():
        return Config()
    try:
        parsed = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
        raise ConfigError(f"could not parse {pyproject}: {exc}") from exc

    tool = parsed.get("tool", {})
    section = tool.get("repoverity", {}) if isinstance(tool, dict) else {}
    if not isinstance(section, dict):
        raise ConfigError("[tool.repoverity] must be a table")

    exclude_raw = section.get("exclude", [])
    if not isinstance(exclude_raw, list) or not all(isinstance(item, str) for item in exclude_raw):
        raise ConfigError("tool.repoverity.exclude must be an array of strings")
    excludes = (*DEFAULT_EXCLUDE_PATTERNS, *tuple(exclude_raw))

    fail_on_raw = section.get("fail-on", "none")
    if not isinstance(fail_on_raw, str) or fail_on_raw not in FAIL_ON_VALUES:
        raise ConfigError("tool.repoverity.fail-on must be none|medium|high|critical")

    baseline_raw = section.get("baseline")
    if baseline_raw is not None and not isinstance(baseline_raw, str):
        raise ConfigError("tool.repoverity.baseline must be a string path")

    rules_raw = section.get("rules", {})
    if not isinstance(rules_raw, dict):
        raise ConfigError("[tool.repoverity.rules] must be a table")
    rule_settings: dict[str, str] = {}
    for rule_id, setting in rules_raw.items():
        if not isinstance(setting, str) or setting not in RULE_SETTING_VALUES:
            raise ConfigError(
                f"tool.repoverity.rules.{rule_id} must be off|warn|info|low|medium|high|critical"
            )
        rule_settings[str(rule_id).upper()] = setting

    return Config(
        exclude=excludes,
        rule_settings=rule_settings,
        baseline=baseline_raw,
        fail_on=fail_on_raw,
    )


def configured_severity(setting: str, default: Severity) -> Severity | None:
    if setting == "off":
        return None
    if setting == "warn":
        return Severity.MEDIUM
    if setting in {severity.value for severity in Severity}:
        return Severity(setting)
    return default
