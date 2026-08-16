"""
Exhaustive Automated Unit Test Suite for 6 Next-Gen 4-Letter Systems:
XFIN, AURA, PULSE, MINT, GRID, NEXS & Master Orchestrator
Requires exactly 5 tests per engine (30 tests total) + master orchestrator integration test.
"""

import unittest
import sys
import os

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sovereign_infrastructure.nextgen_systems.xfin_engine import XFINEngine
from sovereign_infrastructure.nextgen_systems.aura_engine import AURAEngine
from sovereign_infrastructure.nextgen_systems.pulse_engine import PULSEEngine
from sovereign_infrastructure.nextgen_systems.mint_engine import MINTEngine
from sovereign_infrastructure.nextgen_systems.grid_engine import GRIDEngine
from sovereign_infrastructure.nextgen_systems.nexs_engine import NEXSEngine
from sovereign_infrastructure.nextgen_systems.nextgen_master_orchestrator import NextGenMasterOrchestrator


class TestXFINEngine(unittest.TestCase):
    """Test Suite for System 1: XFIN (FX Arbitrage & Telemetry)"""

    def setUp(self):
        self.engine = XFINEngine(treasury_balance_usd=100000.0)

    def test_xfin_calculate_fx_spread(self):
        spread = self.engine.calculate_fx_spread("USD", "EUR")
        self.assertEqual(spread, 0.92)

    def test_xfin_execute_cross_border_settlement(self):
        res = self.engine.execute_cross_border_settlement("usr_101", 100.0, "EUR")
        self.assertEqual(res["status"], "SETTLED")
        self.assertEqual(res["settled_usd"], 108.70)
        self.assertEqual(self.engine.get_treasury_balance(), 100108.70)

    def test_xfin_hedge_currency_exposure(self):
        hedge = self.engine.hedge_currency_exposure("BRL", 5000.0)
        self.assertEqual(hedge["status"], "ACTIVE_HEDGE")
        self.assertGreater(hedge["forward_rate"], 0)
        self.assertEqual(len(self.engine.active_hedges), 1)

    def test_xfin_evaluate_arbitrage_yield(self):
        arb = self.engine.evaluate_arbitrage_yield("BRL", 10000.0)
        self.assertTrue(arb["is_profitable"])
        self.assertGreater(arb["arbitrage_yield_usd"], 0)

    def test_xfin_get_treasury_balance(self):
        bal = self.engine.get_treasury_balance()
        self.assertEqual(bal, 100000.0)


class TestAURAEngine(unittest.TestCase):
    """Test Suite for System 2: AURA (Underwriting & Credit Risk)"""

    def setUp(self):
        self.engine = AURAEngine(base_credit_limit=2000.0)

    def test_aura_evaluate_credit_risk(self):
        pd = self.engine.evaluate_credit_risk("usr_201", payment_history_ratio=0.98, chargebacks=0, tenure_months=12)
        self.assertGreaterEqual(pd, 0.0)
        self.assertLessEqual(pd, 1.0)

    def test_aura_determine_risk_tier(self):
        self.assertEqual(self.engine.determine_risk_tier(0.05), "LOW")
        self.assertEqual(self.engine.determine_risk_tier(0.25), "MEDIUM")
        self.assertEqual(self.engine.determine_risk_tier(0.55), "HIGH")
        self.assertEqual(self.engine.determine_risk_tier(0.85), "CRITICAL")

    def test_aura_calculate_expected_loss(self):
        el = self.engine.calculate_expected_loss(pd=0.10, lgd=0.5, ead=1000.0)
        self.assertEqual(el, 50.0)

    def test_aura_underwrite_subscription_bnpl(self):
        res = self.engine.underwrite_subscription_bnpl("usr_201", subscription_cost=299.0, pd=0.10)
        self.assertEqual(res["status"], "APPROVED")
        self.assertEqual(res["risk_tier"], "LOW")

    def test_aura_adjust_credit_limit(self):
        new_limit = self.engine.adjust_credit_limit("usr_201", performance_score=1.0)
        self.assertEqual(new_limit, 4000.0)


class TestPULSEEngine(unittest.TestCase):
    """Test Suite for System 3: PULSE (Subscriber LTV & Retention)"""

    def setUp(self):
        self.engine = PULSEEngine(default_arpu=19.99)

    def test_pulse_predict_survival_probability(self):
        surv_0 = self.engine.predict_survival_probability(0)
        surv_100 = self.engine.predict_survival_probability(100)
        self.assertEqual(surv_0, 1.0)
        self.assertLess(surv_100, surv_0)

    def test_pulse_calculate_discounted_ltv(self):
        ltv = self.engine.calculate_discounted_ltv(arpu=20.0, monthly_churn_rate=0.05, discount_rate=0.10, months=12)
        self.assertGreater(ltv, 0.0)

    def test_pulse_evaluate_churn_risk(self):
        churn_risk = self.engine.evaluate_churn_risk("usr_301", engagement_score=0.2, support_tickets=3, tenure_days=90)
        self.assertGreaterEqual(churn_risk, 0.0)
        self.assertLessEqual(churn_risk, 1.0)

    def test_pulse_generate_targeted_retention_offer(self):
        offer = self.engine.generate_targeted_retention_offer("usr_301", churn_risk_score=0.75, expected_ltv=150.0)
        self.assertTrue(offer["eligible"])
        self.assertEqual(offer["discount_pct"], 40.0)

    def test_pulse_trigger_revenuecat_winback_hook(self):
        payload = self.engine.trigger_revenuecat_winback_hook("usr_301", discount_pct=40.0)
        self.assertEqual(payload["event"], "REVENUECAT_WINBACK_TRIGGERED")
        self.assertEqual(payload["status"], "DISPATCHED")


