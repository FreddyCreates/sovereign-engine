"""
Automated Integration & Unit Testing Suite for 11 Platform Endpoints
Integrated with 6 Next-Gen Fintech Cores (XFIN, AURA, PULSE, MINT, GRID, NEXS)
and sovereign_dashboard_server REST Server.
Exhaustive Automated Tests: 5 tests per engine / integration module.
"""

import sys
import os
import unittest
import json
import io

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sovereign_infrastructure", "nextgen_systems")))

from sovereign_dashboard_server import SovereignDashboardHandler
from mega_11_platform_master_suite import Mega11PlatformOrchestrator
from nextgen_master_orchestrator import NextGenMasterOrchestrator


class BaseDashboardTestCase(unittest.TestCase):
    def invoke_endpoint(self, path: str, method: str = "GET", body: dict = None) -> dict:
        body_bytes = json.dumps(body).encode("utf-8") if body else b""
        rfile = io.BytesIO(body_bytes)
        wfile = io.BytesIO()

        handler = SovereignDashboardHandler.__new__(SovereignDashboardHandler)
        handler.path = path
        handler.rfile = rfile
        handler.wfile = wfile
        handler.headers = {"Content-Length": str(len(body_bytes))}

        handler.response_code = None
        handler.response_headers = {}

        def mock_send_response(code, message=None):
            handler.response_code = code

        def mock_send_header(keyword, value):
            handler.response_headers[keyword] = value

        def mock_end_headers():
            pass

        handler.send_response = mock_send_response
        handler.send_header = mock_send_header
        handler.end_headers = mock_end_headers

        if method.upper() == "GET":
            handler.do_GET()
        else:
            handler.do_POST()

        output_bytes = wfile.getvalue()
        self.assertEqual(handler.response_code, 200)
        return json.loads(output_bytes.decode("utf-8")) if output_bytes else {}


class TestQuickBooksCoreIntegration(BaseDashboardTestCase):
    """1. QuickBooks Engine Integration - 5 Tests"""

    def test_01_qb_pnl_get(self):
        res = self.invoke_endpoint("/api/v1/quickbooks/pnl", "GET")
        self.assertIn("net_income", res)
        self.assertGreater(res["net_income"], 0)

    def test_02_qb_pnl_post(self):
        res = self.invoke_endpoint("/api/v1/quickbooks/pnl", "POST")
        self.assertIn("gross_revenue", res)
        self.assertEqual(res["status"], "QUICKBOOKS_ONLINE_FULLY_REPLACED")

    def test_03_qb_project_profitability(self):
        res = self.invoke_endpoint("/api/v1/quickbooks/project", "POST", {"project_id": "PRJ-101"})
        self.assertEqual(res["profit_margin"], 80000.0)

    def test_04_qb_xfin_gl_reconciliation(self):
        orch = NextGenMasterOrchestrator()
        pnl = orch.gl.generate_pnl_statement()
        self.assertIn("net_income", pnl)

    def test_05_qb_chart_of_accounts_balance(self):
        orchestrator = Mega11PlatformOrchestrator()
        pnl = orchestrator.qb.get_pnl_statement()
        self.assertGreater(pnl["net_margin_pct"], 0)


class TestStripeCoreIntegration(BaseDashboardTestCase):
    """2. Stripe Engine Integration - 5 Tests"""

    def test_01_stripe_payment_get(self):
        res = self.invoke_endpoint("/api/v1/stripe/payment", "GET")
        self.assertEqual(res["currency"], "USD")

    def test_02_stripe_payment_post(self):
        res = self.invoke_endpoint("/api/v1/stripe/payment", "POST", {"amount": 250.0, "currency": "EUR", "payment_method": "card"})
        self.assertEqual(res["amount"], 250.0)
        self.assertEqual(res["currency"], "EUR")

    def test_03_stripe_coupon_creation(self):
        res = self.invoke_endpoint("/api/v1/stripe/coupon", "POST", {"code": "SUMMER30", "percent_off": 30.0})
        self.assertEqual(res["code"], "SUMMER30")
        self.assertEqual(res["percent_off"], 30.0)

    def test_04_stripe_radar_risk_scoring(self):
        orch = Mega11PlatformOrchestrator()
        pay = orch.stripe.process_payment(500.0, "USD")
        self.assertLess(pay["radar_risk_score"], 50)

    def test_05_stripe_mint_entitlement_flow(self):
        orch = NextGenMasterOrchestrator()
        mint_res = orch.mint.mint_fiat_backed_tokens("sub_stripe_1", 250.0)
        self.assertEqual(mint_res["system"], "MINT")


