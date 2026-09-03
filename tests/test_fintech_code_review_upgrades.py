"""
Exhaustive Automated Test Suite for FinTech Code Review Upgrades:
1. Idempotency-Key Handling on Financial Mutation POST Endpoints (/api/v1/native/*, /api/v1/dilithium/*, /api/v1/email/send)
2. RFC 3339 UTC Timestamps & Rate Limiting HTTP Headers (X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset)
3. Double-Entry Accounting Zero Float Precision Drift Validation
"""

import unittest
import json
import re
from io import BytesIO
from sovereign_dashboard_server import (
    SovereignDashboardHandler,
    validate_double_entry_zero_drift,
    get_rfc3339_utc_timestamp,
    rate_limiter,
    IDEMPOTENCY_STORE
)

class MockHTTPResponse:
    def __init__(self):
        self.headers = {}
        self.status_code = 200
        self.wfile = BytesIO()

class BaseDashboardTestCase(unittest.TestCase):
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
                self._hdrs = {k.lower(): v for k, v in hdrs.items()}
            def get(self, key, default=None):
                return self._hdrs.get(key.lower(), default)

        handler.headers = MockMessage(headers_dict)
        handler.response_headers = {}

        def mock_send_response(code, message=None):
            handler.response_code = code

        def mock_send_header(keyword, value):
            handler.response_headers[keyword] = value

        handler.send_response = mock_send_response
        handler.send_header = mock_send_header
        handler.end_headers = lambda: None

        if method.upper() == "GET":
            handler.do_GET()
        else:
            handler.do_POST()

        output_bytes = handler.wfile.getvalue()
        res_data = json.loads(output_bytes.decode("utf-8")) if output_bytes else {}
        return res_data, handler.response_code, handler.response_headers

class TestFinTechCodeReviewUpgrades(BaseDashboardTestCase):
    
    def test_01_idempotency_key_replay_native_pay(self):
        """1. Verify Idempotency-Key replay on financial mutation POST endpoint (/api/v1/native/pay)."""
        idem_key = "idem_test_native_pay_8899"
        payload = {"amount": 5000.00, "currency": "USD", "customer_id": "cust_fintech_01"}
        headers = {"Idempotency-Key": idem_key}

        # First Call
        res1, status1, resp_headers1 = self.invoke_endpoint("/api/v1/native/pay", "POST", payload, headers)
        self.assertEqual(status1, 200)
        self.assertEqual(res1["amount"], 5000.00)
        self.assertEqual(res1["idempotency_key"], idem_key)
        self.assertEqual(res1["idempotency_handled"], True)

        # Second Call (Duplicate with same Idempotency-Key)
        res2, status2, resp_headers2 = self.invoke_endpoint("/api/v1/native/pay", "POST", payload, headers)
        self.assertEqual(status2, 200)
        self.assertEqual(res2["amount"], res1["amount"])
        self.assertEqual(res2["payment_id"], res1["payment_id"])
        self.assertEqual(resp_headers2.get("Idempotent-Replay"), "true")

    def test_02_idempotency_key_email_send(self):
        """2. Verify Idempotency-Key handling on transactional email POST endpoint (/api/v1/email/send)."""
        idem_key = "idem_email_tx_1001"
        payload = {"to": "cfo@stripe.com", "subject": "Quarterly Billing", "total_amount_usd": 15000.00}
        headers = {"Idempotency-Key": idem_key}

        res1, status1, resp_headers1 = self.invoke_endpoint("/api/v1/email/send", "POST", payload, headers)
        self.assertEqual(status1, 200)
        self.assertEqual(res1["status"], "SUCCESS")
        self.assertEqual(res1["idempotency_key"], idem_key)

        # Replay call
        res2, status2, resp_headers2 = self.invoke_endpoint("/api/v1/email/send", "POST", payload, headers)
        self.assertEqual(status2, 200)
        self.assertEqual(res2, res1)
        self.assertEqual(resp_headers2.get("Idempotent-Replay"), "true")

    def test_03_rfc3339_utc_timestamp_standardization(self):
        """3. Verify RFC 3339 UTC timestamp formatting across GET & POST responses."""
        res_get, _, _ = self.invoke_endpoint("/api/v1/overview", "GET")
        self.assertIn("timestamp", res_get)
        # Verify RFC 3339 pattern YYYY-MM-DDTHH:MM:SSZ
        rfc3339_regex = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$"
        self.assertIsNotNone(re.match(rfc3339_regex, res_get["timestamp"]))

        res_post, _, _ = self.invoke_endpoint("/api/v1/dilithium/settlement", "POST", {"amount": 250.00})
        self.assertIn("timestamp", res_post)
        self.assertIsNotNone(re.match(rfc3339_regex, res_post["timestamp"]))

    def test_04_ratelimit_http_headers(self):
        """4. Verify X-RateLimit-Limit, X-RateLimit-Remaining, and X-RateLimit-Reset headers are returned."""
        _, _, headers = self.invoke_endpoint("/api/v1/overview", "GET")
        self.assertIn("X-RateLimit-Limit", headers)
        self.assertIn("X-RateLimit-Remaining", headers)
        self.assertIn("X-RateLimit-Reset", headers)
        self.assertGreater(int(headers["X-RateLimit-Limit"]), 0)
        self.assertGreaterEqual(int(headers["X-RateLimit-Remaining"]), 0)
        self.assertGreater(int(headers["X-RateLimit-Reset"]), 1700000000)

    def test_05_double_entry_zero_float_precision_drift(self):
        """5. Ensure double-entry accounting entries validate zero float precision drift."""
        # Test valid balanced entries
        audit = validate_double_entry_zero_drift(1250.50, 1250.50)
        self.assertTrue(audit["zero_precision_drift_valid"])
        self.assertEqual(audit["balance_variance"], 0.00)
        self.assertEqual(audit["total_debits"], 1250.50)
        self.assertEqual(audit["total_credits"], 1250.50)

        # Verify posting via native accounting endpoint
        res, status, _ = self.invoke_endpoint("/api/v1/native/accounting", "POST", {
            "amount": 3499.99,
            "description": "Enterprise SaaS Retainer",
            "debit_account": "1000",
            "credit_account": "4000"
        })
        self.assertEqual(status, 200)
        self.assertTrue(res["zero_precision_drift_valid"])
        self.assertEqual(res["balance_variance"], 0.00)

    def test_06_unbalanced_double_entry_drift_rejection(self):
        """6. Verify unbalanced double-entry accounting postings raise ValueError and zero drift rejection."""
        with self.assertRaises(ValueError) as ctx:
            validate_double_entry_zero_drift(100.00, 99.99)
        self.assertIn("UNBALANCED_JOURNAL_ENTRY", str(ctx.exception))

if __name__ == "__main__":
    unittest.main()
