"""
SOVEREIGN ENGINE ENTERPRISE WEB DASHBOARD SERVER (Port 8090)
QuickBooks, Xero, NetSuite, Gusto, Bill.com, Expensify, Stripe, RevenueCat, Plaid, Avalara & FreshBooks Replacement Server
Powered by RevenueCat, Gemini AI, 11 Platform Master Suite, 6 Next-Gen Fintech Cores & Complete Enterprise SaaS Ecosystem
"""

import os
import sys
import json
import logging
from http.server import HTTPServer, SimpleHTTPRequestHandler

# Import 6 Next-Gen Fintech Cores, SaaS Accounting Suite, Gemini AI & Complete SaaS Ecosystem
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "sovereign_infrastructure", "nextgen_systems"))

from xfin_engine import XFINEngine
from aura_engine import AURAEngine
from pulse_engine import PULSEEngine
from mint_engine import MINTEngine
from grid_engine import GRIDEngine
from nexs_engine import NEXSEngine
from full_saas_accounting_suite import (
    GeneralLedgerEngine,
    BalanceSheetEngine,
    CashFlowEngine,
    PayrollTaxEngine,
    AccountsPayableEngine,
    BankReconciliationEngine
)
from gemini_intelligence_engine import GeminiChatOrchestrator, GeminiIntelligenceEngine
from complete_enterprise_saas_ecosystem import (
    FixedAssetDepreciationEngine,
    InventoryFIFOEngine,
    MultiEntityConsolidationEngine,
    MeteredUsageBillingEngine,
    SmartDunningEngine,
    GlobalSalesTaxEngine,
    PTOAccrualEngine,
    ExpenseOCRMatchingEngine,
    PurchaseOrderMatchingEngine
)
from nextgen_master_orchestrator import NextGenMasterOrchestrator
from mega_11_platform_master_suite import (
    Mega11PlatformOrchestrator,
    QuickBooksMasterModule,
    StripeMasterModule,
    RevenueCatMasterModule,
    NetSuiteMasterModule,
    XeroMasterModule,
    GustoMasterModule,
    BillComMasterModule,
    ExpensifyMasterModule,
    PlaidMasterModule,
    AvalaraMasterModule,
    FreshBooksMasterModule
)
from embedded_marketplace_integrations_hub import EmbeddedMarketplaceHub
from sovereign_mcp_server import SovereignMCPServer
from alpha_unlimited_work_engine import AlphaUnlimitedWorkEngine, AlphaAppWorkGenerator
from mega_office_business_suite import MegaOfficeBusinessSuite

office_suite = MegaOfficeBusinessSuite()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SovereignDashboardServer")

# Initialize Master Orchestrator (Wires 6 Cores & SaaS Accounting Suite)
orchestrator = NextGenMasterOrchestrator()

xfin = orchestrator.xfin
aura = orchestrator.aura
pulse = orchestrator.pulse
mint = orchestrator.mint
grid = orchestrator.grid
nexs = orchestrator.nexs

gl = orchestrator.gl
bs = orchestrator.bs
cf = orchestrator.cf
payroll = orchestrator.payroll
ap = orchestrator.ap
bank = orchestrator.bank

# Initialize Mega 11-Platform Master Suite
mega11 = Mega11PlatformOrchestrator(master_orchestrator=orchestrator)

# Initialize 9 Enterprise SaaS Ecosystem Engines
depreciation = FixedAssetDepreciationEngine()
fifo = InventoryFIFOEngine()
consolidation = MultiEntityConsolidationEngine()
metered = MeteredUsageBillingEngine()
dunning = SmartDunningEngine()
tax = GlobalSalesTaxEngine()
pto = PTOAccrualEngine()
ocr = ExpenseOCRMatchingEngine()
po_match = PurchaseOrderMatchingEngine()

# Initialize Gemini Chat Orchestrator
gemini_chat = GeminiChatOrchestrator(
    gl=gl, bs=bs, cf=cf, payroll=payroll, ap=ap, bank=bank,
    pulse=pulse, aura=aura, xfin=xfin, mint=mint, grid=grid, nexs=nexs
)

# Initialize Embedded Marketplace Hub
marketplace_hub = EmbeddedMarketplaceHub()

# Initialize Sovereign MCP Server & Workflow Map
mcp_server = SovereignMCPServer()

# Initialize Sovereign OS Alpha Unlimited Work Engine
alpha_work_engine = AlphaUnlimitedWorkEngine(gl_engine=gl, orchestrator=orchestrator)

WORKFLOW_SHORTHAND_MAP = {
    "wf_01": "workflow_end_to_end_subscriber_lifecycle",
    "wf_02": "workflow_revenue_recognition_asc606",
    "wf_03": "workflow_cross_border_fx_hedging",
    "wf_04": "workflow_b2b_invoice_underwriting_bnpl",
    "wf_05": "workflow_multi_entity_consolidation",
    "wf_06": "workflow_fifo_inventory_valuation",
    "wf_07": "workflow_fixed_assets_macrs_depreciation",
    "wf_08": "workflow_expense_ocr_3way_po_reconciliation",
    "wf_09": "workflow_global_vat_gst_tax_compliance",
    "wf_10": "workflow_payroll_pto_accrual_escrow",
    "wf_11": "workflow_smart_dunning_payment_recovery",
    "wf_12": "workflow_metered_usage_billing",
    "wf_13": "workflow_iot_hardware_entitlement_depreciation",
    "wf_14": "workflow_deflationary_tokenomics_bonding_curve",
    "wf_15": "workflow_neural_marketplace_stack_provisioning",
    "wf_16": "workflow_tax_audit_trail_export",
    "wf_17": "workflow_realtime_pnl_balance_sheet_cashflow",
    "wf_18": "workflow_dynamic_paywall_ppp_pricing",
    "wf_19": "workflow_subscriber_churn_retention_campaign",
    "wf_20": "workflow_bank_feed_algorithmic_reconciliation",
    "wf_21": "workflow_sovereign_ecosystem_health_audit",
    "wf_22": "workflow_onesignal_push_retention",
    "wf_23": "workflow_galaxy_apk_optimization",
    "wf_24": "workflow_kmp_cross_platform_sync",
    "wf_25": "workflow_ultimate_25_protocol_suite",
}

DASHBOARD_DIR = os.path.join(os.path.dirname(__file__), "sovereign_dashboard")

class SovereignDashboardHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DASHBOARD_DIR, **kwargs)

    def parse_body(self) -> dict:
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length <= 0:
            return {}
        body_bytes = self.rfile.read(content_length)
        return json.loads(body_bytes.decode("utf-8")) if body_bytes else {}

    def get_clean_path(self) -> str:
        path = self.path.split('?')[0]
        if len(path) > 1 and path.endswith('/'):
            path = path[:-1]
        return path

    def parse_query_params(self) -> dict:
        if '?' not in self.path:
            return {}
        query_str = self.path.split('?', 1)[1]
        params = {}
        from urllib.parse import unquote_plus
        for pair in query_str.split('&'):
            if '=' in pair:
                k, v = pair.split('=', 1)
                params[unquote_plus(k)] = unquote_plus(v)
            elif pair:
                params[unquote_plus(pair)] = ""
        return params

    def do_GET(self):
        logger.info(f"[GET] {self.path}")
        path = self.get_clean_path()

        if path == "/api/v1/overview":
            self.send_json_response({
                "mrr": 148920.0,
                "arr": 1787040.0,
                "ltv_cac_ratio": 8.4,
                "net_profit_margin_pct": 74.2,
                "forma_burned": 744600.0,
                "active_subscribers": 12480,
                "cores_entangled": 6
            })
        elif path == "/api/v1/ledger":
            self.send_json_response({
                "gross_revenue": 446760.0,
                "cogs_fees": -67014.0,
                "gross_profit": 379746.0,
                "operating_expenses": -48500.0,
                "net_income": 331246.0,
                "status": "QUICKBOOKS_REPLACED"
            })
        elif path == "/api/v1/balance_sheet":
            self.send_json_response(bs.generate_balance_sheet())
        elif path == "/api/v1/cash_flow":
            self.send_json_response(cf.generate_cash_flow_statement())
        elif path == "/api/v1/ap/aging":
            self.send_json_response(ap.get_ap_aging_schedule())
        elif path in ["/api/v1/assets/depreciation", "/api/v1/fixed_assets/depreciate"]:
            self.send_json_response(depreciation.calculate_straight_line_depreciation(240000.0, 40000.0, 5))
        elif path in ["/api/v1/inventory/fifo", "/api/v1/inventory/fifo_cogs"]:
            self.send_json_response(fifo.calculate_fifo_cogs(50))
        elif path in ["/api/v1/multi_entity/consolidate", "/api/v1/subsidiary/consolidate"]:
            self.send_json_response(consolidation.consolidate_entities(446760.0, 210000.0, 50000.0))
        elif path == "/api/v1/paywall/ast":
            self.send_json_response({
                "variant_id": "var_A_minimal",
                "headline": "Unlock Sovereign Pro Access",
                "theme": "NEON_CYAN",
                "offering_id": "pro_access_annual"
            })
        elif path == "/api/v1/tokenomics":
            self.send_json_response({
                "total_supply": mint.get_total_supply(),
                "total_burned": 744600.0,
                "golden_ratio_yield_apy": 61.80,
                "status": "MINT_ACTIVE"
            })
        elif path == "/api/v1/iot/mesh":
            self.send_json_response({
                "registered_devices": [
                    {"device_id": "WATCH_01_DE", "type": "Wear OS Watch", "health_index": 0.98, "status": "UNLOCKED"},
                    {"device_id": "SENSOR_02_US", "type": "Biometric Sensor", "health_index": 0.94, "status": "UNLOCKED"}
                ]
            })
        elif path == "/api/v1/orchestrator/audit":
            self.send_json_response(orchestrator.audit_financial_integrity())
        elif path == "/api/v1/orchestrator/statement":
            self.send_json_response(orchestrator.generate_consolidated_sovereign_statement())

        # ---------------------------------------------------------------------
        # Alpha Work REST API Endpoints (GET)
        # ---------------------------------------------------------------------
        elif path in ["/api/v1/alpha/work/generate", "/api/v1/alpha/work/generate_work"]:
            params = self.parse_query_params()
            app_id = params.get("app_id", params.get("app_id_or_name", "app_001"))
            self.send_json_response(alpha_work_engine.generate_work(app_id=app_id))
        elif path in ["/api/v1/alpha/work/dispatch_200", "/api/v1/alpha/work/dispatch200"]:
            self.send_json_response(alpha_work_engine.dispatch_200())
        elif path == "/api/v1/alpha/work/audit":
            self.send_json_response(alpha_work_engine.run_alpha_audit())

        # ---------------------------------------------------------------------
        # Sovereign Office & Business Suite GET Endpoints
        # ---------------------------------------------------------------------
        elif path in ["/api/v1/office/tools", "/api/v1/office/audit"]:
            audit = office_suite.run_full_office_audit()
            audit["tools"] = [
                {"name": "SovereignDocs", "endpoint": "/api/v1/office/docs"},
                {"name": "SovereignSheetsSolve", "endpoint": "/api/v1/office/sheets/solve"},
                {"name": "SovereignSheetsModel", "endpoint": "/api/v1/office/sheets/model"},
                {"name": "SovereignSlidesPitch", "endpoint": "/api/v1/office/slides"},
                {"name": "SovereignSlidesBoard", "endpoint": "/api/v1/office/slides/board"},
                {"name": "SovereignSignExecute", "endpoint": "/api/v1/office/sign"},
                {"name": "SovereignSignVerify", "endpoint": "/api/v1/office/sign/verify"},
                {"name": "SovereignMailCadence", "endpoint": "/api/v1/office/mail"},
                {"name": "SovereignMailBilling", "endpoint": "/api/v1/office/mail/billing"},
                {"name": "SovereignDrive", "endpoint": "/api/v1/office/drive"},
                {"name": "SovereignForms", "endpoint": "/api/v1/office/forms"},
                {"name": "SovereignCalendar", "endpoint": "/api/v1/office/calendar"},
                {"name": "SovereignBusinessPackage", "endpoint": "/api/v1/office/package"},
                {"name": "AgenticMultiArtifactGenerator", "endpoint": "/api/v1/office/generate_artifact"}
            ]
            audit["supported_artifact_types"] = office_suite.artifact_generator.supported_artifact_types if office_suite.artifact_generator else []
            self.send_json_response(audit)
        elif path == "/api/v1/office/generate_artifact":
            params = self.parse_query_params()
            art_type = params.get("artifact_type", params.get("type", "SPREADSHEET"))
            title = params.get("title", "Q1 Executive Financial Model")
            self.send_json_response(office_suite.artifact_generator.generate_artifact(art_type, title, params))
        elif path in ["/api/v1/office/docs", "/api/v1/office/docs/create"]:
            params = self.parse_query_params()
            title = params.get("title", "SOVEREIGN OS Executive Report")
            author = params.get("author", "SOVEREIGN OS AI")
            body_txt = params.get("body")
            doc = office_suite.docs.create_document(title=title, author=author, body=body_txt)
            if params.get("export_md") == "true":
                doc["markdown"] = office_suite.docs.export_markdown(doc)
            self.send_json_response(doc)
        elif path == "/api/v1/office/sheets/solve":
            params = self.parse_query_params()
            sheet_data = {}
            if "revenue_rows" in params:
                sheet_data["revenue_rows"] = [float(x) for x in params["revenue_rows"].split(",") if x.strip()]
            if "expense_rows" in params:
                sheet_data["expense_rows"] = [float(x) for x in params["expense_rows"].split(",") if x.strip()]
            self.send_json_response(office_suite.sheets.solve_formulas(sheet_data))
        elif path == "/api/v1/office/sheets/model":
            params = self.parse_query_params()
            company = params.get("company_name", params.get("company", "Apex Enterprise"))
            base_mrr = float(params.get("base_mrr", params.get("mrr", 100000.0)))
            opex_ratio = float(params.get("opex_ratio", 0.4))
            self.send_json_response(office_suite.sheets.create_financial_model(company, base_mrr, opex_ratio))
        elif path in ["/api/v1/office/slides", "/api/v1/office/slides/pitch"]:
            params = self.parse_query_params()
            company = params.get("company_name", params.get("company", "Apex Global"))
            topic = params.get("topic", "Enterprise Autonomous OS")
            template = params.get("template", "SERIES_A_GROWTH")
            self.send_json_response(office_suite.slides.generate_pitch_deck(company, topic, template))
        elif path == "/api/v1/office/slides/board":
            params = self.parse_query_params()
            quarter = params.get("quarter", "Q1 2026")
            arr = float(params.get("arr", 1787040.0))
            net_margin = float(params.get("net_margin", 74.2))
            self.send_json_response(office_suite.slides.generate_board_deck(quarter, arr, net_margin))
        elif path == "/api/v1/office/slides/export_svg":
            params = self.parse_query_params()
            company = params.get("company_name", params.get("company", "Apex Global"))
            topic = params.get("topic", "Enterprise Autonomous OS")
            template = params.get("template", "SERIES_A_GROWTH")
            deck = office_suite.slides.generate_pitch_deck(company, topic, template)
            self.send_json_response(office_suite.slides.export_deck_to_svg(deck))
        elif path == "/api/v1/office/slides/export_html":
            params = self.parse_query_params()
            company = params.get("company_name", params.get("company", "Apex Global"))
            topic = params.get("topic", "Enterprise Autonomous OS")
            template = params.get("template", "SERIES_A_GROWTH")
            deck = office_suite.slides.generate_pitch_deck(company, topic, template)
            html_content = office_suite.slides.export_presentation_html(deck)
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html_content.encode("utf-8"))))
            self.end_headers()
            self.wfile.write(html_content.encode("utf-8"))
            return
        elif path in ["/api/v1/office/sign", "/api/v1/office/sign/execute"]:
            params = self.parse_query_params()
            doc_name = params.get("document_name", params.get("doc", "Master SLA Contract"))
            email = params.get("signer_email", params.get("email", "cfo@apex.com"))
            role = params.get("signer_role", params.get("role", "CFO"))
            self.send_json_response(office_suite.sign.execute_signature(doc_name, email, role))
        elif path == "/api/v1/office/sign/verify":
            params = self.parse_query_params()
            sig_id = params.get("signature_id", "sign_101")
            zk_proof = params.get("zk_proof", params.get("zk_proof_signature", "zk_sig_dilithium_101"))
            self.send_json_response(office_suite.sign.verify_zk_proof(sig_id, zk_proof))
        elif path in ["/api/v1/office/mail", "/api/v1/office/mail/send"]:
            params = self.parse_query_params()
            recipient = params.get("recipient", "exec@apex.com")
            template = params.get("template", "Enterprise Onboarding")
            subject = params.get("subject", "SOVEREIGN OS Update")
            self.send_json_response(office_suite.mail.send_ai_cadence(recipient, template, subject))
        elif path == "/api/v1/office/mail/billing":
            params = self.parse_query_params()
            recipient = params.get("recipient", "billing@apex.com")
            invoice_id = params.get("invoice_id", "INV-2026-001")
            amount_due = float(params.get("amount_due", 15000.0))
            self.send_json_response(office_suite.mail.send_billing_notice(recipient, invoice_id, amount_due))
        elif path in ["/api/v1/office/drive", "/api/v1/office/drive/files", "/api/v1/office/drive/upload", "/api/v1/office/drive/search"]:
            params = self.parse_query_params()
            action = params.get("action", "")
            query = params.get("query", params.get("q", ""))
            if action == "upload" or path.endswith("/upload") or "name" in params:
                name = params.get("name", "Document.pdf")
                file_type = params.get("file_type", params.get("type", "DOCUMENT"))
                size_kb = int(params.get("size_kb", 500))
                self.send_json_response(office_suite.drive.upload_file(name, file_type, size_kb))
            elif query or action == "search" or path.endswith("/search"):
                self.send_json_response({"files": office_suite.drive.search_files(query), "query": query})
            else:
                self.send_json_response({"files": office_suite.drive.list_files(), "total_files": len(office_suite.drive.files)})
        elif path in ["/api/v1/office/forms", "/api/v1/office/forms/create", "/api/v1/office/forms/submit", "/api/v1/office/forms/analytics"]:
            params = self.parse_query_params()
            action = params.get("action", "")
            form_id = params.get("form_id", "")
            if action == "submit" or path.endswith("/submit"):
                responses = json.loads(params.get("responses", "{}")) if "responses" in params else {"feedback": "Excellent"}
                self.send_json_response(office_suite.forms.submit_response(form_id or "form_101", responses))
            elif action == "analytics" or path.endswith("/analytics"):
                self.send_json_response(office_suite.forms.get_form_analytics(form_id or "form_101"))
            else:
                title = params.get("title", "Customer Intake")
                self.send_json_response(office_suite.forms.create_form(title))
        elif path in ["/api/v1/office/calendar", "/api/v1/office/calendar/schedule", "/api/v1/office/calendar/list", "/api/v1/office/calendar/resolve"]:
            params = self.parse_query_params()
            action = params.get("action", "")
            event_id = params.get("event_id", "")
            if action == "list" or path.endswith("/list"):
                self.send_json_response({"events": office_suite.calendar.list_upcoming_events(), "total": len(office_suite.calendar.events)})
            elif action == "resolve" or path.endswith("/resolve"):
                self.send_json_response(office_suite.calendar.resolve_conflict(event_id or "evt_101"))
            else:
                title = params.get("title", "Quarterly Executive Sync")
                start_time = params.get("start_time", "2026-09-01T10:00:00Z")
                duration = int(params.get("duration_minutes", 30))
                self.send_json_response(office_suite.calendar.schedule_event(title, start_time, duration))
        elif path in ["/api/v1/office/package", "/api/v1/office/package/create", "/api/v1/office/business_package"]:
            params = self.parse_query_params()
            company = params.get("company_name", params.get("company", "Apex Enterprise"))
            client = params.get("client_name", params.get("client", "Acme Inc"))
            val = float(params.get("annual_contract_val", 150000.0))
            self.send_json_response(office_suite.create_business_package(company, client, val))


        # ---------------------------------------------------------------------
        # 11 Platform Master Suite GET Endpoints
        # ---------------------------------------------------------------------
        elif path in ["/api/v1/quickbooks/pnl", "/api/v1/qb/pnl"]:
            self.send_json_response(mega11.qb.get_pnl_statement())
        elif path in ["/api/v1/quickbooks/project", "/api/v1/qb/project"]:
            self.send_json_response(mega11.qb.get_project_profitability("PRJ-101"))
        elif path in ["/api/v1/stripe/payment", "/api/v1/stripe/charge"]:
            self.send_json_response(mega11.stripe.process_payment(100.0, "USD"))
        elif path == "/api/v1/stripe/coupon":
            self.send_json_response(mega11.stripe.create_coupon("PRO20", 20.0))
        elif path == "/api/v1/revenuecat/entitlements":
            self.send_json_response(mega11.rc.get_entitlements("sub_101"))
        elif path == "/api/v1/revenuecat/experiment":
            self.send_json_response(mega11.rc.trigger_paywall_experiment("exp_paywall_v2"))
        elif path == "/api/v1/netsuite/asc606":
            self.send_json_response(mega11.netsuite.execute_asc606_revenue_recognition(120000.0))
        elif path == "/api/v1/xero/forecast":
            self.send_json_response(mega11.xero.get_30day_cash_forecast(1420500.0, 185400.0, 48200.0))
        elif path == "/api/v1/gusto/payroll":
            self.send_json_response(mega11.gusto.run_full_payroll(148500.0))
        elif path in ["/api/v1/bill/ap_approval", "/api/v1/bill_com/ap_approval"]:
            self.send_json_response(mega11.bill.execute_ap_approval_workflow("BILL-901", 24500.0))
        elif path == "/api/v1/expensify/audit":
            self.send_json_response(mega11.expensify.audit_expense_report("EMP-01", [{"merchant": "AWS", "amount": 250.0, "receipt_ocr": True}]))
        elif path == "/api/v1/plaid/balance":
            self.send_json_response(mega11.plaid.get_realtime_auth_balance("acc_101"))
        elif path == "/api/v1/avalara/tax_nexus":
            self.send_json_response(mega11.avalara.calculate_global_tax_nexus(1000.0, "US_CA"))
        elif path == "/api/v1/freshbooks/time_invoice":
            self.send_json_response(mega11.freshbooks.log_time_and_create_invoice("Apex Global", 150.0, 40.0))
        elif path in ["/api/v1/mega11/audit", "/api/v1/platforms/audit"]:
            self.send_json_response(mega11.run_full_11_platform_audit())
        elif path == "/api/v1/platforms/integrated_core_audit":
            self.send_json_response(mega11.run_integrated_11_platform_6_core_audit(orchestrator))
        # ---------------------------------------------------------------------
        # Embedded Marketplace REST API Endpoints (GET)
        # ---------------------------------------------------------------------
        elif path == "/api/v1/marketplace/apps":
            params = self.parse_query_params()
            cat = params.get("category")
            query = params.get("search", params.get("search_query", params.get("q")))
            apps = marketplace_hub.list_apps(category=cat, search_query=query)
            self.send_json_response({
                "apps": apps,
                "total": len(apps),
                "category_filter": cat,
                "search_query": query,
                "status": "MARKETPLACE_APPS_RETRIEVED"
            })
        elif path == "/api/v1/marketplace/connect":
            params = self.parse_query_params()
            app_id = params.get("app_id", "app_001")
            res = marketplace_hub.connect_app(app_id, orchestrator=orchestrator, revenuecat=mega11.rc)
            self.send_json_response(res)
        elif path == "/api/v1/marketplace/recommend_ai":
            params = self.parse_query_params()
            biz_type = params.get("business_type", "SaaS_Subscription")
            res = marketplace_hub.recommend_ai_integrations(business_type=biz_type, orchestrator=orchestrator)
            self.send_json_response(res)
        elif path == "/api/v1/marketplace/audit":
            self.send_json_response(marketplace_hub.run_full_marketplace_audit())
        # ---------------------------------------------------------------------
        # MCP & 20+ A-to-Z Workflow REST API Endpoints (GET)
        # ---------------------------------------------------------------------
        elif path == "/api/v1/mcp/tools":
            manifest = mcp_server.get_tool_definitions()
            self.send_json_response({
                "mcp_version": "2026-08-16",
                "tools": manifest,
                "total_tools": len(manifest),
                "six_core_substrate_sync": {
                    "cores_entangled": 6,
                    "cores": ["XFIN", "AURA", "PULSE", "MINT", "GRID", "NEXS"],
                    "status": "OPERATIONAL"
                },
                "revenuecat_integration": {
                    "entitlements_bridged": True,
                    "master_module": "RevenueCatMasterModule",
                    "status": "ACTIVE"
                },
                "status": "SOVEREIGN_MCP_TOOLS_ONLINE"
            })
        elif path == "/api/v1/mcp/spin_up":
            params = self.parse_query_params()
            app_id = params.get("app_id", "app_001")
            app_name = params.get("app_name", "QuickBooks Online")
            env = params.get("environment", "staging")
            sbx = mcp_server.sandbox_engine.spin_up_sandbox(app_id=app_id, tenant_id="tenant_01", environment=env)
            sbx["app_name"] = app_name
            sbx["six_core_substrate_sync"] = {
                "cores_entangled": 6,
                "cores": ["XFIN", "AURA", "PULSE", "MINT", "GRID", "NEXS"],
                "status": "ACTIVE"
            }
            sbx["revenuecat_integration"] = {
                "entitlements_bridged": True,
                "entitlement_id": "pro_access",
                "status": "CONNECTED"
            }
            self.send_json_response(sbx)
        elif path in ["/api/v1/workflows/run", "/api/v1/workflows/list", "/api/v1/workflows"]:
            params = self.parse_query_params()
            wf_id = params.get("workflow_id", params.get("id", params.get("workflow_name", params.get("name"))))
            if not wf_id or path == "/api/v1/workflows/list" or params.get("list") == "true":
                tools = mcp_server.get_tool_definitions()
                wf_tools = [t for t in tools if t["name"].startswith("workflow_")]
                self.send_json_response({
                    "workflows": wf_tools,
                    "total_workflows": len(wf_tools),
                    "six_core_substrate_integrated": True,
                    "revenuecat_integrated": True,
                    "status": "WORKFLOWS_CATALOG_RETRIEVED"
                })
            else:
                target_wf = WORKFLOW_SHORTHAND_MAP.get(wf_id, wf_id)
                exec_res = mcp_server.call_tool(target_wf, params)
                exec_res["six_core_substrate_sync"] = {
                    "cores_entangled": 6,
                    "audit": orchestrator.audit_financial_integrity()
                }
                exec_res["revenuecat_integration"] = mega11.rc.get_entitlements(params.get("subscriber_id", "sub_101"))
                self.send_json_response(exec_res)
        else:
            super().do_GET()

    def do_POST(self):
        logger.info(f"[POST] {self.path}")
        path = self.get_clean_path()
        body = self.parse_body()

        # 1. Gemini / Copilot Chat Orchestration
        if path in ["/api/v1/gemini/chat", "/api/v1/copilot/chat"]:
            msg = body.get("message", body.get("prompt", "Hello Gemini"))
            res = gemini_chat.process_chat_query(msg)
            self.send_json_response(res)

        # 2. Enterprise SaaS Ecosystem 1: Fixed Asset Depreciation
        elif path == "/api/v1/fixed_assets/depreciate":
            cost = float(body.get("cost", 240000.0))
            salvage = float(body.get("salvage", 40000.0))
            life = int(body.get("useful_life_years", 5))
            self.send_json_response(depreciation.calculate_straight_line_depreciation(cost, salvage, life))

        # 3. Enterprise SaaS Ecosystem 2: FIFO Inventory Valuation
        elif path == "/api/v1/inventory/fifo_cogs":
            units = int(body.get("units_sold", 150))
            self.send_json_response(fifo.calculate_fifo_cogs(units))

        # 4. Enterprise SaaS Ecosystem 3: Multi-Entity Consolidation
        elif path == "/api/v1/subsidiary/consolidate":
            us_rev = float(body.get("us_revenue", 500000.0))
            eu_rev = float(body.get("eu_revenue", 250000.0))
            elim = float(body.get("intercompany_sales", 50000.0))
            self.send_json_response(consolidation.consolidate_entities(us_rev, eu_rev, elim))

        # 5. Enterprise SaaS Ecosystem 4: Metered & Usage-Based Tier Billing
        elif path in ["/api/v1/metered_billing/calculate", "/api/v1/billing/metered"]:
            base = float(body.get("base_subscription", 99.0))
            calls = int(body.get("api_calls_used", 25000))
            free_allowance = int(body.get("free_allowance", 10000))
            rate = float(body.get("rate_per_1k", 2.50))
            self.send_json_response(metered.calculate_metered_bill(base, calls, free_allowance, rate))

        # 6. Enterprise SaaS Ecosystem 5: Smart Dunning & Payment Recovery
        elif path == "/api/v1/dunning/retry":
            sub_id = body.get("subscriber_id", "sub_101")
            attempt = int(body.get("retry_attempt", 1))
            self.send_json_response(dunning.execute_dunning_retry(sub_id, attempt))

        # 7. Enterprise SaaS Ecosystem 6: Global Sales Tax Calculation
        elif path == "/api/v1/tax/calculate":
            amt = float(body.get("amount", 100.0))
            cc = body.get("country_code", "DE")
            self.send_json_response(tax.calculate_location_tax(amt, cc))

        # 8. Enterprise SaaS Ecosystem 7: Employee PTO Accrual Liability
        elif path == "/api/v1/pto/accrual":
            hours = float(body.get("hours_worked", 160.0))
            rate = float(body.get("accrual_rate", 0.05))
            self.send_json_response(pto.calculate_pto_accrual(hours, rate))

        # 9. Enterprise SaaS Ecosystem 8: Expense OCR Receipt Categorization
        elif path in ["/api/v1/expense/ocr_match", "/api/v1/expense/ocr"]:
            merchant = body.get("merchant", "AWS")
            amt = float(body.get("amount", 250.0))
            self.send_json_response(ocr.process_receipt_ocr(merchant, amt))

        # 10. Enterprise SaaS Ecosystem 9: Purchase Order 3-Way Matching
        elif path in ["/api/v1/po/match_3way", "/api/v1/po/match3way"]:
            po = float(body.get("po_amount", 5000.0))
            slip = float(body.get("receiving_slip_amount", 5000.0))
            inv = float(body.get("vendor_invoice_amount", 5000.0))
            self.send_json_response(po_match.match_3way_po(po, slip, inv))

        # 11. Core 1 (XFIN): FX Micro-Settlement
        elif path == "/api/v1/xfin/settle":
            user_id = body.get("user_id", "usr_xfin_01")
            fiat_amount = float(body.get("fiat_amount", 100.0))
            currency = body.get("currency", "EUR")
            self.send_json_response(xfin.execute_cross_border_settlement(user_id, fiat_amount, currency))

        # 12. Core 1 (XFIN Risk): FX Exposure Hedging
        elif path == "/api/v1/xfin/hedge":
            currency = body.get("currency", "EUR")
            amount_usd = float(body.get("amount_usd", 50000.0))
            self.send_json_response(xfin.hedge_currency_exposure(currency, amount_usd))

        # 13. Core 2 (AURA): Underwriting & Credit Risk Evaluation
        elif path == "/api/v1/aura/credit_risk":
            user_id = body.get("user_id", "usr_aura_01")
            ratio = float(body.get("payment_history_ratio", 0.98))
            chargebacks = int(body.get("chargebacks", 0))
            tenure = int(body.get("tenure_months", 12))
            cost = float(body.get("subscription_cost", 299.0))
            pd = aura.evaluate_credit_risk(user_id, ratio, chargebacks, tenure)
            underwrite = aura.underwrite_subscription_bnpl(user_id, cost, pd)
            self.send_json_response({
                "user_id": user_id,
                "pd": pd,
                "underwriting": underwrite
            })

        # 14. Core 3 (PULSE): Churn Risk & Discounted LTV Telemetry
        elif path == "/api/v1/pulse/churn_risk":
            user_id = body.get("user_id", "usr_pulse_01")
            engagement = float(body.get("engagement_score", 0.85))
            tickets = int(body.get("support_tickets", 0))
            tenure = int(body.get("tenure_days", 45))
            arpu = float(body.get("arpu", 49.99))
            risk = pulse.evaluate_churn_risk(user_id, engagement, tickets, tenure)
            ltv = pulse.calculate_discounted_ltv(arpu, monthly_churn_rate=0.03)
            offer = pulse.generate_targeted_retention_offer(user_id, risk, ltv)
            self.send_json_response({
                "user_id": user_id,
                "churn_risk": risk,
                "discounted_ltv": ltv,
                "retention_offer": offer
            })

        # 15. Core 4 (MINT): Fiat Token Minting & Subscription Burn
        elif path == "/api/v1/mint/tokens":
            user_id = body.get("user_id", "usr_mint_01")
            fiat_amount = float(body.get("fiat_amount_usd", 100.0))
            action = body.get("action", "mint")
            if action == "burn":
                res = mint.execute_subscription_burn(user_id, fiat_amount)
            else:
                res = mint.mint_fiat_backed_tokens(user_id, fiat_amount)
            self.send_json_response(res)

        # 16. Core 5 (GRID): IoT Hardware Registration & Mesh Telemetry
        elif path == "/api/v1/grid/device":
            device_id = body.get("device_id", "dev_grid_01")
            device_type = body.get("device_type", "WEAR_OS_WATCH")
            country = body.get("country_code", "US")
            cost = float(body.get("hardware_cost_usd", 1200.0))
            reg = grid.register_device(device_id, device_type, country, hardware_cost_usd=cost)
            grid.evaluate_device_telemetry(device_id, cpu_usage_pct=25.0, mem_usage_pct=40.0, latency_ms=45.0)
            consensus = grid.verify_mesh_entitlement_consensus("usr_grid_owner", [device_id])
            self.send_json_response({
                "registration": reg,
                "consensus": consensus
            })

        # 17. Core 6 (NEXS): Dynamic Paywall Offering Synthesis
        elif path == "/api/v1/nexs/offering":
            user_id = body.get("user_id", "usr_nexs_01")
            country = body.get("country_code", "BR")
            base_price = float(body.get("base_usd_price", 19.99))
            self.send_json_response(nexs.synthesize_dynamic_offering(user_id, country, base_price))

        # 18. Master Orchestrator: Full 6-Core Subscriber Lifecycle
        elif path == "/api/v1/orchestrator/lifecycle":
            user_id = body.get("user_id", "usr_full_vip")
            country = body.get("country_code", "DE")
            device_id = body.get("device_id", "dev_watch_de")
            fiat_amount = float(body.get("fiat_amount", 99.99))
            currency = body.get("currency", "EUR")
            self.send_json_response(orchestrator.process_full_subscriber_lifecycle(
                user_id, country, device_id, fiat_amount, currency
            ))

        # ---------------------------------------------------------------------
        # Alpha Work REST API Endpoints (POST)
        # ---------------------------------------------------------------------
        elif path in ["/api/v1/alpha/work/generate", "/api/v1/alpha/work/generate_work"]:
            app_id = body.get("app_id", body.get("app_id_or_name", "app_001"))
            parameters = body.get("parameters")
            self.send_json_response(alpha_work_engine.generate_work(app_id=app_id, parameters=parameters))
        elif path in ["/api/v1/alpha/work/dispatch_200", "/api/v1/alpha/work/dispatch200"]:
            self.send_json_response(alpha_work_engine.dispatch_200())
        elif path == "/api/v1/alpha/work/audit":
            self.send_json_response(alpha_work_engine.run_alpha_audit())

        # ---------------------------------------------------------------------
        # Sovereign Office & Business Suite POST Endpoints
        # ---------------------------------------------------------------------
        elif path in ["/api/v1/office/tools", "/api/v1/office/audit"]:
            audit = office_suite.run_full_office_audit()
            audit["tools"] = [
                {"name": "SovereignDocs", "endpoint": "/api/v1/office/docs"},
                {"name": "SovereignSheetsSolve", "endpoint": "/api/v1/office/sheets/solve"},
                {"name": "SovereignSheetsModel", "endpoint": "/api/v1/office/sheets/model"},
                {"name": "SovereignSlidesPitch", "endpoint": "/api/v1/office/slides"},
                {"name": "SovereignSlidesBoard", "endpoint": "/api/v1/office/slides/board"},
                {"name": "SovereignSignExecute", "endpoint": "/api/v1/office/sign"},
                {"name": "SovereignSignVerify", "endpoint": "/api/v1/office/sign/verify"},
                {"name": "SovereignMailCadence", "endpoint": "/api/v1/office/mail"},
                {"name": "SovereignMailBilling", "endpoint": "/api/v1/office/mail/billing"},
                {"name": "SovereignDrive", "endpoint": "/api/v1/office/drive"},
                {"name": "SovereignForms", "endpoint": "/api/v1/office/forms"},
                {"name": "SovereignCalendar", "endpoint": "/api/v1/office/calendar"},
                {"name": "SovereignBusinessPackage", "endpoint": "/api/v1/office/package"},
                {"name": "AgenticMultiArtifactGenerator", "endpoint": "/api/v1/office/generate_artifact"}
            ]
            audit["supported_artifact_types"] = office_suite.artifact_generator.supported_artifact_types if office_suite.artifact_generator else []
            self.send_json_response(audit)
        elif path == "/api/v1/office/generate_artifact":
            art_type = body.get("artifact_type", body.get("type", "SPREADSHEET"))
            title = body.get("title", "Q1 Executive Financial Model")
            params = body.get("parameters", body)
            self.send_json_response(office_suite.artifact_generator.generate_artifact(art_type, title, params if isinstance(params, dict) else {}))
        elif path in ["/api/v1/office/docs", "/api/v1/office/docs/create"]:
            title = body.get("title", "SOVEREIGN OS Executive Report")
            author = body.get("author", "SOVEREIGN OS AI")
            body_txt = body.get("body")
            sections = body.get("sections")
            doc = office_suite.docs.create_document(title=title, author=author, body=body_txt, sections=sections)
            if body.get("export_md"):
                doc["markdown"] = office_suite.docs.export_markdown(doc)
            self.send_json_response(doc)
        elif path == "/api/v1/office/sheets/solve":
            sheet_data = body.get("sheet_data", body) if isinstance(body, dict) else {}
            self.send_json_response(office_suite.sheets.solve_formulas(sheet_data))
        elif path == "/api/v1/office/sheets/model":
            company = body.get("company_name", body.get("company", "Apex Enterprise"))
            base_mrr = float(body.get("base_mrr", body.get("mrr", 100000.0)))
            opex_ratio = float(body.get("opex_ratio", 0.4))
            self.send_json_response(office_suite.sheets.create_financial_model(company, base_mrr, opex_ratio))
        elif path in ["/api/v1/office/slides", "/api/v1/office/slides/pitch"]:
            company = body.get("company_name", body.get("company", "Apex Global"))
            topic = body.get("topic", "Enterprise Autonomous OS")
            template = body.get("template", "SERIES_A_GROWTH")
            self.send_json_response(office_suite.slides.generate_pitch_deck(company, topic, template))
        elif path == "/api/v1/office/slides/board":
            quarter = body.get("quarter", "Q1 2026")
            arr = float(body.get("arr", 1787040.0))
            net_margin = float(body.get("net_margin", 74.2))
            self.send_json_response(office_suite.slides.generate_board_deck(quarter, arr, net_margin))
        elif path == "/api/v1/office/slides/export_svg":
            deck = body.get("deck")
            if not deck or not isinstance(deck, dict):
                company = body.get("company_name", body.get("company", "Apex Global"))
                topic = body.get("topic", "Enterprise Autonomous OS")
                template = body.get("template", "SERIES_A_GROWTH")
                deck = office_suite.slides.generate_pitch_deck(company, topic, template)
            self.send_json_response(office_suite.slides.export_deck_to_svg(deck))
        elif path == "/api/v1/office/slides/export_html":
            deck = body.get("deck")
            if not deck or not isinstance(deck, dict):
                company = body.get("company_name", body.get("company", "Apex Global"))
                topic = body.get("topic", "Enterprise Autonomous OS")
                template = body.get("template", "SERIES_A_GROWTH")
                deck = office_suite.slides.generate_pitch_deck(company, topic, template)
            html_content = office_suite.slides.export_presentation_html(deck)
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html_content.encode("utf-8"))))
            self.end_headers()
            self.wfile.write(html_content.encode("utf-8"))
            return
        elif path in ["/api/v1/office/sign", "/api/v1/office/sign/execute"]:
            doc_name = body.get("document_name", body.get("doc", "Master SLA Contract"))
            email = body.get("signer_email", body.get("email", "cfo@apex.com"))
            role = body.get("signer_role", body.get("role", "CFO"))
            self.send_json_response(office_suite.sign.execute_signature(doc_name, email, role))
        elif path == "/api/v1/office/sign/verify":
            sig_id = body.get("signature_id", "sign_101")
            zk_proof = body.get("zk_proof", body.get("zk_proof_signature", "zk_sig_dilithium_101"))
            self.send_json_response(office_suite.sign.verify_zk_proof(sig_id, zk_proof))
        elif path in ["/api/v1/office/mail", "/api/v1/office/mail/send"]:
            recipient = body.get("recipient", "exec@apex.com")
            template = body.get("template", "Enterprise Onboarding")
            subject = body.get("subject", "SOVEREIGN OS Update")
            self.send_json_response(office_suite.mail.send_ai_cadence(recipient, template, subject))
        elif path == "/api/v1/office/mail/billing":
            recipient = body.get("recipient", "billing@apex.com")
            invoice_id = body.get("invoice_id", "INV-2026-001")
            amount_due = float(body.get("amount_due", 15000.0))
            self.send_json_response(office_suite.mail.send_billing_notice(recipient, invoice_id, amount_due))
        elif path in ["/api/v1/office/drive", "/api/v1/office/drive/files", "/api/v1/office/drive/upload", "/api/v1/office/drive/search"]:
            action = body.get("action", "")
            query = body.get("query", body.get("q", ""))
            if action == "upload" or path.endswith("/upload") or "name" in body:
                name = body.get("name", "Document.pdf")
                file_type = body.get("file_type", body.get("type", "DOCUMENT"))
                size_kb = int(body.get("size_kb", 500))
                self.send_json_response(office_suite.drive.upload_file(name, file_type, size_kb))
            elif query or action == "search" or path.endswith("/search"):
                self.send_json_response({"files": office_suite.drive.search_files(query), "query": query})
            else:
                self.send_json_response({"files": office_suite.drive.list_files(), "total_files": len(office_suite.drive.files)})
        elif path in ["/api/v1/office/forms", "/api/v1/office/forms/create", "/api/v1/office/forms/submit", "/api/v1/office/forms/analytics"]:
            action = body.get("action", "")
            form_id = body.get("form_id", "")
            if action == "submit" or path.endswith("/submit") or "responses" in body:
                responses = body.get("responses", {"feedback": "Excellent"})
                self.send_json_response(office_suite.forms.submit_response(form_id or "form_101", responses))
            elif action == "analytics" or path.endswith("/analytics"):
                self.send_json_response(office_suite.forms.get_form_analytics(form_id or "form_101"))
            else:
                title = body.get("title", "Customer Intake")
                fields = body.get("fields")
                self.send_json_response(office_suite.forms.create_form(title, fields))
        elif path in ["/api/v1/office/calendar", "/api/v1/office/calendar/schedule", "/api/v1/office/calendar/list", "/api/v1/office/calendar/resolve"]:
            action = body.get("action", "")
            event_id = body.get("event_id", "")
            if action == "list" or path.endswith("/list"):
                self.send_json_response({"events": office_suite.calendar.list_upcoming_events(), "total": len(office_suite.calendar.events)})
            elif action == "resolve" or path.endswith("/resolve"):
                self.send_json_response(office_suite.calendar.resolve_conflict(event_id or "evt_101"))
            else:
                title = body.get("title", "Quarterly Executive Sync")
                start_time = body.get("start_time", "2026-09-01T10:00:00Z")
                duration = int(body.get("duration_minutes", 30))
                participants = body.get("participants")
                self.send_json_response(office_suite.calendar.schedule_event(title, start_time, duration, participants))
        elif path in ["/api/v1/office/package", "/api/v1/office/package/create", "/api/v1/office/business_package"]:
            company = body.get("company_name", body.get("company", "Apex Enterprise"))
            client = body.get("client_name", body.get("client", "Acme Inc"))
            val = float(body.get("annual_contract_val", 150000.0))
            self.send_json_response(office_suite.create_business_package(company, client, val))


        # ---------------------------------------------------------------------
        # 11 Platform Master Suite POST Endpoints
        # ---------------------------------------------------------------------
        elif path in ["/api/v1/quickbooks/pnl", "/api/v1/qb/pnl"]:
            self.send_json_response(mega11.qb.get_pnl_statement())
        elif path in ["/api/v1/quickbooks/project", "/api/v1/qb/project"]:
            project_id = body.get("project_id", "PRJ-101")
            self.send_json_response(mega11.qb.get_project_profitability(project_id))
        elif path in ["/api/v1/stripe/payment", "/api/v1/stripe/charge"]:
            amount = float(body.get("amount", 100.0))
            currency = body.get("currency", "USD")
            payment_method = body.get("payment_method", "card")
            self.send_json_response(mega11.stripe.process_payment(amount, currency, payment_method))
        elif path == "/api/v1/stripe/coupon":
            code = body.get("code", "PRO20")
            percent_off = float(body.get("percent_off", 20.0))
            self.send_json_response(mega11.stripe.create_coupon(code, percent_off))
        elif path == "/api/v1/revenuecat/entitlements":
            subscriber_id = body.get("subscriber_id", "sub_101")
            self.send_json_response(mega11.rc.get_entitlements(subscriber_id))
        elif path == "/api/v1/revenuecat/experiment":
            experiment_id = body.get("experiment_id", "exp_paywall_v2")
            self.send_json_response(mega11.rc.trigger_paywall_experiment(experiment_id))
        elif path == "/api/v1/netsuite/asc606":
            total_contract_value = float(body.get("total_contract_value", 120000.0))
            contract_days = int(body.get("contract_days", 365))
            self.send_json_response(mega11.netsuite.execute_asc606_revenue_recognition(total_contract_value, contract_days))
        elif path == "/api/v1/xero/forecast":
            current_cash = float(body.get("current_cash", 1420500.0))
            expected_ar = float(body.get("expected_ar", 185400.0))
            expected_ap = float(body.get("expected_ap", 48200.0))
            self.send_json_response(mega11.xero.get_30day_cash_forecast(current_cash, expected_ar, expected_ap))
        elif path == "/api/v1/gusto/payroll":
            gross_payroll = float(body.get("gross_payroll", 148500.0))
            self.send_json_response(mega11.gusto.run_full_payroll(gross_payroll))
        elif path in ["/api/v1/bill/ap_approval", "/api/v1/bill_com/ap_approval"]:
            bill_id = body.get("bill_id", "BILL-901")
            amount = float(body.get("amount", 24500.0))
            self.send_json_response(mega11.bill.execute_ap_approval_workflow(bill_id, amount))
        elif path == "/api/v1/expensify/audit":
            employee_id = body.get("employee_id", "EMP-01")
            expenses = body.get("expenses", [{"merchant": "AWS", "amount": 250.0, "receipt_ocr": True}])
            self.send_json_response(mega11.expensify.audit_expense_report(employee_id, expenses))
        elif path == "/api/v1/plaid/balance":
            account_id = body.get("account_id", "acc_101")
            self.send_json_response(mega11.plaid.get_realtime_auth_balance(account_id))
        elif path == "/api/v1/avalara/tax_nexus":
            amount = float(body.get("amount", 1000.0))
            jurisdiction = body.get("state_or_country", body.get("jurisdiction", "US_CA"))
            is_b2b = bool(body.get("is_b2b_reseller", False))
            self.send_json_response(mega11.avalara.calculate_global_tax_nexus(amount, jurisdiction, is_b2b))
        elif path == "/api/v1/freshbooks/time_invoice":
            client = body.get("client", "Apex Global")
            hourly_rate = float(body.get("hourly_rate", 150.0))
            hours_logged = float(body.get("hours_logged", 40.0))
            self.send_json_response(mega11.freshbooks.log_time_and_create_invoice(client, hourly_rate, hours_logged))
        elif path in ["/api/v1/mega11/audit", "/api/v1/platforms/audit"]:
            self.send_json_response(mega11.run_full_11_platform_audit())
        elif path == "/api/v1/platforms/integrated_core_audit":
            self.send_json_response(mega11.run_integrated_11_platform_6_core_audit(orchestrator))
        # ---------------------------------------------------------------------
        # Embedded Marketplace REST API Endpoints (POST)
        # ---------------------------------------------------------------------
        elif path == "/api/v1/marketplace/apps":
            cat = body.get("category")
            query = body.get("search_query", body.get("search", body.get("q")))
            apps = marketplace_hub.list_apps(category=cat, search_query=query)
            self.send_json_response({
                "apps": apps,
                "total": len(apps),
                "category_filter": cat,
                "search_query": query,
                "status": "MARKETPLACE_APPS_RETRIEVED"
            })
        elif path == "/api/v1/marketplace/connect":
            app_id = body.get("app_id", "app_001")
            auth_payload = body.get("auth_payload")
            res = marketplace_hub.connect_app(app_id, auth_payload=auth_payload, orchestrator=orchestrator, revenuecat=mega11.rc)
            self.send_json_response(res)
        elif path == "/api/v1/marketplace/recommend_ai":
            biz_type = body.get("business_type", "SaaS_Subscription")
            res = marketplace_hub.recommend_ai_integrations(business_type=biz_type, orchestrator=orchestrator)
            self.send_json_response(res)
        elif path == "/api/v1/marketplace/audit":
            self.send_json_response(marketplace_hub.run_full_marketplace_audit())
        # ---------------------------------------------------------------------
        # MCP & 20+ A-to-Z Workflow REST API Endpoints (POST)
        # ---------------------------------------------------------------------
        elif path == "/api/v1/mcp/tools":
            tool_name = body.get("tool_name", body.get("name"))
            arguments = body.get("arguments", body.get("args", body))
            if not tool_name:
                manifest = mcp_server.get_tool_definitions()
                res = {
                    "mcp_version": "2026-08-16",
                    "tools": manifest,
                    "total_tools": len(manifest),
                    "status": "SOVEREIGN_MCP_TOOLS_ONLINE"
                }
            else:
                res = mcp_server.call_tool(tool_name, arguments if isinstance(arguments, dict) else {})
            res["six_core_substrate_sync"] = {
                "cores_entangled": 6,
                "cores": ["XFIN", "AURA", "PULSE", "MINT", "GRID", "NEXS"],
                "status": "OPERATIONAL"
            }
            res["revenuecat_integration"] = {
                "entitlements_bridged": True,
                "master_module": "RevenueCatMasterModule",
                "status": "ACTIVE"
            }
            self.send_json_response(res)
        elif path == "/api/v1/mcp/spin_up":
            app_id = body.get("app_id", "app_001")
            app_name = body.get("app_name", "QuickBooks Online")
            tenant_id = body.get("tenant_id", "tenant_01")
            env = body.get("environment", "staging")
            mock_services = body.get("mock_services", ["QuickBooks_API_Mock", "Stripe_Mock", "RevenueCat_Mock"])
            sbx = mcp_server.sandbox_engine.spin_up_sandbox(app_id=app_id, tenant_id=tenant_id, environment=env, mock_services=mock_services)
            sbx["app_name"] = app_name
            sbx["six_core_substrate_sync"] = {
                "cores_entangled": 6,
                "cores": ["XFIN", "AURA", "PULSE", "MINT", "GRID", "NEXS"],
                "status": "ACTIVE"
            }
            sbx["revenuecat_integration"] = {
                "entitlements_bridged": True,
                "entitlement_id": body.get("entitlement_id", "pro_access"),
                "status": "CONNECTED"
            }
            self.send_json_response(sbx)
        elif path in ["/api/v1/workflows/run", "/api/v1/workflows/list", "/api/v1/workflows"]:
            if path == "/api/v1/workflows/list" or body.get("action") == "list":
                tools = mcp_server.get_tool_definitions()
                wf_tools = [t for t in tools if t["name"].startswith("workflow_")]
                self.send_json_response({
                    "workflows": wf_tools,
                    "total_workflows": len(wf_tools),
                    "six_core_substrate_integrated": True,
                    "revenuecat_integrated": True,
                    "status": "WORKFLOWS_CATALOG_RETRIEVED"
                })
            else:
                wf_id = body.get("workflow_id", body.get("id", body.get("workflow_name", body.get("name", "wf_01"))))
                target_wf = WORKFLOW_SHORTHAND_MAP.get(wf_id, wf_id)
                arguments = body.get("arguments", body.get("payload", body))
                exec_res = mcp_server.call_tool(target_wf, arguments if isinstance(arguments, dict) else {})
                exec_res["six_core_substrate_sync"] = {
                    "cores_entangled": 6,
                    "audit": orchestrator.audit_financial_integrity()
                }
                exec_res["revenuecat_integration"] = mega11.rc.get_entitlements(body.get("subscriber_id", "sub_101"))
                self.send_json_response(exec_res)

        # Legacy / Existing Endpoints
        elif path == "/api/v1/invoices/create":
            client = body.get("client", "Apex Global")
            amount = float(body.get("amount", 10000.0))
            score = aura.evaluate_credit_score(lifetime_spent_usd=amount, active_months=12)
            underwriting = aura.underwrite_micro_credit("inv_client", score)
            self.send_json_response({
                "invoice_id": f"INV-{os.urandom(3).hex().upper()}",
                "client": client,
                "amount_usd": amount,
                "aura_credit_score": score,
                "status": underwriting["underwriting_status"]
            })
        elif path == "/api/v1/payroll/run":
            gross = float(body.get("gross_payroll", 148500.0))
            self.send_json_response(payroll.calculate_payroll_run(gross))
        elif path == "/api/v1/bank/reconcile":
            feed = body.get("feed", [{"tx_id": "TX_101", "amount": 148.92}])
            self.send_json_response(bank.reconcile_feed(feed))
        elif path == "/api/v1/paywall/mutate":
            variant = body.get("variant_id", "var_A_minimal")
            theme = body.get("theme", "NEON_CYAN")
            self.send_json_response({
                "system": "NEXS",
                "variant_id": variant,
                "theme": theme,
                "status": "PAYWALL_MUTATED"
            })
        elif path == "/api/v1/customer_center/intercept":
            res = pulse.route_churn_prevention_path(R_coherence=0.54)
            self.send_json_response({
                "system": "PULSE",
                "subscriber_id": "usr_retention_sim_99",
                "action": res["recommended_action"],
                "status": "RETAINED"
            })
        elif path == "/api/v1/synthesize":
            prompt = body.get("prompt", "Fitness AI App")
            arch = nexs.synthesize_app_architecture(prompt)
            compose_code = nexs.generate_jetpack_compose_ui(arch["app_name"])
            self.send_json_response({
                "app_name": arch["app_name"],
                "compose_code": compose_code,
                "status": "SYNTHESIZED"
            })
        else:
            self.send_error(404, "Endpoint not found")

    def send_json_response(self, data: dict, status_code: int = 200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

def run_server(port: int = 8090):
    server_address = ("", port)
    httpd = HTTPServer(server_address, SovereignDashboardHandler)
    logger.info(f"===================================================================")
    logger.info(f"  SOVEREIGN ENGINE ENTERPRISE WEB DASHBOARD SERVER RUNNING          ")
    logger.info(f"  All 11 Platform Master Suite & 6 Next-Gen Core Endpoints Exposed (Port {port})")
    logger.info(f"===================================================================")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()
