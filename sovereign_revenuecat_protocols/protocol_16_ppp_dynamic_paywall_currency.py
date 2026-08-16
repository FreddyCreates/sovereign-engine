"""
Protocol 16: Global Purchasing Power Parity (PPP) Paywall Adaptation Protocol
Adapts RevenueCat Paywall v2 experiment targeting based on subscriber country PPP multipliers
to optimize international conversion rates across US, Europe, Asia-Pacific, & LatAm.
"""

import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PPPDynamicPaywall")

class PPPDynamicPaywallCurrency:
    PPP_MULTIPLIERS = {
        "US": 1.00,  # Base US Price ($19.99/mo)
        "CA": 1.00,
        "GB": 0.95,
        "DE": 0.90,
        "JP": 0.75,
        "BR": 0.40,  # 60% PPP Discount for LatAm
        "IN": 0.30,  # 70% PPP Discount for India/SE Asia
        "NG": 0.25
    }

    def __init__(self):
        logger.info("[Protocol 16] Global PPP Dynamic Paywall Adaptation Active.")

    def get_adapted_paywall_offering(self, country_code: str, base_usd_price: float = 19.99) -> Dict[str, Any]:
        mult = self.PPP_MULTIPLIERS.get(country_code.upper(), 0.60) # Default international fallback
        adapted_price = round(base_usd_price * mult, 2)
        discount_percentage = round((1.0 - mult) * 100, 1)

        logger.info(f"[Protocol 16] Country: {country_code} | PPP Multiplier: {mult:.2f} | Adapted Price: ${adapted_price}/mo ({discount_percentage}% PPP Discount)")

        return {
            "country_code": country_code,
            "ppp_multiplier": mult,
            "original_usd_price": base_usd_price,
            "adapted_local_price_usd": adapted_price,
            "ppp_discount_percentage": discount_percentage,
            "revenuecat_offering_key": f"offering_ppp_{country_code.lower()}"
        }

if __name__ == "__main__":
    ppp = PPPDynamicPaywallCurrency()
    print("US Config:", ppp.get_adapted_paywall_offering("US"))
    print("Brazil Config:", ppp.get_adapted_paywall_offering("BR"))
