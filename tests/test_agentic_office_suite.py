"""
Automated Test Suite for SOVEREIGN OS Mega Office Suite & Agentic Multi-Artifact AI Generator
"""

import sys
import os
import unittest
import json
import io

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sovereign_infrastructure", "nextgen_systems")))

from agentic_multi_artifact_generator import AgenticMultiArtifactGenerator
from mega_office_business_suite import (
    MegaOfficeBusinessSuite,
    SovereignDocsModule,
    SovereignSheetsModule,
    SovereignSlidesModule,
    SovereignSignModule,
    SovereignMailModule,
    SovereignDriveModule,
    SovereignFormsModule,
    SovereignCalendarModule
)
from full_saas_accounting_suite import GeneralLedgerEngine
from sovereign_dashboard_server import SovereignDashboardHandler


class TestAgenticOfficeSuite(unittest.TestCase):

    def setUp(self):
        self.gl = GeneralLedgerEngine()
        self.generator = AgenticMultiArtifactGenerator(gl_engine=self.gl)
        self.office = MegaOfficeBusinessSuite(gl_engine=self.gl)

    def test_01_supported_artifact_types_count(self):
        self.assertEqual(len(self.generator.supported_artifact_types), 8)

    def test_02_generate_spreadsheet_artifact(self):
        art = self.generator.generate_artifact("SPREADSHEET", "Q1 Financial Model")
        self.assertEqual(art["artifact_type"], "SPREADSHEET")
        self.assertIn("headers", art["content"])

    def test_03_generate_presentation_artifact(self):
        art = self.generator.generate_artifact("PRESENTATION", "Board Pitch Deck")
        self.assertEqual(art["artifact_type"], "PRESENTATION")
        self.assertGreaterEqual(len(art["content"]["slides"]), 3)

    def test_04_generate_diagram_artifact(self):
        art = self.generator.generate_artifact("DIAGRAM", "System Architecture Flow")
        self.assertEqual(art["artifact_type"], "DIAGRAM")
        self.assertIn("Mermaid", art["content"]["diagram_type"])

    def test_05_generate_invoice_bill_artifact(self):
        art = self.generator.generate_artifact("INVOICE_BILL", "Enterprise SaaS Invoice")
        self.assertEqual(art["artifact_type"], "INVOICE_BILL")
        self.assertEqual(art["content"]["total_due"], 173200.00)
        self.assertIsNotNone(art["content"]["gl_entry_id"])

    def test_06_generate_contract_legal_artifact(self):
        art = self.generator.generate_artifact("CONTRACT_LEGAL", "SLA Agreement")
        self.assertEqual(art["artifact_type"], "CONTRACT_LEGAL")
        self.assertIn("Wyoming DUNA DAO", art["content"]["governance"])

    def test_07_generate_code_module_artifact(self):
        art = self.generator.generate_artifact("CODE_MODULE", "Autonomic Worker Module")
        self.assertEqual(art["artifact_type"], "CODE_MODULE")
        self.assertEqual(art["content"]["language"], "Python 3.11")

    def test_08_generate_analytics_report_artifact(self):
        art = self.generator.generate_artifact("ANALYTICS_REPORT", "Executive Cohort Report")
        self.assertEqual(art["artifact_type"], "ANALYTICS_REPORT")
        self.assertEqual(art["content"]["metrics"]["arr"], 1787040.00)

    def test_09_sovereign_sheets_solver(self):
        res = self.office.sheets.solve_formulas({"revenue_rows": [100.0, 200.0], "expense_rows": [50.0, 50.0]})
        self.assertEqual(res["net_profit"], 200.0)

    def test_10_sovereign_sign_execution(self):
        res = self.office.sign.execute_signature("Master SLA", "cfo@apex.com")
        self.assertEqual(res["status"], "SOVEREIGN_SIGN_EXECUTED")
        verification = self.office.sign.verify_zk_proof(res["signature_id"], res["zk_proof_signature"])
        self.assertTrue(verification["is_valid"])

    def test_11_mega_office_suite_audit(self):
        audit = self.office.run_full_office_audit()
        self.assertEqual(audit["status"], "MEGA_OFFICE_SUITE_FULLY_OPERATIONAL")
        self.assertEqual(len(audit["apps_included"]), 8)
        self.assertIn("SovereignForms", audit["apps_included"])
        self.assertIn("SovereignCalendar", audit["apps_included"])

    def test_12_generate_multi_artifact_suite(self):
        suite = self.generator.generate_multi_artifact_suite("Enterprise Release Suite", "Apex Global")
        self.assertEqual(suite["artifacts_count"], 8)
        self.assertEqual(suite["status"], "MULTI_ARTIFACT_SUITE_GENERATED")

    def test_13_export_artifacts(self):
        art = self.generator.generate_artifact("DOCUMENT", "System Architecture Blueprint")
        json_export = self.generator.export_artifact_as_json(art["artifact_id"])
        md_export = self.generator.export_artifact_as_markdown(art["artifact_id"])
        self.assertIn("Blueprint", json_export)
        self.assertIn("# System Architecture Blueprint", md_export)

    def test_14_sovereign_forms_and_calendar(self):
        form = self.office.forms.create_form("Lead Intake", [{"name": "company", "type": "text"}])
        self.assertEqual(form["status"], "SOVEREIGN_FORMS_CREATED")
        resp = self.office.forms.submit_response(form["form_id"], {"company": "Acme Corp"})
        self.assertTrue(resp["validated"])

        event = self.office.calendar.schedule_event("Quarterly Audit", "2026-09-15T14:00:00Z")
        self.assertEqual(event["status"], "SOVEREIGN_CALENDAR_EVENT_SCHEDULED")
        conflict = self.office.calendar.resolve_conflict(event["event_id"])
        self.assertFalse(conflict["conflict_detected"])

    def invoke_dashboard_endpoint(self, path: str, method: str = "GET", body: dict = None) -> dict:
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

    def test_16_rest_api_office_tools_get(self):
        res = self.invoke_dashboard_endpoint("/api/v1/office/tools", "GET")
        self.assertEqual(res["status"], "MEGA_OFFICE_SUITE_FULLY_OPERATIONAL")
        self.assertIn("tools", res)
        self.assertIn("supported_artifact_types", res)
        self.assertEqual(len(res["supported_artifact_types"]), 8)

    def test_17_rest_api_office_tools_post(self):
        res = self.invoke_dashboard_endpoint("/api/v1/office/tools", "POST")
        self.assertEqual(res["status"], "MEGA_OFFICE_SUITE_FULLY_OPERATIONAL")
        self.assertIn("tools", res)

    def test_18_rest_api_generate_artifact_get(self):
        res = self.invoke_dashboard_endpoint("/api/v1/office/generate_artifact?artifact_type=PRESENTATION&title=Q3+Board+Deck", "GET")
        self.assertEqual(res["artifact_type"], "PRESENTATION")
        self.assertEqual(res["title"], "Q3 Board Deck")
        self.assertEqual(res["status"], "ARTIFACT_GENERATED_SUCCESSFULLY")

    def test_19_rest_api_generate_artifact_post(self):
        res = self.invoke_dashboard_endpoint("/api/v1/office/generate_artifact", "POST", {
            "artifact_type": "CONTRACT_LEGAL",
            "title": "Sovereign Enterprise SLA"
        })
        self.assertEqual(res["artifact_type"], "CONTRACT_LEGAL")
        self.assertEqual(res["title"], "Sovereign Enterprise SLA")
        self.assertEqual(res["status"], "ARTIFACT_GENERATED_SUCCESSFULLY")

    def test_20_rest_api_sheets_solve_get(self):
        res = self.invoke_dashboard_endpoint("/api/v1/office/sheets/solve?revenue_rows=1000,2000&expense_rows=400,600", "GET")
        self.assertEqual(res["status"], "SOVEREIGN_SHEETS_SOLVED")
        self.assertEqual(res["total_revenue"], 3000.0)
        self.assertEqual(res["total_expenses"], 1000.0)
        self.assertEqual(res["net_profit"], 2000.0)

    def test_21_rest_api_sheets_solve_post(self):
        res = self.invoke_dashboard_endpoint("/api/v1/office/sheets/solve", "POST", {
            "revenue_rows": [500.0, 1500.0],
            "expense_rows": [200.0, 300.0]
        })
        self.assertEqual(res["status"], "SOVEREIGN_SHEETS_SOLVED")
        self.assertEqual(res["total_revenue"], 2000.0)
        self.assertEqual(res["total_expenses"], 500.0)
        self.assertEqual(res["net_profit"], 1500.0)
        self.assertEqual(res["profit_margin_pct"], 75.0)

    def test_22_sovereign_sign_duna_dao_governance(self):
        prop_sig = self.office.sign.create_duna_dao_proposal_signature(
            proposal_id="prop_401",
            proposal_title="Treasury Allocation for Quantum Vault",
            proposer_address="0x1234567890abcdef",
            voting_power=150000.0,
            quorum_required_pct=51.0
        )
        self.assertEqual(prop_sig["status"], "DUNA_DAO_PROPOSAL_SIGNATURE_EXECUTED")
        self.assertTrue(prop_sig["duna_governance"]["quorum_verified"])
        self.assertIn("zk_dilithium_proof", prop_sig)
        self.assertEqual(prop_sig["zk_dilithium_proof"]["algorithm"], "Dilithium5_PostQuantum_ZK")

    def test_23_sovereign_sign_multi_sig_contract(self):
        signers = [
            {"name": "Alice CFO", "email": "alice@dao.org", "role": "CFO"},
            {"name": "Bob Counsel", "email": "bob@dao.org", "role": "Legal Counsel"}
        ]
        multisig = self.office.sign.execute_multi_sig_duna_contract(
            contract_title="DUNA Master Treasury SLA",
            signers=signers,
            governance_vote_id="vote_999",
            total_value=250000.0
        )
        self.assertEqual(multisig["status"], "DUNA_MULTISIG_CONTRACT_EXECUTED")
        self.assertEqual(multisig["signers_count"], 2)
        self.assertIn("aggregated_zk_dilithium_proof", multisig)

    def test_24_sovereign_sign_duna_audit(self):
        sig = self.office.sign.execute_signature("Corporate Charter Amendment", "governance@dao.org", signer_role="DAO Chair")
        audit = self.office.sign.audit_duna_compliance(sig["signature_id"])
        self.assertEqual(audit["status"], "DUNA_COMPLIANCE_AUDIT_VERIFIED")
        self.assertEqual(audit["duna_statutory_compliance"], "PASS")
        self.assertTrue(audit["post_quantum_zk_proof_valid"])

    def test_25_sovereign_slides_templates_and_deck_builder(self):
        templates = self.office.slides.get_available_templates()
        self.assertEqual(templates["status"], "TEMPLATES_CATALOG_RETRIEVED")
        self.assertGreaterEqual(len(templates["templates"]), 4)

        deck = self.office.slides.generate_pitch_deck(
            company_name="Antigravity AI",
            topic="Autonomous OS Substrate",
            template="Y_COMBINATOR_SEED",
            target_raise="$5M Seed"
        )
        self.assertEqual(deck["status"], "SOVEREIGN_SLIDES_GENERATED")
        self.assertEqual(deck["slides_count"], 6)

        # Test adding and updating slides
        deck = self.office.slides.add_slide(
            deck,
            title="Customer Case Studies",
            slide_type="CUSTOM_SLIDE",
            subtitle="Enterprise ROI Results",
            bullet_points=["Client A saved 68% on SaaS costs", "Client B eliminated GL variance"]
        )
        self.assertEqual(deck["slides_count"], 7)

        deck = self.office.slides.update_slide(deck, slide_num=1, subtitle="Updated Autonomic Substrate Vision")
        self.assertEqual(deck["slides"][0]["subtitle"], "Updated Autonomic Substrate Vision")

    def test_26_sovereign_slides_svg_export(self):
        deck = self.office.slides.generate_pitch_deck("Apex Autonomous", template="SERIES_A_GROWTH")
        svg_export = self.office.slides.export_deck_to_svg(deck)
        self.assertEqual(svg_export["status"], "DECK_SVG_EXPORT_SUCCESSFUL")
        self.assertEqual(len(svg_export["svg_slides"]), 8)

        first_svg = svg_export["svg_slides"][0]["svg_code"]
        self.assertIn("<svg", first_svg)
        self.assertIn("Apex Autonomous", first_svg)
        self.assertIn("DILITHIUM5 ZK-VERIFIED", first_svg)
        self.assertIn("1920 1080", first_svg)

    def test_27_sovereign_slides_html_viewer_and_save(self):
        import tempfile
        deck = self.office.slides.generate_pitch_deck("Sovereign Enterprise", template="ENTERPRISE_SAAS")
        html_code = self.office.slides.export_presentation_html(deck)
        self.assertIn("<!DOCTYPE html>", html_code)
        self.assertIn("SovereignSlides Pitch Deck", html_code)
        self.assertIn("slidesData =", html_code)

        with tempfile.TemporaryDirectory() as tmpdir:
            save_res = self.office.slides.save_presentation(deck, tmpdir)
            self.assertEqual(save_res["status"], "PRESENTATION_SAVED_SUCCESSFULLY")
            self.assertTrue(os.path.exists(os.path.join(save_res["deck_directory"], "presentation.html")))
            self.assertTrue(os.path.exists(os.path.join(save_res["deck_directory"], "slide_01.svg")))

    def test_28_rest_api_slides_svg_and_html_export(self):
        svg_res = self.invoke_dashboard_endpoint("/api/v1/office/slides/export_svg?company_name=Nexus+Labs", "GET")
        self.assertEqual(svg_res["status"], "DECK_SVG_EXPORT_SUCCESSFUL")
        self.assertEqual(len(svg_res["svg_slides"]), 8)

        post_svg_res = self.invoke_dashboard_endpoint("/api/v1/office/slides/export_svg", "POST", {
            "company_name": "Hyperion Crypto",
            "template": "CRYPTO_WEB3"
        })
        self.assertEqual(post_svg_res["status"], "DECK_SVG_EXPORT_SUCCESSFUL")


if __name__ == "__main__":
    unittest.main()


