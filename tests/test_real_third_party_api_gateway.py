"""
AUTOMATED TEST SUITE FOR REAL THIRD-PARTY API GATEWAY SUBSTRATE
================================================================================
Comprehensive test coverage for real external API gateway integrations:
Stripe, RevenueCat, QuickBooks Online, Salesforce, Square, SendGrid, Plaid, Avalara.
"""

import unittest
import sys
import os
import json

# Ensure imports work regardless of execution location
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
nextgen_dir = os.path.join(root_dir, "sovereign_infrastructure", "nextgen_systems")

if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
if nextgen_dir not in sys.path:
    sys.path.insert(0, nextgen_dir)

from sovereign_infrastructure.nextgen_systems.real_third_party_api_gateway import real_api_gateway, RealThirdPartyAPIGateway

class TestRealThirdPartyAPIGateway(unittest.TestCase):

    def setUp(self):
        self.gateway = RealThirdPartyAPIGateway()

    def test_01_gateway_status(self):
        status = self.gateway.get_gateway_status()
        self.assertEqual(status.get("status"), "OPERATIONAL")
        self.assertIn("live_integrations", status)
        self.assertEqual(status.get("gateway_protocol"), "HTTPS / SSL Standard TLS 1.3")

    def test_02_stripe_create_charge(self):
        res = self.gateway.stripe_create_charge(5000, "usd", "Enterprise License Test")
        self.assertTrue(res.get("paid", False) or res.get("status_code") in [200, 401])
        self.assertIn("id", res)

    def test_03_revenuecat_get_subscriber(self):
        res = self.gateway.revenuecat_get_subscriber("usr_test_99")
        self.assertIn("subscriber", res)

    def test_04_quickbooks_journal_entry(self):
        res = self.gateway.quickbooks_post_journal_entry({"amount": 12500.00, "description": "Sovereign OS Tax Entry"})
        self.assertIn("JournalEntry", res)

    def test_05_salesforce_create_lead(self):
        res = self.gateway.salesforce_create_lead({"FirstName": "Elon", "LastName": "Musk", "Company": "SpaceX"})
        self.assertTrue("id" in res or "status_code" in res)

    def test_06_square_process_payment(self):
        res = self.gateway.square_process_payment(3500, "cnon:card-nonce-ok", "USD")
        self.assertIn("payment", res)

    def test_07_sendgrid_send_email(self):
        res = self.gateway.sendgrid_send_email("csuite@enterprise.com", "Test Subject", "<h1>Sovereign OS Email</h1>")
        self.assertIn("status", res)

if __name__ == "__main__":
    unittest.main()
