"""
Exhaustive Automated Unit Test Suite for Multi-Node Gemini Intelligence Generation Engine
Tests CFO Intelligence Node, Tax Synthesis Node, Retention Strategy Node, Paywall Optimization Node,
App Synthesis Node, Biometric Wear OS Health Node, Conversational Router & Master Orchestrator Integration.
"""

import sys
import os
import unittest

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, root_dir)
sys.path.insert(0, os.path.join(root_dir, "sovereign_infrastructure", "nextgen_systems"))

from full_saas_accounting_suite import GeneralLedgerEngine, PayrollTaxEngine
from gemini_intelligence_engine import (
    GeminiIntelligenceEngine,
    CFOIntelligenceNode,
    TaxSynthesisNode,
    RetentionStrategyNode,
    PaywallOptNode,
    AppSynthesisNode,
    BiometricHealthNode
)
from nextgen_master_orchestrator import NextGenMasterOrchestrator


class TestCFOIntelligenceNode(unittest.TestCase):
    """Test Suite for Node 1: CFO Intelligence & Financial Commentary"""

    def setUp(self):
        self.node = CFOIntelligenceNode()
        self.gl = GeneralLedgerEngine()

    def test_01_cfo_commentary_standalone(self):
        res = self.node.generate_cfo_commentary(mrr=150000.0, net_income=300000.0, net_margin=75.0)
        self.assertEqual(res["mrr"], 150000.0)
        self.assertEqual(res["arr"], 1800000.0)
        self.assertEqual(res["status"], "OPTIMAL_GROWTH")
        self.assertIn("Sovereign Engine operating at $150,000.00 MRR", res["executive_summary"])

    def test_02_cfo_commentary_gl_integrated(self):
        res = self.node.generate_cfo_commentary(gl=self.gl)
        self.assertGreater(res["gross_revenue"], 0)
        self.assertGreater(res["net_income"], 0)
        self.assertGreater(res["cash_runway_months"], 0)
        self.assertIn("capital_allocation_strategy", res)


class TestTaxSynthesisNode(unittest.TestCase):
    """Test Suite for Node 2: Section 41 R&D Credit & Tax Audit Synthesis"""

    def setUp(self):
        self.node = TaxSynthesisNode()
        self.gl = GeneralLedgerEngine()
        self.payroll = PayrollTaxEngine(self.gl)

    def test_01_tax_synthesis_standalone(self):
        res = self.node.synthesize_tax_strategy(cloud_spend=50000.0, rd_payroll=100000.0)
        # Total QRE = 50,000 + (100,000 * 0.8) = 130,000
        self.assertEqual(res["total_qualified_research_expenses"], 130000.0)
        # Section 41 Credit = 130,000 * 0.14 = 18,200
        self.assertEqual(res["section_41_tax_credit"], 18200.0)
        self.assertEqual(res["status"], "TAX_AUDIT_COMPLIANT")
        self.assertGreater(res["audit_readiness_score"], 0.95)

    def test_02_tax_synthesis_gl_payroll_integrated(self):
        self.payroll.calculate_payroll_run(gross_payroll=25000.0, state="CA")
        res = self.node.synthesize_tax_strategy(gl=self.gl, payroll=self.payroll)
        self.assertEqual(res["form_941_audit_status"], "IRS_FORM_941_AUDIT_READY")
        self.assertIn("Section 41", res["tax_recommendation"])


class TestRetentionStrategyNode(unittest.TestCase):
    """Test Suite for Node 3: Churn Defense & Intercept Generator"""

    def setUp(self):
        self.node = RetentionStrategyNode()

    def test_01_critical_churn_risk(self):
        res = self.node.generate_winback_strategy(churn_risk_pct=85.0, user_id="usr_high_risk")
        self.assertEqual(res["risk_tier"], "CRITICAL")
        self.assertEqual(res["action"], "EMERGENCY_CRITICAL_WINBACK")
        self.assertEqual(res["discount_pct"], 50.0)
        self.assertIn("50% OFF", res["message"])

    def test_02_moderate_churn_risk_roi(self):
        res = self.node.generate_winback_strategy(churn_risk_pct=30.0, user_id="usr_mod_risk", arpu=100.0)
        self.assertEqual(res["risk_tier"], "MEDIUM")
        self.assertEqual(res["discount_pct"], 20.0)
        self.assertGreater(res["financial_impact"]["net_retention_roi_pct"], 0)


