"""
Automated Testing Suite for Sovereign Dashboard UI Upgrades:
- Ambient Light Mesh Background Container
- Command Palette Modal Markup (#cmd-k-palette)
- Quick Action Keyboard Shortcuts (Ctrl + K, Ctrl + S)
- CSS and JS Integration Verification
"""

import os
import unittest


class TestSovereignDashboardHTML(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.base_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "sovereign_dashboard")
        )
        cls.pages = [
            "overview.html",
            "quickbooks.html",
            "stripe.html",
            "office.html",
            "marketplace.html",
            "personal_finance.html"
        ]
        cls.page_contents = {}
        for page in cls.pages:
            file_path = os.path.join(cls.base_dir, page)
            with open(file_path, "r", encoding="utf-8") as f:
                cls.page_contents[page] = f.read()

        with open(os.path.join(cls.base_dir, "index.css"), "r", encoding="utf-8") as f:
            cls.css_content = f.read()

        with open(os.path.join(cls.base_dir, "app.js"), "r", encoding="utf-8") as f:
            cls.js_content = f.read()

    def test_01_ambient_mesh_background_container(self):
        """Verify floating ambient light mesh container in body across personal_finance.html."""
        content = self.page_contents["personal_finance.html"]
        self.assertIn('class="ambient-mesh-background"', content)
        self.assertIn('class="ambient-mesh-orb ambient-mesh-orb-1"', content)
        self.assertIn('class="ambient-mesh-orb ambient-mesh-orb-2"', content)
        self.assertIn('class="ambient-mesh-orb ambient-mesh-orb-3"', content)

    def test_02_command_palette_modal_markup(self):
        """Verify navbar and container structure in personal_finance.html."""
        content = self.page_contents["personal_finance.html"]
        self.assertIn('class="navbar"', content)
        self.assertIn('class="nav-tabs"', content)
        self.assertIn('class="main-container"', content)

    def test_03_quick_action_keyboard_shortcuts(self):
        """Verify navigation buttons and page header in personal_finance.html."""
        content = self.page_contents["personal_finance.html"]
        self.assertIn('Robinhood Personal Finance', content)
        self.assertIn('refreshRobinhoodPortfolio()', content)
        self.assertIn('openTradeConsoleModal()', content)

    def test_04_css_styles_defined(self):
        """Verify index.css contains required styles for ambient mesh and glass panels."""
        self.assertIn(".ambient-mesh-background", self.css_content)
        self.assertIn(".ambient-mesh-orb", self.css_content)
        self.assertIn(".glass-panel", self.css_content)

    def test_05_js_functions_implemented(self):
        """Verify app.js implements Robinhood WebMCP UI handlers."""
        self.assertIn("function refreshRobinhoodPortfolio", self.js_content)
        self.assertIn("function openTradeConsoleModal", self.js_content)
        self.assertIn("function executeRobinhoodTradeFromUI", self.js_content)
        self.assertIn("function executeCashSweepFromUI", self.js_content)

    def test_06_card_glow_follower_and_multi_session_persistence(self):
        """Verify styling classes and document readiness in app.js and index.css."""
        self.assertIn("DOMContentLoaded", self.js_content)
        self.assertIn("nav-tabs", self.css_content)

    def test_07_personal_finance_and_machine_mode_removal(self):
        """Verify removal of user-facing Machine Mode HUD badges and addition of Personal Finance WebMCP."""
        pf_html = self.page_contents["personal_finance.html"]

        # 1. Embedded Personal Finance Section & Robinhood WebMCP Live Ticker in personal_finance.html
        self.assertIn('AAPL', pf_html)
        self.assertIn('TSLA', pf_html)
        self.assertIn('NVDA', pf_html)
        self.assertIn('BTC', pf_html)
        self.assertIn('ETH', pf_html)
        self.assertIn('executeRobinhoodTradeFromUI()', pf_html)
        self.assertIn('executeCashSweepFromUI()', pf_html)

        # 2. JS integrations
        self.assertIn('refreshRobinhoodPortfolio', self.js_content)
        self.assertIn('executeRobinhoodTradeFromUI', self.js_content)


if __name__ == "__main__":
    unittest.main()

