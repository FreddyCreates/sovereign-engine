"""
Approvals log: every decision a person makes on an agent's card.

The mobile app and the web console post here when a user confirms a
category, approves a research-credit claim file, sends an invoice
follow-up, or skips a card. It is the audit trail behind "every action
stays in the log".
"""

from __future__ import annotations

import json
import uuid
from typing import Any, Dict, List, Optional

from .bank_service import BankService
from .db import db_session, init_db

APPROVALS_SCHEMA = """
CREATE TABLE IF NOT EXISTS approvals (
    id TEXT PRIMARY KEY,
    business_id TEXT NOT NULL,
    card_id TEXT NOT NULL,
    kind TEXT NOT NULL,
    decision TEXT NOT NULL,
    subject TEXT,
    amount REAL,
    payload_json TEXT NOT NULL DEFAULT '{}',
    source TEXT NOT NULL DEFAULT 'mobile',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_approvals_business ON approvals(business_id, created_at);
"""

KINDS = {"categorize", "tax_credit", "invoice_chase", "other"}
DECISIONS = {"approved", "skipped", "sent"}


class ApprovalsLog:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path
        init_db(db_path)
        self.bank = BankService(db_path) if db_path else BankService()
        with db_session(db_path) as conn:
            conn.executescript(APPROVALS_SCHEMA)

    def _business(self, business_id: Optional[str]) -> str:
        return business_id or self.bank.ensure_demo_workspace()["business_id"]

    def record(
        self,
        kind: str,
        decision: str,
        card_id: str,
        subject: Optional[str] = None,
        amount: Optional[float] = None,
        payload: Optional[Dict[str, Any]] = None,
        business_id: Optional[str] = None,
        source: str = "mobile",
    ) -> Dict[str, Any]:
        kind = (kind or "other").lower()
        decision = (decision or "").lower()
        if kind not in KINDS:
            return {"status": "ERROR", "error": f"Unknown kind '{kind}'", "kinds": sorted(KINDS)}
        if decision not in DECISIONS:
            return {"status": "ERROR", "error": f"Unknown decision '{decision}'", "decisions": sorted(DECISIONS)}
        if not card_id:
            return {"status": "ERROR", "error": "card_id required"}
        bid = self._business(business_id)
        row_id = f"apr_{uuid.uuid4().hex[:12]}"
        with db_session(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO approvals (id, business_id, card_id, kind, decision, subject, amount, payload_json, source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row_id,
                    bid,
                    card_id,
                    kind,
                    decision,
                    subject,
                    float(amount) if amount is not None else None,
                    json.dumps(payload or {}),
                    source or "mobile",
                ),
            )
        return {"id": row_id, "business_id": bid, "card_id": card_id, "kind": kind, "decision": decision, "status": "OK"}

    def list(self, business_id: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
        bid = self._business(business_id)
        with db_session(self.db_path) as conn:
            rows = conn.execute(
                """
                SELECT id, card_id, kind, decision, subject, amount, source, created_at
                FROM approvals WHERE business_id = ?
                ORDER BY created_at DESC, rowid DESC LIMIT ?
                """,
                (bid, int(limit)),
            ).fetchall()
        items: List[Dict[str, Any]] = [dict(r) for r in rows]
        return {"business_id": bid, "approvals": items, "count": len(items), "status": "OK"}

    def summary(self, business_id: Optional[str] = None) -> Dict[str, Any]:
        bid = self._business(business_id)
        with db_session(self.db_path) as conn:
            rows = conn.execute(
                "SELECT kind, decision, COUNT(*) AS n FROM approvals WHERE business_id = ? GROUP BY kind, decision",
                (bid,),
            ).fetchall()
        out: Dict[str, Dict[str, int]] = {}
        for r in rows:
            out.setdefault(r["kind"], {})[r["decision"]] = int(r["n"])
        return {"business_id": bid, "by_kind": out, "status": "OK"}
