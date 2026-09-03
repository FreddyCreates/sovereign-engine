"""
Exhaustive Automated Test Suite for RevenueCat Substrate & Native SaaS Replacements
===================================================================================
Covers:
1. RevenueCat StoreKit 2 Paywall Rules & Entitlements ('sovereign_office_pro', 'sovereign_office_unlimited_ai') & Subscriber Churn Telemetry (5 Tests)
2. SovereignNativePay Engine (5 Tests)
3. SovereignNativeAccounting Engine (5 Tests)
4. SovereignNativeSign Engine (5 Tests)
5. SovereignNativeAPExpense Engine (5 Tests)
6. SovereignNativePayrollTax Engine (5 Tests)
7. SovereignInnerAIEngine DAG Execution & Wiring (5 Tests)
8. SovereignDashboardServer REST Endpoints Wiring (5 Tests)
"""

import unittest
import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../sovereign_infrastructure/nextgen_systems")))

from sovereign_infrastructure.nextgen_systems.mega_11_platform_master_suite import (
    RevenueCatMasterModule,
    SovereignNativePay,
    SovereignNativeAccounting,
    SovereignNativeSign,
    SovereignNativeAPExpense,
    SovereignNativePayrollTax,
    QuickBooksMasterModule,
    Mega11PlatformOrchestrator,
    SovereignZKDilithiumProofEngine
)

from sovereign_infrastructure.nextgen_systems.sovereign_inner_ai_engine import (
    SovereignInnerAIEngine,
    InnerAppSkillRouter,
    InnerContextualPlanner,
    InnerSkillExecutor
)


class TestRevenueCatSubstrateEngine(unittest.TestCase):
    """Engine 1: RevenueCat StoreKit 2 & Subscriber Churn Telemetry (5 Tests)"""

    def setUp(self):
        self.rc = RevenueCatMasterModule()

    def test_01_get_entitlements_includes_sovereign_office_pro_and_unlimited_ai(self):
        """1. Verify get_entitlements returns sovereign_office_pro and sovereign_office_unlimited_ai."""
        res = self.rc.get_entitlements("sub_test_01")
        self.assertEqual(res["status"], "REVENUECAT_ENTITLED")
        self.assertIn("sovereign_office_pro", res["entitlements"])
        self.assertIn("sovereign_office_unlimited_ai", res["entitlements"])
        self.assertTrue(res["entitlements"]["sovereign_office_pro"]["is_active"])

    def test_02_check_entitlement_grant_and_verify(self):
        """2. Verify check_entitlement evaluates active access for sovereign_office_pro."""
        res = self.rc.check_entitlement("sub_test_01", "sovereign_office_pro")
        self.assertEqual(res["status"], "REVENUECAT_ENTITLEMENT_CHECKED")
        self.assertTrue(res["access_granted"])
        self.assertTrue(res["is_active"])

    def test_03_check_entitlement_unlimited_ai(self):
        """3. Verify check_entitlement evaluates active access for sovereign_office_unlimited_ai."""
        res = self.rc.check_entitlement("sub_test_01", "sovereign_office_unlimited_ai")
        self.assertEqual(res["status"], "REVENUECAT_ENTITLEMENT_CHECKED")
        self.assertTrue(res["access_granted"])

    def test_04_get_storekit2_paywall_rules(self):
        """4. Verify get_storekit2_paywall_rules returns StoreKit 2 rules and AST components."""
        res = self.rc.get_storekit2_paywall_rules("offering_enterprise")
        self.assertTrue(res["storekit2_enabled"])
        self.assertIn("sovereign_office_pro", res["paywall_rules"])
        self.assertIn("sovereign_office_unlimited_ai", res["paywall_rules"])
        self.assertEqual(res["paywall_rules"]["sovereign_office_pro"]["product_id"], "sovereign_office_pro_annual")

    def test_05_get_churn_telemetry(self):
        """5. Verify subscriber churn telemetry returns churn probability, LTV, and retention offers."""
        res = self.rc.get_churn_telemetry("sub_test_01")
        self.assertEqual(res["status"], "SUBSCRIBER_CHURN_TELEMETRY_RETRIEVED")
        self.assertLess(res["churn_probability"], 0.05)
        self.assertGreater(res["discounted_ltv_usd"], 2000.0)
        self.assertEqual(res["retention_tier"], "VIP_LOW_RISK")


