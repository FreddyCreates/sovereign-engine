"""
Exhaustive Automated Unit Test Suite for Sovereign Full SaaS Accounting & Fintech Suite:
General Ledger, Balance Sheet, Cash Flow Statement, Payroll & Tax Withholding,
Accounts Payable / Vendor Bills, and Bank Feed Reconciliation.
"""

import sys
import os
import unittest

# Ensure root directory and nextgen_systems are on sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, root_dir)
sys.path.insert(0, os.path.join(root_dir, "sovereign_infrastructure", "nextgen_systems"))

from full_saas_accounting_suite import (
    GeneralLedgerEngine,
    BalanceSheetEngine,
    CashFlowEngine,
    PayrollTaxEngine,
    AccountsPayableEngine,
    BankReconciliationEngine
)


class TestGeneralLedgerEngine(unittest.TestCase):
    """Test Suite for General Ledger Engine & Trial Balance / P&L"""

    def setUp(self):
        self.gl = GeneralLedgerEngine()

    def test_01_account_balance_rules(self):
        # Asset balance = debits - credits
        self.assertEqual(self.gl.get_account_balance("1010"), 1420500.0)
        # Liability balance = credits - debits
        self.assertEqual(self.gl.get_account_balance("2010"), 48200.0)
        # Revenue balance = credits - debits
        self.assertEqual(self.gl.get_account_balance("4010"), 446760.0)

    def test_02_add_account(self):
        acc = self.gl.add_account("1400", "Inventory Assets", "ASSET", 50000.0)
        self.assertEqual(acc["name"], "Inventory Assets")
        self.assertEqual(self.gl.get_account_balance("1400"), 50000.0)

    def test_03_record_journal_entry_success(self):
        debits = {"1010": 5000.0}
        credits = {"4010": 5000.0}
        entry = self.gl.record_journal_entry("B2B Enterprise Sale", debits, credits)
        self.assertEqual(entry["amount"], 5000.0)
        self.assertEqual(entry["status"], "POSTED")
        self.assertEqual(self.gl.get_account_balance("1010"), 1425500.0)
        self.assertEqual(self.gl.get_account_balance("4010"), 451760.0)

    def test_04_record_journal_entry_unbalanced_raises_error(self):
        debits = {"1010": 5000.0}
        credits = {"4010": 4900.0}  # Unbalanced
        with self.assertRaises(ValueError):
            self.gl.record_journal_entry("Unbalanced Entry", debits, credits)

    def test_05_trial_balance(self):
        tb = self.gl.generate_trial_balance()
        self.assertTrue(tb["is_balanced"])
        self.assertEqual(tb["total_debits"], tb["total_credits"])

    def test_06_pnl_statement_generation(self):
        pnl = self.gl.generate_pnl_statement()
        self.assertEqual(pnl["gross_revenue"], 446760.0)
        self.assertEqual(pnl["cogs_fees"], -67014.0)
        self.assertEqual(pnl["gross_profit"], 379746.0)
        self.assertLess(pnl["operating_expenses"], 0)
        self.assertGreater(pnl["net_income"], 0)
        self.assertGreater(pnl["gross_margin_pct"], 80.0)


class TestBalanceSheetEngine(unittest.TestCase):
    """Test Suite for Balance Sheet Engine & Financial Ratios"""

    def setUp(self):
        self.gl = GeneralLedgerEngine()
        self.bs = BalanceSheetEngine(self.gl)

    def test_01_balance_sheet_is_balanced(self):
        bs_report = self.bs.generate_balance_sheet()
        self.assertTrue(bs_report["is_balanced"])
        self.assertEqual(
            bs_report["total_assets"],
            round(bs_report["total_liabilities"] + bs_report["total_equity"], 2)
        )

    def test_02_balance_sheet_ratios(self):
        bs_report = self.bs.generate_balance_sheet()
        ratios = bs_report["financial_ratios"]
        self.assertGreater(ratios["current_ratio"], 1.0)
        self.assertGreater(ratios["quick_ratio"], 1.0)
        self.assertGreater(ratios["working_capital"], 0.0)


