"""
Automated Test Suite for Port 8090 Target REST Endpoints:
- /api/v1/200apps/*
- /api/v1/brain/*
- /api/v1/revenuecat/*
- /api/v1/gateway/*
"""

import sys
import os
import unittest
import json
import io

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sovereign_dashboard_server import SovereignDashboardHandler


class TestTargetAPIEndpoints(unittest.TestCase):

    def invoke_endpoint(self, path: str, method: str = "GET", body: dict = None) -> tuple:
        body_bytes = json.dumps(body).encode("utf-8") if body is not None else b""
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
        data = json.loads(output_bytes.decode("utf-8")) if output_bytes else {}
        return handler.response_code, data

    # -------------------------------------------------------------------------
    # 1. /api/v1/200apps/* ENDPOINTS (5 Tests)
    # -------------------------------------------------------------------------

    def test_200apps_01_catalog_list_get(self):
        code, res = self.invoke_endpoint("/api/v1/200apps/catalog", "GET")
        self.assertEqual(code, 200)
        self.assertEqual(res["status"], "200_APPS_CATALOG_RETRIEVED")
        self.assertGreaterEqual(res["total"], 200)
        self.assertEqual(len(res["apps"]), res["total"])

    def test_200apps_02_catalog_filtered_category(self):
        code, res = self.invoke_endpoint("/api/v1/200apps/catalog?category=Accounting%20%26%20Tax", "GET")
        self.assertEqual(code, 200)
        self.assertEqual(res["status"], "200_APPS_CATALOG_RETRIEVED")
        self.assertTrue(all(app["category"] == "Accounting & Tax" for app in res["apps"]))

    def test_200apps_03_detail_get_valid(self):
        code, res = self.invoke_endpoint("/api/v1/200apps/detail/app_001", "GET")
        self.assertEqual(code, 200)
        self.assertEqual(res["app_id"], "app_001")
        self.assertEqual(res["name"], "QuickBooks Online")

    def test_200apps_04_call_post(self):
        body = {"app_id": "app_001", "action": "post_journal_entry", "payload": {"debit": 100, "credit": 100}}
        code, res = self.invoke_endpoint("/api/v1/200apps/call", "POST", body)
        self.assertEqual(code, 200)
        self.assertEqual(res["app_id"], "app_001")
        self.assertEqual(res["response"]["status"], "EXECUTED_SUCCESSFULLY")

    def test_200apps_05_execute_post(self):
        body = {"app_id": "app_021", "action": "process_charge", "payload": {"amount": 50.0}}
        code, res = self.invoke_endpoint("/api/v1/200apps/execute", "POST", body)
        self.assertEqual(code, 200)
        self.assertEqual(res["app_id"], "app_021")
        self.assertEqual(res["response"]["status"], "EXECUTED_SUCCESSFULLY")

    # -------------------------------------------------------------------------
    # 2. /api/v1/brain/* ENDPOINTS (5 Tests)
    # -------------------------------------------------------------------------

    def test_brain_01_status_get(self):
        code, res = self.invoke_endpoint("/api/v1/brain/status", "GET")
        self.assertEqual(code, 200)
        self.assertEqual(res["brain_status"], "ONLINE_COHERENT")
        self.assertEqual(res["indexed_apps_count"], 200)

    def test_brain_02_health_get(self):
        code, res = self.invoke_endpoint("/api/v1/brain/health", "GET")
        self.assertEqual(code, 200)
        self.assertEqual(res["brain_status"], "ONLINE_COHERENT")
        self.assertEqual(res["indexed_skills_count"], 500)

    def test_brain_03_workflow_post(self):
        body = {"prompt": "Process QuickBooks invoice and Stripe charge", "params": {"amount": 250.0}}
        code, res = self.invoke_endpoint("/api/v1/brain/workflow", "POST", body)
        self.assertEqual(code, 200)
        self.assertEqual(res["status"], "UNIVERSAL_BRAIN_WORKFLOW_COMPLETED")
        self.assertIn("workflow_id", res)
        self.assertIn("execution_steps", res)

    def test_brain_04_execute_workflow_post(self):
        body = {"user_prompt": "Underwrite credit risk for user usr_101", "parameters": {"user_id": "usr_101"}}
        code, res = self.invoke_endpoint("/api/v1/brain/execute_workflow", "POST", body)
        self.assertEqual(code, 200)
        self.assertEqual(res["status"], "UNIVERSAL_BRAIN_WORKFLOW_COMPLETED")

    def test_brain_05_resolve_intent_post(self):
        body = {"prompt": "Calculate FX triangular arbitrage for EUR/USD/GBP"}
        code, res = self.invoke_endpoint("/api/v1/brain/resolve_intent", "POST", body)
        self.assertEqual(code, 200)
        self.assertEqual(res["brain_status"], "INTENT_RESOLVED")
        self.assertIn("dag_plan", res)

    # -------------------------------------------------------------------------
    # 3. /api/v1/revenuecat/* ENDPOINTS (7 Tests)
    # -------------------------------------------------------------------------

    def test_revenuecat_01_entitlements_get(self):
        code, res = self.invoke_endpoint("/api/v1/revenuecat/entitlements", "GET")
        self.assertEqual(code, 200)
        self.assertEqual(res["status"], "REVENUECAT_ENTITLED")
        self.assertIn("entitlements", res)

    def test_revenuecat_02_check_entitlement_get(self):
        code, res = self.invoke_endpoint("/api/v1/revenuecat/check_entitlement?entitlement_id=sovereign_pro", "GET")
        self.assertEqual(code, 200)
        self.assertEqual(res["status"], "REVENUECAT_ENTITLEMENT_CHECKED")
        self.assertTrue(res["is_active"])

    def test_revenuecat_03_paywall_get(self):
        code, res = self.invoke_endpoint("/api/v1/revenuecat/paywall", "GET")
        self.assertEqual(code, 200)
        self.assertEqual(res["status"], "REVENUECAT_PAYWALL_ACTIVE")

    def test_revenuecat_04_paywall_rules_get(self):
        code, res = self.invoke_endpoint("/api/v1/revenuecat/paywall_rules", "GET")
        self.assertEqual(code, 200)
        self.assertEqual(res["status"], "STOREKIT2_PAYWALL_RULES_RETRIEVED")
        self.assertTrue(res["storekit2_enabled"])

    def test_revenuecat_05_churn_telemetry_get(self):
        code, res = self.invoke_endpoint("/api/v1/revenuecat/churn_telemetry", "GET")
        self.assertEqual(code, 200)
        self.assertEqual(res["status"], "SUBSCRIBER_CHURN_TELEMETRY_RETRIEVED")

    def test_revenuecat_06_usage_and_experiment_get(self):
        code1, res1 = self.invoke_endpoint("/api/v1/revenuecat/usage", "GET")
        self.assertEqual(code1, 200)
        self.assertEqual(res1["status"], "REVENUECAT_USAGE_RETRIEVED")

        code2, res2 = self.invoke_endpoint("/api/v1/revenuecat/experiment", "GET")
        self.assertEqual(code2, 200)
        self.assertEqual(res2["status"], "REVENUECAT_EXPERIMENT_ACTIVE")

    def test_revenuecat_07_webhook_post(self):
        body = {"event_type": "INITIAL_PURCHASE", "subscriber_id": "sub_test_01", "product_id": "sovereign_pro_annual"}
        code, res = self.invoke_endpoint("/api/v1/revenuecat/webhook", "POST", body)
        self.assertEqual(code, 200)
        self.assertEqual(res["status"], "REVENUECAT_WEBHOOK_PROCESSED")

    # -------------------------------------------------------------------------
    # 4. /api/v1/gateway/* ENDPOINTS (7 Tests)
    # -------------------------------------------------------------------------

    def test_gateway_01_status_get(self):
        code, res = self.invoke_endpoint("/api/v1/gateway/status", "GET")
        self.assertEqual(code, 200)
        self.assertEqual(res["status"], "OPERATIONAL")
        self.assertIn("live_integrations", res)

    def test_gateway_02_stripe_charge_post(self):
        body = {"amount_cents": 2500, "currency": "usd", "description": "Sovereign Pro License"}
        code, res = self.invoke_endpoint("/api/v1/gateway/stripe/charge", "POST", body)
        self.assertEqual(code, 200)
        self.assertEqual(res["status"], "succeeded")
        self.assertEqual(res["amount"], 2500)

    def test_gateway_03_revenuecat_subscriber_get(self):
        code, res = self.invoke_endpoint("/api/v1/gateway/revenuecat/subscriber?subscriber_id=sub_101", "GET")
        self.assertEqual(code, 200)
        self.assertEqual(res["subscriber"]["original_app_user_id"], "sub_101")
        self.assertIn("entitlements", res["subscriber"])

    def test_gateway_04_quickbooks_journal_post(self):
        body = {"journal_entry": {"debits": [{"account": "1010 Cash", "amount": 100.0}], "credits": [{"account": "4010 Revenue", "amount": 100.0}]}}
        code, res = self.invoke_endpoint("/api/v1/gateway/quickbooks/journal", "POST", body)
        self.assertEqual(code, 200)
        self.assertEqual(res["status"], "SUCCESS")

    def test_gateway_05_salesforce_lead_post(self):
        body = {"lead": {"company": "Acme Global", "first_name": "Jane", "last_name": "Smith", "email": "jane@acme.com"}}
        code, res = self.invoke_endpoint("/api/v1/gateway/salesforce/lead", "POST", body)
        self.assertEqual(code, 200)
        self.assertTrue(res["success"])

    def test_gateway_06_square_payment_post(self):
        body = {"amount_cents": 5000, "card_nonce": "cnon:card-nonce-ok", "currency": "USD"}
        code, res = self.invoke_endpoint("/api/v1/gateway/square/payment", "POST", body)
        self.assertEqual(code, 200)
        self.assertEqual(res["payment"]["status"], "COMPLETED")

    def test_gateway_07_sendgrid_send_post(self):
        body = {"to_email": "client@enterprise.com", "subject": "Invoice Paid", "html_content": "<p>Thank you!</p>"}
        code, res = self.invoke_endpoint("/api/v1/gateway/sendgrid/send", "POST", body)
        self.assertEqual(code, 200)
        self.assertEqual(res["status"], "DELIVERED")


if __name__ == "__main__":
    unittest.main()
