"""
Test suite verifying Edge & Cloud (Vercel/Cloudflare) infrastructure upgrades in sovereign_dashboard_server.py:
1. Full CORS headers & OPTIONS preflight handler (do_OPTIONS)
2. Lightweight /healthz and /readyz probe endpoints
3. Gzip HTTP compression support for large JSON payloads
"""

import sys
import os
import unittest
import json
import io
import gzip

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sovereign_dashboard_server import SovereignDashboardHandler


class TestEdgeCloudInfrastructureUpgrades(unittest.TestCase):

    def create_handler(self, path: str, method: str = "GET", headers: dict = None, body: dict = None):
        body_bytes = json.dumps(body).encode("utf-8") if body else b""
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

        return handler, wfile

    def test_01_options_preflight_cors(self):
        handler, wfile = self.create_handler("/api/v1/overview", "OPTIONS")
        handler.do_OPTIONS()

        self.assertEqual(handler.response_code, 204)
        self.assertEqual(handler.response_headers.get("Access-Control-Allow-Origin"), "*")
        self.assertIn("GET", handler.response_headers.get("Access-Control-Allow-Methods", ""))
        self.assertIn("OPTIONS", handler.response_headers.get("Access-Control-Allow-Methods", ""))
        self.assertIn("Content-Type", handler.response_headers.get("Access-Control-Allow-Headers", ""))
        self.assertEqual(handler.response_headers.get("Access-Control-Max-Age"), "86400")

    def test_02_healthz_liveness_probe(self):
        handler, wfile = self.create_handler("/healthz", "GET")
        handler.do_GET()

        self.assertEqual(handler.response_code, 200)
        output_bytes = wfile.getvalue()
        res = json.loads(output_bytes.decode("utf-8"))
        self.assertEqual(res["status"], "healthy")
        self.assertEqual(res["probe"], "liveness")
        self.assertIn("uptime_seconds", res)

    def test_03_readyz_readiness_probe(self):
        handler, wfile = self.create_handler("/readyz", "GET")
        handler.do_GET()

        self.assertEqual(handler.response_code, 200)
        output_bytes = wfile.getvalue()
        res = json.loads(output_bytes.decode("utf-8"))
        self.assertEqual(res["status"], "ready")
        self.assertEqual(res["probe"], "readiness")
        self.assertTrue(res["checks"]["orchestrator"])
        self.assertTrue(res["checks"]["agent_engine"])

    def test_04_gzip_compression_on_large_payload(self):
        # /api/v1/mcp/tools returns a large payload (> 512 bytes)
        headers = {"Accept-Encoding": "gzip, deflate"}
        handler, wfile = self.create_handler("/api/v1/mcp/tools", "GET", headers=headers)
        handler.do_GET()

        self.assertEqual(handler.response_code, 200)
        self.assertEqual(handler.response_headers.get("Content-Encoding"), "gzip")
        self.assertEqual(handler.response_headers.get("Vary"), "Accept-Encoding")

        output_bytes = wfile.getvalue()
        decompressed = gzip.decompress(output_bytes)
        res = json.loads(decompressed.decode("utf-8"))
        self.assertEqual(res["status"], "SOVEREIGN_MCP_TOOLS_ONLINE")
        self.assertGreater(res["total_tools"], 0)

    def test_05_uncompressed_response_without_gzip_header(self):
        headers = {"Accept-Encoding": "identity"}
        handler, wfile = self.create_handler("/api/v1/mcp/tools", "GET", headers=headers)
        handler.do_GET()

        self.assertEqual(handler.response_code, 200)
        self.assertNotIn("Content-Encoding", handler.response_headers)

        output_bytes = wfile.getvalue()
        res = json.loads(output_bytes.decode("utf-8"))
        self.assertEqual(res["status"], "SOVEREIGN_MCP_TOOLS_ONLINE")

    def test_06_cors_headers_on_standard_get_and_post(self):
        handler, wfile = self.create_handler("/api/v1/overview", "GET")
        handler.do_GET()
        self.assertEqual(handler.response_headers.get("Access-Control-Allow-Origin"), "*")
        self.assertIn("POST", handler.response_headers.get("Access-Control-Allow-Methods", ""))

        handler_post, wfile_post = self.create_handler("/api/v1/gemini/chat", "POST", body={"message": "ping"})
        handler_post.do_POST()
        self.assertEqual(handler_post.response_headers.get("Access-Control-Allow-Origin"), "*")


if __name__ == "__main__":
    unittest.main()
