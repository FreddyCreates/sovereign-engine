"""HTTP helpers for CRM / Apps / Books-extended routes (used by dashboard server)."""

from __future__ import annotations

import json
from typing import Any, Dict, Optional

from .apps_manager import AppsManager
from .books_extended import BooksExtended
from .crm_store import CRMStore
from .roadmap_registry import verify_all

_crm: Optional[CRMStore] = None
_apps: Optional[AppsManager] = None
_books_ext: Optional[BooksExtended] = None


def crm() -> CRMStore:
    global _crm
    if _crm is None:
        _crm = CRMStore()
    return _crm


def apps() -> AppsManager:
    global _apps
    if _apps is None:
        _apps = AppsManager()
    return _apps


def books_ext() -> BooksExtended:
    global _books_ext
    if _books_ext is None:
        _books_ext = BooksExtended()
    return _books_ext


def handle_crm_get(path: str, params: Dict[str, str]) -> Dict[str, Any]:
    store = crm()
    q = params.get("q")
    filters = None
    if path == "/api/v1/crm/companies":
        out = store.list_records("companies")
        if q:
            out["records"] = [r for r in out["records"] if q.lower() in json.dumps(r).lower()]
            out["count"] = len(out["records"])
        return out
    if path == "/api/v1/crm/people":
        out = store.list_records("people")
        if q:
            out["records"] = [r for r in out["records"] if q.lower() in json.dumps(r).lower()]
            out["count"] = len(out["records"])
        return out
    if path == "/api/v1/crm/opportunities":
        return store.list_records("opportunities")
    if path == "/api/v1/crm/tasks":
        return store.list_records("tasks")
    if path == "/api/v1/crm/notes":
        return store.list_records("notes")
    if path == "/api/v1/crm/workflows":
        return store.list_records("workflows")
    if path == "/api/v1/crm/kanban":
        return store.kanban_view(params.get("object", "opportunities"))
    if path == "/api/v1/crm/calendar":
        return store.calendar_view(params.get("month"))
    if path == "/api/v1/crm/pipeline":
        return {
            "expected": store.pipeline_expected_amount(),
            "stages": store.list_records("pipeline_stages"),
            "status": "OK",
        }
    if path == "/api/v1/crm/search":
        return store.command_palette_search(params.get("q") or "")
    if path.startswith("/api/v1/crm/record/"):
        parts = path.strip("/").split("/")
        if len(parts) >= 5:
            return store.record_detail(parts[3], parts[4])
    return {"status": "ERROR", "error": f"Unknown CRM GET {path}"}


def handle_crm_post(path: str, body: Dict[str, Any]) -> Dict[str, Any]:
    store = crm()
    if path == "/api/v1/crm/companies":
        return store.create_company(**body)
    if path == "/api/v1/crm/people":
        return store.create_person(**body)
    if path == "/api/v1/crm/opportunities":
        return store.create_opportunity(**body)
    if path == "/api/v1/crm/tasks":
        return store.create_task(**body)
    if path == "/api/v1/crm/notes":
        return store.create_note(**body)
    if path == "/api/v1/crm/workflows":
        return store.create_workflow(
            body.get("name") or "Workflow",
            body.get("trigger") or {"type": "manual"},
            body.get("actions") or [],
            body.get("branches"),
        )
    if path == "/api/v1/crm/workflows/run":
        return store.run_workflow(body["workflow_id"], body.get("payload"))
    if path == "/api/v1/crm/ai":
        return store.ai_chat(body.get("message") or "")
    if path == "/api/v1/crm/import":
        return store.import_csv(body.get("table") or "companies", body.get("csv") or "")
    return {"status": "ERROR", "error": f"Unknown CRM POST {path}"}


def handle_apps_get(path: str, params: Dict[str, str]) -> Dict[str, Any]:
    mgr = apps()
    if path == "/api/v1/apps/projects":
        return mgr.list_projects()
    if path == "/api/v1/apps/builds":
        pid = params.get("project_id")
        if pid:
            return mgr.rest_list_builds(pid)
        projects = mgr.list_projects()["projects"]
        if not projects:
            return {"builds": [], "status": "OK"}
        return mgr.rest_list_builds(projects[0]["id"])
    if path == "/api/v1/apps/releases":
        with mgr._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM releases ORDER BY created_at DESC LIMIT 50"
            ).fetchall()
        from .apps_manager import _row

        return {"releases": [_row(r) for r in rows], "count": len(rows), "status": "OK"}
    if path == "/api/v1/apps/stores":
        with mgr._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM store_submissions ORDER BY created_at DESC LIMIT 50"
            ).fetchall()
        from .apps_manager import _row

        return {"submissions": [_row(r) for r in rows], "count": len(rows), "status": "OK"}
    if path == "/api/v1/apps/web":
        with mgr._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM web_deploys ORDER BY created_at DESC LIMIT 50"
            ).fetchall()
        from .apps_manager import _row

        return {"deploys": [_row(r) for r in rows], "count": len(rows), "status": "OK"}
    if path == "/api/v1/apps/pipelines":
        with mgr._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM pipelines ORDER BY created_at DESC LIMIT 50"
            ).fetchall()
        from .apps_manager import _row

        return {"pipelines": [_row(r) for r in rows], "count": len(rows), "status": "OK"}
    if path == "/api/v1/apps/audit":
        return mgr.audit_entries()
    return {"status": "ERROR", "error": f"Unknown apps GET {path}"}


