"""
Protocol 06: FORMA φ-Yield Entitlement Scaling Protocol
Calculates compounding yields based on the Golden Ratio (phi = 1.6180339887)
and scales yield multipliers based on RevenueCat subscription tier.
"""

import math
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FormaYieldEntitlement")

class FormaYieldEntitlement:
    PHI = 1.6180339887
    BASE_YIELD_RATE = PHI - 1.0  # 0.6180339887 annualised (61.8%)

    def __init__(self):
        logger.info(f"[Protocol 06] FORMA φ-Yield Protocol Initialized (Base φ-Rate: {self.BASE_YIELD_RATE:.4%}).")

    def calculate_yield(self, staked_amount: float, entitlement_tier: str, duration_days: float) -> Dict[str, Any]:
        multiplier = 1.0
        if entitlement_tier == "pro_access":
            multiplier = 1.618  # 1.618x Golden Multiplier
        elif entitlement_tier == "enterprise_access":
            multiplier = 2.618  # Phi^2 Multiplier

        effective_rate = self.BASE_YIELD_RATE * multiplier
        years = duration_days / 365.0
        accrued_yield = staked_amount * ((1.0 + effective_rate) ** years - 1.0)
        total_balance = staked_amount + accrued_yield

        logger.info(f"[Protocol 06] Staked: {staked_amount} FORMA | Tier: {entitlement_tier} | Multiplier: {multiplier}x | Accrued: {accrued_yield:.2f} FORMA")

        return {
            "staked_amount": staked_amount,
            "entitlement_tier": entitlement_tier,
            "yield_multiplier": multiplier,
            "effective_annual_rate": effective_rate,
            "accrued_yield_forma": round(accrued_yield, 4),
            "total_forma_balance": round(total_balance, 4)
        }

if __name__ == "__main__":
    yield_calc = FormaYieldEntitlement()
    res = yield_calc.calculate_yield(10000.0, "pro_access", 365.0)
    print("Yield Projection:", res)