class TestSovereignNativePayEngine(unittest.TestCase):
    """Engine 2: SovereignNativePay Engine (5 Tests)"""

    def setUp(self):
        self.qb = QuickBooksMasterModule()
        self.pay = SovereignNativePay(self.qb)

    def test_01_process_payment_gl_posting(self):
        """1. Verify payment posts double-entry GL entry to 1000 Cash and 4000 Revenue."""
        res = self.pay.process_payment(1500.00, "USD", "cust_101", "Pro License Payment")
        self.assertEqual(res["status"], "NATIVE_PAY_SETTLED")
        self.assertEqual(res["amount"], 1500.00)
        self.assertEqual(res["debit_account"], "1000 Cash")
        self.assertEqual(res["credit_account"], "4000 Revenue")
        self.assertEqual(res["balance_variance"], 0.00)

    def test_02_process_payment_zk_dilithium_proof(self):
        """2. Verify payment generates post-quantum ZK Dilithium proof."""
        res = self.pay.process_payment(2500.00, "USD", "cust_102")
        proof = res["zk_dilithium_proof"]
        self.assertEqual(proof["algorithm"], "Dilithium5_PostQuantum_ZK")
        self.assertEqual(proof["verified"], "TRUE")
        self.assertTrue(proof["zk_proof_signature"].startswith("zk_sig_dilithium5_"))

    def test_03_process_payment_balance_sheet_equilibrium(self):
        """3. Verify payment maintains GL trial balance debits == credits equilibrium."""
        self.pay.process_payment(4500.00, "USD", "cust_103")
        tb = self.qb.generate_trial_balance()
        self.assertTrue(tb["is_balanced"])

    def test_04_process_payment_multi_currency(self):
        """4. Verify multi-currency payment settlement."""
        res = self.pay.process_payment(3200.00, "EUR", "cust_104")
        self.assertEqual(res["currency"], "EUR")
        self.assertEqual(res["amount"], 3200.00)

    def test_05_process_payment_pnl_impact(self):
        """5. Verify payment correctly increases net income in P&L statement."""
        pnl_before = self.qb.get_pnl_statement()["gross_revenue"]
        self.pay.process_payment(1000.00, "USD", "cust_105")
        pnl_after = self.qb.get_pnl_statement()["gross_revenue"]
        self.assertEqual(pnl_after, pnl_before + 1000.00)


class TestSovereignNativeAccountingEngine(unittest.TestCase):
    """Engine 3: SovereignNativeAccounting Engine (5 Tests)"""

    def setUp(self):
        self.qb = QuickBooksMasterModule()
        self.acc = SovereignNativeAccounting(self.qb)

    def test_01_post_accounting_transaction_double_entry(self):
        """1. Verify posting double-entry transaction (1000 Cash, 4000 Revenue)."""
        res = self.acc.post_accounting_transaction(5000.00, "Enterprise Software License", "1000", "4000")
        self.assertEqual(res["status"], "NATIVE_ACCOUNTING_POSTED")
        self.assertEqual(res["amount"], 5000.00)
        self.assertEqual(res["balance_variance"], 0.00)

    def test_02_post_accounting_transaction_zk_proof(self):
        """2. Verify ZK Dilithium proof generated for accounting transaction."""
        res = self.acc.post_accounting_transaction(3000.00, "Consulting Retainer")
        self.assertIn("zk_dilithium_proof", res)
        self.assertEqual(res["zk_dilithium_proof"]["verified"], "TRUE")

    def test_03_trial_balance_verification(self):
        """3. Verify posting entries preserves trial balance equilibrium."""
        self.acc.post_accounting_transaction(2000.00, "Entry A")
        self.acc.post_accounting_transaction(4000.00, "Entry B")
        tb = self.qb.generate_trial_balance()
        self.assertTrue(tb["is_balanced"])

    def test_04_custom_chart_of_accounts_posting(self):
        """4. Verify posting to custom accounts initializes account and posts cleanly."""
        res = self.acc.post_accounting_transaction(1200.00, "Custom Asset Transfer", "1050", "4050")
        self.assertEqual(res["debit_account"], "1050")
        self.assertEqual(res["credit_account"], "4050")

    def test_05_audit_trail_entry_id(self):
        """5. Verify unique audit trail journal entry ID generation."""
        res1 = self.acc.post_accounting_transaction(100.00, "TX 1")
        res2 = self.acc.post_accounting_transaction(200.00, "TX 2")
        self.assertNotEqual(res1["accounting_entry_id"], res2["accounting_entry_id"])


