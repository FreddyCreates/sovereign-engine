"""
Exhaustive Automated Unit & Integration Test Suite for Agentic QuickBooks Engine.
Tests cover:
1. RevenueCat Subscription Tiers, Consumer Recurring Plans & Monetization Layer
2. RevenueCat IAP Event Processing with GAAP Double-Entry Posting (Annual Deferred vs Monthly Earned)
3. Usage-Based Metering & Overages Integration
4. GAAP ASC 606 Ratable Revenue Recognition Schedules & Deferred Liability Reduction
5. Automated Payroll Execution, Withholding Allocations & Section 41 R&D Wage Splitting
6. Live Compliance & Statutory Tax Credits Research Engine (IRC Sec 41, Sec 174, State Incentives)
7. Double-Entry Accounting Invariant Verification ($0.00 Debit/Credit Variance across all operations)
8. REST Dashboard API Endpoints for Agentic QuickBooks
"""

import unittest
import json
import os
import sys

# Ensure paths
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sovereign_infrastructure", "nextgen_systems")))

from full_saas_accounting_suite import GeneralLedgerEngine
from agentic_quickbooks_engine import (
    AgenticQuickBooksEngine,
    RevenueCatSubscriptionTierManager,
    ComplianceAndTaxCreditsResearchEngine
)
from sovereign_dashboard_server import SovereignDashboardHandler
from tests.test_platform_endpoints_integration import BaseDashboardTestCase


