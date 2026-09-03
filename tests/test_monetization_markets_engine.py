import pytest
from monetization_markets.monetization_markets_engine import (
    FinancialCreditCardChatNode,
    AutonomousAIPurchasingEngine,
    MonetizationMarketsEngine
)

def test_financial_credit_card_chat_node():
    node = FinancialCreditCardChatNode()
    res = node.answer_ledger_query("What credit card should I use for AWS cloud compute?")
    assert res["node"] == "FinancialCreditCardChatNode"
    assert len(res["recommended_business_offers"]) >= 1
    assert res["recommended_business_offers"][0]["category"] in ["BUSINESS_CREDIT_CARD", "BUSINESS_BANKING"]

def test_autonomous_ai_purchasing_engine():
    engine = AutonomousAIPurchasingEngine()
    res = engine.execute_autonomous_purchase(
        item_description="RunPod H100 GPU Compute 10 Hours",
        amount_usd=32.50,
        external_vendor="RunPod Inc",
        user_id="builder_101"
    )
    assert res["vendor"] == "RunPod Inc"
    assert res["amount_usd"] == 32.50
    assert "5412-" in res["virtual_card_used"]
    assert res["settlement_status"] == "SETTLED_IN_APP_LEDGER"

def test_monetization_markets_engine():
    mm = MonetizationMarketsEngine()
    res = mm.package_monetized_app("Sovereign Fitness Pro", "dev_404")
    assert res["app_name"] == "Sovereign Fitness Pro"
    assert res["revenuecat"]["sdk_version"] == "8.2.0"
    assert res["catvertising_ad_substrate"]["ecpm_target"] == 15.00
    assert res["autonomous_ai_purchasing"]["enabled"] is True
    assert res["status"] == "100_PERCENT_PRE_MONETIZED_OUT_OF_THE_BOX"
