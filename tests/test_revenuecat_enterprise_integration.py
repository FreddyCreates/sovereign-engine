"""
Exhaustive Automated Test Suite for Deepened RevenueCat Integration:
1. RevenueCat SDK Webhook Ingestion Engine (5 Tests)
2. RevenueCat Entitlement Gating Engine ('sovereign_office_pro', 'sovereign_office_enterprise') (5 Tests)
3. Dynamic Paywall AST Synthesis Engine (5 Tests)
4. Long-Term SaaS Usage Metering & LTV Prediction Engine (5 Tests)
5. Sovereign Enterprise Suite Integration (5 Tests)
"""

import unittest
import sys
import os
import json
import hmac
import hashlib

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../sovereign_infrastructure/nextgen_systems")))

from sovereign_infrastructure.nextgen_systems.complete_enterprise_saas_ecosystem import (
    RevenueCatSDKWebhookIngestionEngine,
    RevenueCatEntitlementGatingEngine,
    DynamicPaywallASTSynthesizer,
    LongTermSaaSUsageMeteringEngine,
    CompleteEnterpriseSaaSOrchestrator
)

from sovereign_infrastructure.nextgen_systems.mega_office_business_suite import (
    SovereignRevenueCatSuiteEngine,
    MegaOfficeBusinessSuite
)


class TestRevenueCatSDKWebhookIngestionEngine(unittest.TestCase):
    """Engine 1: RevenueCat SDK Webhook Ingestion (5 Tests)"""

    def setUp(self):
        self.secret = "rc_whsec_test_secret_key"
        self.webhook_engine = RevenueCatSDKWebhookIngestionEngine(webhook_secret=self.secret)

    def test_01_verify_webhook_signature_success(self):
        """1. Verify valid HMAC-SHA256 signature verification."""
        payload_bytes = b'{"event": {"type": "INITIAL_PURCHASE", "app_user_id": "usr_101"}}'
        expected_sig = hmac.new(self.secret.encode('utf-8'), payload_bytes, hashlib.sha256).hexdigest()
        self.assertTrue(self.webhook_engine.verify_webhook_signature(payload_bytes, expected_sig))

    def test_02_verify_webhook_signature_failure(self):
        """2. Verify invalid or tampered signature header is rejected."""
        payload_bytes = b'{"event": {"type": "INITIAL_PURCHASE", "app_user_id": "usr_101"}}'
        self.assertFalse(self.webhook_engine.verify_webhook_signature(payload_bytes, "invalid_sig_header"))
        self.assertFalse(self.webhook_engine.verify_webhook_signature(payload_bytes, None))

    def test_03_ingest_initial_purchase_webhook(self):
        """3. Ingest INITIAL_PURCHASE event and record subscriber entitlement state."""
        payload = {
            "event": {
                "id": "evt_purchase_01",
                "type": "INITIAL_PURCHASE",
                "app_user_id": "user_pro_01",
                "product_id": "sovereign_office_pro_annual",
                "entitlement_ids": ["sovereign_office_pro"],
                "store": "APP_STORE",
                "environment": "PRODUCTION",
                "price_in_purchased_currency": 49.99,
                "currency": "USD"
            }
        }
        res = self.webhook_engine.ingest_webhook_event(payload, self.secret)
        self.assertEqual(res["status"], "REVENUECAT_WEBHOOK_INGESTED")
        self.assertEqual(res["app_user_id"], "user_pro_01")
        self.assertIn("sovereign_office_pro", res["active_entitlements"])
        
        state = self.webhook_engine.get_subscriber_state("user_pro_01")
        self.assertEqual(state["last_event_type"], "INITIAL_PURCHASE")

    def test_04_ingest_renewal_and_cancellation_lifecycle(self):
        """4. Ingest RENEWAL and CANCELLATION lifecycle events to verify entitlement state transitions."""
        # Initial renewal
        renewal_payload = {
            "event": {
                "id": "evt_renew_02",
                "type": "RENEWAL",
                "app_user_id": "user_ent_02",
                "product_id": "sovereign_office_enterprise_monthly",
                "entitlement_ids": ["sovereign_office_enterprise"],
                "store": "PLAY_STORE"
            }
        }
        ren_res = self.webhook_engine.ingest_webhook_event(renewal_payload, self.secret)
        self.assertEqual(ren_res["active_entitlements"], ["sovereign_office_enterprise"])

        # Cancellation
        cancel_payload = {
            "event": {
                "id": "evt_cancel_03",
                "type": "CANCELLATION",
                "app_user_id": "user_ent_02",
                "product_id": "sovereign_office_enterprise_monthly",
                "entitlement_ids": ["sovereign_office_enterprise"],
                "store": "PLAY_STORE"
            }
        }
        can_res = self.webhook_engine.ingest_webhook_event(cancel_payload, self.secret)
        self.assertEqual(can_res["active_entitlements"], [])

    def test_05_ingest_product_change_and_uncancellation(self):
        """5. Ingest PRODUCT_CHANGE and UNCANCELLATION events."""
        change_payload = {
            "event": {
                "id": "evt_change_04",
                "type": "PRODUCT_CHANGE",
                "app_user_id": "user_flex_03",
                "product_id": "sovereign_office_enterprise_annual",
                "entitlement_ids": ["sovereign_office_pro", "sovereign_office_enterprise"]
            }
        }
        res = self.webhook_engine.ingest_webhook_event(change_payload, self.secret)
        self.assertIn("sovereign_office_enterprise", res["active_entitlements"])
        self.assertIn("sovereign_office_pro", res["active_entitlements"])


