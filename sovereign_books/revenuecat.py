"""
RevenueCat entitlement bridge for Sovereign Books Pro.

Live mode: GET /v1/subscribers/{app_user_id} with REVENUECAT_SECRET_API_KEY.
Offline mode: local SQLite entitlements table + scripts/activate_pro.py.

How to tie in RevenueCat (product path):
1. Create a RevenueCat project + entitlement `pro_access` (or REVENUECAT_ENTITLEMENT_ID).
2. Add products: sovereign_pro_monthly, sovereign_pro_annual.
3. Mobile: Purchases.configure(REVENUECAT_PUBLIC_SDK_KEY) — Android already scaffolded.
4. Web: use RevenueCat Web Billing / Stripe offerings, OR check subscriber via secret API
   after checkout; this service is the server-side source of truth for gating.
5. Webhooks: POST /api/v1/books/revenuecat/webhook with Authorization Bearer
   REVENUECAT_WEBHOOK_AUTH (optional) to sync INITIAL_PURCHASE / RENEWAL / EXPIRATION.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional

from .db import db_session, init_db

DEFAULT_ENTITLEMENT = "pro_access"
PRO_FEATURES = [
    "unlimited_bank_accounts",
    "ai_categorization",
    "runway_alerts",
    "accountant_export",
]


class RevenueCatService:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path
        init_db(db_path)
        self._ensure_table()
        self.secret = os.environ.get("REVENUECAT_SECRET_API_KEY") or os.environ.get(
            "REVENUECAT_API_KEY"
        )
        self.entitlement_id = os.environ.get(
            "REVENUECAT_ENTITLEMENT_ID", DEFAULT_ENTITLEMENT
        )
        self.mode = "live" if self.secret else "local"

    def _ensure_table(self) -> None:
        with db_session(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS entitlements (
                    app_user_id TEXT PRIMARY KEY,
                    entitlements_json TEXT NOT NULL DEFAULT '[]',
                    pro_active INTEGER NOT NULL DEFAULT 0,
                    source TEXT NOT NULL DEFAULT 'local',
                    product_id TEXT,
                    expires_at TEXT,
                    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
                )
                """
            )

    def get_entitlements(self, app_user_id: Optional[str] = None) -> Dict[str, Any]:
        uid = app_user_id or os.environ.get(
            "REVENUECAT_APP_USER_ID", "books_demo_user"
        )
        if self.mode == "live":
            try:
                remote = self._fetch_subscriber(uid)
                self._cache_local(uid, remote)
                return remote
            except Exception as e:
                local = self._read_local(uid)
                local["warning"] = f"RevenueCat live fetch failed: {e}"
                local["source"] = "local_fallback"
                return local
        return self._read_local(uid)

    def _fetch_subscriber(self, app_user_id: str) -> Dict[str, Any]:
        encoded = urllib.parse.quote(app_user_id, safe="")
        url = f"https://api.revenuecat.com/v1/subscribers/{encoded}"
        req = urllib.request.Request(
            url,
            headers={
                "Authorization": f"Bearer {self.secret}",
                "Content-Type": "application/json",
                "X-Platform": "stripe",
            },
            method="GET",
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.load(resp)
        subscriber = data.get("subscriber") or {}
        ents = subscriber.get("entitlements") or {}
        active: List[str] = []
        expires = None
        product_id = None
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)
        for key, val in ents.items():
            exp = val.get("expires_date")
            active_ent = True
            if exp:
                try:
                    # RevenueCat uses ISO8601; strip Z
                    exp_dt = datetime.fromisoformat(str(exp).replace("Z", "+00:00"))
                    active_ent = exp_dt > now
                except ValueError:
                    active_ent = True
            if not active_ent:
                continue
            active.append(key)
            if key == self.entitlement_id:
                expires = exp
                product_id = val.get("product_identifier")
        pro = self.entitlement_id in active or any(
            k.lower() in ("pro", "pro_access", "sovereign_pro") for k in active
        )
        return {
            "app_user_id": app_user_id,
            "pro_active": bool(pro),
            "entitlements": active,
            "product_id": product_id,
            "expires_at": expires,
            "features": PRO_FEATURES if pro else [],
            "source": "revenuecat",
            "mode": "live",
            "status": "OK",
        }

    def _read_local(self, app_user_id: str) -> Dict[str, Any]:
        with db_session(self.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM entitlements WHERE app_user_id = ?",
                (app_user_id,),
            ).fetchone()
        if not row:
            return {
                "app_user_id": app_user_id,
                "pro_active": False,
                "entitlements": [],
                "features": [],
                "source": "local",
                "mode": self.mode,
                "status": "OK",
                "hint": "Run scripts/activate_pro.py or set REVENUECAT_SECRET_API_KEY",
            }
        ents = json.loads(row["entitlements_json"] or "[]")
        pro = bool(row["pro_active"])
        return {
            "app_user_id": app_user_id,
            "pro_active": pro,
            "entitlements": ents,
            "product_id": row["product_id"],
            "expires_at": row["expires_at"],
            "features": PRO_FEATURES if pro else [],
            "source": row["source"],
            "mode": self.mode,
            "status": "OK",
        }

    def _cache_local(self, app_user_id: str, payload: Dict[str, Any]) -> None:
        with db_session(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO entitlements
                    (app_user_id, entitlements_json, pro_active, source, product_id, expires_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
                ON CONFLICT(app_user_id) DO UPDATE SET
                    entitlements_json = excluded.entitlements_json,
                    pro_active = excluded.pro_active,
                    source = excluded.source,
                    product_id = excluded.product_id,
                    expires_at = excluded.expires_at,
                    updated_at = datetime('now')
                """,
                (
                    app_user_id,
                    json.dumps(payload.get("entitlements") or []),
                    1 if payload.get("pro_active") else 0,
                    payload.get("source") or "revenuecat",
                    payload.get("product_id"),
                    payload.get("expires_at"),
                ),
            )

    def activate_local_pro(
        self,
        app_user_id: Optional[str] = None,
        product_id: str = "sovereign_pro_monthly",
    ) -> Dict[str, Any]:
        """Offline script path — grants Pro without calling RevenueCat."""
        uid = app_user_id or os.environ.get(
            "REVENUECAT_APP_USER_ID", "books_demo_user"
        )
        payload = {
            "app_user_id": uid,
            "pro_active": True,
            "entitlements": [self.entitlement_id],
            "product_id": product_id,
            "expires_at": None,
            "source": "local_script",
            "features": PRO_FEATURES,
            "mode": "local",
            "status": "ACTIVATED",
        }
        self._cache_local(uid, payload)
        return payload

    def deactivate_local_pro(self, app_user_id: Optional[str] = None) -> Dict[str, Any]:
        uid = app_user_id or os.environ.get(
            "REVENUECAT_APP_USER_ID", "books_demo_user"
        )
        payload = {
            "app_user_id": uid,
            "pro_active": False,
            "entitlements": [],
            "product_id": None,
            "expires_at": None,
            "source": "local_script",
            "features": [],
            "mode": "local",
            "status": "DEACTIVATED",
        }
        self._cache_local(uid, payload)
        return payload

    def handle_webhook(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Process RevenueCat webhook-style payloads (simplified)."""
        etype = event.get("type") or event.get("event", {}).get("type")
        ev = event.get("event") or event
        app_user_id = (
            ev.get("app_user_id")
            or ev.get("original_app_user_id")
            or os.environ.get("REVENUECAT_APP_USER_ID", "books_demo_user")
        )
        product_id = ev.get("product_id")
        if etype in (
            "INITIAL_PURCHASE",
            "RENEWAL",
            "UNCANCELLATION",
            "PRODUCT_CHANGE",
            "NON_RENEWING_PURCHASE",
        ):
            return self.activate_local_pro(app_user_id, product_id or "sovereign_pro")
        if etype in ("EXPIRATION", "CANCELLATION"):
            # Cancellation often still entitled until period end — treat EXPIRATION as off
            if etype == "EXPIRATION":
                return self.deactivate_local_pro(app_user_id)
        # refresh from live if possible
        return self.get_entitlements(app_user_id)
