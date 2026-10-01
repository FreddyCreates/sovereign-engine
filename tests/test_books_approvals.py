import os
import tempfile
import unittest

from sovereign_books.approvals import ApprovalsLog
from sovereign_books import http_api


class TestApprovalsLog(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="approvals_")
        self.db = os.path.join(self.tmp, "books.db")
        os.environ["SOVEREIGN_BOOKS_DB"] = self.db
        self.log = ApprovalsLog(self.db)

    def test_record_and_list(self):
        res = self.log.record("categorize", "approved", "cat_txn_1", subject="Notion Labs", amount=4200.0)
        self.assertEqual(res["status"], "OK")
        self.assertTrue(res["id"].startswith("apr_"))
        listed = self.log.list(limit=10)
        self.assertEqual(listed["count"], 1)
        row = listed["approvals"][0]
        self.assertEqual(row["kind"], "categorize")
        self.assertEqual(row["decision"], "approved")
        self.assertEqual(row["amount"], 4200.0)
        self.assertEqual(row["source"], "mobile")

    def test_rejects_unknown_kind_and_decision(self):
        self.assertEqual(self.log.record("bogus", "approved", "x")["status"], "ERROR")
        self.assertEqual(self.log.record("tax_credit", "maybe", "x")["status"], "ERROR")
        self.assertEqual(self.log.record("tax_credit", "approved", "")["status"], "ERROR")

    def test_summary_groups_by_kind_and_decision(self):
        self.log.record("tax_credit", "approved", "credit_US_CA", amount=23026.0)
        self.log.record("invoice_chase", "sent", "inv_1")
        self.log.record("invoice_chase", "skipped", "inv_2")
        summary = self.log.summary()
        self.assertEqual(summary["by_kind"]["tax_credit"]["approved"], 1)
        self.assertEqual(summary["by_kind"]["invoice_chase"]["sent"], 1)
        self.assertEqual(summary["by_kind"]["invoice_chase"]["skipped"], 1)

    def test_http_helpers_round_trip(self):
        http_api._approvals = None
        posted = http_api.handle_books_ext_post(
            "/api/v1/books/approvals",
            {"kind": "categorize", "decision": "approved", "card_id": "cat_1", "payload": {"category": "Software"}},
        )
        self.assertEqual(posted["status"], "OK")
        got = http_api.handle_books_ext_get("/api/v1/books/approvals", {"limit": "5"})
        self.assertEqual(got["count"], 1)
        self.assertEqual(got["approvals"][0]["card_id"], "cat_1")


if __name__ == "__main__":
    unittest.main()
