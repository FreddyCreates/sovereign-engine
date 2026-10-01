#!/usr/bin/env python3
"""
Offline Sovereign Books Pro activation (no RevenueCat API key required).

Usage:
  .venv/bin/python scripts/activate_pro.py
  .venv/bin/python scripts/activate_pro.py --user books_demo_user
  .venv/bin/python scripts/activate_pro.py --off
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

try:
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
except ImportError:
    pass

from sovereign_books.revenuecat import RevenueCatService


def main() -> int:
    parser = argparse.ArgumentParser(description="Activate/deactivate local Pro entitlement")
    parser.add_argument(
        "--user",
        default=os.environ.get("REVENUECAT_APP_USER_ID", "books_demo_user"),
        help="RevenueCat app_user_id",
    )
    parser.add_argument(
        "--product",
        default="sovereign_pro_monthly",
        help="Product identifier to store locally",
    )
    parser.add_argument(
        "--off",
        action="store_true",
        help="Deactivate Pro instead of activating",
    )
    parser.add_argument(
        "--db",
        default=os.environ.get("SOVEREIGN_BOOKS_DB"),
        help="Optional SQLite path",
    )
    args = parser.parse_args()

    rc = RevenueCatService(args.db)
    if args.off:
        result = rc.deactivate_local_pro(args.user)
    else:
        result = rc.activate_local_pro(args.user, product_id=args.product)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
