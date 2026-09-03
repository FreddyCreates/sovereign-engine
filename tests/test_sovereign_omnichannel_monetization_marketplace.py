"""
Automated test suite for Sovereign OS Omnichannel Monetization & Marketplace Engine:
- Pay Link & Pay App Generator
- Sellable Monetized API Endpoints
- Nested In-App & Video Game Virtual Marketplace Substrate
- Public Storefront & Website Host Builder
- Digital Ad Revenue & Marketing Attribution GL Sync
"""

import unittest
from sovereign_infrastructure.nextgen_systems.sovereign_omnichannel_monetization_marketplace import (
    PayLinkAndPayAppGenerator,
    NestedInAppMarketplaceEngine,
    PublicStorefrontAndProfileBuilder,
    AdRevenueAndMarketingAttributionHub
)


class TestOmnichannelMonetizationMarketplace(unittest.TestCase):

    def setUp(self):
        self.paylink_gen = PayLinkAndPayAppGenerator()
        self.nested_mkt = NestedInAppMarketplaceEngine()
        self.storefront = PublicStorefrontAndProfileBuilder()
        self.ad_hub = AdRevenueAndMarketingAttributionHub()

    def test_create_pay_link(self):
        link = self.paylink_gen.create_pay_link("E-Book & Video Masterclass Bundle", 39.00, "USD", "DIGITAL_PRODUCT")
        self.assertTrue(link["pay_url"].startswith("https://pay.sovereign.io/l/"))
        self.assertIn("<iframe", link["embed_code"])
        self.assertEqual(link["price"], 39.00)

    def test_create_sellable_api_endpoint(self):
        api_spec = self.paylink_gen.create_sellable_api_endpoint("Premium Financial OCR API", "https://api.internal.com/ocr", 15.00, 1000)
        self.assertTrue(api_spec["monetized_gateway_url"].startswith("https://api.sovereign.io/v1/monetized/"))
        self.assertTrue(api_spec["dilithium_zk_gated"])
        self.assertEqual(api_spec["price_per_1000_calls"], 15.00)

    def test_nested_in_game_marketplace_flow(self):
        mkt = self.nested_mkt.create_marketplace("Cyber Strike 2026", "VIDEO_GAME_MARKETPLACE")
        m_id = mkt["marketplace_id"]

        item = self.nested_mkt.add_nested_item(m_id, "Quantum Laser Rifle Skin", 14.99, "GAME_SKIN", 1500)
        i_id = item["item_id"]
        self.assertEqual(item["price_usd"], 14.99)
        self.assertEqual(item["sub_entitlement_key"], "in_app_quantum_laser_rifle_skin")

        receipt = self.nested_mkt.purchase_nested_item(i_id, "player_gamer_777", "dilithium_zk")
        self.assertEqual(receipt["status"], "PURCHASED_AND_DELIVERED")
        self.assertTrue(receipt["zk_proof"].startswith("dilithium_3_mkt_"))
        self.assertEqual(receipt["sub_entitlement_granted"], "in_app_quantum_laser_rifle_skin")

    def test_build_storefront_website(self):
        site = self.storefront.build_storefront_website("prof_default", "https://cyberstore.io")
        self.assertEqual(site["status"], "HOSTED_AND_LIVE")
        self.assertEqual(site["public_url"], "https://cyberstore.io")
        self.assertIn("NESTED_IN_GAME_MARKETPLACE", site["sections"])

    def test_track_ad_campaign_revenue(self):
        res = self.ad_hub.track_ad_campaign_revenue("TikTok Viral Launch", "TikTok Ads", 2000.0, 12000.0)
        self.assertEqual(res["net_profit_usd"], 10000.0)
        self.assertEqual(res["roas_multiplier"], 6.0)
        self.assertEqual(res["quickbooks_gl_entry"]["credit_account"], "4100 Digital Ad & Marketing Revenue")
        self.assertEqual(res["quickbooks_gl_entry"]["status"], "AUTO_POSTED_TO_GL")


if __name__ == "__main__":
    unittest.main()
