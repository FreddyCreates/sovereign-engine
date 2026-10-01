"""
Tax opportunity advisor: "you should go do this".

Reads the deductibility summary from the tax classifier and the research
credit estimate from the agentic QuickBooks engine, then ranks the
credits and deductions the business is closest to and says exactly what
to do next. Each opportunity carries the Code section behind it, a
status (qualified, close, or not_yet), an estimated value, and the
action that moves it to qualified.

Dollar limits are the federal figures for the 2025 and 2026 tax years as
published by the IRS; a tax professional confirms them at filing.
"""

from __future__ import annotations

import os
import sys
from datetime import date
from typing import Any, Dict, List, Optional

from .bank_service import BankService
from .tax_classifier import TAX_CLASSES, TaxClassifier

# Assumed marginal rate for turning deductions into dollars saved. Overridable per call.
DEFAULT_MARGINAL_RATE = 0.24
SECTION_179_LIMIT = 1_250_000.0      # 2025 limit, indexed annually
DE_MINIMIS_LIMIT = 2_500.0
RETIREMENT_STARTUP_CREDIT_MAX = 5_000.0   # IRC 45E, per year for 3 years
AUTO_ENROLL_CREDIT = 500.0                # IRC 45T, per year for 3 years
WOTC_MIN, WOTC_MAX = 2_400.0, 9_600.0     # IRC 51, per qualifying hire
HOME_OFFICE_SIMPLIFIED_MAX = 1_500.0      # $5 x 300 sq ft
STANDARD_MILEAGE_RATE = 0.70              # 2025 rate; confirm the current-year figure


def _research_engine():
    """The Section 41 research estimate lives in the nextgen engine; import it lazily."""
    try:
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        nextgen = os.path.join(root, "sovereign_infrastructure", "nextgen_systems")
        for p in (root, nextgen):
            if p not in sys.path:
                sys.path.insert(0, p)
        from agentic_quickbooks_engine import AgenticQuickBooksEngine  # type: ignore

        return AgenticQuickBooksEngine()
    except Exception:  # pragma: no cover - engine optional
        return None


