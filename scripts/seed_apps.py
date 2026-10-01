#!/usr/bin/env python3
"""Seed App Management demo projects (Sovereign Books Android/web)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sovereign_books.apps_manager import AppsManager
from sovereign_books.db import resolve_db_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed App Management projects")
    parser.add_argument("--db", default=None, help="SQLite path")
    args = parser.parse_args()
    path = str(resolve_db_path(args.db))
    apps = AppsManager(path)
    projects = apps.list_projects()
    # trigger a sample build so dashboard isn't empty
    if projects["projects"]:
        pid = projects["projects"][0]["id"]
        build = apps.trigger_build(pid, platform="android", profile="preview")
        apps.publish_ota(pid, "preview", "seed update")
        print({
            "db": path,
            "projects": projects["count"],
            "sample_build": build.get("id"),
            "status": "OK",
        })
    else:
        print({"db": path, "projects": 0, "status": "ERROR"})
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
