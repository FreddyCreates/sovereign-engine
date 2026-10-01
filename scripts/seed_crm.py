#!/usr/bin/env python3
"""Seed CRM demo data into Sovereign Books SQLite DB."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sovereign_books.crm_store import CRMStore
from sovereign_books.db import resolve_db_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed CRM demo workspace")
    parser.add_argument("--db", default=None, help="SQLite path")
    args = parser.parse_args()
    path = str(resolve_db_path(args.db))
    crm = CRMStore(path)
    companies = crm.list_records("companies")
    # ensure a second demo company for UI
    if companies["count"] < 2:
        crm.create_company(
            name="Northwind Labs",
            domain="northwind.lab",
            industry="Biotech",
            arr=80000,
            employees=25,
        )
    print({"db": path, "companies": crm.list_records("companies")["count"], "status": "OK"})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