def handle_apps_post(path: str, body: Dict[str, Any]) -> Dict[str, Any]:
    mgr = apps()
    if path == "/api/v1/apps/projects":
        return mgr.create_project(
            body.get("name") or "App",
            body.get("platforms") or ["android"],
            repo=body.get("repo"),
        )
    if path == "/api/v1/apps/builds":
        return mgr.trigger_build(
            body["project_id"],
            platform=body.get("platform") or "android",
            profile=body.get("profile") or "preview",
        )
    if path == "/api/v1/apps/releases":
        return mgr.publish_ota(
            body["project_id"],
            channel=body.get("channel") or "preview",
            message=body.get("message") or "",
        )
    if path == "/api/v1/apps/stores":
        return mgr.submit_store(
            body["project_id"],
            store=body.get("store") or "play",
            track=body.get("track") or "internal",
            version=body.get("version") or "1.0.0",
            build_id=body.get("build_id"),
        )
    if path == "/api/v1/apps/web":
        return mgr.deploy_web(
            body["project_id"],
            env_name=body.get("env") or "preview",
            provider=body.get("provider") or "vercel",
            url=body.get("url"),
        )
    if path == "/api/v1/apps/pipelines/run":
        return mgr.run_pipeline(body["pipeline_id"], trigger=body.get("trigger") or "manual")
    if path == "/api/v1/apps/cli":
        return mgr.cli(body.get("command") or "status", **{k: v for k, v in body.items() if k != "command"})
    return {"status": "ERROR", "error": f"Unknown apps POST {path}"}


def handle_books_ext_get(path: str, params: Dict[str, str]) -> Dict[str, Any]:
    b = books_ext()
    bid = params.get("business_id")
    if path == "/api/v1/books/reconcile":
        return b.reconcile(float(params.get("statement_balance") or 0), bid)
    if path == "/api/v1/books/reports/pnl":
        return b.pnl_report(bid)
    if path == "/api/v1/books/reports/balance_sheet":
        return b.balance_sheet_export(bid)
    if path == "/api/v1/books/invoices":
        return b.list_invoices(bid) if hasattr(b, "list_invoices") else {"status": "OK", "invoices": []}
    if path == "/api/v1/books/bills":
        return b.list_bills_due(bid)
    if path == "/api/v1/books/runway":
        return b.runway_alerts(float(params.get("weekly_burn") or 5000), bid)
    if path == "/api/v1/books/tax_bucket":
        return b.tax_bucket(business_id=bid)
    if path == "/api/v1/books/anomalies":
        return b.flag_anomalies(bid)
    if path == "/api/v1/books/businesses":
        return b.list_businesses()
    if path == "/api/v1/roadmap/verify":
        return verify_all()
    return {"status": "ERROR", "error": f"Unknown books-ext GET {path}"}


def handle_books_ext_post(path: str, body: Dict[str, Any]) -> Dict[str, Any]:
    b = books_ext()
    bid = body.get("business_id")
    if path == "/api/v1/books/invoices":
        return b.create_invoice(
            body.get("customer") or "Customer",
            float(body.get("amount") or 0),
            business_id=bid,
        )
    if path == "/api/v1/books/invoices/pay":
        return b.mark_invoice_paid(body["id"])
    if path == "/api/v1/books/bills":
        return b.create_bill(
            body.get("vendor") or "Vendor",
            float(body.get("amount") or 0),
            business_id=bid,
        )
    if path == "/api/v1/books/receipts":
        return b.capture_receipt(
            body.get("merchant") or "Merchant",
            float(body.get("amount") or 0),
            business_id=bid,
        )
    if path == "/api/v1/books/rules":
        return b.add_category_rule(
            body.get("pattern") or "",
            body.get("category") or "Uncategorized Expense",
            body.get("account_code") or "6060",
            bid,
        )
    if path == "/api/v1/books/close_month":
        return b.close_month_run(body.get("period"), bid)
    return {"status": "ERROR", "error": f"Unknown books-ext POST {path}"}
