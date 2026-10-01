"""
Tax classification of expenses.

QuickBooks lets you tag an expense with a category; it does not tell you how
much of it the IRS lets you deduct. This module does: every transaction gets
a tax class with a deductible percentage, the Internal Revenue Code section
behind it, and, when the answer depends on facts only the owner knows (who
was at the dinner?), a question for the approval card.

Rules reflect federal law for tax years 2026 onward unless noted. Meals with
clients or employees are 50% (IRC 274(n)(1)); company-wide recreational or
social events are 100% (IRC 274(e)(4), 274(n)(2)(A)); entertainment is 0%
(IRC 274(a)); meals furnished for the employer's convenience and on-premises
eating facilities are 0% from 2026 (IRC 274(o)); business gifts are capped
at $25 per recipient per year (IRC 274(b)). These are estimates for a tax
professional to confirm, not advice.
"""

from __future__ import annotations

import json
import re
import uuid
from dataclasses import asdict, dataclass, field
from datetime import date
from typing import Any, Dict, Iterable, List, Optional

from .db import db_session, init_db

TAX_SCHEMA = """
CREATE TABLE IF NOT EXISTS tax_classifications (
    id TEXT PRIMARY KEY,
    business_id TEXT NOT NULL,
    transaction_id TEXT NOT NULL UNIQUE,
    tax_class TEXT NOT NULL,
    deductible_pct REAL NOT NULL,
    amount REAL NOT NULL,
    deductible_amount REAL NOT NULL,
    confidence INTEGER NOT NULL DEFAULT 0,
    reason TEXT,
    irc_reference TEXT,
    question TEXT,
    context_json TEXT NOT NULL DEFAULT '{}',
    needs_review INTEGER NOT NULL DEFAULT 0,
    tax_year INTEGER,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_tax_class_business ON tax_classifications(business_id, tax_year);
"""


@dataclass(frozen=True)
class TaxClass:
    code: str
    label: str
    deductible_pct: float
    irc_reference: str
    form_line: str
    notes: str
    qre_candidate: bool = False  # counts toward Section 41 qualified research expenses


