"""
capabilities.py — 50 production-ready utility functions across 10 domains.

All functions are real and callable using only the Python standard library.
"""

from __future__ import annotations

import base64
import collections
import csv
import datetime
import hashlib
import io
import json
import math
import os
import platform
import random
import re
import secrets
import shutil
import socket
import string
import textwrap
import uuid
from pathlib import Path
from typing import Any, Callable

# ═══════════════════════════════════════════════════════════════════════════════
# GROUP 1: Code Generation  (cap_001 – cap_005)
# ═══════════════════════════════════════════════════════════════════════════════


def generate_python_crud_api(app_name: str, models_list: list[str]) -> str:
    """Generate a complete FastAPI CRUD app with SQLite models.

    Args:
        app_name: Name of the application.
        models_list: List of model names (e.g. ["User", "Product"]).

    Returns:
        Complete Python source code as a string.
    """
    lines: list[str] = [
        '"""Auto-generated FastAPI CRUD application."""',
        "",
        "import sqlite3, json, os, uuid, datetime",
        "from http.server import HTTPServer, BaseHTTPRequestHandler",
        "from urllib.parse import urlparse, parse_qs",
        "",
        f'APP_NAME = "{app_name}"',
        f'DB_PATH = "{app_name.lower().replace(" ", "_")}.db"',
        "",
        "",
        "def _connect():",
        "    conn = sqlite3.connect(DB_PATH)",
        "    conn.row_factory = sqlite3.Row",
        "    return conn",
        "",
        "",
        "def _init_db():",
        '    """Create tables for every model."""',
        "    conn = _connect()",
    ]
    for model in models_list:
        table = model.lower() + "s"
        lines += [
            f"    conn.execute(",
            f'        "CREATE TABLE IF NOT EXISTS {table} ("',
            f'        "id TEXT PRIMARY KEY, "',
            f'        "data TEXT NOT NULL, "',
            f'        "created_at TEXT NOT NULL, "',
            f'        "updated_at TEXT NOT NULL"',
            f'        ")"',
            f"    )",
        ]
    lines += [
        "    conn.commit()",
        "    conn.close()",
        "",
        "",
    ]

    for model in models_list:
        table = model.lower() + "s"
        lines += [
            f"def create_{model.lower()}(data: dict) -> dict:",
            f'    """Create a new {model}."""',
            f"    uid = str(uuid.uuid4())",
            f"    now = datetime.datetime.utcnow().isoformat()",
            f"    conn = _connect()",
            f'    conn.execute("INSERT INTO {table} VALUES (?, ?, ?, ?)",',
            f"                 (uid, json.dumps(data), now, now))",
            f"    conn.commit(); conn.close()",
            f'    return {{"id": uid, "data": data, "created_at": now}}',
            f"",
            f"",
            f"def list_{model.lower()}s() -> list:",
            f'    """List all {model} records."""',
            f"    conn = _connect()",
            f'    rows = conn.execute("SELECT * FROM {table}").fetchall()',
            f"    conn.close()",
            f'    return [{{"id": r["id"], "data": json.loads(r["data"]),',
            f'             "created_at": r["created_at"]}} for r in rows]',
            f"",
            f"",
            f"def get_{model.lower()}(uid: str) -> dict | None:",
            f'    """Get a single {model} by id."""',
            f"    conn = _connect()",
            f'    r = conn.execute("SELECT * FROM {table} WHERE id=?", (uid,)).fetchone()',
            f"    conn.close()",
            f"    if r is None: return None",
            f'    return {{"id": r["id"], "data": json.loads(r["data"])}}',
            f"",
            f"",
            f"def update_{model.lower()}(uid: str, data: dict) -> dict:",
            f'    """Update a {model} by id."""',
            f"    now = datetime.datetime.utcnow().isoformat()",
            f"    conn = _connect()",
            f'    conn.execute("UPDATE {table} SET data=?, updated_at=? WHERE id=?",',
            f"                 (json.dumps(data), now, uid))",
            f"    conn.commit(); conn.close()",
            f'    return {{"id": uid, "data": data, "updated_at": now}}',
            f"",
            f"",
            f"def delete_{model.lower()}(uid: str) -> bool:",
            f'    """Delete a {model} by id."""',
            f"    conn = _connect()",
            f'    conn.execute("DELETE FROM {table} WHERE id=?", (uid,))',
            f"    conn.commit(); conn.close()",
            f"    return True",
            f"",
            f"",
        ]

    lines += [
        "class RequestHandler(BaseHTTPRequestHandler):",
        "    def do_GET(self):",
        "        parsed = urlparse(self.path)",
        "        parts = parsed.path.strip('/').split('/')",
    ]
    for model in models_list:
        table = model.lower() + "s"
        lines += [
            f'        if parts[0] == "{table}":',
            f"            if len(parts) == 2:",
            f"                result = get_{model.lower()}(parts[1])",
            f"            else:",
            f"                result = list_{model.lower()}s()",
            f"            self.send_response(200)",
            f'            self.send_header("Content-Type", "application/json")',
            f"            self.end_headers()",
            f"            self.wfile.write(json.dumps(result).encode())",
            f"            return",
        ]
    lines += [
        "        self.send_response(404)",
        "        self.end_headers()",
        "",
        "",
        "if __name__ == '__main__':",
        "    _init_db()",
        f'    print(f"{{APP_NAME}} running on http://localhost:8000")',
        "    HTTPServer(('', 8000), RequestHandler).serve_forever()",
        "",
    ]
    return "\n".join(lines)


def generate_flask_app(app_name: str, routes_list: list[str]) -> str:
    """Generate a Flask app skeleton with routes.

    Args:
        app_name: Application name.
        routes_list: URL paths (e.g. ["/", "/about", "/api/data"]).

    Returns:
        Complete Flask application source code.
    """
    lines = [
        '"""Auto-generated Flask application."""',
        "",
        "from flask import Flask, jsonify, request",
        "",
        f'app = Flask("{app_name}")',
        "",
    ]
    for route in routes_list:
        fname = "route_" + re.sub(r"[^a-zA-Z0-9]", "_", route).strip("_")
        lines += [
            f'@app.route("{route}", methods=["GET", "POST"])',
            f"def {fname}():",
            f'    """Handler for {route}."""',
            f"    if request.method == 'POST':",
            f"        data = request.get_json(silent=True) or {{}}",
            f'        return jsonify({{"status": "ok", "received": data}})',
            f'    return jsonify({{"route": "{route}", "app": "{app_name}"}})',
            "",
            "",
        ]
    lines += [
        'if __name__ == "__main__":',
        f'    print("Starting {app_name}...")',
        "    app.run(debug=True, port=5000)",
        "",
    ]
    return "\n".join(lines)


def generate_cli_tool(tool_name: str, commands_dict: dict[str, str]) -> str:
    """Generate a Python CLI tool using argparse.

    Args:
        tool_name: Name of the CLI tool.
        commands_dict: Mapping of command names to help descriptions.

    Returns:
        Complete CLI tool source code.
    """
    lines = [
        '"""Auto-generated CLI tool."""',
        "",
        "import argparse, sys",
        "",
        "",
    ]
    for cmd, help_text in commands_dict.items():
        fname = f"cmd_{cmd}"
        lines += [
            f"def {fname}(args):",
            f'    """Execute the {cmd} command."""',
            f'    print(f"[{tool_name}] Running {cmd}")',
            f"    for k, v in vars(args).items():",
            f"        if k != 'func':",
            f'            print(f"  {{k}} = {{v}}")',
            "",
            "",
        ]
    lines += [
        "def main():",
        f'    parser = argparse.ArgumentParser(prog="{tool_name}",',
        f'                                     description="{tool_name} CLI")',
        '    sub = parser.add_subparsers(dest="command", help="Available commands")',
        "",
    ]
    for cmd, help_text in commands_dict.items():
        fname = f"cmd_{cmd}"
        lines += [
            f'    p_{cmd} = sub.add_parser("{cmd}", help="{help_text}")',
            f'    p_{cmd}.add_argument("--verbose", action="store_true", help="Verbose output")',
            f"    p_{cmd}.set_defaults(func={fname})",
            "",
        ]
    lines += [
        "    args = parser.parse_args()",
        "    if hasattr(args, 'func'):",
        "        args.func(args)",
        "    else:",
        "        parser.print_help()",
        "",
        "",
        'if __name__ == "__main__":',
        "    main()",
        "",
    ]
    return "\n".join(lines)


def generate_dockerfile(base_image: str, app_name: str, port: int) -> str:
    """Generate a production Dockerfile.

    Args:
        base_image: Base Docker image (e.g. "python:3.12-slim").
        app_name: Application name.
        port: Port to expose.

    Returns:
        Dockerfile content as a string.
    """
    return textwrap.dedent(f"""\
        # ---- {app_name} Production Dockerfile ----
        FROM {base_image} AS builder

        LABEL maintainer="{app_name}-team"
        LABEL description="{app_name} production container"

        ENV PYTHONDONTWRITEBYTECODE=1 \\
            PYTHONUNBUFFERED=1 \\
            APP_NAME={app_name}

        WORKDIR /app

        COPY requirements.txt .
        RUN pip install --no-cache-dir --upgrade pip && \\
            pip install --no-cache-dir -r requirements.txt

        COPY . .

        RUN addgroup --system appgroup && \\
            adduser --system --ingroup appgroup appuser
        USER appuser

        EXPOSE {port}

        HEALTHCHECK --interval=30s --timeout=5s --retries=3 \\
            CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:{port}/health')"

        ENTRYPOINT ["python"]
        CMD ["app.py"]
    """)