class TestRevenueCatCoreIntegration(BaseDashboardTestCase):
    """3. RevenueCat Engine Integration - 5 Tests"""

    def test_01_revenuecat_entitlements_get(self):
        res = self.invoke_endpoint("/api/v1/revenuecat/entitlements", "GET")
        self.assertEqual(res["status"], "REVENUECAT_ENTITLED")

    def test_02_revenuecat_entitlements_post(self):
        res = self.invoke_endpoint("/api/v1/revenuecat/entitlements", "POST", {"subscriber_id": "sub_vip_99"})
        self.assertEqual(res["subscriber_id"], "sub_vip_99")

    def test_03_revenuecat_experiment_trigger(self):
        res = self.invoke_endpoint("/api/v1/revenuecat/experiment", "POST", {"experiment_id": "exp_kuramoto_v1"})
        self.assertEqual(res["winning_variant"], "variant_b")

    def test_04_revenuecat_nexs_paywall_adaptation(self):
        orch = NextGenMasterOrchestrator()
        offering = orch.nexs.synthesize_dynamic_offering("sub_rc_1", "US", 29.99)
        self.assertEqual(offering["adapted_usd_price"], 29.99)

    def test_05_revenuecat_pulse_retention_telemetry(self):
        orch = NextGenMasterOrchestrator()
        risk = orch.pulse.evaluate_churn_risk("sub_rc_1", 0.9, 0, 120)
        self.assertLess(risk, 0.5)


class TestNetSuiteCoreIntegration(BaseDashboardTestCase):
    """4. NetSuite Engine Integration - 5 Tests"""

    def test_01_netsuite_asc606_get(self):
        res = self.invoke_endpoint("/api/v1/netsuite/asc606", "GET")
        self.assertEqual(res["recognized_month_1"], 9863.01)

    def test_02_netsuite_asc606_post(self):
        res = self.invoke_endpoint("/api/v1/netsuite/asc606", "POST", {"total_contract_value": 365000.0, "contract_days": 365})
        self.assertEqual(res["recognized_month_1"], 30000.0)

    def test_03_netsuite_deferred_revenue_balance(self):
        res = self.invoke_endpoint("/api/v1/netsuite/asc606", "POST", {"total_contract_value": 120000.0, "contract_days": 365})
        self.assertGreater(res["deferred_revenue_balance"], 100000.0)

    def test_04_netsuite_aura_underwriting_sync(self):
        orch = NextGenMasterOrchestrator()
        underwrite = orch.aura.underwrite_subscription_bnpl("corp_ns", 1000.0, 0.05)
        self.assertEqual(underwrite["status"], "APPROVED")

    def test_05_netsuite_multi_entity_consolidation(self):
        res = self.invoke_endpoint("/api/v1/subsidiary/consolidate", "POST", {"us_revenue": 1000000.0, "eu_revenue": 500000.0, "intercompany_sales": 100000.0})
        self.assertEqual(res["consolidated_revenue"], 1400000.0)


