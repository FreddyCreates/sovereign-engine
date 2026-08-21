"""
Automated Test Suite for SOVEREIGN OS Alpha Unlimited Work Engine & REST API Endpoints
Exposes and tests /api/v1/alpha/work/generate and /api/v1/alpha/work/dispatch_200 in SovereignDashboardServer
"""

import sys
import os
import unittest
import json
import io

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sovereign_infrastructure", "nextgen_systems")))

from alpha_unlimited_work_engine import AlphaUnlimitedWorkEngine, AlphaAppWorkGenerator
from sovereign_dashboard_server import SovereignDashboardHandler


class TestAlphaUnlimitedWorkEngine(unittest.TestCase):

    def setUp(self):
        self.engine = AlphaUnlimitedWorkEngine()

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
        self.assertEqual(handler.response_code, 200)
        return json.loads(output_bytes.decode("utf-8")) if output_bytes else {}

    def test_01_alpha_engine_audit(self):
        audit = self.engine.run_alpha_audit()
        self.assertEqual(audit["capacity"], "UNLIMITED_PARALLEL_EXECUTION")
        self.assertGreaterEqual(audit["total_supported_apps"], 200)
        self.assertEqual(audit["status"], "ALPHA_ENGINE_ONLINE_OPTIMAL")

    def test_02_generate_work_single_app(self):
        task = self.engine.generate_work("app_001")
        self.assertEqual(task["app_name"], "QuickBooks Online")
        self.assertEqual(task["status"], "COMPLETED_SUCCESSFULLY")

    def test_03_generate_work_all_200_apps(self):
        res = self.engine.dispatch_200()
        self.assertEqual(res["total_apps_processed"], 200)
        self.assertEqual(res["total_tasks_completed"], 200)
        self.assertIn("AUTONOMIC_WORK_COMPLETED", res["status"])

    def test_04_rest_api_generate_work_get(self):
        res = self.invoke_endpoint("/api/v1/alpha/work/generate?app_id=app_001", "GET")
        self.assertEqual(res["app_id"], "app_001")
        self.assertEqual(res["app_name"], "QuickBooks Online")
        self.assertEqual(res["status"], "COMPLETED_SUCCESSFULLY")

    def test_05_rest_api_generate_work_post(self):
        res = self.invoke_endpoint("/api/v1/alpha/work/generate", "POST", {"app_id": "app_002"})
        self.assertEqual(res["app_id"], "app_002")
        self.assertEqual(res["status"], "COMPLETED_SUCCESSFULLY")

    def test_06_rest_api_dispatch_200_get(self):
        res = self.invoke_endpoint("/api/v1/alpha/work/dispatch_200", "GET")
        self.assertEqual(res["total_apps_processed"], 200)
        self.assertEqual(res["total_tasks_completed"], 200)

    def test_07_rest_api_dispatch_200_post(self):
        res = self.invoke_endpoint("/api/v1/alpha/work/dispatch_200", "POST")
        self.assertEqual(res["total_apps_processed"], 200)
        self.assertEqual(res["total_tasks_completed"], 200)

    def test_08_rest_api_alpha_work_audit(self):
        res = self.invoke_endpoint("/api/v1/alpha/work/audit", "GET")
        self.assertEqual(res["capacity"], "UNLIMITED_PARALLEL_EXECUTION")
        self.assertEqual(res["status"], "ALPHA_ENGINE_ONLINE_OPTIMAL")


if __name__ == "__main__":
    unittest.main()
