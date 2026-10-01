import os
import tempfile
import unittest

from sovereign_books.bank_service import BankService
from sovereign_books.tax_classifier import MEAL_QUESTION, TAX_CLASSES, TaxClassifier, classify, rulebook


class TestClassifyRules(unittest.TestCase):
    def test_restaurant_without_context_asks_who_attended(self):
        c = classify("Chipotle", "Chipotle", 42.0, "Travel & Meals", "2026-09-01")
        self.assertEqual(c.tax_class, "MEAL_BUSINESS_50")
        self.assertEqual(c.question, MEAL_QUESTION)
        self.assertTrue(c.needs_review)
        self.assertEqual(c.deductible_amount, 21.0)
        ids = {a["id"] for a in c.answers}
        self.assertIn("all_employees", ids)

    def test_company_event_is_fully_deductible(self):
        c = classify("Team dinner", "Bistro 42", 1200.0, "Travel & Meals", "2026-12-15", {"attendees": "all_employees"})
        self.assertEqual(c.tax_class, "MEAL_COMPANY_EVENT_100")
        self.assertEqual(c.deductible_pct, 1.0)
        self.assertEqual(c.deductible_amount, 1200.0)
        self.assertFalse(c.needs_review)
        self.assertIn("274(e)(4)", c.irc_reference)

    def test_ceo_dinner_with_one_employee_is_half(self):
        c = classify("Dinner", "Steakhouse", 200.0, None, "2026-06-01", {"attendees": "employee"})
        self.assertEqual(c.tax_class, "MEAL_BUSINESS_50")
        self.assertEqual(c.deductible_amount, 100.0)

    def test_office_meals_zero_from_2026_but_half_before(self):
        after = classify("Office lunch", "Panera", 300.0, None, "2026-03-01", {"attendees": "office_provided"})
        before = classify("Office lunch", "Panera", 300.0, None, "2025-03-01", {"attendees": "office_provided"})
        self.assertEqual(after.tax_class, "MEAL_EMPLOYER_CONVENIENCE_0")
        self.assertEqual(after.deductible_amount, 0.0)
        self.assertEqual(before.tax_class, "MEAL_BUSINESS_50")
        self.assertEqual(before.deductible_amount, 150.0)

    def test_solo_meal_in_town_is_personal(self):
        c = classify("Lunch", "Sweetgreen", 18.0, None, "2026-05-05", {"attendees": "solo"})
        self.assertEqual(c.deductible_pct, 0.0)

    def test_entertainment_is_zero(self):
        c = classify("Topgolf", "Topgolf", 600.0, None, "2026-09-10")
        self.assertEqual(c.tax_class, "ENTERTAINMENT_0")
        self.assertEqual(c.deductible_amount, 0.0)

    def test_airfare_is_travel(self):
        c = classify("United", "United Airlines", 480.0, "Travel & Meals", "2026-09-10")
        self.assertEqual(c.tax_class, "TRAVEL_100")
        self.assertIsNone(c.question)

    def test_equipment_threshold(self):
        small = classify("Monitor", "Apple Store", 1800.0, None, "2026-02-01")
        big = classify("Laptop", "Apple Store", 3200.0, None, "2026-02-01")
        self.assertEqual(small.tax_class, "EQUIPMENT_DE_MINIMIS")
        self.assertEqual(big.tax_class, "EQUIPMENT_179")

    def test_gift_cap_per_recipient(self):
        c = classify("Gift baskets", "Harry & David", 150.0, None, "2026-12-10", {"recipients": 3})
        self.assertEqual(c.deductible_amount, 75.0)

    def test_income_and_unknown(self):
        self.assertEqual(classify("Stripe", "Stripe", -890.0, "Sales Income", "2026-09-28").tax_class, "INCOME")
        u = classify("Mystery", "XYZ Corp", 77.0, "Uncategorized Expense", "2026-09-28")
        self.assertEqual(u.tax_class, "UNCLASSIFIED")
        self.assertTrue(u.needs_review)

    def test_owner_override_wins(self):
        c = classify("Something", "Vendor", 50.0, None, "2026-01-01", {"tax_class": "EDUCATION_100"})
        self.assertEqual(c.tax_class, "EDUCATION_100")
        self.assertEqual(c.confidence, 100)

    def test_rulebook_lists_every_class(self):
        rb = rulebook()
        self.assertEqual(len(rb["classes"]), len(TAX_CLASSES))
        self.assertTrue(any(a["deductible_pct"] == 1.0 for a in rb["meal_answers"]))


class TestClassifierStore(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="taxcls_")
        self.db = os.path.join(self.tmp, "books.db")
        os.environ["SOVEREIGN_BOOKS_DB"] = self.db
        self.bank = BankService(self.db)
        connected = self.bank.exchange_and_connect(public_token="public-sandbox-mock-chase")
        self.bid = connected["business_id"]
        self.bank.sync_transactions(business_id=self.bid, plaid_item_id=connected.get("plaid_item_id"))
        self.clf = TaxClassifier(self.db)

    def test_classify_all_then_answer_question(self):
        res = self.clf.classify_all(self.bid)
        self.assertEqual(res["status"], "OK")
        self.assertGreater(res["classified"], 0)
        listed = self.clf.list(self.bid)
        self.assertEqual(listed["count"], res["classified"])
        qs = self.clf.questions(self.bid)
        if qs["count"]:
            q = qs["questions"][0]
            answered = self.clf.classify_transaction(self.bid, q["transaction_id"], {"attendees": "all_employees"})
            self.assertEqual(answered["tax_class"], "MEAL_COMPANY_EVENT_100")
            # Re-running keeps the owner's answer.
            self.clf.classify_all(self.bid)
            again = [c for c in self.clf.list(self.bid)["classifications"] if c["transaction_id"] == q["transaction_id"]][0]
            self.assertEqual(again["tax_class"], "MEAL_COMPANY_EVENT_100")

    def test_summary_totals_add_up(self):
        self.clf.classify_all(self.bid)
        s = self.clf.summary(self.bid, 2026)
        self.assertEqual(s["status"], "OK")
        self.assertAlmostEqual(s["total_deductible"] + s["total_nondeductible"], s["total_spent"], places=2)
        self.assertTrue(all("irc_reference" in c for c in s["by_class"]))


if __name__ == "__main__":
    unittest.main()
