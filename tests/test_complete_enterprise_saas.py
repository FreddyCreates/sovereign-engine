"""
Automated Test Suite for Complete Enterprise SaaS Ecosystem Matrix (15+ Features)
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sovereign_infrastructure", "nextgen_systems")))

from complete_enterprise_saas_ecosystem import (
    FixedAssetDepreciationEngine,
    InventoryFIFOEngine,
    MultiEntityConsolidationEngine,
    MeteredUsageBillingEngine,
    SmartDunningEngine,
    GlobalSalesTaxEngine,
    PTOAccrualEngine,
    ExpenseOCRMatchingEngine,
    PurchaseOrderMatchingEngine,
    DeferredRevenueASC606Engine,
    SubscriptionRevShareEngine,
    CorporateTreasuryFXEngine,
    B2BInvoiceUnderwritingEngine,
    CohortLTVRetentionEngine,
    DeflationaryTokenomicsEngine,
    CompleteEnterpriseSaaSOrchestrator
)


class TestCompleteEnterpriseSaaSEcosystem(unittest.TestCase):

    def setUp(self):
        self.depreciation = FixedAssetDepreciationEngine()
        self.fifo = InventoryFIFOEngine()
        self.consolidation = MultiEntityConsolidationEngine()
        self.metered = MeteredUsageBillingEngine()
        self.dunning = SmartDunningEngine()
        self.tax = GlobalSalesTaxEngine()
        self.pto = PTOAccrualEngine()
        self.ocr = ExpenseOCRMatchingEngine()
        self.po = PurchaseOrderMatchingEngine()
        self.revrec = DeferredRevenueASC606Engine()
        self.revshare = SubscriptionRevShareEngine()
        self.treasury = CorporateTreasuryFXEngine()
        self.underwrite = B2BInvoiceUnderwritingEngine()
        self.cohort = CohortLTVRetentionEngine()
        self.tokenomics = DeflationaryTokenomicsEngine()
        self.orchestrator = CompleteEnterpriseSaaSOrchestrator()

    def test_01_depreciation_straight_line(self):
        res = self.depreciation.calculate_straight_line_depreciation(240000.0, 40000.0, 5)
        self.assertEqual(res["annual_depreciation"], 40000.0)
        self.assertEqual(res["monthly_depreciation_expense"], 3333.33)

    def test_01b_depreciation_macrs(self):
        res = self.depreciation.calculate_macrs_depreciation(100000.0, "5-year", recovery_year=1)
        self.assertEqual(res["depreciation_expense"], 20000.0)
        self.assertEqual(res["ending_book_value"], 80000.0)

    def test_01c_depreciation_schedule(self):
        sched = self.depreciation.generate_depreciation_schedule(100000.0, method="MACRS", asset_class="5-year")
        self.assertEqual(len(sched["schedule"]), 6)
        self.assertEqual(sched["total_depreciation"], 100000.0)

    def test_02_fifo_inventory(self):
        res = self.fifo.calculate_fifo_cogs(150)
        self.assertEqual(res["total_cogs"], 7750.0)

    def test_02b_fifo_batch_addition_and_valuation(self):
        self.fifo.add_inventory_batch("BATCH-03", 50, 60.0)
        val = self.fifo.get_ending_inventory_valuation()
        self.assertGreaterEqual(val["total_units_on_hand"], 50)
        self.assertGreater(val["total_inventory_valuation"], 0.0)

    def test_02c_fifo_write_down(self):
        wd = self.fifo.write_down_inventory("BATCH-02", 10)
        self.assertEqual(wd["units_written_off"], 10)
        self.assertEqual(wd["loss_amount"], 550.0)

    def test_03_multi_entity(self):
        res = self.consolidation.consolidate_entities(500000.0, 250000.0, 50000.0)
        self.assertEqual(res["consolidated_revenue"], 700000.0)

    def test_03b_currency_translation_and_elimination(self):
        trans = self.consolidation.translate_subsidiary_currency("EU Sub", "EUR", 100000.0, 1.08)
        self.assertEqual(trans["converted_amount_usd"], 108000.0)
        elim = self.consolidation.eliminate_intercompany_transactions(500000.0, 50000.0, 10000.0)
        self.assertEqual(elim["net_consolidated_revenue"], 450000.0)

    def test_04_metered_billing(self):
        res = self.metered.calculate_metered_bill(99.0, 20000)
        self.assertEqual(res["total_bill_usd"], 124.0)

    def test_04b_tiered_usage_billing(self):
        tiered = self.metered.calculate_tiered_usage_bill(100.0, 60000)
        self.assertEqual(tiered["base_subscription"], 100.0)
        self.assertEqual(tiered["total_bill_usd"], 190.0)

    def test_05_smart_dunning(self):
        res = self.dunning.execute_dunning_retry("sub_101", 1)
        self.assertEqual(res["dunning_action"], "Immediate Retry")

    def test_05b_dunning_schedule_and_entitlements(self):
        sched = self.dunning.get_dunning_retry_schedule("CARD_EXPIRED")
        self.assertTrue(sched["strategy"]["card_updater_enabled"])
        ent = self.dunning.evaluate_subscriber_entitlement("sub_101", days_overdue=20)
        self.assertEqual(ent["entitlement_state"], "SUSPENDED")

    def test_06_sales_tax(self):
        res = self.tax.calculate_location_tax(100.0, "DE")
        self.assertEqual(res["tax_amount"], 19.0)

    def test_06b_b2b_vat_reverse_charge(self):
        b2b = self.tax.calculate_b2b_vat_exemption(1000.0, "DE", "FR", "FR123456789")
        self.assertTrue(b2b["is_exempt"])
        self.assertEqual(b2b["tax_amount"], 0.0)

    def test_07_pto_accrual(self):
        res = self.pto.calculate_pto_accrual(160.0)
        self.assertEqual(res["accrued_pto_hours"], 8.0)

    def test_07b_pto_rollover_and_payout(self):
        roll = self.pto.apply_pto_rollover_cap(180.0, max_cap_hours=160.0, max_rollover_hours=40.0)
        self.assertEqual(roll["rollover_hours"], 40.0)
        self.assertEqual(roll["forfeited_hours"], 140.0)
        payout = self.pto.calculate_pto_termination_payout(40.0, 75.0)
        self.assertEqual(payout["payout_amount_usd"], 3000.0)

    def test_08_expense_ocr(self):
        res = self.ocr.process_receipt_ocr("AWS", 250.0)
        self.assertTrue(res["policy_compliant"])

    def test_08b_expense_categorization_and_audit(self):
        cat = self.ocr.categorize_receipt_expense("AWS Cloud Infrastructure")
        self.assertIn("Infrastructure", cat["assigned_gl_code"])
        audit = self.ocr.audit_expense_policy("emp_101", 1000.0, "Software", has_receipt=False)
        self.assertFalse(audit["passed_audit"])

    def test_09_po_3way_matching(self):
        res = self.po.match_3way_po(5000.0, 5000.0, 5000.0)
        self.assertTrue(res["is_3way_matched"])

    def test_09b_po_line_item_reconciliation(self):
        po_items = [{"item_id": "ITEM-1", "qty": 10, "unit_price": 50.0}]
        grn_items = [{"item_id": "ITEM-1", "qty": 10, "unit_price": 50.0}]
        inv_items = [{"item_id": "ITEM-1", "qty": 10, "unit_price": 50.0}]
        rec = self.po.reconcile_line_items(po_items, grn_items, inv_items)
        self.assertTrue(rec["is_fully_reconciled"])

    def test_10_asc606_revenue_recognition(self):
        sched = self.revrec.create_revenue_schedule("CTR-101", 12000.0, 12)
        self.assertEqual(sched["monthly_recognized_revenue"], 1000.0)
        rec = self.revrec.recognize_monthly_revenue("CTR-101", 3, 12000.0, 12)
        self.assertEqual(rec["cumulative_recognized_revenue"], 3000.0)
        self.assertEqual(rec["remaining_deferred_liability"], 9000.0)

    def test_11_revshare_split_and_payouts(self):
        split = self.revshare.calculate_revshare_split(1000.0, platform_fee_pct=0.15, partner_commission_pct=0.20)
        self.assertEqual(split["platform_fee"], 150.0)
        self.assertEqual(split["partner_commission"], 200.0)
        self.assertEqual(split["net_publisher_payout"], 650.0)

        staged = self.revshare.stage_partner_payouts(1000.0, [{"partner_id": "P-1", "share_pct": 0.20}])
        self.assertEqual(staged["total_partner_payout_usd"], 200.0)

    def test_12_corporate_treasury_fx(self):
        exposure = self.treasury.evaluate_treasury_exposure({"USD": 100000.0, "EUR": 50000.0}, {"USD": 1.0, "EUR": 1.08})
        self.assertEqual(exposure["total_treasury_usd"], 154000.0)
        hedge = self.treasury.execute_fx_forward_hedge("EUR", 50000.0, spot_rate=1.08, lock_rate=1.10)
        self.assertEqual(hedge["hedge_gain_loss_usd"], 1000.0)

    def test_13_b2b_invoice_underwriting(self):
        uw = self.underwrite.underwrite_b2b_invoice(50000.0, buyer_credit_score=780, payment_history_ratio=0.98, tenure_months=24)
        self.assertEqual(uw["underwriting_status"], "APPROVED")
        self.assertEqual(uw["bnpl_terms_offered"], "NET_30")

    def test_14_cohort_ltv_and_retention(self):
        ltv = self.cohort.calculate_cohort_ltv(100.0, monthly_churn_rate=0.05, discount_rate=0.10, months=12)
        self.assertGreater(ltv["discounted_ltv_usd"], 0.0)
        camp = self.cohort.generate_targeted_retention_campaign("usr_101", churn_risk=0.75, expected_ltv=1200.0)
        self.assertEqual(camp["recommended_offer"], "RETENTION_DISCOUNT_40_OFF")

    def test_15_deflationary_tokenomics(self):
        bond = self.tokenomics.calculate_bonding_price(1000000.0, base_price=1.00)
        self.assertEqual(bond["bonding_price_usd"], 2.0)
        burn = self.tokenomics.process_subscription_burn(100.0, token_price=2.0, burn_rate_pct=0.15)
        self.assertEqual(burn["tokens_burned"], 7.5)

    def test_16_master_orchestrator(self):
        res = self.orchestrator.execute_full_saas_matrix_pipeline("usr_enterprise", 299.0, country_code="DE")
        self.assertEqual(res["status"], "ENTERPRISE_SAAS_MATRIX_SUCCESS")
        self.assertEqual(res["matrix_features_verified"], 15)
        audit = self.orchestrator.audit_enterprise_saas_matrix()
        self.assertEqual(audit["audit_result"], "PASS")


if __name__ == "__main__":
    unittest.main()