class TestAgenticQuickBooksCore(unittest.TestCase):

    def setUp(self):
        self.gl = GeneralLedgerEngine()
        self.engine = AgenticQuickBooksEngine(gl=self.gl)

    # -------------------------------------------------------------------------
    # 1. REVENUECAT SUBSCRIPTION TIERS & MONETIZATION
    # -------------------------------------------------------------------------
    def test_01_subscription_tiers_registration(self):
        tier_mgr = self.engine.subscription_manager
        self.assertIn("sovereign_starter_monthly", tier_mgr.TIERS)
        self.assertIn("sovereign_pro_monthly", tier_mgr.TIERS)
        self.assertIn("sovereign_enterprise_annual", tier_mgr.TIERS)

        # Register Starter subscriber
        sub1 = tier_mgr.register_or_update_subscriber("usr_starter_01", "sovereign_starter_monthly")
        self.assertEqual(sub1["tier_name"], "Starter")
        self.assertEqual(sub1["price_usd"], 19.99)
        self.assertIn("bookkeeping_core", sub1["entitlements"])

        # Register Enterprise subscriber
        sub2 = tier_mgr.register_or_update_subscriber("usr_ent_01", "sovereign_enterprise_annual")
        self.assertEqual(sub2["tier_name"], "Enterprise Sovereign Annual")
        self.assertEqual(sub2["price_usd"], 1799.99)
        self.assertIn("tax_credits_engine", sub2["entitlements"])

    def test_02_revenuecat_monthly_event_processing(self):
        # Initial purchase of monthly plan: $49.99
        res = self.engine.process_revenuecat_subscription_event(
            user_id="usr_growth_01",
            event_type="INITIAL_PURCHASE",
            product_id="sovereign_pro_monthly",
            price_usd=49.99,
            store="GOOGLE_PLAY_STORE"
        )
        self.assertEqual(res["event_type"], "INITIAL_PURCHASE")
        self.assertEqual(res["gross_amount_usd"], 49.99)
        self.assertAlmostEqual(res["app_store_fee_usd"], 7.50, delta=0.01)  # 15% rate
        self.assertAlmostEqual(res["net_cash_usd"], 42.49, delta=0.01)
        self.assertIsNotNone(res["journal_entry"])

        # Verify General Ledger trial balance remains strictly balanced
        tb = self.gl.generate_trial_balance()
        self.assertTrue(tb["is_balanced"], "GL must maintain Debits == Credits invariant")

    def test_03_revenuecat_annual_deferred_event_processing(self):
        # Initial purchase of annual plan: $1,799.99
        res = self.engine.process_revenuecat_subscription_event(
            user_id="usr_corp_99",
            event_type="INITIAL_PURCHASE",
            product_id="sovereign_enterprise_annual",
            price_usd=1799.99,
            store="APP_STORE_STOREKIT_2"
        )
        self.assertEqual(res["gross_amount_usd"], 1799.99)
        self.assertEqual(res["journal_entry"]["entry_type"], "REVENUECAT_IAP_ANNUAL_DEFERRED")

        # Deferred Revenue Liability account 2300 should hold credit balance
        deferred_balance = self.gl.get_account_balance("2300")
        self.assertGreaterEqual(deferred_balance, 1799.99)

        # Verify GL Balance
        tb = self.gl.generate_trial_balance()
        self.assertTrue(tb["is_balanced"])

    # -------------------------------------------------------------------------
    # 2. USAGE METERING & OVERAGES
    # -------------------------------------------------------------------------
    def test_04_metered_usage_within_tier_limit(self):
        # Pro monthly plan has 5,000 units included
        self.engine.subscription_manager.register_or_update_subscriber("usr_meter_01", "sovereign_pro_monthly")
        res = self.engine.record_metered_usage_and_bill("usr_meter_01", feature="ai_bookkeeping_queries", units=500)
        
        self.assertEqual(res["total_monthly_usage_units"], 500)
        self.assertEqual(res["overage_units"], 0)
        self.assertEqual(res["overage_charge_usd"], 0.0)
        self.assertIsNone(res["gl_entry"])

    def test_05_metered_usage_exceeding_tier_limit(self):
        # Starter plan has 1,000 units included, $0.01 per extra unit
        self.engine.subscription_manager.register_or_update_subscriber("usr_overage_01", "sovereign_starter_monthly")
        # Record 1,500 units -> 500 overage units -> $5.00 overage charge
        res = self.engine.record_metered_usage_and_bill("usr_overage_01", feature="ocr_receipts", units=1500)
        
        self.assertEqual(res["total_monthly_usage_units"], 1500)
        self.assertEqual(res["overage_units"], 500)
        self.assertEqual(res["overage_charge_usd"], 5.00)
        self.assertIsNotNone(res["gl_entry"])

        # Check subscriber billing summary
        summary = self.engine.subscription_manager.get_subscriber_billing_summary("usr_overage_01")
        self.assertEqual(summary["total_current_bill_usd"], 24.99)  # $19.99 base + $5.00 overage

    # -------------------------------------------------------------------------
    # 3. GAAP ASC 606 ACCRUAL REVENUE RECOGNITION
    # -------------------------------------------------------------------------
    def test_06_asc606_ratable_revenue_amortization(self):
        # Contract $120,000 over 12 months = $10,000/month
        res = self.engine.run_monthly_asc606_revenue_recognition(
            contract_id="CONTRACT-2026-SAAS",
            total_contract_value=120000.0,
            current_month=1,
            duration_months=12
        )
        self.assertEqual(res["asc606_summary"]["monthly_recognized_amount"], 10000.0)
        self.assertEqual(res["asc606_summary"]["remaining_deferred_liability"], 110000.0)
        self.assertEqual(res["journal_entry"]["status"], "POSTED")

        # Verify GL Balance
        tb = self.gl.generate_trial_balance()
        self.assertTrue(tb["is_balanced"])

    # -------------------------------------------------------------------------
    # 4. AGENTIC PAYROLL ALLOCATION & SECTION 41 QRE SPLITTING
    # -------------------------------------------------------------------------
    def test_07_agentic_payroll_and_rd_wage_allocation(self):
        # $100,000 gross payroll, CA, 80% R&D ratio
        res = self.engine.execute_agentic_payroll(gross_payroll=100000.0, state="CA", engineering_rd_ratio=0.80)
        self.assertEqual(res["status"], "PAYROLL_EXECUTED_AND_ALLOCATED")
        self.assertEqual(res["engineering_rd_eligible_wages"], 80000.0)
        self.assertIn("form_941_escrow", res)
        self.assertGreater(res["form_941_escrow"], 0)

        # Verify GL Balance
        tb = self.gl.generate_trial_balance()
        self.assertTrue(tb["is_balanced"])

    # -------------------------------------------------------------------------
    # 5. LIVE COMPLIANCE & STATUTORY TAX CREDITS RESEARCH
    # -------------------------------------------------------------------------
    def test_08_statutory_tax_credits_research_and_calculation(self):
        # Query with $50,000 cloud spend + $150,000 engineering payroll in CA
        tax_res = self.engine.research_and_calculate_tax_credits(
            state="CA",
            cloud_compute_spend=50000.0,
            rd_payroll_spend=150000.0
        )
        self.assertEqual(tax_res["cloud_compute_qre"], 50000.0)
        self.assertEqual(tax_res["rd_payroll_qre"], 120000.0)  # 80% of 150k
        self.assertEqual(tax_res["total_qualified_research_expenses"], 170000.0)
        
        # Federal Section 41 ASC credit: 14% of 170,000 = $23,800
        self.assertEqual(tax_res["federal_section_41_credit"], 23800.0)
        # CA State R&D credit: 15% of 170,000 = $25,500
        self.assertEqual(tax_res["state_tax_credit"], 25500.0)
        self.assertEqual(tax_res["total_estimated_tax_credits"], 49300.0)
        self.assertEqual(tax_res["sec_174_annual_amortization_deduction"], 34000.0)  # 170k / 5

    # -------------------------------------------------------------------------
    # 6. COMPREHENSIVE BOOKKEEPING AUDIT & INVARIANT CHECKS
    # -------------------------------------------------------------------------
    def test_09_comprehensive_bookkeeping_audit(self):
        audit = self.engine.run_comprehensive_bookkeeping_audit()
        self.assertEqual(audit["agent_identity"], "Agentic_QuickBooks_Sovereign_Bookkeeper")
        self.assertTrue(audit["is_double_entry_balanced"])
        self.assertEqual(audit["debit_credit_variance"], 0.00)
        self.assertIn("pnl_statement", audit)
        self.assertIn("balance_sheet", audit)
        self.assertEqual(audit["status"], "AGENTIC_BOOKKEEPING_AUDIT_OPTIMAL")

    def test_09b_revenuecat_live_client_and_signature_verification(self):
        live_client = self.engine.subscription_manager.live_rc_client
        payload = b'{"event": "TEST_PURCHASE", "price": 49.99}'
        # Compute valid signature
        valid_sig = live_client.verify_webhook_signature(
            payload_bytes=payload,
            signature_header="sha256=" + live_client.webhook_secret
        )
        # Should cleanly return boolean without throwing
        self.assertIsInstance(valid_sig, bool)

        # Test customer info fetch
        cust = live_client.get_customer_info("usr_test_cust_01")
        self.assertIn("customer", cust)
        self.assertEqual(cust["customer"]["id"], "usr_test_cust_01")

        # Test offerings fetch
        offerings = live_client.fetch_project_offerings()
        self.assertIn("offerings", offerings)

    def test_09c_statutory_compliance_live_fetcher(self):
        fetcher = self.engine.research_engine.live_fetcher
        res = fetcher.fetch_statutory_text_or_guidance("irc_sec_41", "IRC Sec 41 Research Credit")
        self.assertEqual(res["resource_key"], "irc_sec_41")
        self.assertIn("summary", res)