class TestRevenueCatEntitlementGatingEngine(unittest.TestCase):
    """Engine 2: RevenueCat Entitlement Gating ('sovereign_office_pro', 'sovereign_office_enterprise') (5 Tests)"""

    def setUp(self):
        self.webhook_engine = RevenueCatSDKWebhookIngestionEngine()
        self.gating_engine = RevenueCatEntitlementGatingEngine(webhook_engine=self.webhook_engine)

    def test_01_grant_and_check_pro_access(self):
        """1. Grant 'sovereign_office_pro' entitlement and verify access."""
        grant_res = self.gating_engine.grant_entitlement("sub_pro", "sovereign_office_pro")
        self.assertEqual(grant_res["status"], "ENTITLEMENT_GRANTED")

        check_res = self.gating_engine.check_entitlement("sub_pro", "sovereign_office_pro")
        self.assertTrue(check_res["access_granted"])
        self.assertEqual(check_res["effective_tier"], "sovereign_office_pro")

    def test_02_grant_and_check_enterprise_access(self):
        """2. Grant 'sovereign_office_enterprise' entitlement and verify full access."""
        self.gating_engine.grant_entitlement("sub_ent", "sovereign_office_enterprise")
        
        check_ent = self.gating_engine.check_entitlement("sub_ent", "sovereign_office_enterprise")
        self.assertTrue(check_ent["access_granted"])
        self.assertEqual(check_ent["effective_tier"], "sovereign_office_enterprise")

    def test_03_enterprise_hierarchy_satisfies_pro(self):
        """3. Verify enterprise entitlement subscriber automatically grants pro access."""
        self.gating_engine.grant_entitlement("sub_ent_hier", "sovereign_office_enterprise")
        check_pro = self.gating_engine.check_entitlement("sub_ent_hier", "sovereign_office_pro")
        self.assertTrue(check_pro["access_granted"])

    def test_04_feature_access_evaluation_and_paywall_trigger(self):
        """4. Evaluate feature access and verify paywall trigger when feature is blocked for free tier."""
        # Unsubscribed / free user checking enterprise feature
        eval_res = self.gating_engine.evaluate_feature_access("sub_free", "multi_entity_consolidation")
        self.assertFalse(eval_res["access_granted"])
        self.assertIsNotNone(eval_res["paywall_trigger"])
        self.assertTrue(eval_res["paywall_trigger"]["trigger_paywall"])
        self.assertEqual(eval_res["paywall_trigger"]["required_entitlement"], "sovereign_office_enterprise")

    def test_05_revoke_entitlement_reverts_access(self):
        """5. Revoke entitlement and verify access is denied."""
        self.gating_engine.grant_entitlement("sub_temp", "sovereign_office_pro")
        self.assertTrue(self.gating_engine.check_entitlement("sub_temp", "sovereign_office_pro")["access_granted"])

        revoke_res = self.gating_engine.revoke_entitlement("sub_temp", "sovereign_office_pro")
        self.assertEqual(revoke_res["status"], "ENTITLEMENT_REVOKED")
        self.assertFalse(self.gating_engine.check_entitlement("sub_temp", "sovereign_office_pro")["access_granted"])


