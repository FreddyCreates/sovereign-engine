"""
SYSTEM 2: AURA — Algorithmic Underwriting & Credit Risk Assessment System
Model: Logistic Credit Default Probability & Expected Loss Model
Calculates subscriber credit risk scores, underwrites BNPL / deferred subscriptions,
determines risk tiers, manages subscriber credit limits integrated with RevenueCat,
and posts double-entry accounting records to General Ledger, AP & Balance Sheet.
"""

import math
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AURA_Engine")

class AURAEngine:
    """AURA System: Credit Risk Underwriting & Subscriber Default Prediction Engine integrated with Full SaaS Accounting"""

    def __init__(self, base_credit_limit: float = 1000.0, gl: Optional[Any] = None, ap: Optional[Any] = None, bs: Optional[Any] = None):
        self.base_credit_limit = base_credit_limit
        self.gl = gl
        self.ap = ap
        self.bs = bs
        self.user_credit_profiles: Dict[str, Dict[str, Any]] = {}
        logger.info(f"[AURA System] Initialized with Base Credit Limit ${self.base_credit_limit:.2f}")

    def set_accounting_suite(self, gl: Any = None, ap: Any = None, bs: Any = None):
        """Inject General Ledger, Accounts Payable, and Balance Sheet engines."""
        self.gl = gl
        self.ap = ap
        self.bs = bs

    def evaluate_credit_risk(self, user_id: str, payment_history_ratio: float = 0.95, chargebacks: int = 0, tenure_months: int = 12, **kwargs) -> float:
        """
        Calculates Probability of Default (PD) using Logistic Credit Risk Scoring model.
        PD = 1 / (1 + e^-z)
        """
        # Handle cases where spent_usd or different numeric args are passed
        if isinstance(payment_history_ratio, (int, float)) and payment_history_ratio > 1.0:
            payment_ratio = min(1.0, max(0.0, 1.0 - (chargebacks * 0.1)))
        else:
            payment_ratio = max(0.0, min(1.0, float(payment_history_ratio)))

        chargebacks_cnt = max(0, int(chargebacks))
        tenure_m = max(1, int(tenure_months))

        beta_0 = 0.5
        beta_1 = 3.2 * (1.0 - payment_ratio)
        beta_2 = 1.5 * chargebacks_cnt
        beta_3 = 0.4 * math.log(tenure_m)

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
        Posts Accounts Receivable journal entry in General Ledger upon approval.
        """
        risk_tier = self.determine_risk_tier(pd)
        approved = (pd < 0.50) and (subscription_cost <= self.base_credit_limit)

        status = "APPROVED" if approved else "DECLINED"
        approved_limit = round(self.base_credit_limit * (1.0 - pd), 2)

        gl_entry_id = None
        expected_loss = self.calculate_expected_loss(pd, lgd=0.6, ead=subscription_cost)

        if approved and self.gl:
            try:
                # Debit Accounts Receivable 1200, Credit Subscription Revenue 4010
                entry = self.gl.record_journal_entry(
                    description=f"AURA BNPL AR Entry - {user_id}",
                    debits={"1200": round(subscription_cost, 2)},
                    credits={"4010": round(subscription_cost, 2)},
                    entry_type="AURA_BNPL_AR",
                    reference=f"BNPL-{user_id}"
                )
                gl_entry_id = entry.get("entry_id")
            except Exception as e:
                logger.warning(f"[AURA] GL AR entry warning: {e}")

        result = {
            "system": "AURA",
            "user_id": user_id,
            "subscription_cost": subscription_cost,
            "pd": pd,
            "risk_tier": risk_tier,
            "status": status,
            "max_approved_limit": approved_limit,
            "approved_amount": subscription_cost if approved else 0.0,
            "expected_loss": expected_loss,
            "gl_entry_id": gl_entry_id
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
        Integrates with Accounts Payable / Receivable aging schedules.
        """
        status = "APPROVED (AURA Prime Tier)" if credit_score >= 750 else "REQUIRES DEPOSIT"
        ap_aging = self.ap.get_ap_aging_schedule() if self.ap else {"status": "BILL_COM_REPLACED"}

        return {
            "system": "AURA",
            "client_id": client_id,
            "credit_score": credit_score,
            "underwriting_status": status,
            "ap_aging_summary": ap_aging
        }