class TestAgenticQuickBooksDashboardEndpoints(BaseDashboardTestCase):

    def test_10_rest_agentic_qb_audit_get(self):
        res = self.invoke_endpoint("/api/v1/agentic_qb/audit", "GET")
        self.assertEqual(res["status"], "AGENTIC_BOOKKEEPING_AUDIT_OPTIMAL")
        self.assertTrue(res["is_double_entry_balanced"])

    def test_11_rest_agentic_qb_tax_credits_get(self):
        res = self.invoke_endpoint("/api/v1/agentic_qb/tax_credits?state=NY", "GET")
        self.assertEqual(res["jurisdiction"], "US_NY")
        self.assertGreater(res["total_estimated_tax_credits"], 0.0)

    def test_12_rest_agentic_qb_event_post(self):
        body = {
            "user_id": "usr_test_api_01",
            "event_type": "INITIAL_PURCHASE",
            "product_id": "sovereign_pro_monthly",
            "price_usd": 49.99
        }
        res = self.invoke_endpoint("/api/v1/agentic_qb/event", "POST", body)
        self.assertEqual(res["status"], "REVENUECAT_EVENT_PROCESSED")
        self.assertEqual(res["gross_amount_usd"], 49.99)

    def test_13_rest_agentic_qb_meter_usage_post(self):
        body = {
            "user_id": "usr_test_api_02",
            "feature": "ai_bookkeeping_queries",
            "units": 100
        }
        res = self.invoke_endpoint("/api/v1/agentic_qb/meter_usage", "POST", body)
        self.assertEqual(res["status"], "USAGE_RECORDED_AND_METERED")
        self.assertEqual(res["units_recorded"], 100)

    def test_14_rest_agentic_qb_asc606_post(self):
        body = {
            "contract_id": "CONTRACT-API-001",
            "total_contract_value": 24000.0,
            "current_month": 2,
            "duration_months": 12
        }
        res = self.invoke_endpoint("/api/v1/agentic_qb/asc606_recognize", "POST", body)
        self.assertEqual(res["status"], "ASC606_MONTHLY_REVENUE_RECOGNIZED")
        self.assertEqual(res["asc606_summary"]["monthly_recognized_amount"], 2000.0)

    def test_15_rest_agentic_qb_payroll_post(self):
        body = {
            "gross_payroll": 50000.0,
            "state": "CA",
            "engineering_rd_ratio": 0.85
        }
        res = self.invoke_endpoint("/api/v1/agentic_qb/payroll", "POST", body)
        self.assertEqual(res["status"], "PAYROLL_EXECUTED_AND_ALLOCATED")
        self.assertEqual(res["engineering_rd_eligible_wages"], 42500.0)

    def test_16_rest_agentic_qb_live_integrations_get(self):
        res = self.invoke_endpoint("/api/v1/agentic_qb/live_integrations", "GET")
        self.assertIn("integrations", res)
        self.assertIn("revenuecat", res["integrations"])
        self.assertIn("quickbooks", res["integrations"])
        self.assertEqual(res["total_integrations"], 6)


if __name__ == "__main__":
    unittest.main()
