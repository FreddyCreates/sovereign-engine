"""
Sovereign Books chat — real answers from ledger/inbox/grants.

Uses an offline script engine by default. If GEMINI_API_KEY or OPENAI_API_KEY
is set, optionally enhances the reply (still grounded in tool results).
"""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional

from .bank_service import BankService, CATEGORY_TO_ACCOUNT
from .grants import list_grants


class BooksChatEngine:
    def __init__(self, bank: Optional[BankService] = None):
        self.bank = bank or BankService()

    def reply(self, message: str, business_id: Optional[str] = None) -> Dict[str, Any]:
        msg = (message or "").strip()
        lower = msg.lower()
        artifacts: List[Dict[str, Any]] = []
        tools_used: List[str] = []

        home = self.bank.home_snapshot(business_id)
        tools_used.append("home_snapshot")
        bid = home["business_id"]

        if any(w in lower for w in ("grant", "capital", "non-dilutive", "funding")):
            grants = list_grants()
            tools_used.append("list_grants")
            top = grants["grants"][:3]
            for g in top:
                artifacts.append(
                    {
                        "kind": "grant",
                        "title": g["title"],
                        "subtitle": g.get("amount"),
                        "payload": g,
                    }
                )
            reply = (
                f"Found {grants['count']} grants in the catalog. "
                f"Top fits: " + ", ".join(g["title"] for g in top) + ". "
                "Open Artifacts to preview details."
            )
            engine = "script"
        elif any(w in lower for w in ("inbox", "review", "uncategor")):
            inbox = self.bank.list_inbox(bid, limit=10)
            tools_used.append("list_inbox")
            rows = [
                {"name": t["name"], "amount": t["amount"], "date": t["date"]}
                for t in inbox["transactions"]
            ]
            artifacts.append(
                {
                    "kind": "transactions",
                    "title": "Review inbox",
                    "subtitle": f"{inbox['count']} items",
                    "payload": {"rows": rows},
                }
            )
            reply = (
                f"You have {inbox['count']} transactions waiting. "
                f"Cash on hand is ${home['cash_balance']:,.2f}. "
                "Confirm categories in Books to lock the ledger."
            )
            engine = "script"
        elif any(w in lower for w in ("cash", "runway", "balance", "chart", "dashboard")):
            series = self.bank.cash_series(bid)
            tools_used.append("cash_series")
            artifacts.append(
                {
                    "kind": "chart",
                    "title": "Cash trajectory",
                    "subtitle": "From linked transactions",
                    "payload": {"data": series["points"]},
                }
            )
            reply = (
                f"Cash on hand: ${home['cash_balance']:,.2f}. "
                f"Bank {'connected' if home['bank_connected'] else 'not connected'}. "
                f"Inbox: {home['inbox_count']}. "
                f"Ledger balanced: {home['trial_balance_ok']}."
            )
            engine = "script"
        elif any(w in lower for w in ("pro", "revenuecat", "entitle", "subscription")):
            from .revenuecat import RevenueCatService

            rc = RevenueCatService(self.bank.db_path)
            ent = rc.get_entitlements(app_user_id=os.environ.get("REVENUECAT_APP_USER_ID"))
            tools_used.append("revenuecat_entitlements")
            reply = (
                f"Pro active: {ent.get('pro_active')}. "
                f"Source: {ent.get('source')}. "
                f"Entitlements: {', '.join(ent.get('entitlements') or []) or 'none'}."
            )
            engine = "script"
        elif any(w in lower for w in ("categor", "coa", "account")):
            cats = ", ".join(CATEGORY_TO_ACCOUNT.keys())
            reply = f"Available categories: {cats}."
            engine = "script"
        else:
            reply = (
                f"{home['business_name']}: cash ${home['cash_balance']:,.2f}, "
                f"inbox {home['inbox_count']}, plaid mode {home['mode']}. "
                "Try: cash chart · inbox · grants · pro status."
            )
            engine = "script"

        # Optional LLM polish — only if key present; never invents numbers
        llm = self._maybe_llm_polish(msg, reply, home)
        if llm:
            reply = llm
            engine = "script+llm"

        return {
            "reply": reply,
            "engine": engine,
            "artifacts": artifacts,
            "tools_used": tools_used,
            "home": {
                "cash_balance": home["cash_balance"],
                "inbox_count": home["inbox_count"],
                "bank_connected": home["bank_connected"],
                "mode": home["mode"],
            },
            "status": "OK",
        }

    def _maybe_llm_polish(
        self, user_msg: str, grounded_reply: str, home: Dict[str, Any]
    ) -> Optional[str]:
        gemini_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        openai_key = os.environ.get("OPENAI_API_KEY")
        system = (
            "You are Sovereign Books assistant. Rewrite the grounded reply briefly. "
            "Do not invent numbers. Keep facts exactly as given."
        )
        context = json.dumps(
            {
                "user": user_msg,
                "grounded_reply": grounded_reply,
                "facts": {
                    "cash": home["cash_balance"],
                    "inbox": home["inbox_count"],
                    "connected": home["bank_connected"],
                },
            }
        )
        if gemini_key:
            try:
                return self._call_gemini(gemini_key, system, context)
            except Exception:
                return None
        if openai_key:
            try:
                return self._call_openai(openai_key, system, context)
            except Exception:
                return None
        return None

    def _call_gemini(self, api_key: str, system: str, context: str) -> str:
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"gemini-2.0-flash:generateContent?key={api_key}"
        )
        body = {
            "contents": [
                {
                    "parts": [
                        {"text": f"{system}\n\n{context}\n\nReturn only the reply text."}
                    ]
                }
            ]
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.load(resp)
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        return text.strip()

    def _call_openai(self, api_key: str, system: str, context: str) -> str:
        body = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": context},
            ],
            "temperature": 0.2,
        }
        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=json.dumps(body).encode(),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.load(resp)
        return data["choices"][0]["message"]["content"].strip()
