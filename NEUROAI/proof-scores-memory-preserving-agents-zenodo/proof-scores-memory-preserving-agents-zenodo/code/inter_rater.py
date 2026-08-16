#!/usr/bin/env python3
"""Starter inter-rater agreement calculations for Proof Scores."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from statistics import mean

from proofscore import DIMENSIONS


ROOT = Path(__file__).resolve().parents[1]
SCORES = ROOT / "data" / "example_human_scores.jsonl"


def load_scores(path: Path) -> dict[str, list[dict[str, int | str]]]:
    grouped: dict[str, list[dict[str, int | str]]] = defaultdict(list)
    for line in path.read_text().splitlines():
        record = json.loads(line)
        grouped[record["task_id"]].append(record)
    return grouped


def agreement_summary(grouped: dict[str, list[dict[str, int | str]]]) -> dict[str, object]:
    comparisons = []
    for task_id, records in grouped.items():
        if len(records) < 2:
            continue
        a, b = records[0], records[1]
        for dimension in DIMENSIONS:
            delta = abs(int(a[dimension]) - int(b[dimension]))
            comparisons.append({"task_id": task_id, "dimension": dimension, "delta": delta})
    if not comparisons:
        return {"comparison_count": 0}
    return {
        "comparison_count": len(comparisons),
        "exact_agreement_rate": round(sum(1 for c in comparisons if c["delta"] == 0) / len(comparisons), 3),
        "within_one_rate": round(sum(1 for c in comparisons if c["delta"] <= 1) / len(comparisons), 3),
        "mean_absolute_disagreement": round(mean(c["delta"] for c in comparisons), 3),
        "largest_disagreements": [c for c in comparisons if c["delta"] == max(x["delta"] for x in comparisons)],
    }


def main() -> None:
    print(json.dumps(agreement_summary(load_scores(SCORES)), indent=2))


if __name__ == "__main__":
    main()
