"""
Extended Books features (roadmap 5–24) — reconcile, reports, AR/AP, commerce, multi-biz.
"""

from __future__ import annotations

import csv
import io
import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from .bank_service import BankService
from .db import db_session, init_db
from .ledger_store import PersistentLedger
from .revenuecat import RevenueCatService

EXTENDED_SCHEMA = """
CREATE TABLE IF NOT EXISTS reconciliations (
    id TEXT PRIMARY KEY, business_id TEXT NOT NULL, statement_balance REAL NOT NULL,
    book_balance REAL NOT NULL, difference REAL NOT NULL, status TEXT DEFAULT 'open',
    notes TEXT, created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS invoices (
    id TEXT PRIMARY KEY, business_id TEXT NOT NULL, customer TEXT NOT NULL,
    amount REAL NOT NULL, status TEXT DEFAULT 'open', due_date TEXT,
    gl_entry_id TEXT, created_at TEXT NOT NULL DEFAULT (datetime('now')),
    paid_at TEXT
);
CREATE TABLE IF NOT EXISTS bills (
    id TEXT PRIMARY KEY, business_id TEXT NOT NULL, vendor TEXT NOT NULL,
    amount REAL NOT NULL, status TEXT DEFAULT 'open', due_date TEXT,
    gl_entry_id TEXT, created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS receipts (
    id TEXT PRIMARY KEY, business_id TEXT NOT NULL, merchant TEXT, amount REAL NOT NULL,
    category TEXT, expense_account TEXT DEFAULT '6060',
    image_path TEXT, gl_entry_id TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS commerce_syncs (
    id TEXT PRIMARY KEY, business_id TEXT NOT NULL, provider TEXT NOT NULL,
    external_id TEXT, amount REAL, description TEXT, synced_at TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS category_rules (
    id TEXT PRIMARY KEY, business_id TEXT NOT NULL, match_contains TEXT NOT NULL,
    category TEXT NOT NULL, account_code TEXT, created_at TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS anomaly_flags (
    id TEXT PRIMARY KEY, business_id TEXT NOT NULL, transaction_id TEXT,
    reason TEXT NOT NULL, severity TEXT DEFAULT 'medium',
    created_at TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS tax_buckets (
    id TEXT PRIMARY KEY, business_id TEXT NOT NULL, period TEXT NOT NULL,
    estimated_tax REAL DEFAULT 0, income REAL DEFAULT 0, expense REAL DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS accountant_access (
    id TEXT PRIMARY KEY, business_id TEXT NOT NULL, email TEXT NOT NULL,
    role TEXT DEFAULT 'read_only', created_at TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS month_closes (
    id TEXT PRIMARY KEY, business_id TEXT NOT NULL, period TEXT NOT NULL,
    checklist_json TEXT DEFAULT '[]', status TEXT DEFAULT 'in_progress',
    created_at TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS payroll_links (
    id TEXT PRIMARY KEY, business_id TEXT NOT NULL, provider TEXT NOT NULL,
    status TEXT DEFAULT 'connected', meta_json TEXT DEFAULT '{}',
    created_at TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS runway_alerts (
    id TEXT PRIMARY KEY, business_id TEXT NOT NULL, message TEXT NOT NULL,
    months_runway REAL, created_at TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS report_exports (
    id TEXT PRIMARY KEY, business_id TEXT NOT NULL, report_type TEXT NOT NULL,
    body TEXT NOT NULL, created_at TEXT DEFAULT (datetime('now'))
);
"""


def _uid(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:12]}"


def _row(r) -> Dict[str, Any]:
    return dict(r) if r else {}


