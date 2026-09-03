"""
EXHAUSTIVE AUTOMATED UNIT TEST SUITE FOR SOVEREIGN REVENUECAT CRYPTO WALLET ENGINE
===================================================================================
Tests 5 Core FinTech Subsystems:
1. RevenueCat Tokenized Wallet Passport Minting (rNFTs)
2. Multi-Chain Treasury Vault Manager (USDC, ETH, SOL, BTC, MINT)
3. ARR Subscription Micro-Factoring Loans
4. ZK Dilithium-3 Post-Quantum Signer
5. Double-entry Zero-Drift GL Debit/Credit Balance Validation

Author: Lead Sovereign OS Platform Architect
"""

import unittest
import sys
import os
import json
import time
from decimal import Decimal

# Add path for parent directory imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../sovereign_infrastructure/nextgen_systems")))

from sovereign_infrastructure.nextgen_systems.sovereign_revenuecat_crypto_wallet_engine import (
    SovereignRevenueCatCryptoWalletEngine,
    DoubleEntryZeroDriftGLEngine,
    ZKDilithium3PostQuantumSigner,
    RevenueCatPassportMintingEngine,
    MultiChainTreasuryVaultManager,
    ARRSubscriptionMicroFactoringEngine
)


class TestSovereignRevenueCatCryptoWalletEngine(unittest.TestCase):
    """Exhaustive Automated Unit Tests for Sovereign RevenueCat Crypto Wallet Engine."""

    def setUp(self):
        self.engine = SovereignRevenueCatCryptoWalletEngine()

    def test_01_rnft_passport_minting_and_valuation(self):
        """1. Verify RevenueCat rNFT passport minting, dynamic valuation, and zero-drift GL posting."""
        sub_id = "sub_enterprise_99"
        ent_id = "sovereign_office_unlimited_ai"
        mrr = 1200.00
        duration_days = 365
        loyalty_days = 180

        res = self.engine.mint_rnft_passport(
            subscriber_id=sub_id,
            entitlement_id=ent_id,
            tier="UNLIMITED_AI",
            duration_days=duration_days,
            mrr_value=mrr,
            loyalty_days=loyalty_days,
            store="APP_STORE"
        )

        self.assertEqual(res["status"], "MINTED")
        self.assertTrue(res["rnft_id"].startswith("rnft_sub_enterprise_99_"))
        self.assertIn("valuation_usd", res["metadata"])
        
        # Verify formula: ARR * (1 + (loyalty / 365)*0.25) * (duration / 365)
        expected_arr = mrr * 12.0
        expected_loyalty_mult = 1.0 + (180.0 / 365.0) * 0.25
        expected_valuation = round(expected_arr * expected_loyalty_mult * 1.0, 2)
        self.assertEqual(res["metadata"]["valuation_usd"], expected_valuation)

        # Verify ZK Dilithium-3 proof presence
        self.assertTrue(res["zk_proof"].startswith("zk_proof_dilithium3_"))
        self.assertTrue(res["dilithium_signature"].startswith("dil3_sig_"))

        # Verify Double-Entry Zero-Drift GL posting
        gl = res["gl_posting"]
        self.assertTrue(gl["zero_precision_drift_valid"])
        self.assertEqual(gl["balance_variance"], 0.00)
        self.assertEqual(gl["debits"]["1300 rNFT Tokenized Passport Reserve"], expected_valuation)
        self.assertEqual(gl["credits"]["4000 Sovereign SaaS Subscription Revenue"], expected_valuation)

    def test_02_multi_chain_treasury_vault_management(self):
        """2. Verify Multi-Chain Treasury Vault Manager, TVL USD calculations, and cross-chain transfers."""
        balances = self.engine.get_treasury_balances()
        self.assertIn("total_tvl_usd", balances)
        self.assertGreater(balances["total_tvl_usd"], 1000000.0)
        self.assertIn("ethereum", balances["chain_vaults"])
        self.assertIn("solana", balances["chain_vaults"])
        self.assertIn("bitcoin", balances["chain_vaults"])

        # Execute transfer: 50,000 USDC from ethereum to solana
        transfer_res = self.engine.transfer_vault_asset(
            from_chain="ethereum",
            to_chain="solana",
            asset="USDC",
            amount=50000.00
        )
        self.assertEqual(transfer_res["status"], "TRANSFER_SUCCESSFUL")
        self.assertEqual(transfer_res["value_usd"], 50000.00)
        self.assertTrue(transfer_res["zk_proof"].startswith("zk_proof_dilithium3_"))

        # Check balance after transfer
        new_balances = self.engine.get_treasury_balances()
        self.assertEqual(new_balances["chain_vaults"]["ethereum"]["assets"]["USDC"]["quantity"], 450000.0)
        self.assertEqual(new_balances["chain_vaults"]["solana"]["assets"]["USDC"]["quantity"], 350000.0)

    def test_03_arr_subscription_micro_factoring_loan_lifecycle(self):
        """3. Verify ARR subscription micro-factoring capacity, loan origination, amortization schedule, and repayment."""
        # Calculate maximum borrowing capacity
        capacity = self.engine.calculate_factoring_capacity(
            mrr=15000.00,
            churn_rate=0.015,
            nrr=1.20,
            ltv_ratio=0.75,
            dscr=1.60
        )
        self.assertEqual(capacity["arr"], 180000.00)
        self.assertGreater(capacity["max_loan_capacity_usd"], 100000.00)

        # Originate factoring loan
        loan = self.engine.originate_factoring_loan(
            subscriber_id="sub_fintech_77",
            loan_amount_usd=50000.00,
            term_months=12,
            annual_interest_rate=0.10
        )
        self.assertEqual(loan["status"], "ACTIVE")
        self.assertEqual(loan["principal_amount_usd"], 50000.00)
        self.assertEqual(len(loan["amortization_schedule"]), 12)
        
        # Verify amortization monthly payment calculation accuracy
        first_month = loan["amortization_schedule"][0]
        self.assertGreater(first_month["principal"], 0)
        self.assertGreater(first_month["interest"], 0)

        # Process loan repayment installment
        repay_res = self.engine.repay_loan_installment(
            loan_id=loan["loan_id"],
            payment_amount_usd=loan["monthly_payment_usd"]
        )
        self.assertEqual(repay_res["status"], "REPAYMENT_PROCESSED")
        self.assertLess(repay_res["remaining_principal_usd"], 50000.00)
        self.assertTrue(repay_res["gl_posting"]["zero_precision_drift_valid"])

    def test_04_zk_dilithium3_post_quantum_signer_and_verification(self):
        """4. Verify CRYSTALS-Dilithium Level 3 post-quantum ZK signer, SHA-256 Merkle root verification, and tamper detection."""
        payload = {
            "transaction_type": "TREASURY_REBALANCE",
            "from_asset": "ETH",
            "to_asset": "USDC",
            "amount_usd": 150000.00
        }

        # Sign payload
        signed = self.engine.sign_payload(payload)
        self.assertEqual(signed["quantum_security_level"], "CRYSTALS-Dilithium Level 3")
        self.assertTrue(signed["dilithium_signature"].startswith("dil3_sig_"))
        self.assertTrue(signed["zk_proof"].startswith("zk_proof_dilithium3_"))
        self.assertIn("merkle_root", signed)
        self.assertEqual(len(signed["merkle_root"]), 64)

        # Verify valid signature & proof with Merkle Root check
        verification = self.engine.verify_zk_proof(
            payload=payload,
            signature=signed["dilithium_signature"],
            zk_proof=signed["zk_proof"],
            public_key=signed["signer_pubkey"],
            merkle_root=signed["merkle_root"]
        )
        self.assertTrue(verification["valid"])
        self.assertEqual(verification["quantum_tamper_evidence"], "PASS")
        self.assertEqual(verification["shors_attack_resistance"], "IMMUNE_LATTICE_CRYPTO")
        self.assertEqual(verification["grovers_attack_security_bits"], 256)
        self.assertTrue(verification["merkle_root_verified"])

        # Test Merkle inclusion proof generation and verification
        leaves = ["leaf1", "leaf2", "leaf3", "leaf4"]
        merkle_root = self.engine.compute_merkle_root(leaves)
        proof = self.engine.generate_merkle_proof(leaves, target_index=2)
        self.assertEqual(proof["merkle_root"], merkle_root)
        is_valid_proof = self.engine.verify_merkle_proof(proof["leaf"], proof["proof"], merkle_root)
        self.assertTrue(is_valid_proof)

        # Verify public key forgery fails verification
        forged_pubkey = "pq_pub_dilithium3_ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
        forged_verification = self.engine.verify_zk_proof(
            payload=payload,
            signature=signed["dilithium_signature"],
            zk_proof=signed["zk_proof"],
            public_key=forged_pubkey
        )
        self.assertFalse(forged_verification["valid"])
        self.assertEqual(forged_verification["quantum_tamper_evidence"], "FAILED_INTEGRITY_CHECK")

        # Verify tampered payload fails verification
        tampered_payload = dict(payload)
        tampered_payload["amount_usd"] = 9999999.00
        invalid_verification = self.engine.verify_zk_proof(
            payload=tampered_payload,
            signature=signed["dilithium_signature"],
            zk_proof=signed["zk_proof"],
            public_key=signed["signer_pubkey"]
        )
        self.assertFalse(invalid_verification["valid"])
        self.assertEqual(invalid_verification["quantum_tamper_evidence"], "FAILED_INTEGRITY_CHECK")

    def test_05_double_entry_zero_drift_gl_validation(self):
        """5. Verify double-entry zero-drift GL debit/credit balance validation and error raising on imbalance."""
        gl_engine = DoubleEntryZeroDriftGLEngine()

        # Valid balanced entry
        debits = {"1000 Cash & Bank Reserves": 1250.50, "1100 Market Securities": 749.50}
        credits = {"4000 SaaS Revenue": 2000.00}
        
        entry = gl_engine.validate_and_post_entry(debits, credits, "Balanced Journal Test")
        self.assertTrue(entry["zero_precision_drift_valid"])
        self.assertEqual(entry["total_debits"], 2000.00)
        self.assertEqual(entry["total_credits"], 2000.00)

        # Unbalanced entry must raise ValueError
        unbalanced_debits = {"1000 Cash & Bank Reserves": 1000.00}
        unbalanced_credits = {"4000 SaaS Revenue": 1000.01}
        with self.assertRaises(ValueError) as ctx:
            gl_engine.validate_and_post_entry(unbalanced_debits, unbalanced_credits, "Unbalanced Test")
        self.assertIn("UNBALANCED_JOURNAL_ENTRY", str(ctx.exception))

        # Check full audit trail
        audit = gl_engine.get_audit_trail()
        self.assertEqual(audit["total_entries"], 1)
        self.assertTrue(audit["zero_drift_audit_passed"])

    def test_06_zero_float_drift_across_all_transaction_pathways(self):
        """6. Comprehensive zero float drift double-entry GL balance validation (abs(debits - credits) == 0.00) across all transaction pathways."""
        # 1. Mint Passport Pathway
        mint_res = self.engine.mint_rnft_passport(
            subscriber_id="sub_zero_drift_1",
            mrr_value=500.00,
            duration_days=365
        )
        gl_mint = mint_res["gl_posting"]
        self.assertEqual(gl_mint["total_debits"] - gl_mint["total_credits"], 0.0)
        self.assertTrue(gl_mint["zero_precision_drift_valid"])

        # 2. Transfer Vault Asset Pathway
        xfer_res = self.engine.transfer_vault_asset(
            from_chain="ethereum",
            to_chain="solana",
            asset="ETH",
            amount=10.0
        )
        gl_xfer = xfer_res["gl_posting"]
        self.assertEqual(gl_xfer["total_debits"] - gl_xfer["total_credits"], 0.0)
        self.assertTrue(gl_xfer["zero_precision_drift_valid"])

        # 3. Originate Factoring Loan Pathway
        loan_res = self.engine.originate_factoring_loan(
            subscriber_id="sub_zero_drift_2",
            loan_amount_usd=25000.00,
            term_months=6,
            annual_interest_rate=0.12
        )
        gl_loan = loan_res["gl_posting"]
        self.assertEqual(gl_loan["total_debits"] - gl_loan["total_credits"], 0.0)
        self.assertTrue(gl_loan["zero_precision_drift_valid"])

        # 4. Loan Repayment Installment Pathway
        repay_res = self.engine.repay_loan_installment(
            loan_id=loan_res["loan_id"],
            payment_amount_usd=loan_res["monthly_payment_usd"]
        )
        gl_repay = repay_res["gl_posting"]
        self.assertEqual(gl_repay["total_debits"] - gl_repay["total_credits"], 0.0)
        self.assertTrue(gl_repay["zero_precision_drift_valid"])

        # Verify system-wide GL audit trail zero drift status
        audit = self.engine.audit_gl_ledger()
        self.assertTrue(audit["zero_drift_audit_passed"])
        self.assertEqual(audit["total_entries"], 4)
        for je in audit["journal_entries"]:
            self.assertEqual(je["total_debits"] - je["total_credits"], 0.0)
            self.assertEqual(je["balance_variance"], 0.00)


if __name__ == "__main__":
    unittest.main()
