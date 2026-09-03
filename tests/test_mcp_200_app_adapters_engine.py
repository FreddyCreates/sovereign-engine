"""
Exhaustive Automated Test Suite for Sovereign OS MCP 200 App Adapters & Container Queries Engine.

5 Core Comprehensive Test Scenarios:
1. Adapter Registration & Domain Distribution Verification (200 Apps, 10 Domains, 1,200 Actions)
2. Instant Batch Execution of 1,000 Container Queries with Full Response Payloads
3. Zero Float Drift Mathematical Verification (Decimal precision vs IEEE-754 float drift)
4. Model Context Protocol (MCP) JSON-RPC Tool Schema Generation & Action Search
5. RevenueCat Multi-Store Entitlement Enforcement, Underwriting Risk Scoring & Audit Trail
"""

import sys
import os
import unittest
from decimal import Decimal

# Ensure project root and nextgen_systems are in sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
NEXTGEN_DIR = os.path.join(BASE_DIR, "sovereign_infrastructure", "nextgen_systems")

if NEXTGEN_DIR not in sys.path:
    sys.path.insert(0, NEXTGEN_DIR)
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from sovereign_infrastructure.nextgen_systems.mcp_200_app_adapters_engine import (
    MCP200AppAdaptersEngine,
    MCP200AppAdapterEngine,
    AppAdapter,
    MCPAction,
    MCPExecutionResult,
    FlexResult
)


class TestMCP200AppAdaptersEngine(unittest.TestCase):

    def setUp(self):
        self.engine = MCP200AppAdaptersEngine()

    def test_01_adapter_registration_and_domain_distribution(self):
        """Test 1: Verifies exact registration of 200 apps, 10 categories, 1,200 tool actions, and custom adapter registration."""
        counts = self.engine.get_total_counts()
        self.assertEqual(counts["total_apps"], 200, "Must register exactly 200 app adapters")
        self.assertEqual(counts["total_domains"], 10, "Must contain exactly 10 business domains")
        self.assertEqual(counts["total_actions"], 1200, "Must contain exactly 1,200 actions (6 per app)")

        # Verify domain distribution (20 apps per category)
        for domain, apps in self.engine.domain_map.items():
            self.assertEqual(len(apps), 20, f"Category '{domain}' must contain exactly 20 apps")

        # Test custom adapter dynamic registration
        custom_app = self.engine.register_adapter("app_custom_ai", "Custom Deep Learning Engine", "Analytics & AI")
        self.assertEqual(custom_app["app_id"], "app_custom_ai")
        self.assertEqual(len(self.engine.adapters_registry), 201)

    def test_02_instant_batch_execution_1000_container_queries_with_full_payloads(self):
        """Test 2: Verifies instant batch execution of 1,000 container queries across all 200 adapters with full payloads."""
        batch_report = self.engine.execute_1000_queries(queries=1000, batch_size=100)
        
        self.assertEqual(batch_report["total_queries_executed"], 1000)
        self.assertEqual(batch_report["successful_queries"], 1000)
        self.assertEqual(batch_report["failed_queries"], 0)
        self.assertEqual(batch_report["adapters_queried_count"], 200)
        self.assertEqual(batch_report["full_response_payloads_count"], 1000)
        self.assertGreater(batch_report["throughput_qps"], 1000.0)
        self.assertIn("cryptographic_audit_hash", batch_report)

        # Inspect sample full response payload
        sample_payload = batch_report["sample_response_payload"]
        self.assertIn("query_id", sample_payload)
        self.assertIn("container_id", sample_payload)
        self.assertIn("app_id", sample_payload)
        self.assertIn("category", sample_payload)
        self.assertIn("financial_payload", sample_payload)
        self.assertIn("sha256_signature", sample_payload)
        self.assertEqual(sample_payload["status"], "CONTAINER_QUERY_SUCCESS")

    def test_03_zero_float_drift_mathematical_verification(self):
        """Test 3: Verifies exact Decimal fixed-point calculations across 1,000 container queries (0 float drift)."""
        batch_report = self.engine.execute_1000_queries(queries=1000, batch_size=100)
        fin_summary = batch_report["financial_summary"]

        self.assertTrue(fin_summary["zero_float_drift_verified"])
        self.assertIn("cumulative_total_usd", fin_summary)
        
        # Verify single container query zero float drift math directly
        query_payload = self.engine.execute_container_query(
            app_id="app_001",
            action_name="FINANCIAL_AUDIT",
            params={"base_amount": "100.00", "index": 5},
            container_id="cntr_math_check"
        )
        fin = query_payload["financial_payload"]
        
        # Subtotal = 100.00 + 5 * 0.10 = 100.50
        # Tax = 100.50 * 0.08875 = 8.919375 -> rounded to 8.92
        # Total = 100.50 + 8.92 = 109.42
        self.assertEqual(fin["subtotal"], "100.50")
        self.assertEqual(fin["tax"], "8.92")
        self.assertEqual(fin["total_amount"], "109.42")
        self.assertEqual(fin["subtotal_decimal"] + fin["tax_decimal"], fin["total_decimal"])
        self.assertTrue(fin["zero_float_drift"])

    def test_04_mcp_schema_definitions_and_search(self):
        """Test 4: Verifies export of MCP tool definitions and search capability across app actions."""
        # Export Cloud domain tools (20 apps * 6 actions = 120 tools)
        cloud_tools = self.engine.generate_mcp_tool_definitions(domain="Cloud")
        self.assertEqual(len(cloud_tools), 120)
        
        sample_tool = cloud_tools[0]
        self.assertIn("name", sample_tool)
        self.assertIn("inputSchema", sample_tool)
        self.assertIn("metadata", sample_tool)

        # Search capability
        searchResults = self.engine.search_actions("orders", domain="E-Commerce")
        self.assertGreater(len(searchResults), 0)
        for r in searchResults:
            self.assertEqual(r["domain"], "E-Commerce")

    def test_05_revenuecat_entitlement_and_security_audit(self):
        """Test 5: Verifies RevenueCat billing tier enforcement, underwriting risk scoring, and SHA-256 audit log."""
        first_app = list(self.engine.adapters.keys())[0]
        restricted_app = list(self.engine.adapters.keys())[160]

        # Free tier entitlement checks
        self.assertTrue(self.engine.revenuecat_entitlement_check(first_app, "free"))
        self.assertFalse(self.engine.revenuecat_entitlement_check(restricted_app, "free"))

        # Enterprise tier entitlement allows restricted app
        self.assertTrue(self.engine.revenuecat_entitlement_check(restricted_app, "enterprise"))

        with self.assertRaises(PermissionError):
            self.engine.execute_action(restricted_app, "read_data", entitlement_tier="free")

        # Risk scoring verification: Read action vs Write action
        read_res = self.engine.execute_action("app_001", "read_invoices", entitlement_tier="free")
        self.assertLess(read_res.risk_score, 0.4)

        write_res = self.engine.execute_action("app_001", "create_payment", entitlement_tier="free")
        self.assertGreaterEqual(write_res.risk_score, 0.4)

        # Full system audit
        audit_res = self.engine.run_adapters_audit()
        self.assertEqual(audit_res["total_registered_adapters"], 200)
        self.assertEqual(audit_res["overall_status"], "MCP_200_ADAPTERS_FULLY_OPERATIONAL")


if __name__ == "__main__":
    unittest.main()