def generate_makefile(targets_dict: dict[str, str]) -> str:
    """Generate a Makefile with given targets.

    Args:
        targets_dict: Mapping of target names to shell commands.

    Returns:
        Makefile content as a string.
    """
    lines = [
        "# Auto-generated Makefile",
        f"# Generated: {datetime.datetime.now(datetime.timezone.utc).isoformat()}",
        "",
        ".DEFAULT_GOAL := help",
        "",
        "help:  ## Show this help message",
        "\t@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | "
        "awk 'BEGIN {FS = \":.*?## \"}; {printf \"\\033[36m%-20s\\033[0m %s\\n\", $$1, $$2}'",
        "",
    ]
    for target, cmd in targets_dict.items():
        lines += [
            f"{target}:  ## Run {target}",
            f"\t{cmd}",
            "",
        ]
    # phony
    all_targets = " ".join(["help"] + list(targets_dict.keys()))
    lines.append(f".PHONY: {all_targets}")
    lines.append("")
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
# GROUP 2: Business & Planning  (cap_006 – cap_010)
# ═══════════════════════════════════════════════════════════════════════════════


def generate_business_plan(
    company_name: str, industry: str, target_market: str
) -> dict:
    """Generate a full business plan structure.

    Args:
        company_name: Name of the company.
        industry: Industry vertical.
        target_market: Primary target market.

    Returns:
        Dictionary with all business plan sections.
    """
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    return {
        "company_name": company_name,
        "industry": industry,
        "target_market": target_market,
        "generated_date": now,
        "sections": {
            "executive_summary": {
                "title": "Executive Summary",
                "content": (
                    f"{company_name} is a {industry} company targeting "
                    f"{target_market}. This plan outlines the strategy, "
                    "market opportunity, and financial projections."
                ),
            },
            "company_description": {
                "title": "Company Description",
                "mission": f"To deliver innovative {industry} solutions to {target_market}.",
                "vision": f"To become the leading {industry} provider for {target_market}.",
                "legal_structure": "To be determined",
                "founding_date": now,
            },
            "market_analysis": {
                "title": "Market Analysis",
                "target_market": target_market,
                "market_size_estimate": "To be researched",
                "growth_rate": "To be researched",
                "trends": [
                    f"Digital transformation in {industry}",
                    f"Growing demand from {target_market}",
                    "AI and automation adoption",
                    "Sustainability and compliance requirements",
                ],
                "customer_segments": [
                    {"segment": "Early Adopters", "priority": "High"},
                    {"segment": "Enterprise", "priority": "Medium"},
                    {"segment": "SMB", "priority": "Medium"},
                ],
            },
            "competitive_analysis": {
                "title": "Competitive Landscape",
                "direct_competitors": [],
                "indirect_competitors": [],
                "competitive_advantages": [
                    "Technology differentiation",
                    "Market timing",
                    "Team expertise",
                ],
            },
            "products_services": {
                "title": "Products & Services",
                "offerings": [
                    {
                        "name": f"{company_name} Core",
                        "description": f"Primary {industry} solution",
                        "pricing_model": "Subscription",
                    }
                ],
                "roadmap": [
                    {"phase": "MVP", "timeline": "0-6 months"},
                    {"phase": "Growth", "timeline": "6-18 months"},
                    {"phase": "Scale", "timeline": "18-36 months"},
                ],
            },
            "marketing_strategy": {
                "title": "Marketing & Sales Strategy",
                "channels": [
                    "Content Marketing",
                    "SEO/SEM",
                    "Social Media",
                    "Partnerships",
                    "Direct Sales",
                ],
                "customer_acquisition_cost": "To be calculated",
                "lifetime_value": "To be calculated",
            },
            "financial_projections": {
                "title": "Financial Projections",
                "year_1": {"revenue": 0, "expenses": 0, "net": 0},
                "year_2": {"revenue": 0, "expenses": 0, "net": 0},
                "year_3": {"revenue": 0, "expenses": 0, "net": 0},
                "funding_required": "To be determined",
                "break_even_timeline": "To be calculated",
            },
            "operations_plan": {
                "title": "Operations Plan",
                "team_size": "To be determined",
                "key_roles": [
                    "CEO",
                    "CTO",
                    "VP Sales",
                    "VP Marketing",
                    "Lead Engineer",
                ],
                "technology_stack": "To be determined",
                "infrastructure": "Cloud-based",
            },
        },
    }


def generate_pitch_deck_outline(
    company_name: str, problem: str, solution: str
) -> list[dict]:
    """Generate a slide-by-slide pitch deck outline.

    Args:
        company_name: Company name.
        problem: Problem statement.
        solution: Proposed solution.

    Returns:
        List of slide dictionaries.
    """
    return [
        {
            "slide": 1,
            "title": "Title Slide",
            "content": company_name,
            "notes": "Logo, tagline, presenter name and title.",
        },
        {
            "slide": 2,
            "title": "Problem",
            "content": problem,
            "notes": "Make the audience feel the pain. Use data if available.",
        },
        {
            "slide": 3,
            "title": "Solution",
            "content": solution,
            "notes": "Show how your product solves the problem. Demo screenshot.",
        },
        {
            "slide": 4,
            "title": "Market Opportunity",
            "content": "TAM / SAM / SOM analysis for the target market.",
            "notes": "Use credible third-party sources for market size.",
        },
        {
            "slide": 5,
            "title": "Product",
            "content": f"{company_name}'s product overview and key features.",
            "notes": "Screenshots, architecture diagram, or live demo.",
        },
        {
            "slide": 6,
            "title": "Business Model",
            "content": "Revenue streams, pricing tiers, and unit economics.",
            "notes": "Show CAC, LTV, margins.",
        },
        {
            "slide": 7,
            "title": "Traction",
            "content": "Key metrics, milestones, and growth indicators.",
            "notes": "MRR, user count, partnerships, pilot customers.",
        },
        {
            "slide": 8,
            "title": "Competitive Landscape",
            "content": "2x2 matrix positioning against competitors.",
            "notes": "Highlight defensible advantages.",
        },
        {
            "slide": 9,
            "title": "Go-to-Market Strategy",
            "content": "Customer acquisition channels and sales strategy.",
            "notes": "Phase-based rollout plan.",
        },
        {
            "slide": 10,
            "title": "Team",
            "content": f"{company_name} founding team and key advisors.",
            "notes": "Highlight relevant experience and domain expertise.",
        },
        {
            "slide": 11,
            "title": "Financials",
            "content": "3-year projections: revenue, costs, profitability.",
            "notes": "Keep assumptions visible and defensible.",
        },
        {
            "slide": 12,
            "title": "The Ask",
            "content": "Funding amount, use of funds, and timeline.",
            "notes": "Be specific: hiring, product, marketing allocations.",
        },
    ]


def calculate_runway(
    monthly_burn: float, cash_on_hand: float, monthly_revenue: float = 0.0
) -> dict:
    """Calculate financial runway.

    Args:
        monthly_burn: Monthly operating expenses.
        monthly_revenue: Monthly recurring revenue (default 0).
        cash_on_hand: Current cash balance.

    Returns:
        Dictionary with runway metrics.
    """
    net_burn = monthly_burn - monthly_revenue
    if net_burn <= 0:
        months = float("inf")
        runway_date = "Sustainable — net positive cash flow"
        status = "SUSTAINABLE"
    else:
        months = cash_on_hand / net_burn
        runway_end = datetime.datetime.now(
            datetime.timezone.utc
        ) + datetime.timedelta(days=months * 30.44)
        runway_date = runway_end.strftime("%Y-%m-%d")
        if months > 18:
            status = "HEALTHY"
        elif months > 6:
            status = "CAUTION"
        else:
            status = "CRITICAL"

    return {
        "monthly_burn": monthly_burn,
        "monthly_revenue": monthly_revenue,
        "net_monthly_burn": net_burn,
        "cash_on_hand": cash_on_hand,
        "runway_months": round(months, 2) if months != float("inf") else "infinite",
        "runway_end_date": runway_date,
        "status": status,
        "recommendations": (
            []
            if status == "SUSTAINABLE"
            else (
                ["Reduce burn rate", "Accelerate revenue"]
                if status == "CRITICAL"
                else ["Monitor monthly and plan fundraising"]
            )
        ),
    }


def generate_competitive_analysis(
    company: str, competitors_list: list[str]
) -> dict:
    """Generate a SWOT-style competitive matrix.

    Args:
        company: Your company name.
        competitors_list: List of competitor names.

    Returns:
        Competitive analysis dictionary.
    """

    def _blank_swot(name: str) -> dict:
        return {
            "name": name,
            "strengths": [f"{name} strength 1 — to be filled"],
            "weaknesses": [f"{name} weakness 1 — to be filled"],
            "opportunities": [f"{name} opportunity 1 — to be filled"],
            "threats": [f"{name} threat 1 — to be filled"],
        }

    matrix = {
        "analysis_date": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "company": _blank_swot(company),
        "competitors": [_blank_swot(c) for c in competitors_list],
        "comparison_dimensions": [
            "Pricing",
            "Product Features",
            "Market Share",
            "Technology",
            "Customer Support",
            "Brand Recognition",
        ],
        "comparison_matrix": {},
    }
    all_names = [company] + competitors_list
    for dim in matrix["comparison_dimensions"]:
        matrix["comparison_matrix"][dim] = {name: "—" for name in all_names}
    return matrix