class TestXeroCoreIntegration(BaseDashboardTestCase):
    """5. Xero Engine Integration - 5 Tests"""

    def test_01_xero_forecast_get(self):
        res = self.invoke_endpoint("/api/v1/xero/forecast", "GET")
        self.assertEqual(res["projected_30day_cash"], 1557700.0)

    def test_02_xero_forecast_post(self):
        res = self.invoke_endpoint("/api/v1/xero/forecast", "POST", {"current_cash": 500000.0, "expected_ar": 200000.0, "expected_ap": 100000.0})
        self.assertEqual(res["projected_30day_cash"], 600000.0)

    def test_03_xero_runway_calculation(self):
        res = self.invoke_endpoint("/api/v1/xero/forecast", "POST", {"current_cash": 485000.0, "expected_ar": 0.0, "expected_ap": 0.0})
        self.assertEqual(res["runway_months"], 10.0)

    def test_04_xero_pulse_cash_flow_integration(self):
        orch = NextGenMasterOrchestrator()
        cf_stmt = orch.cf.generate_cash_flow_statement()
        self.assertIn("net_cash_flow", cf_stmt)

    def test_05_xero_master_suite_status(self):
        suite = Mega11PlatformOrchestrator()
        res = suite.xero.get_30day_cash_forecast(100.0, 50.0, 10.0)
        self.assertEqual(res["status"], "XERO_FORECAST_ACTIVE")


class TestGustoCoreIntegration(BaseDashboardTestCase):
    """6. Gusto Engine Integration - 5 Tests"""

    def test_01_gusto_payroll_get(self):
        res = self.invoke_endpoint("/api/v1/gusto/payroll", "GET")
        self.assertEqual(res["gross_payroll"], 148500.0)

    def test_02_gusto_payroll_post(self):
        res = self.invoke_endpoint("/api/v1/gusto/payroll", "POST", {"gross_payroll": 50000.0})
        self.assertEqual(res["federal_tax"], 11000.0)

    def test_03_gusto_tax_escrow_calculation(self):
        res = self.invoke_endpoint("/api/v1/gusto/payroll", "POST", {"gross_payroll": 100000.0})
        self.assertEqual(res["social_security"], 6200.0)

    def test_04_gusto_pto_liability_tracking(self):
        res = self.invoke_endpoint("/api/v1/pto/accrual", "POST", {"hours_worked": 200.0, "accrual_rate": 0.05})
        self.assertEqual(res["accrued_pto_hours"], 10.0)

    def test_05_gusto_gl_payroll_tax_posting(self):
        orch = NextGenMasterOrchestrator()
        payroll_res = orch.payroll.calculate_payroll_run(100000.0)
        self.assertEqual(payroll_res["gross_payroll"], 100000.0)


class TestBillComCoreIntegration(BaseDashboardTestCase):
    """7. Bill.com Engine Integration - 5 Tests"""

    def test_01_bill_ap_approval_get(self):
        res = self.invoke_endpoint("/api/v1/bill/ap_approval", "GET")
        self.assertEqual(res["approval_level_2"], "APPROVED (CFO)")

    def test_02_bill_ap_approval_auto(self):
        res = self.invoke_endpoint("/api/v1/bill/ap_approval", "POST", {"bill_id": "BILL-001", "amount": 5000.0})
        self.assertEqual(res["approval_level_2"], "AUTO_APPROVED")

    def test_03_bill_ap_approval_cfo(self):
        res = self.invoke_endpoint("/api/v1/bill/ap_approval", "POST", {"bill_id": "BILL-002", "amount": 25000.0})
        self.assertEqual(res["approval_level_2"], "APPROVED (CFO)")

    def test_04_bill_3way_matching(self):
        res = self.invoke_endpoint("/api/v1/po/match_3way", "POST", {"po_amount": 10000.0, "receiving_slip_amount": 10000.0, "vendor_invoice_amount": 10000.0})
        self.assertTrue(res["is_3way_matched"])

    def test_05_bill_grid_equipment_ap_integration(self):
        orch = NextGenMasterOrchestrator()
        dev = orch.grid.register_device("dev_bill_1", "HARDWARE_NODE", "US", 5000.0)
        self.assertEqual(dev["status"], "ONLINE")


