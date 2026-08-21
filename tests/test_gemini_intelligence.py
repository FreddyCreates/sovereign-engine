"""
Automated Test Suite for Multi-Node Gemini Intelligence Engine
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sovereign_infrastructure", "nextgen_systems")))

from gemini_intelligence_engine import (
    CFOIntelligenceNode,
    PaywallOptNode,
    RetentionStrategyNode,
    AppSynthesisNode,
    BiometricHealthNode,
    GeminiChatOrchestrator
)

class TestGeminiIntelligenceEngine(unittest.TestCase):

    def setUp(self):
        self.cfo = CFOIntelligenceNode()
        self.paywall = PaywallOptNode()
        self.retention = RetentionStrategyNode()
        self.app = AppSynthesisNode()
        self.health = BiometricHealthNode()
        self.orchestrator = GeminiChatOrchestrator()

    def test_01_cfo_node(self):
        res = self.cfo.generate_cfo_commentary(148920.0, 331246.0, 74.2)
        self.assertIn("MRR", res["executive_summary"])

    def test_02_paywall_node(self):
        res = self.paywall.generate_paywall_copy("DE", "PRO")
        self.assertEqual(res["recommended_theme"], "MINIMAL_DARK")

    def test_03_retention_node(self):
        res = self.retention.generate_winback_strategy(60.0)
        self.assertEqual(res["action"], "AGGRESSIVE_WINBACK")

    def test_04_app_synthesis_node(self):
        res = self.app.synthesize_app_code("Sovereign Fitness AI")
        self.assertIn("@Composable", res["compose_ui_code"])

    def test_05_biometric_health_node(self):
        res = self.health.evaluate_mesh_telemetry(72, 98.5)
        self.assertEqual(res["consensus_status"], "HEALTHY")

    def test_06_gemini_orchestrator_chat(self):
        res = self.orchestrator.process_chat_query("Show me CFO Insights")
        self.assertEqual(res["system"], "CFO_INTELLIGENCE")

    def test_07_gemini_orchestrator_xfin_chat(self):
        res = self.orchestrator.process_chat_query("Check XFIN FX Arbitrage Yield BRL")
        self.assertEqual(res["system"], "XFIN_CORE")
        self.assertIn("XFIN", res["reply"])

    def test_08_gemini_orchestrator_aura_chat(self):
        res = self.orchestrator.process_chat_query("Evaluate AURA credit underwriting status")
        self.assertEqual(res["system"], "AURA_CORE")
        self.assertIn("AURA", res["reply"])

    def test_09_gemini_orchestrator_pulse_chat(self):
        res = self.orchestrator.process_chat_query("Check PULSE core telemetry")
        self.assertEqual(res["system"], "PULSE_CORE")
        self.assertIn("PULSE", res["reply"])

    def test_10_gemini_orchestrator_mint_chat(self):
        res = self.orchestrator.process_chat_query("Show MINT tokenomics FORMA golden ratio yield")
        self.assertEqual(res["system"], "MINT_CORE")
        self.assertIn("MINT", res["reply"])

    def test_11_gemini_orchestrator_grid_chat(self):
        res = self.orchestrator.process_chat_query("Check GRID Wear OS IoT hardware mesh")
        self.assertEqual(res["system"], "GRID_CORE")
        self.assertIn("GRID", res["reply"])

    def test_12_gemini_orchestrator_nexs_chat(self):
        res = self.orchestrator.process_chat_query("Synthesize app with NEXS Jetpack Compose UI code")
        self.assertEqual(res["system"], "NEXS_CORE")
        self.assertIn("NEXS", res["reply"])

if __name__ == "__main__":
    unittest.main()
