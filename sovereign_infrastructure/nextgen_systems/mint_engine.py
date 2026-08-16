"""
SYSTEM 4: MINT — Market Inflation Deflationary Tokenomics & Liquidity System
Model: Bonding Curve & Dynamic Token Velocity Deflation Model
Executes RevenueCat fiat-to-token minting, dynamic token burning on subscription renewals,
staking yield distribution, and protocol liquidity tracking.
"""

import math
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MINT_Engine")

class MINTEngine:
    """MINT System: Deflationary Tokenomics & Subscription Liquidity Entitlement Engine"""

    def __init__(self, initial_supply: float = 1000000.0, base_price_usd: float = 1.00, burn_rate: float = 0.15):
        self.total_supply = initial_supply
        self.total_burned = 0.0
        self.base_price_usd = base_price_usd
        self.burn_rate = burn_rate
        self.user_token_balances: Dict[str, float] = {}
        self.user_staked_balances: Dict[str, float] = {}
        logger.info(f"[MINT System] Initialized: Supply={self.total_supply:,.2f}, BurnRate={self.burn_rate*100}%")

    def calculate_bonding_price(self, current_supply: float, alpha: float = 0.5) -> float:
        """
        Calculates token price using polynomial bonding curve: P(S) = P0 + 0.0001 * S^alpha
        """
        price = self.base_price_usd + 0.0001 * math.pow(current_supply, alpha)
        return round(price, 4)

    def mint_fiat_backed_tokens(self, user_id: str, fiat_amount_usd: float) -> Dict[str, Any]:
        """
        Mints tokens proportional to RevenueCat fiat subscription payment using current bonding curve price.
        """
        current_price = self.calculate_bonding_price(self.total_supply)
        tokens_minted = round(fiat_amount_usd / current_price, 4)

        self.total_supply += tokens_minted
        self.user_token_balances[user_id] = round(self.user_token_balances.get(user_id, 0.0) + tokens_minted, 4)

        logger.info(f"[MINT] Minted {tokens_minted} tokens for {user_id} (${fiat_amount_usd:.2f} USD at ${current_price:.4f})")
        return {
            "system": "MINT",
            "user_id": user_id,
            "fiat_usd": fiat_amount_usd,
            "token_price_usd": current_price,
            "tokens_minted": tokens_minted,
            "user_balance": self.user_token_balances[user_id],
            "total_supply": round(self.total_supply, 2)
        }

    def execute_subscription_burn(self, user_id: str, renewal_amount_usd: float) -> Dict[str, Any]:
        """
        Executes deflationary token burn when a RevenueCat subscription renews.
        """
        current_price = self.calculate_bonding_price(self.total_supply)
        equivalent_tokens = renewal_amount_usd / current_price
        tokens_to_burn = round(equivalent_tokens * self.burn_rate, 4)

        # Deduct from total supply to create deflationary pressure
        self.total_supply = max(0.0, self.total_supply - tokens_to_burn)
        self.total_burned += tokens_to_burn

        logger.info(f"[MINT] Burned {tokens_to_burn} tokens on {user_id} renewal. Total Burned: {self.total_burned:,.2f}")
        return {
            "system": "MINT",
            "user_id": user_id,
            "renewal_usd": renewal_amount_usd,
            "tokens_burned": tokens_to_burn,
            "total_burned": round(self.total_burned, 2),
            "new_total_supply": round(self.total_supply, 2)
        }

    def distribute_staking_yield(self, user_id: str, staked_amount: float, apy_pct: float = 12.0) -> Dict[str, Any]:
        """
        Calculates and distributes monthly protocol yield for staked subscriber tokens.
        """
        monthly_rate = (apy_pct / 100.0) / 12.0
        yield_tokens = round(staked_amount * monthly_rate, 4)

        self.user_staked_balances[user_id] = round(self.user_staked_balances.get(user_id, 0.0) + staked_amount, 4)
        self.user_token_balances[user_id] = round(self.user_token_balances.get(user_id, 0.0) + yield_tokens, 4)

        logger.info(f"[MINT] Yield Dist: {yield_tokens} tokens awarded to {user_id} (APY: {apy_pct}%)")
        return {
            "system": "MINT",
            "user_id": user_id,
            "staked_amount": staked_amount,
            "apy_pct": apy_pct,
            "monthly_yield_tokens": yield_tokens,
            "user_token_balance": self.user_token_balances[user_id]
        }

    def get_tokenomics_state(self) -> Dict[str, Any]:
        """Returns total supply, total burned, and current bonding curve price."""
        return {
            "total_supply": round(self.total_supply, 2),
            "total_burned": round(self.total_burned, 2),
            "current_token_price": self.calculate_bonding_price(self.total_supply),
            "burn_rate_pct": self.burn_rate * 100
        }
