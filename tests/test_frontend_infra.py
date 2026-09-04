import json
import os
import unittest

from sovereign_infrastructure.frontend_infra import financial_snapshot, snapshot


class TestFrontendInfra(unittest.TestCase):
    def test_finance_engines_load_and_journal_balances(self):
        f = financial_snapshot()
        self.assertTrue(f["engines"]["xfin"]["loaded"])
        self.assertTrue(f["engines"]["mint"]["loaded"])
        self.assertTrue(f["engines"]["billing"]["loaded"])
        self.assertTrue(f["engines"]["billing"]["empty_sig_rejected"])
        self.assertTrue(f["journal"]["balanced"])
        self.assertEqual(f["journal"]["drift"], 0.0)
        self.assertGreater(f["engines"]["xfin"]["treasury_usd"], 0)

    def test_snapshot_lists_pocket_in_kiln(self):
        s = snapshot()
        self.assertEqual(s["schema"], "sovereign.frontend_infra.v1")
        self.assertTrue(s["pocket"]["comes_with_kiln"])
        self.assertEqual(s["pocket"]["mcp"], "http://127.0.0.1:8787")
        self.assertIn("pocket", s["kiln"].get("project_ids") or [])
        self.assertTrue(s["kiln"].get("pocket_seeded"))

    def test_registry_file_has_pocket(self):
        path = r"E:\repos\KILN\projects\registry.json"
        if not os.path.isfile(path):
            self.skipTest("KILN registry not on this disk")
        data = json.loads(open(path, encoding="utf-8").read())
        ids = {p["id"] for p in data["projects"]}
        self.assertIn("pocket", ids)
        self.assertIn("sovereign-engine", ids)


if __name__ == "__main__":
    unittest.main()