class TestSovereignNativeSignEngine(unittest.TestCase):
    """Engine 4: SovereignNativeSign Engine (5 Tests)"""

    def setUp(self):
        self.qb = QuickBooksMasterModule()
        self.sign = SovereignNativeSign(self.qb)

    def test_01_execute_signature_settlement(self):
        """1. Verify signature settlement executes contract signature."""
        res = self.sign.execute_signature_settlement("Master SLA Contract", "cfo@apex.com", "CFO", 15000.00)
        self.assertEqual(res["status"], "NATIVE_SIGN_EXECUTED")
        self.assertEqual(res["contract_value"], 15000.00)
        self.assertEqual(res["signer_email"], "cfo@apex.com")

    def test_02_signature_gl_posting_1000_cash_4000_revenue(self):
        """2. Verify signature settlement posts GL entry to 1000 Cash and 4000 Revenue."""
        res = self.sign.execute_signature_settlement("SaaS Agreement", "exec@apex.com", "CEO", 10000.00)
        self.assertEqual(res["debit_account"], "1000 Cash")
        self.assertEqual(res["credit_account"], "4000 Revenue")
        self.assertEqual(res["balance_variance"], 0.00)

    def test_03_signature_zk_dilithium_proof(self):
        """3. Verify post-quantum ZK Dilithium proof for document signature & settlement."""
        res = self.sign.execute_signature_settlement("ND A & SLA", "legal@apex.com", "General Counsel", 5000.00)
        proof = res["zk_dilithium_proof"]
        self.assertEqual(proof["algorithm"], "Dilithium5_PostQuantum_ZK")
        self.assertEqual(proof["verified"], "TRUE")

    def test_04_signature_id_uniqueness(self):
        """4. Verify signature IDs generated are unique per execution."""
        sig1 = self.sign.execute_signature_settlement("Doc 1", "a@test.com")
        sig2 = self.sign.execute_signature_settlement("Doc 2", "b@test.com")
        self.assertNotEqual(sig1["signature_id"], sig2["signature_id"])

    def test_05_signature_trial_balance_impact(self):
        """5. Verify GL trial balance remains balanced after signature settlement."""
        self.sign.execute_signature_settlement("Enterprise Deal", "sales@apex.com", "VP Sales", 50000.00)
        tb = self.qb.generate_trial_balance()
        self.assertTrue(tb["is_balanced"])


class TestSovereignNativeAPExpenseEngine(unittest.TestCase):
    """Engine 5: SovereignNativeAPExpense Engine (5 Tests)"""

    def setUp(self):
        self.qb = QuickBooksMasterModule()
        self.ap_exp = SovereignNativeAPExpense(self.qb)

    def test_01_process_ap_expense_settlement(self):
        """1. Verify AP expense settlement processes vendor bill."""
        res = self.ap_exp.process_ap_expense_settlement("AWS Infrastructure", 2500.00, "Cloud Computing", True)
        self.assertEqual(res["status"], "NATIVE_AP_EXPENSE_SETTLED")
        self.assertEqual(res["vendor_or_merchant"], "AWS Infrastructure")
        self.assertEqual(res["amount"], 2500.00)

    def test_02_ap_expense_gl_posting(self):
        """2. Verify AP expense posts GL transaction (1000 Cash, 4000 Revenue)."""
        res = self.ap_exp.process_ap_expense_settlement("Datadog Monitoring", 800.00)
        self.assertEqual(res["debit_account"], "1000 Cash")
        self.assertEqual(res["credit_account"], "4000 Revenue")
        self.assertEqual(res["balance_variance"], 0.00)

    def test_03_ap_expense_receipt_ocr_verification(self):
        """3. Verify SmartScan OCR verification status is preserved."""
        res = self.ap_exp.process_ap_expense_settlement("GitHub Enterprise", 450.00, "DevTools", True)
        self.assertTrue(res["receipt_ocr_verified"])

    def test_04_ap_expense_zk_proof(self):
        """4. Verify ZK Dilithium settlement proof issued for expense claim."""
        res = self.ap_exp.process_ap_expense_settlement("Snowflake Data Warehouse", 1800.00)
        proof = res["zk_dilithium_proof"]
        self.assertEqual(proof["verified"], "TRUE")

    def test_05_ap_expense_trial_balance_equilibrium(self):
        """5. Verify GL trial balance equilibrium after processing AP expenses."""
        self.ap_exp.process_ap_expense_settlement("OpenAI API", 1200.00)
        tb = self.qb.generate_trial_balance()
        self.assertTrue(tb["is_balanced"])