# The rulebook. Percentages are the federal deductible share of the expense.
TAX_CLASSES: Dict[str, TaxClass] = {
    tc.code: tc
    for tc in [
        TaxClass("MEAL_BUSINESS_50", "Business meal (client or employee present)", 0.50, "IRC 274(n)(1), 274(k)", "Schedule C line 24b / Form 1120 line 26",
                 "Food or drink with a client, prospect, or employee where business is discussed; not lavish; taxpayer present."),
        TaxClass("MEAL_COMPANY_EVENT_100", "Company-wide event (party, offsite, picnic)", 1.00, "IRC 274(e)(4), 274(n)(2)(A)", "Schedule C line 24b / Form 1120 line 26",
                 "Recreational or social activity primarily for employees who are not highly compensated: holiday party, team offsite, picnic. Fully deductible."),
        TaxClass("MEAL_TRAVEL_50", "Meal while traveling for business", 0.50, "IRC 274(n)(1), 162(a)(2)", "Schedule C line 24b",
                 "Meals away from the tax home overnight. 50% of actual cost or the federal per diem."),
        TaxClass("MEAL_EMPLOYER_CONVENIENCE_0", "Meals furnished for the employer's convenience", 0.00, "IRC 274(o) (tax years after 2025)", "Not deductible",
                 "Office lunches, snacks, and on-premises cafeterias became nondeductible for tax years beginning after December 31, 2025."),
        TaxClass("MEAL_SOLO_0", "Solo meal, not traveling", 0.00, "IRC 262", "Not deductible",
                 "A meal by yourself in town is a personal expense."),
        TaxClass("ENTERTAINMENT_0", "Entertainment (tickets, golf, club dues)", 0.00, "IRC 274(a)", "Not deductible",
                 "No deduction for entertainment, amusement, or recreation since 2018. Food bought separately at the event can still be a 50% meal."),
        TaxClass("TRAVEL_100", "Travel: airfare, rail, rideshare, car rental", 1.00, "IRC 162(a)(2)", "Schedule C line 24a",
                 "Transportation for business away from home, and local transportation between work locations. Commuting is not deductible."),
        TaxClass("LODGING_100", "Lodging while traveling", 1.00, "IRC 162(a)(2)", "Schedule C line 24a",
                 "Hotel or short-term rental on an overnight business trip."),
        TaxClass("VEHICLE_MILEAGE", "Vehicle: fuel, parking, tolls", 1.00, "IRC 162, 274(d); Rev. Proc. standard mileage", "Schedule C line 9",
                 "Deduct actual business-use share or the standard mileage rate. Keep a mileage log; commuting miles are personal."),
        TaxClass("GIFT_25_CAP", "Business gift", 1.00, "IRC 274(b)", "Schedule C line 27a",
                 "Deductible up to $25 per recipient per year. The excess is not deductible."),
        TaxClass("SOFTWARE_100", "Software and subscriptions", 1.00, "IRC 162; Rev. Proc. 2000-50", "Schedule C line 18 / 27a",
                 "Off-the-shelf software and SaaS subscriptions are currently deductible."),
        TaxClass("CLOUD_100", "Cloud hosting and compute", 1.00, "IRC 162; IRC 41(b)(2)(A)(iii) for research use", "Schedule C line 27a", 
                 "Fully deductible. Compute used for development can also count as a qualified research expense.", qre_candidate=True),
        TaxClass("ADVERTISING_100", "Advertising and marketing", 1.00, "IRC 162; Reg. 1.162-1(a)", "Schedule C line 8",
                 "Ads, sponsorships, promotional materials."),
        TaxClass("UTILITIES_100", "Utilities and telecom", 1.00, "IRC 162", "Schedule C line 25",
                 "Internet, phone, power for the business. Home-office share only if a home office qualifies."),
        TaxClass("OFFICE_SUPPLIES_100", "Office supplies", 1.00, "IRC 162", "Schedule C line 18",
                 "Consumables used within the year."),
        TaxClass("EQUIPMENT_DE_MINIMIS", "Equipment expensed under the de minimis safe harbor", 1.00, "Reg. 1.263(a)-1(f)", "Schedule C line 22 / 27a",
                 "Items costing $2,500 or less per invoice or item can be expensed in the year of purchase with an annual election statement."),
        TaxClass("EQUIPMENT_179", "Equipment: capitalize, Section 179 or bonus depreciation", 1.00, "IRC 179, 168(k)", "Form 4562",
                 "Over $2,500. Elect Section 179 to expense in year one (subject to annual limits and taxable income) or depreciate."),
        TaxClass("PROFESSIONAL_SERVICES_100", "Legal, accounting, consulting", 1.00, "IRC 162", "Schedule C line 17",
                 "Fees for services to the business."),
        TaxClass("INSURANCE_100", "Business insurance", 1.00, "IRC 162", "Schedule C line 15",
                 "Liability, E&O, cyber, property. Owner life insurance is not deductible."),
        TaxClass("RENT_100", "Rent and coworking", 1.00, "IRC 162(a)(3)", "Schedule C line 20b",
                 "Office rent, coworking memberships."),
        TaxClass("PAYROLL_100", "Wages and payroll", 1.00, "IRC 162(a)(1); IRC 41(b)(2)(A)(i) for research wages", "Schedule C line 26 / Form 1120 line 13",
                 "Deductible compensation. Engineering wages for development work count toward the research credit.", qre_candidate=True),
        TaxClass("CONTRACTOR_100", "Contractors (1099)", 1.00, "IRC 162; IRC 41(b)(3) at 65% for research", "Schedule C line 11",
                 "Payments to independent contractors. Research contractors count at 65% toward QRE.", qre_candidate=True),
        TaxClass("EDUCATION_100", "Training, courses, conferences", 1.00, "Reg. 1.162-5", "Schedule C line 27a",
                 "Education that maintains or improves skills in the current business."),
        TaxClass("COGS_100", "Cost of goods sold", 1.00, "IRC 471; IRC 263A exceptions for small business", "Schedule C Part III",
                 "Inventory and direct costs of products sold."),
        TaxClass("BANK_FEES_100", "Bank, payment processing, and interest", 1.00, "IRC 162, 163", "Schedule C line 16b / 27a",
                 "Processing fees, bank charges, business interest (small businesses are exempt from the 163(j) limit)."),
        TaxClass("TAXES_LICENSES_100", "Taxes and licenses", 1.00, "IRC 164", "Schedule C line 23",
                 "State and local business taxes, licenses, permits. Federal income tax is not deductible."),
        TaxClass("CHARITY_FLOWTHROUGH", "Charitable contribution", 0.00, "IRC 170", "Owner's return (Schedule A) or Form 1120 line 19",
                 "Not a Schedule C business expense; flows to the owner. C corporations deduct up to 10% of taxable income."),
        TaxClass("FINES_0", "Fines and penalties", 0.00, "IRC 162(f)", "Not deductible",
                 "Government fines and penalties are never deductible."),
        TaxClass("POLITICAL_0", "Political and lobbying", 0.00, "IRC 162(e)", "Not deductible", "Contributions and most lobbying are not deductible."),
        TaxClass("PERSONAL_0", "Personal", 0.00, "IRC 262", "Not deductible", "Personal, living, or family expense paid from the business account."),
        TaxClass("INCOME", "Income (not an expense)", 0.00, "IRC 61", "Schedule C Part I", "Revenue; not subject to deduction rules."),
        TaxClass("TRANSFER", "Transfer or owner draw", 0.00, "n/a", "Balance sheet", "Moves money; not income and not an expense."),
        TaxClass("UNCLASSIFIED", "Needs review", 0.00, "n/a", "Pending", "Not enough information. The deduction is lost if it stays unclassified."),
    ]
}

