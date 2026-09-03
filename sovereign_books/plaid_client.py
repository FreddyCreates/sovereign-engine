"""
Plaid bank connector for Sovereign Books.

Uses real Plaid sandbox when PLAID_CLIENT_ID + PLAID_SECRET are set.
Otherwise runs in mock mode so local MVP development works without keys.
"""

from __future__ import annotations

import os
import uuid
from datetime import date, timedelta
from typing import Any, Dict, List, Optional


def _plaid_configured() -> bool:
    return bool(os.environ.get("PLAID_CLIENT_ID") and os.environ.get("PLAID_SECRET"))


class PlaidClient:
    """Thin wrapper: real Plaid SDK or deterministic mock."""

    def __init__(self):
        self.mode = "live" if _plaid_configured() else "mock"
        self._client = None
        if self.mode == "live":
            self._client = self._build_live_client()

    def _build_live_client(self):
        try:
            import plaid
            from plaid.api import plaid_api
            from plaid.model.country_code import CountryCode
            from plaid.model.products import Products
        except ImportError as e:
            raise RuntimeError(
                "plaid-python is required for live mode. pip install plaid-python"
            ) from e

        env_name = os.environ.get("PLAID_ENV", "sandbox").lower()
        host = {
            "sandbox": plaid.Environment.Sandbox,
            "production": plaid.Environment.Production,
        }.get(env_name, plaid.Environment.Sandbox)

        configuration = plaid.Configuration(
            host=host,
            api_key={
                "clientId": os.environ["PLAID_CLIENT_ID"],
                "secret": os.environ["PLAID_SECRET"],
            },
        )
        api_client = plaid.ApiClient(configuration)
        self._Products = Products
        self._CountryCode = CountryCode
        return plaid_api.PlaidApi(api_client)

    def create_link_token(self, user_id: str) -> Dict[str, Any]:
        if self.mode == "mock":
            return {
                "link_token": f"link-sandbox-mock-{uuid.uuid4().hex[:12]}",
                "expiration": (date.today() + timedelta(days=1)).isoformat(),
                "mode": "mock",
            }

        from plaid.model.country_code import CountryCode
        from plaid.model.link_token_create_request import LinkTokenCreateRequest
        from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
        from plaid.model.products import Products

        products = [
            Products(p.strip())
            for p in os.environ.get("PLAID_PRODUCTS", "transactions").split(",")
            if p.strip()
        ]
        countries = [
            CountryCode(c.strip())
            for c in os.environ.get("PLAID_COUNTRY_CODES", "US").split(",")
            if c.strip()
        ]
        req = LinkTokenCreateRequest(
            products=products,
            client_name="Sovereign Books",
            country_codes=countries,
            language="en",
            user=LinkTokenCreateRequestUser(client_user_id=user_id),
        )
        res = self._client.link_token_create(req)
        return {
            "link_token": res["link_token"],
            "expiration": str(res.get("expiration", "")),
            "mode": "live",
        }

    def exchange_public_token(self, public_token: str) -> Dict[str, Any]:
        if self.mode == "mock":
            # public_token may encode institution for demo UX
            inst = "ins_mock_chase"
            name = "Chase (Mock)"
            if "amex" in public_token.lower():
                inst, name = "ins_mock_amex", "American Express (Mock)"
            elif "bofa" in public_token.lower() or "bank of america" in public_token.lower():
                inst, name = "ins_mock_bofa", "Bank of America (Mock)"
            return {
                "access_token": f"access-sandbox-mock-{uuid.uuid4().hex[:16]}",
                "item_id": f"item-mock-{uuid.uuid4().hex[:12]}",
                "institution_id": inst,
                "institution_name": name,
                "mode": "mock",
            }

        from plaid.model.item_public_token_exchange_request import (
            ItemPublicTokenExchangeRequest,
        )

        req = ItemPublicTokenExchangeRequest(public_token=public_token)
        res = self._client.item_public_token_exchange(req)
        access_token = res["access_token"]
        item_id = res["item_id"]
        institution_id = None
        institution_name = None
        try:
            from plaid.model.item_get_request import ItemGetRequest
            from plaid.model.institutions_get_by_id_request import InstitutionsGetByIdRequest
            from plaid.model.country_code import CountryCode

            item_res = self._client.item_get(ItemGetRequest(access_token=access_token))
            item = item_res["item"]
            institution_id = getattr(item, "institution_id", None) or (
                item.get("institution_id") if isinstance(item, dict) else None
            )
            if institution_id:
                inst_res = self._client.institutions_get_by_id(
                    InstitutionsGetByIdRequest(
                        institution_id=institution_id,
                        country_codes=[CountryCode("US")],
                    )
                )
                inst = inst_res["institution"]
                institution_name = getattr(inst, "name", None) or (
                    inst.get("name") if isinstance(inst, dict) else None
                )
        except Exception:
            pass
        return {
            "access_token": access_token,
            "item_id": item_id,
            "institution_id": institution_id,
            "institution_name": institution_name,
            "mode": "live",
        }

    def get_accounts(self, access_token: str) -> List[Dict[str, Any]]:
        if self.mode == "mock" or access_token.startswith("access-sandbox-mock-"):
            return [
                {
                    "account_id": f"acc_checking_{uuid.uuid4().hex[:8]}",
                    "name": "Business Checking",
                    "official_name": "Business Checking ****4521",
                    "mask": "4521",
                    "type": "depository",
                    "subtype": "checking",
                    "balances": {
                        "current": 24180.42,
                        "available": 23850.00,
                        "iso_currency_code": "USD",
                    },
                },
                {
                    "account_id": f"acc_card_{uuid.uuid4().hex[:8]}",
                    "name": "Business Credit Card",
                    "official_name": "Business Platinum ****8890",
                    "mask": "8890",
                    "type": "credit",
                    "subtype": "credit card",
                    "balances": {
                        "current": 1842.15,
                        "available": 8157.85,
                        "iso_currency_code": "USD",
                    },
                },
            ]

        from plaid.model.accounts_get_request import AccountsGetRequest

        res = self._client.accounts_get(AccountsGetRequest(access_token=access_token))
        accounts = []
        for a in res["accounts"]:
            if isinstance(a, dict):
                bal = a.get("balances") or {}
                accounts.append(
                    {
                        "account_id": a["account_id"],
                        "name": a.get("name") or "Account",
                        "official_name": a.get("official_name"),
                        "mask": a.get("mask"),
                        "type": str(a.get("type") or ""),
                        "subtype": str(a.get("subtype") or ""),
                        "balances": {
                            "current": float(bal.get("current") or 0),
                            "available": float(bal["available"]) if bal.get("available") is not None else None,
                            "iso_currency_code": bal.get("iso_currency_code") or "USD",
                        },
                    }
                )
            else:
                bal = a.balances
                accounts.append(
                    {
                        "account_id": a.account_id,
                        "name": a.name or "Account",
                        "official_name": a.official_name,
                        "mask": a.mask,
                        "type": str(a.type or ""),
                        "subtype": str(a.subtype or ""),
                        "balances": {
                            "current": float(bal.current or 0),
                            "available": float(bal.available) if bal.available is not None else None,
                            "iso_currency_code": bal.iso_currency_code or "USD",
                        },
                    }
                )
        return accounts

    def get_transactions(
        self,
        access_token: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[Dict[str, Any]]:
        end = end_date or date.today()
        start = start_date or (end - timedelta(days=30))

        if self.mode == "mock" or access_token.startswith("access-sandbox-mock-"):
            return self._mock_transactions(start, end)

        from plaid.model.transactions_get_request import TransactionsGetRequest
        from plaid.exceptions import ApiException
        import time as _time

        # Sandbox often needs a moment before PRODUCT_NOT_READY clears
        last_err = None
        for attempt in range(6):
            try:
                req = TransactionsGetRequest(
                    access_token=access_token,
                    start_date=start,
                    end_date=end,
                )
                res = self._client.transactions_get(req)
                out = []
                for t in res["transactions"]:
                    cats = getattr(t, "category", None) or (
                        t.get("category") if isinstance(t, dict) else None
                    )
                    out.append(
                        {
                            "transaction_id": t["transaction_id"] if isinstance(t, dict) else t.transaction_id,
                            "account_id": t["account_id"] if isinstance(t, dict) else t.account_id,
                            "date": str(t["date"] if isinstance(t, dict) else t.date),
                            "name": (t.get("name") if isinstance(t, dict) else t.name) or "Transaction",
                            "merchant_name": t.get("merchant_name") if isinstance(t, dict) else getattr(t, "merchant_name", None),
                            "amount": float(t["amount"] if isinstance(t, dict) else t.amount),
                            "pending": bool(t.get("pending") if isinstance(t, dict) else t.pending),
                            "category": (cats[0] if cats else None),
                        }
                    )
                return out
            except ApiException as e:
                last_err = e
                body = getattr(e, "body", "") or str(e)
                if "PRODUCT_NOT_READY" in body or "PRODUCT_NOT_READY" in str(e):
                    _time.sleep(1.5)
                    continue
                raise
        raise RuntimeError(f"Plaid transactions not ready after retries: {last_err}")

    def _mock_transactions(self, start: date, end: date) -> List[Dict[str, Any]]:
        """Deterministic sample feed matching QuickBooks-pain demo scenarios."""
        # Plaid amounts: positive = money out of account for depository
        samples = [
            ("AWS Web Services", "Amazon Web Services", 142.00, "Cloud Hosting", 2),
            ("Stripe Transfer", "Stripe", -890.00, "Sales Income", 3),
            ("Uber Trip", "Uber", 34.50, "Travel & Meals", 5),
            ("Google Workspace", "Google", 72.00, "Office & Software", 7),
            ("Shell Oil", "Shell", 68.20, "Travel & Meals", 8),
            ("Shopify Payout", "Shopify", -1250.00, "Sales Income", 10),
            ("Adobe Creative Cloud", "Adobe", 59.99, "Office & Software", 12),
            ("WeWork Invoice", "WeWork", 450.00, "Office & Software", 14),
            ("POS DEBIT 8472", None, 28.40, "Uncategorized Expense", 15),
            ("ACH PAYROLL", None, 4200.00, "Uncategorized Expense", 18),
            ("Customer Refund", None, 120.00, "Sales Income", 20),
            ("Verizon Wireless", "Verizon", 89.00, "Utilities", 22),
        ]
        txns = []
        for i, (name, merchant, amount, category, day_offset) in enumerate(samples):
            d = end - timedelta(days=day_offset)
            if d < start:
                continue
            txns.append(
                {
                    "transaction_id": f"txn_mock_{i:04d}_{d.isoformat()}",
                    "account_id": None,  # filled by bank_service with checking id
                    "date": d.isoformat(),
                    "name": name,
                    "merchant_name": merchant,
                    "amount": amount,
                    "pending": i == 0,
                    "category": category,
                    "_prefer_checking": amount < 0 or "AWS" in name or "Uber" in name or "Google" in name or "Shell" in name or "Adobe" in name or "WeWork" in name or "POS" in name or "PAYROLL" in name or "Verizon" in name or "Refund" in name or "Shopify" in name or "Stripe" in name,
                }
            )
        return txns
