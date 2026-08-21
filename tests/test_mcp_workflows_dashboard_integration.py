"""
Automated Integration Test Suite for Sovereign OS MCP REST API & 20+ A-to-Z Workflows
Verifies REST endpoints (/api/v1/mcp/tools, /api/v1/mcp/spin_up, /api/v1/workflows/run)
and integration with 6-Core Substrate (XFIN, AURA, PULSE, MINT, GRID, NEXS) & RevenueCat.
Exhaustive Automated Tests: 5 tests per engine / module (20 tests total).
"""

import sys
import os
import unittest
import json
import io

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sovereign_infrastructure", "nextgen_systems")))

from sovereign_dashboard_server import SovereignDashboardHandler
from sovereign_mcp_server import SovereignMCPServer
from nextgen_master_orchestrator import NextGenMasterOrchestrator
from mega_11_platform_master_suite import Mega11PlatformOrchestrator


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
        self.assertEqual(handler.response_code, 200, f"Expected 200 OK for {method} {path}, got {handler.response_code}")
        return json.loads(output_bytes.decode("utf-8")) if output_bytes else {}


class TestMCPToolsEndpoint(BaseDashboardTestCase):
    """Module 1: MCP Tools Endpoint (/api/v1/mcp/tools) - 5 Tests"""

    def test_01_mcp_tools_get_manifest(self):
        res = self.invoke_endpoint("/api/v1/mcp/tools", "GET")
        self.assertEqual(res["status"], "SOVEREIGN_MCP_TOOLS_ONLINE")
        self.assertGreaterEqual(res["total_tools"], 25)
        self.assertIn("tools", res)

    def test_02_mcp_tools_get_substrate_sync(self):
        res = self.invoke_endpoint("/api/v1/mcp/tools", "GET")
        self.assertIn("six_core_substrate_sync", res)
        self.assertEqual(res["six_core_substrate_sync"]["cores_entangled"], 6)

    def test_03_mcp_tools_get_revenuecat_integration(self):
        res = self.invoke_endpoint("/api/v1/mcp/tools", "GET")
        self.assertIn("revenuecat_integration", res)
        self.assertTrue(res["revenuecat_integration"]["entitlements_bridged"])

    def test_04_mcp_tools_post_tool_call_execution(self):
        res = self.invoke_endpoint("/api/v1/mcp/tools", "POST", {
            "tool_name": "workflow_end_to_end_subscriber_lifecycle",
            "arguments": {"user_id": "usr_mcp_test_01", "country_code": "DE"}
        })
        self.assertEqual(res["status"], "NEXTGEN_PIPELINE_SUCCESS")
        self.assertEqual(res["user_id"], "usr_mcp_test_01")

    def test_05_mcp_tools_post_manifest_fallback(self):
        res = self.invoke_endpoint("/api/v1/mcp/tools", "POST", {})
        self.assertEqual(res["status"], "SOVEREIGN_MCP_TOOLS_ONLINE")
        self.assertGreaterEqual(res["total_tools"], 25)


class TestMCPSpinUpEndpoint(BaseDashboardTestCase):
    """Module 2: MCP Sandbox Spin-Up Endpoint (/api/v1/mcp/spin_up) - 5 Tests"""

    def test_01_mcp_spin_up_get_default(self):
        res = self.invoke_endpoint("/api/v1/mcp/spin_up", "GET")
        self.assertEqual(res["status"], "RUNNING")
        self.assertEqual(res["app_name"], "QuickBooks Online")

    def test_02_mcp_spin_up_get_query_params(self):
        res = self.invoke_endpoint("/api/v1/mcp/spin_up?app_id=app_021&app_name=Stripe%20Payments&environment=production", "GET")
        self.assertEqual(res["app_id"], "app_021")
        self.assertEqual(res["app_name"], "Stripe Payments")
        self.assertEqual(res["environment"], "production")

    def test_03_mcp_spin_up_post_custom_sandbox(self):
        res = self.invoke_endpoint("/api/v1/mcp/spin_up", "POST", {
            "app_id": "app_045",
            "app_name": "RevenueCat Subscriptions",
            "tenant_id": "tenant_enterprise_01",
            "environment": "staging",
            "mock_services": ["RevenueCat_StoreKit2_Mock", "PostgreSQL_Ledger_Db"]
        })
        self.assertEqual(res["status"], "RUNNING")
        self.assertEqual(res["app_id"], "app_045")
        self.assertEqual(res["tenant_id"], "tenant_enterprise_01")

    def test_04_mcp_spin_up_substrate_sync(self):
        res = self.invoke_endpoint("/api/v1/mcp/spin_up", "POST", {"app_id": "app_001"})
        self.assertIn("six_core_substrate_sync", res)
        self.assertEqual(res["six_core_substrate_sync"]["cores_entangled"], 6)

    def test_05_mcp_spin_up_revenuecat_integration(self):
        res = self.invoke_endpoint("/api/v1/mcp/spin_up", "POST", {"app_id": "app_001", "entitlement_id": "enterprise_pro"})
        self.assertIn("revenuecat_integration", res)
        self.assertTrue(res["revenuecat_integration"]["entitlements_bridged"])
        self.assertEqual(res["revenuecat_integration"]["entitlement_id"], "enterprise_pro")