# Attendee answers for the meal question and the class they resolve to.
MEAL_ANSWERS: Dict[str, Dict[str, str]] = {
    "client": {"label": "Client or prospect was there", "tax_class": "MEAL_BUSINESS_50"},
    "employee": {"label": "One or a few employees", "tax_class": "MEAL_BUSINESS_50"},
    "all_employees": {"label": "Whole company event", "tax_class": "MEAL_COMPANY_EVENT_100"},
    "traveling": {"label": "I was traveling for work", "tax_class": "MEAL_TRAVEL_50"},
    "office_provided": {"label": "Food for the office", "tax_class": "MEAL_EMPLOYER_CONVENIENCE_0"},
    "solo": {"label": "Just me, in town", "tax_class": "MEAL_SOLO_0"},
    "personal": {"label": "Personal", "tax_class": "PERSONAL_0"},
}

MEAL_QUESTION = "Who was this meal with?"

# Merchant keyword rules, checked in order. (pattern, tax class, confidence, needs meal question)
_MERCHANT_RULES: List[tuple] = [
    (r"\b(parking ticket|citation|penalty|late fee|irs penalty)\b", "FINES_0", 90, False),
    (r"\b(actblue|winred|campaign|pac\b|lobby)", "POLITICAL_0", 80, False),
    (r"\b(aws|amazon web services|google cloud|gcp|azure|vercel|cloudflare|digitalocean|heroku|supabase|render\.com|netlify|fly\.io|linode|hetzner|railway)\b", "CLOUD_100", 92, False),
    (r"\b(github|notion|slack|figma|adobe|microsoft 365|google workspace|zoom|atlassian|jira|jetbrains|openai|anthropic|hubspot|salesforce|intuit|quickbooks|dropbox|1password|canva|loom|calendly|zapier|twilio|sendgrid|mailchimp|linear|asana|airtable|revenuecat)\b", "SOFTWARE_100", 90, False),
    (r"\b(google ads|meta ads|facebook ads|linkedin ads|twitter ads|x ads|tiktok ads|apple search ads|adroll|taboola|outbrain|sponsor)", "ADVERTISING_100", 90, False),
    (r"\b(gusto|adp|rippling|justworks|paychex|deel|remote\.com|trinet|zenefits|payroll)\b", "PAYROLL_100", 90, False),
    (r"\b(upwork|fiverr|toptal|contractor|freelance|1099)\b", "CONTRACTOR_100", 80, False),
    (r"\b(united airlines|delta|american airlines|southwest|jetblue|alaska air|spirit|frontier|amtrak|hertz|avis|enterprise rent|budget rent|uber(?! eats)|lyft|taxi)\b", "TRAVEL_100", 85, False),
    (r"\b(marriott|hilton|hyatt|airbnb|vrbo|hotel|motel|inn\b|resort|holiday inn|best western)", "LODGING_100", 85, False),
    (r"\b(shell|chevron|exxon|mobil|bp\b|arco|76\b|sunoco|wawa|speedway|parking|toll|ez pass|fastrak)\b", "VEHICLE_MILEAGE", 75, False),
    (r"\b(ticketmaster|stubhub|topgolf|golf|theater|theatre|cinema|amc\b|concert|stadium|arena|club dues|country club)\b", "ENTERTAINMENT_0", 85, False),
    (r"\b(gift|edible arrangements|1-800-flowers|harry & david)\b", "GIFT_25_CAP", 75, False),
    (r"\b(udemy|coursera|pluralsight|o'reilly|oreilly|conference|summit|workshop|masterclass|linkedin learning)\b", "EDUCATION_100", 80, False),
    (r"\b(wework|regus|industrious|coworking|rent\b|lease)\b", "RENT_100", 80, False),
    (r"\b(hiscox|next insurance|embroker|vouch|state farm|geico|progressive|hartford|insurance)\b", "INSURANCE_100", 85, False),
    (r"\b(law|legal|attorney|cpa|accounting|accountant|bookkeep|consult|advisory)\b", "PROFESSIONAL_SERVICES_100", 75, False),
    (r"\b(comcast|xfinity|verizon|at&t|t-mobile|spectrum|pg&e|con edison|duke energy|utility|electric|water bill)\b", "UTILITIES_100", 85, False),
    (r"\b(stripe fee|stripe|square fee|paypal fee|wire fee|bank fee|interest charge|monthly service fee)\b", "BANK_FEES_100", 80, False),
    (r"\b(franchise tax|state tax|business license|permit|dept of revenue|secretary of state)\b", "TAXES_LICENSES_100", 85, False),
    (r"\b(red cross|unicef|donation|charity|foundation|nonprofit|goodwill)\b", "CHARITY_FLOWTHROUGH", 75, False),
    (r"\b(staples|office depot|officemax|office supplies)\b", "OFFICE_SUPPLIES_100", 80, False),
    (r"\b(apple store|apple\.com|best buy|dell|lenovo|b&h|micro center|newegg|hardware)\b", "EQUIPMENT", 70, False),
    (r"\b(restaurant|grill|cafe|café|coffee|starbucks|dunkin|doordash|uber eats|grubhub|postmates|pizza|sushi|steakhouse|taqueria|bistro|kitchen|diner|chipotle|sweetgreen|panera|bar & grill|brewery|bakery|deli|burger|ramen|thai|tavern|eatery|catering|caterer)\b", "MEAL", 70, True),
]