class TestMINTEngine(unittest.TestCase):
    """Test Suite for System 4: MINT (Deflationary Tokenomics & Liquidity)"""

    def setUp(self):
        self.engine = MINTEngine(initial_supply=100000.0, base_price_usd=1.00, burn_rate=0.15)

    def test_mint_calculate_bonding_price(self):
        price = self.engine.calculate_bonding_price(100000.0)
        self.assertGreater(price, 1.00)

    def test_mint_mint_fiat_backed_tokens(self):
        res = self.engine.mint_fiat_backed_tokens("usr_401", fiat_amount_usd=100.0)
        self.assertEqual(res["system"], "MINT")
        self.assertGreater(res["tokens_minted"], 0)

    def test_mint_execute_subscription_burn(self):
        res = self.engine.execute_subscription_burn("usr_401", renewal_amount_usd=50.0)
        self.assertGreater(res["tokens_burned"], 0)
        self.assertGreater(res["total_burned"], 0)

    def test_mint_distribute_staking_yield(self):
        res = self.engine.distribute_staking_yield("usr_401", staked_amount=1000.0, apy_pct=12.0)
        self.assertEqual(res["monthly_yield_tokens"], 10.0)

    def test_mint_get_tokenomics_state(self):
        state = self.engine.get_tokenomics_state()
        self.assertIn("total_supply", state)
        self.assertIn("total_burned", state)
        self.assertIn("current_token_price", state)


class TestGRIDEngine(unittest.TestCase):
    """Test Suite for System 5: GRID (IoT Telemetry & Mesh Entitlement)"""

    def setUp(self):
        self.engine = GRIDEngine()

    def test_grid_register_device(self):
        dev = self.engine.register_device("dev_watch_01", "WEAR_OS", "US")
        self.assertEqual(dev["status"], "ONLINE")
        self.assertEqual(dev["device_type"], "WEAR_OS")

    def test_grid_evaluate_device_telemetry(self):
        score = self.engine.evaluate_device_telemetry("dev_watch_01", cpu_usage_pct=20.0, mem_usage_pct=30.0, latency_ms=50.0)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

    def test_grid_verify_mesh_entitlement_consensus(self):
        self.engine.register_device("dev_01", "MOBILE", "US")
        self.engine.evaluate_device_telemetry("dev_01", 10.0, 10.0, 10.0)
        consensus = self.engine.verify_mesh_entitlement_consensus("usr_501", ["dev_01"])
        self.assertTrue(consensus["quorum_reached"])
        self.assertEqual(consensus["entitlement_status"], "ENTITLED_MESH_ACTIVE")

    def test_grid_enforce_geofenced_tier_access(self):
        res = self.engine.enforce_geofenced_tier_access("dev_01", lat=37.7749, lon=-122.4194)
        self.assertEqual(res["access_status"], "ACCESS_GRANTED")
        self.assertEqual(res["distance_km"], 0.0)

    def test_grid_get_device_telemetry_status(self):
        self.engine.register_device("dev_02", "EDGE_NODE", "DE")
        status = self.engine.get_device_telemetry_status("dev_02")
        self.assertEqual(status["status"], "ONLINE")


class TestNEXSEngine(unittest.TestCase):
    """Test Suite for System 6: NEXS (Neural Dynamic App Synthesis & Paywalls)"""

    def setUp(self):
        self.engine = NEXSEngine()

    def test_nexs_select_optimal_paywall_variant(self):
        var = self.engine.select_optimal_paywall_variant("usr_601")
        self.assertIn(var, self.engine.paywall_variants)

    def test_nexs_record_paywall_conversion(self):
        self.engine.record_paywall_conversion("var_A_minimal", converted=True, revenue_usd=19.99)
        stats = self.engine.get_paywall_performance_stats()
        self.assertEqual(stats["variants"]["var_A_minimal"]["conversions"], 1)

    def test_nexs_synthesize_dynamic_offering(self):
        offering = self.engine.synthesize_dynamic_offering("usr_601", "BR", base_usd_price=20.0)
        self.assertEqual(offering["adapted_usd_price"], 9.0)  # PPP factor 0.45 * 20.0

    def test_nexs_calculate_segment_elasticity(self):
        ped = self.engine.calculate_segment_elasticity(price_point_1=10.0, demand_1=100, price_point_2=12.0, demand_2=70)
        self.assertEqual(ped, -1.5)

    def test_nexs_get_paywall_performance_stats(self):
        stats = self.engine.get_paywall_performance_stats()
        self.assertIn("total_trials", stats)
        self.assertIn("variants", stats)


class TestNextGenMasterOrchestrator(unittest.TestCase):
    """Integration Test for Next-Gen Master Orchestrator"""

    def setUp(self):
        self.orchestrator = NextGenMasterOrchestrator()

    def test_master_orchestrator_full_lifecycle(self):
        res = self.orchestrator.process_full_subscriber_lifecycle(
            user_id="usr_full_vip",
            country_code="DE",
            device_id="dev_watch_de",
            fiat_amount=29.99,
            currency="EUR"
        )
        self.assertEqual(res["status"], "NEXTGEN_PIPELINE_SUCCESS")
        self.assertIn("nexs_offering", res)
        self.assertIn("xfin_settlement", res)
        self.assertIn("aura_underwrite", res)
        self.assertIn("mint_minting", res)
        self.assertIn("grid_consensus", res)
        self.assertIn("pulse_telemetry", res)


if __name__ == "__main__":
    unittest.main()
