"""
SQLite persistence for Sovereign Books MVP.

Roadmap: SQLite now → PostgreSQL before launch.
"""

from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Optional

_REPO_ROOT = Path(__file__).resolve().parent.parent
_DEFAULT_DB = _REPO_ROOT / "data" / "sovereign_books.db"

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS businesses (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS plaid_items (
    id TEXT PRIMARY KEY,
    business_id TEXT NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    item_id TEXT NOT NULL UNIQUE,
    access_token TEXT NOT NULL,
    institution_id TEXT,
    institution_name TEXT,
    status TEXT NOT NULL DEFAULT 'CONNECTED',
    sync_cursor TEXT,
    last_synced_at TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS bank_accounts (
    id TEXT PRIMARY KEY,
    plaid_item_id TEXT NOT NULL REFERENCES plaid_items(id) ON DELETE CASCADE,
    business_id TEXT NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    plaid_account_id TEXT NOT NULL,
    name TEXT NOT NULL,
    official_name TEXT,
    mask TEXT,
    type TEXT,
    subtype TEXT,
    current_balance REAL DEFAULT 0,
    available_balance REAL,
    currency TEXT DEFAULT 'USD',
    UNIQUE(plaid_item_id, plaid_account_id)
);

CREATE TABLE IF NOT EXISTS transactions (
    id TEXT PRIMARY KEY,
    bank_account_id TEXT NOT NULL REFERENCES bank_accounts(id) ON DELETE CASCADE,
    business_id TEXT NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    plaid_transaction_id TEXT NOT NULL UNIQUE,
    date TEXT NOT NULL,
    name TEXT NOT NULL,
    merchant_name TEXT,
    amount REAL NOT NULL,
    pending INTEGER NOT NULL DEFAULT 0,
    category_suggested TEXT,
    category_confirmed TEXT,
    status TEXT NOT NULL DEFAULT 'inbox',
    gl_entry_id TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_transactions_business_status
    ON transactions(business_id, status);
CREATE INDEX IF NOT EXISTS idx_transactions_date
    ON transactions(date);

CREATE TABLE IF NOT EXISTS ledger_accounts (
    business_id TEXT NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    code TEXT NOT NULL,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    debits REAL NOT NULL DEFAULT 0,
    credits REAL NOT NULL DEFAULT 0,
    PRIMARY KEY (business_id, code)
);

CREATE TABLE IF NOT EXISTS journal_entries (
    id TEXT PRIMARY KEY,
    business_id TEXT NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    description TEXT NOT NULL,
    entry_type TEXT NOT NULL DEFAULT 'MANUAL',
    reference TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS journal_lines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_id TEXT NOT NULL REFERENCES journal_entries(id) ON DELETE CASCADE,
    account_code TEXT NOT NULL,
    debit REAL NOT NULL DEFAULT 0,
    credit REAL NOT NULL DEFAULT 0
);
"""

# Minimal SMB chart — not the demo enterprise COA
SMB_CHART_OF_ACCOUNTS = [
    ("1010", "Cash & Cash Equivalents", "ASSET"),
    ("1100", "Bank Checking", "ASSET"),
    ("1200", "Accounts Receivable", "ASSET"),
    ("2010", "Accounts Payable", "LIABILITY"),
    ("2100", "Credit Card Payable", "LIABILITY"),
    ("3010", "Owner Equity", "EQUITY"),
    ("4010", "Sales Income", "REVENUE"),
    ("4020", "Other Income", "REVENUE"),
    ("5010", "Cost of Goods Sold", "EXPENSE"),
    ("6010", "Office & Software", "EXPENSE"),
    ("6020", "Cloud Hosting", "EXPENSE"),
    ("6030", "Travel & Meals", "EXPENSE"),
    ("6040", "Marketing", "EXPENSE"),
    ("6050", "Utilities", "EXPENSE"),
    ("6060", "Uncategorized Expense", "EXPENSE"),
]


def resolve_db_path(db_path: Optional[str] = None) -> Path:
    if db_path:
        return Path(db_path)
    env = os.environ.get("SOVEREIGN_BOOKS_DB")
    if env:
        return Path(env)
    return _DEFAULT_DB


def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    path = resolve_db_path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path), timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def db_session(db_path: Optional[str] = None) -> Iterator[sqlite3.Connection]:
    conn = get_connection(db_path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db(db_path: Optional[str] = None) -> Path:
    path = resolve_db_path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with db_session(str(path)) as conn:
        conn.executescript(SCHEMA_SQL)
    return path
