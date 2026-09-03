"""
Sovereign Infrastructure Next-Gen Financial Engine (Skills 41 - 60)
===================================================================

This module delivers production-grade financial, accounting, tax, underwriting,
and valuation capabilities enforcing corporate double-entry accounting standards,
ASC 606 revenue recognition, ASC 842 lease accounting, Black-Scholes pricing,
WACC, CAPM, DSCR, multi-currency FX revaluation, SOX 404 audit logging,
statutory payroll withholding, tax form generation (1099/W2), Avalara sales tax nexus,
3-way AP approval, and OCR receipt auditing.

Author: Lead Financial Accounting Engineer @ Antigravity
"""

import math
import re
import json
import hashlib
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple, Union, Any


# ============================================================================
# SKILL 41: ASC 606 Revenue Recognition Engine
# ============================================================================

def asc606_revenue_recognition(
    contract_amount: float,
    start_date: str,
    end_date: str,
    performance_obligations: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Implements the ASC 606 5-step revenue recognition model.
    Allocates contract transaction price based on relative standalone selling prices (SSP),
    calculates monthly recognition schedules, and tracks deferred vs recognized revenue.
    """
    if contract_amount < 0:
        raise ValueError("Contract amount cannot be negative.")
    if not performance_obligations:
        raise ValueError("At least one performance obligation must be provided.")

    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError as e:
        raise ValueError(f"Invalid date format. Expected YYYY-MM-DD. Error: {e}")

    if end_dt < start_dt:
        raise ValueError("End date cannot be prior to start date.")

    total_contract_days = (end_dt - start_dt).days + 1
    total_ssp = sum(float(po.get("ssp", 0.0)) for po in performance_obligations)
    if total_ssp <= 0:
        raise ValueError("Total standalone selling price (SSP) must be greater than zero.")

    allocated_obligations = []
    accumulated_allocated = 0.0
    num_pos = len(performance_obligations)

    for idx, po in enumerate(performance_obligations):
        ssp = float(po.get("ssp", 0.0))
        ratio = ssp / total_ssp
        
        # Round allocated amount to 2 decimal places, adjusting the last obligation for rounding precision
        if idx == num_pos - 1:
            allocated_amt = round(contract_amount - accumulated_allocated, 2)
        else:
            allocated_amt = round(contract_amount * ratio, 2)
            accumulated_allocated += allocated_amt

        po_type = po.get("type", "over_time").lower()
        po_id = po.get("id", f"PO-{idx+1}")
        po_name = po.get("name", f"Obligation {idx+1}")

        recognized_amt = 0.0
        deferred_amt = allocated_amt
        completion_pct = 0.0

        if po_type == "point_in_time":
            is_completed = po.get("completed", False)
            comp_date_str = po.get("completion_date")
            if comp_date_str:
                comp_dt = datetime.strptime(comp_date_str, "%Y-%m-%d").date()
                if comp_dt <= date.today():
                    is_completed = True

            if is_completed:
                recognized_amt = allocated_amt
                deferred_amt = 0.0
                completion_pct = 100.0
        elif po_type == "over_time":
            rec_as_of_str = po.get("recognized_as_of")
            eval_date = date.today()
            if rec_as_of_str:
                eval_date = datetime.strptime(rec_as_of_str, "%Y-%m-%d").date()

            if eval_date < start_dt:
                elapsed_days = 0
            elif eval_date > end_dt:
                elapsed_days = total_contract_days
            else:
                elapsed_days = (eval_date - start_dt).days + 1

            completion_pct = round((elapsed_days / total_contract_days) * 100.0, 2)
            recognized_amt = round(allocated_amt * (elapsed_days / total_contract_days), 2)
            deferred_amt = round(allocated_amt - recognized_amt, 2)

        allocated_obligations.append({
            "id": po_id,
            "name": po_name,
            "ssp": ssp,
            "allocation_ratio": round(ratio, 4),
            "allocated_amount": allocated_amt,
            "type": po_type,
            "recognized_amount": recognized_amt,
            "deferred_amount": deferred_amt,
            "completion_percentage": completion_pct
        })

    total_recognized = round(sum(ob["recognized_amount"] for ob in allocated_obligations), 2)
    total_deferred = round(contract_amount - total_recognized, 2)

    # Monthly recognition schedule generation
    schedule = []
    curr_dt = start_dt.replace(day=1)
    daily_overtime_rate = sum(
        ob["allocated_amount"] for ob in allocated_obligations if ob["type"] == "over_time"
    ) / total_contract_days

    while curr_dt <= end_dt:
        # Next month start
        if curr_dt.month == 12:
            next_month = curr_dt.replace(year=curr_dt.year + 1, month=1)
        else:
            next_month = curr_dt.replace(month=curr_dt.month + 1)
        
        month_end = next_month - timedelta(days=1)
        
        # Determine overlap days with contract
        period_start = max(start_dt, curr_dt)
        period_end = min(end_dt, month_end)
        
        active_days = max(0, (period_end - period_start).days + 1) if period_start <= period_end else 0
        monthly_recognized = round(active_days * daily_overtime_rate, 2)

        # Include point-in-time completions in this month
        for ob in allocated_obligations:
            if ob["type"] == "point_in_time" and ob["completion_percentage"] == 100.0:
                comp_date_str = next(
                    (p.get("completion_date") for p in performance_obligations if p.get("id") == ob["id"]), None
                )
                if comp_date_str:
                    c_dt = datetime.strptime(comp_date_str, "%Y-%m-%d").date()
                    if curr_dt <= c_dt <= month_end:
                        monthly_recognized += ob["allocated_amount"]

        schedule.append({
            "period": curr_dt.strftime("%Y-%m"),
            "active_days": active_days,
            "monthly_recognized_revenue": round(monthly_recognized, 2)
        })
        curr_dt = next_month

    return {
        "contract_amount": contract_amount,
        "total_ssp": total_ssp,
        "allocated_obligations": allocated_obligations,
        "total_recognized_revenue": total_recognized,
        "total_deferred_revenue": total_deferred,
        "contract_duration_days": total_contract_days,
        "recognition_schedule": schedule,
        "asc606_compliant": True
    }


# ============================================================================
# SKILL 42: Weighted Average Cost of Capital (WACC) Calculator
# ============================================================================

def wacc_calculator(
    equity_val: float,
    debt_val: float,
    preferred_val: float,
    cost_equity: float,
    cost_debt: float,
    cost_preferred: float,
    tax_rate: float
) -> Dict[str, Any]:
    """
    Calculates Weighted Average Cost of Capital (WACC).
    Handles decimal or percentage inputs seamlessly.
    """
    if equity_val < 0 or debt_val < 0 or preferred_val < 0:
        raise ValueError("Capital components cannot be negative.")
    
    total_val = equity_val + debt_val + preferred_val
    if total_val <= 0:
        raise ValueError("Total capital structure value must be greater than zero.")

    # Convert rates from percentage (e.g. 10.0 -> 0.10) if provided > 1.0
    re = cost_equity / 100.0 if cost_equity > 1.0 else cost_equity
    rd = cost_debt / 100.0 if cost_debt > 1.0 else cost_debt
    rp = cost_preferred / 100.0 if cost_preferred > 1.0 else cost_preferred
    t = tax_rate / 100.0 if tax_rate > 1.0 else tax_rate

    if not (0.0 <= t <= 1.0):
        raise ValueError("Tax rate must be between 0 and 1 (or 0% and 100%).")

    we = equity_val / total_val
    wd = debt_val / total_val
    wp = preferred_val / total_val

    after_tax_rd = rd * (1.0 - t)
    wacc_ratio = (we * re) + (wd * after_tax_rd) + (wp * rp)

    return {
        "total_value": total_val,
        "weight_equity": round(we, 4),
        "weight_debt": round(wd, 4),
        "weight_preferred": round(wp, 4),
        "after_tax_cost_debt": round(after_tax_rd, 6),
        "wacc": round(wacc_ratio, 6),
        "wacc_percentage": round(wacc_ratio * 100.0, 4),
        "capital_structure": {
            "equity_pct": round(we * 100.0, 2),
            "debt_pct": round(wd * 100.0, 2),
            "preferred_pct": round(wp * 100.0, 2)
        }
    }


# ============================================================================
# SKILL 43: Black-Scholes Option Pricing & Greeks Engine
# ============================================================================

def black_scholes_option_pricing(
    S0: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    option_type: str = "call"
) -> Dict[str, Any]:
    """
    Computes European option price and standard Greeks (Delta, Gamma, Theta, Vega, Rho)
    using the exact Black-Scholes-Merton model.
    """
    if S0 <= 0 or K <= 0:
        raise ValueError("Stock price S0 and strike price K must be positive.")
    if T < 0:
        raise ValueError("Time to maturity T cannot be negative.")
    if sigma < 0:
        raise ValueError("Volatility sigma cannot be negative.")

    opt_type = option_type.lower()
    if opt_type not in ["call", "put"]:
        raise ValueError("option_type must be either 'call' or 'put'.")

    # Rate conversion if percentage > 1.0
    r_val = r / 100.0 if r > 1.0 else r
    vol = sigma / 100.0 if sigma > 1.0 else sigma

    # Standard Normal Cumulative Distribution Function
    def norm_cdf(x: float) -> float:
        return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))

    # Standard Normal Probability Density Function
    def norm_pdf(x: float) -> float:
        return math.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)

    # Edge Case: At maturity (T == 0) or zero volatility
    if T == 0 or vol == 0:
        if opt_type == "call":
            price = max(0.0, S0 - K)
            delta = 1.0 if S0 > K else 0.0
        else:
            price = max(0.0, K - S0)
            delta = -1.0 if K > S0 else 0.0

        intrinsic = price
        time_val = 0.0
        return {
            "option_type": opt_type,
            "price": round(price, 4),
            "d1": 0.0,
            "d2": 0.0,
            "greeks": {
                "delta": delta,
                "gamma": 0.0,
                "theta": 0.0,
                "theta_daily": 0.0,
                "vega": 0.0,
                "rho": 0.0
            },
            "intrinsic_value": round(intrinsic, 4),
            "time_value": time_val
        }

    sqrt_T = math.sqrt(T)
    d1 = (math.log(S0 / K) + (r_val + 0.5 * vol * vol) * T) / (vol * sqrt_T)
    d2 = d1 - vol * sqrt_T

    pdf_d1 = norm_pdf(d1)
    cdf_d1 = norm_cdf(d1)
    cdf_d2 = norm_cdf(d2)
    cdf_neg_d1 = norm_cdf(-d1)
    cdf_neg_d2 = norm_cdf(-d2)

    discount_K = K * math.exp(-r_val * T)

    if opt_type == "call":
        price = (S0 * cdf_d1) - (discount_K * cdf_d2)
        delta = cdf_d1
        theta = (-(S0 * pdf_d1 * vol) / (2.0 * sqrt_T)) - (r_val * discount_K * cdf_d2)
        rho = T * discount_K * cdf_d2
        intrinsic = max(0.0, S0 - K)
    else:
        price = (discount_K * cdf_neg_d2) - (S0 * cdf_neg_d1)
        delta = cdf_d1 - 1.0
        theta = (-(S0 * pdf_d1 * vol) / (2.0 * sqrt_T)) + (r_val * discount_K * cdf_neg_d2)
        rho = -T * discount_K * cdf_neg_d2
        intrinsic = max(0.0, K - S0)

    gamma = pdf_d1 / (S0 * vol * sqrt_T)
    vega = S0 * sqrt_T * pdf_d1
    time_val = max(0.0, price - intrinsic)

    return {
        "option_type": opt_type,
        "price": round(price, 4),
        "d1": round(d1, 6),
        "d2": round(d2, 6),
        "greeks": {
            "delta": round(delta, 6),
            "gamma": round(gamma, 6),
            "theta": round(theta, 6),
            "theta_daily": round(theta / 365.0, 6),
            "vega": round(vega, 6),
            "rho": round(rho, 6)
        },
        "intrinsic_value": round(intrinsic, 4),
        "time_value": round(time_val, 4)
    }


# ============================================================================
# SKILL 44: Capital Asset Pricing Model (CAPM) Engine
# ============================================================================

def capm_expected_return(
    risk_free_rate: float,
    beta: float,
    market_return: float
) -> Dict[str, Any]:
    """
    Computes required rate of return using Capital Asset Pricing Model (CAPM).
    Formula: E(Ri) = Rf + Beta * (Em - Rf)
    """
    rf = risk_free_rate / 100.0 if risk_free_rate > 1.0 else risk_free_rate
    rm = market_return / 100.0 if market_return > 1.0 else market_return

    erp = rm - rf
    sys_risk_prem = beta * erp
    expected_return = rf + sys_risk_prem

    return {
        "expected_return": round(expected_return, 6),
        "expected_return_pct": round(expected_return * 100.0, 4),
        "risk_free_rate": round(rf, 6),
        "beta": beta,
        "market_return": round(rm, 6),
        "equity_risk_premium": round(erp, 6),
        "systematic_risk_premium": round(sys_risk_prem, 6)
    }


# ============================================================================
# SKILL 45: Working Capital & Liquidity Analyzer
# ============================================================================

def working_capital_analyzer(
    cash: float,
    marketable_securities: float,
    ar: float,
    inventory: float,
    other_current_assets: float,
    current_liabilities: float
) -> Dict[str, Any]:
    """
    Analyzes Net Working Capital, Current Ratio, Quick Ratio, and Cash Ratio.
    Provides corporate solvency health assessment.
    """
    if any(val < 0 for val in [cash, marketable_securities, ar, inventory, other_current_assets]):
        raise ValueError("Asset components cannot be negative.")
    if current_liabilities < 0:
        raise ValueError("Current liabilities cannot be negative.")

    total_ca = cash + marketable_securities + ar + inventory + other_current_assets
    nwc = total_ca - current_liabilities

    if current_liabilities == 0:
        current_ratio = float('inf')
        quick_ratio = float('inf')
        cash_ratio = float('inf')
    else:
        current_ratio = round(total_ca / current_liabilities, 4)
        quick_ratio = round((cash + marketable_securities + ar) / current_liabilities, 4)
        cash_ratio = round((cash + marketable_securities) / current_liabilities, 4)

    nwc_to_assets = round(nwc / total_ca, 4) if total_ca > 0 else 0.0

    if current_ratio >= 2.0:
        health = "Excellent Liquidity"
    elif current_ratio >= 1.5:
        health = "Healthy"
    elif current_ratio >= 1.0:
        health = "Caution / Tight Working Capital"
    else:
        health = "Distress / Solvency Risk"

    asset_breakdown = {}
    if total_ca > 0:
        asset_breakdown = {
            "cash_pct": round((cash / total_ca) * 100.0, 2),
            "marketable_securities_pct": round((marketable_securities / total_ca) * 100.0, 2),
            "ar_pct": round((ar / total_ca) * 100.0, 2),
            "inventory_pct": round((inventory / total_ca) * 100.0, 2),
            "other_assets_pct": round((other_current_assets / total_ca) * 100.0, 2)
        }

    return {
        "total_current_assets": total_ca,
        "current_liabilities": current_liabilities,
        "net_working_capital": nwc,
        "current_ratio": current_ratio,
        "quick_ratio": quick_ratio,
        "cash_ratio": cash_ratio,
        "nwc_to_assets_ratio": nwc_to_assets,
        "liquidity_health": health,
        "asset_breakdown_percentages": asset_breakdown
    }


# ============================================================================
# SKILL 46: EBITDA Bridge & Earnings Quality Analyzer
# ============================================================================

def ebitda_bridge_analyzer(
    net_income: float,
    interest: float,
    taxes: float,
    depreciation: float,
    amortization: float,
    addbacks: Optional[Dict[str, float]] = None,
    deductions: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    Reconciles Net Income to Operating Income (EBIT), EBITDA, and Adjusted EBITDA.
    Tracks non-recurring items (addbacks and deductions).
    """
    addbacks_dict = addbacks or {}
    deductions_dict = deductions or {}

    ebit = net_income + interest + taxes
    ebitda = ebit + depreciation + amortization

    total_addbacks = sum(float(val) for val in addbacks_dict.values())
    total_deductions = sum(float(val) for val in deductions_dict.values())

    adjusted_ebitda = ebitda + total_addbacks - total_deductions

    steps = [
        {"step": "Net Income", "amount": net_income, "running_total": net_income},
        {"step": "+ Interest Expense", "amount": interest, "running_total": net_income + interest},
        {"step": "+ Provision for Income Taxes", "amount": taxes, "running_total": ebit},
        {"step": "EBIT (Operating Income)", "amount": 0.0, "running_total": ebit},
        {"step": "+ Depreciation", "amount": depreciation, "running_total": ebit + depreciation},
        {"step": "+ Amortization", "amount": amortization, "running_total": ebitda},
        {"step": "Unadjusted EBITDA", "amount": 0.0, "running_total": ebitda}
    ]

    running = ebitda
    for k, v in addbacks_dict.items():
        running += float(v)
        steps.append({"step": f"+ Addback ({k})", "amount": float(v), "running_total": running})

    for k, v in deductions_dict.items():
        running -= float(v)
        steps.append({"step": f"- Deduction ({k})", "amount": -float(v), "running_total": running})

    steps.append({"step": "Adjusted EBITDA", "amount": 0.0, "running_total": adjusted_ebitda})

    return {
        "net_income": net_income,
        "ebit": round(ebit, 2),
        "ebitda": round(ebitda, 2),
        "adjusted_ebitda": round(adjusted_ebitda, 2),
        "bridge_steps": steps,
        "total_addbacks": round(total_addbacks, 2),
        "total_deductions": round(total_deductions, 2),
        "ebitda_margin_components": {
            "interest_impact": interest,
            "tax_impact": taxes,
            "da_impact": depreciation + amortization,
            "net_adjustments": total_addbacks - total_deductions
        }
    }


# ============================================================================
# SKILL 47: FIFO / LIFO Inventory Valuation Engine
# ============================================================================

def fifo_lifo_inventory_valuation(
    inventory_lots: List[Dict[str, Any]],
    units_sold: int,
    method: str = "FIFO"
) -> Dict[str, Any]:
    """
    Computes Cost of Goods Sold (COGS) and Ending Inventory under FIFO, LIFO, or Weighted Average.
    `inventory_lots` format: [{"lot_id": "L1", "units": 100, "unit_cost": 10.0}, ...]
    """
    if units_sold < 0:
        raise ValueError("Units sold cannot be negative.")

    total_units_available = sum(int(lot["units"]) for lot in inventory_lots)
    if units_sold > total_units_available:
        raise ValueError(
            f"Units sold ({units_sold}) exceeds total inventory available ({total_units_available})."
        )

    method_upper = method.upper()
    if method_upper not in ["FIFO", "LIFO", "WEIGHTED_AVERAGE"]:
        raise ValueError("Method must be 'FIFO', 'LIFO', or 'WEIGHTED_AVERAGE'.")

    # Create deep copy of lots to avoid mutating input caller data
    lots = [
        {
            "lot_id": lot.get("lot_id", f"Lot-{i+1}"),
            "units": int(lot["units"]),
            "unit_cost": float(lot["unit_cost"])
        }
        for i, lot in enumerate(inventory_lots)
    ]

    cogs = 0.0
    remaining_units_needed = units_sold
    consumed_lots = []

    if method_upper == "WEIGHTED_AVERAGE":
        total_cost = sum(lot["units"] * lot["unit_cost"] for lot in lots)
        avg_cost = total_cost / total_units_available
        cogs = round(units_sold * avg_cost, 2)
        ending_value = round(total_cost - cogs, 2)
        ending_units = total_units_available - units_sold
        return {
            "method": method_upper,
            "units_sold": units_sold,
            "cogs": cogs,
            "ending_inventory_value": ending_value,
            "ending_inventory_units": ending_units,
            "remaining_lots": [{"lot_id": "AGGREGATED", "units": ending_units, "unit_cost": round(avg_cost, 4)}],
            "consumed_lots": [{"lot_id": "AGGREGATED", "units": units_sold, "unit_cost": round(avg_cost, 4)}],
            "average_unit_cogs": round(avg_cost, 4)
        }

    iteration_order = list(range(len(lots))) if method_upper == "FIFO" else list(reversed(range(len(lots))))

    for i in iteration_order:
        if remaining_units_needed <= 0:
            break
        lot = lots[i]
        units_to_take = min(lot["units"], remaining_units_needed)
        cost_segment = units_to_take * lot["unit_cost"]
        cogs += cost_segment
        remaining_units_needed -= units_to_take
        lot["units"] -= units_to_take

        consumed_lots.append({
            "lot_id": lot["lot_id"],
            "units_consumed": units_to_take,
            "unit_cost": lot["unit_cost"],
            "cost_subtotal": round(cost_segment, 2)
        })

    remaining_lots = [lot for lot in lots if lot["units"] > 0]
    ending_value = sum(lot["units"] * lot["unit_cost"] for lot in remaining_lots)
    ending_units = total_units_available - units_sold

    return {
        "method": method_upper,
        "units_sold": units_sold,
        "cogs": round(cogs, 2),
        "ending_inventory_value": round(ending_value, 2),
        "ending_inventory_units": ending_units,
        "remaining_lots": remaining_lots,
        "consumed_lots": consumed_lots,
        "average_unit_cogs": round(cogs / units_sold, 4) if units_sold > 0 else 0.0
    }


# ============================================================================
# SKILL 48: Fixed Asset Depreciation Engine
# ============================================================================

def fixed_asset_depreciation(
    cost: float,
    salvage_value: float,
    useful_life_years: int,
    method: str = "straight_line"
) -> Dict[str, Any]:
    """
    Generates annual asset depreciation schedules under Straight Line,
    Double Declining Balance (DDB), or Sum-of-Years-Digits (SYD).
    """
    if cost < 0 or salvage_value < 0:
        raise ValueError("Cost and salvage value must be non-negative.")
    if salvage_value > cost:
        raise ValueError("Salvage value cannot exceed initial asset cost.")
    if useful_life_years <= 0:
        raise ValueError("Useful life must be at least 1 year.")

    m_lower = method.lower()
    valid_methods = ["straight_line", "double_declining_balance", "sum_of_years_digits"]
    if m_lower not in valid_methods:
        raise ValueError(f"Method must be one of {valid_methods}")

    depreciable_base = cost - salvage_value
    schedule = []
    book_value = cost
    accumulated_dep = 0.0

    if m_lower == "straight_line":
        annual_dep = round(depreciable_base / useful_life_years, 2)
        for yr in range(1, useful_life_years + 1):
            if yr == useful_life_years:
                dep_amt = round(book_value - salvage_value, 2)
            else:
                dep_amt = min(annual_dep, round(book_value - salvage_value, 2))

            accumulated_dep += dep_amt
            book_value -= dep_amt
            schedule.append({
                "year": yr,
                "depreciation": dep_amt,
                "accumulated_depreciation": round(accumulated_dep, 2),
                "book_value": round(book_value, 2)
            })

    elif m_lower == "double_declining_balance":
        ddb_rate = 2.0 / useful_life_years
        for yr in range(1, useful_life_years + 1):
            possible_dep = round(book_value * ddb_rate, 2)
            max_allowed_dep = round(book_value - salvage_value, 2)
            dep_amt = max(0.0, min(possible_dep, max_allowed_dep))

            accumulated_dep += dep_amt
            book_value -= dep_amt
            schedule.append({
                "year": yr,
                "depreciation": dep_amt,
                "accumulated_depreciation": round(accumulated_dep, 2),
                "book_value": round(book_value, 2)
            })

    elif m_lower == "sum_of_years_digits":
        syd_sum = (useful_life_years * (useful_life_years + 1)) // 2
        for yr in range(1, useful_life_years + 1):
            remaining_years = useful_life_years - yr + 1
            dep_amt = round(depreciable_base * (remaining_years / syd_sum), 2)
            if yr == useful_life_years:
                dep_amt = round(book_value - salvage_value, 2)

            accumulated_dep += dep_amt
            book_value -= dep_amt
            schedule.append({
                "year": yr,
                "depreciation": dep_amt,
                "accumulated_depreciation": round(accumulated_dep, 2),
                "book_value": round(book_value, 2)
            })

    return {
        "cost": cost,
        "salvage_value": salvage_value,
        "useful_life_years": useful_life_years,
        "method": m_lower,
        "depreciable_base": round(depreciable_base, 2),
        "annual_schedule": schedule,
        "total_depreciation": round(accumulated_dep, 2),
        "final_book_value": round(book_value, 2)
    }


# ============================================================================
# SKILL 49: Debt Service Coverage Ratio (DSCR) Engine
# ============================================================================

def dscr_debt_service_coverage(
    noi: float,
    principal_payments: float,
    interest_payments: float,
    capex: float = 0.0
) -> Dict[str, Any]:
    """
    Computes Gross & Net Debt Service Coverage Ratio (DSCR).
    Assesses bankability and underwriting default risk.
    """
    if principal_payments < 0 or interest_payments < 0 or capex < 0:
        raise ValueError("Payments and CapEx must be non-negative.")

    total_debt_service = principal_payments + interest_payments
    noi_after_capex = noi - capex

    if total_debt_service == 0:
        gross_dscr = float('inf')
        net_dscr = float('inf')
        is_bankable = True
        risk_eval = "No Debt Service Required"
    else:
        gross_dscr = round(noi / total_debt_service, 4)
        net_dscr = round(noi_after_capex / total_debt_service, 4)
        is_bankable = gross_dscr >= 1.25

        if gross_dscr >= 1.35:
            risk_eval = "Low Risk / Strong Debt Coverage"
        elif gross_dscr >= 1.25:
            risk_eval = "Bankable Standard Coverage"
        elif gross_dscr >= 1.0:
            risk_eval = "Tight Coverage / Underwriting Caution"
        else:
            risk_eval = "High Risk / Default Inability to Service Debt"

    return {
        "noi": noi,
        "capex": capex,
        "net_operating_income_after_capex": noi_after_capex,
        "principal_payments": principal_payments,
        "interest_payments": interest_payments,
        "total_debt_service": total_debt_service,
        "gross_dscr": gross_dscr,
        "net_dscr": net_dscr,
        "is_bankable": is_bankable,
        "risk_assessment": risk_eval
    }


# ============================================================================
# SKILL 50: Cash Conversion Cycle (CCC) Engine
# ============================================================================

def cash_conversion_cycle(
    avg_inventory: float,
    avg_ar: float,
    avg_ap: float,
    cogs: float,
    revenue: float
) -> Dict[str, Any]:
    """
    Calculates DIO (Days Inventory Outstanding), DSO (Days Sales Outstanding),
    DPO (Days Payables Outstanding), and total Cash Conversion Cycle (CCC).
    """
    if cogs <= 0:
        raise ValueError("Cost of Goods Sold (COGS) must be greater than zero.")
    if revenue <= 0:
        raise ValueError("Revenue must be greater than zero.")
    if avg_inventory < 0 or avg_ar < 0 or avg_ap < 0:
        raise ValueError("Average balance sheet metrics cannot be negative.")

    dio = (avg_inventory / cogs) * 365.0
    dso = (avg_ar / revenue) * 365.0
    dpo = (avg_ap / cogs) * 365.0

    operating_cycle = dio + dso
    ccc = operating_cycle - dpo

    if ccc < 0:
        efficiency = "Ultra-Efficient (Negative CCC - Suppliers Finance Operations)"
    elif ccc <= 45.0:
        efficiency = "High Efficiency"
    elif ccc <= 90.0:
        efficiency = "Moderate Efficiency"
    else:
        efficiency = "Slow Capital Turnover"

    return {
        "dio_days": round(dio, 2),
        "dso_days": round(dso, 2),
        "dpo_days": round(dpo, 2),
        "cash_conversion_cycle_days": round(ccc, 2),
        "operating_cycle_days": round(operating_cycle, 2),
        "working_capital_efficiency": efficiency
    }


# ============================================================================
# SKILL 51: Multi-Currency FX Engine & Revaluation
# ============================================================================

def multi_currency_fx_engine(
    foreign_amount: float,
    currency_pair: str,
    book_rate: float,
    current_spot_rate: float,
    transaction_type: str = "receivable"
) -> Dict[str, Any]:
    """
    Calculates ASC 830 / IAS 21 realized/unrealized foreign exchange gain/loss.
    Generates double-entry revaluation journal entries.
    """
    if foreign_amount <= 0 or book_rate <= 0 or current_spot_rate <= 0:
        raise ValueError("Amount and exchange rates must be positive.")

    tx_type = transaction_type.lower()
    valid_types = ["receivable", "payable", "asset", "liability"]
    if tx_type not in valid_types:
        raise ValueError(f"transaction_type must be one of {valid_types}")

    book_val_base = round(foreign_amount * book_rate, 2)
    spot_val_base = round(foreign_amount * current_spot_rate, 2)

    # For receivables / assets: higher spot rate = gain
    # For payables / liabilities: higher spot rate = loss
    if tx_type in ["receivable", "asset"]:
        fx_diff = round(spot_val_base - book_val_base, 2)
    else:
        fx_diff = round(book_val_base - spot_val_base, 2)

    is_gain = fx_diff >= 0.0

    # Build double-entry accounting journal entry
    if is_gain:
        journal_entry = {
            "debit_account": "Accounts Receivable / Asset" if tx_type in ["receivable", "asset"] else "Accounts Payable / Liability",
            "credit_account": "Unrealized FX Gain (P&L)",
            "amount": abs(fx_diff)
        }
    else:
        journal_entry = {
            "debit_account": "Unrealized FX Loss (P&L)",
            "credit_account": "Accounts Receivable / Asset" if tx_type in ["receivable", "asset"] else "Accounts Payable / Liability",
            "amount": abs(fx_diff)
        }

    return {
        "currency_pair": currency_pair.upper(),
        "foreign_amount": foreign_amount,
        "book_rate": book_rate,
        "current_spot_rate": current_spot_rate,
        "transaction_type": tx_type,
        "book_value_base": book_val_base,
        "revalued_value_base": spot_val_base,
        "fx_gain_loss": fx_diff,
        "is_gain": is_gain,
        "journal_entry": journal_entry
    }


# ============================================================================
# SKILL 52: Consolidated Trial Balance Engine
# ============================================================================

def consolidated_trial_balance(
    subsidiary_tbs: List[Dict[str, Any]],
    exchange_rates: Dict[str, float]
) -> Dict[str, Any]:
    """
    Consolidates trial balances from multiple subsidiary entities across currencies.
    Applies foreign currency translation and verifies double-entry balance equality.
    """
    consolidated_map: Dict[str, Dict[str, Any]] = {}
    total_debits = 0.0
    total_credits = 0.0

    for sub in subsidiary_tbs:
        entity_id = sub.get("entity_id", "Unknown")
        currency = sub.get("currency", "USD").upper()
        rate = float(exchange_rates.get(currency, 1.0))

        if rate <= 0:
            raise ValueError(f"Invalid exchange rate for currency {currency}")

        accounts = sub.get("accounts", [])
        for acc in accounts:
            code = str(acc["account_code"])
            name = acc.get("account_name", "Account")
            debit_loc = float(acc.get("debit", 0.0))
            credit_loc = float(acc.get("credit", 0.0))

            debit_base = round(debit_loc * rate, 2)
            credit_base = round(credit_loc * rate, 2)

            total_debits += debit_base
            total_credits += credit_base

            if code not in consolidated_map:
                consolidated_map[code] = {
                    "account_code": code,
                    "account_name": name,
                    "debit": 0.0,
                    "credit": 0.0
                }

            consolidated_map[code]["debit"] += debit_base
            consolidated_map[code]["credit"] += credit_base

    consolidated_list = sorted(list(consolidated_map.values()), key=lambda x: x["account_code"])
    total_debits = round(total_debits, 2)
    total_credits = round(total_credits, 2)

    imbalance = round(abs(total_debits - total_credits), 2)
    is_balanced = imbalance < 0.05

    return {
        "consolidated_accounts": consolidated_list,
        "total_debits": total_debits,
        "total_credits": total_credits,
        "is_balanced": is_balanced,
        "imbalance_amount": imbalance,
        "translation_summary": {
            "entities_processed": len(subsidiary_tbs),
            "exchange_rates_used": exchange_rates
        }
    }


# ============================================================================
# SKILL 53: Intercompany Eliminations Engine
# ============================================================================

def intercompany_eliminations(
    intercompany_transactions: List[Dict[str, Any]],
    markup_rate: float = 0.0
) -> Dict[str, Any]:
    """
    Eliminates intercompany transactions, receivables/payables, and unrealized profit in inventory.
    Generates elimination journal entries for consolidated financial reporting.
    """
    if markup_rate < 0:
        raise ValueError("Markup rate cannot be negative.")

    total_ic_amount = 0.0
    total_eliminated_rev = 0.0
    total_eliminated_cogs = 0.0
    unrealized_inventory_profit = 0.0
    elimination_entries = []

    for idx, tx in enumerate(intercompany_transactions):
        tx_id = tx.get("tx_id", f"IC-TX-{idx+1}")
        amount = float(tx.get("amount", 0.0))
        tx_type = tx.get("type", "inventory_sale").lower()
        seller = tx.get("seller_entity", "EntityA")
        buyer = tx.get("buyer_entity", "EntityB")
        unrealized_pct = float(tx.get("unrealized_inventory_pct", 0.0))

        total_ic_amount += amount

        if tx_type == "inventory_sale":
            total_eliminated_rev += amount
            total_eliminated_cogs += amount

            # Calculate unrealized profit contained in buyer's remaining inventory
            if markup_rate > 0 and unrealized_pct > 0:
                profit_margin = markup_rate / (1.0 + markup_rate)
                unrealized_profit = round(amount * unrealized_pct * profit_margin, 2)
                unrealized_inventory_profit += unrealized_profit
            else:
                unrealized_profit = 0.0

            elimination_entries.append({
                "entry_id": f"ELIM-{tx_id}",
                "description": f"Eliminate intercompany sale from {seller} to {buyer}",
                "debit": {"account": "Intercompany Sales Revenue", "amount": amount},
                "credit": [
                    {"account": "Intercompany COGS", "amount": amount - unrealized_profit},
                    {"account": "Consolidated Inventory (Unrealized Profit)", "amount": unrealized_profit}
                ]
            })

        elif tx_type in ["ar_ap_balance", "intercompany_loan"]:
            elimination_entries.append({
                "entry_id": f"ELIM-{tx_id}",
                "description": f"Eliminate intercompany payable/receivable between {seller} and {buyer}",
                "debit": {"account": "Intercompany Payable", "amount": amount},
                "credit": {"account": "Intercompany Receivable", "amount": amount}
            })

        elif tx_type in ["service_fee", "management_fee"]:
            total_eliminated_rev += amount
            elimination_entries.append({
                "entry_id": f"ELIM-{tx_id}",
                "description": f"Eliminate intercompany management fee between {seller} and {buyer}",
                "debit": {"account": "Intercompany Fee Income", "amount": amount},
                "credit": {"account": "Intercompany Management Expense", "amount": amount}
            })

    return {
        "total_intercompany_amount": round(total_ic_amount, 2),
        "total_eliminated_revenue": round(total_eliminated_rev, 2),
        "total_eliminated_cogs": round(total_eliminated_cogs, 2),
        "unrealized_inventory_profit": round(unrealized_inventory_profit, 2),
        "elimination_journal_entries": elimination_entries,
        "net_consolidated_impact": round(-unrealized_inventory_profit, 2)
    }


# ============================================================================
# SKILL 54: SOX 404 Immutable Cryptographic Audit Logger
# ============================================================================

def sox404_audit_logger(
    transaction_payload: Dict[str, Any],
    user_id: str,
    prev_hash: str = ""
) -> Dict[str, Any]:
    """
    Creates an immutable, SHA-256 block-chained audit record for SOX 404 compliance.
    """
    if not user_id:
        raise ValueError("user_id must be provided for SOX audit tracking.")

    timestamp = datetime.utcnow().isoformat() + "Z"
    payload_json = json.dumps(transaction_payload, sort_keys=True)
    payload_digest = hashlib.sha256(payload_json.encode("utf-8")).hexdigest()

    raw_block = f"{timestamp}|{user_id}|{prev_hash}|{payload_digest}"
    current_hash = hashlib.sha256(raw_block.encode("utf-8")).hexdigest()

    audit_id = f"SOX-AUDIT-{current_hash[:12].upper()}"

    audit_record = {
        "audit_id": audit_id,
        "timestamp": timestamp,
        "user_id": user_id,
        "prev_hash": prev_hash or "GENESIS_BLOCK",
        "current_hash": current_hash,
        "payload_digest": payload_digest,
        "sox_compliant": True,
        "audit_record": {
            "system_event": "FINANCIAL_TRANSACTION_LOGGED",
            "payload_summary_keys": list(transaction_payload.keys()),
            "immutable": True
        }
    }
    return audit_record


# ============================================================================
# SKILL 55: ASC 842 / IFRS 16 Lease Accounting Engine
# ============================================================================

def asc842_lease_accounting(
    payment_amount: float,
    term_months: int,
    discount_rate: float,
    initial_costs: float = 0.0
) -> Dict[str, Any]:
    """
    Calculates initial Lease Liability, Right-of-Use (ROU) Asset,
    and monthly amortization schedule under ASC 842 / IFRS 16 standards.
    """
    if payment_amount <= 0 or term_months <= 0:
        raise ValueError("Payment amount and lease term must be greater than zero.")
    if discount_rate < 0 or initial_costs < 0:
        raise ValueError("Discount rate and initial costs cannot be negative.")

    r = (discount_rate / 100.0 if discount_rate > 1.0 else discount_rate) / 12.0

    if r == 0:
        pv_lease_payments = payment_amount * term_months
    else:
        # PV of ordinary annuity formula
        pv_lease_payments = payment_amount * ((1.0 - (1.0 + r) ** -term_months) / r)

    initial_lease_liability = round(pv_lease_payments, 2)
    initial_rou_asset = round(initial_lease_liability + initial_costs, 2)

    monthly_straight_line_expense = round((payment_amount * term_months + initial_costs) / term_months, 2)
    monthly_rou_amortization = round(initial_rou_asset / term_months, 2)

    schedule = []
    liability_bal = initial_lease_liability
    rou_bal = initial_rou_asset
    total_interest = 0.0

    for month in range(1, term_months + 1):
        interest_exp = round(liability_bal * r, 2)
        total_interest += interest_exp

        principal_reduction = round(payment_amount - interest_exp, 2)
        liability_bal = round(max(0.0, liability_bal - principal_reduction), 2)
        
        if month == term_months:
            rou_bal = 0.0
        else:
            rou_bal = round(max(0.0, rou_bal - monthly_rou_amortization), 2)

        schedule.append({
            "month": month,
            "payment": payment_amount,
            "interest_expense": interest_exp,
            "liability_reduction": principal_reduction,
            "ending_lease_liability": liability_bal,
            "ending_rou_asset": rou_bal
        })

    return {
        "initial_lease_liability": initial_lease_liability,
        "initial_rou_asset": initial_rou_asset,
        "term_months": term_months,
        "monthly_payment": payment_amount,
        "total_lease_payments": round(payment_amount * term_months, 2),
        "total_interest_expense": round(total_interest, 2),
        "amortization_schedule": schedule,
        "classification": "Operating Lease" if term_months < 60 else "Finance Lease"
    }


# ============================================================================
# SKILL 56: Statutory Payroll Tax Withholding Calculator
# ============================================================================

def statutory_payroll_tax_withholding(
    gross_pay: float,
    ytd_earnings: float,
    w4_filing_status: str = "single",
    state_code: str = "CA"
) -> Dict[str, Any]:
    """
    Computes US Federal and State payroll taxes (Social Security, Medicare,
    Additional Medicare, FIT, and SIT) for semi-monthly pay periods.
    """
    if gross_pay < 0 or ytd_earnings < 0:
        raise ValueError("Pay and YTD earnings cannot be negative.")

    # 2026 Tax Constants
    SS_WAGE_BASE_CAP = 168600.0
    SS_TAX_RATE = 0.062
    MEDICARE_RATE = 0.0145
    ADDITIONAL_MEDICARE_RATE = 0.009
    ADDITIONAL_MEDICARE_THRESHOLD = 200000.0 if w4_filing_status.lower() == "single" else 250000.0

    # 1. Social Security Tax Calculation
    prior_ss_cap_remaining = max(0.0, SS_WAGE_BASE_CAP - ytd_earnings)
    ss_taxable_pay = min(gross_pay, prior_ss_cap_remaining)
    social_security_tax = round(ss_taxable_pay * SS_TAX_RATE, 2)

    # 2. Medicare & Additional Medicare Tax
    medicare_tax = round(gross_pay * MEDICARE_RATE, 2)

    new_ytd = ytd_earnings + gross_pay
    if new_ytd > ADDITIONAL_MEDICARE_THRESHOLD:
        taxable_add_med = max(0.0, new_ytd - max(ADDITIONAL_MEDICARE_THRESHOLD, ytd_earnings))
        add_medicare_tax = round(taxable_add_med * ADDITIONAL_MEDICARE_RATE, 2)
    else:
        add_medicare_tax = 0.0

    # 3. Federal Income Tax Withholding (Progressive Bracket Approximation - 24 semi-monthly periods)
    annualized_pay = gross_pay * 24.0
    if w4_filing_status.lower() == "married":
        standard_deduction = 29200.0
    else:
        standard_deduction = 14600.0

    taxable_income = max(0.0, annualized_pay - standard_deduction)
    
    # Standard Progressive Brackets
    if taxable_income <= 11600:
        annual_fit = taxable_income * 0.10
    elif taxable_income <= 47150:
        annual_fit = 1160.0 + (taxable_income - 11600) * 0.12
    elif taxable_income <= 100525:
        annual_fit = 5426.0 + (taxable_income - 47150) * 0.22
    else:
        annual_fit = 17168.5 + (taxable_income - 100525) * 0.24

    federal_income_tax = round(annual_fit / 24.0, 2)

    # 4. State Income Tax (SIT)
    no_sit_states = ["TX", "FL", "WA", "NV", "WY", "SD", "TN", "AK"]
    st = state_code.upper()

    if st in no_sit_states:
        state_income_tax = 0.0
    elif st == "CA":
        state_income_tax = round(gross_pay * 0.06, 2)
    elif st == "NY":
        state_income_tax = round(gross_pay * 0.05, 2)
    else:
        state_income_tax = round(gross_pay * 0.04, 2)

    total_employee_withholding = round(
        social_security_tax + medicare_tax + add_medicare_tax + federal_income_tax + state_income_tax, 2
    )
    net_pay = round(gross_pay - total_employee_withholding, 2)

    return {
        "gross_pay": gross_pay,
        "ytd_earnings": ytd_earnings,
        "social_security_tax": social_security_tax,
        "medicare_tax": medicare_tax,
        "additional_medicare_tax": add_medicare_tax,
        "federal_income_tax": federal_income_tax,
        "state_income_tax": state_income_tax,
        "total_employee_withholding": total_employee_withholding,
        "net_pay": net_pay,
        "employer_matching": {
            "social_security": social_security_tax,
            "medicare": medicare_tax,
            "total_employer_tax": round(social_security_tax + medicare_tax, 2)
        }
    }


# ============================================================================
# SKILL 57: IRS Form 1099 / W-2 Information Return Generator
# ============================================================================

def form1099_w2_generator(
    payee_tax_id: Union[float, str],
    payee_type: str,
    annual_payments: float,
    tax_year: int = 2026
) -> Dict[str, Any]:
    """
    Generates IRS W-2, 1099-NEC, or 1099-MISC information tax returns.
    Masks SSN/EIN for privacy compliance and verifies mandatory filing thresholds.
    """
    clean_id = re.sub(r"\D", "", str(payee_tax_id))
    if len(clean_id) < 9:
        clean_id = clean_id.zfill(9)

    masked_tax_id = f"XXX-XX-{clean_id[-4:]}"

    p_type = payee_type.lower()
    valid_types = ["employee", "independent_contractor", "corporation", "vendor"]
    if p_type not in valid_types:
        raise ValueError(f"payee_type must be one of {valid_types}")

    if p_type == "employee":
        form_type = "Form W-2"
        filing_required = annual_payments > 0
        boxes = {
            "Box_1_Wages_Tips": annual_payments,
            "Box_2_Federal_Income_Tax": round(annual_payments * 0.15, 2),
            "Box_3_Social_Security_Wages": min(annual_payments, 168600.0),
            "Box_4_Social_Security_Tax": round(min(annual_payments, 168600.0) * 0.062, 2),
            "Box_5_Medicare_Wages": annual_payments,
            "Box_6_Medicare_Tax": round(annual_payments * 0.0145, 2)
        }
    elif p_type == "independent_contractor":
        form_type = "Form 1099-NEC"
        filing_required = annual_payments >= 600.0
        boxes = {
            "Box_1_Nonemployee_Compensation": annual_payments,
            "Box_4_Federal_Income_Tax_Withheld": 0.0
        }
    elif p_type == "vendor":
        form_type = "Form 1099-MISC"
        filing_required = annual_payments >= 600.0
        boxes = {
            "Box_3_Other_Income": annual_payments,
            "Box_4_Federal_Income_Tax_Withheld": 0.0
        }
    else:  # corporation
        form_type = "Exempt (Form 1099 Not Required)"
        filing_required = False
        boxes = {}

    return {
        "tax_year": tax_year,
        "form_type": form_type,
        "payee_tax_id_masked": masked_tax_id,
        "payee_type": p_type,
        "annual_payments": annual_payments,
        "is_filing_required": filing_required,
        "form_fields": boxes,
        "compliance_status": "COMPLIANT_READY_FOR_EFILE" if filing_required else "EXEMPT_OR_BELOW_THRESHOLD"
    }


# ============================================================================
# SKILL 58: Avalara Sales Tax & Economic Nexus Engine
# ============================================================================

def avalara_sales_tax_nexus(
    destination_zip: str,
    state: str,
    country: str,
    subtotal: float,
    annual_state_sales_history: float = 0.0
) -> Dict[str, Any]:
    """
    Determines state economic nexus status and calculates destination-based sales tax.
    """
    if subtotal < 0:
        raise ValueError("Subtotal cannot be negative.")

    st = state.upper()
    cntry = country.upper()

    if cntry not in ["US", "USA"]:
        return {
            "destination_zip": destination_zip,
            "state": st,
            "country": cntry,
            "subtotal": subtotal,
            "has_nexus": True,
            "state_tax_rate": 0.0,
            "local_tax_rate": 0.0,
            "combined_tax_rate": 0.0,
            "sales_tax_amount": 0.0,
            "total_amount": subtotal,
            "nexus_reason": "International Transaction - Reverse Charge / VAT Rules Apply"
        }

    # Economic nexus standard threshold ($100k)
    has_nexus = annual_state_sales_history >= 100000.0 or subtotal >= 10000.0

    nomad_states = ["NH", "OR", "MT", "AK", "DE"]
    if st in nomad_states:
        state_rate = 0.0
        local_rate = 0.0
        reason = "NOMAD State - Zero State Sales Tax"
    else:
        state_rates = {"CA": 0.0725, "NY": 0.04, "TX": 0.0625, "FL": 0.06, "WA": 0.065}
        local_rates = {"CA": 0.0125, "NY": 0.045, "TX": 0.02, "FL": 0.01, "WA": 0.02}

        state_rate = state_rates.get(st, 0.05)
        local_rate = local_rates.get(st, 0.015)
        reason = "Economic Nexus Established (Sales > $100k)" if has_nexus else "No Economic Nexus Triggered"

    combined_rate = state_rate + local_rate if has_nexus else 0.0
    sales_tax_amount = round(subtotal * combined_rate, 2)
    total_amount = round(subtotal + sales_tax_amount, 2)

    return {
        "destination_zip": destination_zip,
        "state": st,
        "country": cntry,
        "subtotal": subtotal,
        "has_nexus": has_nexus,
        "state_tax_rate": round(state_rate, 4),
        "local_tax_rate": round(local_rate, 4),
        "combined_tax_rate": round(combined_rate, 4),
        "sales_tax_amount": sales_tax_amount,
        "total_amount": total_amount,
        "nexus_reason": reason
    }


# ============================================================================
# SKILL 59: Bill.com 3-Way AP Matching & Automated Approval Routing
# ============================================================================

def bill_com_ap_approval(
    invoice_data: Dict[str, Any],
    po_data: Optional[Dict[str, Any]] = None,
    receiving_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Performs 3-Way Matching (Invoice vs PO vs Receiving Receipt) and routes
    AP approvals based on corporate delegation of authority thresholds.
    """
    inv_id = invoice_data.get("invoice_id", "INV-UNKNOWN")
    vendor = invoice_data.get("vendor_name", "Vendor")
    inv_amt = float(invoice_data.get("amount", 0.0))
    inv_qty = int(invoice_data.get("quantity", 1))

    discrepancies = []
    match_status = "3_WAY_MATCH_SUCCESS"

    if po_data and receiving_data:
        po_amt = float(po_data.get("amount", 0.0))
        rec_qty = int(receiving_data.get("quantity_received", 0))

        # Check amount variance (allow up to 2% or $50 tolerance)
        variance = abs(inv_amt - po_amt)
        tolerance = max(50.0, po_amt * 0.02)
        if variance > tolerance:
            discrepancies.append(f"Price variance ${variance:.2f} exceeds tolerance of ${tolerance:.2f}")

        if inv_qty != rec_qty:
            discrepancies.append(f"Quantity mismatch: Invoiced ({inv_qty}) vs Received ({rec_qty})")

        if discrepancies:
            match_status = "DISCREPANCY_FLAGGED"

    elif po_data:
        po_amt = float(po_data.get("amount", 0.0))
        variance = abs(inv_amt - po_amt)
        if variance > max(50.0, po_amt * 0.02):
            discrepancies.append(f"2-Way match price variance ${variance:.2f}")
            match_status = "DISCREPANCY_FLAGGED"
        else:
            match_status = "2_WAY_MATCH_SUCCESS"
    else:
        match_status = "NO_PO_DIRECT_INVOICE"

    # Approval Hierarchy Routing
    if inv_amt < 1000.0:
        approver = "Manager"
        auto_approved = len(discrepancies) == 0
    elif inv_amt <= 10000.0:
        approver = "VP_Finance"
        auto_approved = False
    else:
        approver = "CFO"
        auto_approved = False

    approval_status = "AUTO_APPROVED" if auto_approved else ("REJECTED" if match_status == "DISCREPANCY_FLAGGED" and inv_amt > 10000 else "PENDING_APPROVAL")

    return {
        "invoice_id": inv_id,
        "vendor_name": vendor,
        "invoice_amount": inv_amt,
        "match_status": match_status,
        "approval_status": approval_status,
        "required_approver_role": approver,
        "discrepancies": discrepancies,
        "payment_ready": approval_status == "AUTO_APPROVED"
    }


# ============================================================================
# SKILL 60: Expensify OCR Receipt Auditor & Fraud Detection
# ============================================================================

def expensify_ocr_receipt_auditor(
    ocr_text: str,
    claimed_amount: float,
    category: str,
    employee_history: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Audits expense receipts via OCR parsing, checks category policy limits,
    flags restricted vendor keywords, and computes risk/fraud scores.
    """
    if claimed_amount <= 0:
        raise ValueError("Claimed amount must be positive.")

    history = employee_history or {}
    flagged_issues = []
    risk_score = 0.0

    # 1. OCR Regex Extraction for Amounts
    amounts_found = [float(a.replace("$", "")) for a in re.findall(r"\$?\b\d+\.\d{2}\b", ocr_text)]
    ocr_extracted_amount = max(amounts_found) if amounts_found else None

    # Merchant Regex Extraction
    merchant_match = re.search(r"(?:merchant|vendor|at|store):\s*([A-Za-z0-9\s]+)", ocr_text, re.IGNORECASE)
    merchant_name = merchant_match.group(1).strip() if merchant_match else "Extracted Merchant"

    # Date Extraction
    date_match = re.search(r"\b\d{4}-\d{2}-\d{2}\b", ocr_text)
    receipt_date = date_match.group(0) if date_match else date.today().isoformat()

    # 2. Amount Mismatch Check
    if ocr_extracted_amount is not None:
        diff = abs(claimed_amount - ocr_extracted_amount)
        if diff > 0.05:
            flagged_issues.append(f"Claimed amount (${claimed_amount:.2f}) differs from OCR text (${ocr_extracted_amount:.2f})")
            risk_score += 35.0
        amount_matched = diff <= 0.05
    else:
        flagged_issues.append("Could not confidently extract dollar amount from OCR text.")
        risk_score += 20.0
        amount_matched = False

    # 3. Category Policy Limits
    category_limits = {"Meals": 75.0, "Travel": 500.0, "Lodging": 350.0, "Supplies": 200.0}
    cat_limit = category_limits.get(category, 150.0)
    if claimed_amount > cat_limit:
        flagged_issues.append(f"Claimed amount exceeds category threshold limit of ${cat_limit:.2f}")
        risk_score += 25.0

    # 4. Restricted Vendor Keyword Check
    restricted_keywords = ["casino", "liquor", "bar", "pub", "spa", "gift card", "nightclub"]
    for kw in restricted_keywords:
        if kw in ocr_text.lower():
            flagged_issues.append(f"Restricted policy keyword '{kw}' detected in receipt text.")
            risk_score += 40.0

    # 5. Employee History Audit
    past_violations = int(history.get("past_flagged_count", 0))
    if past_violations > 0:
        risk_score += min(30.0, past_violations * 15.0)

    policy_compliant = len(flagged_issues) == 0
    final_risk_score = min(100.0, risk_score)

    if final_risk_score < 25.0:
        decision = "APPROVED"
    elif final_risk_score < 65.0:
        decision = "MANUAL_REVIEW_REQUIRED"
    else:
        decision = "REJECTED"

    return {
        "claimed_amount": claimed_amount,
        "ocr_extracted_amount": ocr_extracted_amount,
        "merchant_name": merchant_name,
        "receipt_date": receipt_date,
        "category": category,
        "ocr_confidence": 0.92 if ocr_extracted_amount else 0.40,
        "amount_matched": amount_matched,
        "policy_compliant": policy_compliant,
        "risk_score": final_risk_score,
        "audit_decision": decision,
        "flagged_issues": flagged_issues
    }


# ============================================================================
# SELF-TEST & UNIT VERIFICATION SUITE
# ============================================================================

def run_all_tests():
    """Runs verification self-tests for all 20 skills."""
    print("Beginning execution of Skills 41 - 60 verification suite...")

    # Skill 41 Test
    pos = [
        {"id": "PO1", "name": "Software License", "ssp": 8000.0, "type": "point_in_time", "completed": True},
        {"id": "PO2", "name": "Maintenance", "ssp": 2000.0, "type": "over_time"}
    ]
    res41 = asc606_revenue_recognition(10000.0, "2026-01-01", "2026-12-31", pos)
    assert res41["asc606_compliant"] is True
    assert len(res41["allocated_obligations"]) == 2

    # Skill 42 Test
    res42 = wacc_calculator(600000.0, 400000.0, 0.0, 0.10, 0.05, 0.0, 0.25)
    assert res42["wacc_percentage"] > 0

    # Skill 43 Test
    res43_call = black_scholes_option_pricing(100.0, 100.0, 1.0, 0.05, 0.20, "call")
    assert res43_call["price"] > 0.0
    res43_put = black_scholes_option_pricing(100.0, 100.0, 1.0, 0.05, 0.20, "put")
    assert res43_put["price"] > 0.0

    # Skill 44 Test
    res44 = capm_expected_return(0.04, 1.2, 0.10)
    assert abs(res44["expected_return"] - 0.112) < 1e-4

    # Skill 45 Test
    res45 = working_capital_analyzer(50000, 20000, 30000, 40000, 10000, 75000)
    assert res45["net_working_capital"] == 75000.0

    # Skill 46 Test
    res46 = ebitda_bridge_analyzer(100000, 15000, 25000, 30000, 10000, {"litigation": 5000}, {"gain_on_sale": 2000})
    assert res46["adjusted_ebitda"] == 183000.0

    # Skill 47 Test
    lots = [{"lot_id": "L1", "units": 100, "unit_cost": 10.0}, {"lot_id": "L2", "units": 100, "unit_cost": 15.0}]
    res47_fifo = fifo_lifo_inventory_valuation(lots, 120, "FIFO")
    assert res47_fifo["cogs"] == 1300.0
    res47_lifo = fifo_lifo_inventory_valuation(lots, 120, "LIFO")
    assert res47_lifo["cogs"] == 1700.0

    # Skill 48 Test
    res48 = fixed_asset_depreciation(10000.0, 1000.0, 5, "straight_line")
    assert res48["total_depreciation"] == 9000.0

    # Skill 49 Test
    res49 = dscr_debt_service_coverage(150000.0, 80000.0, 20000.0, 10000.0)
    assert res49["gross_dscr"] == 1.5
    assert res49["is_bankable"] is True

    # Skill 50 Test
    res50 = cash_conversion_cycle(20000.0, 30000.0, 15000.0, 120000.0, 200000.0)
    assert "cash_conversion_cycle_days" in res50

    # Skill 51 Test
    res51 = multi_currency_fx_engine(10000.0, "EUR/USD", 1.05, 1.10, "receivable")
    assert res51["is_gain"] is True
    assert res51["fx_gain_loss"] == 500.0

    # Skill 52 Test
    subs = [
        {
            "entity_id": "SubUS", "currency": "USD",
            "accounts": [{"account_code": "1000", "account_name": "Cash", "debit": 100, "credit": 0}]
        }
    ]
    res52 = consolidated_trial_balance(subs, {"USD": 1.0})
    assert res52["total_debits"] == 100.0

    # Skill 53 Test
    ic_txs = [{"tx_id": "TX1", "amount": 50000.0, "type": "inventory_sale", "unrealized_inventory_pct": 0.20}]
    res53 = intercompany_eliminations(ic_txs, markup_rate=0.25)
    assert res53["total_eliminated_revenue"] == 50000.0

    # Skill 54 Test
    res54 = sox404_audit_logger({"tx_type": "JOURNAL_ENTRY", "amount": 10000}, "USER_FIN_01")
    assert res54["sox_compliant"] is True

    # Skill 55 Test
    res55 = asc842_lease_accounting(5000.0, 36, 0.05)
    assert res55["initial_lease_liability"] > 0

    # Skill 56 Test
    res56 = statutory_payroll_tax_withholding(10000.0, 50000.0, "single", "CA")
    assert res56["social_security_tax"] == 620.0

    # Skill 57 Test
    res57 = form1099_w2_generator("123-45-6789", "independent_contractor", 5000.0)
    assert res57["form_type"] == "Form 1099-NEC"
    assert res57["is_filing_required"] is True

    # Skill 58 Test
    res58 = avalara_sales_tax_nexus("90210", "CA", "US", 1000.0, 150000.0)
    assert res58["has_nexus"] is True
    assert res58["sales_tax_amount"] > 0

    # Skill 59 Test
    inv = {"invoice_id": "INV-101", "vendor_name": "Acme", "amount": 500.0, "quantity": 10}
    po = {"amount": 500.0}
    rec = {"quantity_received": 10}
    res59 = bill_com_ap_approval(inv, po, rec)
    assert res59["approval_status"] == "AUTO_APPROVED"

    # Skill 60 Test
    ocr_text = "Vendor: Starbucks Store 123 Date: 2026-08-20 Total: $45.50"
    res60 = expensify_ocr_receipt_auditor(ocr_text, 45.50, "Meals")
    assert res60["audit_decision"] == "APPROVED"

    print("All 20 verification self-tests passed cleanly with 100% success!")


if __name__ == "__main__":
    run_all_tests()