class TestPaywallOptNode(unittest.TestCase):
    """Test Suite for Node 4: Paywall AST Copy Synthesizer"""

    def test_01_paywall_theme_localization(self):
        node = PaywallOptNode()
        res_us = node.generate_paywall_copy("US", "PRO")
        res_de = node.generate_paywall_copy("DE", "ENTERPRISE")
        self.assertEqual(res_us["recommended_theme"], "NEON_CYAN")
        self.assertEqual(res_de["recommended_theme"], "MINIMAL_DARK")
        self.assertIn("Enterprise", res_de["headline"])


class TestAppSynthesisNode(unittest.TestCase):
    """Test Suite for Node 5: Jetpack Compose App Code Synthesizer"""

    def test_01_app_code_synthesis(self):
        node = AppSynthesisNode()
        res = node.synthesize_app_code("Sovereign Portfolio Pro")
        self.assertEqual(res["app_name"], "Sovereign Portfolio Pro")
        self.assertIn("@Composable", res["compose_ui_code"])
        self.assertIn("RevenueCat SDK 8.2.0", res["compose_ui_code"])


class TestBiometricHealthNode(unittest.TestCase):
    """Test Suite for Node 6: Wear OS Biometric Radar"""

    def test_01_telemetry_evaluation(self):
        node = BiometricHealthNode()
        healthy = node.evaluate_mesh_telemetry(bpm=72, spo2_pct=98.5)
        self.assertEqual(healthy["consensus_status"], "HEALTHY")
        
        anomaly = node.evaluate_mesh_telemetry(bpm=135, spo2_pct=91.0)
        self.assertEqual(anomaly["consensus_status"], "ANOMALY_DETECTED")


class TestGeminiIntelligenceEngine(unittest.TestCase):
    """Test Suite for Multi-Node Engine & Conversational Router"""

    def setUp(self):
        self.gl = GeneralLedgerEngine()
        self.engine = GeminiIntelligenceEngine(gl=self.gl)

    def test_01_multi_node_report(self):
        report = self.engine.generate_multi_node_report()
        self.assertEqual(report["system_status"], "MULTI_NODE_SYNTHESIS_COMPLETE")
        self.assertIn("cfo_intelligence", report["nodes"])
        self.assertIn("tax_synthesis", report["nodes"])
        self.assertIn("retention_strategy", report["nodes"])

    def test_02_chat_query_routing(self):
        cfo_q = self.engine.process_chat_query("Show me our CFO commentary and Net Income margins")
        tax_q = self.engine.process_chat_query("What is our Section 41 tax credit estimate?")
        churn_q = self.engine.process_chat_query("What churn winback offer strategy should we use?")
        general_q = self.engine.process_chat_query("Hello Sovereign AI")

        self.assertEqual(cfo_q["system"], "CFO_INTELLIGENCE")
        self.assertEqual(tax_q["system"], "TAX_SYNTHESIS")
        self.assertEqual(churn_q["system"], "RETENTION_DEFENSE")
        self.assertEqual(general_q["system"], "GENERAL_GEMINI")


class TestMasterOrchestratorIntegration(unittest.TestCase):
    """Test Suite for NextGenMasterOrchestrator Integration"""

    def test_01_master_orchestrator_gemini_integration(self):
        orchestrator = NextGenMasterOrchestrator()
        stmt = orchestrator.generate_consolidated_sovereign_statement()
        self.assertIn("gemini_intelligence", stmt)
        self.assertEqual(stmt["gemini_intelligence"]["system_status"], "MULTI_NODE_SYNTHESIS_COMPLETE")


if __name__ == "__main__":
    unittest.main()
