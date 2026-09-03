"""
Tests for Sovereign Books MVP — Connect Bank (Phase 0).
"""

import os
import tempfile
import unittest
from pathlib import Path

from sovereign_books.bank_service import BankService
from sovereign_books.db import init_db
from sovereign_books.ledger_store import PersistentLedger
from sovereign_books.plaid_client import PlaidClient


class TestPersistentLedger(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp.close()
        self.db_path = self.tmp.name
        init_db(self.db_path)
        # seed a business row for FK
        from sovereign_books.db import db_session

        with db_session(self.db_path) as conn:
            conn.execute("INSERT INTO users (id, email) VALUES ('usr_t', 't@test.local')")
            conn.execute(
                "INSERT INTO businesses (id, user_id, name) VALUES ('biz_t', 'usr_t', 'Test Co')"
            )
        self.ledger = PersistentLedger("biz_t", self.db_path)

    def tearDown(self):
        Path(self.db_path).unlink(missing_ok=True)

    def test_chart_seeded(self):
        accounts = self.ledger.list_accounts()
        codes = {a["code"] for a in accounts}
        self.assertIn("1100", codes)
        self.assertIn("4010", codes)

    def test_balanced_journal(self):
        entry = self.ledger.record_journal_entry(
            "Sale",
            debits={"1100": 100.0},
            credits={"4010": 100.0},
        )
        self.assertTrue(entry["entry_id"].startswith("JE-"))
        self.assertTrue(self.ledger.trial_balance_ok())
        self.assertEqual(self.ledger.get_account_balance("1100"), 100.0)
        self.assertEqual(self.ledger.get_account_balance("4010"), 100.0)

    def test_unbalanced_rejected(self):
        with self.assertRaises(ValueError):
            self.ledger.record_journal_entry(
                "Bad",
                debits={"1100": 50.0},
                credits={"4010": 40.0},
            )


class TestPlaidMock(unittest.TestCase):
    def test_mock_link_and_exchange(self):
        # Force mock regardless of env
        os.environ.pop("PLAID_CLIENT_ID", None)
        os.environ.pop("PLAID_SECRET", None)
        client = PlaidClient()
        self.assertEqual(client.mode, "mock")
        link = client.create_link_token("usr_1")
        self.assertIn("link_token", link)
        exchanged = client.exchange_public_token("public-sandbox-mock-chase")
        self.assertTrue(exchanged["access_token"].startswith("access-sandbox-mock-"))
        accounts = client.get_accounts(exchanged["access_token"])
        self.assertGreaterEqual(len(accounts), 1)
        txns = client.get_transactions(exchanged["access_token"])
        self.assertGreaterEqual(len(txns), 5)


class TestBankConnectFlow(unittest.TestCase):
    def setUp(self):
        os.environ.pop("PLAID_CLIENT_ID", None)
        os.environ.pop("PLAID_SECRET", None)
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp.close()
        self.db_path = self.tmp.name
        self.svc = BankService(db_path=self.db_path)

    def tearDown(self):
        Path(self.db_path).unlink(missing_ok=True)

    def test_connect_and_sync_inbox(self):
        ws = self.svc.ensure_demo_workspace()
        link = self.svc.create_link_token()
        self.assertEqual(link["mode"], "mock")

        connected = self.svc.exchange_and_connect(
            public_token="public-sandbox-mock-chase",
            institution_name="Chase",
        )
        self.assertEqual(connected["status"], "CONNECTED")
        self.assertGreaterEqual(connected["account_count"], 1)

        sync = self.svc.sync_transactions(
            business_id=ws["business_id"],
            plaid_item_id=connected["plaid_item_id"],
            post_to_ledger=True,
        )
        self.assertEqual(sync["status"], "SYNCED")
        self.assertGreater(sync["imported"], 0)
        self.assertTrue(sync["trial_balance_ok"])

        inbox = self.svc.list_inbox(ws["business_id"])
        self.assertGreater(inbox["count"], 0)

        # Second sync should dedupe
        sync2 = self.svc.sync_transactions(
            business_id=ws["business_id"],
            plaid_item_id=connected["plaid_item_id"],
            post_to_ledger=True,
        )
        self.assertEqual(sync2["imported"], 0)
        self.assertGreater(sync2["skipped_duplicates"], 0)

        home = self.svc.home_snapshot()
        self.assertTrue(home["bank_connected"])
        self.assertGreater(home["cash_balance"], 0)
        self.assertTrue(home["trial_balance_ok"])


if __name__ == "__main__":
    unittest.main()
