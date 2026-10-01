"""Grants catalog — file-backed, editable without code changes."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

_DATA = Path(__file__).resolve().parent / "data" / "grants.json"


def load_grants() -> List[Dict[str, Any]]:
    if not _DATA.exists():
        return []
    with _DATA.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, list) else []


def list_grants(fit: Optional[str] = None, q: Optional[str] = None) -> Dict[str, Any]:
    grants = load_grants()
    if fit:
        grants = [g for g in grants if str(g.get("fit", "")).lower() == fit.lower()]
    if q:
        ql = q.lower()
        grants = [
            g
            for g in grants
            if ql in json.dumps(g).lower()
        ]
    return {
        "grants": grants,
        "count": len(grants),
        "source": str(_DATA),
        "status": "OK",
    }


def get_grant(grant_id: str) -> Dict[str, Any]:
    for g in load_grants():
        if g.get("id") == grant_id:
            return {"grant": g, "status": "OK"}
    return {"error": "Grant not found", "status": "ERROR"}
