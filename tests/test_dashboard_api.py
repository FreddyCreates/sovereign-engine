"""
Automated Testing Suite for Sovereign Engine Dashboard REST API & 15+ Enterprise SaaS Endpoints
"""

import sys
import os
import unittest
import json
import io

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sovereign_dashboard_server import SovereignDashboardHandler


class TestDashboardAPI(unittest.TestCase):

    def invoke_endpoint(self, path: str, method: str = "GET", body: dict = None) -> dict:
        body_bytes = json.dumps(body).encode("utf-8") if body else b""
        rfile = io.BytesIO(body_bytes)
        wfile = io.BytesIO()

        handler = SovereignDashboardHandler.__new__(SovereignDashboardHandler)
        handler.path = path
        handler.rfile = rfile
        handler.wfile = wfile
        handler.headers = {"Content-Length": str(len(body_bytes))}

        handler.response_code = None
        handler.response_headers = {}

        def mock_send_response(code, message=None):
            handler.response_code = code

        def mock_send_header(keyword, value):
            handler.response_headers[keyword] = value

        def mock_end_headers():
            pass

        handler.send_response = mock_send_response
        handler.send_header = mock_send_header
        handler.end_headers = mock_end_headers

        if method.upper() == "GET":
            handler.do_GET()
        else:
            handler.do_POST()

        output_bytes = wfile.getvalue()
        self.assertEqual(handler.response_code, 200)
        return json.loads(output_bytes.decode("utf-8")) if output_bytes else {}

    def invoke_raw_endpoint(self, path: str, method: str = "GET", body: dict = None):
        body_bytes = json.dumps(body).encode("utf-8") if body else b""
        rfile = io.BytesIO(body_bytes)
        wfile = io.BytesIO()

        handler = SovereignDashboardHandler.__new__(SovereignDashboardHandler)
        handler.path = path
        handler.rfile = rfile
        handler.wfile = wfile
        handler.headers = {"Content-Length": str(len(body_bytes))}

        handler.response_code = None
        handler.response_headers = {}

        def mock_send_response(code, message=None):
            handler.response_code = code

        def mock_send_header(keyword, value):
            handler.response_headers[keyword] = value

        def mock_end_headers():
            pass

        handler.send_response = mock_send_response
        handler.send_header = mock_send_header
        handler.end_headers = mock_end_headers

        if method.upper() == "GET":
            handler.do_GET()
        else:
            handler.do_POST()

        output_bytes = wfile.getvalue()
        return handler.response_code, handler.response_headers, output_bytes

    def test_01_overview_endpoint(self):
        res = self.invoke_endpoint("/api/v1/overview", "GET")
        self.assertEqual(res["arr"], 1787040.0)
        self.assertEqual(res["cores_entangled"], 6)

    def test_02_ledger_endpoint(self):
        res = self.invoke_endpoint("/api/v1/ledger", "GET")
        self.assertEqual(res["net_income"], 331246.0)
        self.assertEqual(res["status"], "QUICKBOOKS_REPLACED")

    def test_03_balance_sheet_endpoint(self):
        res = self.invoke_endpoint("/api/v1/balance_sheet", "GET")
        self.assertTrue(res["is_balanced"])

    def test_04_cash_flow_endpoint(self):
        res = self.invoke_endpoint("/api/v1/cash_flow", "GET")
        self.assertGreater(res["net_cash_flow"], 0)

    def test_05_ap_aging_endpoint(self):
        res = self.invoke_endpoint("/api/v1/ap/aging", "GET")
        self.assertIn("total_ap", res)

    def test_06_orchestrator_audit_endpoint(self):
        res = self.invoke_endpoint("/api/v1/orchestrator/audit", "GET")
        self.assertTrue(res["trial_balance_balanced"])
        self.assertEqual(res["system_health_status"], "AUDIT_PASSED")

    def test_07_orchestrator_statement_endpoint(self):
        res = self.invoke_endpoint("/api/v1/orchestrator/statement", "GET")
        self.assertIn("cores_status", res)
        self.assertIn("financial_audit", res)

    def test_08_fixed_assets_depreciate_endpoint(self):
        res = self.invoke_endpoint("/api/v1/fixed_assets/depreciate", "POST", {"cost": 240000.0, "salvage": 40000.0, "useful_life_years": 5})
        self.assertEqual(res["annual_depreciation"], 40000.0)
        self.assertEqual(res["status"], "NETSUITE_FIXED_ASSETS_VERIFIED")

    def test_09_inventory_fifo_cogs_endpoint(self):
        res = self.invoke_endpoint("/api/v1/inventory/fifo_cogs", "POST", {"units_sold": 150})
        self.assertEqual(res["total_cogs"], 7750.0)
        self.assertEqual(res["status"], "QUICKBOOKS_FIFO_VERIFIED")

    def test_10_subsidiary_consolidate_endpoint(self):
        res = self.invoke_endpoint("/api/v1/subsidiary/consolidate", "POST", {"us_revenue": 500000.0, "eu_revenue": 250000.0, "intercompany_sales": 50000.0})
        self.assertEqual(res["consolidated_revenue"], 700000.0)
        self.assertEqual(res["status"], "NETSUITE_MULTI_ENTITY_CONSOLIDATED")

    def test_11_metered_billing_calculate_endpoint(self):
        res = self.invoke_endpoint("/api/v1/metered_billing/calculate", "POST", {"base_subscription": 99.0, "api_calls_used": 20000})
        self.assertEqual(res["total_bill_usd"], 124.0)
        self.assertEqual(res["status"], "STRIPE_METERED_BILLING_VERIFIED")

    def test_12_dunning_retry_endpoint(self):
        res = self.invoke_endpoint("/api/v1/dunning/retry", "POST", {"subscriber_id": "sub_101", "retry_attempt": 1})
        self.assertEqual(res["dunning_action"], "Immediate Retry")
        self.assertEqual(res["status"], "REVENUECAT_DUNNING_ACTIVE")

    def test_13_tax_calculate_endpoint(self):
        res = self.invoke_endpoint("/api/v1/tax/calculate", "POST", {"amount": 100.0, "country_code": "DE"})
        self.assertEqual(res["tax_amount"], 19.0)
        self.assertEqual(res["status"], "AVALARA_STRIPE_TAX_VERIFIED")

    def test_14_pto_accrual_endpoint(self):
        res = self.invoke_endpoint("/api/v1/pto/accrual", "POST", {"hours_worked": 160.0})
        self.assertEqual(res["accrued_pto_hours"], 8.0)
        self.assertEqual(res["status"], "GUSTO_PTO_ACCRUED")

    def test_15_expense_ocr_match_endpoint(self):
        res = self.invoke_endpoint("/api/v1/expense/ocr_match", "POST", {"merchant": "AWS", "amount": 250.0})
        self.assertEqual(res["auto_category"], "5030 - Cloud Compute")
        self.assertEqual(res["status"], "EXPENSIFY_OCR_MATCHED")

    def test_16_po_match_3way_endpoint(self):
        res = self.invoke_endpoint("/api/v1/po/match_3way", "POST", {"po_amount": 5000.0, "receiving_slip_amount": 5000.0, "vendor_invoice_amount": 5000.0})
        self.assertTrue(res["is_3way_matched"])
        self.assertEqual(res["status"], "BILL_COM_3WAY_MATCHED")

    def test_17_xfin_settle_endpoint(self):
        res = self.invoke_endpoint("/api/v1/xfin/settle", "POST", {"user_id": "usr_x1", "fiat_amount": 100.0, "currency": "EUR"})
        self.assertEqual(res["status"], "SETTLED")
        self.assertEqual(res["settled_usd"], 108.70)

    def test_18_xfin_hedge_endpoint(self):
        res = self.invoke_endpoint("/api/v1/xfin/hedge", "POST", {"currency": "EUR", "amount_usd": 50000.0})
        self.assertEqual(res["status"], "ACTIVE_HEDGE")

    def test_19_aura_credit_risk_endpoint(self):
        res = self.invoke_endpoint("/api/v1/aura/credit_risk", "POST", {"user_id": "usr_a1", "payment_history_ratio": 0.98, "subscription_cost": 299.0})
        self.assertEqual(res["underwriting"]["status"], "APPROVED")

    def test_20_pulse_churn_risk_endpoint(self):
        res = self.invoke_endpoint("/api/v1/pulse/churn_risk", "POST", {"user_id": "usr_p1", "engagement_score": 0.85})
        self.assertIn("churn_risk", res)
        self.assertIn("discounted_ltv", res)

    def test_21_mint_tokens_endpoint(self):
        res = self.invoke_endpoint("/api/v1/mint/tokens", "POST", {"user_id": "usr_m1", "fiat_amount_usd": 100.0, "action": "mint"})
        self.assertEqual(res["system"], "MINT")
        self.assertGreater(res["tokens_minted"], 0)

    def test_22_grid_device_endpoint(self):
        res = self.invoke_endpoint("/api/v1/grid/device", "POST", {"device_id": "dev_g1", "device_type": "WEAR_OS_WATCH"})
        self.assertEqual(res["registration"]["status"], "ONLINE")

    def test_23_nexs_offering_endpoint(self):
        res = self.invoke_endpoint("/api/v1/nexs/offering", "POST", {"user_id": "usr_n1", "country_code": "BR", "base_usd_price": 20.0})
        self.assertEqual(res["adapted_usd_price"], 9.0)

    def test_24_orchestrator_lifecycle_endpoint(self):
        res = self.invoke_endpoint("/api/v1/orchestrator/lifecycle", "POST", {
            "user_id": "usr_full_vip", "country_code": "DE", "device_id": "dev_watch_de", "fiat_amount": 99.99, "currency": "EUR"
        })
        self.assertEqual(res["status"], "NEXTGEN_PIPELINE_SUCCESS")

    def test_25_gemini_chat_endpoint(self):
        res = self.invoke_endpoint("/api/v1/gemini/chat", "POST", {"message": "Audit cores"})
        self.assertIn("reply", res)

    def test_26_quickbooks_endpoints(self):
        pnl = self.invoke_endpoint("/api/v1/quickbooks/pnl", "GET")
        self.assertEqual(pnl["net_income"], 331246.0)
        proj = self.invoke_endpoint("/api/v1/quickbooks/project", "POST", {"project_id": "PRJ-101"})
        self.assertEqual(proj["status"], "QUICKBOOKS_JOB_COSTING_ACTIVE")

    def test_27_stripe_endpoints(self):
        pay = self.invoke_endpoint("/api/v1/stripe/payment", "POST", {"amount": 100.0, "currency": "USD"})
        self.assertIn("SETTLEMENT_SUCCESS", pay["status"])
        coupon = self.invoke_endpoint("/api/v1/stripe/coupon", "POST", {"code": "OFF50", "percent_off": 50.0})
        self.assertEqual(coupon["code"], "OFF50")

    def test_28_revenuecat_endpoints(self):
        ent = self.invoke_endpoint("/api/v1/revenuecat/entitlements", "GET")
        self.assertEqual(ent["status"], "REVENUECAT_ENTITLED")
        exp = self.invoke_endpoint("/api/v1/revenuecat/experiment", "POST", {"experiment_id": "exp_v2"})
        self.assertEqual(exp["status"], "REVENUECAT_EXPERIMENT_ACTIVE")

    def test_29_netsuite_endpoint(self):
        res = self.invoke_endpoint("/api/v1/netsuite/asc606", "POST", {"total_contract_value": 120000.0})
        self.assertEqual(res["recognized_month_1"], 9863.01)

    def test_30_xero_endpoint(self):
        res = self.invoke_endpoint("/api/v1/xero/forecast", "POST", {"current_cash": 100000.0, "expected_ar": 50000.0, "expected_ap": 20000.0})
        self.assertEqual(res["projected_30day_cash"], 130000.0)

    def test_31_gusto_endpoint(self):
        res = self.invoke_endpoint("/api/v1/gusto/payroll", "POST", {"gross_payroll": 10000.0})
        self.assertEqual(res["federal_tax"], 2200.0)

    def test_32_bill_com_endpoint(self):
        res = self.invoke_endpoint("/api/v1/bill/ap_approval", "POST", {"bill_id": "BILL-101", "amount": 15000.0})
        self.assertEqual(res["approval_level_2"], "APPROVED (CFO)")

    def test_33_expensify_endpoint(self):
        res = self.invoke_endpoint("/api/v1/expensify/audit", "POST", {"employee_id": "EMP-1", "expenses": [{"merchant": "AWS", "amount": 100.0, "receipt_ocr": True}]})
        self.assertEqual(res["reimbursement_status"], "APPROVED_FOR_PAYOUT")

    def test_34_plaid_endpoint(self):
        res = self.invoke_endpoint("/api/v1/plaid/balance", "GET")
        self.assertEqual(res["available_balance"], 1420500.0)

    def test_35_avalara_endpoint(self):
        res = self.invoke_endpoint("/api/v1/avalara/tax_nexus", "POST", {"amount": 100.0, "state_or_country": "US_CA"})
        self.assertEqual(res["tax_due"], 8.75)

    def test_36_freshbooks_endpoint(self):
        res = self.invoke_endpoint("/api/v1/freshbooks/time_invoice", "POST", {"client": "Client A", "hourly_rate": 150.0, "hours_logged": 10.0})
        self.assertEqual(res["total_invoiced"], 1500.0)

    def test_37_mega11_audit_endpoint(self):
        res = self.invoke_endpoint("/api/v1/mega11/audit", "GET")
        self.assertIn("FULLY_OPERATIONAL", res["status"])

    def test_39_marketplace_apps_endpoint(self):
        res_get = self.invoke_endpoint("/api/v1/marketplace/apps?category=Accounting%20%26%20Tax", "GET")
        self.assertEqual(res_get["status"], "MARKETPLACE_APPS_RETRIEVED")
        self.assertEqual(res_get["total"], 20)

        res_post = self.invoke_endpoint("/api/v1/marketplace/apps", "POST", {"search_query": "Stripe"})
        self.assertEqual(res_post["status"], "MARKETPLACE_APPS_RETRIEVED")
        self.assertTrue(any(a["name"] == "Stripe Payments" for a in res_post["apps"]))

    def test_40_marketplace_connect_endpoint(self):
        res = self.invoke_endpoint("/api/v1/marketplace/connect", "POST", {"app_id": "app_002"})
        self.assertEqual(res["sync_status"], "CONNECTED")
        self.assertEqual(res["status"], "MARKETPLACE_APP_CONNECTED_SUCCESSFULLY")
        self.assertIn("revenuecat_integration", res)
        self.assertTrue(res["revenuecat_integration"]["entitlements_bridged"])
        self.assertIn("six_core_substrate_sync", res)
        self.assertEqual(res["six_core_substrate_sync"]["cores_entangled"], 6)

    def test_41_marketplace_recommend_ai_endpoint(self):
        res = self.invoke_endpoint("/api/v1/marketplace/recommend_ai", "POST", {"business_type": "SaaS_Subscription"})
        self.assertEqual(res["status"], "AI_RECOMMENDATION_ENGINE_ACTIVE")
        self.assertEqual(len(res["neural_recommendations"]), 6)
        self.assertIn("six_core_substrate_optimization", res)
        self.assertEqual(res["six_core_substrate_optimization"]["cores_entangled"], 6)
        self.assertIn("revenuecat_integration", res)

    def test_42_marketplace_connect_get_query_params(self):
        res = self.invoke_endpoint("/api/v1/marketplace/connect?app_id=app_021", "GET")
        self.assertEqual(res["sync_status"], "CONNECTED")
        self.assertEqual(res["status"], "MARKETPLACE_APP_CONNECTED_SUCCESSFULLY")
        self.assertEqual(res["six_core_substrate_sync"]["cores_entangled"], 6)

    def test_44_inner_ai_status_endpoint(self):
        res = self.invoke_endpoint("/api/v1/inner_ai/status", "GET")
        self.assertEqual(res["engine_status"], "ONLINE")
        self.assertEqual(res["subsystem"], "SovereignInnerAIEngine")
        self.assertGreaterEqual(res["registered_app_skills_count"], 6)

    def test_45_inner_ai_route_endpoint_post(self):
        body = {"prompt": "Calculate FX triangular arbitrage for EUR/USD/GBP"}
        res = self.invoke_endpoint("/api/v1/inner_ai/route", "POST", body)
        self.assertEqual(res["routed_intent"], "FINTECH_ARBITRAGE")
        self.assertEqual(res["target_app_skill"], "fx_triangular_arbitrage")
        self.assertGreater(res["confidence_score"], 0.20)

    def test_46_inner_ai_execute_app_skill_endpoint_post(self):
        body = {
            "skill_id": "fx_triangular_arbitrage",
            "params": {
                "rate_eur_usd": 1.0850,
                "rate_usd_gbp": 0.7850,
                "rate_gbp_eur": 1.1780,
                "notional_principal": 500000.0
            }
        }
        res = self.invoke_endpoint("/api/v1/inner_ai/execute_app_skill", "POST", body)
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["skill_id"], "fx_triangular_arbitrage")
        self.assertIn("profit_margin_pct", res["result"])

    def test_47_inner_ai_route_and_execute_get_query_params(self):
        res_route = self.invoke_endpoint("/api/v1/inner_ai/route?prompt=Underwrite%20credit%20risk", "GET")
        self.assertEqual(res_route["routed_intent"], "RISK_UNDERWRITING")

        res_exec = self.invoke_endpoint("/api/v1/inner_ai/execute_app_skill?skill_id=credit_risk_underwriting", "GET")
        self.assertEqual(res_exec["status"], "SUCCESS")
        self.assertEqual(res_exec["skill_id"], "credit_risk_underwriting")


    def assert_rfc3339_and_zero_float_drift(self, res: dict):
        self.assertIsNotNone(res)
        self.assertIn("timestamp", res)
        ts = str(res["timestamp"])
        self.assertTrue("T" in ts and (ts.endswith("Z") or "+" in ts or "-" in ts[10:]))

        def check_floats(obj):
            if isinstance(obj, float):
                s = str(obj)
                if "." in s and not ("e" in s.lower()):
                    decimals = len(s.split(".")[1])
                    self.assertLessEqual(decimals, 6)
            elif isinstance(obj, dict):
                for v in obj.values():
                    check_floats(v)
            elif isinstance(obj, list):
                for item in obj:
                    check_floats(item)

        check_floats(res)

    def test_48_gemini_enterprise_endpoints_rfc3339_and_zero_drift(self):
        status = self.invoke_endpoint("/api/v1/gemini_enterprise/status", "GET")
        self.assert_rfc3339_and_zero_float_drift(status)

        qb = self.invoke_endpoint("/api/v1/gemini_enterprise/quickbooks", "POST", {"action": "sox_tax", "amount": 10000.0})
        self.assert_rfc3339_and_zero_float_drift(qb)

        sf = self.invoke_endpoint("/api/v1/gemini_enterprise/salesforce", "POST", {"action": "email_cadence", "name": "Jane", "company": "Apex"})
        self.assert_rfc3339_and_zero_float_drift(sf)

        bill = self.invoke_endpoint("/api/v1/gemini_enterprise/billcom", "POST", {"action": "zk_wire"})
        self.assert_rfc3339_and_zero_float_drift(bill)

        sq = self.invoke_endpoint("/api/v1/gemini_enterprise/square_rc", "POST", {"action": "pos_charge", "amount": 250.0})
        self.assert_rfc3339_and_zero_float_drift(sq)

        wf = self.invoke_endpoint("/api/v1/gemini_enterprise/workflow", "POST", {"acv": 50000.0})
        self.assert_rfc3339_and_zero_float_drift(wf)

    def test_49_polymath_endpoints_rfc3339_and_zero_drift(self):
        status = self.invoke_endpoint("/api/v1/polymath/status", "GET")
        self.assert_rfc3339_and_zero_float_drift(status)

        gateways = self.invoke_endpoint("/api/v1/polymath/university_gateways", "GET")
        self.assert_rfc3339_and_zero_float_drift(gateways)

        spec = self.invoke_endpoint("/api/v1/polymath/spectral_confidence", "GET")
        self.assert_rfc3339_and_zero_float_drift(spec)

        ingest = self.invoke_endpoint("/api/v1/polymath/machine_ingest", "POST", {"title": "Quantum Systems", "duration": 45.0})
        self.assert_rfc3339_and_zero_float_drift(ingest)

        nav = self.invoke_endpoint("/api/v1/polymath/autonomous_navigate", "POST", {"agent": "SILVER NOVA", "action": "set_playback_rate", "value": 4.0, "reason": "High density"})
        self.assert_rfc3339_and_zero_float_drift(nav)

        curr = self.invoke_endpoint("/api/v1/polymath/build_curriculum", "POST", {"topic": "AI Cryptography"})
        self.assert_rfc3339_and_zero_float_drift(curr)

        rec = self.invoke_endpoint("/api/v1/polymath/recursive_search", "POST", {"gap_name": "Lattice reduction"})
        self.assert_rfc3339_and_zero_float_drift(rec)

    def test_50_revenuecat_endpoints_rfc3339_and_zero_drift(self):
        ent = self.invoke_endpoint("/api/v1/revenuecat/entitlements", "GET")
        self.assert_rfc3339_and_zero_float_drift(ent)

        chk = self.invoke_endpoint("/api/v1/revenuecat/check_entitlement", "GET")
        self.assert_rfc3339_and_zero_float_drift(chk)

        paywall = self.invoke_endpoint("/api/v1/revenuecat/paywall", "GET")
        self.assert_rfc3339_and_zero_float_drift(paywall)

        rules = self.invoke_endpoint("/api/v1/revenuecat/paywall_rules", "GET")
        self.assert_rfc3339_and_zero_float_drift(rules)

        churn = self.invoke_endpoint("/api/v1/revenuecat/churn_telemetry", "GET")
        self.assert_rfc3339_and_zero_float_drift(churn)

        usage = self.invoke_endpoint("/api/v1/revenuecat/usage", "GET")
        self.assert_rfc3339_and_zero_float_drift(usage)

        exp = self.invoke_endpoint("/api/v1/revenuecat/experiment", "GET")
        self.assert_rfc3339_and_zero_float_drift(exp)

        wh = self.invoke_endpoint("/api/v1/revenuecat/webhook", "GET")
        self.assert_rfc3339_and_zero_float_drift(wh)

    def test_51_native_endpoints_rfc3339_and_zero_drift(self):
        pay = self.invoke_endpoint("/api/v1/native/pay", "POST", {"amount": 2500.0, "currency": "USD"})
        self.assert_rfc3339_and_zero_float_drift(pay)

        acct = self.invoke_endpoint("/api/v1/native/accounting", "POST", {"amount": 2500.0, "description": "GL Posting"})
        self.assert_rfc3339_and_zero_float_drift(acct)

        sign = self.invoke_endpoint("/api/v1/native/sign", "POST", {"document_name": "SLA Contract", "signer_email": "cfo@apex.com"})
        self.assert_rfc3339_and_zero_float_drift(sign)

        ap_exp = self.invoke_endpoint("/api/v1/native/ap_expense", "POST", {"vendor_or_merchant": "AWS", "amount": 1250.0})
        self.assert_rfc3339_and_zero_float_drift(ap_exp)

        payroll = self.invoke_endpoint("/api/v1/native/payroll_tax", "POST", {"gross_payroll": 148500.0, "state": "CA"})
        self.assert_rfc3339_and_zero_float_drift(payroll)

    def test_52_default_landing_route_index_html(self):
        code_root, headers_root, body_root = self.invoke_raw_endpoint("/", "GET")
        self.assertEqual(code_root, 200)
        self.assertEqual(headers_root.get("Content-Type"), "text/html; charset=utf-8")
        self.assertIn(b"SOVEREIGN", body_root)
        self.assertIn(b"ENTERPRISE OS", body_root)

        code_idx, headers_idx, body_idx = self.invoke_raw_endpoint("/index.html", "GET")
        self.assertEqual(code_idx, 200)
        self.assertEqual(headers_idx.get("Content-Type"), "text/html; charset=utf-8")
        self.assertIn(b"SOVEREIGN", body_idx)
        self.assertIn(b"ENTERPRISE OS", body_idx)

    def test_53_unified_200apps_endpoints(self):
        catalog = self.invoke_endpoint("/api/v1/200apps/catalog", "GET")
        self.assertEqual(catalog["status"], "200_APPS_CATALOG_RETRIEVED")
        self.assertIn("apps", catalog)

        app_list = self.invoke_endpoint("/api/v1/200apps/list", "GET")
        self.assertEqual(app_list["status"], "200_APPS_CATALOG_RETRIEVED")
        self.assertIn("apps", app_list)

        app_detail = self.invoke_endpoint("/api/v1/200apps/detail/app_001", "GET")
        self.assertIn("app_id", app_detail)
        self.assertEqual(app_detail["app_id"], "app_001")


if __name__ == "__main__":
    unittest.main()




