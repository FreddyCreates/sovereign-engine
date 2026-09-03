"""
Automated Test Suite for AI/DevTools DX Review Upgrades on Sovereign Dashboard Server:
1. OpenAPI 3.0 specification endpoint (/api/v1/openapi.json)
2. Standardized error responses (400, 404, 422, 500)
3. Request content type & schema field validations
"""

import sys
import os
import unittest
import json
import io

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sovereign_dashboard_server import SovereignDashboardHandler


class TestDXImprovements(unittest.TestCase):

    def invoke_handler(self, path: str, method: str = "GET", body_bytes: bytes = b"", headers: dict = None) -> tuple:
        rfile = io.BytesIO(body_bytes)
        wfile = io.BytesIO()

        handler = SovereignDashboardHandler.__new__(SovereignDashboardHandler)
        handler.path = path
        handler.rfile = rfile
        handler.wfile = wfile
        
        req_headers = {"Content-Length": str(len(body_bytes))}
        if headers:
            req_headers.update(headers)
        handler.headers = req_headers

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
        body_json = json.loads(output_bytes.decode("utf-8")) if output_bytes else {}
        return handler.response_code, body_json

    def test_01_openapi_json_endpoint(self):
        code, body = self.invoke_handler("/api/v1/openapi.json", "GET")
        self.assertEqual(code, 200)
        self.assertEqual(body["openapi"], "3.0.3")
        self.assertEqual(body["info"]["title"], "Sovereign Engine Enterprise Platform API")
        self.assertIn("paths", body)
        self.assertIn("/api/v1/overview", body["paths"])
        self.assertIn("/api/v1/stripe/payment", body["paths"])
        self.assertIn("/api/v1/openapi.json", body["paths"])
        self.assertIn("ErrorResponse", body["components"]["schemas"])

    def test_02_404_not_found_standardized_error(self):
        code, body = self.invoke_handler("/api/v1/unknown_endpoint_xyz", "GET")
        self.assertEqual(code, 404)
        self.assertEqual(body["error_code"], "NOT_FOUND")
        self.assertTrue(body["request_id"].startswith("req_"))
        self.assertIn("docs_url", body)
        self.assertIn("API endpoint '/api/v1/unknown_endpoint_xyz' not found", body["message"])

    def test_03_400_invalid_content_type(self):
        code, body = self.invoke_handler(
            "/api/v1/stripe/payment",
            method="POST",
            body_bytes=b'{"amount": 100.0}',
            headers={"Content-Type": "text/plain"}
        )
        self.assertEqual(code, 400)
        self.assertEqual(body["error_code"], "INVALID_CONTENT_TYPE")
        self.assertTrue(body["request_id"].startswith("req_"))
        self.assertIn("docs_url", body)

    def test_04_400_malformed_json_payload(self):
        code, body = self.invoke_handler(
            "/api/v1/stripe/payment",
            method="POST",
            body_bytes=b'{"amount": 100.0, invalid}',
            headers={"Content-Type": "application/json"}
        )
        self.assertEqual(code, 400)
        self.assertEqual(body["error_code"], "MALFORMED_JSON")
        self.assertTrue(body["request_id"].startswith("req_"))
        self.assertIn("docs_url", body)

    def test_05_422_schema_validation_negative_value(self):
        code, body = self.invoke_handler(
            "/api/v1/stripe/payment",
            method="POST",
            body_bytes=json.dumps({"amount": -150.0, "currency": "USD"}).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        self.assertEqual(code, 422)
        self.assertEqual(body["error_code"], "INVALID_FIELD_VALUE")
        self.assertTrue(body["request_id"].startswith("req_"))
        self.assertIn("docs_url", body)
        self.assertIn("Field 'amount' must be a positive number", body["message"])

    def test_06_422_schema_validation_invalid_type(self):
        code, body = self.invoke_handler(
            "/api/v1/stripe/payment",
            method="POST",
            body_bytes=json.dumps({"amount": "one_hundred"}).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        self.assertEqual(code, 422)
        self.assertEqual(body["error_code"], "INVALID_FIELD_TYPE")
        self.assertTrue(body["request_id"].startswith("req_"))
        self.assertIn("docs_url", body)

    def test_07_500_internal_server_error_format(self):
        # Trigger hand-crafted server exception to test 500 error structure
        handler = SovereignDashboardHandler.__new__(SovereignDashboardHandler)
        handler.path = "/api/v1/test_500"
        handler.response_code = None
        handler.response_headers = {}

        def mock_send_response(code, message=None):
            handler.response_code = code

        def mock_send_header(keyword, value):
            handler.response_headers[keyword] = value

        def mock_end_headers():
            pass

        wfile = io.BytesIO()
        handler.wfile = wfile
        handler.send_response = mock_send_response
        handler.send_header = mock_send_header
        handler.end_headers = mock_end_headers

        handler.send_json_error(500, "INTERNAL_SERVER_ERROR", "Internal test exception")
        output_bytes = wfile.getvalue()
        body = json.loads(output_bytes.decode("utf-8"))

        self.assertEqual(handler.response_code, 500)
        self.assertEqual(body["error_code"], "INTERNAL_SERVER_ERROR")
        self.assertEqual(body["message"], "Internal test exception")
        self.assertTrue(body["request_id"].startswith("req_"))
        self.assertEqual(body["docs_url"], "https://docs.sovereign.engine/errors/INTERNAL_SERVER_ERROR")


if __name__ == "__main__":
    unittest.main()