_CATEGORY_DEFAULTS: Dict[str, str] = {
    "Sales Income": "INCOME",
    "Other Income": "INCOME",
    "Cloud Hosting": "CLOUD_100",
    "Office & Software": "SOFTWARE_100",
    "Travel & Meals": "MEAL",  # resolved by merchant or question
    "Marketing": "ADVERTISING_100",
    "Utilities": "UTILITIES_100",
    "Cost of Goods Sold": "COGS_100",
    "Uncategorized Expense": "UNCLASSIFIED",
}

DE_MINIMIS_LIMIT = 2500.0


@dataclass
class Classification:
    transaction_id: str
    tax_class: str
    label: str
    deductible_pct: float
    amount: float
    deductible_amount: float
    confidence: int
    reason: str
    irc_reference: str
    form_line: str
    question: Optional[str] = None
    answers: Optional[List[Dict[str, str]]] = None
    needs_review: bool = False
    qre_candidate: bool = False
    tax_year: Optional[int] = None
    context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _tax_year(date_str: Optional[str]) -> int:
    try:
        return int(str(date_str)[:4])
    except (TypeError, ValueError):
        return date.today().year


def _resolve_meal(context: Dict[str, Any], year: int) -> Optional[str]:
    attendees = (context.get("attendees") or "").lower()
    if attendees in MEAL_ANSWERS:
        code = MEAL_ANSWERS[attendees]["tax_class"]
        # Before 2026 employer-provided meals were still 50%.
        if code == "MEAL_EMPLOYER_CONVENIENCE_0" and year < 2026:
            return "MEAL_BUSINESS_50"
        return code
    if context.get("traveling"):
        return "MEAL_TRAVEL_50"
    return None