class BooksExtended:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path
        init_db(db_path)
        self._ensure_tables()
        self.bank = BankService(db_path)

    def _conn(self):
        return db_session(self.db_path)

    def _ensure_tables(self) -> None:
        with self._conn() as conn:
            conn.executescript(EXTENDED_SCHEMA)

    def _biz(self, business_id: Optional[str] = None) -> str:
        if business_id:
            return business_id
        return self.bank.ensure_demo_workspace()["business_id"]

    def reconcile(self, statement_balance: float, business_id: Optional[str] = None, notes: str = "") -> Dict[str, Any]:
        bid = self._biz(business_id)
        ledger = PersistentLedger(bid, self.db_path)
        try:
            book = ledger.get_account_balance("1100")
        except KeyError:
            book = ledger.get_account_balance("1010")
        diff = round(statement_balance - book, 2)
        rid = _uid("rec_")
        with self._conn() as conn:
            conn.execute(
                """INSERT INTO reconciliations
                   (id,business_id,statement_balance,book_balance,difference,status,notes)
                   VALUES (?,?,?,?,?,?,?)""",
                (rid, bid, statement_balance, book, diff, "matched" if abs(diff) < 0.01 else "open", notes),
            )
        return {
            "id": rid, "statement_balance": statement_balance, "book_balance": book,
            "difference": diff, "status": "OK",
        }

    def pnl_report(self, business_id: Optional[str] = None) -> Dict[str, Any]:
        bid = self._biz(business_id)
        ledger = PersistentLedger(bid, self.db_path)
        accounts = ledger.list_accounts()
        revenue = sum(a["balance"] for a in accounts if a["type"] == "REVENUE")
        expense = sum(a["balance"] for a in accounts if a["type"] == "EXPENSE")
        report = {
            "revenue": round(revenue, 2),
            "expense": round(expense, 2),
            "net_income": round(revenue - expense, 2),
            "lines": [a for a in accounts if a["type"] in ("REVENUE", "EXPENSE")],
        }
        body = json.dumps(report, indent=2)
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO report_exports (id,business_id,report_type,body) VALUES (?,?,?,?)",
                (_uid("rpt_"), bid, "pnl", body),
            )
        return {"report": report, "status": "OK"}

    def balance_sheet_export(self, business_id: Optional[str] = None) -> Dict[str, Any]:
        bid = self._biz(business_id)
        ledger = PersistentLedger(bid, self.db_path)
        accounts = ledger.list_accounts()
        assets = [a for a in accounts if a["type"] == "ASSET"]
        liabilities = [a for a in accounts if a["type"] == "LIABILITY"]
        equity = [a for a in accounts if a["type"] == "EQUITY"]
        report = {
            "assets": assets,
            "liabilities": liabilities,
            "equity": equity,
            "total_assets": round(sum(a["balance"] for a in assets), 2),
            "total_liabilities": round(sum(a["balance"] for a in liabilities), 2),
            "total_equity": round(sum(a["balance"] for a in equity), 2),
        }
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["section", "code", "name", "balance"])
        for section, rows in (("ASSET", assets), ("LIABILITY", liabilities), ("EQUITY", equity)):
            for a in rows:
                writer.writerow([section, a["code"], a["name"], a["balance"]])
        csv_body = buf.getvalue()
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO report_exports (id,business_id,report_type,body) VALUES (?,?,?,?)",
                (_uid("rpt_"), bid, "balance_sheet", csv_body),
            )
        return {"report": report, "csv": csv_body, "status": "OK"}

    def create_invoice(self, customer: str, amount: float, due_date: str = None, business_id: Optional[str] = None) -> Dict[str, Any]:
        bid = self._biz(business_id)
        iid = _uid("inv_")
        with self._conn() as conn:
            conn.execute(
                """INSERT INTO invoices (id,business_id,customer,amount,due_date) VALUES (?,?,?,?,?)""",
                (iid, bid, customer, amount, due_date),
            )
        return {"id": iid, "status": "OK"}

    def mark_invoice_paid(self, invoice_id: str) -> Dict[str, Any]:
        with self._conn() as conn:
            inv = conn.execute("SELECT * FROM invoices WHERE id=?", (invoice_id,)).fetchone()
            if not inv:
                return {"error": "not found", "status": "ERROR"}
            if inv["status"] == "paid":
                return {"id": invoice_id, "already_paid": True, "status": "OK"}
            inv_data = _row(inv)
        ledger = PersistentLedger(inv_data["business_id"], self.db_path)
        entry = ledger.record_journal_entry(
            description=f"Invoice paid {invoice_id}",
            debits={"1100": float(inv_data["amount"])},
            credits={"4010": float(inv_data["amount"])},
            entry_type="INVOICE",
            reference=invoice_id,
        )
        with self._conn() as conn:
            conn.execute(
                "UPDATE invoices SET status='paid', paid_at=datetime('now'), gl_entry_id=? WHERE id=?",
                (entry["entry_id"], invoice_id),
            )
        return {"id": invoice_id, "gl_entry_id": entry["entry_id"], "status": "OK"}

    def list_invoices(self, business_id: Optional[str] = None) -> Dict[str, Any]:
        bid = self._biz(business_id)
        with self._conn() as conn:
            rows = [_row(r) for r in conn.execute(
                "SELECT * FROM invoices WHERE business_id=?", (bid,)
            ).fetchall()]
        return {"invoices": rows, "status": "OK"}

    def create_bill(self, vendor: str, amount: float, due_date: str = None, business_id: Optional[str] = None) -> Dict[str, Any]:
        bid = self._biz(business_id)
        iid = _uid("bill_")
        ledger = PersistentLedger(bid, self.db_path)
        entry = ledger.record_journal_entry(
            description=f"Bill {vendor}",
            debits={"6060": amount},
            credits={"2010": amount},
            entry_type="BILL",
            reference=iid,
        )
        with self._conn() as conn:
            conn.execute(
                """INSERT INTO bills (id,business_id,vendor,amount,due_date,gl_entry_id)
                   VALUES (?,?,?,?,?,?)""",
                (iid, bid, vendor, amount, due_date, entry["entry_id"]),
            )
        return {"id": iid, "gl_entry_id": entry["entry_id"], "status": "OK"}

    def list_bills_due(self, business_id: Optional[str] = None) -> Dict[str, Any]:
        bid = self._biz(business_id)
        with self._conn() as conn:
            rows = [_row(r) for r in conn.execute(
                "SELECT * FROM bills WHERE business_id=? AND status='open' ORDER BY due_date",
                (bid,),
            ).fetchall()]
        return {"bills": rows, "status": "OK"}

    def capture_receipt(
        self, merchant: str, amount: float, category: str = "Uncategorized Expense",
        image_path: str = "", business_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        bid = self._biz(business_id)
        rid = _uid("rcpt_")
        ledger = PersistentLedger(bid, self.db_path)
        entry = ledger.record_journal_entry(
            description=f"Receipt {merchant}",
            debits={"6060": amount},
            credits={"1100": amount},
            entry_type="RECEIPT",
            reference=rid,
        )
        with self._conn() as conn:
            conn.execute(
                """INSERT INTO receipts
                   (id,business_id,merchant,amount,category,image_path,gl_entry_id)
                   VALUES (?,?,?,?,?,?,?)""",
                (rid, bid, merchant, amount, category, image_path, entry["entry_id"]),
            )
        return {"id": rid, "gl_entry_id": entry["entry_id"], "status": "OK"}

    def commerce_sync(self, provider: str, sales: List[Dict[str, Any]], business_id: Optional[str] = None) -> Dict[str, Any]:
        bid = self._biz(business_id)
        ledger = PersistentLedger(bid, self.db_path)
        imported = 0
        for s in sales:
            sid = _uid("com_")
            amt = float(s.get("amount", 0))
            with self._conn() as conn:
                conn.execute(
                    """INSERT INTO commerce_syncs (id,business_id,provider,external_id,amount,description)
                       VALUES (?,?,?,?,?,?)""",
                    (sid, bid, provider, s.get("external_id", sid), amt, s.get("description", provider)),
                )
            if amt:
                ledger.record_journal_entry(
                    description=f"{provider} sale {s.get('external_id', sid)}",
                    debits={"1100": amt},
                    credits={"4010": amt},
                    entry_type="COMMERCE",
                    reference=sid,
                )
                imported += 1
        return {"provider": provider, "imported": imported, "status": "OK"}

    def runway_alerts(self, monthly_burn: float = 5000.0, business_id: Optional[str] = None) -> Dict[str, Any]:
        bid = self._biz(business_id)
        rc = RevenueCatService(self.db_path)
        home = self.bank.home_snapshot(bid)
        cash = float(home.get("cash_balance") or 0)
        months = round(cash / monthly_burn, 2) if monthly_burn else 0
        msg = f"Runway ~{months} months at ${monthly_burn}/mo burn (cash ${cash:,.2f})"
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO runway_alerts (id,business_id,message,months_runway) VALUES (?,?,?,?)",
                (_uid("run_"), bid, msg, months),
            )
        return {
            "message": msg, "months_runway": months, "cash": cash,
            "pro_feature": "runway_alerts" in (rc.get_entitlements().get("features") or [])
            or rc.get_entitlements().get("pro_active"),
            "status": "OK",
        }

    def add_category_rule(self, match_contains: str, category: str, account_code: str = "6060", business_id: Optional[str] = None) -> Dict[str, Any]:
        bid = self._biz(business_id)
        rid = _uid("rule_")
        with self._conn() as conn:
            conn.execute(
                """INSERT INTO category_rules (id,business_id,match_contains,category,account_code)
                   VALUES (?,?,?,?,?)""",
                (rid, bid, match_contains, category, account_code),
            )
        return {"id": rid, "status": "OK"}

    def apply_category_rules(self, business_id: Optional[str] = None) -> Dict[str, Any]:
        bid = self._biz(business_id)
        applied = 0
        with self._conn() as conn:
            rules = conn.execute(
                "SELECT * FROM category_rules WHERE business_id=?", (bid,)
            ).fetchall()
            txns = conn.execute(
                "SELECT id, name, merchant_name FROM transactions WHERE business_id=? AND status='inbox'",
                (bid,),
            ).fetchall()
            for t in txns:
                hay = f"{t['name']} {t['merchant_name'] or ''}".lower()
                for rule in rules:
                    if rule["match_contains"].lower() in hay:
                        conn.execute(
                            "UPDATE transactions SET category_suggested=? WHERE id=?",
                            (rule["category"], t["id"]),
                        )
                        applied += 1
                        break
        return {"applied": applied, "status": "OK"}

    def flag_anomalies(self, business_id: Optional[str] = None, threshold: float = 2000.0) -> Dict[str, Any]:
        bid = self._biz(business_id)
        flagged = []
        with self._conn() as conn:
            txns = conn.execute(
                "SELECT id, name, amount FROM transactions WHERE business_id=?", (bid,)
            ).fetchall()
            for t in txns:
                if abs(float(t["amount"])) >= threshold:
                    aid = _uid("anom_")
                    reason = f"Large amount ${t['amount']} on {t['name']}"
                    conn.execute(
                        """INSERT INTO anomaly_flags (id,business_id,transaction_id,reason,severity)
                           VALUES (?,?,?,?,?)""",
                        (aid, bid, t["id"], reason, "high"),
                    )
                    flagged.append({"id": aid, "transaction_id": t["id"], "reason": reason})
        return {"flags": flagged, "count": len(flagged), "status": "OK"}

    def tax_bucket(self, period: str = None, business_id: Optional[str] = None) -> Dict[str, Any]:
        bid = self._biz(business_id)
        period = period or datetime.utcnow().strftime("%Y-Q") + str((datetime.utcnow().month - 1) // 3 + 1)
        pnl = self.pnl_report(bid)["report"]
        estimated = round(max(0, pnl["net_income"]) * 0.25, 2)
        tid = _uid("tax_")
        with self._conn() as conn:
            conn.execute(
                """INSERT INTO tax_buckets (id,business_id,period,estimated_tax,income,expense)
                   VALUES (?,?,?,?,?,?)""",
                (tid, bid, period, estimated, pnl["revenue"], pnl["expense"]),
            )
        return {"id": tid, "period": period, "estimated_tax": estimated, "status": "OK"}

    def list_businesses(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        ws = self.bank.ensure_demo_workspace()
        uid = user_id or ws["user_id"]
        with self._conn() as conn:
            rows = [_row(r) for r in conn.execute(
                "SELECT * FROM businesses WHERE user_id=?", (uid,)
            ).fetchall()]
        return {"businesses": rows, "active_id": ws["business_id"], "status": "OK"}

    def create_business(self, name: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        ws = self.bank.ensure_demo_workspace()
        uid = user_id or ws["user_id"]
        bid = _uid("biz_")
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO businesses (id,user_id,name) VALUES (?,?,?)", (bid, uid, name)
            )
        PersistentLedger(bid, self.db_path)
        return {"id": bid, "name": name, "status": "OK"}

    def switch_business(self, business_id: str) -> Dict[str, Any]:
        with self._conn() as conn:
            row = conn.execute("SELECT * FROM businesses WHERE id=?", (business_id,)).fetchone()
        if not row:
            return {"error": "not found", "status": "ERROR"}
        # persist preference
        with self._conn() as conn:
            conn.execute(
                """CREATE TABLE IF NOT EXISTS active_business (
                    user_id TEXT PRIMARY KEY, business_id TEXT NOT NULL
                )"""
            )
            conn.execute(
                "INSERT OR REPLACE INTO active_business (user_id,business_id) VALUES (?,?)",
                (row["user_id"], business_id),
            )
        return {"business_id": business_id, "name": row["name"], "status": "OK"}

    def grant_accountant(self, email: str, business_id: Optional[str] = None) -> Dict[str, Any]:
        bid = self._biz(business_id)
        aid = _uid("acct_")
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO accountant_access (id,business_id,email,role) VALUES (?,?,?,?)",
                (aid, bid, email, "read_only"),
            )
        return {"id": aid, "role": "read_only", "status": "OK"}

    def qbo_import_mock(self, csv_text: str, business_id: Optional[str] = None) -> Dict[str, Any]:
        bid = self._biz(business_id)
        reader = csv.DictReader(io.StringIO(csv_text))
        count = 0
        ledger = PersistentLedger(bid, self.db_path)
        for row in reader:
            amt = float(row.get("Amount") or row.get("amount") or 0)
            desc = row.get("Description") or row.get("description") or "QBO import"
            if amt >= 0:
                ledger.record_journal_entry(
                    description=desc, debits={"1100": amt}, credits={"4010": amt},
                    entry_type="QBO_IMPORT",
                )
            else:
                a = abs(amt)
                ledger.record_journal_entry(
                    description=desc, debits={"6060": a}, credits={"1100": a},
                    entry_type="QBO_IMPORT",
                )
            count += 1
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO report_exports (id,business_id,report_type,body) VALUES (?,?,?,?)",
                (_uid("rpt_"), bid, "qbo_import", f"imported={count}"),
            )
        return {"imported": count, "status": "OK"}

    def close_month_run(self, period: str = None, business_id: Optional[str] = None) -> Dict[str, Any]:
        bid = self._biz(business_id)
        period = period or datetime.utcnow().strftime("%Y-%m")
        checklist = [
            "reconcile_bank", "review_inbox", "post_accruals", "export_pnl", "export_balance_sheet",
        ]
        pnl = self.pnl_report(bid)
        bs = self.balance_sheet_export(bid)
        mid = _uid("close_")
        with self._conn() as conn:
            conn.execute(
                """INSERT INTO month_closes (id,business_id,period,checklist_json,status)
                   VALUES (?,?,?,?,?)""",
                (mid, bid, period, json.dumps(checklist), "completed"),
            )
        return {
            "id": mid, "period": period, "checklist": checklist,
            "pnl": pnl["report"], "balance_sheet_exported": bool(bs.get("csv")),
            "status": "OK",
        }

    def payroll_connector_stub(self, provider: str = "gusto", business_id: Optional[str] = None) -> Dict[str, Any]:
        bid = self._biz(business_id)
        pid = _uid("pay_")
        with self._conn() as conn:
            conn.execute(
                """INSERT INTO payroll_links (id,business_id,provider,status,meta_json)
                   VALUES (?,?,?,?,?)""",
                (pid, bid, provider, "connected", json.dumps({"mode": "stub"})),
            )
        return {"id": pid, "provider": provider, "status": "OK"}

    def agency_bill_client(self, client: str, amount: float, business_id: Optional[str] = None) -> Dict[str, Any]:
        inv = self.create_invoice(client, amount, business_id=business_id)
        return {"invoice_id": inv["id"], "agency": True, "status": "OK"}
