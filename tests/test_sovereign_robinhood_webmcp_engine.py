import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from sovereign_infrastructure.nextgen_systems.sovereign_robinhood_webmcp_engine import robinhood_webmcp_engine

class TestSovereignRobinhoodWebMCPEngine(unittest.TestCase):
    def setUp(self):
        self.engine = robinhood_webmcp_engine

    def test_01_portfolio_summary_and_net_worth(self):
        summary = self.engine.get_portfolio_summary()
        self.assertEqual(summary["status"], "success")
        self.assertEqual(summary["portfolio_id"], "rh_port_8829104")
        self.assertGreater(summary["net_worth"], 1000000.0)
        self.assertIn("holdings", summary)
        self.assertTrue(summary["gl_equilibrium"]["zero_drift_valid"])

    def test_02_agentic_trade_execution_buy_stock(self):
        initial_bp = self.engine.buying_power
        res = self.engine.execute_trade(symbol="NVDA", side="buy", quantity=10, price=128.00)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["order"]["symbol"], "NVDA")
        self.assertEqual(res["order"]["quantity"], 10)
        self.assertEqual(self.engine.buying_power, initial_bp - 1280.00)
        self.assertTrue(self.engine.verify_gl_equilibrium()["zero_drift_valid"])

    def test_03_cash_reserve_sweep(self):
        initial_reserve = self.engine.cash_reserve
        initial_bp = self.engine.buying_power
        res = self.engine.sweep_cash_reserve(amount=5000.00)
        self.assertEqual(res["status"], "success")
        self.assertEqual(self.engine.cash_reserve, initial_reserve + 5000.00)
        self.assertEqual(self.engine.buying_power, initial_bp - 5000.00)
        self.assertTrue(self.engine.verify_gl_equilibrium()["zero_drift_valid"])

    def test_04_options_chain_greeks(self):
        chain = self.engine.get_options_chain(symbol="NVDA")
        self.assertEqual(chain["status"], "success")
        self.assertEqual(chain["symbol"], "NVDA")
        self.assertGreater(len(chain["calls"]), 0)
        self.assertIn("delta", chain["calls"][0])

    def test_05_webmcp_tool_manifest_definitions(self):
        tools = self.engine.get_webmcp_tool_definitions()
        self.assertEqual(len(tools), 4)
        tool_names = [t["name"] for t in tools]
        self.assertIn("robinhood_get_portfolio", tool_names)
        self.assertIn("robinhood_execute_trade", tool_names)
        self.assertIn("robinhood_sync_cash_reserve", tool_names)
        self.assertIn("robinhood_get_options_chain", tool_names)

if __name__ == "__main__":
    unittest.main()
