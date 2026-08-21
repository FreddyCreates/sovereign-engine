"""
Automated Test Suite for Sovereign OS MCP Server & 20+ A-to-Z Workflows
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sovereign_infrastructure", "nextgen_systems")))

from sovereign_mcp_server import SovereignMCPServer, SovereignAppSandboxEngine, SovereignDataIngestionEngine, SovereignAtoZWorkflowOrchestrator

class TestSovereignMCPServer(unittest.TestCase):

    def setUp(self):
        self.mcp = SovereignMCPServer()

    def test_01_mcp_manifest(self):
        manifest = self.mcp.get_mcp_manifest()
        self.assertEqual(manifest["platform_identity"]["platform_name"], "SOVEREIGN OS")
        self.assertGreaterEqual(len(manifest["tools"]), 5)

    def test_02_sandbox_spin_up(self):
        res = self.mcp.handle_mcp_tool_call("mcp_spin_up_app_sandbox", {"app_id": "app_001", "app_name": "QuickBooks Online"})
        self.assertEqual(res["status"], "RUNNING_ACTIVE")
        self.assertEqual(res["platform"], "SOVEREIGN OS")

    def test_03_data_ingestion(self):
        res = self.mcp.handle_mcp_tool_call("mcp_ingest_app_data", {"app_id": "app_021", "app_name": "Stripe Payments"})
        self.assertEqual(res["status"], "DATA_INGESTION_COMPLETED")
        self.assertEqual(res["general_ledger_posted"], True)

    def test_04_atoz_workflows_catalog(self):
        orch = SovereignAtoZWorkflowOrchestrator()
        self.assertGreaterEqual(len(orch.workflows_catalog), 20)

    def test_05_execute_atoz_workflow(self):
        res = self.mcp.handle_mcp_tool_call("mcp_execute_atoz_workflow", {"workflow_id": "wf_01"})
        self.assertEqual(res["status"], "WORKFLOW_EXECUTED_SUCCESSFULLY")
        self.assertEqual(res["steps_completed"], 6)

    def test_06_query_sovereign_os(self):
        res = self.mcp.handle_mcp_tool_call("mcp_query_sovereign_os", {})
        self.assertEqual(res["status"], "SOVEREIGN_OS_STATE_OPTIMAL")

if __name__ == "__main__":
    unittest.main()
