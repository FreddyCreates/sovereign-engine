"""
Automated test suite for Sovereign OS Enterprise Billing Engine & Omnichannel Ad Aggregator:
- Enterprise Contract Billing Lifecycle Engine
- Multi-Tenant Revenue Split Engine (Double-entry GL check)
- High-Frequency Usage Metering Aggregator
- Automated Tax Remittance Engine
- Post-Quantum ZK Proof Registry
- Multi-Platform Ad Network Aggregator
- Programmatic Ad Bidding Engine
- Multi-Touch Attribution Engine (W-Shaped, First-Touch, Last-Touch, Linear)
"""

import unittest
from sovereign_infrastructure.nextgen_systems.sovereign_enterprise_billing_marketplace_engine import (
    EnterpriseContractBillingLifecycleEngine,
    MultiTenantRevenueSplitEngine,
    HighFrequencyUsageMeteringAggregator,
    AutomatedTaxWithholdingRemittanceEngine,
    PostQuantumZKProofRegistry
)
from sovereign_infrastructure.nextgen_systems.sovereign_omnichannel_ad_network_aggregator import (
    MultiPlatformAdNetworkAggregator,
    ProgrammaticAdBiddingEngine,
    MultiTouchAttributionEngine
)


class TestEnterpriseBillingAndAdAggregator(unittest.TestCase):

    def setUp(self):
        self.billing_engine = EnterpriseContractBillingLifecycleEngine()
        self.split_engine = MultiTenantRevenueSplitEngine()
        self.usage_meter = HighFrequencyUsageMeteringAggregator()
        self.tax_engine = AutomatedTaxWithholdingRemittanceEngine()
        self.zk_registry = PostQuantumZKProofRegistry()
        self.ad_aggregator = MultiPlatformAdNetworkAggregator()
        self.bidding_engine = ProgrammaticAdBiddingEngine()
        self.attribution_engine = MultiTouchAttributionEngine()

    def test_enterprise_contract_billing_calculator(self):
        res = self.billing_engine.calculate_contract_billing(1000.0, 10000, 15000, 0.05, "ENTERPRISE_VIP")
        self.assertEqual(res["overage_units"], 5000)
        self.assertEqual(res["overage_charge"], 250.0)
        self.assertEqual(res["subtotal"], 1250.0)
        self.assertEqual(res["discount_amount"], 250.0)
        self.assertEqual(res["total_due"], 1000.0)
        self.assertEqual(res["status"], "BILLED_AND_CALCULATED")

    def test_multi_tenant_revenue_split_balancing(self):
        res = self.split_engine.calculate_revenue_split(1000.0, 0.05, 0.10, 0.85)
        self.assertTrue(res["is_balanced"])
        self.assertEqual(res["platform_fee"], 50.0)
        self.assertEqual(res["affiliate_payout"], 100.0)
        self.assertEqual(res["creator_payout"], 850.0)
        self.assertEqual(res["status"], "REVENUE_SPLIT_BALANCED")

    def test_usage_metering_aggregator(self):
        r1 = self.usage_meter.log_usage_event("tenant_apex", "api_calls", 100)
        r2 = self.usage_meter.log_usage_event("tenant_apex", "api_calls", 250)
        self.assertEqual(r2["cumulative_units"], 350)
        self.assertEqual(r2["status"], "EVENT_LOGGED")

    def test_automated_tax_remittance(self):
        res = self.tax_engine.calculate_tax_remittance(1000.0, "US", "CA")
        self.assertEqual(res["tax_amount"], 87.50)
        self.assertEqual(res["total_with_tax"], 1087.50)
        self.assertEqual(res["status"], "TAX_CALCULATED_AND_REMITTED")

    def test_post_quantum_zk_proof_registry(self):
        res = self.zk_registry.register_zk_proof("sender_01", "recipient_02", 5000.0, "dilithium_3_valid_proof_hex_999")
        self.assertEqual(res["status"], "PROOF_REGISTERED")
        self.assertTrue(res["proof_record"]["is_valid"])

    def test_multi_platform_ad_network_aggregator(self):
        campaigns = [
            {"spend_usd": 1000.0, "revenue_usd": 4000.0, "clicks": 500, "impressions": 10000},
            {"spend_usd": 2000.0, "revenue_usd": 10000.0, "clicks": 1200, "impressions": 25000}
        ]
        res = self.ad_aggregator.aggregate_ad_networks(campaigns)
        self.assertEqual(res["total_spend_usd"], 3000.0)
        self.assertEqual(res["total_revenue_usd"], 14000.0)
        self.assertEqual(res["overall_roas"], 4.67)

    def test_programmatic_ad_bidding(self):
        res = self.bidding_engine.calculate_optimal_bid(target_roas=4.0, conversion_rate=0.05, avg_order_value=200.0)
        self.assertEqual(res["calculated_bid_usd"], 2.50)
        self.assertEqual(res["status"], "OPTIMAL_BID_CALCULATED")

    def test_multi_touch_attribution_models(self):
        touchpoints = [{"name": "Google Ad"}, {"name": "Meta Retargeting"}, {"name": "Email Newsletter"}]
        res = self.attribution_engine.calculate_attribution(touchpoints, 1000.0, "W_SHAPED")
        self.assertEqual(res["status"], "ATTRIBUTION_COMPLETED")
        self.assertEqual(len(res["attributed_splits"]), 3)
        total_attr = sum(s["attributed_revenue"] for s in res["attributed_splits"])
        self.assertAlmostEqual(total_attr, 1000.0, places=1)


if __name__ == "__main__":
    unittest.main()
