"""
TEST SUITE FOR SOVEREIGN ISO 20022, SWIFT MT103, AND FEDNOW BANKING ENGINE
==================================================================================
Tests:
1. ISO 20022 pacs.008 XML Message Generation
2. ISO 20022 camt.053 XML Statement Generation
3. SWIFT MT103 Telegraphic Wire Transfer
4. FedNow RTP Instant Payment Processing
5. FIX 5.0 Order Execution
6. Plaid Bank Token Verification
"""

import sys
import os
import unittest
from decimal import Decimal

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sovereign_infrastructure.nextgen_systems.sovereign_iso20022_swift_banking_engine import (
    SovereignBankingEngine,
    sovereign_banking_engine
)


class TestSovereignISO20022SwiftBankingEngine(unittest.TestCase):

    def setUp(self):
        self.engine = SovereignBankingEngine()

    def test_01_pacs_008_xml_generation(self):
        xml_res = self.engine.generate_pacs_008(
            sender_bic="BOFAUS3NXXX",
            receiver_bic="CHASUS33XXX",
            amount=Decimal("100000.00"),
            currency="USD",
            debtor_acct="US89BOFA1234567890",
            creditor_acct="US44CHAS0987654321"
        )
        self.assertIn("pacs.008.001.10", xml_res)
        self.assertIn("BOFAUS3NXXX", xml_res)
        self.assertIn("100000.00", xml_res)

    def test_02_camt_053_xml_statement_generation(self):
        xml_res = self.engine.generate_camt_053(
            account_id="US89BOFA1234567890",
            balance=Decimal("250000.00"),
            currency="USD",
            transactions=[
                {"amount": Decimal("10000.00")},
                {"amount": Decimal("-2500.00")}
            ]
        )
        self.assertIn("camt.053.001.08", xml_res)
        self.assertIn("250000.00", xml_res)

    def test_03_swift_mt103_wire(self):
        wire_res = self.engine.generate_mt103(
            sender_bic="BOFAUS3NXXX",
            receiver_bic="CHASUS33XXX",
            amount=Decimal("250000.00"),
            currency="USD",
            date="260831",
            orderer_acct="US89BOFA1234567890",
            beneficiary_acct="US44CHAS0987654321"
        )
        self.assertIn("{1:F01BOFAUS3NXXX", wire_res)
        self.assertIn("{2:I103CHASUS33XXX", wire_res)
        self.assertIn(":32A:260831USD250000.00", wire_res)

    def test_04_fednow_rtp(self):
        success = self.engine.process_fednow_rtp(
            sender_routing="021000021",
            receiver_routing="121000358",
            amount=Decimal("50000.00")
        )
        self.assertTrue(success)

    def test_05_fix_5_0_order(self):
        fix_msg = self.engine.execute_fix_5_0_order(
            symbol="NVDA",
            side="BUY",
            qty=Decimal("100"),
            price=Decimal("128.50")
        )
        self.assertIn("8=FIXT.1.1", fix_msg)
        self.assertIn("35=D", fix_msg)
        self.assertIn("55=NVDA", fix_msg)

    def test_06_plaid_token_verification(self):
        result = sovereign_banking_engine.verify_plaid_token("public-sandbox-881920-alpha")
        self.assertTrue(result)
        self.assertFalse(sovereign_banking_engine.verify_plaid_token("short"))

    def test_07_pacs_002_payment_status_report(self):
        xml_out = sovereign_banking_engine.generate_pacs_002("MSG-ORIG-9912", "ACTC")
        self.assertIn("pacs.002.001.12", xml_out)
        self.assertIn("MSG-ORIG-9912", xml_out)
        self.assertIn("ACTC", xml_out)

    def test_08_pacs_004_payment_return(self):
        xml_out = sovereign_banking_engine.generate_pacs_004("MSG-ORIG-9912", "NARR")
        self.assertIn("pacs.004.001.11", xml_out)
        self.assertIn("MSG-ORIG-9912", xml_out)

    def test_09_camt_054_notification(self):
        xml_out = sovereign_banking_engine.generate_camt_054("GB33BUKB20201555555555", Decimal("50000.00"), "USD")
        self.assertIn("camt.054.001.08", xml_out)
        self.assertIn("GB33BUKB20201555555555", xml_out)

    def test_10_swift_gpi_uetr(self):
        gpi = sovereign_banking_engine.generate_swift_gpi_uetr()
        self.assertIn("swift_gpi_uetr", gpi)
        self.assertIn(":121:", gpi["swift_gpi_header_tag_121"])

    def test_11_ebics_3_0_payload(self):
        ebics = sovereign_banking_engine.generate_ebics_3_0_payload("PARTNER01", "USER01")
        self.assertEqual(ebics["ebics_version"], "3.0")
        self.assertEqual(ebics["partner_id"], "PARTNER01")

    def test_12_sepa_sct_inst(self):
        xml_out = sovereign_banking_engine.generate_sepa_sct_inst("DE89370400440532013000", "FR7630006000011234567890189", Decimal("1250.00"))
        self.assertIn("SEPA_INSTANT_SCT", xml_out)
        self.assertIn("DE89370400440532013000", xml_out)

    def test_13_cbdc_rtgs_settlement(self):
        cbdc = sovereign_banking_engine.process_cbdc_rtgs_settlement("FEDUS33XXX", "token_sov_8819", Decimal("1000000.00"))
        self.assertEqual(cbdc["status"], "CBDC_RTGS_SETTLED_ZERO_DRIFT")
        self.assertEqual(cbdc["amount_settled_usd"], 1000000.0)

    def test_14_dtcc_acats_transfer(self):
        acats = sovereign_banking_engine.generate_dtcc_acats_transfer("0164", "0010", "ACCT-9812401")
        self.assertEqual(acats["status"], "ACATS_TRANSFER_SUBMITTED_DTCC_VERIFIED")
        self.assertEqual(acats["delivering_broker_dtc_number"], "0164")

    def test_15_singleton_instance(self):
        res = sovereign_banking_engine.generate_pacs_008(
            sender_bic="BOFAUS3NXXX",
            receiver_bic="CHASUS33XXX",
            amount=Decimal("10000.00"),
            currency="USD",
            debtor_acct="US12BOFA1234567890",
            creditor_acct="US98CHAS0987654321"
        )
        self.assertIn("pacs.008.001.10", res)


if __name__ == "__main__":
    unittest.main()