class TestCashFlowEngine(unittest.TestCase):
    """Test Suite for Statement of Cash Flows Engine"""

    def setUp(self):
        self.gl = GeneralLedgerEngine()
        self.cf = CashFlowEngine(self.gl)

    def test_01_cash_flow_statement(self):
        cf_report = self.cf.generate_cash_flow_statement(beginning_cash=1205754.0)
        self.assertGreater(cf_report["operating_activities"], 0)
        self.assertGreater(cf_report["net_cash_flow"], 0)
        self.assertEqual(
            cf_report["ending_cash"],
            round(cf_report["beginning_cash"] + cf_report["net_cash_flow"], 2)
        )


class TestPayrollTaxEngine(unittest.TestCase):
    """Test Suite for Payroll & Tax Withholding Engine"""

    def setUp(self):
        self.gl = GeneralLedgerEngine()
        self.payroll = PayrollTaxEngine(self.gl)

    def test_01_payroll_tax_calculation(self):
        pay = self.payroll.calculate_payroll_run(gross_payroll=10000.0, state="CA")
        self.assertEqual(pay["gross_payroll"], 10000.0)
        self.assertEqual(pay["federal_tax_withheld"], 2200.0)
        self.assertEqual(pay["social_security_tax"], 620.0)
        self.assertEqual(pay["medicare_tax"], 145.0)
        self.assertEqual(pay["state_tax_withheld"], 600.0)
        self.assertEqual(pay["net_disbursement"], 6435.0)

    def test_02_post_payroll_to_gl(self):
        pay = self.payroll.calculate_payroll_run(gross_payroll=10000.0, state="CA")
        # GL balance should stay balanced after payroll posting
        tb = self.gl.generate_trial_balance()
        self.assertTrue(tb["is_balanced"])

    def test_03_form_941_summary(self):
        self.payroll.calculate_payroll_run(gross_payroll=50000.0, state="CA")
        summary = self.payroll.generate_form_941_summary()
        self.assertEqual(summary["quarter"], "Q3 2026")
        self.assertEqual(summary["total_wages_tips_compensation"], 50000.0)
        self.assertGreater(summary["total_tax_liability"], 0)


class TestAccountsPayableEngine(unittest.TestCase):
    """Test Suite for Accounts Payable & Vendor Bills Engine"""

    def setUp(self):
        self.gl = GeneralLedgerEngine()
        self.ap = AccountsPayableEngine(self.gl)

    def test_01_ap_aging_schedule(self):
        aging = self.ap.get_ap_aging_schedule()
        self.assertGreater(aging["total_ap"], 0)
        self.assertGreaterEqual(aging["current_0_30_days"], 0)

    def test_02_create_vendor_bill(self):
        bill = self.ap.create_vendor_bill(vendor="Datadog", amount=5000.0, due_days=30)
        self.assertEqual(bill["vendor"], "Datadog")
        self.assertEqual(bill["status"], "UNPAID")

    def test_03_pay_vendor_bill_with_discount(self):
        # Bill 902 has terms 2_10_NET_30 ($18,000)
        res = self.ap.pay_vendor_bill("BILL-902", days_elapsed=5)
        self.assertEqual(res["status"], "PAID")
        self.assertEqual(res["discount_earned"], 360.0)
        self.assertEqual(res["net_payment"], 17640.0)


class TestBankReconciliationEngine(unittest.TestCase):
    """Test Suite for Bank Feed 3-Way Reconciliation Engine"""

    def setUp(self):
        self.gl = GeneralLedgerEngine()
        self.bank = BankReconciliationEngine(self.gl)

    def test_01_bank_reconciliation_matching(self):
        feed = [
            {"tx_id": "TX_01", "description": "AWS CLOUD INFRASTRUCTURE", "amount": -24500.0},
            {"tx_id": "TX_02", "description": "REVENUECAT SUBSCRIPTION DEPOSIT", "amount": 446760.0},
            {"tx_id": "TX_03", "description": "GUSTO PAYROLL DISBURSEMENT", "amount": -148500.0}
        ]
        res = self.bank.reconcile_feed(feed)
        self.assertEqual(res["matched_transactions"], 3)
        self.assertEqual(res["reconciliation_confidence_pct"], 100.0)

    def test_02_reconciliation_report(self):
        # Bank ending balance 1,408,000 + 25000 in transit - 12500 outstanding = 1,420,500 == GL cash balance
        report = self.bank.generate_reconciliation_report(
            statement_date="2026-08-31",
            bank_ending_balance=1408000.0
        )
        self.assertTrue(report["is_reconciled"])
        self.assertEqual(report["variance"], 0.0)


if __name__ == "__main__":
    unittest.main()
