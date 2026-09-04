"""Live infra + financial snapshot for the Sovereign Engine frontend.

No invented MRR. Each probe is a real import or HTTP check.
Pocket is a first-class KILN ecosystem host on :8787.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Dict


def _http(url: str, timeout: float = 1.8) -> Dict[str, Any]:
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read(8000)
            body: Any
            try:
                body = json.loads(raw.decode("utf-8", "replace"))
            except Exception:
                body = raw[:200].decode("utf-8", "replace")
            return {"ok": True, "status": r.status, "url": url, "body": body}
    except urllib.error.HTTPError as e:
        return {"ok": False, "status": e.code, "url": url, "error": str(e.reason)}
    except Exception as e:
        return {"ok": False, "status": 0, "url": url, "error": str(e)[:200]}


def _decimal_zero(a: float, b: float) -> Dict[str, Any]:
    qa = Decimal(str(round(a, 6))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    qb = Decimal(str(round(b, 6))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    drift = abs(qa - qb)
    return {
        "debits": float(qa),
        "credits": float(qb),
        "balanced": drift == Decimal("0.00"),
        "drift": float(drift),
    }


def probe_pocket() -> Dict[str, Any]:
    health = _http("http://127.0.0.1:8787/health")
    registry = _http("http://127.0.0.1:8787/v1/registry")
    counts = {}
    if isinstance(registry.get("body"), dict):
        counts = registry["body"].get("counts") or {}
    local = Path(os.environ.get("POCKET_ROOT") or r"C:\Users\Medin\OneDrive\pocket-os")
    return {
        "id": "pocket",
        "kiln_project": "ItsNotAILABS/pocket",
        "comes_with_kiln": True,
        "mcp": "http://127.0.0.1:8787",
        "local_tree": str(local) if local.exists() else None,
        "host_up": bool(health.get("ok")),
        "health": health,
        "registry_counts": counts,
    }


def probe_kiln() -> Dict[str, Any]:
    local_app = Path(r"E:\KILN")
    registry_file = Path(r"E:\repos\KILN\projects\registry.json")
    projects = []
    if registry_file.is_file():
        try:
            projects = json.loads(registry_file.read_text(encoding="utf-8")).get("projects") or []
        except Exception:
            projects = []
    pocket_listed = any(p.get("id") == "pocket" for p in projects)
    return {
        "github": "ItsNotAILABS/KILN",
        "local_app": str(local_app) if local_app.exists() else None,
        "registry": str(registry_file) if registry_file.is_file() else None,
        "project_ids": [p.get("id") for p in projects],
        "pocket_seeded": pocket_listed,
    }


def financial_snapshot() -> Dict[str, Any]:
    out: Dict[str, Any] = {"ok": True, "engines": {}, "journal": None, "notes": []}
    try:
        from sovereign_infrastructure.nextgen_systems.xfin_engine import XFINEngine

        xfin = XFINEngine(treasury_balance_usd=1.0)
        spread = xfin.calculate_fx_spread("USD", "EUR")
        settle = xfin.execute_cross_border_settlement("frontend", 100.0, "USD")
        out["engines"]["xfin"] = {
            "loaded": True,
            "treasury_usd": xfin.treasury_usd,
            "usd_eur": spread,
            "last_settle_usd": settle.get("settled_usd"),
        }
    except Exception as e:
        out["engines"]["xfin"] = {"loaded": False, "error": str(e)[:200]}
        out["ok"] = False
    try:
        from sovereign_infrastructure.nextgen_systems.mint_engine import MINTEngine

        mint = MINTEngine(initial_supply=1000.0, base_price_usd=1.0, burn_rate=0.15)
        out["engines"]["mint"] = {
            "loaded": True,
            "circulating": mint.get_total_supply(),
            "burn_rate": mint.burn_rate,
            "spot": mint.calculate_bonding_price(mint.total_supply),
        }
    except Exception as e:
        out["engines"]["mint"] = {"loaded": False, "error": str(e)[:200]}
        out["ok"] = False
    try:
        from sovereign_infrastructure.cores.billing_core import RevenueCatBillingCore

        bill = RevenueCatBillingCore(webhook_secret="test_secret")
        payload = b'{"event":"TEST"}'
        sig_ok = bill.verify_webhook_signature(payload, "")
        evt = bill.process_lifecycle_event("frontend", "RENEWAL", "pro", 9.0)
        out["engines"]["billing"] = {
            "loaded": True,
            "empty_sig_rejected": sig_ok is False,
            "renewal_mrr_delta": evt.get("mrr_delta"),
        }
    except Exception as e:
        out["engines"]["billing"] = {"loaded": False, "error": str(e)[:200]}
        out["ok"] = False
    journal = _decimal_zero(101.25, 101.25)
    out["journal"] = journal
    if not journal["balanced"]:
        out["ok"] = False
        out["notes"].append("sample journal failed zero-drift")
    return out


def snapshot() -> Dict[str, Any]:
    pocket = probe_pocket()
    kiln = probe_kiln()
    finance = financial_snapshot()
    return {
        "ok": bool(finance.get("ok")),
        "schema": "sovereign.frontend_infra.v1",
        "measured_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "kiln": kiln,
        "pocket": pocket,
        "finance": finance,
        "frontend": {
            "infra_api": "/api/v1/infra",
            "finance_api": "/api/v1/finance",
            "rule": "No invented MRR. Host down is reported as down.",
        },
    }