class TestDynamicPaywallASTSynthesizer(unittest.TestCase):
    """Engine 3: Dynamic Paywall AST Synthesis (5 Tests)"""

    def setUp(self):
        self.synthesizer = DynamicPaywallASTSynthesizer()

    def test_01_synthesize_pro_paywall_ast(self):
        """1. Synthesize paywall AST layout for 'sovereign_office_pro'."""
        res = self.synthesizer.synthesize_paywall_ast("sovereign_office_pro", country_code="US", currency="USD")
        self.assertEqual(res["status"], "PAYWALL_AST_SYNTHESIZED")
        self.assertEqual(res["target_entitlement"], "sovereign_office_pro")
        
        ast = res["paywall_ast"]
        self.assertEqual(ast["version"], "2.0")
        self.assertGreater(len(ast["components"]), 3)

    def test_02_synthesize_enterprise_paywall_ast(self):
        """2. Synthesize paywall AST layout for 'sovereign_office_enterprise'."""
        res = self.synthesizer.synthesize_paywall_ast("sovereign_office_enterprise", country_code="DE", currency="EUR")
        self.assertEqual(res["localized_price"], "€199.99")
        
        feat_comp = next(c for c in res["paywall_ast"]["components"] if c["type"] == "FeatureList")
        self.assertTrue(any("Multi-Entity" in item for item in feat_comp["items"]))

    def test_03_localized_ppp_discount_paywall_ast(self):
        """3. Synthesize localized paywall with Purchasing Power Parity (PPP) discount rate."""
        res = self.synthesizer.synthesize_paywall_ast(
            target_entitlement="sovereign_office_pro",
            country_code="INR",
            currency="INR",
            ppp_discount_rate=0.40
        )
        self.assertEqual(res["ppp_discount_rate"], 0.40)
        self.assertEqual(res["localized_price"], "₹29.99")

    def test_04_kuramoto_coherence_paywall_mutation(self):
        """4. Mutate paywall AST layout when user engagement/coherence threshold R > 0.618 is reached."""
        base = self.synthesizer.synthesize_paywall_ast("sovereign_office_pro")
        mutated = self.synthesizer.mutate_paywall_variant(base, scroll_velocity=0.95, engagement_score=0.98)
        
        self.assertGreater(mutated["kuramoto_R"], 0.618)
        self.assertEqual(mutated["mutated_variant"], "GLASSMORPHIC_URGENCY_TRIAL")
        
        header = next(c for c in mutated["mutated_paywall_ast"]["components"] if c["type"] == "HeaderSection")
        self.assertIn("RETENTION OFFER", header["badge"])

    def test_05_high_churn_risk_paywall_mutation(self):
        """5. Mutate paywall AST layout when churn risk score > 0.50 is detected."""
        base = self.synthesizer.synthesize_paywall_ast("sovereign_office_pro")
        mutated = self.synthesizer.mutate_paywall_variant(base, churn_risk_score=0.75)
        
        self.assertEqual(mutated["mutated_variant"], "GLASSMORPHIC_URGENCY_TRIAL")
        cta = next(c for c in mutated["mutated_paywall_ast"]["components"] if c["type"] == "CTAButton")
        self.assertIn("Claim 50% Off", cta["label"])


class TestLongTermSaaSUsageMeteringEngine(unittest.TestCase):
    """Engine 4: Long-Term SaaS Usage Metering (MAU, Quota Caps, LTV Prediction) (5 Tests)"""

    def setUp(self):
        self.gating = RevenueCatEntitlementGatingEngine()
        self.metering = LongTermSaaSUsageMeteringEngine(gating_engine=self.gating)

    def test_01_user_activity_and_mau_analytics(self):
        """1. Record user sessions and compute Monthly Active Users (MAU) analytics."""
        self.metering.record_user_activity("user_a")
        self.metering.record_user_activity("user_b")
        self.metering.record_user_activity("user_c")

        mau_res = self.metering.get_mau_analytics()
        self.assertEqual(mau_res["monthly_active_users"], 3)
        self.assertEqual(mau_res["daily_active_users"], 3)
        self.assertEqual(mau_res["dau_mau_stickiness_pct"], 100.0)

    def test_02_quota_cap_enforcement_free_tier(self):
        """2. Enforce quota caps for free tier subscriber."""
        # Free tier cap for documents is 5
        for _ in range(5):
            self.metering.record_usage("user_free", "documents", 1)

        cap_check = self.metering.check_quota_cap("user_free", "documents", requested_units=1)
        self.assertFalse(cap_check["within_cap"])
        self.assertEqual(cap_check["status"], "QUOTA_CAP_EXCEEDED")

    def test_03_quota_cap_enforcement_pro_tier(self):
        """3. Enforce elevated quota caps for 'sovereign_office_pro' subscriber."""
        self.gating.grant_entitlement("user_pro_meter", "sovereign_office_pro")
        self.metering.record_usage("user_pro_meter", "documents", 10)

        cap_check = self.metering.check_quota_cap("user_pro_meter", "documents", requested_units=1)
        self.assertTrue(cap_check["within_cap"])
        self.assertEqual(cap_check["quota_cap"], 100)
        self.assertEqual(cap_check["quota_remaining"], 90)

    def test_04_predictive_ltv_calculation(self):
        """4. Calculate long-term predictive subscriber LTV over 24-month horizon."""
        ltv_res = self.metering.predict_subscriber_ltv(
            subscriber_id="sub_ltv_01",
            monthly_arpu=149.00,
            active_months=6,
            churn_risk=0.03,
            horizon_months=24
        )
        self.assertEqual(ltv_res["status"], "LTV_PREDICTION_COMPLETED")
        self.assertGreater(ltv_res["predicted_ltv_usd"], 2000.0)
        self.assertGreater(ltv_res["ltv_to_cac_ratio"], 3.0)

    def test_05_ltv_payback_and_retention_campaign_recommendation(self):
        """5. Verify LTV payback period and churn-risk retention campaign offer."""
        # High churn risk > 0.40 triggers retention discount
        ltv_high_risk = self.metering.predict_subscriber_ltv("sub_risk", monthly_arpu=49.99, churn_risk=0.45)
        self.assertEqual(ltv_high_risk["recommended_campaign"], "RETENTION_50_OFF_3_MONTHS")

        # Low churn risk triggers standard offer
        ltv_low_risk = self.metering.predict_subscriber_ltv("sub_loyal", monthly_arpu=49.99, churn_risk=0.02)
        self.assertEqual(ltv_low_risk["recommended_campaign"], "STANDARD_ANNUAL_UPGRADE")