class TestSovereignNativePayrollTaxEngine(unittest.TestCase):
    """Engine 6: SovereignNativePayrollTax Engine (5 Tests)"""

    def setUp(self):
        self.qb = QuickBooksMasterModule()
        self.payroll_tax = SovereignNativePayrollTax(self.qb)

    def test_01_run_payroll_tax_settlement(self):
        """1. Verify payroll tax settlement calculates FIT, FICA, and Net Pay."""
        res = self.payroll_tax.run_payroll_tax_settlement(100000.00, "CA")
        self.assertEqual(res["status"], "NATIVE_PAYROLL_TAX_SETTLED")
        self.assertEqual(res["gross_payroll"], 100000.00)
        self.assertEqual(res["federal_income_tax"], 22000.00)
        self.assertEqual(res["social_security"], 6200.00)
        self.assertEqual(res["medicare"], 1450.00)
        self.assertEqual(res["net_disbursement"], 70350.00)

    def test_02_payroll_tax_gl_posting(self):
        """2. Verify payroll tax posts double-entry GL entry (1000 Cash, 4000 Revenue)."""
        res = self.payroll_tax.run_payroll_tax_settlement(50000.00, "NY")
        self.assertEqual(res["debit_account"], "1000 Cash")
        self.assertEqual(res["credit_account"], "4000 Revenue")
        self.assertEqual(res["balance_variance"], 0.00)

    def test_03_payroll_tax_zk_proof(self):
        """3. Verify ZK Dilithium proof issued for payroll tax escrow."""
        res = self.payroll_tax.run_payroll_tax_settlement(75000.00, "TX")
        proof = res["zk_dilithium_proof"]
        self.assertEqual(proof["algorithm"], "Dilithium5_PostQuantum_ZK")
        self.assertEqual(proof["verified"], "TRUE")

    def test_04_payroll_tax_state_code(self):
        """4. Verify state code normalization."""
        res = self.payroll_tax.run_payroll_tax_settlement(20000.00, "fl")
        self.assertEqual(res["state"], "FL")

    def test_05_payroll_tax_trial_balance(self):
        """5. Verify GL trial balance equilibrium after running payroll tax settlement."""
        self.payroll_tax.run_payroll_tax_settlement(148500.00, "CA")
        tb = self.qb.generate_trial_balance()
        self.assertTrue(tb["is_balanced"])


class TestSovereignInnerAIEngineIntegration(unittest.TestCase):
    """Engine 7: SovereignInnerAIEngine DAG Execution & Wiring (5 Tests)"""

    def setUp(self):
        self.engine = SovereignInnerAIEngine(memory_dir=".agents/inner_memory")

    def test_01_router_matches_skills_and_adapters(self):
        """1. Verify InnerAppSkillRouter resolves goal to skills and adapters."""
        res = self.engine.router.route_goal("Execute RevenueCat entitlement check and post double-entry GL")
        self.assertGreater(res["total_skills_matched"], 0)
        self.assertGreater(res["total_adapters_matched"], 0)

    def test_02_planner_creates_6_step_dag_plan(self):
        """2. Verify InnerContextualPlanner formulates 6-step DAG plan with Native SaaS Replacements."""
        route = self.engine.router.route_goal("Automate native accounting")
        plan = self.engine.planner.create_dag_plan("Automate native accounting", route["matched_skills"], route["matched_adapters"])
        self.assertEqual(plan["total_steps"], 6)
        self.assertIn("node_06_native_saas_replacements", plan["execution_order"])

    def test_03_executor_runs_native_saas_replacements_node(self):
        """3. Verify InnerSkillExecutor executes Native SaaS Replacements node and posts 1000 Cash / 4000 Revenue."""
        route = self.engine.router.route_goal("Automate native accounting")
        plan = self.engine.planner.create_dag_plan("Automate native accounting", route["matched_skills"], route["matched_adapters"])
        exec_res = self.engine.executor.execute_plan(plan)
        self.assertEqual(exec_res["nodes_executed"], 6)
        native_trace = next(t for t in exec_res["execution_trace"] if t["node_id"] == "node_06_native_saas_replacements")
        self.assertEqual(native_trace["result"]["double_entry_gl_posting"]["debit_account"], "1000 Cash")
        self.assertEqual(native_trace["result"]["double_entry_gl_posting"]["credit_account"], "4000 Revenue")

    def test_04_master_process_goal_end_to_end(self):
        """4. Verify SovereignInnerAIEngine process_goal executes end-to-end and returns complete master_audit."""
        res = self.engine.process_goal("Automate corporate accounting with RevenueCat paywalls and ZK Dilithium proofs")
        self.assertEqual(res["status"], "SUCCESS")
        audit = res["master_audit"]
        self.assertTrue(audit["sovereign_office_pro_entitled"])
        self.assertTrue(audit["sovereign_office_unlimited_ai_entitled"])
        self.assertTrue(audit["native_saas_replacements_executed"])
        self.assertTrue(audit["double_entry_gl_1000_cash_4000_revenue_posted"])
        self.assertTrue(audit["zk_dilithium_proof_generated"])
        self.assertEqual(audit["kuramoto_phase_coherence_R"], 0.9999)

    def test_05_telemetry_pulse_kuramoto_coherence(self):
        """5. Verify telemetry pulse emits Kuramoto phase coherence R = 0.9999."""
        pulse = self.engine.telemetry.emit_pulse()
        self.assertEqual(pulse["kuramoto_coherence_R"], 0.9999)


