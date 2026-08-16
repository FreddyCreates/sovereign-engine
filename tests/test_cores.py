"""
Enterprise Automated Testing Suite for Sovereign Substrate Core Engines
Executes unit and integration tests across all 6 decoupled Core Engines.
"""

import sys
import os
import unittest
import hmac
import hashlib

# Path setup to import sovereign_infrastructure
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "sovereign_infrastructure"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "sovereign_infrastructure", "cores"))

from billing_core import RevenueCatBillingCore
from paywall_core import PaywallMutationCore
from retention_core import CustomerCenterRetentionCore
from app_builder_core import GeminiAppBuilderCore
from iot_telemetry_core import IoTHardwareTelemetryCore
from ppp_localization_core import PPPLocalizationCore

class TestSovereignCoreEngines(unittest.TestCase):

    def setUp(self):
        self.billing = RevenueCatBillingCore("test_secret_123")
        self.paywall = PaywallMutationCore()
        self.retention = CustomerCenterRetentionCore()
        self.app_builder = GeminiAppBuilderCore()
        self.iot = IoTHardwareTelemetryCore()
        self.ppp = PPPLocalizationCore()

    def test_core1_billing_signature_verification(self):
        payload = b'{"event":{"type":"INITIAL_PURCHASE"}}'
        valid_sig = hmac.new(b"test_secret_123", payload, hashlib.sha256).hexdigest()
        
        self.assertTrue(self.billing.verify_webhook_signature(payload, valid_sig))
        self.assertFalse(self.billing.verify_webhook_signature(payload, "invalid_sig"))

    def test_core1_billing_lifecycle_event(self):
        res = self.billing.process_lifecycle_event("user_test", "INITIAL_PURCHASE", "monthly_pro", 19.99)
        self.assertEqual(res["status"], "PROCESSED")
        self.assertEqual(res["mrr_delta"], 19.99)

    def test_core2_paywall_mutation(self):
        res = self.paywall.compute_coherence_and_mutate(scroll_depth=0.9, engagement_score=0.95)
        self.assertEqual(res["mutated_variant"], "GLASSMORPHIC_HERO_TRIAL")
        self.assertGreater(res["kuramoto_R"], 0.618)

    def test_core3_retention_interception(self):
        res = self.retention.intercept_cancellation("user_test", "TOO_EXPENSIVE")
        self.assertEqual(res["status"], "RETAINED")
        self.assertEqual(res["customer_center_promo"]["discount_percentage"], 50)

    def test_core4_app_builder(self):
        res = self.app_builder.synthesize_app("Fitness AI Coach", ["App Store", "Google Play"])
        self.assertEqual(res["status"], "SYNTHESIZED")
        self.assertEqual(res["app_name"], "Fitness App")

    def test_core5_iot_telemetry(self):
        res = self.iot.sync_hardware_entitlements("WATCH_01", "WEAR_OS_WATCH", ["pro_access"])
        self.assertTrue(res["hardware_unlocked"])

    def test_core6_ppp_localization(self):
        res = self.ppp.compute_local_price(19.99, "BR")
        self.assertEqual(res["currency"], "BRL")
        self.assertEqual(res["local_price"], 9.0)

if __name__ == "__main__":
    unittest.main()
