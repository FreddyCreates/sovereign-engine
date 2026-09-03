"""
TEST SUITE FOR SOVEREIGN AUTONOMOUS BUSINESS LIFECYCLE AGENT SWARM
==================================================================================
Tests:
1. Real-Time Market Research Scanner
2. Autonomous Product & Ad Campaign Generator
3. Storefront & Account Provisioner (RevenueCat, QuickBooks COA, Salesforce CRM, ZK Wallet)
4. Full Business Lifecycle Agent Swarm Execution (ROAS, Zero Float Drift, Cash Sweep)
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sovereign_infrastructure.nextgen_systems.sovereign_autonomous_business_lifecycle_agent_swarm import (
    AutonomousMarketResearcher,
    AutonomousProductAndAdCreator,
    AutonomousStoreAndAccountProvisioner,
    AutonomousSalesAndLifecycleRunner,
    business_lifecycle_agent_swarm
)


class TestSovereignAutonomousBusinessLifecycleAgentSwarm(unittest.TestCase):

    def setUp(self):
        self.researcher = AutonomousMarketResearcher()
        self.creator = AutonomousProductAndAdCreator()
        self.provisioner = AutonomousStoreAndAccountProvisioner()
        self.runner = AutonomousSalesAndLifecycleRunner()

    def test_01_market_research_scanner(self):
        res = self.researcher.scan_market_opportunity("ai_copilot_saas")
        self.assertEqual(res["niche_keyword"], "ai_copilot_saas")
        self.assertGreater(res["market_demand_index"], 90)
        self.assertEqual(len(res["competitors_analyzed"]), 3)
        self.assertEqual(res["opportunity_score"], "HIGH_CONVERSION_OPPORTUNITY")

    def test_02_product_and_ad_creator(self):
        campaign = self.creator.create_product_and_ad_campaign("ai_copilot_saas")
        self.assertEqual(campaign["niche_keyword"], "ai_copilot_saas")
        self.assertEqual(len(campaign["products_generated"]), 2)
        self.assertEqual(len(campaign["ad_creatives_generated"]), 2)
        self.assertIn("paywall_id", campaign["revenuecat_paywall_ast"])

    def test_03_store_and_account_provisioner(self):
        stack = self.provisioner.provision_full_business_stack("Sovereign OS Inc.")
        self.assertEqual(stack["company_name"], "Sovereign OS Inc.")
        self.assertTrue(stack["revenuecat_app_id"].startswith("app_rc_"))
        self.assertTrue(stack["revenuecat_api_keys"]["secret_v2_key"].startswith("rcb_"))
        self.assertEqual(len(stack["quickbooks_gl_chart_of_accounts"]), 5)
        self.assertEqual(len(stack["salesforce_crm_pipeline_stages"]), 4)
        self.assertTrue(stack["zk_dilithium_merchant_wallet"].startswith("0x"))

    def test_04_full_autonomous_business_lifecycle_runner(self):
        res = self.runner.run_full_autonomous_business_cycle(
            niche_keyword="autonomous_business_os",
            company_name="Autonomous Ventures Inc.",
            initial_ad_budget_usd=1000.0
        )
        self.assertEqual(res["company_name"], "Autonomous Ventures Inc.")
        self.assertEqual(res["stage_4_sales_and_lifecycle_performance"]["gross_subscription_sales_usd"], 4850.0)
        self.assertEqual(res["stage_4_sales_and_lifecycle_performance"]["autonomic_net_profit_usd"], 3598.70)
        self.assertEqual(res["stage_4_sales_and_lifecycle_performance"]["swept_to_5percent_cash_reserve_usd"], 1799.35)
        self.assertTrue(res["stage_4_sales_and_lifecycle_performance"]["zero_float_drift_validated"])

    def test_05_singleton_instance_execution(self):
        res = business_lifecycle_agent_swarm.run_full_autonomous_business_cycle()
        self.assertEqual(res["stage_4_sales_and_lifecycle_performance"]["status"], "BUSINESS_CYCLE_RUNNING_AUTONOMOUSLY")

    def test_06_autonomic_self_healing_ast(self):
        from sovereign_infrastructure.nextgen_systems.sovereign_autonomous_business_lifecycle_agent_swarm import autonomic_ast_engine
        heal = autonomic_ast_engine.heal_runtime_exception("Traceback (most recent call last): SchemaMismatchError", "banking_engine")
        self.assertEqual(heal["status"], "AUTONOMIC_CODE_MUTATION_APPLIED_ZERO_DOWNTIME")
        self.assertEqual(heal["downtime_seconds"], 0.0)

    def test_07_zk_proof_ai_inference(self):
        from sovereign_infrastructure.nextgen_systems.sovereign_autonomous_business_lifecycle_agent_swarm import zk_ai_inference_engine
        zk = zk_ai_inference_engine.execute_zk_proven_inference("Summarize financial statements")
        self.assertEqual(zk["verification_status"], "ZK_STARK_PROOF_VALIDATED_ON_CHAIN")
        self.assertTrue(zk["zk_stark_proof_hash"].startswith("zk_proof_stark_sp1_"))

    def test_08_customer_center_ai_retention_mesh(self):
        from sovereign_infrastructure.nextgen_systems.sovereign_autonomous_business_lifecycle_agent_swarm import customer_center_retention_mesh
        ret = customer_center_retention_mesh.evaluate_churn_risk_and_intervene("user_sub_8819", app_open_frequency_weekly=1)
        self.assertEqual(ret["risk_level"], "HIGH_CHURN_RISK")
        self.assertTrue(ret["ai_intervention"]["intervention_triggered"])


if __name__ == "__main__":
    unittest.main()
