from __future__ import annotations

import json
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
    if missing: raise ValueError(f"{source}: missing rule fields: {', '.join(sorted(missing))}")
    severity = str(raw["severity"]).upper()
    if severity not in {"INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"}: raise ValueError(f"{source}: invalid severity {severity}")
    pattern = str(raw["pattern"])
    if len(pattern) > 500: raise ValueError(f"{source}: rule pattern is too long")
    return PluginRule(str(raw["id"]), severity, str(raw["category"]), str(raw["title"]), re.compile(pattern, re.I), str(raw["recommendation"]), source)


def load_rules(directory: Path | None = None) -> tuple[list[PluginRule], list[str]]:
    """Load declarative JSON rule packs. Plugins are data, not executable code."""
    root = directory or plugin_dir(); rules: list[PluginRule] = []; errors: list[str] = []
    for path in sorted(root.glob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            raw_rules = payload.get("rules") if isinstance(payload, dict) else payload
            if not isinstance(raw_rules, list): raise ValueError("rule pack must be a list or contain a 'rules' list")
            for item in raw_rules:
                if not isinstance(item, dict): raise ValueError("every rule must be an object")
                rules.append(_compile_rule(item, path.name))
        except (OSError, ValueError, json.JSONDecodeError, re.error) as exc:
            errors.append(f"{path.name}: {exc}")
    return rules, errors


def apply_rules(lines: list[str], rules: list[PluginRule]) -> list[Finding]:
    findings: list[Finding] = []
    for raw in lines:
        line = raw.strip()
        if not line: continue
        for rule in rules:
            if rule.pattern.search(line): findings.append(Finding(rule.severity, rule.category, rule.title, line[:500], rule.recommendation))
    return findings
