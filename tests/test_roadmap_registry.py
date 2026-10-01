"""Assert roadmap verify_all has zero failures across IDs 1–250."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from sovereign_books.roadmap_registry import FEATURE_REGISTRY, verify_all


class TestRoadmapRegistry(unittest.TestCase):
    def setUp(self):
        os.environ.pop("PLAID_CLIENT_ID", None)
        os.environ.pop("PLAID_SECRET", None)
        os.environ.pop("REVENUECAT_SECRET_API_KEY", None)
        os.environ.pop("REVENUECAT_API_KEY", None)
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp.close()
        self.db_path = self.tmp.name

    def tearDown(self):
        Path(self.db_path).unlink(missing_ok=True)

    def test_registry_has_250(self):
        self.assertEqual(len(FEATURE_REGISTRY), 250)
        self.assertEqual(set(FEATURE_REGISTRY.keys()), set(range(1, 251)))

    def test_verify_all_zero_failures(self):
        result = verify_all(self.db_path)
        self.assertEqual(
            result["failed"],
            0,
            msg=f"failures={result['failures']} details={[r for r in result['results'] if not r.get('pass')]}",
        )
        self.assertEqual(result["passed"], 250)
        self.assertEqual(result["status"], "OK")


if __name__ == "__main__":
    unittest.main()
