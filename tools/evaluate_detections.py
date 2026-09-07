from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from aegislog.engine import analyze_lines

SEVERITY_RANK = {"INFO": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}


def _safe_div(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def evaluate(path: Path, min_severity: str = "MEDIUM") -> dict:
    threshold = SEVERITY_RANK[min_severity.upper()]
    cases = []
    categories = set()
    with path.open("r", encoding="utf-8") as handle:
        for raw in handle:
            if raw.strip():
                case = json.loads(raw)
                if not isinstance(case, dict) or not isinstance(case.get("lines"), list):
                    raise ValueError("each evaluation row must contain a list of lines")
                cases.append(case)
                categories.update(case.get("expected_categories", []))

    rows = []
    totals = {"tp": 0, "fp": 0, "fn": 0}
    per_category = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0})

    for case in cases:
        expected = set(case.get("expected_categories", []))
        detected = {
            finding.category
            for finding in analyze_lines(case["lines"])
            if SEVERITY_RANK.get(finding.severity.upper(), -1) >= threshold
        }
        categories.update(detected)
        tp = expected & detected
        fp = detected - expected
        fn = expected - detected
        totals["tp"] += len(tp)
        totals["fp"] += len(fp)
        totals["fn"] += len(fn)
        for category in tp:
            per_category[category]["tp"] += 1
        for category in fp:
            per_category[category]["fp"] += 1
        for category in fn:
            per_category[category]["fn"] += 1
        rows.append(
            {
                "id": case.get("id", "unnamed"),
                "label": case.get("label", "unspecified"),
                "expected": sorted(expected),
                "detected": sorted(detected),
            }
        )

    category_metrics = {}
    for category in sorted(categories):
        values = per_category[category]
        category_metrics[category] = {
            **values,
            "precision": round(_safe_div(values["tp"], values["tp"] + values["fp"]), 4),
            "recall": round(_safe_div(values["tp"], values["tp"] + values["fn"]), 4),
        }

    return {
        "dataset": str(path),
        "cases": len(cases),
        "minimum_reported_severity": min_severity.upper(),
        "tp": totals["tp"],
        "fp": totals["fp"],
        "fn": totals["fn"],
        "precision": round(_safe_div(totals["tp"], totals["tp"] + totals["fp"]), 4),
        "recall": round(_safe_div(totals["tp"], totals["tp"] + totals["fn"]), 4),
        "per_category": category_metrics,
        "results": rows,
        "limitations": (
            "This is a small synthetic regression dataset. It measures consistency against hand-labeled fixtures, "
            "not real-world security effectiveness, deployment-specific false-positive rates, or adversarial robustness."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate AegisLog detections against a labeled JSONL dataset.")
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--min-severity", default="MEDIUM", choices=tuple(SEVERITY_RANK))
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    report = evaluate(args.dataset, args.min_severity)
    if args.as_json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(
            f"cases={report['cases']} precision={report['precision']:.4f} "
            f"recall={report['recall']:.4f} fp={report['fp']} fn={report['fn']}"
        )
        for category, metrics in report["per_category"].items():
            print(
                f"{category}: precision={metrics['precision']:.4f} recall={metrics['recall']:.4f} "
                f"tp={metrics['tp']} fp={metrics['fp']} fn={metrics['fn']}"
            )
        print(f"limitations: {report['limitations']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