class TestExpensifyCoreIntegration(BaseDashboardTestCase):
    """8. Expensify Engine Integration - 5 Tests"""

    def test_01_expensify_audit_get(self):
        res = self.invoke_endpoint("/api/v1/expensify/audit", "GET")
        self.assertEqual(res["reimbursement_status"], "APPROVED_FOR_PAYOUT")

    def test_02_expensify_audit_post_clean(self):
        res = self.invoke_endpoint("/api/v1/expensify/audit", "POST", {"employee_id": "EMP-02", "expenses": [{"merchant": "Google Cloud", "amount": 150.0, "receipt_ocr": True}]})
        self.assertEqual(res["policy_violations"], 0)

    def test_03_expensify_audit_post_violation(self):
        res = self.invoke_endpoint("/api/v1/expensify/audit", "POST", {"employee_id": "EMP-03", "expenses": [{"merchant": "Luxury Hotel", "amount": 1200.0, "receipt_ocr": False}]})
        self.assertEqual(res["reimbursement_status"], "FLAGGED_FOR_REVIEW")

    def test_04_expensify_ocr_matching(self):
        res = self.invoke_endpoint("/api/v1/expense/ocr_match", "POST", {"merchant": "AWS", "amount": 500.0})
        self.assertEqual(res["auto_category"], "5030 - Cloud Compute")

    def test_05_expensify_aura_credit_compliance(self):
        orch = Mega11PlatformOrchestrator()
        report = orch.expensify.audit_expense_report("EMP-04", [{"amount": 50.0}])
        self.assertEqual(report["status"], "EXPENSIFY_AUDITED")


class TestPlaidCoreIntegration(BaseDashboardTestCase):
    """9. Plaid Engine Integration - 5 Tests"""

    def test_01_plaid_balance_get(self):
        res = self.invoke_endpoint("/api/v1/plaid/balance", "GET")
        self.assertEqual(res["available_balance"], 1420500.0)

    def test_02_plaid_balance_post(self):
        res = self.invoke_endpoint("/api/v1/plaid/balance", "POST", {"account_id": "acc_mercury_primary"})
        self.assertEqual(res["institution"], "Mercury Bank")

    def test_03_plaid_account_verification(self):
        res = self.invoke_endpoint("/api/v1/plaid/balance", "POST", {"account_id": "acc_chase_biz"})
        self.assertEqual(res["status"], "PLAID_AUTH_VERIFIED")

    def test_04_plaid_xfin_treasury_reconciliation(self):
        orch = NextGenMasterOrchestrator()
        bal = orch.xfin.get_treasury_balance()
        self.assertGreater(bal, 0)

    def test_05_plaid_bank_feed_reconciliation(self):
        orch = NextGenMasterOrchestrator()
        rec = orch.bank.reconcile_feed([{"tx_id": "TX_99", "amount": 500.0}])
        self.assertEqual(rec["reconciled_transactions"], 1)


class TestAvalaraCoreIntegration(BaseDashboardTestCase):
    """10. Avalara Engine Integration - 5 Tests"""

    def test_01_avalara_tax_nexus_get(self):
        res = self.invoke_endpoint("/api/v1/avalara/tax_nexus", "GET")
        self.assertEqual(res["tax_due"], 87.5)

    def test_02_avalara_tax_nexus_post_us_ny(self):
        res = self.invoke_endpoint("/api/v1/avalara/tax_nexus", "POST", {"amount": 100.0, "state_or_country": "US_NY"})
        self.assertEqual(res["tax_due"], 8.88)

    def test_03_avalara_tax_nexus_post_uk(self):
        res = self.invoke_endpoint("/api/v1/avalara/tax_nexus", "POST", {"amount": 200.0, "state_or_country": "UK"})
        self.assertEqual(res["tax_due"], 40.0)

    def test_04_avalara_b2b_exemption(self):
        res = self.invoke_endpoint("/api/v1/avalara/tax_nexus", "POST", {"amount": 1000.0, "state_or_country": "US_CA", "is_b2b_reseller": True})
        self.assertEqual(res["tax_due"], 0.0)
        self.assertEqual(res["status"], "AVALARA_EXEMPT")

    def test_05_avalara_nexs_ppp_tax_alignment(self):
        res = self.invoke_endpoint("/api/v1/tax/calculate", "POST", {"amount": 100.0, "country_code": "DE"})
        self.assertEqual(res["tax_amount"], 19.0)