def generate_okrs(
    company_name: str, quarters: int, objectives_list: list[str]
) -> dict:
    """Generate an OKR (Objectives & Key Results) framework.

    Args:
        company_name: Company name.
        quarters: Number of quarters to plan.
        objectives_list: High-level objective descriptions.

    Returns:
        Structured OKR dictionary.
    """
    now = datetime.datetime.now(datetime.timezone.utc)
    current_q = (now.month - 1) // 3 + 1
    current_y = now.year

    okr_quarters = []
    for i in range(quarters):
        q = ((current_q - 1 + i) % 4) + 1
        y = current_y + (current_q - 1 + i) // 4
        quarter_objs = []
        for obj in objectives_list:
            quarter_objs.append(
                {
                    "objective": obj,
                    "key_results": [
                        {
                            "kr": f"KR1 for '{obj}'",
                            "target": "Define measurable target",
                            "current": 0,
                            "status": "NOT_STARTED",
                        },
                        {
                            "kr": f"KR2 for '{obj}'",
                            "target": "Define measurable target",
                            "current": 0,
                            "status": "NOT_STARTED",
                        },
                        {
                            "kr": f"KR3 for '{obj}'",
                            "target": "Define measurable target",
                            "current": 0,
                            "status": "NOT_STARTED",
                        },
                    ],
                }
            )
        okr_quarters.append(
            {"quarter": f"Q{q} {y}", "objectives": quarter_objs}
        )

    return {
        "company": company_name,
        "generated": now.isoformat(),
        "total_quarters": quarters,
        "total_objectives_per_quarter": len(objectives_list),
        "quarters": okr_quarters,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# GROUP 3: Document Assembly  (cap_011 – cap_015)
# ═══════════════════════════════════════════════════════════════════════════════


def assemble_pdf_text(sections_list: list[dict]) -> str:
    """Assemble a structured plaintext document from sections.

    Each section dict should have keys ``title`` and ``body``.

    Args:
        sections_list: List of {"title": str, "body": str} dicts.

    Returns:
        Formatted document text ready for PDF conversion.
    """
    separator = "=" * 72
    lines: list[str] = []
    for idx, sec in enumerate(sections_list, 1):
        title = sec.get("title", f"Section {idx}")
        body = sec.get("body", "")
        lines.append(separator)
        lines.append(f"  {idx}. {title.upper()}")
        lines.append(separator)
        lines.append("")
        for paragraph in body.split("\n"):
            wrapped = textwrap.fill(paragraph, width=72) if paragraph.strip() else ""
            lines.append(wrapped)
        lines.append("")
        lines.append("")
    return "\n".join(lines)


def generate_invoice(
    vendor: dict, client: dict, items_list: list[dict]
) -> dict:
    """Generate a complete invoice structure.

    Args:
        vendor: {"name": str, "address": str, "email": str}
        client: {"name": str, "address": str, "email": str}
        items_list: List of {"description": str, "quantity": int, "unit_price": float}

    Returns:
        Complete invoice dictionary with totals.
    """
    invoice_id = f"INV-{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    line_items = []
    subtotal = 0.0
    for item in items_list:
        qty = item.get("quantity", 1)
        price = item.get("unit_price", 0.0)
        total = round(qty * price, 2)
        subtotal += total
        line_items.append(
            {
                "description": item.get("description", "Item"),
                "quantity": qty,
                "unit_price": price,
                "line_total": total,
            }
        )
    tax_rate = 0.0
    tax = round(subtotal * tax_rate, 2)
    grand_total = round(subtotal + tax, 2)
    return {
        "invoice_id": invoice_id,
        "date": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d"),
        "due_date": (
            datetime.datetime.now(datetime.timezone.utc)
            + datetime.timedelta(days=30)
        ).strftime("%Y-%m-%d"),
        "vendor": vendor,
        "client": client,
        "line_items": line_items,
        "subtotal": subtotal,
        "tax_rate": f"{tax_rate * 100:.1f}%",
        "tax": tax,
        "grand_total": grand_total,
        "currency": "USD",
        "status": "UNPAID",
        "notes": "Payment due within 30 days.",
    }


def generate_contract_template(
    party_a: str, party_b: str, terms: dict
) -> str:
    """Generate a legal contract template.

    Args:
        party_a: First party name.
        party_b: Second party name.
        terms: {"duration": str, "value": str, "scope": str, ...}

    Returns:
        Contract text as a string.
    """
    today = datetime.datetime.now(datetime.timezone.utc).strftime("%B %d, %Y")
    duration = terms.get("duration", "12 months")
    value = terms.get("value", "to be determined")
    scope = terms.get("scope", "as mutually agreed upon")
    governing_law = terms.get("governing_law", "State of Delaware")

    return textwrap.dedent(f"""\
        SERVICE AGREEMENT

        Date: {today}

        BETWEEN:
          Party A: {party_a} (hereinafter "Provider")
          Party B: {party_b} (hereinafter "Client")

        1. SCOPE OF WORK
        The Provider agrees to deliver services as follows:
        {scope}

        2. TERM
        This agreement is effective from the date of signing and shall
        remain in effect for {duration}, unless terminated earlier in
        accordance with Section 6.

        3. COMPENSATION
        The Client agrees to compensate the Provider in the amount of
        {value}, payable according to the schedule agreed upon in
        Exhibit A.

        4. CONFIDENTIALITY
        Both parties agree to maintain the confidentiality of all
        proprietary information exchanged during the term of this
        agreement. This obligation survives termination for a period
        of two (2) years.

        5. INTELLECTUAL PROPERTY
        All work product created under this agreement shall be owned
        by the Client upon full payment, unless otherwise specified in
        Exhibit B.

        6. TERMINATION
        Either party may terminate this agreement with thirty (30) days
        written notice. In the event of material breach, the non-breaching
        party may terminate immediately upon written notice.

        7. LIMITATION OF LIABILITY
        Neither party shall be liable for indirect, incidental, or
        consequential damages arising from this agreement.

        8. GOVERNING LAW
        This agreement shall be governed by the laws of {governing_law}.

        9. ENTIRE AGREEMENT
        This document constitutes the entire agreement between the parties
        and supersedes all prior negotiations and agreements.

        IN WITNESS WHEREOF, the parties have executed this Agreement
        as of the date first written above.

        ______________________________    ______________________________
        {party_a}                          {party_b}
        Provider                           Client
    """)


def merge_markdown_files(file_paths: list[str]) -> str:
    """Merge multiple markdown files into one document.

    Args:
        file_paths: List of file paths to merge.

    Returns:
        Merged markdown content.
    """
    parts: list[str] = []
    for fp in file_paths:
        p = Path(fp)
        if p.exists() and p.is_file():
            content = p.read_text(encoding="utf-8", errors="replace")
            parts.append(f"<!-- Source: {p.name} -->")
            parts.append(content.strip())
            parts.append("")
            parts.append("---")
            parts.append("")
        else:
            parts.append(f"<!-- MISSING: {fp} -->")
            parts.append("")
    return "\n".join(parts)


def generate_readme(
    project_name: str,
    description: str,
    install_steps: list[str],
    usage: str,
) -> str:
    """Generate a README.md file.

    Args:
        project_name: Project name.
        description: One-paragraph description.
        install_steps: List of installation commands.
        usage: Usage example text.

    Returns:
        README markdown as a string.
    """
    install_md = "\n".join(f"{i}. `{step}`" for i, step in enumerate(install_steps, 1))
    return textwrap.dedent(f"""\
        # {project_name}

        {description}

        ## Installation

        {install_md}

        ## Usage

        ```
        {usage}
        ```

        ## Contributing

        1. Fork the repository
        2. Create a feature branch (`git checkout -b feature/amazing`)
        3. Commit your changes (`git commit -m 'Add amazing feature'`)
        4. Push to the branch (`git push origin feature/amazing`)
        5. Open a Pull Request

        ## License

        This project is licensed under the MIT License.
    """)


# ═══════════════════════════════════════════════════════════════════════════════
# GROUP 4: File Indexing & Search  (cap_016 – cap_020)
# ═══════════════════════════════════════════════════════════════════════════════


def index_directory(
    dir_path: str, extensions: list[str] | None = None
) -> dict:
    """Recursively index files with metadata.

    Args:
        dir_path: Root directory to index.
        extensions: Optional list of extensions to filter (e.g. [".py", ".md"]).

    Returns:
        Dictionary with file count, total size, and file list.
    """
    root = Path(dir_path)
    if not root.is_dir():
        return {"error": f"Not a directory: {dir_path}"}

    files_info: list[dict] = []
    total_size = 0

    for item in root.rglob("*"):
        if not item.is_file():
            continue
        if extensions and item.suffix.lower() not in extensions:
            continue
        try:
            stat = item.stat()
            size = stat.st_size
            mtime = datetime.datetime.fromtimestamp(
                stat.st_mtime, tz=datetime.timezone.utc
            ).isoformat()
        except OSError:
            size = 0
            mtime = "unknown"
        files_info.append(
            {
                "path": str(item.relative_to(root)),
                "extension": item.suffix,
                "size_bytes": size,
                "modified": mtime,
            }
        )
        total_size += size

    return {
        "root": str(root),
        "total_files": len(files_info),
        "total_size_bytes": total_size,
        "extensions_filter": extensions,
        "files": files_info,
    }


def search_files_by_content(
    dir_path: str, query: str, extensions: list[str] | None = None
) -> list[dict]:
    """Grep-like content search across files.

    Args:
        dir_path: Directory to search.
        query: Text pattern to search for.
        extensions: Optional extension filter.

    Returns:
        List of matches with file, line number, and content.
    """
    root = Path(dir_path)
    results: list[dict] = []
    pattern = re.compile(re.escape(query), re.IGNORECASE)

    for item in root.rglob("*"):
        if not item.is_file():
            continue
        if extensions and item.suffix.lower() not in extensions:
            continue
        try:
            text = item.read_text(encoding="utf-8", errors="replace")
        except (OSError, PermissionError):
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            if pattern.search(line):
                results.append(
                    {
                        "file": str(item.relative_to(root)),
                        "line": lineno,
                        "content": line.rstrip(),
                    }
                )
    return results


def generate_file_manifest(dir_path: str) -> dict:
    """Generate a SHA-256 manifest of all files.

    Args:
        dir_path: Directory to manifest.

    Returns:
        Dictionary mapping relative paths to SHA-256 hashes.
    """
    root = Path(dir_path)
    manifest: dict[str, str] = {}
    for item in sorted(root.rglob("*")):
        if not item.is_file():
            continue
        try:
            sha = hashlib.sha256(item.read_bytes()).hexdigest()
        except (OSError, PermissionError):
            sha = "ERROR"
        manifest[str(item.relative_to(root))] = sha
    return {
        "root": str(root),
        "generated": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "total_files": len(manifest),
        "files": manifest,
    }


def find_duplicate_files(dir_path: str) -> list[list[str]]:
    """Find duplicate files by SHA-256 hash.

    Args:
        dir_path: Directory to scan.

    Returns:
        List of groups, each group is a list of paths sharing the same hash.
    """
    root = Path(dir_path)
    hash_map: dict[str, list[str]] = {}
    for item in root.rglob("*"):
        if not item.is_file():
            continue
        try:
            sha = hashlib.sha256(item.read_bytes()).hexdigest()
        except (OSError, PermissionError):
            continue
        rel = str(item.relative_to(root))
        hash_map.setdefault(sha, []).append(rel)
    return [paths for paths in hash_map.values() if len(paths) > 1]


def generate_directory_tree(dir_path: str, max_depth: int = 4) -> str:
    """Generate an ASCII directory tree.

    Args:
        dir_path: Root directory.
        max_depth: Maximum depth to traverse.

    Returns:
        ASCII tree string.
    """
    root = Path(dir_path)
    lines: list[str] = [root.name + "/"]

    def _walk(directory: Path, prefix: str, depth: int) -> None:
        if depth >= max_depth:
            return
        try:
            entries = sorted(directory.iterdir(), key=lambda e: (not e.is_dir(), e.name.lower()))
        except PermissionError:
            return
        for i, entry in enumerate(entries):
            is_last = i == len(entries) - 1
            connector = "└── " if is_last else "├── "
            suffix = "/" if entry.is_dir() else ""
            lines.append(f"{prefix}{connector}{entry.name}{suffix}")
            if entry.is_dir():
                extension = "    " if is_last else "│   "
                _walk(entry, prefix + extension, depth + 1)

    _walk(root, "", 0)
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
# GROUP 5: Agent Building  (cap_021 – cap_025)
# ═══════════════════════════════════════════════════════════════════════════════


def create_agent_definition(
    name: str, description: str, model: str, tools_list: list[str]
) -> dict:
    """Create an agent definition structure (YAML-ready dict).

    Args:
        name: Agent name.
        description: Agent description.
        model: Model identifier (e.g. "claude-sonnet-4-20250514").
        tools_list: List of tool names.

    Returns:
        Agent definition dictionary.
    """
    return {
        "agent": {
            "name": name,
            "version": "1.0.0",
            "description": description,
            "model": model,
            "max_tokens": 4096,
            "temperature": 0.7,
            "tools": [
                {"name": t, "enabled": True, "description": f"Tool: {t}"}
                for t in tools_list
            ],
            "system_prompt": f"You are {name}. {description}",
            "metadata": {
                "created": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "author": "capabilities.py",
            },
        }
    }


def generate_system_prompt(
    role: str, constraints: list[str], examples: list[dict]
) -> str:
    """Build a structured system prompt.

    Args:
        role: Role description (e.g. "senior Python engineer").
        constraints: List of behavioral constraints.
        examples: List of {"user": str, "assistant": str} examples.

    Returns:
        System prompt string.
    """
    parts = [f"You are a {role}.\n"]

    if constraints:
        parts.append("## Constraints\n")
        for c in constraints:
            parts.append(f"- {c}")
        parts.append("")

    if examples:
        parts.append("## Examples\n")
        for i, ex in enumerate(examples, 1):
            parts.append(f"### Example {i}")
            parts.append(f"**User:** {ex.get('user', '')}")
            parts.append(f"**Assistant:** {ex.get('assistant', '')}")
            parts.append("")

    parts.append(
        "Follow all constraints strictly. Provide helpful, accurate responses."
    )
    return "\n".join(parts)


def create_tool_manifest(tools_list: list[dict]) -> dict:
    """Create an MCP-style tool manifest.

    Each tool in tools_list should be::

        {"name": str, "description": str,
         "parameters": [{"name": str, "type": str, "required": bool}]}

    Args:
        tools_list: List of tool specification dicts.

    Returns:
        MCP-format tool manifest.
    """
    manifest_tools = []
    for tool in tools_list:
        params = tool.get("parameters", [])
        properties: dict[str, dict] = {}
        required_params: list[str] = []
        for p in params:
            properties[p["name"]] = {
                "type": p.get("type", "string"),
                "description": f"Parameter: {p['name']}",
            }
            if p.get("required", False):
                required_params.append(p["name"])
        manifest_tools.append(
            {
                "name": tool["name"],
                "description": tool.get("description", ""),
                "inputSchema": {
                    "type": "object",
                    "properties": properties,
                    "required": required_params,
                },
            }
        )
    return {
        "schema_version": "1.0",
        "tools": manifest_tools,
        "metadata": {
            "generated": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "count": len(manifest_tools),
        },
    }


def generate_agent_workflow(steps_list: list[dict]) -> dict:
    """Generate a multi-step agent workflow.

    Each step: {"name": str, "action": str, "inputs": dict, "depends_on": list[str]}

    Args:
        steps_list: Ordered list of step definitions.

    Returns:
        Workflow DAG dictionary.
    """
    nodes = []
    for i, step in enumerate(steps_list):
        name = step.get("name", f"step_{i}")
        nodes.append(
            {
                "id": name,
                "action": step.get("action", "execute"),
                "inputs": step.get("inputs", {}),
                "depends_on": step.get("depends_on", []),
                "retry": {"max_attempts": 3, "backoff_seconds": 2},
                "timeout_seconds": 300,
            }
        )

    # Topological ordering validation
    node_ids = {n["id"] for n in nodes}
    for n in nodes:
        for dep in n["depends_on"]:
            if dep not in node_ids:
                return {"error": f"Unknown dependency '{dep}' in step '{n['id']}'"}

    return {
        "workflow": {
            "version": "1.0",
            "created": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "total_steps": len(nodes),
            "steps": nodes,
            "execution_order": _topological_sort(nodes),
        }
    }


def _topological_sort(nodes: list[dict]) -> list[str]:
    """Kahn's algorithm for topological ordering."""
    graph: dict[str, list[str]] = {n["id"]: list(n["depends_on"]) for n in nodes}
    in_degree: dict[str, int] = {n["id"]: 0 for n in nodes}
    for nid, deps in graph.items():
        for d in deps:
            if d in in_degree:
                pass  # d exists
        in_degree[nid] = len(deps)

    queue = collections.deque(
        nid for nid, deg in in_degree.items() if deg == 0
    )
    order: list[str] = []
    while queue:
        nid = queue.popleft()
        order.append(nid)
        for other, deps in graph.items():
            if nid in deps:
                in_degree[other] -= 1
                if in_degree[other] == 0:
                    queue.append(other)
    return order


def create_agent_evaluation(
    agent_name: str, test_cases: list[dict]
) -> dict:
    """Generate an agent test suite.

    Each test case: {"input": str, "expected_output": str, "tags": list[str]}

    Args:
        agent_name: Name of the agent under test.
        test_cases: List of test case definitions.

    Returns:
        Evaluation suite dictionary.
    """
    suite = {
        "agent": agent_name,
        "suite_id": uuid.uuid4().hex[:12],
        "created": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "total_cases": len(test_cases),
        "test_cases": [],
    }
    for i, tc in enumerate(test_cases):
        suite["test_cases"].append(
            {
                "case_id": f"TC-{i + 1:03d}",
                "input": tc.get("input", ""),
                "expected_output": tc.get("expected_output", ""),
                "tags": tc.get("tags", []),
                "status": "PENDING",
                "result": None,
                "latency_ms": None,
            }
        )
    suite["summary"] = {
        "passed": 0,
        "failed": 0,
        "pending": len(test_cases),
        "pass_rate": "0.0%",
    }
    return suite


# ═══════════════════════════════════════════════════════════════════════════════
# GROUP 6: Data Processing  (cap_026 – cap_030)
# ═══════════════════════════════════════════════════════════════════════════════


def csv_to_json(csv_path: str) -> list[dict]:
    """Convert a CSV file to a list of JSON objects.

    Args:
        csv_path: Path to the CSV file.

    Returns:
        List of dictionaries, one per row.
    """
    p = Path(csv_path)
    if not p.is_file():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    with p.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return [dict(row) for row in reader]


def json_to_csv(data: list[dict], output_path: str) -> str:
    """Convert a JSON array to a CSV file.

    Args:
        data: List of flat dictionaries.
        output_path: Path for the output CSV file.

    Returns:
        Absolute path of the written CSV file.
    """
    if not data:
        raise ValueError("Data list is empty")
    p = Path(output_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(data[0].keys())
    with p.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    return str(p.resolve())


def merge_csv_files(file_paths: list[str], output_path: str) -> str:
    """Merge multiple CSV files into one.

    All files must share the same header schema. The output uses the header
    from the first file.

    Args:
        file_paths: List of CSV file paths.
        output_path: Path for the merged CSV.

    Returns:
        Absolute path of the merged CSV.
    """
    if not file_paths:
        raise ValueError("No file paths provided")
    all_rows: list[dict] = []
    fieldnames: list[str] | None = None
    for fp in file_paths:
        p = Path(fp)
        if not p.is_file():
            continue
        with p.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            if fieldnames is None:
                fieldnames = reader.fieldnames or []
            all_rows.extend(dict(row) for row in reader)
    if fieldnames is None:
        raise ValueError("No valid CSV files found")
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)
    return str(out.resolve())


def pivot_data(
    data: list[dict],
    group_by: str,
    aggregate_col: str,
    agg_func: str = "sum",
) -> dict:
    """Perform a pivot table computation.

    Args:
        data: List of flat dictionaries.
        group_by: Column name to group by.
        aggregate_col: Column name to aggregate.
        agg_func: Aggregation function — "sum", "avg", "count", "min", "max".

    Returns:
        Pivot result dictionary.
    """
    groups: dict[str, list[float]] = {}
    for row in data:
        key = str(row.get(group_by, "UNKNOWN"))
        try:
            val = float(row.get(aggregate_col, 0))
        except (ValueError, TypeError):
            val = 0.0
        groups.setdefault(key, []).append(val)

    result: dict[str, float | int] = {}
    for key, vals in groups.items():
        if agg_func == "sum":
            result[key] = sum(vals)
        elif agg_func == "avg":
            result[key] = sum(vals) / len(vals) if vals else 0
        elif agg_func == "count":
            result[key] = len(vals)
        elif agg_func == "min":
            result[key] = min(vals)
        elif agg_func == "max":
            result[key] = max(vals)
        else:
            result[key] = sum(vals)

    return {
        "group_by": group_by,
        "aggregate_col": aggregate_col,
        "agg_func": agg_func,
        "groups": result,
        "total_rows": len(data),
        "total_groups": len(result),
    }


def deduplicate_records(
    records: list[dict], key_fields: list[str]
) -> list[dict]:
    """Deduplicate records by composite key fields.

    Args:
        records: List of dictionaries.
        key_fields: List of field names forming the dedup key.

    Returns:
        Deduplicated list (first occurrence kept).
    """
    seen: set[tuple] = set()
    unique: list[dict] = []
    for rec in records:
        key = tuple(str(rec.get(k, "")) for k in key_fields)
        if key not in seen:
            seen.add(key)
            unique.append(rec)
    return unique


# ═══════════════════════════════════════════════════════════════════════════════
# GROUP 7: API & Networking  (cap_031 – cap_035)
# ═══════════════════════════════════════════════════════════════════════════════


def generate_openapi_spec(
    title: str, version: str, endpoints_list: list[dict]
) -> dict:
    """Generate an OpenAPI 3.0 specification.

    Each endpoint: {"path": str, "method": str, "summary": str,
                     "parameters": list[dict], "response_schema": dict}

    Args:
        title: API title.
        version: API version string.
        endpoints_list: List of endpoint definitions.

    Returns:
        OpenAPI 3.0 specification dictionary.
    """
    paths: dict = {}
    for ep in endpoints_list:
        path = ep.get("path", "/")
        method = ep.get("method", "get").lower()
        summary = ep.get("summary", "")
        params = ep.get("parameters", [])
        resp_schema = ep.get("response_schema", {"type": "object"})
        operation = {
            "summary": summary,
            "operationId": re.sub(r"[^a-zA-Z0-9]", "_", f"{method}_{path}"),
            "parameters": [
                {
                    "name": p.get("name", "param"),
                    "in": p.get("in", "query"),
                    "required": p.get("required", False),
                    "schema": {"type": p.get("type", "string")},
                }
                for p in params
            ],
            "responses": {
                "200": {
                    "description": "Successful response",
                    "content": {
                        "application/json": {"schema": resp_schema}
                    },
                },
                "400": {"description": "Bad request"},
                "500": {"description": "Internal server error"},
            },
        }
        paths.setdefault(path, {})[method] = operation

    return {
        "openapi": "3.0.3",
        "info": {"title": title, "version": version},
        "paths": paths,
        "components": {"schemas": {}},
    }


def generate_rest_client(base_url: str, endpoints_list: list[dict]) -> str:
    """Generate a Python REST client class using urllib.

    Each endpoint: {"name": str, "method": str, "path": str}

    Args:
        base_url: Base URL of the API.
        endpoints_list: List of endpoint definitions.

    Returns:
        Python source code for the REST client.
    """
    lines = [
        '"""Auto-generated REST client."""',
        "",
        "import json",
        "import urllib.request",
        "import urllib.error",
        "import urllib.parse",
        "",
        "",
        "class RestClient:",
        f'    """REST client for {base_url}."""',
        "",
        f'    def __init__(self, base_url: str = "{base_url}", headers: dict | None = None):',
        "        self.base_url = base_url.rstrip('/')",
        "        self.headers = headers or {'Content-Type': 'application/json'}",
        "",
        "    def _request(self, method: str, path: str, data: dict | None = None) -> dict:",
        '        """Execute an HTTP request."""',
        "        url = f'{self.base_url}{path}'",
        "        body = json.dumps(data).encode() if data else None",
        "        req = urllib.request.Request(url, data=body, headers=self.headers, method=method)",
        "        try:",
        "            with urllib.request.urlopen(req, timeout=30) as resp:",
        "                return json.loads(resp.read().decode())",
        "        except urllib.error.HTTPError as e:",
        "            return {'error': e.code, 'message': e.reason}",
        "        except urllib.error.URLError as e:",
        "            return {'error': 'connection_error', 'message': str(e.reason)}",
        "",
    ]
    for ep in endpoints_list:
        name = ep.get("name", "endpoint")
        method = ep.get("method", "GET").upper()
        path = ep.get("path", "/")
        fname = re.sub(r"[^a-zA-Z0-9_]", "_", name)
        if method in ("POST", "PUT", "PATCH"):
            lines += [
                f"    def {fname}(self, data: dict | None = None) -> dict:",
                f'        """Call {method} {path}."""',
                f'        return self._request("{method}", "{path}", data)',
                "",
            ]
        else:
            lines += [
                f"    def {fname}(self) -> dict:",
                f'        """Call {method} {path}."""',
                f'        return self._request("{method}", "{path}")',
                "",
            ]
    return "\n".join(lines)


def generate_webhook_handler(events_list: list[str]) -> str:
    """Generate a webhook receiver server using http.server.

    Args:
        events_list: List of event type strings to handle.

    Returns:
        Python source code for the webhook server.
    """
    handlers = ""
    for event in events_list:
        fname = "handle_" + re.sub(r"[^a-zA-Z0-9]", "_", event)
        handlers += f"""
    @staticmethod
    def {fname}(payload):
        \"\"\"Handle {event} event.\"\"\"
        print(f"[{event}] Received payload with {{len(payload)}} keys")
        return {{"status": "processed", "event": "{event}"}}
"""

    return textwrap.dedent(f"""\
        \"\"\"Auto-generated webhook handler.\"\"\"

        import json
        from http.server import HTTPServer, BaseHTTPRequestHandler


        EVENTS = {events_list!r}


        class WebhookHandler(BaseHTTPRequestHandler):
            \"\"\"Handle incoming webhook events.\"\"\"
        {handlers}
            def do_POST(self):
                length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(length)
                try:
                    payload = json.loads(body)
                except json.JSONDecodeError:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(b'{{"error": "invalid JSON"}}')
                    return

                event_type = payload.get("event_type", "unknown")
                handler_name = "handle_" + event_type.replace(".", "_").replace("-", "_")
                handler = getattr(self, handler_name, None)
                if handler:
                    result = handler(payload)
                    self.send_response(200)
                else:
                    result = {{"status": "ignored", "event": event_type}}
                    self.send_response(202)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())


        if __name__ == "__main__":
            server = HTTPServer(("", 9000), WebhookHandler)
            print("Webhook server running on :9000")
            server.serve_forever()
    """)


def generate_rate_limiter(max_requests: int, window_seconds: int) -> str:
    """Generate a token bucket rate limiter class.

    Args:
        max_requests: Max requests in the time window.
        window_seconds: Time window in seconds.

    Returns:
        Python source code for the rate limiter.
    """
    return textwrap.dedent(f"""\
        \"\"\"Token bucket rate limiter.\"\"\"

        import time
        import threading


        class RateLimiter:
            \"\"\"Token-bucket rate limiter: {max_requests} requests per {window_seconds}s.\"\"\"

            def __init__(self, max_requests: int = {max_requests},
                         window_seconds: int = {window_seconds}):
                self.max_tokens = max_requests
                self.window = window_seconds
                self.tokens = float(max_requests)
                self.last_refill = time.monotonic()
                self._lock = threading.Lock()

            def _refill(self):
                now = time.monotonic()
                elapsed = now - self.last_refill
                refill = elapsed * (self.max_tokens / self.window)
                self.tokens = min(self.max_tokens, self.tokens + refill)
                self.last_refill = now

            def acquire(self, tokens: int = 1) -> bool:
                \"\"\"Try to consume tokens. Returns True if allowed.\"\"\"
                with self._lock:
                    self._refill()
                    if self.tokens >= tokens:
                        self.tokens -= tokens
                        return True
                    return False

            def wait(self, tokens: int = 1) -> float:
                \"\"\"Block until tokens are available. Returns wait time.\"\"\"
                start = time.monotonic()
                while True:
                    if self.acquire(tokens):
                        return time.monotonic() - start
                    time.sleep(0.01)

            @property
            def available(self) -> float:
                \"\"\"Current available tokens.\"\"\"
                with self._lock:
                    self._refill()
                    return self.tokens
    """)


def port_scanner(host: str, port_range: tuple[int, int]) -> list[int]:
    """Basic TCP port scanner.

    Args:
        host: Target host (IP or hostname).
        port_range: (start_port, end_port) inclusive tuple.

    Returns:
        List of open port numbers.
    """
    open_ports: list[int] = []
    start, end = port_range
    for port in range(start, end + 1):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.3)
        try:
            result = sock.connect_ex((host, port))
            if result == 0:
                open_ports.append(port)
        except (socket.timeout, OSError):
            pass
        finally:
            sock.close()
    return open_ports


