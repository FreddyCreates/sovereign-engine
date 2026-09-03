"""
Exhaustive Automated Test Suite for Sovereign Dashboard Unified Live Payloads
Verifies simultaneous real-time updates across Accounting Ledger, CRM, and Dynamic Paywalls for:
- /api/v1/overview
- /api/v1/revenuecat/*
- /api/v1/200apps/*
- /api/v1/brain/*
"""

import sys
import os
import unittest
import json
import io

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sovereign_dashboard_server import SovereignDashboardHandler, synchronize_unified_substrate


class TestUnifiedLivePayloads(unittest.TestCase):

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

    def test_01_overview_unified_live_payload(self):
        """Verify /api/v1/overview returns unified live payload updating ledger, CRM, & paywalls simultaneously."""
        for method in ["GET", "POST"]:
            res = self.invoke_endpoint("/api/v1/overview", method=method, body={"subscriber_id": "sub_overview_test"})
            self.assertIn("mrr", res)
            self.assertEqual(res["mrr"], 148920.0)
            self.assertEqual(res["sync_status"], "SYNCHRONIZED_SIMULTANEOUSLY")
            self.assertIn("unified_live_payload", res)
            payload = res["unified_live_payload"]
            
            # 1. Accounting Ledger
            self.assertIn("accounting_ledger", payload)
            ledger = payload["accounting_ledger"]
            self.assertEqual(ledger["status"], "LEDGER_UPDATED_LIVE")
            self.assertTrue(ledger["zero_precision_drift_valid"])
            self.assertEqual(ledger["precision_guard"], "DECIMAL_EXACT_ZERO_DRIFT")
            
            # 2. CRM
            self.assertIn("crm", payload)
            crm = payload["crm"]
            self.assertEqual(crm["status"], "CRM_UPDATED_LIVE")
            self.assertEqual(crm["crm_provider"], "Salesforce_Gemini_Enterprise")
            
            # 3. Paywalls
            self.assertIn("paywalls", payload)
            paywalls = payload["paywalls"]
            self.assertEqual(paywalls["status"], "PAYWALL_UPDATED_LIVE")
            self.assertEqual(paywalls["paywall_provider"], "RevenueCat_NEXS_Substrate")

    def test_02_revenuecat_family_unified_live_payloads(self):
        """Verify all /api/v1/revenuecat/* endpoints return unified live payloads with simultaneous updates."""
        rc_routes = [
            ("/api/v1/revenuecat/entitlements", "GET", None),
            ("/api/v1/revenuecat/entitlements", "POST", {"subscriber_id": "sub_rc_01"}),
            ("/api/v1/revenuecat/paywall", "GET", None),
            ("/api/v1/revenuecat/paywall", "POST", {"subscriber_id": "sub_rc_02", "offering_id": "pro"}),
            ("/api/v1/revenuecat/webhook", "POST", {"event_type": "INITIAL_PURCHASE", "subscriber_id": "sub_rc_03"}),
            ("/api/v1/revenuecat/churn_telemetry", "GET", None),
            ("/api/v1/revenuecat/usage", "GET", None),
            ("/api/v1/revenuecat/experiment", "POST", {"experiment_id": "exp_v3"}),
            ("/api/v1/revenuecat/custom_wildcard", "GET", None)
        ]

        for path, method, body in rc_routes:
            res = self.invoke_endpoint(path, method=method, body=body)
            self.assertEqual(res.get("sync_status"), "SYNCHRONIZED_SIMULTANEOUSLY", f"Failed sync_status check on {path}")
            self.assertIn("unified_live_payload", res, f"Missing unified_live_payload on {path}")
            payload = res["unified_live_payload"]
            self.assertIn("accounting_ledger", payload)
            self.assertIn("crm", payload)
            self.assertIn("paywalls", payload)

    def test_03_200apps_family_unified_live_payloads(self):
        """Verify all /api/v1/200apps/* endpoints return unified live payloads with simultaneous updates."""
        apps_routes = [
            ("/api/v1/200apps/catalog", "GET", None),
            ("/api/v1/200apps/list", "POST", {"category": "Analytics"}),
            ("/api/v1/200apps/detail/app_001", "GET", None),
            ("/api/v1/200apps/call", "POST", {"app_id": "app_001", "action": "ping"}),
            ("/api/v1/200apps/custom_app_endpoint", "GET", None)
        ]

        for path, method, body in apps_routes:
            res = self.invoke_endpoint(path, method=method, body=body)
            self.assertEqual(res.get("sync_status"), "SYNCHRONIZED_SIMULTANEOUSLY", f"Failed sync_status check on {path}")
            self.assertIn("unified_live_payload", res, f"Missing unified_live_payload on {path}")
            payload = res["unified_live_payload"]
            self.assertEqual(payload["accounting_ledger"]["status"], "LEDGER_UPDATED_LIVE")
            self.assertEqual(payload["crm"]["status"], "CRM_UPDATED_LIVE")
            self.assertEqual(payload["paywalls"]["status"], "PAYWALL_UPDATED_LIVE")

    def test_04_brain_family_unified_live_payloads(self):
        """Verify all /api/v1/brain/* endpoints return unified live payloads with simultaneous updates."""
        brain_routes = [
            ("/api/v1/brain/status", "GET", None),
            ("/api/v1/brain/health", "GET", None),
            ("/api/v1/brain/workflows", "POST", {"filter": "active"}),
            ("/api/v1/brain/workflow", "POST", {"prompt": "Run accounting reconciliation"}),
            ("/api/v1/brain/resolve_intent", "POST", {"prompt": "Create QuickBooks invoice"}),
            ("/api/v1/brain/custom_workflow", "GET", None)
        ]

        for path, method, body in brain_routes:
            res = self.invoke_endpoint(path, method=method, body=body)
            self.assertEqual(res.get("sync_status"), "SYNCHRONIZED_SIMULTANEOUSLY", f"Failed sync_status check on {path}")
            self.assertIn("unified_live_payload", res, f"Missing unified_live_payload on {path}")
            payload = res["unified_live_payload"]
            self.assertIn("accounting_ledger", payload)
            self.assertIn("crm", payload)
            self.assertIn("paywalls", payload)

    def test_05_simultaneous_substrate_synchronization_integrity(self):
        """Directly verify synchronize_unified_substrate updates accounting ledger, CRM, and paywalls simultaneously."""
        sync_result = synchronize_unified_substrate(
            subscriber_id="sub_vip_test_99",
            amount=5000.00,
            context={"company": "Apex Dynamics", "country_code": "DE"}
        )

        self.assertEqual(sync_result["sync_status"], "SYNCHRONIZED_SIMULTANEOUSLY")
        
        # Check Accounting Ledger Substrate
        ledger = sync_result["accounting_ledger"]
        self.assertEqual(ledger["status"], "LEDGER_UPDATED_LIVE")
        self.assertTrue(ledger["zero_precision_drift_valid"])
        self.assertGreater(ledger["gross_revenue"], 0)

        # Check Salesforce CRM Substrate
        crm = sync_result["crm"]
        self.assertEqual(crm["status"], "CRM_UPDATED_LIVE")
        self.assertEqual(crm["subscriber_id"], "sub_vip_test_99")
        self.assertGreater(crm["lead_score"], 0)

        # Check Dynamic Paywalls Substrate
        paywalls = sync_result["paywalls"]
        self.assertEqual(paywalls["status"], "PAYWALL_UPDATED_LIVE")
        self.assertEqual(paywalls["subscriber_id"], "sub_vip_test_99")
        self.assertTrue(paywalls["storekit2_rules_active"])


if __name__ == "__main__":
    unittest.main()
