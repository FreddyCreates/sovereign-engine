"""
AUTOMATED TEST SUITE FOR AGENTIC GRANTS & OMNICHANNEL EMAIL ENGINE
================================================================================
Exhaustive unit test suite verifying Real-World Passport Perks, Agentic Grant Auto-Filer,
Omnichannel Email/SMS Parsing (Gmail, Outlook, Yahoo, Apple Mail, SMS Logs),
and QuickBooks GL / Salesforce CRM zero-float-drift dispatchers.
"""

import unittest
import sys
import os
import json
from decimal import Decimal

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
nextgen_dir = os.path.join(root_dir, "sovereign_infrastructure", "nextgen_systems")

if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
if nextgen_dir not in sys.path:
    sys.path.insert(0, nextgen_dir)

from sovereign_infrastructure.nextgen_systems.sovereign_agentic_grants_and_email_ingest_engine import (
    passport_perks_engine,
    agentic_grant_filer,
    omnichannel_email_engine,
    quickbooks_gl_dispatcher,
    salesforce_crm_dispatcher
)


class TestAgenticGrantsAndEmailEngine(unittest.TestCase):

    def test_01_claim_cloud_credits_perk(self):
        res = passport_perks_engine.claim_cloud_credits("rnft_rc_9981", provider="AWS_GCP")
        self.assertEqual(res["status"], "CREDITS_PROVISIONED_SUCCESSFULLY")
        self.assertEqual(res["total_cloud_value_usd"], 350000.0)

    def test_02_mint_airport_lounge_pass_perk(self):
        res = passport_perks_engine.mint_airport_lounge_pass("rnft_rc_9981", passenger_name="Medin Founder")
        self.assertEqual(res["status"], "PASS_ACTIVE_AND_VERIFIED")
        self.assertEqual(res["valid_lounges_count"], 1300)

    def test_03_generate_rd_tax_filing_perk(self):
        res = passport_perks_engine.generate_rd_tax_filing("rnft_rc_9981", annual_rd_spend=500000.0)
        self.assertEqual(res["status"], "DOSSIER_READY_FOR_CPAS")
        self.assertEqual(res["estimated_tax_credit_usd"], 70000.0)

    def test_04_auto_fill_grant_application(self):
        res = agentic_grant_filer.auto_fill_grant_application(
            grant_id="grant-sbir-sttr",
            mrr=148920.0,
            company_name="Sovereign OS Inc."
        )
        self.assertEqual(res["application_status"], "AUTO_FILLED_AND_SUBMITTED")
        self.assertGreaterEqual(res["approval_probability_pct"], 90.0)

    def test_05_parse_omnichannel_email_invoice(self):
        email_sample = "Hello Team, Please find attached Invoice #INV-2026-99 for $12,500.00 due in 30 days."
        res = omnichannel_email_engine.parse_omnichannel_email(email_sample, channel="Microsoft Outlook", sender="billing@vendor.com")
        self.assertEqual(res["entity_type"], "ACCOUNTS_PAYABLE_INVOICE")
        self.assertEqual(res["extracted_data"]["amount_usd"], 12500.0)
        self.assertEqual(res["extracted_data"]["invoice_number"], "INV-2026-99")
        self.assertTrue(res["zero_float_drift_guarantee"])
        self.assertTrue(res["dispatch_result"]["zero_float_drift_verified"])

    def test_06_parse_gmail_sales_quote_salesforce_dispatch(self):
        email_sample = "Hi, here is Sales Quote #QUO-8821 for $45,000.00 valid for 14 days."
        res = omnichannel_email_engine.parse_omnichannel_email(email_sample, channel="Gmail", sender="sales@enterprise.com")
        self.assertEqual(res["channel"], "Gmail")
        self.assertEqual(res["entity_type"], "SALES_QUOTE")
        self.assertEqual(res["action_taken"], "AUTO_DISPATCHED_TO_SALESFORCE_CRM_ZERO_FLOAT_DRIFT")
        self.assertEqual(res["dispatch_result"]["sobject_type"], "Opportunity")
        self.assertEqual(res["dispatch_result"]["amount_decimal"], "45000.00")

    def test_07_parse_apple_mail_customer_estimate(self):
        email_sample = "Attached is Customer Estimate #EST-4402 for $8,200.00 project work."
        res = omnichannel_email_engine.parse_omnichannel_email(email_sample, channel="iCloud Mail", sender="estimates@buildco.com")
        self.assertEqual(res["channel"], "Apple Mail")
        self.assertEqual(res["entity_type"], "CUSTOMER_ESTIMATE")
        self.assertTrue(res["dispatch_result"]["zero_float_drift_verified"])

    def test_08_parse_sms_project_milestone(self):
        sms_sample = "SMS Log: Project Titan Phase 1 is 80% complete."
        res = omnichannel_email_engine.parse_omnichannel_email(sms_sample, channel="SMS Logs", sender="+15550192831")
        self.assertEqual(res["channel"], "SMS Logs")
        self.assertEqual(res["entity_type"], "PROJECT_MILESTONE")
        self.assertEqual(res["extracted_data"]["completion_pct"], 80)

    def test_09_parse_yahoo_workspace_provision(self):
        email_sample = "Workspace Enterprise-Cluster created with 50 seats for your organization."
        res = omnichannel_email_engine.parse_omnichannel_email(email_sample, channel="Yahoo Mail", sender="admin@yahoo.com")
        self.assertEqual(res["channel"], "Yahoo Mail")
        self.assertEqual(res["entity_type"], "WORKSPACE_PROVISION")
        self.assertEqual(res["extracted_data"]["seat_count"], 50)

    def test_10_parse_financial_analysis_telemetry(self):
        email_sample = "Quarterly Financial Analysis: ARR report shows $1,800,000 USD revenue with 88% gross margin."
        res = omnichannel_email_engine.parse_omnichannel_email(email_sample, channel="Gmail", sender="analyst@finance.com")
        self.assertEqual(res["entity_type"], "FINANCIAL_ANALYSIS")
        self.assertEqual(res["action_taken"], "INDEXED_IN_FINANCIAL_KNOWLEDGE_BASE")

    def test_11_zero_float_drift_precision_verification(self):
        qb_res = quickbooks_gl_dispatcher.dispatch_invoice("INV-DEC-1", "12500.005", "VendorCorp")
        self.assertEqual(qb_res["float_drift"], 0.0)
        self.assertTrue(qb_res["zero_float_drift_verified"])
        self.assertEqual(qb_res["debit_amount_decimal"], qb_res["credit_amount_decimal"])

        sf_res = salesforce_crm_dispatcher.dispatch_quote("QUO-DEC-1", Decimal("45000.00"), "ClientCorp")
        self.assertTrue(sf_res["zero_float_drift_verified"])
        self.assertEqual(sf_res["amount_decimal"], "45000.00")


if __name__ == "__main__":
    unittest.main()
