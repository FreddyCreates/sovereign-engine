"""
AUTOMATED TEST SUITE FOR GEMINI 2.0 EMBEDDED ENTERPRISE PLATFORM SUITE
================================================================================
Comprehensive test coverage for QuickBooks, Wave.com, Salesforce, HubSpot, Bill.com,
Ramp, Brex, Square, and RevenueCat native AI replacement engines.
"""

import unittest
import sys
import os

# Ensure imports work regardless of execution location
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
nextgen_dir = os.path.join(root_dir, "sovereign_infrastructure", "nextgen_systems")

if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
if nextgen_dir not in sys.path:
    sys.path.insert(0, nextgen_dir)

from sovereign_infrastructure.nextgen_systems.gemini_embedded_enterprise_suite import (
    TestGeminiQuickBooksEngine,
    TestGeminiSalesforceEngine,
    TestGeminiBillComEngine,
    TestGeminiSquareRevenueCatEngine,
    TestGeminiEmbeddedEnterpriseSuite,
    gemini_enterprise_suite
)

if __name__ == "__main__":
    unittest.main()
