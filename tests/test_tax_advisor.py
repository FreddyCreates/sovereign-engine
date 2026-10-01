import os
import tempfile
import unittest

from sovereign_books.bank_service import BankService
from sovereign_books.tax_advisor import TaxAdvisor
from sovereign_books.tax_classifier import TaxClassifier
from sovereign_books import http_api


class TestTaxAdvisor(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="taxadv_")
        self.db = os.path.join(self.tmp, "books.db")
        os.environ["SOVEREIGN_BOOKS_DB"] = self.db
        self.bank = BankService(self.db)
        connected = self.bank.exchange_and_connect(public_token="public-sandbox-mock-chase")
        self.bid = connected["business_id"]
        self.bank.sync_transactions(business_id=self.bid, plaid_item_id=connected.get("plaid_item_id"))
        self.clf = TaxClassifier(self.db)
        self.clf.classify_all(self.bid)
        self.advisor = TaxAdvisor(self.db, classifier=self.clf)

    def test_opportunities_are_ranked_with_a_next_action(self):
        res = self.advisor.opportunities(self.bid, state="CA", tax_year=2026)
        self.assertEqual(res["status"], "OK")
        self.assertGreater(res["count"], 3)
        ids = {o["id"] for o in res["opportunities"]}
        self.assertIn("company_event_100", ids)
        self.assertIn("section_179", ids)
        self.assertIn("retirement_startup_credit", ids)
        statuses = [o["status"] for o in res["opportunities"]]
        order = {"close": 0, "qualified": 1, "not_yet": 2}
        self.assertEqual(statuses, sorted(statuses, key=lambda s: order[s]))
        self.assertIsNotNone(res["next_action"])
        for o in res["opportunities"]:
            self.assertTrue(o["title"] and o["action"] and o["reference"])
            self.assertGreaterEqual(o["estimated_value"], 0)

    def test_research_credit_uses_engine_when_available(self):
        res = self.advisor.opportunities(self.bid, state="NY", tax_year=2026)
        rd = [o for o in res["opportunities"] if o["id"] == "research_credit_41"]
        if rd:
            self.assertIn("41", rd[0]["reference"])
            self.assertEqual(rd[0]["detail"]["jurisdiction"], "US_NY")

    def test_http_round_trip(self):
        http_api._tax = None
        http_api._advisor = None
        http_api._books_ext = None
        rb = http_api.handle_tax_get("/api/v1/books/tax/classes", {})
        self.assertGreater(len(rb["classes"]), 20)
        summary = http_api.handle_tax_get("/api/v1/books/tax/summary", {"business_id": self.bid, "year": "2026"})
        self.assertEqual(summary["status"], "OK")
        qs = http_api.handle_tax_get("/api/v1/books/tax/questions", {"business_id": self.bid})
        self.assertEqual(qs["status"], "OK")
        if qs["count"]:
            q = qs["questions"][0]
            ans = http_api.handle_tax_post("/api/v1/books/tax/classify", {"business_id": self.bid, "txn_id": q["transaction_id"], "attendees": "all_employees"})
            self.assertEqual(ans["tax_class"], "MEAL_COMPANY_EVENT_100")
        opps = http_api.handle_tax_get("/api/v1/books/tax/opportunities", {"business_id": self.bid, "state": "TX"})
        self.assertEqual(opps["state"], "TX")
        self.assertEqual(http_api.handle_tax_post("/api/v1/books/tax/classify", {"business_id": self.bid})["status"], "ERROR")


if __name__ == "__main__":
    unittest.main()
