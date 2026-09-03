"""
Automated test suite for Sovereign OS Business Document & Payment Suite:
- Estimate & Quote Builder
- Pro-Forma & Final Invoice Engine (with ZK Dilithium Proofs)
- Payment Receipt & Tax Proof Engine
- Technical Spec & Statement of Work (SOW) Synthesizer
- Digital Product Fulfillment Manifest
- Legal Contract & MSA Synthesizer
"""

import unittest
from sovereign_infrastructure.nextgen_systems.sovereign_business_document_suite import (
    EstimateAndQuoteBuilder,
    InvoiceAndReceiptEngine,
    TechnicalSpecAndSOWSynthesizer,
    DigitalProductFulfillmentManifest,
    LegalContractAndMSASynthesizer
)


class TestBusinessDocumentSuite(unittest.TestCase):

    def setUp(self):
        self.estimate_builder = EstimateAndQuoteBuilder()
        self.invoice_engine = InvoiceAndReceiptEngine()
        self.spec_synthesizer = TechnicalSpecAndSOWSynthesizer()
        self.fulfillment = DigitalProductFulfillmentManifest()
        self.legal_contract = LegalContractAndMSASynthesizer()

    def test_estimate_builder(self):
        items = [{"name": "Enterprise SaaS Seat", "price": 100.0, "quantity": 10}]
        est = self.estimate_builder.create_estimate("Global Corp", "billing@global.com", items, discount_pct=10.0)
        self.assertEqual(est["status"], "DRAFT_SENT_FOR_APPROVAL")
        self.assertEqual(est["subtotal"], 1000.0)
        self.assertEqual(est["discount_amount"], 100.0)
        self.assertEqual(est["total_due"], 900.0)

    def test_invoice_and_receipt_flow(self):
        items = [{"name": "Custom AI Agent Engine", "price": 10000.0, "quantity": 1}]
        inv = self.invoice_engine.create_invoice("Global Corp", "billing@global.com", items, tax_rate_pct=10.0)
        self.assertEqual(inv["status"], "UNPAID_SENT")
        self.assertEqual(inv["subtotal"], 10000.0)
        self.assertEqual(inv["tax_amount"], 1000.0)
        self.assertEqual(inv["total_due"], 11000.0)
        self.assertTrue(inv["zk_dilithium_signature"].startswith("dilithium_3_inv_"))

        rec = self.invoice_engine.generate_payment_receipt(inv["invoice_id"], 11000.0, "dilithium_zk")
        self.assertEqual(rec["status"], "PAID_AND_RECEIPTED")
        self.assertTrue(rec["zk_settlement_proof"].startswith("dilithium_3_settle_"))

    def test_technical_spec_sow_synthesis(self):
        milestones = [{"title": "Phase 1 Architecture", "payout": 15000.0}, {"title": "Phase 2 Deployment", "payout": 25000.0}]
        sow = self.spec_synthesizer.synthesize_sow_spec("Banking Modernization", "Full migration of legacy COBOL to ZK Rail", milestones)
        self.assertEqual(sow["status"], "SPEC_SYNTHESIZED")
        self.assertEqual(sow["total_contract_value"], 40000.0)
        self.assertIn("# Statement of Work: Banking Modernization", sow["document_markdown"])

    def test_digital_product_fulfillment_manifest(self):
        ful = self.fulfillment.generate_fulfillment_manifest("Sovereign OS Pro Enterprise Key", "licensee@corp.org")
        self.assertEqual(ful["status"], "FULFILLED_AND_DELIVERED")
        self.assertTrue(ful["license_key"].startswith("SOV-"))
        self.assertIn("dl.sovereign.io", ful["download_url"])

    def test_legal_msa_contract_synthesis(self):
        msa = self.legal_contract.generate_msa_contract("Sovereign OS Inc.", "Acme Corp")
        self.assertEqual(msa["status"], "AWAITING_E_SIGNATURE")
        self.assertIn("Master Service Agreement between Sovereign OS Inc. and Acme Corp", msa["contract_title"])


if __name__ == "__main__":
    unittest.main()
