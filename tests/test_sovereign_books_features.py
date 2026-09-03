"""Tests for Sovereign Books chat, grants, confirm, cash series, RevenueCat local."""

import os
import tempfile
import unittest
from pathlib import Path

from sovereign_books.bank_service import BankService
from sovereign_books.chat_engine import BooksChatEngine
from sovereign_books.db import init_db
from sovereign_books.grants import get_grant, list_grants
from sovereign_books.revenuecat import RevenueCatService


class TestGrantsCatalog(unittest.TestCase):
    def test_list_and_get(self):
        data = list_grants()
        self.assertGreaterEqual(data["count"], 3)
        self.assertEqual(data["status"], "OK")
        one = get_grant(data["grants"][0]["id"])
        self.assertEqual(one["status"], "OK")
        self.assertIn("title", one["grant"])


class TestChatEngine(unittest.TestCase):
    def setUp(self):
        os.environ.pop("PLAID_CLIENT_ID", None)
        os.environ.pop("PLAID_SECRET", None)
        os.environ.pop("GEMINI_API_KEY", None)
        os.environ.pop("OPENAI_API_KEY", None)
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp.close()
        self.db_path = self.tmp.name
        self.bank = BankService(self.db_path)
        self.chat = BooksChatEngine(self.bank)

    def tearDown(self):
        Path(self.db_path).unlink(missing_ok=True)

    def test_script_cash(self):
        out = self.chat.reply("show cash chart")
        self.assertEqual(out["status"], "OK")
        self.assertEqual(out["engine"], "script")
        self.assertTrue(any(a["kind"] == "chart" for a in out["artifacts"]))

    def test_script_grants(self):
        out = self.chat.reply("find grants for my app")
        self.assertTrue(any(a["kind"] == "grant" for a in out["artifacts"]))


class TestConfirmAndCash(unittest.TestCase):
    def setUp(self):
        os.environ.pop("PLAID_CLIENT_ID", None)
        os.environ.pop("PLAID_SECRET", None)
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp.close()
        self.db_path = self.tmp.name
        self.bank = BankService(self.db_path)

    def tearDown(self):
        Path(self.db_path).unlink(missing_ok=True)

    def test_connect_sync_confirm_cash(self):
        connected = self.bank.exchange_and_connect("public-sandbox-mock-chase")
        self.assertEqual(connected["status"], "CONNECTED")
        sync = self.bank.sync_transactions(
            business_id=connected["business_id"],
            plaid_item_id=connected["plaid_item_id"],
            post_to_ledger=False,
        )
        self.assertGreater(sync["imported"], 0)
        inbox = self.bank.list_inbox()
        self.assertGreater(inbox["count"], 0)
        txn = inbox["transactions"][0]
        confirmed = self.bank.confirm_transaction(
            txn["id"], category=txn.get("category_suggested") or "Office & Software"
        )
        self.assertEqual(confirmed["status"], "CONFIRMED")
        series = self.bank.cash_series()
        self.assertEqual(series["status"], "OK")
        self.assertGreaterEqual(len(series["points"]), 1)
        home = self.bank.home_snapshot()
        self.assertIn("cash_series", home)


class TestRevenueCatLocal(unittest.TestCase):
    def setUp(self):
        os.environ.pop("REVENUECAT_SECRET_API_KEY", None)
        os.environ.pop("REVENUECAT_API_KEY", None)
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp.close()
        self.db_path = self.tmp.name
        init_db(self.db_path)
        self.rc = RevenueCatService(self.db_path)

    def tearDown(self):
        Path(self.db_path).unlink(missing_ok=True)

    def test_activate_and_gate(self):
        before = self.rc.get_entitlements("u_test")
        self.assertFalse(before["pro_active"])
        act = self.rc.activate_local_pro("u_test")
        self.assertTrue(act["pro_active"])
        after = self.rc.get_entitlements("u_test")
        self.assertTrue(after["pro_active"])
        self.assertIn("unlimited_bank_accounts", after["features"])
        hook = self.rc.handle_webhook(
            {"type": "EXPIRATION", "event": {"app_user_id": "u_test"}}
        )
        self.assertFalse(hook["pro_active"])


class TestProBankGate(unittest.TestCase):
    def setUp(self):
        os.environ.pop("PLAID_CLIENT_ID", None)
        os.environ.pop("PLAID_SECRET", None)
        os.environ.pop("REVENUECAT_SECRET_API_KEY", None)
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp.close()
        self.db_path = self.tmp.name
        self.bank = BankService(self.db_path)

    def tearDown(self):
        Path(self.db_path).unlink(missing_ok=True)

    def test_second_bank_requires_pro(self):
        first = self.bank.exchange_and_connect("public-sandbox-mock-chase")
        self.assertEqual(first["status"], "CONNECTED")
        second = self.bank.exchange_and_connect("public-sandbox-mock-chase")
        self.assertEqual(second["status"], "ERROR")
        self.assertTrue(second.get("pro_required"))
        RevenueCatService(self.db_path).activate_local_pro()
        third = self.bank.exchange_and_connect("public-sandbox-mock-chase")
        self.assertEqual(third["status"], "CONNECTED")


if __name__ == "__main__":
    unittest.main()
