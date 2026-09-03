"""
SOVEREIGN GRANTS AND APP CAPITAL ENGINE
==================================================================================
Production-Grade Engine for Active Business Grants & Revenue-Based Capital.

Grants Covered:
  - SBIR / STTR (US Federal R&D Grants)
  - RevenueCat Growth & Mobile Developer Grants
  - AWS Activate & Google Cloud for Startups Grants
  - FedDev Ontario / Canadian Regional Economic Development
  - EIC Accelerator (European Innovation Council)

Revenue-Based Capital Platforms Covered:
  - Stripe Capital
  - Pipe
  - Capchase
  - Braavo (Braavo Capital for Mobile Apps)
  - Clearco (Clearbanc Revenue-Based Capital)

Author: Sovereign OS Platform Architect
"""

import math
import time
import uuid
import logging
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any, List, Optional, Union

logger = logging.getLogger("SovereignGrantsAndAppCapitalEngine")


def get_utc_timestamp_str() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


class SovereignGrantsAndAppCapitalEngine:
    """
    Core engine managing active business grants, eligibility scoring,
    and revenue-based app financing offer calculations.
    """

    def __init__(self):
        self.grants_catalog = self._init_grants_catalog()
        self.capital_platforms = self._init_capital_platforms()
        self.applications_log: List[Dict[str, Any]] = []
        self.drawdowns_log: List[Dict[str, Any]] = []

    def _init_grants_catalog(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "grant-sbir-sttr",
                "name": "SBIR / STTR Small Business Innovation Research",
                "agency": "US Federal Government (NSF, NIH, DoD, DoE, NASA)",
                "category": "R&D & Deeptech Innovation",
                "non_dilutive": True,
                "grant_min_amount": 50000.0,
                "grant_max_amount": 1800000.0,
                "currency": "USD",
                "phase_i_amount": 275000.0,
                "phase_ii_amount": 1800000.0,
                "equity_taken_pct": 0.0,
                "eligible_countries": ["US"],
                "target_stage": "Pre-seed to Seed / High-Tech R&D",
                "key_criteria": [
                    "For-profit US small business (<500 employees)",
                    ">51% US citizen or permanent resident ownership",
                    "High scientific/technical risk with commercialization potential",
                    "STTR requires min 30% formal collaboration with US research institution"
                ],
                "application_window": "Rolling / 3 Windows per year (Jan, May, Sept)",
                "url": "https://www.sbir.gov"
            },
            {
                "id": "grant-revenuecat-growth",
                "name": "RevenueCat Growth & Developer Grants",
                "agency": "RevenueCat Mobile Developer Fund",
                "category": "Mobile & Web Subscription Apps",
                "non_dilutive": True,
                "grant_min_amount": 10000.0,
                "grant_max_amount": 50000.0,
                "currency": "USD",
                "perks_included": [
                    "$10,000 - $50,000 non-equity grant credit",
                    "Free RevenueCat Pro Tier up to $100k MTR",
                    "App Store Optimization (ASO) & UA campaign mentorship",
                    "1:1 sessions with top subscription app founders"
                ],
                "equity_taken_pct": 0.0,
                "eligible_countries": ["Global"],
                "target_stage": "Indie Developers & Early Stage Mobile Startups (MRR < $50k)",
                "key_criteria": [
                    "Active iOS or Android subscription app integrated with StoreKit 2 / Google Play",
                    "Monthly recurring revenue under $50,000",
                    "High retention or promising trial-to-paid conversion metrics"
                ],
                "application_window": "Open Quarterly",
                "url": "https://www.revenuecat.com/grants"
            },
            {
                "id": "grant-cloud-aws-google",
                "name": "AWS Activate & Google Cloud Startup Grants",
                "agency": "Amazon Web Services & Google Cloud",
                "category": "Cloud Infrastructure & AI Compute",
                "non_dilutive": True,
                "grant_min_amount": 5000.0,
                "grant_max_amount": 350000.0,
                "currency": "USD",
                "aws_activate_portfolio": 100000.0,
                "gcp_startup_credits": 200000.0,
                "gcp_ai_grant": 350000.0,
                "equity_taken_pct": 0.0,
                "eligible_countries": ["Global"],
                "target_stage": "Bootstrap to Series A Startups",
                "key_criteria": [
                    "Incorporated tech business under 10 years old",
                    "Not previously received max tier cloud credits",
                    "AI Startups eligible for up to $350k GenAI compute credits on GCP"
                ],
                "application_window": "Always Open / Continuous",
                "url": "https://aws.amazon.com/activate / https://cloud.google.com/startup"
            },
            {
                "id": "grant-feddev-ontario",
                "name": "FedDev Ontario Business Scale-up & Growth Grant",
                "agency": "Government of Canada (FedDev Ontario)",
                "category": "Regional Industrial Scale-up & Cleantech",
                "non_dilutive": True,
                "grant_min_amount": 500000.0,
                "grant_max_amount": 10000000.0,
                "currency": "CAD",
                "equity_taken_pct": 0.0,
                "repayable": True,
                "interest_rate_pct": 0.0,
                "eligible_countries": ["CA"],
                "target_stage": "Growth & Scale-up Tech SMEs",
                "key_criteria": [
                    "Located in Southern Ontario, Canada",
                    "Minimum 5 full-time employees and 3 years operations",
                    "Developing innovative export-ready tech/manufacturing",
                    "Co-funding requirement (covers up to 50% eligible costs)"
                ],
                "application_window": "Continuous Intake",
                "url": "https://www.feddevontario.gc.ca"
            },
            {
                "id": "grant-eic-accelerator",
                "name": "EIC Accelerator (European Innovation Council)",
                "agency": "European Union / Horizon Europe",
                "category": "Deeptech & Breakthrough Innovation",
                "non_dilutive": False,
                "grant_component_max": 2500000.0,
                "equity_component_max": 15000000.0,
                "currency": "EUR",
                "grant_co_funding_pct": 70.0,
                "eligible_countries": ["EU Member States", "Horizon Europe Associated"],
                "target_stage": "TRL 5/6 to TRL 8/9 High-Risk Deeptech Startups",
                "key_criteria": [
                    "SME established in EU or Horizon Europe associated country",
                    "Game-changing breakthrough technology (high risk / high impact)",
                    "Requires grant for TRL 5-8 R&D and equity for TRL 9 commercial deployment"
                ],
                "application_window": "4 Cut-off Dates per Year",
                "url": "https://eic.ec.europa.eu"
            }
        ]

    def _init_capital_platforms(self) -> List[Dict[str, Any]]:
        return [
            {
                "platform_id": "platform-stripe-capital",
                "name": "Stripe Capital",
                "type": "Embedded Revenue-Based Financing",
                "max_advance_pct_of_arr": 20.0,
                "flat_fee_pct_range": [6.0, 10.0],
                "daily_withholding_pct_range": [8.0, 15.0],
                "underwriting_source": "Stripe Payment Volume & Transaction Health",
                "no_personal_guarantee": True,
                "no_equity_dilution": True,
                "description": "Seamless capital advance repaid via a fixed percentage of daily Stripe processing sales."
            },
            {
                "platform_id": "platform-pipe",
                "name": "Pipe",
                "type": "Recurring Revenue Trading Platform",
                "max_advance_pct_of_arr": 40.0,
                "micro_discount_rate_pct": [4.0, 8.0],
                "payout_upfront_pct": [92.0, 96.0],
                "underwriting_source": "ARR Quality, Churn & Subscriber Retention",
                "no_personal_guarantee": True,
                "no_equity_dilution": True,
                "description": "Trade active annual/monthly subscription contracts for immediate upfront capital."
            },
            {
                "platform_id": "platform-capchase",
                "name": "Capchase (Capchase Grow & Pay)",
                "type": "SaaS & Subscription Revenue Financing",
                "max_advance_pct_of_arr": 60.0,
                "fee_pct_range": [5.0, 9.0],
                "repayment_term_months": 12,
                "underwriting_source": "Bank Accounts, Accounting (QuickBooks/Xero) & Billing API",
                "no_personal_guarantee": True,
                "no_equity_dilution": True,
                "description": "Draw up to 60% of ARR with flexible monthly repayments synced to actual collections."
            },
            {
                "platform_id": "platform-braavo",
                "name": "Braavo Capital",
                "type": "App Store & Mobile Revenue Financing",
                "max_advance_pct_of_arr": 50.0,
                "products": ["Braavo Reserve", "Braavo Yield", "Braavo Accelerate"],
                "fee_pct_range": [3.5, 7.5],
                "underwriting_source": "App Store Connect, Google Play Console & MMP (AppsFlyer/Adjust)",
                "no_personal_guarantee": True,
                "no_equity_dilution": True,
                "description": "Accelerate App Store payouts, fund user acquisition, and scale subscription app MRR."
            },
            {
                "platform_id": "platform-clearco",
                "name": "Clearco (Clearbanc)",
                "type": "Revenue-Based Capital for Apps & E-Commerce",
                "max_advance_pct_of_arr": 45.0,
                "flat_fee_pct_range": [6.0, 12.0],
                "daily_withholding_pct_range": [5.0, 10.0],
                "underwriting_source": "Ad Account Performance (Meta/Google Ads) & Revenue Streams",
                "no_personal_guarantee": True,
                "no_equity_dilution": True,
                "description": "Capital advances specifically for scaling ad campaigns, user acquisition, and inventory."
            }
        ]

    def get_grants_catalog(
        self,
        category_filter: Optional[str] = None,
        country_filter: Optional[str] = None,
        max_amount: Optional[float] = None
    ) -> Dict[str, Any]:
        catalog = list(self.grants_catalog)
        if category_filter:
            catalog = [g for g in catalog if category_filter.lower() in g["category"].lower()]
        if country_filter:
            catalog = [g for g in catalog if "Global" in g["eligible_countries"] or country_filter.upper() in g["eligible_countries"]]
        if max_amount:
            catalog = [g for g in catalog if g.get("grant_min_amount", 0) <= max_amount]

        total_grant_pool = sum(g.get("grant_max_amount", g.get("grant_component_max", 0)) for g in self.grants_catalog)

        return {
            "status": "success",
            "timestamp": get_utc_timestamp_str(),
            "total_grants_available": len(catalog),
            "aggregate_grant_pool_value_usd": round(total_grant_pool, 2),
            "grants": catalog
        }

    def get_capital_offers(
        self,
        mrr: float = 148920.0,
        arr: Optional[float] = None,
        store_platform: str = "RevenueCat StoreKit 2"
    ) -> Dict[str, Any]:
        calculated_arr = arr if arr is not None else (mrr * 12.0)
        offers = []

        # 1. Stripe Capital
        sc_max = round(calculated_arr * 0.20, 2)
        sc_fee_pct = 7.5
        sc_fee_amt = round(sc_max * (sc_fee_pct / 100.0), 2)
        offers.append({
            "platform_id": "platform-stripe-capital",
            "name": "Stripe Capital",
            "max_eligible_advance": sc_max,
            "flat_fee_pct": sc_fee_pct,
            "flat_fee_amount": sc_fee_amt,
            "total_repayable": round(sc_max + sc_fee_amt, 2),
            "daily_withholding_rate_pct": 10.0,
            "estimated_payoff_days": 240,
            "underwriting_source": "Stripe Sales Analytics",
            "equity_dilution_pct": 0.0,
            "non_dilutive_score": 98.5
        })

        # 2. Pipe
        pipe_max = round(calculated_arr * 0.40, 2)
        pipe_discount = 5.0
        pipe_upfront = round(pipe_max * ((100.0 - pipe_discount) / 100.0), 2)
        offers.append({
            "platform_id": "platform-pipe",
            "name": "Pipe",
            "max_eligible_advance": pipe_max,
            "discount_rate_pct": pipe_discount,
            "upfront_cash_payout": pipe_upfront,
            "trading_fee_amount": round(pipe_max - pipe_upfront, 2),
            "underwriting_source": "ARR Contract Quality",
            "equity_dilution_pct": 0.0,
            "non_dilutive_score": 99.0
        })

        # 3. Capchase
        cap_max = round(calculated_arr * 0.60, 2)
        cap_fee_pct = 6.5
        cap_fee_amt = round(cap_max * (cap_fee_pct / 100.0), 2)
        offers.append({
            "platform_id": "platform-capchase",
            "name": "Capchase Grow",
            "max_eligible_advance": cap_max,
            "flat_fee_pct": cap_fee_pct,
            "flat_fee_amount": cap_fee_amt,
            "total_repayable": round(cap_max + cap_fee_amt, 2),
            "monthly_repayment_est": round((cap_max + cap_fee_amt) / 12.0, 2),
            "underwriting_source": "Banking & Billing API (RevenueCat)",
            "equity_dilution_pct": 0.0,
            "non_dilutive_score": 97.0
        })

        # 4. Braavo
        braavo_max = round(calculated_arr * 0.50, 2)
        braavo_fee_pct = 4.5
        braavo_fee_amt = round(braavo_max * (braavo_fee_pct / 100.0), 2)
        offers.append({
            "platform_id": "platform-braavo",
            "name": "Braavo Capital",
            "max_eligible_advance": braavo_max,
            "products_available": ["Braavo Reserve", "Braavo Yield", "Braavo Accelerate"],
            "flat_fee_pct": braavo_fee_pct,
            "flat_fee_amount": braavo_fee_amt,
            "total_repayable": round(braavo_max + braavo_fee_amt, 2),
            "underwriting_source": "App Store Connect & Google Play Console",
            "equity_dilution_pct": 0.0,
            "non_dilutive_score": 99.5
        })

        # 5. Clearco
        clear_max = round(calculated_arr * 0.45, 2)
        clear_fee_pct = 8.0
        clear_fee_amt = round(clear_max * (clear_fee_pct / 100.0), 2)
        offers.append({
            "platform_id": "platform-clearco",
            "name": "Clearco (Clearbanc)",
            "max_eligible_advance": clear_max,
            "flat_fee_pct": clear_fee_pct,
            "flat_fee_amount": clear_fee_amt,
            "total_repayable": round(clear_max + clear_fee_amt, 2),
            "daily_withholding_rate_pct": 7.5,
            "underwriting_source": "UA Performance & Ad Analytics",
            "equity_dilution_pct": 0.0,
            "non_dilutive_score": 96.5
        })

        total_capital_capacity = sum(o["max_eligible_advance"] for o in offers)

        return {
            "status": "success",
            "timestamp": get_utc_timestamp_str(),
            "input_mrr": mrr,
            "calculated_arr": calculated_arr,
            "store_platform": store_platform,
            "total_non_dilutive_capital_capacity": total_capital_capacity,
            "offers_count": len(offers),
            "capital_offers": offers
        }


# Singleton Engine Instance
grants_and_capital_engine = SovereignGrantsAndAppCapitalEngine()
