#!/usr/bin/env python3
"""
Offline Sovereign Books chat (no LLM required).

Usage:
  .venv/bin/python scripts/chat_books.py "show cash"
  .venv/bin/python scripts/chat_books.py  # interactive
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

try:
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
except ImportError:
    pass

from sovereign_books.chat_engine import BooksChatEngine


def main() -> int:
    engine = BooksChatEngine()
    if len(sys.argv) > 1:
        msg = " ".join(sys.argv[1:])
        print(json.dumps(engine.reply(msg), indent=2))
        return 0
    print("Sovereign Books chat (script engine). Empty line to quit.")
    while True:
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if not line:
            return 0
        out = engine.reply(line)
        print(out["reply"])
        if out.get("artifacts"):
            print(f"  artifacts: {len(out['artifacts'])} · tools: {out.get('tools_used')}")


if __name__ == "__main__":
    raise SystemExit(main())
