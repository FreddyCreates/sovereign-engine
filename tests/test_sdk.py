"""
Automated Test Suite for Sovereign Core SDK and Sovereign AI SDK
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sdk", "python")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ai_sdk", "python")))

from sovereign_sdk import SovereignClient
from sovereign_ai_sdk import (
    AURARiskUnderwriterAgent,
    PULSERetentionAgent,
    XFINArbitrageAgent,
    MINTBurnAgent,
    NEXSAgentSynthesizer,
    SovereignAgenticOrchestrator
)

class TestSDKAndAISDK(unittest.TestCase):

    # =========================================================================
    # CORE SDK TESTS
    # =========================================================================
    def setUp(self):
        self.client = SovereignClient("http://localhost:8090")
        self.orchestrator = SovereignAgenticOrchestrator()

    def test_01_sdk_get_overview(self):
        res = self.client.get_overview()
        self.assertIn("mrr", res)

    def test_02_sdk_get_ledger(self):
        res = self.client.get_ledger()
        self.assertIn("net_income", res)

    def test_03_sdk_create_invoice(self):
        res = self.client.create_invoice("Apex Global", 12500.0)
        self.assertEqual(res["client"], "Apex Global")

    # =========================================================================
    # AI SDK TESTS (AGENTS)
    # =========================================================================
    def test_04_ai_sdk_aura_agent(self):
        agent = AURARiskUnderwriterAgent()
        res = agent.evaluate_subscriber_risk("usr_test_01", 500.0, 12)
        self.assertIn("risk_score", res)
        self.assertIn("underwriting_status", res)

    def test_05_ai_sdk_pulse_agent(self):
        agent = PULSERetentionAgent()
        res = agent.evaluate_churn_and_route("usr_test_01", 15)
        self.assertIn("churn_probability", res)
        self.assertIn("offer_type", res)

    def test_06_ai_sdk_xfin_agent(self):
        agent = XFINArbitrageAgent()
        res = agent.evaluate_currency_arbitrage("usr_test_01", "EUR", 1000.0)
        self.assertEqual(res["currency"], "EUR")

    def test_07_ai_sdk_mint_agent(self):
        agent = MINTBurnAgent()
        res = agent.execute_subscription_burn("usr_test_01", 100.0)
        self.assertIn("burned_tokens", res)

    def test_08_ai_sdk_nexs_agent(self):
        agent = NEXSAgentSynthesizer()
        res = agent.synthesize_offering("usr_test_01", "US", 19.99)
        self.assertEqual(res["agent"], "NEXS_Neural_Synthesizer")

    def test_09_ai_sdk_orchestrator(self):
        res = self.orchestrator.run_agentic_pipeline("usr_test_vip", 100.0, "DE")
        self.assertEqual(res["status"], "ALL_AGENTS_SUCCESSFUL")

if __name__ == "__main__":
    unittest.main()