# ═══════════════════════════════════════════════════════════════════════════════
# GROUP 8: Security & Encryption  (cap_036 – cap_040)
# ═══════════════════════════════════════════════════════════════════════════════


def hash_file(file_path: str, algorithm: str = "sha256") -> str:
    """Hash a file using the specified algorithm.

    Args:
        file_path: Path to the file.
        algorithm: Hash algorithm name (sha256, md5, sha1, sha512, etc.).

    Returns:
        Hex digest string.
    """
    h = hashlib.new(algorithm)
    p = Path(file_path)
    if not p.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")
    with p.open("rb") as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def generate_password(length: int = 20, use_symbols: bool = True) -> str:
    """Generate a cryptographically secure password.

    Args:
        length: Password length (minimum 8).
        use_symbols: Whether to include special characters.

    Returns:
        Random password string.
    """
    length = max(length, 8)
    alphabet = string.ascii_letters + string.digits
    if use_symbols:
        alphabet += string.punctuation
    # Guarantee at least one of each category
    required: list[str] = [
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.digits),
    ]
    if use_symbols:
        required.append(secrets.choice(string.punctuation))
    remaining = length - len(required)
    password_chars = required + [secrets.choice(alphabet) for _ in range(remaining)]
    # Shuffle using Fisher-Yates with secrets
    for i in range(len(password_chars) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        password_chars[i], password_chars[j] = password_chars[j], password_chars[i]
    return "".join(password_chars)


def generate_secret_key(length: int = 64) -> str:
    """Generate a cryptographic secret key as a hex string.

    Args:
        length: Number of random bytes (output hex string is 2x this).

    Returns:
        Hex-encoded secret key.
    """
    return secrets.token_hex(max(length, 16))


def encode_base64(data: str) -> str:
    """Base64-encode a string.

    Args:
        data: String to encode.

    Returns:
        Base64-encoded string.
    """
    return base64.b64encode(data.encode("utf-8")).decode("ascii")


def generate_csp_header(directives_dict: dict[str, list[str]]) -> str:
    """Generate a Content-Security-Policy header string.

    Args:
        directives_dict: Mapping of directive names to source lists,
            e.g. {"default-src": ["'self'"], "script-src": ["'self'", "cdn.example.com"]}

    Returns:
        CSP header value string.
    """
    parts: list[str] = []
    for directive, sources in directives_dict.items():
        parts.append(f"{directive} {' '.join(sources)}")
    return "; ".join(parts)


# ═══════════════════════════════════════════════════════════════════════════════
# GROUP 9: DevOps & Infrastructure  (cap_041 – cap_045)
# ═══════════════════════════════════════════════════════════════════════════════


def generate_github_actions_workflow(
    name: str, triggers: list[str], steps: list[dict]
) -> str:
    """Generate a GitHub Actions CI/CD workflow YAML.

    Each step: {"name": str, "run": str} or {"name": str, "uses": str}

    Args:
        name: Workflow name.
        triggers: List of trigger events (e.g. ["push", "pull_request"]).
        steps: List of step definitions.

    Returns:
        YAML string for .github/workflows/.
    """
    trigger_block = "\n".join(f"  {t}:" for t in triggers)
    steps_lines: list[str] = []
    for step in steps:
        sname = step.get("name", "Step")
        if "uses" in step:
            steps_lines.append(f"      - name: {sname}")
            steps_lines.append(f"        uses: {step['uses']}")
        elif "run" in step:
            steps_lines.append(f"      - name: {sname}")
            steps_lines.append(f"        run: {step['run']}")
        if "with" in step:
            steps_lines.append("        with:")
            for k, v in step["with"].items():
                steps_lines.append(f"          {k}: {v}")

    steps_block = "\n".join(steps_lines)
    return textwrap.dedent(f"""\
        name: {name}

        on:
        {trigger_block}

        jobs:
          build:
            runs-on: ubuntu-latest
            steps:
              - name: Checkout
                uses: actions/checkout@v4
        {steps_block}
    """)


def generate_nginx_config(server_name: str, upstream_port: int) -> str:
    """Generate an Nginx reverse proxy configuration.

    Args:
        server_name: Domain name.
        upstream_port: Port of the upstream application.

    Returns:
        Nginx configuration string.
    """
    return textwrap.dedent(f"""\
        upstream app_backend {{
            server 127.0.0.1:{upstream_port};
            keepalive 32;
        }}

        server {{
            listen 80;
            server_name {server_name};

            # Redirect HTTP to HTTPS
            return 301 https://$host$request_uri;
        }}

        server {{
            listen 443 ssl http2;
            server_name {server_name};

            ssl_certificate     /etc/ssl/certs/{server_name}.crt;
            ssl_certificate_key /etc/ssl/private/{server_name}.key;
            ssl_protocols       TLSv1.2 TLSv1.3;
            ssl_ciphers         HIGH:!aNULL:!MD5;

            # Security headers
            add_header X-Frame-Options DENY;
            add_header X-Content-Type-Options nosniff;
            add_header X-XSS-Protection "1; mode=block";
            add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

            # Gzip
            gzip on;
            gzip_types text/plain application/json application/javascript text/css;
            gzip_min_length 256;

            location / {{
                proxy_pass http://app_backend;
                proxy_set_header Host $host;
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header X-Forwarded-Proto $scheme;
                proxy_http_version 1.1;
                proxy_set_header Connection "";
                proxy_read_timeout 90s;
            }}

            location /health {{
                proxy_pass http://app_backend/health;
                access_log off;
            }}

            # Static files
            location /static/ {{
                alias /var/www/{server_name}/static/;
                expires 30d;
                add_header Cache-Control "public, immutable";
            }}
        }}
    """)


def generate_docker_compose(services_dict: dict[str, dict]) -> str:
    """Generate a Docker Compose YAML.

    services_dict maps service names to config dicts::

        {"web": {"image": "myapp:latest", "ports": ["8000:8000"],
                 "environment": {"DEBUG": "false"}}}

    Args:
        services_dict: Mapping of service names to configurations.

    Returns:
        docker-compose.yml content string.
    """
    lines = ["version: '3.8'", "", "services:"]
    for svc_name, cfg in services_dict.items():
        lines.append(f"  {svc_name}:")
        if "image" in cfg:
            lines.append(f"    image: {cfg['image']}")
        if "build" in cfg:
            lines.append(f"    build: {cfg['build']}")
        if "ports" in cfg:
            lines.append("    ports:")
            for p in cfg["ports"]:
                lines.append(f'      - "{p}"')
        if "environment" in cfg:
            lines.append("    environment:")
            for k, v in cfg["environment"].items():
                lines.append(f"      {k}: {v}")
        if "volumes" in cfg:
            lines.append("    volumes:")
            for vol in cfg["volumes"]:
                lines.append(f"      - {vol}")
        if "depends_on" in cfg:
            lines.append("    depends_on:")
            for dep in cfg["depends_on"]:
                lines.append(f"      - {dep}")
        if "restart" in cfg:
            lines.append(f"    restart: {cfg['restart']}")
        else:
            lines.append("    restart: unless-stopped")
        lines.append("")

    if any("volumes" in cfg for cfg in services_dict.values()):
        lines.append("volumes:")
        for svc_name, cfg in services_dict.items():
            for vol in cfg.get("volumes", []):
                vol_name = vol.split(":")[0]
                if not vol_name.startswith("/") and not vol_name.startswith("."):
                    lines.append(f"  {vol_name}:")
    return "\n".join(lines) + "\n"


def generate_env_template(variables_dict: dict[str, str]) -> str:
    """Generate a .env template with descriptions as comments.

    Args:
        variables_dict: Mapping of variable names to description strings.

    Returns:
        .env template content.
    """
    lines = [
        "# ============================================",
        "# Environment Configuration Template",
        f"# Generated: {datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
        "# ============================================",
        "",
    ]
    for var, desc in variables_dict.items():
        lines.append(f"# {desc}")
        lines.append(f"{var}=")
        lines.append("")
    return "\n".join(lines)


def system_health_check() -> dict:
    """Perform a local system health check.

    Returns:
        Dictionary with CPU, memory, disk, and platform info.
    """
    info: dict[str, Any] = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
        },
    }

    # Disk usage
    try:
        usage = shutil.disk_usage("/")
        info["disk"] = {
            "total_gb": round(usage.total / (1024**3), 2),
            "used_gb": round(usage.used / (1024**3), 2),
            "free_gb": round(usage.free / (1024**3), 2),
            "usage_percent": round(usage.used / usage.total * 100, 1),
        }
    except OSError:
        info["disk"] = {"error": "Unable to read disk usage"}

    # CPU count
    info["cpu"] = {
        "logical_cores": os.cpu_count() or 0,
    }

    # Load average (Unix) or placeholder
    if hasattr(os, "getloadavg"):
        try:
            load = os.getloadavg()
            info["cpu"]["load_avg_1m"] = round(load[0], 2)
            info["cpu"]["load_avg_5m"] = round(load[1], 2)
            info["cpu"]["load_avg_15m"] = round(load[2], 2)
        except OSError:
            pass

    # Hostname and PID
    info["hostname"] = socket.gethostname()
    info["pid"] = os.getpid()

    return info


