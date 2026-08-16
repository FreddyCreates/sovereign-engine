"""
Protocol 04: Kuramoto Coherence Paywall Targeting Protocol
Computes swarm phase coherence (R). If R < 0.618 (Inverse Phi), dynamically adjusts RevenueCat
Paywall v2 targeting rules and coupling strength (K) to maximize conversion & synchronization.
"""

import math
import cmath
import logging
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("KuramotoPaywall")

class KuramotoPaywallTargeting:
    PHI_INVERSE = 0.6180339887  # Golden Ratio Inverse

    def __init__(self, num_agents: int = 4):
        self.num_agents = num_agents
        self.coupling_strength = 1.0  # K
        self.agent_phases: List[float] = [0.0] * num_agents  # Theta_i in radians

    def set_agent_phases(self, phases: List[float]):
        if len(phases) == self.num_agents:
            self.agent_phases = phases

    def calculate_coherence(self) -> float:
        """
        Calculates order parameter R = (1/N) * |sum(exp(i * theta_j))|
        R ranges from 0.0 (incoherent) to 1.0 (perfect synchronization).
        """
        complex_sum = sum(cmath.exp(complex(0, theta)) for theta in self.agent_phases)
        r_order = abs(complex_sum) / self.num_agents
        logger.info(f"[Protocol 04] Swarm Kuramoto Coherence Order Parameter R = {r_order:.4f}")
        return r_order

    def optimize_paywall_targeting(self) -> Dict[str, Any]:
        R = self.calculate_coherence()
        
        if R < self.PHI_INVERSE:
            logger.warning(f"[Protocol 04] Coherence R ({R:.4f}) < Inverse Phi ({self.PHI_INVERSE:.4f})!")
            logger.info("[Protocol 04] Dynamic Coupling Active: Increasing K and switching to High-Conversion Paywall Offering.")
            self.coupling_strength *= 1.618
            return {
                "active_offering_id": "offering_high_conversion_phi",
                "paywall_variant": "variant_dark_glass_trial_first",
                "discount_active": True,
                "discount_percentage": 37.0,
                "coupling_strength_k": self.coupling_strength
            }
        else:
            logger.info(f"[Protocol 04] Swarm Coherence R ({R:.4f}) is Nominal.")
            return {
                "active_offering_id": "offering_main",
                "paywall_variant": "variant_standard_pro",
                "discount_active": False,
                "coupling_strength_k": self.coupling_strength
            }

if __name__ == "__main__":
    targeting = KuramotoPaywallTargeting(num_agents=4)
    # Test incoherent state
    targeting.set_agent_phases([0.0, 1.57, 3.14, 4.71])
    config = targeting.optimize_paywall_targeting()
    print("Targeting Config:", config)