def classify(
    name: str,
    merchant: Optional[str],
    amount: float,
    category: Optional[str],
    txn_date: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
    transaction_id: str = "",
) -> Classification:
    """Pure function: returns the tax classification for one transaction."""
    context = dict(context or {})
    year = _tax_year(txn_date)
    text = f"{merchant or ''} {name or ''}".lower()
    spend = abs(float(amount or 0.0))
    is_income = float(amount or 0.0) < 0  # Plaid: negative = money in

    # An explicit answer from the owner always wins.
    override = (context.get("tax_class") or "").upper()
    if override in TAX_CLASSES:
        tc = TAX_CLASSES[override]
        return _build(transaction_id, tc, spend, 100, "Set by owner", year, context)

    if is_income or (category in ("Sales Income", "Other Income")):
        return _build(transaction_id, TAX_CLASSES["INCOME"], spend, 95, "Money in; income is not an expense", year, context)
    if re.search(r"\b(transfer|owner draw|distribution|capital contribution)\b", text):
        return _build(transaction_id, TAX_CLASSES["TRANSFER"], spend, 85, "Transfer between accounts", year, context)

    code: Optional[str] = None
    confidence = 0
    reason = ""
    for pattern, cls, conf, _ in _MERCHANT_RULES:
        if re.search(pattern, text):
            code, confidence, reason = cls, conf, f"Merchant matches {TAX_CLASSES.get(cls, TaxClass(cls, cls, 0, '', '', '')).label.lower() if cls in TAX_CLASSES else cls.lower()} rule"
            break

    if code is None and category in _CATEGORY_DEFAULTS:
        code = _CATEGORY_DEFAULTS[category]
        confidence = 60
        reason = f"Category '{category}'"

    if code == "EQUIPMENT":
        code = "EQUIPMENT_DE_MINIMIS" if spend <= DE_MINIMIS_LIMIT else "EQUIPMENT_179"
        reason = f"Equipment purchase of {spend:,.2f}; {'at or under' if spend <= DE_MINIMIS_LIMIT else 'over'} the {DE_MINIMIS_LIMIT:,.0f} de minimis limit"

    if code == "MEAL":
        resolved = _resolve_meal(context, year)
        if resolved:
            return _build(transaction_id, TAX_CLASSES[resolved], spend, 95, f"Owner answered: {MEAL_ANSWERS.get(context.get('attendees', ''), {}).get('label', 'traveling')}", year, context)
        # Travel & Meals category with a non-restaurant merchant is probably travel.
        if category == "Travel & Meals" and not any(re.search(p, text) for p, c, _, q in _MERCHANT_RULES if q):
            return _build(transaction_id, TAX_CLASSES["TRAVEL_100"], spend, 55, "Travel category without a restaurant merchant", year, context, needs_review=True)
        provisional = TAX_CLASSES["MEAL_BUSINESS_50"]
        c = _build(transaction_id, provisional, spend, max(confidence, 50), "Looks like a meal; the deductible share depends on who attended", year, context, needs_review=True)
        c.question = MEAL_QUESTION
        c.answers = [{"id": k, "label": v["label"], "deductible_pct": TAX_CLASSES[v["tax_class"]].deductible_pct} for k, v in MEAL_ANSWERS.items()]
        return c

    if code is None or code not in TAX_CLASSES:
        return _build(transaction_id, TAX_CLASSES["UNCLASSIFIED"], spend, 0, "No rule matched; needs a category", year, context, needs_review=True)

    tc = TAX_CLASSES[code]
    cls = _build(transaction_id, tc, spend, confidence, reason, year, context)
    if code == "GIFT_25_CAP":
        recipients = max(1, int(context.get("recipients") or 1))
        cap = 25.0 * recipients
        cls.deductible_amount = round(min(spend, cap), 2)
        cls.deductible_pct = round(cls.deductible_amount / spend, 4) if spend else 0.0
        cls.reason = f"Gift capped at $25 per recipient ({recipients})"
    return cls


