"""
Persistent double-entry ledger for Sovereign Books.

Promotes the in-memory GeneralLedgerEngine pattern to SQLite while keeping
the same debit == credit invariant.
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional

from .db import SMB_CHART_OF_ACCOUNTS, db_session


class PersistentLedger:
    def __init__(self, business_id: str, db_path: Optional[str] = None):
        self.business_id = business_id
        self.db_path = db_path
        self.ensure_chart_of_accounts()

    def _conn(self):
        return db_session(self.db_path)

    def ensure_chart_of_accounts(self) -> None:
        with self._conn() as conn:
            for code, name, acc_type in SMB_CHART_OF_ACCOUNTS:
                conn.execute(
                    """
                    INSERT OR IGNORE INTO ledger_accounts
                        (business_id, code, name, type, debits, credits)
                    VALUES (?, ?, ?, ?, 0, 0)
                    """,
                    (self.business_id, code, name, acc_type),
                )
            conn.commit()

    def get_account_balance(self, account_code: str) -> float:
        with self._conn() as conn:
            row = conn.execute(
                """
                SELECT type, debits, credits FROM ledger_accounts
                WHERE business_id = ? AND code = ?
                """,
                (self.business_id, account_code),
            ).fetchone()
        if not row:
            raise KeyError(f"Account '{account_code}' not found")
        if row["type"] in ("ASSET", "EXPENSE"):
            return round(row["debits"] - row["credits"], 2)
        return round(row["credits"] - row["debits"], 2)

    def list_accounts(self) -> List[Dict[str, Any]]:
        with self._conn() as conn:
            rows = conn.execute(
                """
                SELECT code, name, type, debits, credits
                FROM ledger_accounts WHERE business_id = ?
                ORDER BY code
                """,
                (self.business_id,),
            ).fetchall()
        out = []
        for r in rows:
            bal = (
                round(r["debits"] - r["credits"], 2)
                if r["type"] in ("ASSET", "EXPENSE")
                else round(r["credits"] - r["debits"], 2)
            )
            out.append(
                {
                    "code": r["code"],
                    "name": r["name"],
                    "type": r["type"],
                    "balance": bal,
                }
            )
        return out

    def record_journal_entry(
        self,
        description: str,
        debits: Dict[str, float],
        credits: Dict[str, float],
        entry_type: str = "BANK_SYNC",
        reference: Optional[str] = None,
    ) -> Dict[str, Any]:
        total_debit = round(sum(debits.values()), 2)
        total_credit = round(sum(credits.values()), 2)
        if total_debit != total_credit:
            raise ValueError(
                f"Double-entry error: Debits (${total_debit:.2f}) != Credits (${total_credit:.2f})"
            )

        entry_id = f"JE-{uuid.uuid4().hex[:10]}"
        with self._conn() as conn:
            for code in list(debits) + list(credits):
                exists = conn.execute(
                    "SELECT 1 FROM ledger_accounts WHERE business_id = ? AND code = ?",
                    (self.business_id, code),
                ).fetchone()
                if not exists:
                    raise KeyError(f"Account '{code}' not found")

            conn.execute(
                """
                INSERT INTO journal_entries
                    (id, business_id, description, entry_type, reference)
                VALUES (?, ?, ?, ?, ?)
                """,
                (entry_id, self.business_id, description, entry_type, reference),
            )
            for code, amt in debits.items():
                amt = round(amt, 2)
                conn.execute(
                    """
                    UPDATE ledger_accounts SET debits = debits + ?
                    WHERE business_id = ? AND code = ?
                    """,
                    (amt, self.business_id, code),
                )
                conn.execute(
                    """
                    INSERT INTO journal_lines (entry_id, account_code, debit, credit)
                    VALUES (?, ?, ?, 0)
                    """,
                    (entry_id, code, amt),
                )
            for code, amt in credits.items():
                amt = round(amt, 2)
                conn.execute(
                    """
                    UPDATE ledger_accounts SET credits = credits + ?
                    WHERE business_id = ? AND code = ?
                    """,
                    (amt, self.business_id, code),
                )
                conn.execute(
                    """
                    INSERT INTO journal_lines (entry_id, account_code, debit, credit)
                    VALUES (?, ?, 0, ?)
                    """,
                    (entry_id, code, amt),
                )
            conn.commit()

        return {
            "entry_id": entry_id,
            "description": description,
            "entry_type": entry_type,
            "reference": reference,
            "total": total_debit,
            "status": "POSTED",
        }

    def trial_balance_ok(self) -> bool:
        with self._conn() as conn:
            row = conn.execute(
                """
                SELECT COALESCE(SUM(debits), 0) AS d, COALESCE(SUM(credits), 0) AS c
                FROM ledger_accounts WHERE business_id = ?
                """,
                (self.business_id,),
            ).fetchone()
        return round(row["d"], 2) == round(row["c"], 2)