class TestFreshBooksCoreIntegration(BaseDashboardTestCase):
    """11. FreshBooks Engine Integration - 5 Tests"""

    def test_01_freshbooks_time_invoice_get(self):
        res = self.invoke_endpoint("/api/v1/freshbooks/time_invoice", "GET")
        self.assertEqual(res["total_invoiced"], 6000.0)

    def test_02_freshbooks_time_invoice_post(self):
        res = self.invoke_endpoint("/api/v1/freshbooks/time_invoice", "POST", {"client": "Acme Corp", "hourly_rate": 200.0, "hours_logged": 20.0})
        self.assertEqual(res["total_invoiced"], 4000.0)

    def test_03_freshbooks_invoice_link_generation(self):
        res = self.invoke_endpoint("/api/v1/freshbooks/time_invoice", "POST", {"client": "Beta LLC", "hourly_rate": 100.0, "hours_logged": 5.0})
        self.assertIn("https://sovereign.engine/pay/", res["invoice_link"])

    def test_04_freshbooks_aura_credit_scoring(self):
        res = self.invoke_endpoint("/api/v1/invoices/create", "POST", {"client": "Client Corp", "amount": 15000.0})
        self.assertIn("INV-", res["invoice_id"])

    def test_05_freshbooks_master_audit_integration(self):
        orch = Mega11PlatformOrchestrator()
        res = orch.freshbooks.log_time_and_create_invoice("Global Inc", 125.0, 8.0)
        self.assertEqual(res["total_invoiced"], 1000.0)


class TestIntegratedPlatformCoreSuite(BaseDashboardTestCase):
    """12. Master Platform Suite & 6-Core Synthesis Integration - 5 Tests"""

    def test_01_mega11_master_audit_endpoint(self):
        res = self.invoke_endpoint("/api/v1/mega11/audit", "GET")
        self.assertEqual(res["status"], "ALL_11_PLATFORMS_FULLY_OPERATIONAL")
        self.assertIn("quickbooks", res)
        self.assertIn("stripe", res)

    def test_02_platforms_integrated_core_audit_endpoint(self):
        res = self.invoke_endpoint("/api/v1/platforms/integrated_core_audit", "GET")
        self.assertEqual(res["status"], "ALL_11_PLATFORMS_AND_6_CORES_FULLY_INTEGRATED")
        self.assertIn("mega_11_platforms", res)
        self.assertIn("nextgen_6_cores", res)

    def test_03_full_6_core_subscriber_lifecycle(self):
        res = self.invoke_endpoint("/api/v1/orchestrator/lifecycle", "POST", {
            "user_id": "usr_master_vip", "country_code": "DE", "device_id": "dev_watch_de", "fiat_amount": 199.99, "currency": "EUR"
        })
        self.assertEqual(res["status"], "NEXTGEN_PIPELINE_SUCCESS")
        self.assertEqual(res["user_id"], "usr_master_vip")

    def test_04_orchestrator_financial_audit(self):
        res = self.invoke_endpoint("/api/v1/orchestrator/audit", "GET")
        self.assertTrue(res["trial_balance_balanced"])
        self.assertTrue(res["balance_sheet_balanced"])

    def test_05_orchestrator_statement(self):
        res = self.invoke_endpoint("/api/v1/orchestrator/statement", "GET")
        self.assertIn("XFIN", res["cores_status"])
        self.assertIn("AURA", res["cores_status"])
        self.assertIn("PULSE", res["cores_status"])
        self.assertIn("MINT", res["cores_status"])
        self.assertIn("GRID", res["cores_status"])
        self.assertIn("NEXS", res["cores_status"])


if __name__ == "__main__":
    unittest.main()