class TestSovereignDashboardServerRESTEndpoints(unittest.TestCase):
    """Engine 8: SovereignDashboardServer REST Endpoints Wiring (5 Tests)"""

    def setUp(self):
        self.mega11 = Mega11PlatformOrchestrator()

    def test_01_revenuecat_entitlement_check_endpoint(self):
        """1. Verify RevenueCat entitlement check for sovereign_office_pro."""
        res = self.mega11.rc.check_entitlement("sub_101", "sovereign_office_pro")
        self.assertTrue(res["access_granted"])
        self.assertEqual(res["entitlement_id"], "sovereign_office_pro")

    def test_02_revenuecat_storekit2_paywall_rules_endpoint(self):
        """2. Verify RevenueCat StoreKit 2 paywall rules endpoint."""
        res = self.mega11.rc.get_storekit2_paywall_rules("default")
        self.assertTrue(res["storekit2_enabled"])
        self.assertIn("sovereign_office_pro", res["paywall_rules"])

    def test_03_revenuecat_churn_telemetry_endpoint(self):
        """3. Verify RevenueCat subscriber churn telemetry endpoint."""
        res = self.mega11.rc.get_churn_telemetry("sub_101")
        self.assertEqual(res["status"], "SUBSCRIBER_CHURN_TELEMETRY_RETRIEVED")
        self.assertIn("churn_probability", res)

    def test_04_native_saas_replacements_audit_integration(self):
        """4. Verify Native SaaS Replacements integrated in mega 11 platform audit."""
        audit = self.mega11.run_full_11_platform_audit()
        self.assertIn("native_saas_replacements", audit)
        native = audit["native_saas_replacements"]
        self.assertEqual(native["native_pay"]["status"], "NATIVE_PAY_SETTLED")
        self.assertEqual(native["native_accounting"]["status"], "NATIVE_ACCOUNTING_POSTED")
        self.assertEqual(native["native_sign"]["status"], "NATIVE_SIGN_EXECUTED")
        self.assertEqual(native["native_ap_expense"]["status"], "NATIVE_AP_EXPENSE_SETTLED")
        self.assertEqual(native["native_payroll_tax"]["status"], "NATIVE_PAYROLL_TAX_SETTLED")

    def test_05_native_pay_gl_posting_and_zk_proof(self):
        """5. Verify Native Pay endpoint posts 1000 Cash / 4000 Revenue GL and generates ZK Dilithium proof."""
        res = self.mega11.native_pay.process_payment(999.00, "USD", "cust_999")
        self.assertEqual(res["debit_account"], "1000 Cash")
        self.assertEqual(res["credit_account"], "4000 Revenue")
        self.assertEqual(res["zk_dilithium_proof"]["algorithm"], "Dilithium5_PostQuantum_ZK")


if __name__ == "__main__":
    unittest.main()
