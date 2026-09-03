"""
Exhaustive Automated Test Suite for FinTech REST API Audit:
Verifies Idempotency-Key handling, rate limiting (X-RateLimit-*), RFC 3339 UTC timestamps,
and Gzip HTTP compression on all financial mutation endpoints (/api/v1/gemini_enterprise/*, /api/v1/native/*).
"""

import unittest
import json
import re
import gzip
import sys
import os
from io import BytesIO

# Ensure imports work regardless of execution location
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from sovereign_dashboard_server import (
    SovereignDashboardHandler,
    validate_double_entry_zero_drift,
    get_rfc3339_utc_timestamp,
    rate_limiter,
    IDEMPOTENCY_STORE
)

class BaseFintechAuditTestCase(unittest.TestCase):
    def invoke_endpoint(self, path: str, method: str = "GET", body: dict = None, extra_headers: dict = None):
        handler = SovereignDashboardHandler.__new__(SovereignDashboardHandler)
        handler.path = path
        handler.command = method.upper()
        handler.client_address = ("127.0.0.1", 54321)
        handler.rfile = BytesIO()
        handler.wfile = BytesIO()
        handler._cors_sent = False

        headers_dict = {"Host": "localhost:8090"}
        if body is not None:
            body_bytes = json.dumps(body).encode("utf-8")
            headers_dict["Content-Length"] = str(len(body_bytes))
            headers_dict["Content-Type"] = "application/json"
            handler.rfile = BytesIO(body_bytes)
        else:
            headers_dict["Content-Length"] = "0"

        if extra_headers:
            headers_dict.update(extra_headers)

        class MockMessage:
            def __init__(self, hdrs):
                self._hdrs = {k.lower(): str(v) for k, v in hdrs.items()}
            def get(self, key, default=None):
                return self._hdrs.get(key.lower(), default)

        handler.headers = MockMessage(headers_dict)
        handler.response_headers = {}
        handler.response_code = 200

        def mock_send_response(code, message=None):
            handler.response_code = code

        def mock_send_header(keyword, value):
            handler.response_headers[keyword] = str(value)

        handler.send_response = mock_send_response
        handler.send_header = mock_send_header
        handler.end_headers = lambda: None

        if method.upper() == "GET":
            handler.do_GET()
        else:
            handler.do_POST()

        output_bytes = handler.wfile.getvalue()
        content_encoding = handler.response_headers.get("Content-Encoding", "")
        
        if content_encoding == "gzip":
            decompressed = gzip.decompress(output_bytes)
            res_data = json.loads(decompressed.decode("utf-8")) if decompressed else {}
        else:
            res_data = json.loads(output_bytes.decode("utf-8")) if output_bytes else {}

        return res_data, handler.response_code, handler.response_headers, output_bytes