def _build(txn_id: str, tc: TaxClass, spend: float, confidence: int, reason: str, year: int, context: Dict[str, Any], needs_review: bool = False) -> Classification:
    return Classification(
        transaction_id=txn_id,
        tax_class=tc.code,
        label=tc.label,
        deductible_pct=tc.deductible_pct,
        amount=round(spend, 2),
        deductible_amount=round(spend * tc.deductible_pct, 2),
        confidence=int(confidence),
        reason=reason,
        irc_reference=tc.irc_reference,
        form_line=tc.form_line,
        needs_review=needs_review or tc.code == "UNCLASSIFIED",
        qre_candidate=tc.qre_candidate,
        tax_year=year,
        context=context,
    )


def rulebook() -> Dict[str, Any]:
    return {
        "classes": [asdict(tc) for tc in TAX_CLASSES.values()],
        "meal_question": MEAL_QUESTION,
        "meal_answers": [{"id": k, **v, "deductible_pct": TAX_CLASSES[v["tax_class"]].deductible_pct} for k, v in MEAL_ANSWERS.items()],
        "de_minimis_limit": DE_MINIMIS_LIMIT,
        "status": "OK",
    }


class TaxClassifier:
    """Persists classifications for a business's transactions."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path
        init_db(db_path)
        with db_session(db_path) as conn:
            conn.executescript(TAX_SCHEMA)

    # --- persistence --------------------------------------------------------

    def save(self, business_id: str, c: Classification) -> Dict[str, Any]:
        with db_session(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO tax_classifications
                    (id, business_id, transaction_id, tax_class, deductible_pct, amount, deductible_amount,
                     confidence, reason, irc_reference, question, context_json, needs_review, tax_year)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(transaction_id) DO UPDATE SET
                    tax_class=excluded.tax_class, deductible_pct=excluded.deductible_pct,
                    amount=excluded.amount, deductible_amount=excluded.deductible_amount,
                    confidence=excluded.confidence, reason=excluded.reason,
                    irc_reference=excluded.irc_reference, question=excluded.question,
                    context_json=excluded.context_json, needs_review=excluded.needs_review,
                    tax_year=excluded.tax_year, updated_at=datetime('now')
                """,
                (
                    f"tax_{uuid.uuid4().hex[:12]}", business_id, c.transaction_id, c.tax_class, c.deductible_pct,
                    c.amount, c.deductible_amount, c.confidence, c.reason, c.irc_reference, c.question,
                    json.dumps(c.context), 1 if c.needs_review else 0, c.tax_year,
                ),
            )
        return {**c.to_dict(), "business_id": business_id, "status": "OK"}

    def _txn(self, conn, business_id: str, txn_id: str):
        return conn.execute(
            "SELECT id, date, name, merchant_name, amount, category_confirmed, category_suggested FROM transactions WHERE id = ? AND business_id = ?",
            (txn_id, business_id),
        ).fetchone()

    def classify_transaction(self, business_id: str, txn_id: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        with db_session(self.db_path) as conn:
            row = self._txn(conn, business_id, txn_id)
        if not row:
            return {"status": "ERROR", "error": "Transaction not found"}
        c = classify(
            name=row["name"], merchant=row["merchant_name"], amount=row["amount"],
            category=row["category_confirmed"] or row["category_suggested"],
            txn_date=row["date"], context=context, transaction_id=row["id"],
        )
        return self.save(business_id, c)

    def classify_all(self, business_id: str, only_missing: bool = True) -> Dict[str, Any]:
        with db_session(self.db_path) as conn:
            rows = conn.execute(
                "SELECT id, date, name, merchant_name, amount, category_confirmed, category_suggested FROM transactions WHERE business_id = ?",
                (business_id,),
            ).fetchall()
            existing = {r["transaction_id"]: json.loads(r["context_json"] or "{}") for r in conn.execute(
                "SELECT transaction_id, context_json FROM tax_classifications WHERE business_id = ?", (business_id,)
            ).fetchall()}
        done = 0
        questions = 0
        for r in rows:
            if only_missing and r["id"] in existing and existing[r["id"]]:
                continue  # keep answered ones
            c = classify(r["name"], r["merchant_name"], r["amount"], r["category_confirmed"] or r["category_suggested"], r["date"], existing.get(r["id"]), r["id"])
            self.save(business_id, c)
            done += 1
            if c.question:
                questions += 1
        return {"business_id": business_id, "classified": done, "open_questions": questions, "status": "OK"}

    def list(self, business_id: str, limit: int = 100, needs_review: Optional[bool] = None) -> Dict[str, Any]:
        sql = """
            SELECT t.transaction_id, t.tax_class, t.deductible_pct, t.amount, t.deductible_amount, t.confidence,
                   t.reason, t.irc_reference, t.question, t.needs_review, t.tax_year, t.context_json,
                   x.date, x.name, x.merchant_name, x.status AS txn_status
            FROM tax_classifications t JOIN transactions x ON x.id = t.transaction_id
            WHERE t.business_id = ?
        """
        args: List[Any] = [business_id]
        if needs_review is not None:
            sql += " AND t.needs_review = ?"
            args.append(1 if needs_review else 0)
        sql += " ORDER BY x.date DESC LIMIT ?"
        args.append(int(limit))
        with db_session(self.db_path) as conn:
            rows = [dict(r) for r in conn.execute(sql, args).fetchall()]
        for r in rows:
            r["label"] = TAX_CLASSES.get(r["tax_class"], TAX_CLASSES["UNCLASSIFIED"]).label
            r["context"] = json.loads(r.pop("context_json") or "{}")
            r["needs_review"] = bool(r["needs_review"])
        return {"business_id": business_id, "classifications": rows, "count": len(rows), "status": "OK"}

    def questions(self, business_id: str, limit: int = 20) -> Dict[str, Any]:
        """Open questions for the approval cards (meals that need an attendee answer)."""
        res = self.list(business_id, limit=limit * 3, needs_review=True)
        items = []
        for r in res["classifications"]:
            if r.get("question"):
                items.append({
                    "transaction_id": r["transaction_id"],
                    "question": r["question"],
                    "answers": rulebook()["meal_answers"],
                    "merchant": r["merchant_name"] or r["name"],
                    "date": r["date"],
                    "amount": r["amount"],
                    "current_class": r["tax_class"],
                    "current_deductible_pct": r["deductible_pct"],
                })
            if len(items) >= limit:
                break
        return {"business_id": business_id, "questions": items, "count": len(items), "status": "OK"}

    def summary(self, business_id: str, tax_year: Optional[int] = None) -> Dict[str, Any]:
        year = tax_year or date.today().year
        with db_session(self.db_path) as conn:
            rows = conn.execute(
                """
                SELECT tax_class, COUNT(*) AS n, SUM(amount) AS spent, SUM(deductible_amount) AS deductible,
                       SUM(needs_review) AS open_items
                FROM tax_classifications WHERE business_id = ? AND tax_year = ?
                GROUP BY tax_class
                """,
                (business_id, year),
            ).fetchall()
        by_class = []
        spent = deductible = lost = 0.0
        open_items = 0
        qre = 0.0
        for r in rows:
            tc = TAX_CLASSES.get(r["tax_class"], TAX_CLASSES["UNCLASSIFIED"])
            if tc.code in ("INCOME", "TRANSFER"):
                continue
            s, d = float(r["spent"] or 0), float(r["deductible"] or 0)
            spent += s
            deductible += d
            lost += s - d
            open_items += int(r["open_items"] or 0)
            if tc.qre_candidate:
                qre += s
            by_class.append({
                "tax_class": tc.code, "label": tc.label, "deductible_pct": tc.deductible_pct, "count": int(r["n"]),
                "spent": round(s, 2), "deductible": round(d, 2), "nondeductible": round(s - d, 2),
                "irc_reference": tc.irc_reference, "form_line": tc.form_line,
            })
        by_class.sort(key=lambda x: -x["spent"])
        return {
            "business_id": business_id,
            "tax_year": year,
            "total_spent": round(spent, 2),
            "total_deductible": round(deductible, 2),
            "total_nondeductible": round(lost, 2),
            "open_questions": open_items,
            "qre_candidate_spend": round(qre, 2),
            "by_class": by_class,
            "status": "OK",
        }