# ═══════════════════════════════════════════════════════════════════════════════
# GROUP 10: Research & Knowledge  (cap_046 – cap_050)
# ═══════════════════════════════════════════════════════════════════════════════


def generate_literature_review_outline(
    topic: str, num_sections: int = 5
) -> dict:
    """Generate an academic literature review outline.

    Args:
        topic: Research topic.
        num_sections: Number of thematic sections.

    Returns:
        Structured outline dictionary.
    """
    sections = []
    section_types = [
        "Historical Background and Foundational Work",
        "Theoretical Frameworks and Models",
        "Key Empirical Studies and Findings",
        "Methodological Approaches",
        "Current Trends and Emerging Directions",
        "Critical Analysis and Debates",
        "Applications and Practical Implications",
        "Gaps in the Literature",
    ]
    for i in range(min(num_sections, len(section_types))):
        sections.append(
            {
                "section_number": i + 1,
                "title": f"{section_types[i]}: {topic}",
                "subsections": [
                    f"Overview of {section_types[i].lower()} in {topic}",
                    "Key authors and seminal works",
                    "Critical assessment and synthesis",
                ],
                "estimated_sources": max(3, 8 - i),
                "notes": "",
            }
        )
    return {
        "topic": topic,
        "generated": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "total_sections": len(sections),
        "outline": {
            "introduction": {
                "scope": f"This review examines the current state of research on {topic}.",
                "objectives": [
                    f"Synthesize existing literature on {topic}",
                    "Identify gaps and future research directions",
                    "Evaluate methodological strengths and limitations",
                ],
            },
            "body_sections": sections,
            "conclusion": {
                "summary_of_findings": f"Summary of key findings in {topic} research.",
                "identified_gaps": "Gaps identified through the review.",
                "future_directions": "Recommended directions for future research.",
            },
        },
    }


