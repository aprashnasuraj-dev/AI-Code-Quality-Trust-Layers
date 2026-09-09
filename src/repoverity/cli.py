"""Thin command-line interface for RepoVerity."""

from __future__ import annotations

import argparse
import platform
import sys
from collections.abc import Sequence
from pathlib import Path

from repoverity import __version__
from repoverity.baseline import BaselineError, write_baseline
from repoverity.config import FAIL_ON_VALUES, ConfigError, load_config
from repoverity.engine import AuditOptions, audit_repository
from repoverity.models import SEVERITY_RANK, AuditResult, Severity
from repoverity.reporters import render_json, render_markdown, render_sarif, render_terminal
from repoverity.rules.registry import all_rules, get_rule

EXIT_OK = 0
EXIT_GATE = 1
EXIT_USAGE = 2
EXIT_ANALYSIS = 3
EXIT_INTERNAL = 4


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="repoverity",
        description="Evidence-based code trust audit for Python repositories.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    audit = subparsers.add_parser("audit", help="audit a repository")
    audit.add_argument("path", nargs="?", default=".")
    audit.add_argument(
        "--format", choices=("terminal", "json", "markdown", "sarif"), default="terminal"
    )
    audit.add_argument("--output", type=Path)
    audit.add_argument("--severity", choices=tuple(item.value for item in Severity), default="info")
    audit.add_argument("--rules", help="comma-separated rule IDs")
    audit.add_argument("--exclude", help="additional glob pattern to exclude")
    audit.add_argument("--baseline", type=Path)
    audit.add_argument("--fail-on", choices=tuple(sorted(FAIL_ON_VALUES)))
    audit.add_argument("--changed-only", nargs="?", const="HEAD~1", metavar="BASE_REF")
    audit.add_argument("--no-color", action="store_true")
    audit.add_argument("--verbose", action="store_true")

    explain = subparsers.add_parser("explain", help="explain one rule")
    explain.add_argument("rule_id")

    fix_preview = subparsers.add_parser(
        "fix-preview", help="preview remediation without modifying source"
    )
    fix_preview.add_argument("path", nargs="?", default=".")
    fix_preview.add_argument("--rules", help="comma-separated rule IDs")

    baseline = subparsers.add_parser("baseline", help="create or inspect a baseline")
    baseline_sub = baseline.add_subparsers(dest="baseline_command", required=True)
    baseline_create = baseline_sub.add_parser("create", help="create a fingerprint baseline")
    baseline_create.add_argument("path", nargs="?", default=".")
    baseline_create.add_argument("--output", type=Path, required=True)
    baseline_check = baseline_sub.add_parser(
        "check", help="compare current findings with a baseline"
    )
    baseline_check.add_argument("path", nargs="?", default=".")
    baseline_check.add_argument("--baseline", type=Path, required=True)

    rules = subparsers.add_parser("rules", help="discover built-in rules")
    rules_sub = rules.add_subparsers(dest="rules_command", required=True)
    rules_sub.add_parser("list", help="list rule metadata")
    rules_show = rules_sub.add_parser("show", help="show one rule")
    rules_show.add_argument("rule_id")

    subparsers.add_parser("version", help="print tool and runtime version")
    return parser


def _selected_rules(raw: str | None) -> frozenset[str] | None:
    if raw is None:
        return None
    selected = frozenset(part.strip().upper() for part in raw.split(",") if part.strip())
    unknown = sorted(rule_id for rule_id in selected if get_rule(rule_id) is None)
    if unknown:
        raise ConfigError(f"unknown rule ID(s): {', '.join(unknown)}")
    return selected


def _resolve_root(raw: str) -> Path:
    path = Path(raw).expanduser()
    if not path.exists():
        raise ConfigError(f"path does not exist: {path}")
    if not path.is_dir():
        raise ConfigError(f"audit path must be a directory: {path}")
    return path.resolve()


def _resolve_optional_path(root: Path, path: Path | None) -> Path | None:
    if path is None:
        return None
    return path if path.is_absolute() else root / path


def _load_effective_config(root: Path, exclude: str | None = None, fail_on: str | None = None):  # type: ignore[no-untyped-def]
    config = load_config(root).with_cli_exclude(exclude).with_fail_on(fail_on)
    return config


def _render(result: AuditResult, format_name: str, *, no_color: bool, verbose: bool) -> str:
    if format_name == "terminal":
        return render_terminal(result, no_color=no_color, verbose=verbose)
    if format_name == "json":
        return render_json(result)
    if format_name == "markdown":
        return render_markdown(result)
    if format_name == "sarif":
        return render_sarif(result)
    raise ConfigError(f"unknown output format: {format_name}")


def _write_or_print(content: str, output: Path | None) -> None:
    if output is None:
        sys.stdout.write(content)
        return
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8")


def _gate_failed(result: AuditResult, fail_on: str) -> bool:
    if fail_on == "none":
        return False
    threshold = Severity(fail_on)
    return any(
        SEVERITY_RANK[item.severity] >= SEVERITY_RANK[threshold] for item in result.new_findings
    )


def _has_internal_analysis_failure(result: AuditResult) -> bool:
    return any(issue.kind == "rule-error" for issue in result.issues)