class TestSovereignEnterpriseSuiteIntegration(unittest.TestCase):
    """Engine 5: Master Sovereign Enterprise Suite Integration (5 Tests)"""

    def setUp(self):
        self.complete_orchestrator = CompleteEnterpriseSaaSOrchestrator()
        self.mega_suite = MegaOfficeBusinessSuite()

    def test_01_complete_saas_orchestrator_pipeline_with_revenuecat(self):
        """1. Execute complete enterprise SaaS pipeline incorporating RevenueCat engines."""
        res = self.complete_orchestrator.execute_full_saas_matrix_pipeline("usr_ent_master", 199.99, country_code="DE")
        self.assertEqual(res["status"], "ENTERPRISE_SAAS_MATRIX_SUCCESS")
        self.assertEqual(res["matrix_features_verified"], 15)
        self.assertEqual(res["revenuecat_webhook_ingestion"]["status"], "REVENUECAT_WEBHOOK_INGESTED")

    def test_02_complete_saas_orchestrator_audit(self):
        """2. Run full audit on CompleteEnterpriseSaaSOrchestrator."""
        audit = self.complete_orchestrator.audit_enterprise_saas_matrix()
        self.assertEqual(audit["total_engines_active"], 19)
        self.assertEqual(audit["audit_result"], "PASS")

    def test_03_mega_office_suite_revenuecat_webhook_and_entitlement(self):
        """3. Ingest webhook and check entitlement via MegaOfficeBusinessSuite master class."""
        wh_res = self.mega_suite.ingest_revenuecat_webhook({
            "event": {
                "id": "evt_suite_01",
                "type": "INITIAL_PURCHASE",
                "app_user_id": "suite_user_01",
                "entitlement_ids": ["sovereign_office_pro"]
            }
        })
        self.assertEqual(wh_res["status"], "REVENUECAT_WEBHOOK_INGESTED")

        check_res = self.mega_suite.check_entitlement("suite_user_01", "sovereign_office_pro")
        self.assertTrue(check_res["access_granted"])

    def test_04_mega_office_suite_paywall_ast_and_metering(self):
        """4. Synthesize paywall AST and record usage via MegaOfficeBusinessSuite."""
        ast_res = self.mega_suite.synthesize_paywall_ast("sovereign_office_enterprise", "US", "USD")
        self.assertEqual(ast_res["target_entitlement"], "sovereign_office_enterprise")

        self.mega_suite.record_usage("suite_user_01", "api_calls", 50)
        cap = self.mega_suite.check_quota_cap("suite_user_01", "api_calls", 10)
        self.assertTrue(cap["within_cap"])

    def test_05_mega_office_suite_create_package_and_audit(self):
        """5. Create business package and run full office audit incorporating RevenueCat metrics."""
        pkg = self.mega_suite.create_business_package("Apex Sovereign", "Acme Enterprise", 240000.0)
        self.assertEqual(pkg["status"], "BUSINESS_PACKAGE_CREATED")
        self.assertIn("ltv_prediction", pkg)

        audit = self.mega_suite.run_full_office_audit()
        self.assertEqual(audit["status"], "MEGA_OFFICE_SUITE_FULLY_OPERATIONAL")
        self.assertTrue(audit["revenuecat_integration"]["sdk_webhook_ingestion"])


if __name__ == "__main__":
    unittest.main()
