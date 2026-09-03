"""
AUTOMATED TEST SUITE FOR UNIVERSAL 200 APPS REAL API CATALOG & MCP BRAIN
================================================================================
Comprehensive test coverage for 200 SaaS Apps catalog, real/fallback REST endpoints,
Universal MCP Brain intent resolution, DAG plan execution, and RAG memory persistence.
"""

import unittest
import sys
import os
import json

# Ensure imports work regardless of execution location
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
nextgen_dir = os.path.join(root_dir, "sovereign_infrastructure", "nextgen_systems")

if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
if nextgen_dir not in sys.path:
    sys.path.insert(0, nextgen_dir)

from sovereign_infrastructure.nextgen_systems.universal_200_apps_real_api_catalog import universal_catalog, Universal200AppsCatalog
from sovereign_infrastructure.nextgen_systems.universal_inner_ai_mcp_brain import universal_mcp_brain, UniversalMCPBrain

class TestUniversal200AppsBrain(unittest.TestCase):

    def test_01_200_apps_catalog_registration(self):
        catalog = universal_catalog.get_catalog()
        self.assertEqual(len(catalog), 200)

    def test_02_category_filtering(self):
        acct_apps = universal_catalog.get_catalog(category="Accounting_Tax")
        self.assertEqual(len(acct_apps), 20)
        self.assertEqual(acct_apps[0]["app_id"], "app_001")

    def test_03_app_detail_lookup(self):
        stripe_spec = universal_catalog.get_app_detail("app_021")
        self.assertIsNotNone(stripe_spec)
        self.assertEqual(stripe_spec["name"], "Stripe Monetization")
        self.assertIn("/charges", stripe_spec["endpoints"])

    def test_04_universal_app_call_execution(self):
        res = universal_catalog.execute_universal_app_call("app_001", "post_journal_entry", "/journalentry", {"amount": 7500.0})
        self.assertIn(res["status_code"], [200, 401])
        self.assertEqual(res["app_name"], "QuickBooks Online")
        self.assertTrue(res["response"]["zero_float_drift"])

    def test_05_mcp_brain_intent_resolution(self):
        intent = universal_mcp_brain.resolve_intent_to_workflow("Score lead in Salesforce and charge credit card in Stripe")
        self.assertIn("Salesforce CRM", intent["target_apps"])
        self.assertEqual(len(intent["dag_plan"]), 4)

    def test_06_mcp_brain_workflow_execution_and_memory(self):
        res = universal_mcp_brain.execute_brain_workflow("Process $10,000 QuickBooks invoice and Stripe charge")
        self.assertEqual(res["status"], "UNIVERSAL_BRAIN_WORKFLOW_COMPLETED")
        self.assertEqual(len(res["execution_steps"]), 4)
        self.assertTrue(res["memory_persisted"].startswith("mem_"))

if __name__ == "__main__":
    unittest.main()
