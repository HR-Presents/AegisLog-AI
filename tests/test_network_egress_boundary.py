from __future__ import annotations

import ast
from pathlib import Path


APP_ROOT = Path(__file__).resolve().parents[1] / "src" / "aegislog"
NETWORK_OWNER = APP_ROOT / "providers.py"
OUTBOUND_IMPORTS = {
    "aiohttp",
    "http.client",
    "httpx",
    "requests",
    "socket",
    "urllib.request",
    "urllib3",
}
NETWORK_SHELL_TOOLS = {"curl", "wget"}


def _import_names(tree: ast.AST) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
    return names


def _literal_command_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value.strip().split(maxsplit=1)[0].lower() if node.value.strip() else None
    if isinstance(node, (ast.List, ast.Tuple)) and node.elts:
        first = node.elts[0]
        if isinstance(first, ast.Constant) and isinstance(first.value, str):
            return first.value.strip().lower()
    return None


def _network_shell_calls(tree: ast.AST) -> list[str]:
    findings: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not node.args:
            continue
        command = _literal_command_name(node.args[0])
        if command not in NETWORK_SHELL_TOOLS:
            continue
        if isinstance(node.func, ast.Attribute):
            owner = node.func.value.id if isinstance(node.func.value, ast.Name) else None
            if owner in {"subprocess", "os"}:
                findings.append(command)
    return findings


def test_only_provider_module_owns_outbound_network_clients() -> None:
    violations: list[str] = []
    for path in sorted(APP_ROOT.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        imports = _import_names(tree)
        outbound = sorted(
            name
            for name in imports
            if any(name == blocked or name.startswith(f"{blocked}.") for blocked in OUTBOUND_IMPORTS)
        )
        shell_calls = _network_shell_calls(tree)

        if path != NETWORK_OWNER and outbound:
            violations.append(f"{path.name}: outbound imports {', '.join(outbound)}")
        if shell_calls:
            violations.append(f"{path.name}: network shell command(s) {', '.join(sorted(shell_calls))}")

    assert not violations, (
        "Outbound networking must remain centralized in providers.py so the remote-AI consent gate "
        "cannot be bypassed. Review any new network path explicitly before changing this allowlist:\n"
        + "\n".join(violations)
    )


def test_provider_transport_keeps_consent_guard_before_network_setup() -> None:
    tree = ast.parse(NETWORK_OWNER.read_text(encoding="utf-8"), filename=str(NETWORK_OWNER))
    post_json = next(
        node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "_post_json"
    )
    calls = [
        node.func.id
        for node in ast.walk(post_json)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    ]

    assert "_require_remote_ai_opt_in" in calls
    assert "_validated_endpoint" in calls
    assert calls.index("_require_remote_ai_opt_in") < calls.index("_validated_endpoint")
