"""
Protocol 02: Real-Time Webhook Event Pulse Ingestion Protocol
Listens for RevenueCat subscription events (INITIAL_PURCHASE, RENEWAL, CANCELLATION, EXPIRATION)
and dispatches state updates across the Sovereign Swarm.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Callable

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WebhookPulse")

class WebhookIngestionPulse:
    def __init__(self):
        self.event_handlers: Dict[str, Callable] = {}
        self.register_default_handlers()

    def register_default_handlers(self):
        self.event_handlers["INITIAL_PURCHASE"] = self._on_initial_purchase
        self.event_handlers["RENEWAL"] = self._on_renewal
        self.event_handlers["CANCELLATION"] = self._on_cancellation
        self.event_handlers["EXPIRATION"] = self._on_expiration

    async def process_event(self, webhook_payload: Dict[str, Any]):
        event = webhook_payload.get("event", {})
        event_type = event.get("type")
        app_user_id = event.get("app_user_id")

        logger.info(f"[Protocol 02] Ingesting Webhook Event: {event_type} for User: {app_user_id}")

        handler = self.event_handlers.get(event_type)
        if handler:
            await handler(event)
        else:
            logger.warning(f"[Protocol 02] Unhandled event type: {event_type}")

    async def _on_initial_purchase(self, event: Dict[str, Any]):
        user_id = event.get("app_user_id")
        product_id = event.get("product_id")
        logger.info(f"[Protocol 02] 🎉 INITIAL PURCHASE confirmed: {user_id} -> {product_id}. Granting Sovereign Entitlement.")

    async def _on_renewal(self, event: Dict[str, Any]):
        user_id = event.get("app_user_id")
        logger.info(f"[Protocol 02] 🔄 RENEWAL processed for: {user_id}. Extending entitlement window.")

    async def _on_cancellation(self, event: Dict[str, Any]):
        user_id = event.get("app_user_id")
        logger.info(f"[Protocol 02] ⚠️ CANCELLATION notice for: {user_id}. Triggering retention pulse.")

    async def _on_expiration(self, event: Dict[str, Any]):
        user_id = event.get("app_user_id")
        logger.info(f"[Protocol 02] 🛑 EXPIRATION for: {user_id}. Revoking pro access.")

if __name__ == "__main__":
    pulse = WebhookIngestionPulse()
    sample_payload = {
        "event": {
            "type": "INITIAL_PURCHASE",
            "app_user_id": "usr_medin_01",
            "product_id": "parallax_pro_monthly"
        }
    }
    asyncio.run(pulse.process_event(sample_payload))