class TaxAdvisor:
    def __init__(self, db_path: Optional[str] = None, classifier: Optional[TaxClassifier] = None):
        self.db_path = db_path
        self.classifier = classifier or TaxClassifier(db_path)
        self.bank = BankService(db_path) if db_path else BankService()

    def _business(self, business_id: Optional[str]) -> str:
        return business_id or self.bank.ensure_demo_workspace()["business_id"]

    def opportunities(
        self,
        business_id: Optional[str] = None,
        state: str = "CA",
        tax_year: Optional[int] = None,
        marginal_rate: float = DEFAULT_MARGINAL_RATE,
        employees: Optional[int] = None,
    ) -> Dict[str, Any]:
        bid = self._business(business_id)
        year = tax_year or date.today().year
        summary = self.classifier.summary(bid, year)
        by_class = {c["tax_class"]: c for c in summary["by_class"]}
        spent = lambda code: float(by_class.get(code, {}).get("spent", 0.0))  # noqa: E731
        rate = float(marginal_rate)
        days_left = (date(year, 12, 31) - date.today()).days if year == date.today().year else 0

        opps: List[Dict[str, Any]] = []

        # 1. Company-wide events are 100%; business meals are 50%.
        meals50 = spent("MEAL_BUSINESS_50") + spent("MEAL_TRAVEL_50")
        events = spent("MEAL_COMPANY_EVENT_100")
        example = max(meals50, 1_000.0)
        opps.append(self._opp(
            "company_event_100",
            "Hold a company-wide event",
            "Your next team dinner or offsite: invite the whole team and it is 100% deductible instead of 50%. Hold it before December 31 and keep the invite list.",
            "IRC 274(e)(4), 274(n)(2)(A)",
            status="qualified" if events > 0 else "close",
            value=round(example * 0.50 * rate, 2),
            gap=f"You have {self._money(meals50)} of 50% meals this year and {self._money(events)} of 100% events." if meals50 or events else "No meal spend recorded yet.",
            deadline=f"{year}-12-31",
            value_note=f"Tax saved on a {self._money(example)} event versus the same amount as 50% meals, at {int(rate * 100)}%",
        ))

        # 2. Open meal questions are deductions waiting to be claimed.
        open_q = int(summary.get("open_questions", 0))
        if open_q:
            pending = sum(c["nondeductible"] for c in summary["by_class"] if c["tax_class"] in ("MEAL_BUSINESS_50",))
            opps.append(self._opp(
                "answer_meal_questions",
                f"Answer {open_q} open meal question{'s' if open_q != 1 else ''}",
                "Swipe through the meal cards and say who was there. A whole-company answer doubles the deduction; an unanswered card is treated as 50% and flagged for review.",
                "IRC 274(d) substantiation",
                status="close",
                value=round(pending * rate, 2),
                gap=f"{open_q} meals are provisionally 50% deductible.",
                value_note="Tax on the half that becomes deductible if these were company events",
            ))

        # 3. Entertainment is 0%; separate the food.
        ent = spent("ENTERTAINMENT_0")
        if ent > 0:
            opps.append(self._opp(
                "separate_meals_from_entertainment",
                "Separate food from entertainment",
                "Tickets and golf are not deductible, but food bought separately at the event is a 50% meal. Ask vendors to invoice food on its own line.",
                "IRC 274(a); Reg. 1.274-11",
                status="close",
                value=round(ent * 0.30 * 0.50 * rate, 2),
                gap=f"{self._money(ent)} of entertainment is currently 0% deductible.",
                value_note="Assumes 30% of the spend was food",
            ))

        # 4. Office-provided meals became nondeductible in 2026.
        office = spent("MEAL_EMPLOYER_CONVENIENCE_0")
        if office > 0 and year >= 2026:
            opps.append(self._opp(
                "office_meals_sunset",
                "Redirect office meal spend",
                "Office lunches and snacks are 0% deductible from 2026. Move that budget to company-wide events (100%) or treat it as taxable compensation.",
                "IRC 274(o)",
                status="close",
                value=round(office * rate, 2),
                gap=f"{self._money(office)} of office meals this year has no deduction.",
            ))

        # 5. Research credit from the engine.
        engine = _research_engine()
        rd = None
        if engine is not None:
            try:
                rd = engine.research_and_calculate_tax_credits(
                    state=state,
                    cloud_compute_spend=spent("CLOUD_100") or None,
                    rd_payroll_spend=spent("PAYROLL_100") + spent("CONTRACTOR_100") * 0.65 or None,
                )
            except Exception:
                rd = None
        qre_spend = float(summary.get("qre_candidate_spend", 0.0))
        if rd:
            opps.append(self._opp(
                "research_credit_41",
                "Claim the research credit",
                "Track engineering hours by project and keep commit history. File Form 6765 with the return. Businesses under five years of revenue can take up to $500,000 against payroll tax on Form 8974.",
                "IRC 41; IRC 41(h) payroll offset",
                status="qualified" if rd["total_qualified_research_expenses"] > 0 else "not_yet",
                value=float(rd["federal_section_41_credit"]),
                gap=f"Qualified research expenses so far: {self._money(rd['total_qualified_research_expenses'])}.",
                value_note="Federal credit at the 14% alternative simplified rate",
                detail=rd,
            ))
            if rd.get("state_tax_credit", 0) > 0:
                opps.append(self._opp(
                    "state_research_credit",
                    f"Claim the {state.upper()} research credit",
                    f"File the state research credit form with the {state.upper()} return using the same qualified research expenses.",
                    rd["statutory_references"][-1] if rd.get("statutory_references") else f"{state.upper()} research credit",
                    status="qualified",
                    value=float(rd["state_tax_credit"]),
                    gap="Uses the same QRE as the federal credit.",
                ))
            opps.append(self._opp(
                "section_174_amortization",
                "Amortize development costs correctly",
                "Domestic development costs are capitalized and amortized over five years. Keep development spend tagged so the amortization schedule is right.",
                "IRC 174",
                status="qualified" if qre_spend > 0 else "not_yet",
                value=float(rd["sec_174_annual_amortization_deduction"]) * rate,
                gap=f"Annual amortization deduction: {self._money(rd['sec_174_annual_amortization_deduction'])}.",
                value_note="Tax value of this year's amortization deduction",
            ))

        # 6. Equipment: Section 179 and de minimis.
        eq179 = spent("EQUIPMENT_179")
        eqdm = spent("EQUIPMENT_DE_MINIMIS")
        opps.append(self._opp(
            "section_179",
            "Expense equipment in year one",
            "Buy and place in service the equipment you already need before December 31 and elect Section 179 on Form 4562 to deduct it this year instead of over five years.",
            "IRC 179; IRC 168(k)",
            status="qualified" if eq179 > 0 else "close",
            value=round((eq179 if eq179 > 0 else 5_000.0) * rate, 2),
            gap=f"{self._money(eq179)} of equipment over the {self._money(DE_MINIMIS_LIMIT)} threshold this year." if eq179 else "No equipment over the threshold yet.",
            deadline=f"{year}-12-31",
            value_note="Tax on the amount deducted this year rather than depreciated",
        ))
        if eqdm > 0:
            opps.append(self._opp(
                "de_minimis_election",
                "Attach the de minimis safe harbor election",
                f"Include the annual election statement with the return so items at or under {self._money(DE_MINIMIS_LIMIT)} stay expensed.",
                "Reg. 1.263(a)-1(f)",
                status="qualified",
                value=round(eqdm * rate, 2),
                gap=f"{self._money(eqdm)} of small equipment expensed this year.",
            ))

        # 7. Retirement plan startup credit.
        payroll = spent("PAYROLL_100")
        opps.append(self._opp(
            "retirement_startup_credit",
            "Start a retirement plan",
            "Open a 401(k) or SIMPLE IRA. Employers with up to 100 employees get a credit for startup costs for three years, plus $500 a year for auto-enrollment, plus a credit for employer contributions in the first five years.",
            "IRC 45E, 45T",
            status="close" if payroll > 0 else "not_yet",
            value=RETIREMENT_STARTUP_CREDIT_MAX + AUTO_ENROLL_CREDIT,
            gap="No retirement plan provider seen in payroll vendors." if payroll > 0 else "Needs W-2 employees first.",
            value_note="Maximum first-year credit (startup costs plus auto-enrollment)",
        ))

        # 8. Work Opportunity Tax Credit.
        if payroll > 0:
            opps.append(self._opp(
                "wotc_hiring",
                "Screen new hires for the Work Opportunity credit",
                "Before the offer, have candidates complete Form 8850. Hires from targeted groups (veterans, long-term unemployed, SNAP recipients) earn a credit per hire. Submit within 28 days of the start date.",
                "IRC 51; Form 5884",
                status="close",
                value=WOTC_MIN,
                gap="Credit per qualifying hire ranges from $2,400 to $9,600.",
                value_note="Minimum credit for one qualifying hire",
            ))

        # 9. Small employer health insurance credit.
        if payroll > 0 and (employees is None or employees < 25):
            opps.append(self._opp(
                "small_employer_health_credit",
                "Claim the small employer health credit",
                "If you pay at least half of employee premiums through a SHOP plan and have fewer than 25 full-time equivalents with average wages under the limit, up to 50% of premiums comes back as a credit for two years.",
                "IRC 45R; Form 8941",
                status="close" if spent("INSURANCE_100") > 0 else "not_yet",
                value=round(spent("INSURANCE_100") * 0.50, 2) if spent("INSURANCE_100") else 0.0,
                gap="Requires a SHOP marketplace plan and employee wage data.",
            ))

        # 10. Home office when there is no rent.
        if spent("RENT_100") == 0:
            opps.append(self._opp(
                "home_office_simplified",
                "Take the home office deduction",
                "If a room is used regularly and exclusively for the business, deduct $5 per square foot up to 300 square feet with the simplified method. No receipts needed.",
                "IRC 280A; Rev. Proc. 2013-13",
                status="close",
                value=round(HOME_OFFICE_SIMPLIFIED_MAX * rate, 2),
                gap="No rent expense seen; a qualifying home office may apply.",
                value_note="Tax on the maximum simplified deduction",
            ))

        # 11. Vehicle mileage log.
        if spent("VEHICLE_MILEAGE") > 0:
            opps.append(self._opp(
                "mileage_log",
                "Keep a mileage log",
                f"Fuel and parking charges suggest business driving. Log business miles; each mile is worth about {STANDARD_MILEAGE_RATE:.2f} dollars at the standard rate, often more than the actual fuel cost.",
                "IRC 274(d); IRS standard mileage rate",
                status="close",
                value=round(5_000 * STANDARD_MILEAGE_RATE * rate, 2),
                gap=f"{self._money(spent('VEHICLE_MILEAGE'))} of vehicle costs recorded without a mileage log.",
                value_note="Tax on 5,000 logged business miles",
            ))

        # 12. Gifts over the cap.
        gifts = by_class.get("GIFT_25_CAP")
        if gifts and gifts["nondeductible"] > 0:
            opps.append(self._opp(
                "gift_cap",
                "Keep business gifts at $25 per person",
                "Gifts above $25 per recipient per year are not deductible. Branded items under $4 and food shared at the office count differently; split large gifts across recipients.",
                "IRC 274(b)",
                status="close",
                value=round(gifts["nondeductible"] * rate, 2),
                gap=f"{self._money(gifts['nondeductible'])} of gifts above the cap.",
            ))

        # 13. Unclassified spend is a lost deduction.
        uncl = by_class.get("UNCLASSIFIED")
        if uncl and uncl["spent"] > 0:
            opps.append(self._opp(
                "classify_unknown_spend",
                f"Classify {uncl['count']} unknown transaction{'s' if uncl['count'] != 1 else ''}",
                "Give each one a category on the approvals screen. Anything left unclassified at year end is treated as nondeductible.",
                "IRC 162; IRC 6001 recordkeeping",
                status="close",
                value=round(uncl["spent"] * rate, 2),
                gap=f"{self._money(uncl['spent'])} has no tax class.",
                value_note="Tax on the full amount if it is all ordinary business expense",
            ))

        order = {"close": 0, "qualified": 1, "not_yet": 2}
        opps.sort(key=lambda o: (order.get(o["status"], 3), -float(o["estimated_value"] or 0)))
        next_action = next((o for o in opps if o["status"] == "close"), opps[0] if opps else None)
        return {
            "business_id": bid,
            "tax_year": year,
            "state": state.upper(),
            "marginal_rate": rate,
            "days_left_in_year": max(days_left, 0),
            "summary": {
                "total_spent": summary["total_spent"],
                "total_deductible": summary["total_deductible"],
                "total_nondeductible": summary["total_nondeductible"],
                "open_questions": summary["open_questions"],
            },
            "next_action": next_action,
            "opportunities": opps,
            "count": len(opps),
            "disclaimer": "Estimates for planning. A tax professional confirms eligibility and files the forms.",
            "status": "OK",
        }

    @staticmethod
    def _money(v: float) -> str:
        return f"${v:,.0f}"

    @staticmethod
    def _opp(
        oid: str, title: str, action: str, reference: str, status: str, value: float,
        gap: str = "", deadline: Optional[str] = None, value_note: str = "", detail: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return {
            "id": oid,
            "title": title,
            "action": action,
            "reference": reference,
            "status": status,
            "estimated_value": round(float(value or 0.0), 2),
            "value_note": value_note,
            "gap": gap,
            "deadline": deadline,
            "detail": detail,
        }
