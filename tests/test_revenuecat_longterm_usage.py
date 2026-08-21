"""
Comprehensive Automated Test Suite for RevenueCat REST API Endpoints & Long-Term Usage Tracking
Target Endpoints:
  - /api/v1/revenuecat/webhook
  - /api/v1/revenuecat/entitlements
  - /api/v1/revenuecat/paywall
  - /api/v1/revenuecat/usage
"""

import sys
import os
import unittest
import json
import io

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sovereign_infrastructure", "nextgen_systems")))

from sovereign_dashboard_server import SovereignDashboardHandler, mega11
from mega_11_platform_master_suite import RevenueCatMasterModule


class TestRevenueCatLongtermUsage(unittest.TestCase):

    def setUp(self):
        self.rc_module = RevenueCatMasterModule()

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
        self.assertEqual(handler.response_code, 200, f"Endpoint {path} returned HTTP status {handler.response_code}")
        return json.loads(output_bytes.decode("utf-8")) if output_bytes else {}

    # -------------------------------------------------------------------------
    # 1. DIRECT MODULE REVENUECAT MASTER MODULE TESTS
    # -------------------------------------------------------------------------
    def test_01_webhook_lifecycle_processing(self):
        res_init = self.rc_module.process_webhooks("INITIAL_PURCHASE", "sub_test_101", "sovereign_pro_annual")
        self.assertEqual(res_init["status"], "REVENUECAT_WEBHOOK_PROCESSED")
        self.assertEqual(res_init["event_type"], "INITIAL_PURCHASE")
        self.assertEqual(res_init["subscriber_id"], "sub_test_101")
        self.assertIn("evt_", res_init["event_id"])

        res_ent = self.rc_module.get_entitlements("sub_test_101")
        self.assertIn("pro_access", res_ent["entitlements"])
        self.assertEqual(res_ent["entitlements"]["pro_access"]["product_identifier"], "sovereign_pro_annual")

        res_cancel = self.rc_module.process_webhooks("CANCELLATION", "sub_test_101", "sovereign_pro_annual")
        self.assertEqual(res_cancel["event_type"], "CANCELLATION")
        res_ent_after = self.rc_module.get_entitlements("sub_test_101")
        self.assertNotIn("pro_access", res_ent_after["entitlements"])

    def test_02_entitlements_query_and_updates(self):
        res_default = self.rc_module.get_entitlements("sub_default_user")
        self.assertEqual(res_default["status"], "REVENUECAT_ENTITLED")
        self.assertEqual(res_default["subscriber_id"], "sub_default_user")
        self.assertIn("pro_access", res_default["entitlements"])

    def test_03_paywall_configuration_and_experiments(self):
        paywall = self.rc_module.get_paywall(offering_id="enterprise_offer", subscriber_id="sub_101", experiment_id="exp_paywall_v2")
        self.assertEqual(paywall["status"], "REVENUECAT_PAYWALL_ACTIVE")
        self.assertEqual(paywall["offering_id"], "enterprise_offer")
        self.assertGreaterEqual(len(paywall["packages"]), 3)
        self.assertIsNotNone(paywall["experiment"])
        self.assertEqual(paywall["experiment"]["winning_variant"], "variant_b")

    def test_04_longterm_usage_recording_and_aggregation(self):
        rec1 = self.rc_module.record_usage("sub_usage_user", feature_id="api_calls", units=100)
        self.assertEqual(rec1["status"], "REVENUECAT_USAGE_RECORDED")
        rec2 = self.rc_module.record_usage("sub_usage_user", feature_id="compute_credits", units=50)
        self.assertEqual(rec2["status"], "REVENUECAT_USAGE_RECORDED")

        usage = self.rc_module.get_usage("sub_usage_user", period="longterm")
        self.assertEqual(usage["status"], "REVENUECAT_USAGE_RETRIEVED")
        self.assertEqual(usage["period"], "longterm")
        self.assertEqual(usage["total_units_consumed"], 150)
        self.assertIn("feature_breakdown", usage)
        self.assertEqual(usage["feature_breakdown"]["api_calls"], 100)
        self.assertEqual(usage["feature_breakdown"]["compute_credits"], 50)
        self.assertIn("historical_months", usage)

    def test_05_iap_proceeds_calculation(self):
        proceeds_apple_std = self.rc_module.calculate_iap_proceeds(100.0, "apple")
        self.assertEqual(proceeds_apple_std["net_proceeds"], 70.0)
        self.assertEqual(proceeds_apple_std["store_fee_pct"], 30.0)

        proceeds_apple_small_biz = self.rc_module.calculate_iap_proceeds(100.0, "apple_small_biz")
        self.assertEqual(proceeds_apple_small_biz["net_proceeds"], 85.0)
        self.assertEqual(proceeds_apple_small_biz["store_fee_pct"], 15.0)

    # -------------------------------------------------------------------------
    # 2. HTTP REST API ENDPOINT INTEGRATION TESTS
    # -------------------------------------------------------------------------
    def test_06_http_get_revenuecat_webhook(self):
        res = self.invoke_endpoint("/api/v1/revenuecat/webhook?event_type=RENEWAL&subscriber_id=sub_http_01&product_id=sovereign_pro_annual", "GET")
        self.assertEqual(res["status"], "REVENUECAT_WEBHOOK_PROCESSED")
        self.assertEqual(res["event_type"], "RENEWAL")
        self.assertEqual(res["subscriber_id"], "sub_http_01")

    def test_07_http_post_revenuecat_webhook(self):
        body = {
            "event_type": "INITIAL_PURCHASE",
            "subscriber_id": "sub_http_02",
            "product_id": "sovereign_pro_monthly"
        }
        res = self.invoke_endpoint("/api/v1/revenuecat/webhook", "POST", body)
        self.assertEqual(res["status"], "REVENUECAT_WEBHOOK_PROCESSED")
        self.assertEqual(res["event_type"], "INITIAL_PURCHASE")
        self.assertEqual(res["subscriber_id"], "sub_http_02")

    def test_08_http_get_revenuecat_entitlements(self):
        res = self.invoke_endpoint("/api/v1/revenuecat/entitlements?subscriber_id=sub_http_01", "GET")
        self.assertEqual(res["status"], "REVENUECAT_ENTITLED")
        self.assertEqual(res["subscriber_id"], "sub_http_01")
        self.assertIn("pro_access", res["entitlements"])

    def test_09_http_post_revenuecat_entitlements(self):
        body = {"subscriber_id": "sub_http_02"}
        res = self.invoke_endpoint("/api/v1/revenuecat/entitlements", "POST", body)
        self.assertEqual(res["status"], "REVENUECAT_ENTITLED")
        self.assertEqual(res["subscriber_id"], "sub_http_02")
        self.assertIn("pro_access", res["entitlements"])

    def test_10_http_get_revenuecat_paywall(self):
        res = self.invoke_endpoint("/api/v1/revenuecat/paywall?offering_id=enterprise_v1&experiment_id=exp_paywall_v2", "GET")
        self.assertEqual(res["status"], "REVENUECAT_PAYWALL_ACTIVE")
        self.assertEqual(res["offering_id"], "enterprise_v1")
        self.assertIn("packages", res)
        self.assertEqual(res["experiment"]["winning_variant"], "variant_b")

    def test_11_http_post_revenuecat_paywall(self):
        body = {
            "offering_id": "pro_v2",
            "subscriber_id": "sub_http_03",
            "experiment_id": "exp_paywall_v2"
        }
        res = self.invoke_endpoint("/api/v1/revenuecat/paywall", "POST", body)
        self.assertEqual(res["status"], "REVENUECAT_PAYWALL_ACTIVE")
        self.assertEqual(res["offering_id"], "pro_v2")
        self.assertEqual(res["subscriber_id"], "sub_http_03")

    def test_12_http_get_revenuecat_usage(self):
        res = self.invoke_endpoint("/api/v1/revenuecat/usage?subscriber_id=sub_http_01&period=longterm", "GET")
        self.assertEqual(res["status"], "REVENUECAT_USAGE_RETRIEVED")
        self.assertEqual(res["subscriber_id"], "sub_http_01")
        self.assertEqual(res["period"], "longterm")
        self.assertIn("total_api_calls", res)
        self.assertIn("historical_months", res)

    def test_13_http_post_revenuecat_usage_record_and_fetch(self):
        body = {
            "subscriber_id": "sub_http_record_01",
            "feature_id": "api_calls",
            "units": 250,
            "period": "longterm"
        }
        res = self.invoke_endpoint("/api/v1/revenuecat/usage", "POST", body)
        self.assertEqual(res["status"], "REVENUECAT_USAGE_RETRIEVED")
        self.assertEqual(res["subscriber_id"], "sub_http_record_01")
        self.assertEqual(res["total_units_consumed"], 250)
        self.assertEqual(res["feature_breakdown"]["api_calls"], 250)

    def test_14_multi_month_longterm_usage_simulation(self):
        subscriber_id = "sub_corporate_longterm"
        # Simulate 6 months of usage recording
        months = ["2026-03", "2026-04", "2026-05", "2026-06", "2026-07", "2026-08"]
        for month in months:
            self.invoke_endpoint("/api/v1/revenuecat/usage", "POST", {
                "subscriber_id": subscriber_id,
                "feature_id": "api_calls",
                "units": 1200
            })
            self.invoke_endpoint("/api/v1/revenuecat/usage", "POST", {
                "subscriber_id": subscriber_id,
                "feature_id": "compute_credits",
                "units": 50
            })

        final_usage = self.invoke_endpoint(f"/api/v1/revenuecat/usage?subscriber_id={subscriber_id}&period=longterm", "GET")
        self.assertEqual(final_usage["status"], "REVENUECAT_USAGE_RETRIEVED")
        self.assertEqual(final_usage["subscriber_id"], subscriber_id)
        self.assertEqual(final_usage["feature_breakdown"]["api_calls"], 7200)
        self.assertEqual(final_usage["feature_breakdown"]["compute_credits"], 300)
        self.assertEqual(final_usage["total_units_consumed"], 7500)
        self.assertGreater(final_usage["longterm_retention_score"], 0.90)


if __name__ == "__main__":
    unittest.main()
