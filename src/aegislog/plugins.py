from __future__ import annotations

import importlib.util
import re
from dataclasses import dataclass
from pathlib import Path

from .config import config_dir
from .engine import Finding


@dataclass(frozen=True)
class PluginRule:
    id: str
    severity: str
    category: str
    title: str
    pattern: re.Pattern[str]
    recommendation: str
    source: str


def plugin_dir() -> Path:
    path = config_dir() / "rules.d"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _compile_rule(raw: dict, source: str) -> PluginRule:
    required = {"id", "severity", "category", "title", "pattern", "recommendation"}
    missing = required - raw.keys()
    if missing:
        raise ValueError(f"{source}: missing rule fields: {', '.join(sorted(missing))}")
    severity = str(raw["severity"]).upper()
    if severity not in {"INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"}:
        raise ValueError(f"{source}: invalid severity {severity}")
    pattern = str(raw["pattern"])
    if len(pattern) > 500:
        raise ValueError(f"{source}: rule pattern is too long")
    return PluginRule(str(raw["id"]), severity, str(raw["category"]), str(raw["title"]), re.compile(pattern, re.I), str(raw["recommendation"]), source)


def load_rules(directory: Path | None = None) -> tuple[list[PluginRule], list[str]]:
    root = directory or plugin_dir()
    rules: list[PluginRule] = []
    errors: list[str] = []
    for path in sorted(root.glob("*.py")):
        try:
            spec = importlib.util.spec_from_file_location(f"aegislog_user_rule_{path.stem}", path)
            if spec is None or spec.loader is None:
                raise ValueError("unable to load module")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            raw_rules = getattr(module, "RULES", None)
            if not isinstance(raw_rules, list):
                raise ValueError("plugin must define RULES as a list")
            rules.extend(_compile_rule(item, path.name) for item in raw_rules if isinstance(item, dict))
        except Exception as exc:
            errors.append(f"{path.name}: {exc}")
    return rules, errors


def apply_rules(lines: list[str], rules: list[PluginRule]) -> list[Finding]:
    findings: list[Finding] = []
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        for rule in rules:
            if rule.pattern.search(line):
                findings.append(Finding(rule.severity, rule.category, rule.title, line[:500], rule.recommendation))
    return findings