class TestFintechAPIAudit(BaseFintechAuditTestCase):

    def test_01_idempotency_gemini_enterprise_endpoints(self):
        """1. Verify Idempotency-Key handling & replay caching on /api/v1/gemini_enterprise/* endpoints."""
        idem_key = "idem_gemini_qb_5544"
        payload = {"action": "sox_tax", "amount": 15000.0, "jurisdiction": "US_CA"}
        headers = {"Idempotency-Key": idem_key}

        # Initial POST request
        res1, status1, resp_headers1, _ = self.invoke_endpoint(
            "/api/v1/gemini_enterprise/quickbooks", "POST", payload, headers
        )
        self.assertEqual(status1, 200)
        self.assertEqual(res1.get("idempotency_key"), idem_key)
        self.assertEqual(res1.get("idempotency_handled"), True)
        self.assertEqual(resp_headers1.get("Idempotent-Replay"), "false")

        # Replay POST request with duplicate Idempotency-Key
        res2, status2, resp_headers2, _ = self.invoke_endpoint(
            "/api/v1/gemini_enterprise/quickbooks", "POST", payload, headers
        )
        self.assertEqual(status2, 200)
        self.assertEqual(res2.get("idempotency_key"), idem_key)
        self.assertEqual(resp_headers2.get("Idempotent-Replay"), "true")
        self.assertEqual(res2.get("total_liability_usd"), res1.get("total_liability_usd"))

    def test_02_idempotency_native_endpoints(self):
        """2. Verify Idempotency-Key handling & replay caching on /api/v1/native/* endpoints."""
        idem_key = "idem_native_sign_9911"
        payload = {"document_name": "Sovereign SLA", "signer_email": "cto@enterprise.com", "contract_value": 7500.0}
        headers = {"Idempotency-Key": idem_key}

        res1, status1, resp_headers1, _ = self.invoke_endpoint(
            "/api/v1/native/sign", "POST", payload, headers
        )
        self.assertEqual(status1, 200)
        self.assertEqual(res1.get("idempotency_key"), idem_key)
        self.assertEqual(res1.get("idempotency_handled"), True)
        self.assertEqual(resp_headers1.get("Idempotent-Replay"), "false")

        res2, status2, resp_headers2, _ = self.invoke_endpoint(
            "/api/v1/native/sign", "POST", payload, headers
        )
        self.assertEqual(status2, 200)
        self.assertEqual(resp_headers2.get("Idempotent-Replay"), "true")
        self.assertEqual(res2.get("contract_value"), res1.get("contract_value"))

    def test_03_rate_limiting_headers(self):
        """3. Verify X-RateLimit-Limit, X-RateLimit-Remaining, and X-RateLimit-Reset headers across endpoints."""
        endpoints = [
            ("/api/v1/gemini_enterprise/billcom", "POST", {"action": "parse_ocr"}),
            ("/api/v1/native/ap_expense", "POST", {"vendor_or_merchant": "Datadog", "amount": 850.0}),
            ("/api/v1/native/pay", "POST", {"amount": 1200.0, "currency": "USD"}),
        ]
        for path, method, payload in endpoints:
            _, status, resp_headers, _ = self.invoke_endpoint(path, method, payload)
            self.assertEqual(status, 200)
            self.assertIn("X-RateLimit-Limit", resp_headers)
            self.assertIn("X-RateLimit-Remaining", resp_headers)
            self.assertIn("X-RateLimit-Reset", resp_headers)
            self.assertGreater(int(resp_headers["X-RateLimit-Limit"]), 0)
            self.assertGreaterEqual(int(resp_headers["X-RateLimit-Remaining"]), 0)
            self.assertGreater(int(resp_headers["X-RateLimit-Reset"]), 1700000000)

    def test_04_rfc3339_utc_timestamps(self):
        """4. Verify RFC 3339 UTC timestamp string formatting across financial mutation responses."""
        rfc3339_pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$"
        endpoints = [
            ("/api/v1/gemini_enterprise/square_rc", "POST", {"action": "pos_charge", "amount": 350.0}),
            ("/api/v1/native/payroll_tax", "POST", {"gross_payroll": 85000.0, "state": "NY"}),
            ("/api/v1/gemini_enterprise/workflow", "POST", {"acv": 25000.0}),
        ]
        for path, method, payload in endpoints:
            res, status, _, _ = self.invoke_endpoint(path, method, payload)
            self.assertEqual(status, 200)
            self.assertIn("timestamp", res)
            self.assertIsNotNone(re.match(rfc3339_pattern, res["timestamp"]))

    def test_05_gzip_http_compression(self):
        """5. Verify Gzip HTTP compression when Accept-Encoding: gzip is supplied."""
        headers = {"Accept-Encoding": "gzip"}
        payload = {"action": "3way_match", "invoice": {"total_amount": 5000.0}}
        res, status, resp_headers, raw_bytes = self.invoke_endpoint(
            "/api/v1/gemini_enterprise/billcom", "POST", payload, headers
        )
        self.assertEqual(status, 200)
        self.assertEqual(resp_headers.get("Content-Encoding"), "gzip")
        # Verify body is valid gzip binary payload that decompresses into valid JSON
        decompressed_json = json.loads(gzip.decompress(raw_bytes).decode("utf-8"))
        self.assertEqual(decompressed_json, res)


if __name__ == "__main__":
    unittest.main()
