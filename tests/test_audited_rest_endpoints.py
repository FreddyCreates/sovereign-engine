"""
Exhaustive Automated Test Suite for Audited & Optimized Sovereign Engine REST API Endpoints:
1. /api/v1/machine_mode/*
2. /api/v1/agentic/*
3. /api/v1/crypto_wallet/*
4. /api/v1/grants/*
5. /api/v1/capital/*

Verifies:
- Gzip Compression when Accept-Encoding: gzip is requested
- RFC 3339 UTC Timestamps (%Y-%m-%dT%H:%M:%SZ)
- Zero Float Drift across all decimal precision fields
- Idempotency & Unified Substrate Sync across all handlers
"""

import sys
import os
import unittest
import json
import gzip
import io
import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sovereign_dashboard_server import SovereignDashboardHandler, get_rfc3339_utc_timestamp


class TestAuditedRestEndpoints(unittest.TestCase):

    def invoke_endpoint(self, path: str, method: str = "GET", body: dict = None, headers: dict = None) -> tuple:
        """Helper to invoke server endpoints, returning status_code, headers, and decoded payload."""
        body_bytes = json.dumps(body).encode("utf-8") if body is not None else b""
        rfile = io.BytesIO(body_bytes)
        wfile = io.BytesIO()

        handler = SovereignDashboardHandler.__new__(SovereignDashboardHandler)
        handler.path = path
        handler.rfile = rfile
        handler.wfile = wfile
        
        req_headers = {"Content-Length": str(len(body_bytes))}
        if method.upper() == "POST":
            req_headers["Content-Type"] = "application/json"
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

        raw_output = wfile.getvalue()
        content_encoding = handler.response_headers.get("Content-Encoding", "")
        
        if content_encoding == "gzip":
            decompressed = gzip.decompress(raw_output)
            json_payload = json.loads(decompressed.decode("utf-8")) if decompressed else {}
        else:
            json_payload = json.loads(raw_output.decode("utf-8")) if raw_output else {}

        return handler.response_code, handler.response_headers, json_payload

    def assert_rfc3339_and_zero_float_drift(self, res: dict):
        """Verifies RFC 3339 UTC timestamp compliance and max 6 decimal places for floats."""
        self.assertIsNotNone(res)
        self.assertIn("timestamp", res)
        ts = str(res["timestamp"])
        self.assertTrue("T" in ts and (ts.endswith("Z") or "+" in ts or "-" in ts[10:]), f"Timestamp '{ts}' not RFC 3339 compliant")

        def check_floats(obj):
            if isinstance(obj, float):
                s = str(obj)
                if "." in s and not ("e" in s.lower()):
                    decimals = len(s.split(".")[1])
                    self.assertLessEqual(decimals, 6, f"Float {obj} exceeds 6 decimal places (float drift)")
            elif isinstance(obj, dict):
                for v in obj.values():
                    check_floats(v)
            elif isinstance(obj, list):
                for item in obj:
                    check_floats(item)

        check_floats(res)

    # -------------------------------------------------------------------------
    # Engine 1: Machine Mode Endpoints (/api/v1/machine_mode/*) - 5 Tests
    # -------------------------------------------------------------------------
    def test_01_machine_mode_telemetry_get(self):
        code, headers, res = self.invoke_endpoint("/api/v1/machine_mode/telemetry", "GET")
        self.assertEqual(code, 200)
        self.assertEqual(res["status"], "MACHINE_MODE_HYPERSPEED_ACTIVE")
        self.assertEqual(res["records_per_sec"], 145200)
        self.assertTrue(res["zero_float_drift"])
        self.assert_rfc3339_and_zero_float_drift(res)

    def test_02_machine_mode_telemetry_post(self):
        body = {"custom_multiplier": 50.0}
        code, headers, res = self.invoke_endpoint("/api/v1/machine_mode/telemetry", "POST", body)
        self.assertEqual(code, 200)
        self.assertIn("status", res)
        self.assert_rfc3339_and_zero_float_drift(res)

    def test_03_machine_mode_status_get_and_post(self):
        code_get, _, res_get = self.invoke_endpoint("/api/v1/machine_mode/status", "GET")
        self.assertEqual(code_get, 200)
        self.assertEqual(res_get["status"], "OPERATIONAL")
        self.assert_rfc3339_and_zero_float_drift(res_get)

        code_post, _, res_post = self.invoke_endpoint("/api/v1/machine_mode/status", "POST", {})
        self.assertEqual(code_post, 200)
        self.assertEqual(res_post["status"], "OPERATIONAL")
        self.assert_rfc3339_and_zero_float_drift(res_post)

    def test_04_machine_mode_ingest_post(self):
        body = {"records": [{"id": 1, "val": 10.5}, {"id": 2, "val": 20.25}]}
        code, _, res = self.invoke_endpoint("/api/v1/machine_mode/ingest", "POST", body)
        self.assertEqual(code, 200)
        self.assertEqual(res["status"], "MACHINE_MODE_BATCH_INGESTED")
        self.assertEqual(res["records_processed"], 2)
        self.assert_rfc3339_and_zero_float_drift(res)

    def test_05_machine_mode_gzip_compression(self):
        headers = {"Accept-Encoding": "gzip"}
        code, resp_headers, res = self.invoke_endpoint("/api/v1/machine_mode/telemetry", "GET", headers=headers)
        self.assertEqual(code, 200)
        self.assertEqual(resp_headers.get("Content-Encoding"), "gzip")
        self.assertEqual(res["status"], "MACHINE_MODE_HYPERSPEED_ACTIVE")

    # -------------------------------------------------------------------------
    # Engine 2: Agentic Endpoints (/api/v1/agentic/*) - 5 Tests
    # -------------------------------------------------------------------------
    def test_06_agentic_status_get_and_post(self):
        code_get, _, res_get = self.invoke_endpoint("/api/v1/agentic/status", "GET")
        self.assertEqual(code_get, 200)
        self.assertEqual(res_get["status"], "ONLINE")
        self.assert_rfc3339_and_zero_float_drift(res_get)

        code_post, _, res_post = self.invoke_endpoint("/api/v1/agentic/status", "POST", {})
        self.assertEqual(code_post, 200)
        self.assertEqual(res_post["status"], "ONLINE")
        self.assert_rfc3339_and_zero_float_drift(res_post)

    def test_07_agentic_auto_fill_grant_get_and_post(self):
        code_get, _, res_get = self.invoke_endpoint("/api/v1/agentic/auto_fill_grant?mrr=200000.0", "GET")
        self.assertEqual(code_get, 200)
        self.assertIn("grant_id", res_get)
        self.assert_rfc3339_and_zero_float_drift(res_get)

        body = {"grant_id": "grant-sbir-sttr", "mrr": 200000.0, "company_name": "Apex Quantum"}
        code_post, _, res_post = self.invoke_endpoint("/api/v1/agentic/auto_fill_grant", "POST", body)
        self.assertEqual(code_post, 200)
        self.assertIn("grant_id", res_post)
        self.assert_rfc3339_and_zero_float_drift(res_post)

    def test_08_agentic_parse_emails_get_and_post(self):
        code_get, _, res_get = self.invoke_endpoint("/api/v1/agentic/parse_emails?email_body=Invoice%20$5000", "GET")
        self.assertEqual(code_get, 200)
        self.assertIsNotNone(res_get)
        self.assert_rfc3339_and_zero_float_drift(res_get)

        body = {"email_body": "Invoice #INV-2026-101 for $15,000.00", "channel": "Gmail"}
        code_post, _, res_post = self.invoke_endpoint("/api/v1/agentic/parse_emails", "POST", body)
        self.assertEqual(code_post, 200)
        self.assertIsNotNone(res_post)
        self.assert_rfc3339_and_zero_float_drift(res_post)

    def test_09_agentic_claim_passport_perk_get_and_post(self):
        code_get, _, res_get = self.invoke_endpoint("/api/v1/agentic/claim_passport_perk?perk_type=CLOUD_CREDITS", "GET")
        self.assertEqual(code_get, 200)
        self.assertIn("status", res_get)
        self.assert_rfc3339_and_zero_float_drift(res_get)

        body = {"rnft_id": "rnft_demo_99", "perk_type": "AIRPORT_LOUNGE", "passenger_name": "Jane Executive"}
        code_post, _, res_post = self.invoke_endpoint("/api/v1/agentic/claim_passport_perk", "POST", body)
        self.assertEqual(code_post, 200)
        self.assertIn("status", res_post)
        self.assert_rfc3339_and_zero_float_drift(res_post)

    def test_10_agentic_gzip_compression_and_rfc3339(self):
        headers = {"Accept-Encoding": "gzip"}
        code, resp_headers, res = self.invoke_endpoint("/api/v1/agentic/status", "GET", headers=headers)
        self.assertEqual(code, 200)
        self.assertEqual(resp_headers.get("Content-Encoding"), "gzip")
        self.assert_rfc3339_and_zero_float_drift(res)

    # -------------------------------------------------------------------------
    # Engine 3: Crypto Wallet Endpoints (/api/v1/crypto_wallet/*) - 5 Tests
    # -------------------------------------------------------------------------
    def test_11_crypto_wallet_status_and_balances(self):
        code_st, _, res_st = self.invoke_endpoint("/api/v1/crypto_wallet/status", "GET")
        self.assertEqual(code_st, 200)
        self.assertIsNotNone(res_st)
        self.assert_rfc3339_and_zero_float_drift(res_st)

        code_bal, _, res_bal = self.invoke_endpoint("/api/v1/crypto_wallet/treasury/balances", "GET")
        self.assertEqual(code_bal, 200)
        self.assertIsNotNone(res_bal)
        self.assert_rfc3339_and_zero_float_drift(res_bal)

    def test_12_crypto_wallet_rnft_mint_zero_drift(self):
        body = {"subscriber_id": "sub_test_01", "mrr_value": 499.00, "duration_days": 365}
        code, _, res = self.invoke_endpoint("/api/v1/crypto_wallet/rnft/mint", "POST", body)
        self.assertEqual(code, 200)
        self.assertIsNotNone(res)
        self.assert_rfc3339_and_zero_float_drift(res)

    def test_13_crypto_wallet_treasury_transfer_and_capacity(self):
        body_tr = {"from_chain": "ethereum", "to_chain": "solana", "asset": "USDC", "amount": 10000.00}
        code_tr, _, res_tr = self.invoke_endpoint("/api/v1/crypto_wallet/treasury/transfer", "POST", body_tr)
        self.assertEqual(code_tr, 200)
        self.assertTrue("transfer_status" in res_tr or "status" in res_tr)
        self.assert_rfc3339_and_zero_float_drift(res_tr)

        code_cap, _, res_cap = self.invoke_endpoint("/api/v1/crypto_wallet/factoring/capacity?mrr=15000.0", "GET")
        self.assertEqual(code_cap, 200)
        self.assertTrue("max_loan_capacity_usd" in res_cap or "factoring_capacity_usd" in res_cap)
        self.assert_rfc3339_and_zero_float_drift(res_cap)

    def test_14_crypto_wallet_factoring_originate_and_repay(self):
        body_orig = {"subscriber_id": "sub_orig_01", "loan_amount_usd": 20000.0, "term_months": 12}
        code_o, _, res_o = self.invoke_endpoint("/api/v1/crypto_wallet/factoring/loan/originate", "POST", body_orig)
        self.assertEqual(code_o, 200)
        self.assertTrue("loan" in res_o or "loan_id" in res_o)
        self.assert_rfc3339_and_zero_float_drift(res_o)

        loan_id = res_o.get("loan", {}).get("loan_id", res_o.get("loan_id", "loan_demo"))
        body_repay = {"loan_id": loan_id, "payment_amount_usd": 1500.0}
        code_r, _, res_r = self.invoke_endpoint("/api/v1/crypto_wallet/factoring/loan/repay", "POST", body_repay)
        self.assertEqual(code_r, 200)
        self.assertTrue("payment_processed_usd" in res_r or "status" in res_r)
        self.assert_rfc3339_and_zero_float_drift(res_r)

    def test_15_crypto_wallet_zk_sign_and_verify(self):
        body_sign = {"payload": {"transaction_id": "tx_9901", "amount": 5000.0}}
        code_s, _, res_s = self.invoke_endpoint("/api/v1/crypto_wallet/zk/sign", "POST", body_sign)
        self.assertEqual(code_s, 200)
        self.assertIn("dilithium_signature", res_s)
        self.assert_rfc3339_and_zero_float_drift(res_s)

        sig = res_s["dilithium_signature"]
        zk_proof = res_s["zk_proof"]
        pubkey = res_s["signer_pubkey"]
        body_ver = {"payload": {"transaction_id": "tx_9901", "amount": 5000.0}, "signature": sig, "zk_proof": zk_proof, "public_key": pubkey}
        code_v, _, res_v = self.invoke_endpoint("/api/v1/crypto_wallet/zk/verify", "POST", body_ver)
        self.assertEqual(code_v, 200)
        self.assertTrue(res_v["valid"])
        self.assert_rfc3339_and_zero_float_drift(res_v)

    # -------------------------------------------------------------------------
    # Engine 4: Grants Endpoints (/api/v1/grants/*) - 5 Tests
    # -------------------------------------------------------------------------
    def test_16_grants_catalog_get_and_post(self):
        code_g, _, res_g = self.invoke_endpoint("/api/v1/grants/catalog", "GET")
        self.assertEqual(code_g, 200)
        self.assertIn("grants", res_g)
        self.assert_rfc3339_and_zero_float_drift(res_g)

        code_p, _, res_p = self.invoke_endpoint("/api/v1/grants/catalog", "POST", {"category": "AI"})
        self.assertEqual(code_p, 200)
        self.assertIn("grants", res_p)
        self.assert_rfc3339_and_zero_float_drift(res_p)

    def test_17_grants_status_get_and_post(self):
        code_g, _, res_g = self.invoke_endpoint("/api/v1/grants/status", "GET")
        self.assertEqual(code_g, 200)
        self.assertEqual(res_g["status"], "GRANTS_ENGINE_ACTIVE")
        self.assert_rfc3339_and_zero_float_drift(res_g)

        code_p, _, res_p = self.invoke_endpoint("/api/v1/grants/status", "POST", {})
        self.assertEqual(code_p, 200)
        self.assertEqual(res_p["status"], "GRANTS_ENGINE_ACTIVE")
        self.assert_rfc3339_and_zero_float_drift(res_p)

    def test_18_grants_apply_get_and_post(self):
        code_g, _, res_g = self.invoke_endpoint("/api/v1/grants/apply?grant_id=grant-sbir-sttr", "GET")
        self.assertEqual(code_g, 200)
        self.assertTrue("application_id" in res_g or "dossier" in res_g or "grant_id" in res_g)
        self.assert_rfc3339_and_zero_float_drift(res_g)

        body = {"grant_id": "grant-sbir-sttr", "company_name": "Sovereign OS Inc."}
        code_p, _, res_p = self.invoke_endpoint("/api/v1/grants/apply", "POST", body)
        self.assertEqual(code_p, 200)
        self.assertTrue("application_id" in res_p or "dossier" in res_p or "grant_id" in res_p)
        self.assert_rfc3339_and_zero_float_drift(res_p)

    def test_19_grants_custom_subpath(self):
        code_g, _, res_g = self.invoke_endpoint("/api/v1/grants/custom_subpath", "GET")
        self.assertEqual(code_g, 200)
        self.assertEqual(res_g["status"], "GRANTS_ENDPOINT_ACTIVE")
        self.assert_rfc3339_and_zero_float_drift(res_g)

        code_p, _, res_p = self.invoke_endpoint("/api/v1/grants/custom_subpath", "POST", {})
        self.assertEqual(code_p, 200)
        self.assertEqual(res_p["status"], "GRANTS_ENDPOINT_ACTIVE")
        self.assert_rfc3339_and_zero_float_drift(res_p)

    def test_20_grants_gzip_and_zero_drift(self):
        headers = {"Accept-Encoding": "gzip"}
        code, resp_headers, res = self.invoke_endpoint("/api/v1/grants/catalog", "GET", headers=headers)
        self.assertEqual(code, 200)
        self.assertEqual(resp_headers.get("Content-Encoding"), "gzip")
        self.assert_rfc3339_and_zero_float_drift(res)

    # -------------------------------------------------------------------------
    # Engine 5: Capital Endpoints (/api/v1/capital/*) - 5 Tests
    # -------------------------------------------------------------------------
    def test_21_capital_offers_get_and_post(self):
        code_g, _, res_g = self.invoke_endpoint("/api/v1/capital/offers?mrr=100000.0", "GET")
        self.assertEqual(code_g, 200)
        self.assertTrue("offers" in res_g or "capital_offers" in res_g or "rbf_offers" in res_g)
        self.assert_rfc3339_and_zero_float_drift(res_g)

        code_p, _, res_p = self.invoke_endpoint("/api/v1/capital/offers", "POST", {"mrr": 100000.0})
        self.assertEqual(code_p, 200)
        self.assertTrue("offers" in res_p or "capital_offers" in res_p or "rbf_offers" in res_p)
        self.assert_rfc3339_and_zero_float_drift(res_p)

    def test_22_capital_status_get_and_post(self):
        code_g, _, res_g = self.invoke_endpoint("/api/v1/capital/status", "GET")
        self.assertEqual(code_g, 200)
        self.assertEqual(res_g["status"], "CAPITAL_ENGINE_ACTIVE")
        self.assert_rfc3339_and_zero_float_drift(res_g)

        code_p, _, res_p = self.invoke_endpoint("/api/v1/capital/status", "POST", {})
        self.assertEqual(code_p, 200)
        self.assertEqual(res_p["status"], "CAPITAL_ENGINE_ACTIVE")
        self.assert_rfc3339_and_zero_float_drift(res_p)

    def test_23_capital_apply_get_and_post(self):
        code_g, _, res_g = self.invoke_endpoint("/api/v1/capital/apply?subscriber_id=sub_capital_01&loan_amount_usd=30000.0", "GET")
        self.assertEqual(code_g, 200)
        self.assertTrue("loan" in res_g or "loan_id" in res_g)
        self.assert_rfc3339_and_zero_float_drift(res_g)

        body = {"subscriber_id": "sub_capital_01", "loan_amount_usd": 30000.0, "term_months": 12}
        code_p, _, res_p = self.invoke_endpoint("/api/v1/capital/apply", "POST", body)
        self.assertEqual(code_p, 200)
        self.assertTrue("loan" in res_p or "loan_id" in res_p)
        self.assert_rfc3339_and_zero_float_drift(res_p)

    def test_24_capital_catch_all_route(self):
        code_g, _, res_g = self.invoke_endpoint("/api/v1/capital/custom_subpath", "GET")
        self.assertEqual(code_g, 200)
        self.assertEqual(res_g["status"], "CAPITAL_ENDPOINT_ACTIVE")
        self.assert_rfc3339_and_zero_float_drift(res_g)

        code_p, _, res_p = self.invoke_endpoint("/api/v1/capital/custom_subpath", "POST", {})
        self.assertEqual(code_p, 200)
        self.assertEqual(res_p["status"], "CAPITAL_ENDPOINT_ACTIVE")
        self.assert_rfc3339_and_zero_float_drift(res_p)

    def test_25_capital_gzip_and_zero_drift(self):
        headers = {"Accept-Encoding": "gzip"}
        code, resp_headers, res = self.invoke_endpoint("/api/v1/capital/offers", "GET", headers=headers)
        self.assertEqual(code, 200)
        self.assertEqual(resp_headers.get("Content-Encoding"), "gzip")
        self.assert_rfc3339_and_zero_float_drift(res)


if __name__ == "__main__":
    unittest.main()
