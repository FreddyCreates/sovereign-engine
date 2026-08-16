"""
SYSTEM 6: NEXS — Neural Dynamic App Synthesis & Paywall Optimization Engine
Model: Multi-Armed Bandit (UCB1) & Dynamic Purchasing Power Parity (PPP) Price Elasticity Model
Synthesizes real-time paywall variants, optimizes price elasticity per region,
tracks paywall conversion rates, and unlocks dynamic AI feature entitlements via RevenueCat.
"""

import math
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NEXS_Engine")

PPP_FACTORS = {
    "US": 1.00,
    "DE": 0.95,
    "GB": 1.00,
    "BR": 0.45,
    "IN": 0.35,
    "JP": 0.85
}

class NEXSEngine:
    """NEXS System: Neural Paywall Synthesis & Dynamic Pricing Engine"""

    def __init__(self, exploration_factor: float = 1.414):
        self.exploration_factor = exploration_factor
        self.paywall_variants = {
            "var_A_minimal": {"trials": 0, "conversions": 0, "revenue": 0.0},
            "var_B_feature_list": {"trials": 0, "conversions": 0, "revenue": 0.0},
            "var_C_annual_discount": {"trials": 0, "conversions": 0, "revenue": 0.0},
            "var_D_crypto_rebate": {"trials": 0, "conversions": 0, "revenue": 0.0}
        }
        self.total_trials = 0
        logger.info("[NEXS System] Initialized Neural Dynamic Paywall Synthesis Engine.")

    def select_optimal_paywall_variant(self, user_id: str, user_segment: str = "DEFAULT") -> str:
        """
        Selects paywall variant using UCB1 Multi-Armed Bandit algorithm:
        UCB_i = mean_reward_i + c * sqrt(ln(N) / n_i)
        """
        self.total_trials += 1
        best_variant = None
        best_ucb = -1.0

        for var_id, stats in self.paywall_variants.items():
            n_i = stats["trials"]
            if n_i == 0:
                best_variant = var_id
                break
            
            mean_reward = stats["conversions"] / n_i
            ucb_value = mean_reward + self.exploration_factor * math.sqrt(math.log(self.total_trials) / n_i)
            
            if ucb_value > best_ucb:
                best_ucb = ucb_value
                best_variant = var_id

        # Update trial counter for selected variant
        self.paywall_variants[best_variant]["trials"] += 1
        logger.info(f"[NEXS] Variant Selected for {user_id} ({user_segment}): {best_variant} (UCB: {best_ucb:.4f})")
        return best_variant

    def record_paywall_conversion(self, variant_id: str, converted: bool, revenue_usd: float = 0.0):
        """Records conversion outcome and updates bandit statistics."""
        if variant_id in self.paywall_variants:
            if converted:
                self.paywall_variants[variant_id]["conversions"] += 1
                self.paywall_variants[variant_id]["revenue"] += revenue_usd
            logger.info(f"[NEXS] Recorded outcome for {variant_id}: Converted={converted}, Revenue=${revenue_usd:.2f}")

    def synthesize_dynamic_offering(self, user_id: str, region_code: str, base_usd_price: float = 19.99) -> Dict[str, Any]:
        """
        Synthesizes localized dynamic offering price using Purchasing Power Parity (PPP) elasticity factor.
        """
        ppp_factor = PPP_FACTORS.get(region_code, 1.0)
        adapted_price = round(base_usd_price * ppp_factor, 2)
        variant = self.select_optimal_paywall_variant(user_id, region_code)

        offering = {
            "system": "NEXS",
            "user_id": user_id,
            "region_code": region_code,
            "base_usd_price": base_usd_price,
            "ppp_factor": ppp_factor,
            "adapted_usd_price": adapted_price,
            "selected_variant": variant,
            "ai_entitlements_unlocked": ["neural_copilot", "predictive_signals", "hyper_automation"]
        }
        logger.info(f"[NEXS] Synthesized Offering for {user_id} in {region_code}: ${adapted_price:.2f} (Variant: {variant})")
        return offering

    def calculate_segment_elasticity(self, price_point_1: float, demand_1: int, price_point_2: float, demand_2: int) -> float:
        """
        Calculates Price Elasticity of Demand (PED) = (% Change in Q) / (% Change in P)
        """
        if price_point_1 <= 0 or demand_1 <= 0 or price_point_1 == price_point_2:
            return 0.0

        pct_change_q = (demand_2 - demand_1) / demand_1
        pct_change_p = (price_point_2 - price_point_1) / price_point_1
        
        ped = pct_change_q / pct_change_p
        return round(ped, 4)

    def get_paywall_performance_stats(self) -> Dict[str, Any]:
        """Returns stats for all paywall variants."""
        summary = {}
        for var_id, stats in self.paywall_variants.items():
            n = stats["trials"]
            c = stats["conversions"]
            conv_rate = round(c / n, 4) if n > 0 else 0.0
            summary[var_id] = {
                "trials": n,
                "conversions": c,
                "conversion_rate": conv_rate,
                "total_revenue_usd": round(stats["revenue"], 2)
            }
        return {
            "total_trials": self.total_trials,
            "variants": summary
        }
