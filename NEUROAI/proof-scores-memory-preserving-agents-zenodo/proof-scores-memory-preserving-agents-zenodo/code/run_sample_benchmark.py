#!/usr/bin/env python3
"""Run a toy Proof Scores evaluation over sample tasks.

The sample observations are illustrative only. Replace them with scored agent
outputs when building a real benchmark.
"""

from __future__ import annotations

import json
from pathlib import Path

from proofscore import DIMENSIONS, evaluate_against_minimums


ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "data" / "sample_tasks.jsonl"


def toy_observation_for(task: dict[str, object]) -> dict[str, int]:
    """Create illustrative observations that satisfy each task's minimums.

    Real benchmark runs should replace this function with scored agent outputs.
    """
    minimums = task.get("expected_min_scores", {})
    return {dimension: max(2, int(minimums.get(dimension, 2))) for dimension in DIMENSIONS}


def main() -> None:
    family_counts: dict[str, int] = {}
    for line in TASKS.read_text().splitlines():
        task = json.loads(line)
        observed = toy_observation_for(task)
        evaluation = evaluate_against_minimums(observed, task.get("expected_min_scores", {}))
        family = str(task.get("corpus_family", "UNKNOWN"))
        family_counts[family] = family_counts.get(family, 0) + 1
        print(json.dumps({"task_id": task["task_id"], "corpus_family": family, **evaluation}, indent=2))
    print(json.dumps({"seed_suite_family_counts": family_counts}, indent=2))


if __name__ == "__main__":
    main()
