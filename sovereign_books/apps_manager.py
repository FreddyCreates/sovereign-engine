"""
SQLite-backed App Deployment Manager — EAS / Fastlane / Vercel-class ops (simulated + persisted).
"""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from .db import db_session, init_db

APPS_SCHEMA = """
CREATE TABLE IF NOT EXISTS app_projects (
    id TEXT PRIMARY KEY, name TEXT NOT NULL, platforms_json TEXT DEFAULT '[]',
    git_url TEXT, expo_slug TEXT, android_module TEXT, eas_profiles_json TEXT DEFAULT '{}',
    team_access_json TEXT DEFAULT '[]', created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS builds (
    id TEXT PRIMARY KEY, project_id TEXT NOT NULL, platform TEXT NOT NULL,
    profile TEXT DEFAULT 'production', status TEXT NOT NULL DEFAULT 'queued',
    fingerprint TEXT, artifact_url TEXT, logs TEXT, runner TEXT DEFAULT 'cloud',
    git_ref TEXT, triggered_by TEXT, cache_hit INTEGER DEFAULT 0,
    started_at TEXT DEFAULT (datetime('now')), finished_at TEXT
);
CREATE TABLE IF NOT EXISTS releases (
    id TEXT PRIMARY KEY, project_id TEXT NOT NULL, build_id TEXT, version TEXT,
    channel TEXT DEFAULT 'production', rollout_pct REAL DEFAULT 100,
    status TEXT DEFAULT 'active', notes TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS store_submissions (
    id TEXT PRIMARY KEY, project_id TEXT NOT NULL, build_id TEXT, store TEXT NOT NULL,
    track TEXT DEFAULT 'internal', status TEXT DEFAULT 'pending',
    changelog TEXT, metadata_json TEXT DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT (datetime('now')), updated_at TEXT
);
CREATE TABLE IF NOT EXISTS web_deploys (
    id TEXT PRIMARY KEY, project_id TEXT NOT NULL, env TEXT DEFAULT 'preview',
    url TEXT, status TEXT DEFAULT 'building', git_ref TEXT, framework TEXT,
    bandwidth_mb REAL DEFAULT 0, created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS pipelines (
    id TEXT PRIMARY KEY, project_id TEXT NOT NULL, name TEXT NOT NULL,
    yaml_text TEXT NOT NULL, visual_json TEXT DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS pipeline_runs (
    id TEXT PRIMARY KEY, pipeline_id TEXT NOT NULL, status TEXT NOT NULL,
    trigger TEXT DEFAULT 'manual', logs TEXT, artifacts_json TEXT DEFAULT '[]',
    approval_required INTEGER DEFAULT 0, approved_by TEXT,
    started_at TEXT DEFAULT (datetime('now')), finished_at TEXT
);
CREATE TABLE IF NOT EXISTS signing_credentials (
    id TEXT PRIMARY KEY, project_id TEXT NOT NULL, kind TEXT NOT NULL,
    label TEXT, vault_ref TEXT, encrypted_blob TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS ota_channels (
    id TEXT PRIMARY KEY, project_id TEXT NOT NULL, name TEXT NOT NULL,
    runtime_policy TEXT DEFAULT 'sdkVersion', mapped_profile TEXT,
    UNIQUE(project_id, name)
);
CREATE TABLE IF NOT EXISTS ota_updates (
    id TEXT PRIMARY KEY, channel_id TEXT NOT NULL, project_id TEXT NOT NULL,
    bundle_hash TEXT, message TEXT, rollout_pct REAL DEFAULT 100,
    status TEXT DEFAULT 'active', insights_json TEXT DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS environments (
    id TEXT PRIMARY KEY, project_id TEXT NOT NULL, name TEXT NOT NULL,
    secrets_json TEXT DEFAULT '{}', UNIQUE(project_id, name)
);
CREATE TABLE IF NOT EXISTS app_secrets (
    id TEXT PRIMARY KEY, project_id TEXT NOT NULL, env_name TEXT NOT NULL,
    key TEXT NOT NULL, value TEXT NOT NULL, UNIQUE(project_id, env_name, key)
);
CREATE TABLE IF NOT EXISTS revenuecat_links (
    id TEXT PRIMARY KEY, project_id TEXT NOT NULL, public_sdk_key TEXT,
    products_json TEXT DEFAULT '[]', verified_purchase INTEGER DEFAULT 0,
    promo_checklist_json TEXT DEFAULT '[]',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS audit_log (
    id TEXT PRIMARY KEY, actor TEXT, action TEXT NOT NULL, target TEXT,
    detail_json TEXT DEFAULT '{}', created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS app_billing (
    id INTEGER PRIMARY KEY CHECK (id = 1), build_credits INTEGER DEFAULT 500,
    approve_seats INTEGER DEFAULT 3, pro_active INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS app_insights (
    id TEXT PRIMARY KEY, project_id TEXT NOT NULL, kind TEXT NOT NULL,
    data_json TEXT NOT NULL DEFAULT '{}', created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS distribution_links (
    id TEXT PRIMARY KEY, project_id TEXT NOT NULL, build_id TEXT, kind TEXT,
    url TEXT, cohort_json TEXT DEFAULT '[]',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS status_badges (
    id TEXT PRIMARY KEY, project_id TEXT NOT NULL, label TEXT, svg_text TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS app_webhooks (
    id TEXT PRIMARY KEY, project_id TEXT, url TEXT NOT NULL, events_json TEXT DEFAULT '[]',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
"""