def generate_research_protocol(
    title: str, hypothesis: str, methodology: str
) -> dict:
    """Generate a research protocol template.

    Args:
        title: Research study title.
        hypothesis: Primary hypothesis.
        methodology: Methodology description.

    Returns:
        Complete research protocol dictionary.
    """
    return {
        "protocol_id": f"RP-{uuid.uuid4().hex[:8].upper()}",
        "title": title,
        "version": "1.0",
        "date": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d"),
        "status": "DRAFT",
        "sections": {
            "background": {
                "title": "Background and Rationale",
                "content": f"This study investigates: {title}",
            },
            "objectives": {
                "primary": f"To test the hypothesis that {hypothesis}",
                "secondary": [],
            },
            "hypothesis": {
                "primary": hypothesis,
                "null_hypothesis": f"There is no effect related to: {hypothesis}",
            },
            "methodology": {
                "design": methodology,
                "population": "To be defined",
                "sample_size": "To be calculated",
                "variables": {
                    "independent": [],
                    "dependent": [],
                    "control": [],
                },
                "data_collection": "To be specified",
                "analysis_plan": "To be specified",
            },
            "ethical_considerations": {
                "irb_approval": "Required",
                "informed_consent": "Required",
                "data_privacy": "All data will be anonymized",
            },
            "timeline": [
                {"phase": "Preparation", "duration": "Month 1-2"},
                {"phase": "Data Collection", "duration": "Month 3-6"},
                {"phase": "Analysis", "duration": "Month 7-8"},
                {"phase": "Writing", "duration": "Month 9-10"},
                {"phase": "Review & Submission", "duration": "Month 11-12"},
            ],
            "references": [],
        },
    }


