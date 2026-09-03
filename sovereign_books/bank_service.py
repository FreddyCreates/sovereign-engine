"""
Bank connect + sync service for Sovereign Books MVP.

Flow:
  1. ensure_demo_workspace() — create demo user/business if needed
  2. create_link_token() — start Plaid Link (or mock)
  3. exchange_and_connect() — store item + accounts
  4. sync_transactions() — import feed into inbox + optional GL cash posts
"""

from __future__ import annotations

import os
import uuid
from typing import Any, Dict, List, Optional

from .db import db_session, init_db
from .ledger_store import PersistentLedger
from .plaid_client import PlaidClient

# Map suggested category names → ledger codes
CATEGORY_TO_ACCOUNT = {
    "Sales Income": "4010",
    "Other Income": "4020",
    "Cloud Hosting": "6020",
    "Office & Software": "6010",
    "Travel & Meals": "6030",
    "Marketing": "6040",
    "Utilities": "6050",
    "Cost of Goods Sold": "5010",
    "Uncategorized Expense": "6060",
}


class BankService:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path
        init_db(db_path)
        self.plaid = PlaidClient()

    def _conn(self):
        return db_session(self.db_path)

    def ensure_demo_workspace(self) -> Dict[str, str]:
        email = os.environ.get("SOVEREIGN_DEMO_EMAIL", "owner@sovereign.local")
        biz_name = os.environ.get("SOVEREIGN_DEMO_BUSINESS", "Sovereign Demo Co")
        with self._conn() as conn:
            user = conn.execute(
                "SELECT id FROM users WHERE email = ?", (email,)
            ).fetchone()
            if user:
                user_id = user["id"]
            else:
                user_id = f"usr_{uuid.uuid4().hex[:10]}"
                conn.execute(
                    "INSERT INTO users (id, email) VALUES (?, ?)", (user_id, email)
                )

            biz = conn.execute(
                "SELECT id FROM businesses WHERE user_id = ? ORDER BY created_at LIMIT 1",
                (user_id,),
            ).fetchone()
            if biz:
                business_id = biz["id"]
            else:
                business_id = f"biz_{uuid.uuid4().hex[:10]}"
                conn.execute(
                    "INSERT INTO businesses (id, user_id, name) VALUES (?, ?, ?)",
                    (business_id, user_id, biz_name),
                )
            conn.commit()

        PersistentLedger(business_id, self.db_path)
        return {"user_id": user_id, "business_id": business_id, "email": email, "business_name": biz_name}

    def create_link_token(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        ws = self.ensure_demo_workspace()
        uid = user_id or ws["user_id"]
        token = self.plaid.create_link_token(uid)
        token["user_id"] = uid
        token["business_id"] = ws["business_id"]
        return token

    def exchange_and_connect(
        self,
        public_token: str,
        business_id: Optional[str] = None,
        institution_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        ws = self.ensure_demo_workspace()
        bid = business_id or ws["business_id"]

        # Free tier: one connected bank item unless Pro (RevenueCat / local)
        with self._conn() as conn:
            existing = conn.execute(
                "SELECT COUNT(*) AS c FROM plaid_items WHERE business_id = ? AND status = 'CONNECTED'",
                (bid,),
            ).fetchone()["c"]
        if existing >= 1:
            from .revenuecat import RevenueCatService

            ent = RevenueCatService(self.db_path).get_entitlements()
            if not ent.get("pro_active"):
                return {
                    "status": "ERROR",
                    "error": "Free tier allows 1 bank. Activate Pro (RevenueCat or scripts/activate_pro.py).",
                    "pro_required": True,
                    "feature": "unlimited_bank_accounts",
                }

        exchanged = self.plaid.exchange_public_token(public_token)
        if institution_name:
            exchanged["institution_name"] = institution_name

        access_token = exchanged["access_token"]
        item_id = exchanged["item_id"]
        plaid_item_pk = f"pi_{uuid.uuid4().hex[:12]}"

        accounts = self.plaid.get_accounts(access_token)
        stored_accounts: List[Dict[str, Any]] = []

        with self._conn() as conn:
            # Replace prior connection for same institution name in MVP (one bank focus)
            conn.execute(
                """
                INSERT INTO plaid_items
                    (id, business_id, item_id, access_token, institution_id,
                     institution_name, status, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, 'CONNECTED', datetime('now'))
                """,
                (
                    plaid_item_pk,
                    bid,
                    item_id,
                    access_token,
                    exchanged.get("institution_id"),
                    exchanged.get("institution_name") or institution_name or "Connected Bank",
                ),
            )
            for acc in accounts:
                acc_pk = f"ba_{uuid.uuid4().hex[:12]}"
                bal = acc.get("balances") or {}
                conn.execute(
                    """
                    INSERT INTO bank_accounts
                        (id, plaid_item_id, business_id, plaid_account_id, name,
                         official_name, mask, type, subtype, current_balance,
                         available_balance, currency)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        acc_pk,
                        plaid_item_pk,
                        bid,
                        acc["account_id"],
                        acc["name"],
                        acc.get("official_name"),
                        acc.get("mask"),
                        acc.get("type"),
                        acc.get("subtype"),
                        float(bal.get("current") or 0),
                        bal.get("available"),
                        bal.get("iso_currency_code") or "USD",
                    ),
                )
                stored_accounts.append(
                    {
                        "id": acc_pk,
                        "name": acc["name"],
                        "mask": acc.get("mask"),
                        "type": acc.get("type"),
                        "subtype": acc.get("subtype"),
                        "current_balance": float(bal.get("current") or 0),
                        "plaid_account_id": acc["account_id"],
                    }
                )
            conn.commit()

        return {
            "status": "CONNECTED",
            "mode": exchanged.get("mode", self.plaid.mode),
            "plaid_item_id": plaid_item_pk,
            "item_id": item_id,
            "institution_name": exchanged.get("institution_name") or institution_name,
            "business_id": bid,
            "accounts": stored_accounts,
            "account_count": len(stored_accounts),
        }

    def sync_transactions(
        self,
        business_id: Optional[str] = None,
        plaid_item_id: Optional[str] = None,
        post_to_ledger: bool = False,
    ) -> Dict[str, Any]:
        ws = self.ensure_demo_workspace()
        bid = business_id or ws["business_id"]

        with self._conn() as conn:
            if plaid_item_id:
                item = conn.execute(
                    "SELECT * FROM plaid_items WHERE id = ? AND business_id = ?",
                    (plaid_item_id, bid),
                ).fetchone()
            else:
                item = conn.execute(
                    """
                    SELECT * FROM plaid_items
                    WHERE business_id = ? AND status = 'CONNECTED'
                    ORDER BY created_at DESC LIMIT 1
                    """,
                    (bid,),
                ).fetchone()
            if not item:
                return {"status": "ERROR", "error": "No connected bank. Connect a bank first."}

            accounts = conn.execute(
                "SELECT * FROM bank_accounts WHERE plaid_item_id = ?",
                (item["id"],),
            ).fetchall()

        if not accounts:
            return {"status": "ERROR", "error": "Connected item has no accounts."}

        checking = next(
            (a for a in accounts if (a["subtype"] or "").lower() == "checking"),
            accounts[0],
        )
        credit = next(
            (a for a in accounts if (a["type"] or "").lower() == "credit"),
            None,
        )
        plaid_to_local = {a["plaid_account_id"]: a for a in accounts}

        raw_txns = self.plaid.get_transactions(item["access_token"])
        imported = 0
        skipped = 0
        pending_ledger: List[Dict[str, Any]] = []

        with self._conn() as conn:
            for t in raw_txns:
                plaid_acc = t.get("account_id")
                if plaid_acc and plaid_acc in plaid_to_local:
                    local_acc = plaid_to_local[plaid_acc]
                elif t.get("_prefer_checking", True):
                    local_acc = checking
                else:
                    local_acc = credit or checking

                existing = conn.execute(
                    "SELECT id FROM transactions WHERE plaid_transaction_id = ?",
                    (t["transaction_id"],),
                ).fetchone()
                if existing:
                    skipped += 1
                    continue

                txn_id = f"txn_{uuid.uuid4().hex[:12]}"
                suggested = t.get("category") or "Uncategorized Expense"
                conn.execute(
                    """
                    INSERT INTO transactions
                        (id, bank_account_id, business_id, plaid_transaction_id,
                         date, name, merchant_name, amount, pending,
                         category_suggested, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'inbox')
                    """,
                    (
                        txn_id,
                        local_acc["id"],
                        bid,
                        t["transaction_id"],
                        t["date"],
                        t["name"],
                        t.get("merchant_name"),
                        float(t["amount"]),
                        1 if t.get("pending") else 0,
                        suggested,
                    ),
                )
                imported += 1
                if post_to_ledger and not t.get("pending"):
                    pending_ledger.append(
                        {"txn_id": txn_id, "txn": t, "suggested": suggested}
                    )

            # Refresh balances from Plaid accounts snapshot
            for acc in self.plaid.get_accounts(item["access_token"]):
                bal = acc.get("balances") or {}
                conn.execute(
                    """
                    UPDATE bank_accounts
                    SET current_balance = ?, available_balance = ?
                    WHERE plaid_item_id = ? AND plaid_account_id = ?
                    """,
                    (
                        float(bal.get("current") or 0),
                        bal.get("available"),
                        item["id"],
                        acc["account_id"],
                    ),
                )

            conn.execute(
                """
                UPDATE plaid_items
                SET last_synced_at = datetime('now'), updated_at = datetime('now')
                WHERE id = ?
                """,
                (item["id"],),
            )
            conn.commit()

        # Post GL after txn connection is released (avoid SQLite write lock)
        ledger = PersistentLedger(bid, self.db_path) if post_to_ledger else None
        if ledger and pending_ledger:
            for item_post in pending_ledger:
                entry_id = self._post_txn_to_ledger(
                    ledger,
                    item_post["txn_id"],
                    item_post["txn"],
                    item_post["suggested"],
                )
                with self._conn() as conn:
                    conn.execute(
                        "UPDATE transactions SET gl_entry_id = ? WHERE id = ?",
                        (entry_id, item_post["txn_id"]),
                    )
                    conn.commit()

        return {
            "status": "SYNCED",
            "mode": self.plaid.mode,
            "plaid_item_id": item["id"],
            "business_id": bid,
            "imported": imported,
            "skipped_duplicates": skipped,
            "inbox_count": self.inbox_count(bid),
            "cash_balance": self.cash_balance(bid),
            "trial_balance_ok": ledger.trial_balance_ok() if ledger else None,
        }

    def _post_txn_to_ledger(
        self,
        ledger: PersistentLedger,
        txn_id: str,
        t: Dict[str, Any],
        suggested: str,
    ) -> str:
        """
        Plaid convention: positive amount = money leaving depository account.
        Debit expense (or credit revenue), credit/debit cash accordingly.
        """
        amount = abs(float(t["amount"]))
        is_outflow = float(t["amount"]) > 0
        cash_code = "1100"

        if is_outflow:
            expense_code = CATEGORY_TO_ACCOUNT.get(suggested, "6060")
            if suggested in ("Sales Income", "Other Income"):
                expense_code = "6060"
            entry = ledger.record_journal_entry(
                description=t["name"],
                debits={expense_code: amount},
                credits={cash_code: amount},
                entry_type="BANK_SYNC",
                reference=txn_id,
            )
        else:
            revenue_code = CATEGORY_TO_ACCOUNT.get(suggested, "4020")
            if suggested not in ("Sales Income", "Other Income"):
                revenue_code = "4010"
            entry = ledger.record_journal_entry(
                description=t["name"],
                debits={cash_code: amount},
                credits={revenue_code: amount},
                entry_type="BANK_SYNC",
                reference=txn_id,
            )
        return entry["entry_id"]

    def list_connections(self, business_id: Optional[str] = None) -> Dict[str, Any]:
        ws = self.ensure_demo_workspace()
        bid = business_id or ws["business_id"]
        with self._conn() as conn:
            items = conn.execute(
                """
                SELECT id, institution_name, status, last_synced_at, created_at
                FROM plaid_items WHERE business_id = ?
                ORDER BY created_at DESC
                """,
                (bid,),
            ).fetchall()
            accounts = conn.execute(
                """
                SELECT id, name, mask, type, subtype, current_balance, available_balance,
                       plaid_item_id
                FROM bank_accounts WHERE business_id = ?
                """,
                (bid,),
            ).fetchall()
        return {
            "business_id": bid,
            "mode": self.plaid.mode,
            "connections": [dict(i) for i in items],
            "accounts": [dict(a) for a in accounts],
            "cash_balance": self.cash_balance(bid),
            "inbox_count": self.inbox_count(bid),
        }

    def list_inbox(
        self, business_id: Optional[str] = None, limit: int = 50
    ) -> Dict[str, Any]:
        ws = self.ensure_demo_workspace()
        bid = business_id or ws["business_id"]
        with self._conn() as conn:
            rows = conn.execute(
                """
                SELECT t.id, t.date, t.name, t.merchant_name, t.amount, t.pending,
                       t.category_suggested, t.status, ba.name AS account_name, ba.mask
                FROM transactions t
                JOIN bank_accounts ba ON ba.id = t.bank_account_id
                WHERE t.business_id = ? AND t.status = 'inbox'
                ORDER BY t.date DESC
                LIMIT ?
                """,
                (bid, limit),
            ).fetchall()
        return {
            "business_id": bid,
            "count": len(rows),
            "transactions": [dict(r) for r in rows],
        }

    def inbox_count(self, business_id: str) -> int:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT COUNT(*) AS c FROM transactions WHERE business_id = ? AND status = 'inbox'",
                (business_id,),
            ).fetchone()
        return int(row["c"])

    def cash_balance(self, business_id: str) -> float:
        with self._conn() as conn:
            row = conn.execute(
                """
                SELECT COALESCE(SUM(current_balance), 0) AS bal
                FROM bank_accounts
                WHERE business_id = ? AND LOWER(COALESCE(type, '')) = 'depository'
                """,
                (business_id,),
            ).fetchone()
        return round(float(row["bal"]), 2)

    def home_snapshot(self, business_id: Optional[str] = None) -> Dict[str, Any]:
        ws = self.ensure_demo_workspace()
        bid = business_id or ws["business_id"]
        connections = self.list_connections(bid)
        ledger = PersistentLedger(bid, self.db_path)
        connected = any(c["status"] == "CONNECTED" for c in connections["connections"])
        return {
            "business_id": bid,
            "business_name": ws["business_name"],
            "mode": self.plaid.mode,
            "bank_connected": connected,
            "cash_balance": self.cash_balance(bid),
            "inbox_count": self.inbox_count(bid),
            "accounts": connections["accounts"],
            "connections": connections["connections"],
            "ledger_accounts": ledger.list_accounts(),
            "trial_balance_ok": ledger.trial_balance_ok(),
            "cash_series": self.cash_series(bid)["points"],
            "categories": list(CATEGORY_TO_ACCOUNT.keys()),
            "status": "OK",
        }

    def cash_series(self, business_id: Optional[str] = None) -> Dict[str, Any]:
        """Monthly cash path from stored transactions (Plaid: +amount = outflow)."""
        ws = self.ensure_demo_workspace()
        bid = business_id or ws["business_id"]
        running = float(self.cash_balance(bid))
        with self._conn() as conn:
            rows = conn.execute(
                """
                SELECT substr(date, 1, 7) AS month, SUM(amount) AS amt_sum
                FROM transactions
                WHERE business_id = ?
                GROUP BY substr(date, 1, 7)
                ORDER BY month ASC
                """,
                (bid,),
            ).fetchall()
        months = [
            {"month": r["month"], "flow": round(-float(r["amt_sum"]), 2)} for r in rows
        ]
        points: List[Dict[str, Any]] = []
        if months:
            total_flow = sum(m["flow"] for m in months)
            cursor = round(running - total_flow, 2)
            for m in months:
                cursor = round(cursor + m["flow"], 2)
                points.append({"month": m["month"], "cash": cursor, "flow": m["flow"]})
        if not points:
            points = [{"month": "now", "cash": running, "flow": 0.0}]
        return {
            "business_id": bid,
            "points": points,
            "cash_balance": running,
            "status": "OK",
        }

    def confirm_transaction(
        self,
        txn_id: str,
        category: Optional[str] = None,
        business_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Confirm inbox item category; post to GL if not already posted."""
        ws = self.ensure_demo_workspace()
        bid = business_id or ws["business_id"]
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM transactions WHERE id = ? AND business_id = ?",
                (txn_id, bid),
            ).fetchone()
            if not row:
                return {"status": "ERROR", "error": "Transaction not found"}
            cat = category or row["category_suggested"] or "Uncategorized Expense"
            if cat not in CATEGORY_TO_ACCOUNT:
                return {
                    "status": "ERROR",
                    "error": f"Unknown category '{cat}'",
                    "categories": list(CATEGORY_TO_ACCOUNT.keys()),
                }
            conn.execute(
                """
                UPDATE transactions
                SET category_confirmed = ?, status = 'confirmed'
                WHERE id = ?
                """,
                (cat, txn_id),
            )
            gl_entry_id = row["gl_entry_id"]
            pending = bool(row["pending"])
            txn_payload = {
                "name": row["name"],
                "amount": row["amount"],
                "pending": False,
            }

        if not gl_entry_id and not pending:
            ledger = PersistentLedger(bid, self.db_path)
            entry_id = self._post_txn_to_ledger(ledger, txn_id, txn_payload, cat)
            with self._conn() as conn:
                conn.execute(
                    "UPDATE transactions SET gl_entry_id = ? WHERE id = ?",
                    (entry_id, txn_id),
                )
            gl_entry_id = entry_id

        return {
            "status": "CONFIRMED",
            "txn_id": txn_id,
            "category": cat,
            "gl_entry_id": gl_entry_id,
            "inbox_count": self.inbox_count(bid),
        }

    def list_categories(self) -> Dict[str, Any]:
        return {
            "categories": [
                {"name": name, "account_code": code}
                for name, code in CATEGORY_TO_ACCOUNT.items()
            ],
            "status": "OK",
        }
