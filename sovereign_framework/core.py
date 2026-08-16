"""
Core Framework Class: SovereignApp
Provides a 1-line instantiation wrapper connecting RevenueCat REST API v2,
Gemini Autonomous Builder, Motoko canisters, and 20 Multi-Agent Protocols.
"""

import sys
import os
import asyncio
import logging
from typing import Dict, Any, List, Optional

# Path setup to import internal protocols
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "sovereign_revenuecat_protocols"))

from revenuecat_backend_intelligence import RevenueCatBackendIntelligence
from gemini_app_generator import GeminiAppGeneratorEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SovereignFramework")

class RevenueCatConfig:
    def __init__(self, api_key: str = "rcb_v2_live_sovereign_key", project_id: str = "proj_sovereign_main"):
        self.api_key = api_key
        self.project_id = project_id

class SovereignApp:
    def __init__(self, app_name: str, rc_config: Optional[RevenueCatConfig] = None):
        self.app_name = app_name
        self.rc_config = rc_config or RevenueCatConfig()
        self.backend_intel = RevenueCatBackendIntelligence()
        self.gemini_generator = GeminiAppGeneratorEngine()
        
        logger.info(f"[Sovereign Framework v1.0.0] Initialized Framework for '{self.app_name}'.")

    async def build_and_deploy_app(self, prompt: str, marketplaces: List[str]) -> Dict[str, Any]:
        """
        Workflow 01: Builds full application stack, Motoko canisters, and RevenueCat offerings in 1 call.
        """
        logger.info(f"[{self.app_name}] Executing 1-Line Build & Deploy Workflow...")
        res = await self.gemini_generator.generate_entire_app_session(prompt, marketplaces)
        return res

    async def run_intelligence_cycle(self, user_id: str) -> Dict[str, Any]:
        """
        Runs full 20-protocol multi-agent backend cycle.
        """
        return await self.backend_intel.execute_autonomous_backend_cycle(user_id=user_id, app_prompt=self.app_name)

if __name__ == "__main__":
    app = SovereignApp("FitnessCopilot")
    asyncio.run(app.build_and_deploy_app("AI Fitness Coach", ["App Store", "Google Play"]))
