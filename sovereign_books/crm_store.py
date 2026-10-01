"""
SQLite-backed CRM store — Twenty-parity core objects, views, pipeline, custom model.
"""

from __future__ import annotations

import csv
import io
import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .db import db_session, init_db

from .crm_schema import CRM_SCHEMA

_DEFAULT_STAGES = [
    ("NEW", 0, 0.1),
    ("QUALIFIED", 1, 0.25),
    ("PROPOSAL", 2, 0.5),
    ("NEGOTIATION", 3, 0.75),
    ("CLOSED_WON", 4, 1.0),
    ("CLOSED_LOST", 5, 0.0),
]


def _uid(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:12]}"


def _row(r) -> Dict[str, Any]:
    return dict(r) if r else {}


def _now() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


class CRMStore:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path
        init_db(db_path)
        self._ensure_tables()
        self._seed_if_empty()

    def _conn(self):
        return db_session(self.db_path)

    def _ensure_tables(self) -> None:
        with self._conn() as conn:
            conn.executescript(CRM_SCHEMA)

    def _seed_if_empty(self) -> None:
        with self._conn() as conn:
            n = conn.execute("SELECT COUNT(*) AS c FROM companies").fetchone()["c"]
            if n:
                return
            for name, pos, prob in _DEFAULT_STAGES:
                conn.execute(
                    "INSERT OR IGNORE INTO pipeline_stages (id, name, position, probability) VALUES (?,?,?,?)",
                    (_uid("stg_"), name, pos, prob),
                )
            co = _uid("co_")
            pe = _uid("pe_")
            opp = _uid("opp_")
            conn.execute(
                "INSERT INTO companies (id,name,domain,icp,arr,industry,employees) VALUES (?,?,?,?,?,?,?)",
                (co, "Acme Robotics", "acme.robot", "B2B SaaS", 120000, "Manufacturing", 42),
            )
            conn.execute(
                "INSERT INTO people (id,first_name,last_name,email,role,company_id) VALUES (?,?,?,?,?,?)",
                (pe, "Ada", "Lovelace", "ada@acme.robot", "CTO", co),
            )
            conn.execute(
                "UPDATE companies SET main_contact_id=? WHERE id=?", (pe, co)
            )
            conn.execute(
                """INSERT INTO opportunities (id,name,company_id,stage,amount,probability,close_date)
                   VALUES (?,?,?,?,?,?,?)""",
                (opp, "Acme Platform Deal", co, "PROPOSAL", 48000, 0.5, "2026-12-01"),
            )
            conn.execute(
                "INSERT INTO tasks (id,title,status,due_date,company_id,person_id,opportunity_id) VALUES (?,?,?,?,?,?,?)",
                (_uid("tsk_"), "Send proposal PDF", "TODO", "2026-09-15", co, pe, opp),
            )
            conn.execute(
                "INSERT INTO notes (id,body,company_id,person_id,opportunity_id) VALUES (?,?,?,?,?)",
                (_uid("note_"), "Interested in annual plan.", co, pe, opp),
            )
            conn.execute(
                "INSERT INTO roles (id,name,permissions_json) VALUES (?,?,?)",
                ("role_admin", "Admin", json.dumps(["*"])),
            )
            conn.execute(
                "INSERT INTO roles (id,name,permissions_json) VALUES (?,?,?)",
                ("role_member", "Member", json.dumps(["read", "write"])),
            )
            conn.execute(
                "INSERT INTO members (id,email,role_id,display_name) VALUES (?,?,?,?)",
                (_uid("mem_"), "owner@sovereign.local", "role_admin", "Owner"),
            )
            conn.execute(
                "INSERT OR REPLACE INTO workspace_settings (key,value_json) VALUES (?,?)",
                ("workspace", json.dumps({"name": "Sovereign CRM", "theme": "system", "locale": "en-US"})),
            )
            conn.execute(
                "INSERT OR IGNORE INTO crm_credits (id,workflow_credits,ai_credits,seat_plan,seat_count) VALUES (1,1000,500,'free',1)"
            )
            conn.execute(
                "INSERT INTO activities (id,object_type,object_id,activity_type,summary) VALUES (?,?,?,?,?)",
                (_uid("act_"), "company", co, "created", "Seeded Acme Robotics"),
            )

    # ---- generic REST-like ----
    def list_records(
        self,
        table: str,
        filters: Optional[Dict[str, Any]] = None,
        sort: Optional[List[Tuple[str, str]]] = None,
        group_by: Optional[str] = None,
        limit: int = 200,
    ) -> Dict[str, Any]:
        allowed = {
            "companies", "people", "opportunities", "tasks", "notes", "favorites",
            "activities", "attachments", "custom_objects", "object_records",
            "saved_views", "pipeline_stages", "workflows", "workflow_runs",
            "emails", "calendar_events", "crm_dashboards", "members", "import_jobs",
        }
        if table not in allowed:
            raise ValueError(f"Unknown table {table}")
        clauses, params = [], []
        for k, v in (filters or {}).items():
            clauses.append(f"{k} = ?")
            params.append(v)
        where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
        order = ""
        if sort:
            parts = [f"{c} {'DESC' if d.upper()=='DESC' else 'ASC'}" for c, d in sort]
            order = " ORDER BY " + ", ".join(parts)
        with self._conn() as conn:
            rows = conn.execute(
                f"SELECT * FROM {table}{where}{order} LIMIT ?", (*params, limit)
            ).fetchall()
        items = [_row(r) for r in rows]
        groups = None
        if group_by and items:
            groups = {}
            for it in items:
                key = str(it.get(group_by, ""))
                groups.setdefault(key, []).append(it)
        return {"object": table, "count": len(items), "records": items, "groups": groups, "status": "OK"}

    def get_record(self, table: str, record_id: str) -> Dict[str, Any]:
        with self._conn() as conn:
            row = conn.execute(f"SELECT * FROM {table} WHERE id = ?", (record_id,)).fetchone()
        if not row:
            return {"error": "not found", "status": "ERROR"}
        return {"record": _row(row), "status": "OK"}

    def create_record(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        rid = data.get("id") or _uid(table[:3] + "_")
        data = {**data, "id": rid}
        cols = list(data.keys())
        placeholders = ",".join("?" for _ in cols)
        with self._conn() as conn:
            conn.execute(
                f"INSERT INTO {table} ({','.join(cols)}) VALUES ({placeholders})",
                [data[c] for c in cols],
            )
            self._log_activity(conn, table.rstrip("s") if table.endswith("ies") else table.rstrip("s"),
                               rid, "created", f"Created {table} {rid}")
        return {"id": rid, "status": "OK"}

    def update_record(self, table: str, record_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        data = {k: v for k, v in data.items() if k != "id"}
        if not data:
            return {"id": record_id, "status": "OK"}
        sets = ", ".join(f"{k}=?" for k in data)
        with self._conn() as conn:
            if table == "opportunities" and "stage" in data:
                data["stage_entered_at"] = _now()
                sets = ", ".join(f"{k}=?" for k in data)
            conn.execute(
                f"UPDATE {table} SET {sets} WHERE id=?",
                [*data.values(), record_id],
            )
            self._log_activity(conn, table, record_id, "updated", f"Updated fields {list(data)}")
        return {"id": record_id, "status": "OK"}

    def delete_record(self, table: str, record_id: str) -> Dict[str, Any]:
        with self._conn() as conn:
            conn.execute(f"DELETE FROM {table} WHERE id=?", (record_id,))
        return {"id": record_id, "deleted": True, "status": "OK"}

    def _log_activity(self, conn, object_type: str, object_id: str, activity_type: str, summary: str) -> None:
        try:
            conn.execute(
                "INSERT INTO activities (id,object_type,object_id,activity_type,summary) VALUES (?,?,?,?,?)",
                (_uid("act_"), object_type, object_id, activity_type, summary),
            )
        except Exception:
            pass

    # ---- companies / people / opportunities / tasks / notes ----
    def create_company(self, **kw) -> Dict[str, Any]:
        return self.create_record("companies", kw)

    def create_person(self, **kw) -> Dict[str, Any]:
        return self.create_record("people", kw)

    def create_opportunity(self, **kw) -> Dict[str, Any]:
        return self.create_record("opportunities", kw)

    def create_task(self, **kw) -> Dict[str, Any]:
        return self.create_record("tasks", kw)

    def create_note(self, **kw) -> Dict[str, Any]:
        return self.create_record("notes", kw)

    def add_favorite(self, user_id: str, object_type: str, object_id: str, label: str = "") -> Dict[str, Any]:
        return self.create_record(
            "favorites",
            {"user_id": user_id, "object_type": object_type, "object_id": object_id, "label": label},
        )

    def record_detail(self, object_type: str, object_id: str) -> Dict[str, Any]:
        table_map = {
            "company": "companies", "person": "people", "opportunity": "opportunities",
            "task": "tasks", "note": "notes",
        }
        table = table_map.get(object_type, object_type)
        base = self.get_record(table, object_id)
        if base.get("status") != "OK":
            return base
        timeline = self.timeline(object_type, object_id)
        with self._conn() as conn:
            atts = [_row(r) for r in conn.execute(
                "SELECT * FROM attachments WHERE object_type=? AND object_id=?",
                (object_type, object_id),
            ).fetchall()]
            related = {}
            if object_type == "company":
                related["people"] = [_row(r) for r in conn.execute(
                    "SELECT * FROM people WHERE company_id=?", (object_id,)
                ).fetchall()]
                related["opportunities"] = [_row(r) for r in conn.execute(
                    "SELECT * FROM opportunities WHERE company_id=?", (object_id,)
                ).fetchall()]
        return {
            "record": base["record"],
            "tabs": ["overview", "timeline", "tasks", "notes", "files"],
            "timeline": timeline["activities"],
            "attachments": atts,
            "related": related,
            "status": "OK",
        }

    def timeline(self, object_type: str, object_id: str) -> Dict[str, Any]:
        with self._conn() as conn:
            rows = conn.execute(
                """SELECT * FROM activities WHERE object_type=? AND object_id=?
                   ORDER BY created_at DESC LIMIT 100""",
                (object_type, object_id),
            ).fetchall()
        return {"activities": [_row(r) for r in rows], "status": "OK"}

    def attach_file(
        self, object_type: str, object_id: str, filename: str, content: bytes, mime_type: str = "application/octet-stream"
    ) -> Dict[str, Any]:
        root = Path(self.db_path).parent if self.db_path else Path("data")
        dest_dir = root / "crm_attachments"
        dest_dir.mkdir(parents=True, exist_ok=True)
        aid = _uid("att_")
        path = dest_dir / f"{aid}_{filename}"
        path.write_bytes(content)
        with self._conn() as conn:
            conn.execute(
                """INSERT INTO attachments (id,object_type,object_id,filename,path,mime_type,size_bytes)
                   VALUES (?,?,?,?,?,?,?)""",
                (aid, object_type, object_id, filename, str(path), mime_type, len(content)),
            )
            self._log_activity(conn, object_type, object_id, "attachment", f"Attached {filename}")
        return {"id": aid, "path": str(path), "status": "OK"}

    # ---- views ----
    def table_view(self, object_name: str, filters=None, sort=None, group_by=None, columns=None) -> Dict[str, Any]:
        table = object_name if object_name.endswith("s") else object_name + "s"
        if object_name == "people":
            table = "people"
        elif object_name == "companies":
            table = "companies"
        elif object_name == "opportunities":
            table = "opportunities"
        elif object_name == "tasks":
            table = "tasks"
        out = self.list_records(table, filters=filters, sort=sort, group_by=group_by)
        out["view_type"] = "table"
        out["columns"] = columns or list((out["records"][0] or {}).keys()) if out["records"] else []
        return out

    def kanban_view(self, object_name: str = "opportunities") -> Dict[str, Any]:
        with self._conn() as conn:
            stages = [_row(r) for r in conn.execute(
                "SELECT * FROM pipeline_stages ORDER BY position"
            ).fetchall()]
            opps = [_row(r) for r in conn.execute("SELECT * FROM opportunities").fetchall()]
        board = {s["name"]: [] for s in stages}
        for o in opps:
            board.setdefault(o.get("stage") or "NEW", []).append(o)
        return {"view_type": "kanban", "stages": stages, "columns": board, "status": "OK"}

    def calendar_view(self, month: Optional[str] = None) -> Dict[str, Any]:
        with self._conn() as conn:
            tasks = [_row(r) for r in conn.execute(
                "SELECT * FROM tasks WHERE due_date IS NOT NULL"
            ).fetchall()]
            events = [_row(r) for r in conn.execute("SELECT * FROM calendar_events").fetchall()]
        return {"view_type": "calendar", "month": month or datetime.utcnow().strftime("%Y-%m"),
                "tasks": tasks, "events": events, "status": "OK"}

    def save_view(self, name: str, object_name: str, view_type: str = "table", **kw) -> Dict[str, Any]:
        payload = {
            "name": name, "object_name": object_name, "view_type": view_type,
            "icon": kw.get("icon", "table"),
            "visibility": kw.get("visibility", "workspace"),
            "columns_json": json.dumps(kw.get("columns", [])),
            "filters_json": json.dumps(kw.get("filters", [])),
            "sort_json": json.dumps(kw.get("sort", [])),
            "group_by": kw.get("group_by"),
            "restricted_roles_json": json.dumps(kw.get("restricted_roles", [])),
            "owner_id": kw.get("owner_id"),
        }
        return self.create_record("saved_views", payload)

    def pipeline_expected_amount(self) -> Dict[str, Any]:
        with self._conn() as conn:
            rows = conn.execute("SELECT stage, amount, probability FROM opportunities").fetchall()
            stages = {r["name"]: r["probability"] for r in conn.execute("SELECT name, probability FROM pipeline_stages")}
        weighted = 0.0
        by_stage: Dict[str, float] = {}
        for r in rows:
            prob = r["probability"] if r["probability"] is not None else stages.get(r["stage"], 0.1)
            w = float(r["amount"] or 0) * float(prob or 0)
            weighted += w
            by_stage[r["stage"]] = by_stage.get(r["stage"], 0) + w
        return {"expected_amount": round(weighted, 2), "by_stage": by_stage, "status": "OK"}

    def time_in_stage(self, opportunity_id: Optional[str] = None) -> Dict[str, Any]:
        with self._conn() as conn:
            if opportunity_id:
                rows = conn.execute(
                    "SELECT id, name, stage, stage_entered_at FROM opportunities WHERE id=?",
                    (opportunity_id,),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT id, name, stage, stage_entered_at FROM opportunities"
                ).fetchall()
        now = datetime.utcnow()
        out = []
        for r in rows:
            entered = r["stage_entered_at"] or _now()
            try:
                dt = datetime.strptime(entered[:19], "%Y-%m-%d %H:%M:%S")
            except ValueError:
                dt = now
            hours = round((now - dt).total_seconds() / 3600, 2)
            out.append({"id": r["id"], "name": r["name"], "stage": r["stage"], "hours_in_stage": hours})
        return {"records": out, "status": "OK"}

    def set_pipeline_stages(self, stages: List[Dict[str, Any]]) -> Dict[str, Any]:
        with self._conn() as conn:
            conn.execute("DELETE FROM pipeline_stages")
            for i, s in enumerate(stages):
                conn.execute(
                    "INSERT INTO pipeline_stages (id,name,position,probability,color) VALUES (?,?,?,?,?)",
                    (s.get("id") or _uid("stg_"), s["name"], s.get("position", i),
                     s.get("probability", 0.1), s.get("color")),
                )
        return {"count": len(stages), "status": "OK"}

    # ---- custom data model ----
    def create_custom_object(self, name: str, label: str = "", description: str = "") -> Dict[str, Any]:
        return self.create_record(
            "custom_objects",
            {"name": name, "label": label or name, "description": description},
        )

    def add_custom_field(
        self, object_name: str, field_name: str, field_type: str = "text",
        unique: bool = False, relation_target: str = None, relation_kind: str = None, formula: str = None,
    ) -> Dict[str, Any]:
        fid = _uid("fld_")
        with self._conn() as conn:
            existing = conn.execute(
                "SELECT id FROM custom_fields WHERE object_name=? AND field_name=?",
                (object_name, field_name),
            ).fetchone()
            if existing:
                if unique:
                    conn.execute(
                        "UPDATE custom_fields SET unique_constraint=1, field_type=? WHERE id=?",
                        (field_type, existing["id"]),
                    )
                return {"id": existing["id"], "status": "OK", "existing": True}
            conn.execute(
                """INSERT INTO custom_fields
                   (id,object_name,field_name,field_type,unique_constraint,relation_target,relation_kind,formula)
                   VALUES (?,?,?,?,?,?,?,?)""",
                (fid, object_name, field_name, field_type, 1 if unique else 0,
                 relation_target, relation_kind, formula),
            )
        return {"id": fid, "status": "OK"}

    def create_object_record(self, object_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        with self._conn() as conn:
            unique_fields = conn.execute(
                "SELECT field_name FROM custom_fields WHERE object_name=? AND unique_constraint=1",
                (object_name,),
            ).fetchall()
            for uf in unique_fields:
                fname = uf["field_name"]
                if fname in data:
                    existing = conn.execute(
                        "SELECT id, data_json FROM object_records WHERE object_name=?",
                        (object_name,),
                    ).fetchall()
                    for ex in existing:
                        if json.loads(ex["data_json"]).get(fname) == data[fname]:
                            return {"error": f"unique constraint on {fname}", "status": "ERROR"}
        return self.create_record(
            "object_records",
            {"object_name": object_name, "data_json": json.dumps(data)},
        )

    def evaluate_formula(self, object_name: str, record_id: str, field_name: str) -> Dict[str, Any]:
        with self._conn() as conn:
            fld = conn.execute(
                "SELECT formula FROM custom_fields WHERE object_name=? AND field_name=?",
                (object_name, field_name),
            ).fetchone()
            rec = conn.execute("SELECT data_json FROM object_records WHERE id=?", (record_id,)).fetchone()
        if not fld or not fld["formula"] or not rec:
            return {"value": None, "status": "OK"}
        data = json.loads(rec["data_json"])
        # simple formula: amount * 1.1 style
        try:
            env = {k: float(v) if isinstance(v, (int, float, str)) and str(v).replace(".", "", 1).isdigit() else v
                   for k, v in data.items()}
            value = eval(fld["formula"], {"__builtins__": {}}, env)  # noqa: S307 — local CRM formula
        except Exception as e:
            return {"error": str(e), "status": "ERROR"}
        return {"value": value, "status": "OK"}

    def set_page_layout(self, object_name: str, tabs: List, widgets: List) -> Dict[str, Any]:
        lid = _uid("lay_")
        with self._conn() as conn:
            conn.execute("DELETE FROM page_layouts WHERE object_name=?", (object_name,))
            conn.execute(
                "INSERT INTO page_layouts (id,object_name,tabs_json,widgets_json) VALUES (?,?,?,?)",
                (lid, object_name, json.dumps(tabs), json.dumps(widgets)),
            )
        return {"id": lid, "status": "OK"}

    # ---- email / calendar ----
    def connect_mailbox(self, user_id: str, email: str, import_filter: str = "") -> Dict[str, Any]:
        return self.create_record(
            "mailbox_accounts",
            {"user_id": user_id, "email": email, "provider": "mock", "import_filter": import_filter},
        )

    def sync_emails(self, mailbox_id: str, object_type: str = None, object_id: str = None) -> Dict[str, Any]:
        eid = _uid("em_")
        with self._conn() as conn:
            mb = conn.execute("SELECT * FROM mailbox_accounts WHERE id=?", (mailbox_id,)).fetchone()
            if not mb:
                return {"error": "mailbox not found", "status": "ERROR"}
            filt = mb["import_filter"] or ""
            subject = f"Follow-up {filt}".strip() or "Mock synced email"
            conn.execute(
                """INSERT INTO emails (id,mailbox_id,subject,body,from_addr,to_addr,object_type,object_id,direction)
                   VALUES (?,?,?,?,?,?,?,?,?)""",
                (eid, mailbox_id, subject, "Mock body from sync", "client@example.com",
                 mb["email"], object_type, object_id, "inbound"),
            )
            if object_type and object_id:
                self._log_activity(conn, object_type, object_id, "email", subject)
        return {"email_id": eid, "imported": 1, "status": "OK"}

    def sync_calendar(self, title: str, starts_at: str, person_id: str = None, company_id: str = None) -> Dict[str, Any]:
        return self.create_record(
            "calendar_events",
            {"title": title, "starts_at": starts_at, "ends_at": starts_at,
             "person_id": person_id, "company_id": company_id, "source": "mock"},
        )

    def email_count_for_person(self, person_id: str) -> Dict[str, Any]:
        with self._conn() as conn:
            pe = conn.execute("SELECT email FROM people WHERE id=?", (person_id,)).fetchone()
            c = 0
            if pe and pe["email"]:
                c = conn.execute(
                    "SELECT COUNT(*) AS c FROM emails WHERE from_addr=? OR to_addr=? OR object_id=?",
                    (pe["email"], pe["email"], person_id),
                ).fetchone()["c"]
        return {"person_id": person_id, "email_count": c, "status": "OK"}

    # ---- workflows ----
    def create_workflow(self, name: str, trigger: Dict, actions: List, branches: List = None, status: str = "draft") -> Dict[str, Any]:
        return self.create_record(
            "workflows",
            {
                "name": name,
                "status": status,
                "trigger_json": json.dumps(trigger),
                "actions_json": json.dumps(actions),
                "branches_json": json.dumps(branches or []),
            },
        )

    def publish_workflow(self, workflow_id: str) -> Dict[str, Any]:
        with self._conn() as conn:
            conn.execute(
                "UPDATE workflows SET status='active', version=version+1, updated_at=? WHERE id=?",
                (_now(), workflow_id),
            )
        return {"id": workflow_id, "status": "OK"}

    def run_workflow(self, workflow_id: str, payload: Optional[Dict] = None) -> Dict[str, Any]:
        with self._conn() as conn:
            wf = conn.execute("SELECT * FROM workflows WHERE id=?", (workflow_id,)).fetchone()
            if not wf:
                return {"error": "workflow not found", "status": "ERROR"}
            actions = json.loads(wf["actions_json"] or "[]")
            branches = json.loads(wf["branches_json"] or "[]")
            results = []
            for action in actions:
                results.append(self._exec_action(conn, action, payload or {}))
            for br in branches:
                cond = br.get("when")
                ok = True
                if cond and payload:
                    ok = payload.get(cond.get("field")) == cond.get("equals")
                if ok:
                    for action in br.get("actions", []):
                        results.append(self._exec_action(conn, action, payload or {}))
            # iterator
            for action in actions:
                if action.get("type") == "iterate":
                    items = (payload or {}).get(action.get("over", "items"), [])
                    for item in items:
                        for sub in action.get("actions", []):
                            results.append(self._exec_action(conn, sub, item if isinstance(item, dict) else {"item": item}))
            rid = _uid("run_")
            conn.execute(
                """INSERT INTO workflow_runs (id,workflow_id,status,trigger_payload,result_json,finished_at)
                   VALUES (?,?,?,?,?,?)""",
                (rid, workflow_id, "succeeded", json.dumps(payload or {}), json.dumps(results), _now()),
            )
            conn.execute(
                "UPDATE workflows SET credits_used=credits_used+1 WHERE id=?", (workflow_id,)
            )
            conn.execute(
                "UPDATE crm_credits SET workflow_credits=MAX(0, workflow_credits-1) WHERE id=1"
            )
        return {"run_id": rid, "results": results, "status": "OK"}

    def _exec_action(self, conn, action: Dict, payload: Dict) -> Dict[str, Any]:
        at = action.get("type")
        if at == "create_task":
            tid = _uid("tsk_")
            conn.execute(
                "INSERT INTO tasks (id,title,status,due_date,company_id,opportunity_id) VALUES (?,?,?,?,?,?)",
                (tid, action.get("title", "Auto task"), "TODO", action.get("due_date"),
                 payload.get("company_id"), payload.get("opportunity_id")),
            )
            return {"type": at, "task_id": tid}
        if at == "update_record":
            table = action.get("table", "opportunities")
            rid = action.get("id") or payload.get("id")
            fields = action.get("fields", {})
            if rid and fields:
                sets = ", ".join(f"{k}=?" for k in fields)
                conn.execute(f"UPDATE {table} SET {sets} WHERE id=?", [*fields.values(), rid])
            return {"type": at, "id": rid}
        if at == "send_email":
            eid = _uid("em_")
            conn.execute(
                """INSERT INTO emails (id,subject,body,from_addr,to_addr,direction)
                   VALUES (?,?,?,?,?,?)""",
                (eid, action.get("subject", "Workflow email"), action.get("body", ""),
                 "crm@sovereign.local", action.get("to") or payload.get("email", "user@example.com"), "outbound"),
            )
            return {"type": at, "email_id": eid}
        if at == "notify":
            return {"type": at, "message": action.get("message", "notify"), "logged": True}
        if at == "http":
            return {"type": at, "url": action.get("url"), "simulated": True, "status_code": 200}
        if at == "code":
            return {"type": at, "result": action.get("result", list(range(3)))}
        if at == "ai":
            return {"type": at, "reply": f"AI stub for: {action.get('prompt', '')}"}
        if at == "create_invoice_hook":
            return {"type": at, "invoice_stub": True, "amount": payload.get("amount", 0)}
        if at == "attach_pdf":
            return {"type": at, "pdf": "quote.pdf", "attached": True}
        return {"type": at or "noop", "ok": True}

    def detect_stale_opportunities(self, days: int = 14) -> Dict[str, Any]:
        cutoff = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
        with self._conn() as conn:
            rows = [_row(r) for r in conn.execute(
                """SELECT * FROM opportunities WHERE stage NOT IN ('CLOSED_WON','CLOSED_LOST')
                   AND stage_entered_at < ?""",
                (cutoff,),
            ).fetchall()]
        return {"stale": rows, "count": len(rows), "status": "OK"}

    def task_due_alerts(self) -> Dict[str, Any]:
        today = datetime.utcnow().strftime("%Y-%m-%d")
        with self._conn() as conn:
            rows = [_row(r) for r in conn.execute(
                "SELECT * FROM tasks WHERE status!='DONE' AND due_date IS NOT NULL AND due_date<=?",
                (today,),
            ).fetchall()]
            for t in rows:
                conn.execute(
                    """INSERT INTO emails (id,subject,body,from_addr,to_addr,direction)
                       VALUES (?,?,?,?,?,?)""",
                    (_uid("em_"), f"Task due: {t['title']}", "Reminder", "crm@sovereign.local",
                     "owner@sovereign.local", "outbound"),
                )
        return {"alerts": len(rows), "tasks": rows, "status": "OK"}

    # ---- AI ----
    def ai_chat(self, message: str) -> Dict[str, Any]:
        with self._conn() as conn:
            cos = conn.execute("SELECT COUNT(*) AS c FROM companies").fetchone()["c"]
            opps = conn.execute("SELECT COUNT(*) AS c FROM opportunities").fetchone()["c"]
            expected = self.pipeline_expected_amount()["expected_amount"]
            conn.execute("UPDATE crm_credits SET ai_credits=MAX(0, ai_credits-1) WHERE id=1")
        reply = (
            f"CRM context: {cos} companies, {opps} opportunities, "
            f"pipeline expected ${expected:,.2f}. Re: {message[:120]}"
        )
        return {"reply": reply, "engine": "crm_stub", "status": "OK"}

    def ai_enrich(self, company_id: str) -> Dict[str, Any]:
        with self._conn() as conn:
            co = conn.execute("SELECT * FROM companies WHERE id=?", (company_id,)).fetchone()
            if not co:
                return {"error": "not found", "status": "ERROR"}
            suggestion = {"industry": co["industry"] or "Technology", "employees": co["employees"] or 10}
            conn.execute(
                "UPDATE companies SET custom_json=? WHERE id=?",
                (json.dumps({"enrichment": suggestion}), company_id),
            )
        return {"company_id": company_id, "suggestion": suggestion, "status": "OK"}

    # ---- dashboards ----
    def create_dashboard(self, name: str, tabs: List = None) -> Dict[str, Any]:
        return self.create_record(
            "crm_dashboards",
            {"name": name, "tabs_json": json.dumps(tabs or ["Overview"])},
        )

    def add_widget(self, dashboard_id: str, widget_type: str, title: str, settings: Dict = None) -> Dict[str, Any]:
        return self.create_record(
            "crm_widgets",
            {
                "dashboard_id": dashboard_id,
                "widget_type": widget_type,
                "title": title,
                "settings_json": json.dumps(settings or {}),
            },
        )

    def gtm_performance(self) -> Dict[str, Any]:
        expected = self.pipeline_expected_amount()
        with self._conn() as conn:
            won = conn.execute(
                "SELECT COALESCE(SUM(amount),0) AS s FROM opportunities WHERE stage='CLOSED_WON'"
            ).fetchone()["s"]
        return {"expected": expected["expected_amount"], "won": won, "status": "OK"}

    # ---- RBAC / workspace ----
    def set_role_permissions(self, role_id: str, permissions: List[str]) -> Dict[str, Any]:
        with self._conn() as conn:
            conn.execute(
                "UPDATE roles SET permissions_json=? WHERE id=?",
                (json.dumps(permissions), role_id),
            )
        return {"role_id": role_id, "status": "OK"}

    def invite_member(self, email: str, role_id: str = "role_member", display_name: str = "") -> Dict[str, Any]:
        return self.create_record(
            "members",
            {"email": email, "role_id": role_id, "display_name": display_name or email.split("@")[0]},
        )

    def set_workspace(self, key: str, value: Any) -> Dict[str, Any]:
        with self._conn() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO workspace_settings (key,value_json) VALUES (?,?)",
                (key, json.dumps(value)),
            )
        return {"key": key, "status": "OK"}

    def get_workspace(self, key: str) -> Dict[str, Any]:
        with self._conn() as conn:
            row = conn.execute("SELECT value_json FROM workspace_settings WHERE key=?", (key,)).fetchone()
        return {"key": key, "value": json.loads(row["value_json"]) if row else None, "status": "OK"}

    def set_sso_config(self, provider: str, metadata: Dict) -> Dict[str, Any]:
        return self.set_workspace("sso", {"provider": provider, "metadata": metadata, "enabled": True})

    def check_permission(self, member_email: str, permission: str) -> Dict[str, Any]:
        with self._conn() as conn:
            m = conn.execute("SELECT role_id FROM members WHERE email=?", (member_email,)).fetchone()
            if not m:
                return {"allowed": False, "status": "OK"}
            role = conn.execute("SELECT permissions_json FROM roles WHERE id=?", (m["role_id"],)).fetchone()
            perms = json.loads(role["permissions_json"]) if role else []
        allowed = "*" in perms or permission in perms
        return {"allowed": allowed, "status": "OK"}

    def row_level_filter(self, member_email: str, table: str) -> Dict[str, Any]:
        # org-tier parity: owner sees all; others filtered by owner_id if present
        with self._conn() as conn:
            m = conn.execute("SELECT id, role_id FROM members WHERE email=?", (member_email,)).fetchone()
            if not m:
                return {"records": [], "status": "OK"}
            if m["role_id"] == "role_admin":
                rows = conn.execute(f"SELECT * FROM {table} LIMIT 50").fetchall()
            else:
                try:
                    rows = conn.execute(
                        f"SELECT * FROM {table} WHERE owner_id=? LIMIT 50", (m["id"],)
                    ).fetchall()
                except Exception:
                    rows = conn.execute(f"SELECT * FROM {table} LIMIT 50").fetchall()
        return {"records": [_row(r) for r in rows], "status": "OK"}

    # ---- import / export ----
    def import_csv(
        self, object_name: str, csv_text: str, mapping: Dict[str, str], update_existing: bool = False
    ) -> Dict[str, Any]:
        reader = csv.DictReader(io.StringIO(csv_text))
        table = {"companies": "companies", "people": "people", "opportunities": "opportunities"}.get(
            object_name, "object_records"
        )
        ok, fail, errors = 0, 0, []
        job_id = _uid("imp_")
        with self._conn() as conn:
            for i, row in enumerate(reader):
                try:
                    data = {dest: row.get(src, "") for src, dest in mapping.items()}
                    if table == "object_records":
                        conn.execute(
                            "INSERT INTO object_records (id,object_name,data_json) VALUES (?,?,?)",
                            (_uid("or_"), object_name, json.dumps(data)),
                        )
                    else:
                        rid = data.get("id") or _uid(table[:3] + "_")
                        data["id"] = rid
                        if update_existing and "domain" in data and table == "companies":
                            ex = conn.execute(
                                "SELECT id FROM companies WHERE domain=?", (data["domain"],)
                            ).fetchone()
                            if ex:
                                sets = ", ".join(f"{k}=?" for k in data if k != "id")
                                vals = [data[k] for k in data if k != "id"]
                                conn.execute(f"UPDATE companies SET {sets} WHERE id=?", [*vals, ex["id"]])
                                ok += 1
                                continue
                        cols = list(data.keys())
                        conn.execute(
                            f"INSERT INTO {table} ({','.join(cols)}) VALUES ({','.join('?' for _ in cols)})",
                            [data[c] for c in cols],
                        )
                    ok += 1
                except Exception as e:
                    fail += 1
                    errors.append({"row": i, "error": str(e)})
            conn.execute(
                """INSERT INTO import_jobs (id,object_name,status,mapping_json,errors_json,rows_ok,rows_fail)
                   VALUES (?,?,?,?,?,?,?)""",
                (job_id, object_name, "done" if fail == 0 else "partial",
                 json.dumps(mapping), json.dumps(errors), ok, fail),
            )
        return {"job_id": job_id, "rows_ok": ok, "rows_fail": fail, "errors": errors, "status": "OK"}

    def export_csv(self, table: str) -> Dict[str, Any]:
        data = self.list_records(table)
        if not data["records"]:
            return {"csv": "", "count": 0, "status": "OK"}
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=list(data["records"][0].keys()))
        writer.writeheader()
        writer.writerows(data["records"])
        return {"csv": buf.getvalue(), "count": data["count"], "status": "OK"}

    # ---- API / webhooks / apps ----
    def create_api_key(self, name: str, scopes: List[str] = None) -> Dict[str, Any]:
        raw = uuid.uuid4().hex
        kid = _uid("key_")
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO api_keys (id,name,key_hash,scopes_json) VALUES (?,?,?,?)",
                (kid, name, raw, json.dumps(scopes or ["read", "write"])),
            )
        return {"id": kid, "api_key": raw, "status": "OK"}

    def create_webhook(self, url: str, events: List[str] = None) -> Dict[str, Any]:
        return self.create_record(
            "webhooks",
            {"url": url, "events_json": json.dumps(events or ["record.created"])},
        )

    def install_app(self, name: str, manifest: Dict = None) -> Dict[str, Any]:
        return self.create_record(
            "apps_extensions",
            {"name": name, "manifest_json": json.dumps(manifest or {}), "status": "installed"},
        )

    def app_kv_set(self, app_id: str, key: str, value: Any) -> Dict[str, Any]:
        with self._conn() as conn:
            row = conn.execute("SELECT kv_store_json FROM apps_extensions WHERE id=?", (app_id,)).fetchone()
            if not row:
                return {"error": "app not found", "status": "ERROR"}
            store = json.loads(row["kv_store_json"] or "{}")
            store[key] = value
            conn.execute("UPDATE apps_extensions SET kv_store_json=? WHERE id=?", (json.dumps(store), app_id))
        return {"key": key, "status": "OK"}

    def command_palette_search(self, q: str) -> Dict[str, Any]:
        ql = f"%{q.lower()}%"
        with self._conn() as conn:
            cos = [_row(r) for r in conn.execute(
                "SELECT id,name,'company' AS kind FROM companies WHERE lower(name) LIKE ? LIMIT 10", (ql,)
            ).fetchall()]
            pe = [_row(r) for r in conn.execute(
                "SELECT id, first_name||' '||last_name AS name, 'person' AS kind FROM people WHERE lower(email) LIKE ? OR lower(first_name) LIKE ? LIMIT 10",
                (ql, ql),
            ).fetchall()]
            opps = [_row(r) for r in conn.execute(
                "SELECT id,name,'opportunity' AS kind FROM opportunities WHERE lower(name) LIKE ? LIMIT 10", (ql,)
            ).fetchall()]
        return {"results": cos + pe + opps, "status": "OK"}

    def bulk_action(self, table: str, ids: List[str], action: str) -> Dict[str, Any]:
        with self._conn() as conn:
            if action == "delete":
                for i in ids:
                    conn.execute(f"DELETE FROM {table} WHERE id=?", (i,))
            elif action == "export":
                return self.export_csv(table)
        return {"action": action, "count": len(ids), "status": "OK"}

    def set_seat_plan(self, plan: str, seats: int) -> Dict[str, Any]:
        with self._conn() as conn:
            conn.execute(
                "UPDATE crm_credits SET seat_plan=?, seat_count=? WHERE id=1", (plan, seats)
            )
        return {"plan": plan, "seats": seats, "status": "OK"}

    def credits_balance(self) -> Dict[str, Any]:
        with self._conn() as conn:
            row = conn.execute("SELECT * FROM crm_credits WHERE id=1").fetchone()
        return {"balance": _row(row), "status": "OK"}

    def graphql_query_stub(self, query: str) -> Dict[str, Any]:
        # persist query log via activity; return companies list for { companies { id name } }
        data = self.list_records("companies", limit=20)
        with self._conn() as conn:
            self._log_activity(conn, "workspace", "graphql", "graphql", query[:200])
        return {"data": {"companies": data["records"]}, "status": "OK"}

    def mcp_tools_list(self) -> Dict[str, Any]:
        tools = ["crm.list", "crm.get", "crm.create", "crm.update", "crm.search"]
        self.set_workspace("mcp_tools", tools)
        return {"tools": tools, "status": "OK"}
