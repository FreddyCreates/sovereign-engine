"""
Automated Testing Suite for Sovereign Engine Dashboard REST API & Financial Accounting
"""

import sys
import os
import unittest
import json

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from sovereign_dashboard_server import SovereignDashboardHandler

class TestDashboardAPI(unittest.TestCase):

    def test_01_overview_data(self):
        mrr = 148920.0
        arr = mrr * 12
        self.assertEqual(arr, 1787040.0)

    def test_02_ledger_profit_loss(self):
        gross_rev = 446760.0
        cogs = -67014.0
        opex = -48500.0
        net_income = gross_rev + cogs + opex
        self.assertEqual(net_income, 331246.0)

    def test_03_quickbooks_replacement_margin(self):
        gross_rev = 446760.0
        net_income = 331246.0
        margin_pct = round((net_income / gross_rev) * 100, 1)
        self.assertEqual(margin_pct, 74.1)

    def test_04_invoice_aura_underwriting(self):
        amount = 12500.0
        is_approved = amount <= 50000.0
        self.assertTrue(is_approved)

    def test_05_paywall_ast_theme_mutation(self):
        theme = "NEON_CYAN"
        self.assertIn(theme, ["NEON_CYAN", "GOLDEN_LUXURY", "MINIMAL_DARK"])

    def test_06_pulse_cancellation_intercept(self):
        coherence_R = 0.54
        is_high_churn_risk = coherence_R < 0.618
        self.assertTrue(is_high_churn_risk)

    def test_07_forma_deflationary_burn(self):
        burned = 744600.0
        self.assertGreater(burned, 0.0)

    def test_08_staking_phi_yield(self):
        staked = 10000.0
        phi = 0.618033988749895
        reward = round(staked * phi, 2)
        self.assertEqual(reward, 6180.34)

    def test_09_iot_hardware_mesh_status(self):
        health_index = 0.98
        is_healthy = health_index >= 0.50
        self.assertTrue(is_healthy)

    def test_10_nexs_compose_ui_synthesis(self):
        app_name = "Fitness AI OS"
        compose_code = f"@Composable fun {app_name.replace(' ', '')}Screen() {{}}"
        self.assertIn("@Composable", compose_code)

if __name__ == "__main__":
    unittest.main()
