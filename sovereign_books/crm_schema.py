"""CRM SQLite DDL (CREATE IF NOT EXISTS)."""

CRM_SCHEMA = """
CREATE TABLE IF NOT EXISTS companies (
    id TEXT PRIMARY KEY, name TEXT NOT NULL, domain TEXT, icp TEXT, arr REAL DEFAULT 0,
    owner_id TEXT, industry TEXT, address TEXT, linkedin TEXT, employees INTEGER DEFAULT 0,
    main_contact_id TEXT, custom_json TEXT DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT (datetime('now')), updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS people (
    id TEXT PRIMARY KEY, first_name TEXT, last_name TEXT, email TEXT, role TEXT,
    company_id TEXT, phone TEXT, linkedin TEXT, custom_json TEXT DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT (datetime('now')), updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS opportunities (
    id TEXT PRIMARY KEY, name TEXT NOT NULL, company_id TEXT, stage TEXT DEFAULT 'NEW',
    amount REAL DEFAULT 0, probability REAL DEFAULT 0.1, close_date TEXT, owner_id TEXT,
    stage_entered_at TEXT DEFAULT (datetime('now')), custom_json TEXT DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT (datetime('now')), updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY, title TEXT NOT NULL, status TEXT DEFAULT 'TODO', due_date TEXT,
    company_id TEXT, person_id TEXT, opportunity_id TEXT, assignee_id TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')), updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS notes (
    id TEXT PRIMARY KEY, body TEXT NOT NULL, company_id TEXT, person_id TEXT,
    opportunity_id TEXT, author_id TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS favorites (
    id TEXT PRIMARY KEY, user_id TEXT NOT NULL, object_type TEXT NOT NULL,
    object_id TEXT NOT NULL, label TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(user_id, object_type, object_id)
);
CREATE TABLE IF NOT EXISTS activities (
    id TEXT PRIMARY KEY, object_type TEXT NOT NULL, object_id TEXT NOT NULL,
    activity_type TEXT NOT NULL, summary TEXT, payload_json TEXT DEFAULT '{}',
    actor_id TEXT, created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS attachments (
    id TEXT PRIMARY KEY, object_type TEXT NOT NULL, object_id TEXT NOT NULL,
    filename TEXT NOT NULL, path TEXT NOT NULL, mime_type TEXT, size_bytes INTEGER DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS custom_objects (
    id TEXT PRIMARY KEY, name TEXT NOT NULL UNIQUE, label TEXT, description TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS custom_fields (
    id TEXT PRIMARY KEY, object_name TEXT NOT NULL, field_name TEXT NOT NULL,
    field_type TEXT NOT NULL DEFAULT 'text', unique_constraint INTEGER DEFAULT 0,
    relation_target TEXT, relation_kind TEXT, formula TEXT,
    UNIQUE(object_name, field_name)
);
CREATE TABLE IF NOT EXISTS object_records (
    id TEXT PRIMARY KEY, object_name TEXT NOT NULL, data_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL DEFAULT (datetime('now')), updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS saved_views (
    id TEXT PRIMARY KEY, name TEXT NOT NULL, object_name TEXT NOT NULL,
    view_type TEXT NOT NULL DEFAULT 'table', icon TEXT, visibility TEXT DEFAULT 'workspace',
    columns_json TEXT DEFAULT '[]', filters_json TEXT DEFAULT '[]',
    sort_json TEXT DEFAULT '[]', group_by TEXT, restricted_roles_json TEXT DEFAULT '[]',
    owner_id TEXT, created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS pipeline_stages (
    id TEXT PRIMARY KEY, name TEXT NOT NULL UNIQUE, position INTEGER NOT NULL,
    probability REAL DEFAULT 0.1, color TEXT
);
CREATE TABLE IF NOT EXISTS workflows (
    id TEXT PRIMARY KEY, name TEXT NOT NULL, status TEXT DEFAULT 'draft',
    trigger_json TEXT NOT NULL DEFAULT '{}', actions_json TEXT NOT NULL DEFAULT '[]',
    branches_json TEXT DEFAULT '[]', version INTEGER DEFAULT 1, credits_used INTEGER DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now')), updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS workflow_runs (
    id TEXT PRIMARY KEY, workflow_id TEXT NOT NULL, status TEXT NOT NULL,
    trigger_payload TEXT DEFAULT '{}', result_json TEXT DEFAULT '{}',
    started_at TEXT NOT NULL DEFAULT (datetime('now')), finished_at TEXT
);
CREATE TABLE IF NOT EXISTS mailbox_accounts (
    id TEXT PRIMARY KEY, user_id TEXT NOT NULL, email TEXT NOT NULL,
    provider TEXT DEFAULT 'mock', import_filter TEXT, active INTEGER DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS emails (
    id TEXT PRIMARY KEY, mailbox_id TEXT, subject TEXT, body TEXT, from_addr TEXT,
    to_addr TEXT, object_type TEXT, object_id TEXT, direction TEXT DEFAULT 'inbound',
    received_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS calendar_events (
    id TEXT PRIMARY KEY, title TEXT NOT NULL, starts_at TEXT NOT NULL, ends_at TEXT,
    company_id TEXT, person_id TEXT, source TEXT DEFAULT 'mock',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS crm_dashboards (
    id TEXT PRIMARY KEY, name TEXT NOT NULL, tabs_json TEXT DEFAULT '[]',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS crm_widgets (
    id TEXT PRIMARY KEY, dashboard_id TEXT NOT NULL, widget_type TEXT NOT NULL,
    title TEXT, settings_json TEXT DEFAULT '{}', position INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS roles (
    id TEXT PRIMARY KEY, name TEXT NOT NULL UNIQUE, permissions_json TEXT NOT NULL DEFAULT '[]'
);
CREATE TABLE IF NOT EXISTS members (
    id TEXT PRIMARY KEY, email TEXT NOT NULL UNIQUE, role_id TEXT, display_name TEXT,
    status TEXT DEFAULT 'active', invited_at TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS workspace_settings (
    key TEXT PRIMARY KEY, value_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS import_jobs (
    id TEXT PRIMARY KEY, object_name TEXT NOT NULL, status TEXT NOT NULL,
    mapping_json TEXT DEFAULT '{}', errors_json TEXT DEFAULT '[]',
    rows_ok INTEGER DEFAULT 0, rows_fail INTEGER DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS api_keys (
    id TEXT PRIMARY KEY, name TEXT NOT NULL, key_hash TEXT NOT NULL UNIQUE,
    scopes_json TEXT DEFAULT '[]', created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS webhooks (
    id TEXT PRIMARY KEY, url TEXT NOT NULL, events_json TEXT DEFAULT '[]',
    active INTEGER DEFAULT 1, created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS apps_extensions (
    id TEXT PRIMARY KEY, name TEXT NOT NULL, version TEXT DEFAULT '1.0.0',
    manifest_json TEXT DEFAULT '{}', status TEXT DEFAULT 'installed',
    kv_store_json TEXT DEFAULT '{}', created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS page_layouts (
    id TEXT PRIMARY KEY, object_name TEXT NOT NULL, tabs_json TEXT DEFAULT '[]',
    widgets_json TEXT DEFAULT '[]'
);
CREATE TABLE IF NOT EXISTS crm_credits (
    id INTEGER PRIMARY KEY CHECK (id = 1), workflow_credits INTEGER DEFAULT 1000,
    ai_credits INTEGER DEFAULT 500, seat_plan TEXT DEFAULT 'free', seat_count INTEGER DEFAULT 1
);
"""
