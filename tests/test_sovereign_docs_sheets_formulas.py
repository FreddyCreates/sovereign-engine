"""
Automated Test Suite for SovereignDocs and SovereignSheets Formula Evaluation.
Verifies SUM, AVG, MIN, MAX, NPV, IRR, VLOOKUP, document template formula tag substitution,
and dynamic matrix spreadsheet cell updates.
"""

import unittest
import sys
import os

# Add parent directory to sys.path for proper package imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../sovereign_infrastructure/nextgen_systems')))

from sovereign_infrastructure.nextgen_systems.mega_office_business_suite import (
    SovereignFormulaEvaluator,
    SovereignDocsModule,
    SovereignSheetsModule,
    MegaOfficeBusinessSuite
)

class TestSovereignDocsSheetsFormulas(unittest.TestCase):

    def setUp(self):
        self.evaluator = SovereignFormulaEvaluator()
        self.docs = SovereignDocsModule()
        self.sheets = SovereignSheetsModule()
        self.suite = MegaOfficeBusinessSuite()

    def test_01_formula_evaluator_sum_avg_min_max(self):
        """Test SUM, AVG, MIN, MAX formula evaluation across scalar args, lists, and cell ranges."""
        grid = {
            "A1": 100.0,
            "A2": 200.0,
            "A3": 300.0,
            "B1": 10.0,
            "B2": 20.0,
            "B3": 30.0,
            "matrix": [
                [100.0, 10.0],
                [200.0, 20.0],
                [300.0, 30.0]
            ]
        }

        # SUM
        sum_val = self.evaluator.evaluate_formula("=SUM(A1:A3)", grid)
        self.assertEqual(sum_val, 600.0)

        # AVG / AVERAGE
        avg_val = self.evaluator.evaluate_formula("=AVG(A1:A3)", grid)
        self.assertEqual(avg_val, 200.0)

        # MIN
        min_val = self.evaluator.evaluate_formula("=MIN(A1:B3)", grid)
        self.assertEqual(min_val, 10.0)

        # MAX
        max_val = self.evaluator.evaluate_formula("=MAX(A1:B3)", grid)
        self.assertEqual(max_val, 300.0)

    def test_02_formula_evaluator_npv_irr(self):
        """Test NPV and IRR financial cash flow evaluations with mathematical precision."""
        cash_flows = [-100000.0, 30000.0, 40000.0, 50000.0, 60000.0]
        grid = {
            "CashFlows": cash_flows,
            "A1": -100000.0,
            "A2": 30000.0,
            "A3": 40000.0,
            "A4": 50000.0,
            "A5": 60000.0
        }

        # NPV test with 8% discount rate
        npv_val = self.evaluator.evaluate_formula("=NPV(0.08, CashFlows)", grid)
        self.assertIsInstance(npv_val, float)
        self.assertGreater(npv_val, 0.0)

        # IRR test
        irr_val = self.evaluator.evaluate_formula("=IRR(CashFlows)", grid)
        self.assertIsInstance(irr_val, float)
        # Expected IRR for these cash flows is approx 0.225 (22.5%)
        self.assertAlmostEqual(irr_val, 0.225, delta=0.05)

    def test_03_formula_evaluator_vlookup(self):
        """Test VLOOKUP with exact and approximate matching on 2D table matrices."""
        grid = {
            "matrix": [
                ["Jan", 125000.0, 45000.0],
                ["Feb", 140000.0, 48000.0],
                ["Mar", 165000.0, 52000.0]
            ],
            "A1": "Jan", "B1": 125000.0, "C1": 45000.0,
            "A2": "Feb", "B2": 140000.0, "C2": 48000.0,
            "A3": "Mar", "B3": 165000.0, "C3": 52000.0
        }

        # Exact match VLOOKUP for column 2 (Revenue for Feb)
        feb_rev = self.evaluator.evaluate_formula("=VLOOKUP('Feb', matrix, 2, FALSE)", grid)
        self.assertEqual(feb_rev, 140000.0)

        # Exact match VLOOKUP for column 3 (Expenses for Mar)
        mar_exp = self.evaluator.evaluate_formula("=VLOOKUP('Mar', matrix, 3, FALSE)", grid)
        self.assertEqual(mar_exp, 52000.0)

        # Non-matching key returns #N/A
        unknown = self.evaluator.evaluate_formula("=VLOOKUP('Dec', matrix, 2, FALSE)", grid)
        self.assertEqual(unknown, "#N/A")

    def test_04_sovereign_docs_template_formula_replacement(self):
        """Test SovereignDocs parsing and replacing formula tags in text content."""
        grid = {
            "A1": 5000.0,
            "A2": 7000.0,
            "A3": 8000.0
        }

        doc = self.docs.create_document(
            title="Q3 Quarterly Financial Report",
            body="Total revenue calculated is {{=SUM(A1:A3)}} with an average monthly revenue of {{=AVG(A1:A3)}}.",
            grid_data=grid
        )

        self.assertEqual(doc["status"], "SOVEREIGN_DOCS_CREATED")
        self.assertGreater(doc["formulas_evaluated_count"], 0)
        
        # Verify tag replacement in paragraphs
        full_text = " ".join(doc["paragraphs"])
        self.assertIn("$20,000.00", full_text)
        self.assertIn("$6,666.6667", full_text)

        # Export Markdown verification
        md_text = self.docs.export_markdown(doc)
        self.assertIn("# Q3 Quarterly Financial Report", md_text)
        self.assertIn("$20,000.00", md_text)

    def test_05_sovereign_sheets_create_and_update_cell(self):
        """Test SovereignSheets matrix creation, cell updating, and dynamic formula recalculation."""
        columns = ["Month", "Revenue", "Expenses"]
        rows = [
            ["Jan", 10000.0, 4000.0],
            ["Feb", 15000.0, 5000.0],
            ["Mar", 20000.0, 6000.0]
        ]
        formulas = {
            "TotalRevenue": "=SUM(B1:B3)",
            "AverageRevenue": "=AVG(B1:B3)",
            "MaxExpense": "=MAX(C1:C3)"
        }

        sheet = self.sheets.create_sheet("2026 Q1 Revenue Sheet", columns, rows, formulas)
        self.assertEqual(sheet["status"], "SOVEREIGN_SHEETS_CREATED")
        self.assertEqual(sheet["resolved_formulas"]["TotalRevenue"], 45000.0)
        self.assertEqual(sheet["resolved_formulas"]["AverageRevenue"], 15000.0)
        self.assertEqual(sheet["resolved_formulas"]["MaxExpense"], 6000.0)

        # Update cell B1 (row 0, col 1) from 10000 to 30000
        updated_sheet = self.sheets.update_cell(sheet, "B1", 30000.0)
        self.assertEqual(updated_sheet["resolved_formulas"]["TotalRevenue"], 65000.0)
        self.assertAlmostEqual(updated_sheet["resolved_formulas"]["AverageRevenue"], 21666.6667, delta=0.01)

if __name__ == "__main__":
    unittest.main()
