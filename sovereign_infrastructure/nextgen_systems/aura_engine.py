"""
SYSTEM 2: AURA — Algorithmic Underwriting & Credit Risk Assessment System
Model: Logistic Credit Default Probability & Expected Loss Model
Calculates subscriber credit risk scores, underwrites BNPL / deferred subscriptions,
determines risk tiers, and manages subscriber credit limits integrated with RevenueCat.
"""

import math
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AURA_Engine")

class AURAEngine:
    """AURA System: Credit Risk Underwriting & Subscriber Default Prediction Engine"""

    def __init__(self, base_credit_limit: float = 1000.0):
        self.base_credit_limit = base_credit_limit
        self.user_credit_profiles: Dict[str, Dict[str, Any]] = {}
        logger.info(f"[AURA System] Initialized with Base Credit Limit ${self.base_credit_limit:.2f}")

    def evaluate_credit_risk(self, user_id: str, payment_history_ratio: float, chargebacks: int, tenure_months: int) -> float:
        """
        Calculates Probability of Default (PD) using Logistic Credit Risk Scoring model.
        PD = 1 / (1 + e^-z)
        """
        beta_0 = 0.5
        beta_1 = 3.2 * (1.0 - max(0.0, min(1.0, payment_history_ratio)))
        beta_2 = 1.5 * max(0, chargebacks)
        beta_3 = 0.4 * math.log(max(1, tenure_months))

        z = beta_0 + beta_1 + beta_2 - beta_3
        pd = 1.0 / (1.0 + math.exp(-z))
        pd_rounded = round(pd, 4)

        logger.info(f"[AURA] Risk Evaluation for {user_id}: PD={pd_rounded:.4f} (z={z:.2f})")
        return pd_rounded

    def determine_risk_tier(self, pd: float) -> str:
        """Categorizes user PD into risk tiers."""
        if pd < 0.15:
            return "LOW"
        elif pd < 0.40:
            return "MEDIUM"
        elif pd < 0.70:
            return "HIGH"
        else:
            return "CRITICAL"

    def calculate_expected_loss(self, pd: float, lgd: float = 0.6, ead: float = 500.0) -> float:
        """
        Calculates Expected Loss (EL) = PD * LGD * EAD
        """
        el = pd * lgd * ead
        return round(el, 2)

    def underwrite_subscription_bnpl(self, user_id: str, subscription_cost: float, pd: float) -> Dict[str, Any]:
        """
        Evaluates whether a subscriber qualifies for BNPL / deferred RevenueCat subscription billing.
        """
        risk_tier = self.determine_risk_tier(pd)
        approved = (pd < 0.50) and (subscription_cost <= self.base_credit_limit)

        status = "APPROVED" if approved else "DECLINED"
        result = {
            "system": "AURA",
            "user_id": user_id,
            "subscription_cost": subscription_cost,
            "pd": pd,
            "risk_tier": risk_tier,
            "status": status,
            "max_approved_limit": round(self.base_credit_limit * (1.0 - pd), 2)
        }
        self.user_credit_profiles[user_id] = result
        logger.info(f"[AURA] BNPL Underwriting for {user_id}: {status} (Tier: {risk_tier})")
        return result

    def adjust_credit_limit(self, user_id: str, performance_score: float) -> float:
        """
        Dynamically adjusts user credit limit based on subscription payment performance score [0.0 - 1.0].
        """
        multiplier = 0.5 + max(0.0, min(1.0, performance_score)) * 1.5
        new_limit = round(self.base_credit_limit * multiplier, 2)
        logger.info(f"[AURA] Credit Limit for {user_id} adjusted to ${new_limit:.2f} (Score: {performance_score})")
        return new_limit

    def evaluate_credit_score(self, lifetime_spent_usd: float = 10000.0, active_months: int = 12) -> int:
        """
        Calculates AURA credit score in range [300 - 850] based on lifetime spend and subscriber tenure.
        """
        base_score = 650
        spend_bonus = min(150, int((lifetime_spent_usd / 10000.0) * 100))
        tenure_bonus = min(50, active_months * 4)
        score = base_score + spend_bonus + tenure_bonus
        return min(850, max(300, score))

    def underwrite_micro_credit(self, client_id: str, credit_score: int) -> Dict[str, Any]:
        """
        Evaluates B2B invoice micro-credit underwrite status based on credit score.
        """
        status = "APPROVED (AURA Prime Tier)" if credit_score >= 750 else "REQUIRES DEPOSIT"
        return {
            "system": "AURA",
            "client_id": client_id,
            "credit_score": credit_score,
            "underwriting_status": status
        }

