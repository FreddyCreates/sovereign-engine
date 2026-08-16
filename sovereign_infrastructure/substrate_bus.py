"""
Sovereign Substrate Bus
Decoupled event bus connecting the 6 independent Core Engines into a unified infrastructure substrate.
Developers and platforms build on top of this substrate by importing cores or subscribing to bus events.
"""

import sys
import os
import json
import asyncio
import logging
from typing import Dict, Any, List

sys.path.append(os.path.join(os.path.dirname(__file__), "cores"))

from billing_core import RevenueCatBillingCore
from paywall_core import PaywallMutationCore
from retention_core import CustomerCenterRetentionCore
from app_builder_core import GeminiAppBuilderCore
from iot_telemetry_core import IoTHardwareTelemetryCore
from ppp_localization_core import PPPLocalizationCore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SubstrateBus")

class SovereignSubstrateBus:
    def __init__(self):
        logger.info("==========================================================================")
        logger.info("      SOVEREIGN SUBSTRATE BUS — INDEPENDENT CORE ENGINE INFRASTRUCTURE    ")
        logger.info("==========================================================================")
        
        # Instantiate 6 independent Core Engines
        self.billing = RevenueCatBillingCore()
        self.paywall = PaywallMutationCore()
        self.retention = CustomerCenterRetentionCore()
        self.app_builder = GeminiAppBuilderCore()
        self.iot = IoTHardwareTelemetryCore()
        self.ppp = PPPLocalizationCore()

    async def execute_decoupled_event_pipeline(self, user_id: str = "usr_dev_01", country: str = "DE") -> Dict[str, Any]:
        logger.info(f"[Substrate Bus] Pipeline Execution for User: {user_id} ({country})")

        # 1. PPP Core calculates localized pricing
        local_price = self.ppp.compute_local_price(19.99, country)

        # 2. Billing Core processes purchase event
        billing_event = self.billing.process_lifecycle_event(user_id, "INITIAL_PURCHASE", "monthly_pro", local_price["local_price"])

        # 3. Paywall Core mutates Paywall v2 AST
        paywall_event = self.paywall.compute_coherence_and_mutate(scroll_depth=0.88, engagement_score=0.92)

        # 4. IoT Core syncs connected Wear OS watch
        iot_event = self.iot.sync_hardware_entitlements("WEAR_OS_WATCH_01", "WEAR_OS_WATCH", billing_event["entitlements"])

        return {
            "status": "SUBSTRATE_PIPELINE_COMPLETE",
            "ppp_localization": local_price,
            "billing": billing_event,
            "paywall_mutation": paywall_event,
            "iot_hardware_sync": iot_event
        }

if __name__ == "__main__":
    bus = SovereignSubstrateBus()
    res = asyncio.run(bus.execute_decoupled_event_pipeline("usr_builder_01", "BR"))
    print("\nSubstrate Pipeline Output:\n", json.dumps(res, indent=2))