class TestWorkflowsRunEndpoint(BaseDashboardTestCase):
    """Module 3: 20+ A-to-Z Workflows REST API Endpoint (/api/v1/workflows/run) - 5 Tests"""

    def test_01_workflows_list_get(self):
        res = self.invoke_endpoint("/api/v1/workflows/list", "GET")
        self.assertEqual(res["status"], "WORKFLOWS_CATALOG_RETRIEVED")
        self.assertGreaterEqual(res["total_workflows"], 25)

    def test_02_workflow_run_get_shorthand_wf_01(self):
        res = self.invoke_endpoint("/api/v1/workflows/run?workflow_id=wf_01&user_id=usr_get_01", "GET")
        self.assertEqual(res["status"], "NEXTGEN_PIPELINE_SUCCESS")
        self.assertIn("six_core_substrate_sync", res)
        self.assertIn("revenuecat_integration", res)

    def test_03_workflow_run_post_named_workflow(self):
        res = self.invoke_endpoint("/api/v1/workflows/run", "POST", {
            "workflow_name": "workflow_cross_border_fx_hedging",
            "fiat_amount": 75000.0,
            "currency": "EUR"
        })
        self.assertIn("settlement", res)
        self.assertIn("hedging", res)
        self.assertEqual(res["settlement"]["status"], "SETTLED")

    def test_04_workflow_run_post_shorthand_wf_02(self):
        res = self.invoke_endpoint("/api/v1/workflows/run", "POST", {
            "workflow_id": "wf_02",
            "contract_id": "CTR-TEST-2026",
            "total_contract_value": 240000.0,
            "contract_term_months": 12
        })
        self.assertIn("schedule", res)
        self.assertEqual(res["contract_id"], "CTR-TEST-2026")

    def test_05_workflow_run_post_shorthand_wf_25_ultimate_suite(self):
        res = self.invoke_endpoint("/api/v1/workflows/run", "POST", {
            "workflow_id": "wf_25",
            "user_id": "usr_grand_prize_winner"
        })
        self.assertEqual(res["status"], "GRAND_PRIZE_25_PROTOCOL_SUITE_SUCCESS")
        self.assertEqual(res["total_protocols_executed"], 25)


class TestSubstrateAndRevenueCatIntegration(BaseDashboardTestCase):
    """Module 4: 6-Core Substrate & RevenueCat Integration Verification - 5 Tests"""

    def test_01_xfin_fx_and_revenuecat_bridge(self):
        orch = NextGenMasterOrchestrator()
        settle = orch.xfin.execute_cross_border_settlement("usr_bridge_01", 100.0, "EUR")
        self.assertEqual(settle["status"], "SETTLED")
        self.assertGreater(settle["settled_usd"], 100.0)

    def test_02_aura_underwriting_and_revenuecat_entitlement(self):
        res = self.invoke_endpoint("/api/v1/workflows/run", "POST", {
            "workflow_name": "workflow_b2b_invoice_underwriting_bnpl",
            "invoice_amount": 50000.0,
            "credit_score": 820
        })
        self.assertEqual(res["status"], "B2B_INVOICE_UNDERWRITTEN")
        self.assertEqual(res["underwriting_status"], "APPROVED")
        self.assertEqual(res["invoice_amount"], 50000.0)

    def test_03_pulse_churn_and_revenuecat_retention(self):
        res = self.invoke_endpoint("/api/v1/workflows/run", "POST", {
            "workflow_name": "workflow_subscriber_churn_retention_campaign",
            "user_id": "usr_retention_99",
            "engagement_score": 0.20
        })
        self.assertIn("churn_risk", res)
        self.assertIn("retention_offer", res)

    def test_04_mint_tokenomics_and_grid_mesh_entitlement(self):
        res = self.invoke_endpoint("/api/v1/workflows/run", "POST", {
            "workflow_name": "workflow_iot_hardware_entitlement_depreciation",
            "device_id": "dev_watch_mesh_01",
            "hardware_cost_usd": 1500.0
        })
        self.assertEqual(res["device_registration"]["status"], "ONLINE")
        self.assertTrue(res["mesh_consensus"]["quorum_reached"])

    def test_05_nexs_paywall_synthesis_and_revenuecat_offering(self):
        res = self.invoke_endpoint("/api/v1/workflows/run", "POST", {
            "workflow_name": "workflow_dynamic_paywall_ppp_pricing",
            "user_id": "usr_nexs_ppp",
            "country_code": "IN",
            "base_usd_price": 49.99
        })
        self.assertEqual(res["region_code"], "IN")
        self.assertLess(res["adapted_usd_price"], 49.99)
        self.assertEqual(res["revenuecat_integration"]["status"], "REVENUECAT_ENTITLED")


if __name__ == "__main__":
    unittest.main()
