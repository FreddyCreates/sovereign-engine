"""
Automated test suite for Sovereign OS Business Profile & Omnichannel Store Orchestrator:
- Business Profile Manager (Manual creation & AI Agent auto-synthesis)
- Omnichannel Product & Service Catalog Manager
- Direct Charge Engine (RevenueCat entitlements + ZK Dilithium Settlement Rail)
- Omnichannel Multi-Store Push Engine (Shopify, WooCommerce, Amazon, eBay, RevenueCat)
"""

import unittest
from sovereign_infrastructure.nextgen_systems.business_profile_and_store_orchestrator import (
    BusinessProfileManager,
    OmnichannelProductCatalogManager,
    OmnichannelMultiStorePushEngine,
    DirectChargeEngine
)


class TestBusinessProfileAndStoreOrchestrator(unittest.TestCase):

    def setUp(self):
        self.profile_mgr = BusinessProfileManager()
        self.catalog_mgr = OmnichannelProductCatalogManager()
        self.push_engine = OmnichannelMultiStorePushEngine()
        self.charge_engine = DirectChargeEngine()

    def test_default_profile_exists(self):
        prof = self.profile_mgr.get_profile("prof_default")
        self.assertEqual(prof["company_name"], "Apex Sovereign Labs Inc.")
        self.assertEqual(prof["status"], "ACTIVE")
        self.assertTrue(prof["dilithium_wallet_address"].startswith("dilithium_3_"))

    def test_agent_autobuild_profile(self):
        prof = self.profile_mgr.agent_autobuild_profile("Build business profile for CyberNet AI Systems")
        self.assertEqual(prof["company_name"], "CyberNet AI Systems")
        self.assertEqual(prof["status"], "ACTIVE")
        self.assertIn("cybernetaisystems", prof["website"])

    def test_create_and_list_products(self):
        prod = self.catalog_mgr.create_product(
            title="Custom Enterprise AI Agent Plugin",
            price=299.00,
            product_type="MONTHLY_SAAS",
            revenuecat_entitlement="sovereign_enterprise"
        )
        self.assertEqual(prod["price"], 299.00)
        self.assertEqual(prod["revenuecat_entitlement"], "sovereign_enterprise")
        self.assertGreaterEqual(len(self.catalog_mgr.list_products()), 4)

    def test_push_to_all_stores(self):
        prods = self.catalog_mgr.list_products()
        p_id = prods[0]["product_id"]
        res = self.push_engine.push_to_all_stores(p_id)
        self.assertEqual(res["status"], "PUSH_SUCCESS")
        self.assertEqual(len(res["stores_synced"]), 5)
        store_names = [s["store"] for s in res["stores_synced"]]
        self.assertIn("Shopify Storefront", store_names)
        self.assertIn("Amazon Seller Central", store_names)
        self.assertIn("RevenueCat Paywall AST", store_names)

    def test_charge_customer_direct(self):
        prods = self.catalog_mgr.list_products()
        p_id = prods[0]["product_id"]
        res = self.charge_engine.charge_customer_direct("cfo@enterprise.com", p_id, "dilithium_zk")
        self.assertEqual(res["status"], "CHARGED_AND_SETTLED")
        self.assertEqual(res["platform_fee_usd"], 0.00)
        self.assertTrue(res["zk_proof"].startswith("dilithium_3_zk_"))
        self.assertTrue(res["revenuecat_entitlement_granted"])
        self.assertTrue(res["quickbooks_gl_posted"])


if __name__ == "__main__":
    unittest.main()
