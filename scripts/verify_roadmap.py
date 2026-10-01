#!/usr/bin/env python3
"""Verify all ROADMAP feature IDs 1–250 against a SQLite DB."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

# Allow running from repo root without install
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sovereign_books.roadmap_registry import FEATURE_REGISTRY, verify_all


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify Sovereign roadmap features 1–250")
    parser.add_argument("--db", default=None, help="SQLite path (default: temp db)")
    parser.add_argument("--json", action="store_true", help="Print full JSON result")
    args = parser.parse_args()

    db_path = args.db
    tmp = None
    if not db_path:
        tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        tmp.close()
        db_path = tmp.name

    result = verify_all(db_path)
    if args.json:
        # trim bulky results for readability unless failures
        slim = {k: v for k, v in result.items() if k != "results"}
        slim["failure_details"] = [r for r in result["results"] if not r.get("pass")]
        print(json.dumps(slim, indent=2))
    else:
        print(result)

    print(
        f"\nRegistered features: {len(FEATURE_REGISTRY)} | "
        f"passed={result['passed']} failed={result['failed']}",
        file=sys.stderr,
    )
    if result["failures"]:
        print(f"Failures: {result['failures']}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
