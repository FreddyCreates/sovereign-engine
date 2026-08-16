"""
SYSTEM 3: PULSE — Predictive User Lifetime & Subscriber Retention Engine
Model: Weibull Survival Probability & Cox Proportional Hazards Churn Elasticity Model
Computes real-time subscriber survival rates, dynamic LTV, churn risk scores,
targeted retention discount offers, and RevenueCat winback hooks.
"""

import math
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PULSE_Engine")

class PULSEEngine:
    """PULSE System: Subscriber LTV Elasticity & Churn Telemetry Engine"""

    def __init__(self, default_arpu: float = 29.99):
        self.default_arpu = default_arpu
        self.user_telemetry: Dict[str, Dict[str, Any]] = {}
        logger.info(f"[PULSE System] Initialized with Default ARPU ${self.default_arpu:.2f}")

    def predict_survival_probability(self, tenure_days: int, alpha: float = 0.01, beta: float = 1.2) -> float:
        """
        Weibull Survival Probability: S(t) = exp(-(alpha * t)^beta)
        """
        if tenure_days <= 0:
            return 1.0
        survival = math.exp(-math.pow(alpha * tenure_days, beta))
        return round(max(0.0, min(1.0, survival)), 4)

    def calculate_discounted_ltv(self, arpu: float, monthly_churn_rate: float, discount_rate: float = 0.10, months: int = 24) -> float:
        """
        Calculates Net Present Value (NPV) Discounted Subscriber LTV over N months.
        LTV = sum_{t=1}^{months} (ARPU * (1 - churn)^t) / (1 + r/12)^t
        """
        monthly_r = discount_rate / 12.0
        total_ltv = 0.0

        for t in range(1, months + 1):
            survival_t = math.pow(1.0 - monthly_churn_rate, t)
            discount_factor = math.pow(1.0 + monthly_r, t)
            discounted_cash_flow = (arpu * survival_t) / discount_factor
            total_ltv += discounted_cash_flow

        return round(total_ltv, 2)

    def evaluate_churn_risk(self, user_id: str, engagement_score: float, support_tickets: int, tenure_days: int) -> float:
        """
        Evaluates churn risk probability score [0.0 - 1.0].
        """
        survival = self.predict_survival_probability(tenure_days)
        inactivity_factor = max(0.0, 1.0 - max(0.0, min(1.0, engagement_score)))
        support_factor = min(1.0, support_tickets * 0.15)

        churn_risk = (1.0 - survival) * 0.4 + inactivity_factor * 0.4 + support_factor * 0.2
        churn_risk_score = round(max(0.0, min(1.0, churn_risk)), 4)

        self.user_telemetry[user_id] = {
            "churn_risk": churn_risk_score,
            "survival_prob": survival,
            "tenure_days": tenure_days
        }
        logger.info(f"[PULSE] Churn Risk for {user_id}: {churn_risk_score:.4f} (Survival: {survival:.4f})")
        return churn_risk_score

    def generate_targeted_retention_offer(self, user_id: str, churn_risk_score: float, expected_ltv: float) -> Dict[str, Any]:
        """
        Generates dynamic retention offer based on churn risk and expected LTV.
        """
        if churn_risk_score >= 0.70:
            discount_pct = 40.0
            offer_type = "AGGRESSIVE_WINBACK_40_OFF"
        elif churn_risk_score >= 0.40:
            discount_pct = 20.0
            offer_type = "MODERATE_RETENTION_20_OFF"
        else:
            discount_pct = 0.0
            offer_type = "STANDARD_RENEWAL"

        offer = {
            "system": "PULSE",
            "user_id": user_id,
            "churn_risk_score": churn_risk_score,
            "expected_ltv": expected_ltv,
            "discount_pct": discount_pct,
            "offer_type": offer_type,
            "eligible": discount_pct > 0
        }
        logger.info(f"[PULSE] Retention Offer for {user_id}: {offer_type} ({discount_pct}% OFF)")
        return offer

    def trigger_revenuecat_winback_hook(self, user_id: str, discount_pct: float) -> Dict[str, Any]:
        """
        Simulates payload delivery to RevenueCat Customer Center / Webhook for Winback campaign.
        """
        hook_payload = {
            "event": "REVENUECAT_WINBACK_TRIGGERED",
            "user_id": user_id,
            "applied_discount_pct": discount_pct,
            "status": "DISPATCHED",
            "channel": "REVENUECAT_CUSTOMER_CENTER"
        }
        logger.info(f"[PULSE] RevenueCat Winback Hook Dispatched for {user_id}")
        return hook_payload

    def route_churn_prevention_path(self, R_coherence: float = 0.54) -> Dict[str, Any]:
        """
        Routes churn prevention intervention based on Kuramoto phase coherence R_coherence.
        """
        is_high_risk = R_coherence < 0.618
        action = "REVENUECAT_CUSTOMER_CENTER_INTERCEPT" if is_high_risk else "STANDARD_RETENTION"
        return {
            "system": "PULSE",
            "coherence_R": R_coherence,
            "is_high_churn_risk": is_high_risk,
            "recommended_action": action,
            "applied_discount_pct": 50.0 if is_high_risk else 0.0
        }