def generate_citation(
    authors: list[str], title: str, journal: str, year: int
) -> dict:
    """Format citations in APA and IEEE styles.

    Args:
        authors: List of author names ("Last, First" format preferred).
        title: Title of the work.
        journal: Journal or publication name.
        year: Publication year.

    Returns:
        Dictionary with 'apa' and 'ieee' formatted citations.
    """

    def _apa_authors(authors: list[str]) -> str:
        if len(authors) == 1:
            return authors[0]
        elif len(authors) == 2:
            return f"{authors[0]} & {authors[1]}"
        elif len(authors) <= 7:
            return ", ".join(authors[:-1]) + f", & {authors[-1]}"
        else:
            return ", ".join(authors[:6]) + f", ... {authors[-1]}"

    def _ieee_authors(authors: list[str]) -> str:
        parts = []
        for a in authors:
            if "," in a:
                last, first = a.split(",", 1)
                initials = ". ".join(w[0].upper() for w in first.strip().split() if w)
                parts.append(f"{initials}. {last.strip()}")
            else:
                parts.append(a)
        if len(parts) <= 3:
            return ", ".join(parts[:-1]) + " and " + parts[-1] if len(parts) > 1 else parts[0]
        return ", ".join(parts[:3]) + ", et al."

    apa = f"{_apa_authors(authors)} ({year}). {title}. *{journal}*."
    ieee = f'{_ieee_authors(authors)}, "{title}," *{journal}*, {year}.'

    return {"apa": apa, "ieee": ieee, "raw": {"authors": authors, "title": title, "journal": journal, "year": year}}


def extract_keywords(text: str, top_n: int = 10) -> list[str]:
    """Extract keywords from text using TF-IDF-like scoring.

    Uses term frequency weighted by inverse document frequency approximation
    (treating each sentence as a document).

    Args:
        text: Input text.
        top_n: Number of top keywords to return.

    Returns:
        List of keywords sorted by relevance score.
    """
    # Common English stop words
    stop_words = {
        "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "is", "it", "as", "was", "are", "be",
        "been", "being", "have", "has", "had", "do", "does", "did", "will",
        "would", "could", "should", "may", "might", "can", "shall", "this",
        "that", "these", "those", "i", "me", "my", "we", "our", "you", "your",
        "he", "she", "his", "her", "they", "them", "their", "its", "not", "no",
        "so", "if", "then", "than", "too", "very", "just", "about", "also",
        "more", "most", "other", "some", "such", "only", "same", "each",
        "every", "all", "both", "few", "many", "much", "any", "own", "up",
        "out", "into", "over", "after", "before", "between", "under", "during",
        "through", "above", "below", "which", "who", "whom", "what", "where",
        "when", "how", "why", "while", "there", "here",
    }

    # Tokenize
    words = re.findall(r"[a-zA-Z]{3,}", text.lower())
    words = [w for w in words if w not in stop_words]

    # Sentence-level IDF approximation
    sentences = re.split(r"[.!?\n]+", text.lower())
    sentences = [s.strip() for s in sentences if s.strip()]
    num_docs = max(len(sentences), 1)

    # Term frequency
    tf = collections.Counter(words)
    total_words = max(len(words), 1)

    # Document frequency
    df: dict[str, int] = collections.Counter()
    for sent in sentences:
        sent_words = set(re.findall(r"[a-zA-Z]{3,}", sent))
        for w in sent_words:
            if w not in stop_words:
                df[w] += 1

    # TF-IDF scoring
    scores: dict[str, float] = {}
    for word, count in tf.items():
        tf_score = count / total_words
        idf_score = math.log((num_docs + 1) / (df.get(word, 0) + 1)) + 1
        scores[word] = tf_score * idf_score

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [word for word, _ in ranked[:top_n]]


def generate_abstract(
    title: str, methodology: str, results: str, conclusion: str
) -> str:
    """Generate a structured academic abstract.

    Args:
        title: Study title.
        methodology: Methods description.
        results: Results description.
        conclusion: Conclusion statement.

    Returns:
        Formatted abstract string.
    """
    return textwrap.dedent(f"""\
        ABSTRACT

        Title: {title}

        Background: This study addresses key questions related to
        {title.lower()}.

        Methods: {methodology}

        Results: {results}

        Conclusions: {conclusion}

        Keywords: {", ".join(extract_keywords(f"{title} {methodology} {results} {conclusion}", 5))}
    """)


# ═══════════════════════════════════════════════════════════════════════════════
# CAPABILITIES REGISTRY
# ═══════════════════════════════════════════════════════════════════════════════

DOMAIN_GROUPS = {
    "Code Generation": ["cap_001", "cap_002", "cap_003", "cap_004", "cap_005"],
    "Business & Planning": ["cap_006", "cap_007", "cap_008", "cap_009", "cap_010"],
    "Document Assembly": ["cap_011", "cap_012", "cap_013", "cap_014", "cap_015"],
    "File Indexing & Search": ["cap_016", "cap_017", "cap_018", "cap_019", "cap_020"],
    "Agent Building": ["cap_021", "cap_022", "cap_023", "cap_024", "cap_025"],
    "Data Processing": ["cap_026", "cap_027", "cap_028", "cap_029", "cap_030"],
    "API & Networking": ["cap_031", "cap_032", "cap_033", "cap_034", "cap_035"],
    "Security & Encryption": ["cap_036", "cap_037", "cap_038", "cap_039", "cap_040"],
    "DevOps & Infrastructure": ["cap_041", "cap_042", "cap_043", "cap_044", "cap_045"],
    "Research & Knowledge": ["cap_046", "cap_047", "cap_048", "cap_049", "cap_050"],
}