def _run_audit(args: argparse.Namespace) -> int:
    root = _resolve_root(args.path)
    config = _load_effective_config(root, args.exclude, args.fail_on)
    baseline_path = _resolve_optional_path(root, args.baseline)
    if baseline_path is None and config.baseline:
        baseline_path = _resolve_optional_path(root, Path(config.baseline))
    if baseline_path is not None and not baseline_path.is_file():
        raise ConfigError(f"baseline file does not exist: {baseline_path}")
    options = AuditOptions(
        minimum_severity=Severity(args.severity),
        selected_rules=_selected_rules(args.rules),
        baseline_path=baseline_path,
        changed_only_base=args.changed_only,
    )
    result = audit_repository(root, config, options)
    content = _render(result, args.format, no_color=args.no_color, verbose=args.verbose)
    _write_or_print(content, args.output)
    if _has_internal_analysis_failure(result):
        return EXIT_ANALYSIS
    return EXIT_GATE if _gate_failed(result, config.fail_on) else EXIT_OK


def _rule_text(rule_id: str) -> str:
    rule = get_rule(rule_id)
    if rule is None:
        raise ConfigError(f"unknown rule ID: {rule_id}")
    suppression = f"# repoverity: ignore[{rule.rule_id}] - <why this exception is intentional>"
    return "\n".join(
        [
            f"{rule.rule_id} — {rule.title}",
            f"Category: {rule.category}",
            f"Default severity: {rule.severity.value}",
            f"Confidence: {rule.confidence.value}",
            f"Evidence level: {rule.evidence_level.value}",
            "",
            "What it detects",
            rule.summary,
            "",
            "Why it matters",
            rule.mechanism,
            "",
            "Bad candidate",
            rule.bad_example,
            "",
            "Legitimate counterexample",
            rule.acceptable_example,
            "",
            "Limitations",
            rule.limitations,
            "",
            "Recommended action",
            rule.recommendation,
            "",
            "Suppression",
            suppression,
            "",
        ]
    )


def _run_fix_preview(args: argparse.Namespace) -> int:
    root = _resolve_root(args.path)
    config = load_config(root)
    audit_result = audit_repository(
        root,
        config,
        AuditOptions(selected_rules=_selected_rules(args.rules)),
    )
    lines = [
        "RepoVerity fix preview",
        "No source files will be modified.",
        "v0.1 intentionally ships no automatic architecture rewrite; recommendations are preview-only.",
        "",
    ]
    if not audit_result.findings:
        lines.append("No findings in the selected scope.")
    for item in audit_result.findings[:30]:
        location = item.location.path
        if item.location.start_line is not None:
            location += f":{item.location.start_line}"
        lines.extend(
            [
                f"{item.rule_id} {location}",
                f"  {item.message}",
                f"  Proposed action: {item.recommendation}",
                "  Auto-apply: unavailable (review required)",
                "",
            ]
        )
    sys.stdout.write("\n".join(lines).rstrip() + "\n")
    return EXIT_ANALYSIS if _has_internal_analysis_failure(audit_result) else EXIT_OK


def _run_baseline_create(args: argparse.Namespace) -> int:
    root = _resolve_root(args.path)
    config = load_config(root)
    audit_result = audit_repository(root, config, AuditOptions())
    if _has_internal_analysis_failure(audit_result):
        sys.stderr.write(render_terminal(audit_result, no_color=True, verbose=True))
        return EXIT_ANALYSIS
    output = args.output if args.output.is_absolute() else root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    write_baseline(output, audit_result.findings)
    sys.stdout.write(
        f"Baseline written: {output}\nFindings captured: {len(audit_result.findings)}\n"
    )
    return EXIT_OK


def _run_baseline_check(args: argparse.Namespace) -> int:
    root = _resolve_root(args.path)
    config = load_config(root)
    baseline_path = args.baseline if args.baseline.is_absolute() else root / args.baseline
    if not baseline_path.is_file():
        raise ConfigError(f"baseline file does not exist: {baseline_path}")
    result = audit_repository(root, config, AuditOptions(baseline_path=baseline_path))
    sys.stdout.write(render_terminal(result, no_color=True, verbose=False))
    return EXIT_ANALYSIS if _has_internal_analysis_failure(result) else EXIT_OK


def _run_rules(args: argparse.Namespace) -> int:
    if args.rules_command == "list":
        for rule in all_rules():
            sys.stdout.write(
                f"{rule.rule_id:<8} {rule.severity.value:<8} {rule.confidence.value:<7} "
                f"{rule.category:<20} {rule.title}\n"
            )
        return EXIT_OK
    if args.rules_command == "show":
        sys.stdout.write(_rule_text(args.rule_id))
        return EXIT_OK
    raise ConfigError("missing rules subcommand")


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    try:
        args = parser.parse_args(argv)
        if args.command == "audit":
            return _run_audit(args)
        if args.command == "explain":
            sys.stdout.write(_rule_text(args.rule_id))
            return EXIT_OK
        if args.command == "fix-preview":
            return _run_fix_preview(args)
        if args.command == "baseline":
            if args.baseline_command == "create":
                return _run_baseline_create(args)
            if args.baseline_command == "check":
                return _run_baseline_check(args)
        if args.command == "rules":
            return _run_rules(args)
        if args.command == "version":
            sys.stdout.write(
                f"RepoVerity {__version__}\n"
                f"Python {platform.python_version()}\n"
                f"Platform {platform.platform()}\n"
            )
            return EXIT_OK
        raise ConfigError(f"unknown command: {args.command}")
    except (ConfigError, BaselineError) as exc:
        sys.stderr.write(f"repoverity: {exc}\n")
        return EXIT_USAGE
    except (OSError, RuntimeError) as exc:
        sys.stderr.write(f"repoverity analysis failure: {exc}\n")
        return EXIT_ANALYSIS
    except Exception as exc:  # last-resort stable machine exit; not a substitute for tests
        sys.stderr.write(f"repoverity internal error: {type(exc).__name__}: {exc}\n")
        return EXIT_INTERNAL


if __name__ == "__main__":
    raise SystemExit(main())
