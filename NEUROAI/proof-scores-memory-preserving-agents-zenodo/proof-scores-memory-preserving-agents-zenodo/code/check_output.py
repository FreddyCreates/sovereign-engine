#!/usr/bin/env python3
"""Run deterministic Proof Scores checks on an output text file."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from proofscore import deterministic_checks, suggested_scores_from_checks


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output_text", type=Path)
    args = parser.parse_args()

    text = args.output_text.read_text(encoding="utf-8")
    checks = deterministic_checks(text)
    scores = suggested_scores_from_checks(checks)
    print(json.dumps({"checks": checks, "suggested_scores": scores}, indent=2))


if __name__ == "__main__":
    main()