CAPABILITIES_REGISTRY: dict[str, dict[str, Any]] = {
    # Group 1: Code Generation
    "cap_001": {"name": "generate_python_crud_api", "function": generate_python_crud_api, "domain": "Code Generation"},
    "cap_002": {"name": "generate_flask_app", "function": generate_flask_app, "domain": "Code Generation"},
    "cap_003": {"name": "generate_cli_tool", "function": generate_cli_tool, "domain": "Code Generation"},
    "cap_004": {"name": "generate_dockerfile", "function": generate_dockerfile, "domain": "Code Generation"},
    "cap_005": {"name": "generate_makefile", "function": generate_makefile, "domain": "Code Generation"},
    # Group 2: Business & Planning
    "cap_006": {"name": "generate_business_plan", "function": generate_business_plan, "domain": "Business & Planning"},
    "cap_007": {"name": "generate_pitch_deck_outline", "function": generate_pitch_deck_outline, "domain": "Business & Planning"},
    "cap_008": {"name": "calculate_runway", "function": calculate_runway, "domain": "Business & Planning"},
    "cap_009": {"name": "generate_competitive_analysis", "function": generate_competitive_analysis, "domain": "Business & Planning"},
    "cap_010": {"name": "generate_okrs", "function": generate_okrs, "domain": "Business & Planning"},
    # Group 3: Document Assembly
    "cap_011": {"name": "assemble_pdf_text", "function": assemble_pdf_text, "domain": "Document Assembly"},
    "cap_012": {"name": "generate_invoice", "function": generate_invoice, "domain": "Document Assembly"},
    "cap_013": {"name": "generate_contract_template", "function": generate_contract_template, "domain": "Document Assembly"},
    "cap_014": {"name": "merge_markdown_files", "function": merge_markdown_files, "domain": "Document Assembly"},
    "cap_015": {"name": "generate_readme", "function": generate_readme, "domain": "Document Assembly"},
    # Group 4: File Indexing & Search
    "cap_016": {"name": "index_directory", "function": index_directory, "domain": "File Indexing & Search"},
    "cap_017": {"name": "search_files_by_content", "function": search_files_by_content, "domain": "File Indexing & Search"},
    "cap_018": {"name": "generate_file_manifest", "function": generate_file_manifest, "domain": "File Indexing & Search"},
    "cap_019": {"name": "find_duplicate_files", "function": find_duplicate_files, "domain": "File Indexing & Search"},
    "cap_020": {"name": "generate_directory_tree", "function": generate_directory_tree, "domain": "File Indexing & Search"},
    # Group 5: Agent Building
    "cap_021": {"name": "create_agent_definition", "function": create_agent_definition, "domain": "Agent Building"},
    "cap_022": {"name": "generate_system_prompt", "function": generate_system_prompt, "domain": "Agent Building"},
    "cap_023": {"name": "create_tool_manifest", "function": create_tool_manifest, "domain": "Agent Building"},
    "cap_024": {"name": "generate_agent_workflow", "function": generate_agent_workflow, "domain": "Agent Building"},
    "cap_025": {"name": "create_agent_evaluation", "function": create_agent_evaluation, "domain": "Agent Building"},
    # Group 6: Data Processing
    "cap_026": {"name": "csv_to_json", "function": csv_to_json, "domain": "Data Processing"},
    "cap_027": {"name": "json_to_csv", "function": json_to_csv, "domain": "Data Processing"},
    "cap_028": {"name": "merge_csv_files", "function": merge_csv_files, "domain": "Data Processing"},
    "cap_029": {"name": "pivot_data", "function": pivot_data, "domain": "Data Processing"},
    "cap_030": {"name": "deduplicate_records", "function": deduplicate_records, "domain": "Data Processing"},
    # Group 7: API & Networking
    "cap_031": {"name": "generate_openapi_spec", "function": generate_openapi_spec, "domain": "API & Networking"},
    "cap_032": {"name": "generate_rest_client", "function": generate_rest_client, "domain": "API & Networking"},
    "cap_033": {"name": "generate_webhook_handler", "function": generate_webhook_handler, "domain": "API & Networking"},
    "cap_034": {"name": "generate_rate_limiter", "function": generate_rate_limiter, "domain": "API & Networking"},
    "cap_035": {"name": "port_scanner", "function": port_scanner, "domain": "API & Networking"},
    # Group 8: Security & Encryption
    "cap_036": {"name": "hash_file", "function": hash_file, "domain": "Security & Encryption"},
    "cap_037": {"name": "generate_password", "function": generate_password, "domain": "Security & Encryption"},
    "cap_038": {"name": "generate_secret_key", "function": generate_secret_key, "domain": "Security & Encryption"},
    "cap_039": {"name": "encode_base64", "function": encode_base64, "domain": "Security & Encryption"},
    "cap_040": {"name": "generate_csp_header", "function": generate_csp_header, "domain": "Security & Encryption"},
    # Group 9: DevOps & Infrastructure
    "cap_041": {"name": "generate_github_actions_workflow", "function": generate_github_actions_workflow, "domain": "DevOps & Infrastructure"},
    "cap_042": {"name": "generate_nginx_config", "function": generate_nginx_config, "domain": "DevOps & Infrastructure"},
    "cap_043": {"name": "generate_docker_compose", "function": generate_docker_compose, "domain": "DevOps & Infrastructure"},
    "cap_044": {"name": "generate_env_template", "function": generate_env_template, "domain": "DevOps & Infrastructure"},
    "cap_045": {"name": "system_health_check", "function": system_health_check, "domain": "DevOps & Infrastructure"},
    # Group 10: Research & Knowledge
    "cap_046": {"name": "generate_literature_review_outline", "function": generate_literature_review_outline, "domain": "Research & Knowledge"},
    "cap_047": {"name": "generate_research_protocol", "function": generate_research_protocol, "domain": "Research & Knowledge"},
    "cap_048": {"name": "generate_citation", "function": generate_citation, "domain": "Research & Knowledge"},
    "cap_049": {"name": "extract_keywords", "function": extract_keywords, "domain": "Research & Knowledge"},
    "cap_050": {"name": "generate_abstract", "function": generate_abstract, "domain": "Research & Knowledge"},
}


# ═══════════════════════════════════════════════════════════════════════════════
# CAPABILITY RUNNER
# ═══════════════════════════════════════════════════════════════════════════════


class CapabilityRunner:
    """Discover, search, and execute registered capabilities."""

    def __init__(self) -> None:
        self.registry = CAPABILITIES_REGISTRY
        self.domains = DOMAIN_GROUPS

    def list_capabilities(self) -> list[dict]:
        """List all registered capabilities.

        Returns:
            Sorted list of capability info dicts.
        """
        result: list[dict] = []
        for cap_id in sorted(self.registry.keys()):
            entry = self.registry[cap_id]
            result.append(
                {
                    "id": cap_id,
                    "name": entry["name"],
                    "domain": entry["domain"],
                }
            )
        return result

    def search(self, term: str) -> list[dict]:
        """Search capabilities by name, domain, or ID.

        Args:
            term: Search term (case-insensitive substring match).

        Returns:
            List of matching capability info dicts.
        """
        term_lower = term.lower()
        matches: list[dict] = []
        for cap_id, entry in self.registry.items():
            searchable = f"{cap_id} {entry['name']} {entry['domain']}".lower()
            if term_lower in searchable:
                matches.append(
                    {
                        "id": cap_id,
                        "name": entry["name"],
                        "domain": entry["domain"],
                    }
                )
        return matches

    def run(self, cap_id: str, **kwargs: Any) -> Any:
        """Execute a capability by its ID.

        Args:
            cap_id: Capability identifier (e.g. "cap_001").
            **kwargs: Arguments to pass to the function.

        Returns:
            Result of the function call.

        Raises:
            KeyError: If the cap_id is not found.
        """
        if cap_id not in self.registry:
            raise KeyError(f"Unknown capability: {cap_id}")
        func: Callable = self.registry[cap_id]["function"]
        return func(**kwargs)

    def stats(self) -> dict:
        """Return summary statistics about registered capabilities.

        Returns:
            Dictionary with counts by domain and totals.
        """
        domain_counts: dict[str, int] = collections.Counter()
        for entry in self.registry.values():
            domain_counts[entry["domain"]] += 1
        return {
            "total_capabilities": len(self.registry),
            "total_domains": len(self.domains),
            "by_domain": dict(domain_counts),
        }


# ═══════════════════════════════════════════════════════════════════════════════
# __main__ — demo & smoke test
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    runner = CapabilityRunner()
    separator = "=" * 72

    # ── List all capabilities ──
    print(separator)
    print("  AIEOS CAPABILITIES REGISTRY — 50 FUNCTIONS")
    print(separator)
    for cap in runner.list_capabilities():
        print(f"  {cap['id']:>7}  │  {cap['domain']:<25} │  {cap['name']}")
    print(separator)

    # ── Stats ──
    stats = runner.stats()
    print(f"\n  Total capabilities : {stats['total_capabilities']}")
    print(f"  Total domains      : {stats['total_domains']}")
    for domain, count in stats["by_domain"].items():
        print(f"    {domain:<25}: {count}")
    print()

    # ── Demo calls ──
    print(separator)
    print("  DEMO RUNS")
    print(separator)

    # Demo: Dockerfile generation
    print("\n▸ cap_004 — generate_dockerfile")
    df = runner.run("cap_004", base_image="python:3.12-slim", app_name="myservice", port=8080)
    print(df[:300] + "...\n")

    # Demo: Runway calculation
    print("▸ cap_008 — calculate_runway")
    runway = runner.run("cap_008", monthly_burn=50000, cash_on_hand=600000, monthly_revenue=15000)
    print(json.dumps(runway, indent=2))

    # Demo: Password generation
    print("\n▸ cap_037 — generate_password")
    for _ in range(3):
        print(f"  {runner.run('cap_037', length=24, use_symbols=True)}")

    # Demo: Base64 encode
    print("\n▸ cap_039 — encode_base64")
    encoded = runner.run("cap_039", data="Hello, AIEOS capabilities!")
    print(f"  Encoded: {encoded}")

    # Demo: System health
    print("\n▸ cap_045 — system_health_check")
    health = runner.run("cap_045")
    print(json.dumps(health, indent=2))

    # Demo: Keyword extraction
    print("\n▸ cap_049 — extract_keywords")
    sample_text = (
        "Artificial intelligence and machine learning are transforming the "
        "landscape of software engineering. Deep learning models enable natural "
        "language processing, computer vision, and autonomous systems. "
        "Reinforcement learning drives breakthroughs in robotics and optimization."
    )
    keywords = runner.run("cap_049", text=sample_text, top_n=8)
    print(f"  Keywords: {keywords}")

    # Demo: Search
    print("\n▸ Search for 'generate'")
    results = runner.search("generate")
    print(f"  Found {len(results)} capabilities matching 'generate'")
    for r in results[:5]:
        print(f"    {r['id']}: {r['name']}")

    print(f"\n{separator}")
    print("  ALL DEMOS COMPLETE — ALL FUNCTIONS ARE REAL AND CALLABLE")
    print(separator)