def _uid(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:12]}"


def _row(r) -> Dict[str, Any]:
    return dict(r) if r else {}


def _now() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


class AppsManager:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path
        init_db(db_path)
        self._ensure_tables()
        self._seed_if_empty()

    def _conn(self):
        return db_session(self.db_path)

    def _ensure_tables(self) -> None:
        with self._conn() as conn:
            conn.executescript(APPS_SCHEMA)

    def _audit(self, conn, action: str, target: str = "", detail: Dict = None, actor: str = "system") -> None:
        conn.execute(
            "INSERT INTO audit_log (id,actor,action,target,detail_json) VALUES (?,?,?,?,?)",
            (_uid("aud_"), actor, action, target, json.dumps(detail or {})),
        )

    def _seed_if_empty(self) -> None:
        with self._conn() as conn:
            n = conn.execute("SELECT COUNT(*) AS c FROM app_projects").fetchone()["c"]
            if n:
                return
            android = _uid("proj_")
            web = _uid("proj_")
            conn.execute(
                """INSERT INTO app_projects (id,name,platforms_json,git_url,android_module,eas_profiles_json,team_access_json)
                   VALUES (?,?,?,?,?,?,?)""",
                (android, "Sovereign Books Android", json.dumps(["android"]),
                 "https://github.com/sovereign/sovereign-engine", "android-app",
                 json.dumps({"development": {}, "preview": {}, "production": {}}),
                 json.dumps([{"email": "owner@sovereign.local", "role": "admin"}])),
            )
            conn.execute(
                """INSERT INTO app_projects (id,name,platforms_json,git_url,expo_slug,eas_profiles_json,team_access_json)
                   VALUES (?,?,?,?,?,?,?)""",
                (web, "Sovereign Books Web", json.dumps(["web"]),
                 "https://github.com/sovereign/sovereign-engine", "sovereign-books-web",
                 json.dumps({"preview": {}, "production": {}}),
                 json.dumps([{"email": "owner@sovereign.local", "role": "admin"}])),
            )
            for pid, envs in ((android, ["development", "preview", "production"]),
                              (web, ["preview", "production"])):
                for e in envs:
                    conn.execute(
                        "INSERT INTO environments (id,project_id,name,secrets_json) VALUES (?,?,?,?)",
                        (_uid("env_"), pid, e, "{}"),
                    )
                conn.execute(
                    "INSERT INTO ota_channels (id,project_id,name,mapped_profile) VALUES (?,?,?,?)",
                    (_uid("ch_"), pid, "production", "production"),
                )
                conn.execute(
                    "INSERT INTO ota_channels (id,project_id,name,mapped_profile) VALUES (?,?,?,?)",
                    (_uid("ch_"), pid, "preview", "preview"),
                )
            conn.execute(
                "INSERT OR IGNORE INTO app_billing (id,build_credits,approve_seats,pro_active) VALUES (1,500,3,0)"
            )
            self._audit(conn, "seed", "workspace", {"android": android, "web": web})

    def create_project(
        self, name: str, platforms: List[str], git_url: str = "", **kw
    ) -> Dict[str, Any]:
        pid = _uid("proj_")
        with self._conn() as conn:
            conn.execute(
                """INSERT INTO app_projects
                   (id,name,platforms_json,git_url,expo_slug,android_module,eas_profiles_json,team_access_json)
                   VALUES (?,?,?,?,?,?,?,?)""",
                (pid, name, json.dumps(platforms), git_url, kw.get("expo_slug"),
                 kw.get("android_module"), json.dumps(kw.get("eas_profiles", {"production": {}})),
                 json.dumps(kw.get("team_access", []))),
            )
            for e in ("development", "preview", "production"):
                conn.execute(
                    "INSERT INTO environments (id,project_id,name) VALUES (?,?,?)",
                    (_uid("env_"), pid, e),
                )
            self._audit(conn, "project.create", pid, {"name": name})
        return {"id": pid, "status": "OK"}

    def list_projects(self) -> Dict[str, Any]:
        with self._conn() as conn:
            rows = [_row(r) for r in conn.execute("SELECT * FROM app_projects").fetchall()]
        return {"projects": rows, "count": len(rows), "status": "OK"}

    def project_dashboard(self, project_id: str) -> Dict[str, Any]:
        with self._conn() as conn:
            proj = conn.execute("SELECT * FROM app_projects WHERE id=?", (project_id,)).fetchone()
            build = conn.execute(
                "SELECT * FROM builds WHERE project_id=? ORDER BY started_at DESC LIMIT 1",
                (project_id,),
            ).fetchone()
            ota = conn.execute(
                """SELECT u.* FROM ota_updates u JOIN ota_channels c ON c.id=u.channel_id
                   WHERE u.project_id=? ORDER BY u.created_at DESC LIMIT 1""",
                (project_id,),
            ).fetchone()
            store = conn.execute(
                "SELECT * FROM store_submissions WHERE project_id=? ORDER BY created_at DESC LIMIT 1",
                (project_id,),
            ).fetchone()
            web = conn.execute(
                "SELECT * FROM web_deploys WHERE project_id=? AND env='production' ORDER BY created_at DESC LIMIT 1",
                (project_id,),
            ).fetchone()
        return {
            "project": _row(proj),
            "latest_build": _row(build),
            "latest_ota": _row(ota),
            "store_status": _row(store),
            "web_url": (_row(web) or {}).get("url"),
            "status": "OK",
        }

    def set_eas_profiles(self, project_id: str, profiles: Dict) -> Dict[str, Any]:
        with self._conn() as conn:
            conn.execute(
                "UPDATE app_projects SET eas_profiles_json=? WHERE id=?",
                (json.dumps(profiles), project_id),
            )
        return {"project_id": project_id, "status": "OK"}

    def set_team_access(self, project_id: str, access: List[Dict]) -> Dict[str, Any]:
        with self._conn() as conn:
            conn.execute(
                "UPDATE app_projects SET team_access_json=? WHERE id=?",
                (json.dumps(access), project_id),
            )
        return {"project_id": project_id, "status": "OK"}

    def trigger_build(
        self,
        project_id: str,
        platform: str = "android",
        profile: str = "production",
        git_ref: str = "main",
        runner: str = "cloud",
        succeed: bool = True,
        fingerprint: str = None,
        cache_hit: bool = False,
        triggered_by: str = "ui",
    ) -> Dict[str, Any]:
        bid = _uid("bld_")
        fp = fingerprint or hashlib.sha256(f"{project_id}:{platform}:{profile}".encode()).hexdigest()[:16]
        status = "succeeded" if succeed else "failed"
        artifact = f"https://artifacts.sovereign.local/{bid}.{'aab' if platform=='android' else 'ipa' if platform=='ios' else 'tgz'}"
        with self._conn() as conn:
            # reuse existing by fingerprint
            if fingerprint:
                existing = conn.execute(
                    "SELECT * FROM builds WHERE fingerprint=? AND status='succeeded' LIMIT 1",
                    (fingerprint,),
                ).fetchone()
                if existing:
                    self._audit(conn, "build.reuse", existing["id"], {"fingerprint": fingerprint})
                    return {"id": existing["id"], "reused": True, "status": "OK", "build": _row(existing)}
            conn.execute(
                """INSERT INTO builds
                   (id,project_id,platform,profile,status,fingerprint,artifact_url,logs,runner,git_ref,triggered_by,cache_hit,finished_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (bid, project_id, platform, profile, status, fp, artifact if succeed else None,
                 f"Build {status} on {runner}", runner, git_ref, triggered_by, 1 if cache_hit else 0, _now()),
            )
            conn.execute("UPDATE app_billing SET build_credits=MAX(0,build_credits-1) WHERE id=1")
            self._audit(conn, "build.trigger", bid, {"platform": platform, "status": status})
        return {"id": bid, "fingerprint": fp, "artifact_url": artifact if succeed else None,
                "build_status": status, "status": "OK"}

    def fingerprint_native(self, project_id: str, tree_digest: str) -> Dict[str, Any]:
        fp = hashlib.sha256(f"{project_id}:{tree_digest}".encode()).hexdigest()[:20]
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO app_insights (id,project_id,kind,data_json) VALUES (?,?,?,?)",
                (_uid("ins_"), project_id, "fingerprint", json.dumps({"fingerprint": fp, "digest": tree_digest})),
            )
        return {"fingerprint": fp, "status": "OK"}

    def get_build_by_fingerprint(self, fingerprint: str) -> Dict[str, Any]:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM builds WHERE fingerprint=? AND status='succeeded' ORDER BY started_at DESC LIMIT 1",
                (fingerprint,),
            ).fetchone()
        return {"build": _row(row), "status": "OK" if row else "ERROR"}

    def repack(self, build_id: str, js_bundle_hash: str) -> Dict[str, Any]:
        with self._conn() as conn:
            b = conn.execute("SELECT * FROM builds WHERE id=?", (build_id,)).fetchone()
            if not b:
                return {"error": "build not found", "status": "ERROR"}
            nid = _uid("bld_")
            conn.execute(
                """INSERT INTO builds
                   (id,project_id,platform,profile,status,fingerprint,artifact_url,logs,runner,git_ref,triggered_by,finished_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                (nid, b["project_id"], b["platform"], b["profile"], "succeeded",
                 b["fingerprint"], f"https://artifacts.sovereign.local/{nid}-repack.aab",
                 f"Repack JS {js_bundle_hash}", "repack", b["git_ref"], "repack", _now()),
            )
            self._audit(conn, "build.repack", nid, {"from": build_id})
        return {"id": nid, "repack": True, "status": "OK"}

    def provision_credentials(self, project_id: str, kind: str, label: str) -> Dict[str, Any]:
        cid = _uid("cred_")
        with self._conn() as conn:
            conn.execute(
                """INSERT INTO signing_credentials (id,project_id,kind,label,vault_ref,encrypted_blob)
                   VALUES (?,?,?,?,?,?)""",
                (cid, project_id, kind, label, f"vault://{cid}", "enc:" + uuid.uuid4().hex),
            )
            self._audit(conn, "credentials.provision", cid, {"kind": kind})
        return {"id": cid, "status": "OK"}

    def upload_credentials(self, project_id: str, kind: str, label: str, blob: str) -> Dict[str, Any]:
        cid = _uid("cred_")
        with self._conn() as conn:
            conn.execute(
                """INSERT INTO signing_credentials (id,project_id,kind,label,vault_ref,encrypted_blob)
                   VALUES (?,?,?,?,?,?)""",
                (cid, project_id, kind, label, f"byo://{cid}", "enc:" + hashlib.sha256(blob.encode()).hexdigest()),
            )
        return {"id": cid, "status": "OK"}

    def sync_match_repo(self, project_id: str, repo_url: str) -> Dict[str, Any]:
        with self._conn() as conn:
            self._audit(conn, "credentials.match_sync", project_id, {"repo": repo_url})
            conn.execute(
                """INSERT INTO signing_credentials (id,project_id,kind,label,vault_ref,encrypted_blob)
                   VALUES (?,?,?,?,?,?)""",
                (_uid("cred_"), project_id, "match", "fastlane-match", repo_url, "synced"),
            )
        return {"synced": True, "status": "OK"}

    def publish_ota(
        self, project_id: str, channel: str, message: str = "", rollout_pct: float = 100
    ) -> Dict[str, Any]:
        with self._conn() as conn:
            ch = conn.execute(
                "SELECT id FROM ota_channels WHERE project_id=? AND name=?",
                (project_id, channel),
            ).fetchone()
            if not ch:
                cid = _uid("ch_")
                conn.execute(
                    "INSERT INTO ota_channels (id,project_id,name) VALUES (?,?,?)",
                    (cid, project_id, channel),
                )
            else:
                cid = ch["id"]
            uid = _uid("ota_")
            bh = hashlib.sha256(f"{uid}:{message}".encode()).hexdigest()[:16]
            conn.execute(
                """INSERT INTO ota_updates (id,channel_id,project_id,bundle_hash,message,rollout_pct,insights_json)
                   VALUES (?,?,?,?,?,?,?)""",
                (uid, cid, project_id, bh, message, rollout_pct,
                 json.dumps({"installs": 0, "reach": 0})),
            )
            rid = _uid("rel_")
            conn.execute(
                """INSERT INTO releases (id,project_id,version,channel,rollout_pct,notes)
                   VALUES (?,?,?,?,?,?)""",
                (rid, project_id, bh, channel, rollout_pct, message),
            )
            self._audit(conn, "ota.publish", uid, {"channel": channel})
        return {"update_id": uid, "bundle_hash": bh, "status": "OK"}

    def rollback_ota(self, project_id: str, channel: str) -> Dict[str, Any]:
        with self._conn() as conn:
            rows = conn.execute(
                """SELECT u.id FROM ota_updates u JOIN ota_channels c ON c.id=u.channel_id
                   WHERE u.project_id=? AND c.name=? ORDER BY u.created_at DESC LIMIT 2""",
                (project_id, channel),
            ).fetchall()
            if len(rows) < 2:
                return {"error": "no previous update", "status": "ERROR"}
            current, previous = rows[0]["id"], rows[1]["id"]
            conn.execute("UPDATE ota_updates SET status='rolled_back' WHERE id=?", (current,))
            conn.execute("UPDATE ota_updates SET status='active' WHERE id=?", (previous,))
            self._audit(conn, "ota.rollback", previous, {"from": current})
        return {"active_update_id": previous, "status": "OK"}

    def map_channel_profile(self, project_id: str, channel: str, profile: str) -> Dict[str, Any]:
        with self._conn() as conn:
            conn.execute(
                "UPDATE ota_channels SET mapped_profile=? WHERE project_id=? AND name=?",
                (profile, project_id, channel),
            )
        return {"channel": channel, "profile": profile, "status": "OK"}

    def ota_insights(self, update_id: str, installs: int = 10, reach: int = 8) -> Dict[str, Any]:
        with self._conn() as conn:
            conn.execute(
                "UPDATE ota_updates SET insights_json=? WHERE id=?",
                (json.dumps({"installs": installs, "reach": reach}), update_id),
            )
        return {"update_id": update_id, "installs": installs, "reach": reach, "status": "OK"}

    def submit_store(
        self, project_id: str, build_id: str, store: str, track: str = "internal", changelog: str = ""
    ) -> Dict[str, Any]:
        sid = _uid("sub_")
        with self._conn() as conn:
            conn.execute(
                """INSERT INTO store_submissions
                   (id,project_id,build_id,store,track,status,changelog,updated_at)
                   VALUES (?,?,?,?,?,?,?,?)""",
                (sid, project_id, build_id, store, track, "waiting_for_review", changelog, _now()),
            )
            self._audit(conn, "store.submit", sid, {"store": store, "track": track})
        return {"id": sid, "submission_status": "waiting_for_review", "status": "OK"}

    def advance_store_status(self, submission_id: str, new_status: str) -> Dict[str, Any]:
        with self._conn() as conn:
            conn.execute(
                "UPDATE store_submissions SET status=?, updated_at=? WHERE id=?",
                (new_status, _now(), submission_id),
            )
        return {"id": submission_id, "submission_status": new_status, "status": "OK"}

    def promote_play_track(self, submission_id: str, to_track: str) -> Dict[str, Any]:
        with self._conn() as conn:
            conn.execute(
                "UPDATE store_submissions SET track=?, updated_at=? WHERE id=?",
                (to_track, _now(), submission_id),
            )
        return {"id": submission_id, "track": to_track, "status": "OK"}

    def cancel_submission(self, submission_id: str) -> Dict[str, Any]:
        return self.advance_store_status(submission_id, "cancelled")

    def upload_store_metadata(self, submission_id: str, metadata: Dict) -> Dict[str, Any]:
        with self._conn() as conn:
            conn.execute(
                "UPDATE store_submissions SET metadata_json=?, updated_at=? WHERE id=?",
                (json.dumps(metadata), _now(), submission_id),
            )
        return {"id": submission_id, "status": "OK"}

    def bump_version(self, project_id: str, version: str, build_number: int) -> Dict[str, Any]:
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO app_insights (id,project_id,kind,data_json) VALUES (?,?,?,?)",
                (_uid("ins_"), project_id, "version",
                 json.dumps({"version": version, "build_number": build_number})),
            )
        return {"version": version, "build_number": build_number, "status": "OK"}

    def store_status_timeline(self, submission_id: str) -> Dict[str, Any]:
        with self._conn() as conn:
            row = conn.execute("SELECT * FROM store_submissions WHERE id=?", (submission_id,)).fetchone()
        status = row["status"] if row else "unknown"
        order = ["pending", "waiting_for_review", "in_review", "ready_for_sale", "live", "cancelled"]
        idx = order.index(status) if status in order else 0
        return {"current": status, "timeline": order[: idx + 1], "status": "OK"}

    def deploy_web(
        self, project_id: str, env: str = "preview", git_ref: str = "main", framework: str = "nextjs"
    ) -> Dict[str, Any]:
        did = _uid("dep_")
        url = f"https://{did[:8]}-{env}.sovereign.app"
        with self._conn() as conn:
            conn.execute(
                """INSERT INTO web_deploys (id,project_id,env,url,status,git_ref,framework,bandwidth_mb)
                   VALUES (?,?,?,?,?,?,?,?)""",
                (did, project_id, env, url, "live", git_ref, framework, 1.5),
            )
            self._audit(conn, "web.deploy", did, {"env": env, "url": url})
        return {"id": did, "url": url, "status": "OK"}

    def promote_web(self, deploy_id: str) -> Dict[str, Any]:
        with self._conn() as conn:
            d = conn.execute("SELECT * FROM web_deploys WHERE id=?", (deploy_id,)).fetchone()
            if not d:
                return {"error": "not found", "status": "ERROR"}
            nid = _uid("dep_")
            prod_url = f"https://{d['project_id'][:8]}.sovereign.app"
            conn.execute(
                """INSERT INTO web_deploys (id,project_id,env,url,status,git_ref,framework)
                   VALUES (?,?,?,?,?,?,?)""",
                (nid, d["project_id"], "production", prod_url, "live", d["git_ref"], d["framework"]),
            )
        return {"id": nid, "url": prod_url, "status": "OK"}

    def rollback_web(self, project_id: str) -> Dict[str, Any]:
        with self._conn() as conn:
            rows = conn.execute(
                """SELECT id FROM web_deploys WHERE project_id=? AND env='production'
                   ORDER BY created_at DESC LIMIT 2""",
                (project_id,),
            ).fetchall()
            if len(rows) < 2:
                return {"error": "no prior deploy", "status": "ERROR"}
            conn.execute("UPDATE web_deploys SET status='rolled_back' WHERE id=?", (rows[0]["id"],))
            conn.execute("UPDATE web_deploys SET status='live' WHERE id=?", (rows[1]["id"],))
        return {"active_deploy_id": rows[1]["id"], "status": "OK"}

    def set_secret(self, project_id: str, env_name: str, key: str, value: str) -> Dict[str, Any]:
        with self._conn() as conn:
            conn.execute(
                """INSERT INTO app_secrets (id,project_id,env_name,key,value) VALUES (?,?,?,?,?)
                   ON CONFLICT(project_id,env_name,key) DO UPDATE SET value=excluded.value""",
                (_uid("sec_"), project_id, env_name, key, value),
            )
        return {"key": key, "env": env_name, "status": "OK"}

    def set_custom_domain(self, project_id: str, domain: str) -> Dict[str, Any]:
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO app_insights (id,project_id,kind,data_json) VALUES (?,?,?,?)",
                (_uid("ins_"), project_id, "domain", json.dumps({"domain": domain, "https": True})),
            )
        return {"domain": domain, "https": True, "status": "OK"}

    def save_pipeline(self, project_id: str, name: str, yaml_text: str, visual: Dict = None) -> Dict[str, Any]:
        pid = _uid("pipe_")
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO pipelines (id,project_id,name,yaml_text,visual_json) VALUES (?,?,?,?,?)",
                (pid, project_id, name, yaml_text, json.dumps(visual or {})),
            )
        return {"id": pid, "status": "OK"}

    def run_pipeline(
        self, pipeline_id: str, trigger: str = "manual", require_approval: bool = False, approved_by: str = None
    ) -> Dict[str, Any]:
        with self._conn() as conn:
            pipe = conn.execute("SELECT * FROM pipelines WHERE id=?", (pipeline_id,)).fetchone()
            if not pipe:
                return {"error": "pipeline not found", "status": "ERROR"}
            if require_approval and not approved_by:
                rid = _uid("prun_")
                conn.execute(
                    """INSERT INTO pipeline_runs
                       (id,pipeline_id,status,trigger,logs,approval_required)
                       VALUES (?,?,?,?,?,1)""",
                    (rid, pipeline_id, "awaiting_approval", trigger, "Waiting for approval"),
                )
                return {"run_id": rid, "run_status": "awaiting_approval", "status": "OK"}
            # simulate jobs from yaml presence
            logs = [
                "job:lint ok", "job:unit ok", "job:maestro stub ok",
                "job:build ok", "job:notify slack stub ok",
            ]
            if "submit" in (pipe["yaml_text"] or ""):
                logs.append("job:submit ok")
            rid = _uid("prun_")
            conn.execute(
                """INSERT INTO pipeline_runs
                   (id,pipeline_id,status,trigger,logs,artifacts_json,approval_required,approved_by,finished_at)
                   VALUES (?,?,?,?,?,?,?,?,?)""",
                (rid, pipeline_id, "succeeded", trigger, "\n".join(logs),
                 json.dumps([{"name": "build.log"}]), 1 if require_approval else 0,
                 approved_by, _now()),
            )
            self._audit(conn, "pipeline.run", rid, {"trigger": trigger})
            # slack notify stub
            self._audit(conn, "notify.slack", rid, {"message": f"Pipeline {pipeline_id} succeeded"})
        return {"run_id": rid, "run_status": "succeeded", "logs": logs, "status": "OK"}

    def approve_pipeline_run(self, run_id: str, approved_by: str) -> Dict[str, Any]:
        with self._conn() as conn:
            run = conn.execute("SELECT * FROM pipeline_runs WHERE id=?", (run_id,)).fetchone()
            if not run:
                return {"error": "not found", "status": "ERROR"}
            conn.execute(
                """UPDATE pipeline_runs SET status='succeeded', approved_by=?, finished_at=?, logs=?
                   WHERE id=?""",
                (approved_by, _now(), (run["logs"] or "") + "\napproved + continued", run_id),
            )
        return {"run_id": run_id, "run_status": "succeeded", "status": "OK"}

    def maestro_test(self, project_id: str, suite: str = "smoke") -> Dict[str, Any]:
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO app_insights (id,project_id,kind,data_json) VALUES (?,?,?,?)",
                (_uid("ins_"), project_id, "maestro", json.dumps({"suite": suite, "passed": True})),
            )
        return {"suite": suite, "passed": True, "status": "OK"}

    def slack_notify(self, message: str, project_id: str = "") -> Dict[str, Any]:
        with self._conn() as conn:
            self._audit(conn, "notify.slack", project_id, {"message": message})
        return {"notified": True, "status": "OK"}

    def github_pr_comment(self, pr: int, body: str, project_id: str = "") -> Dict[str, Any]:
        with self._conn() as conn:
            self._audit(conn, "notify.github_pr", project_id, {"pr": pr, "body": body})
        return {"pr": pr, "status": "OK"}

    def install_qr(self, build_id: str) -> Dict[str, Any]:
        url = f"sovereign://install/{build_id}"
        with self._conn() as conn:
            b = conn.execute("SELECT project_id FROM builds WHERE id=?", (build_id,)).fetchone()
            pid = b["project_id"] if b else ""
            conn.execute(
                "INSERT INTO distribution_links (id,project_id,build_id,kind,url) VALUES (?,?,?,?,?)",
                (_uid("dist_"), pid, build_id, "qr", url),
            )
        return {"url": url, "qr_payload": url, "status": "OK"}

    def orbit_install(self, build_id: str) -> Dict[str, Any]:
        return self.install_qr(build_id)

    def link_revenuecat(self, project_id: str, public_sdk_key: str, products: List[str] = None) -> Dict[str, Any]:
        rid = _uid("rc_")
        with self._conn() as conn:
            conn.execute(
                """INSERT INTO revenuecat_links (id,project_id,public_sdk_key,products_json,promo_checklist_json)
                   VALUES (?,?,?,?,?)""",
                (rid, project_id, public_sdk_key, json.dumps(products or ["pro_access"]),
                 json.dumps(["offerings", "paywall", "promo_codes"])),
            )
        return {"id": rid, "status": "OK"}

    def verify_rc_purchase(self, link_id: str) -> Dict[str, Any]:
        with self._conn() as conn:
            conn.execute(
                "UPDATE revenuecat_links SET verified_purchase=1 WHERE id=?", (link_id,)
            )
        return {"verified": True, "status": "OK"}

    def cli(self, command: str, **kwargs) -> Dict[str, Any]:
        """CLI-equivalent: build | submit | update | deploy."""
        parts = command.strip().split()
        if not parts:
            return {"error": "empty command", "status": "ERROR"}
        cmd = parts[0]
        project_id = kwargs.get("project_id") or (parts[1] if len(parts) > 1 else None)
        if not project_id:
            projects = self.list_projects()["projects"]
            project_id = projects[0]["id"] if projects else None
        if cmd == "build":
            return self.trigger_build(project_id, platform=kwargs.get("platform", "android"))
        if cmd == "submit":
            b = self.trigger_build(project_id)
            return self.submit_store(project_id, b["id"], kwargs.get("store", "play"))
        if cmd == "update":
            return self.publish_ota(project_id, kwargs.get("channel", "production"), kwargs.get("message", "cli update"))
        if cmd == "deploy":
            return self.deploy_web(project_id, env=kwargs.get("env", "preview"))
        return {"error": f"unknown command {cmd}", "status": "ERROR"}

    def rest_list_builds(self, project_id: str) -> Dict[str, Any]:
        with self._conn() as conn:
            rows = [_row(r) for r in conn.execute(
                "SELECT * FROM builds WHERE project_id=? ORDER BY started_at DESC", (project_id,)
            ).fetchall()]
        return {"builds": rows, "status": "OK"}

    def create_app_webhook(self, url: str, events: List[str] = None, project_id: str = None) -> Dict[str, Any]:
        wid = _uid("awh_")
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO app_webhooks (id,project_id,url,events_json) VALUES (?,?,?,?)",
                (wid, project_id, url, json.dumps(events or ["build.finished"])),
            )
        return {"id": wid, "status": "OK"}

    def status_badge(self, project_id: str) -> Dict[str, Any]:
        with self._conn() as conn:
            b = conn.execute(
                "SELECT status FROM builds WHERE project_id=? ORDER BY started_at DESC LIMIT 1",
                (project_id,),
            ).fetchone()
            label = (b["status"] if b else "unknown").upper()
            svg = f'<svg xmlns="http://www.w3.org/2000/svg"><text>{label}</text></svg>'
            bid = _uid("badge_")
            conn.execute(
                "INSERT INTO status_badges (id,project_id,label,svg_text) VALUES (?,?,?,?)",
                (bid, project_id, label, svg),
            )
        return {"label": label, "svg": svg, "status": "OK"}

    def audit_entries(self, limit: int = 50) -> Dict[str, Any]:
        with self._conn() as conn:
            rows = [_row(r) for r in conn.execute(
                "SELECT * FROM audit_log ORDER BY created_at DESC LIMIT ?", (limit,)
            ).fetchall()]
        return {"entries": rows, "status": "OK"}

    def set_billing(self, build_credits: int = None, approve_seats: int = None, pro_active: bool = None) -> Dict[str, Any]:
        with self._conn() as conn:
            if build_credits is not None:
                conn.execute("UPDATE app_billing SET build_credits=? WHERE id=1", (build_credits,))
            if approve_seats is not None:
                conn.execute("UPDATE app_billing SET approve_seats=? WHERE id=1", (approve_seats,))
            if pro_active is not None:
                conn.execute("UPDATE app_billing SET pro_active=? WHERE id=1", (1 if pro_active else 0,))
            row = conn.execute("SELECT * FROM app_billing WHERE id=1").fetchone()
        return {"billing": _row(row), "status": "OK"}

    def record_insight(self, project_id: str, kind: str, data: Dict) -> Dict[str, Any]:
        iid = _uid("ins_")
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO app_insights (id,project_id,kind,data_json) VALUES (?,?,?,?)",
                (iid, project_id, kind, json.dumps(data)),
            )
        return {"id": iid, "status": "OK"}

    def public_download_page(self, build_id: str) -> Dict[str, Any]:
        with self._conn() as conn:
            b = conn.execute("SELECT * FROM builds WHERE id=?", (build_id,)).fetchone()
            if not b:
                return {"error": "not found", "status": "ERROR"}
            url = f"https://download.sovereign.local/{build_id}"
            conn.execute(
                "INSERT INTO distribution_links (id,project_id,build_id,kind,url) VALUES (?,?,?,?,?)",
                (_uid("dist_"), b["project_id"], build_id, "public", url),
            )
        return {"url": url, "status": "OK"}

    def beta_cohort(self, project_id: str, emails: List[str], kind: str = "testflight") -> Dict[str, Any]:
        did = _uid("dist_")
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO distribution_links (id,project_id,kind,url,cohort_json) VALUES (?,?,?,?,?)",
                (did, project_id, kind, f"https://beta.sovereign.local/{did}", json.dumps(emails)),
            )
        return {"id": did, "cohort_size": len(emails), "status": "OK"}

    def import_pipeline_yaml(self, project_id: str, name: str, yaml_text: str, source: str = "eas") -> Dict[str, Any]:
        out = self.save_pipeline(project_id, name, yaml_text, visual={"imported_from": source})
        out["source"] = source
        return out

    def ssh_debug_stub(self, build_id: str) -> Dict[str, Any]:
        with self._conn() as conn:
            self._audit(conn, "build.ssh_debug", build_id, {"session": "simulated"})
        return {"build_id": build_id, "ssh": "simulated-session", "status": "OK"}

    def provision_managed_db(self, project_id: str, engine: str = "postgres") -> Dict[str, Any]:
        conn_str = f"{engine}://sovereign:secret@db.sovereign.local:5432/{project_id[:8]}"
        self.set_secret(project_id, "production", f"{engine.upper()}_URL", conn_str)
        return self.record_insight(project_id, "managed_db", {"engine": engine, "url": conn_str})

    def provision_redis(self, project_id: str) -> Dict[str, Any]:
        url = f"redis://cache.sovereign.local:6379/{project_id[:6]}"
        self.set_secret(project_id, "production", "REDIS_URL", url)
        return self.record_insight(project_id, "redis", {"url": url})
