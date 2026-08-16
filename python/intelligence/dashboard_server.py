"""
dashboard_server.py -- Sovereign Intelligence Dashboard API

Real FastAPI server exposing the master index, character agents,
sovereign models, and organism status as queryable REST endpoints.

Run:
    python python/intelligence/dashboard_server.py

Endpoints:
    GET  /                          Health + stats overview
    GET  /api/index                 Full master index (86 entries)
    GET  /api/index/search?q=...    Search the master index
    GET  /api/index/stats           Entry counts by kind
    GET  /api/agents                All character AI agents
    GET  /api/agents/{name}         Single agent details
    POST /api/agents/{name}/dispatch  Dispatch a task to an agent
    GET  /api/models                All 16 sovereign models
    GET  /api/models/{model_id}     Single model details
    POST /api/models/{model_id}/invoke  Record an invocation
    GET  /api/organism              Organism architecture + organ status
    GET  /api/protocols             All 32+ protocols from CSV
    GET  /api/protocols/{proto_id}  Single protocol details

(c) 2026 Alfredo Medina Hernandez. All Rights Reserved.
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add parent to path so we can import sibling modules
sys.path.insert(0, str(Path(__file__).resolve().parent))

from master_index import MasterIndex, EntryKind
from character_ai import CharacterRegistry, TaskPriority
from sovereign_models import SovereignModelRegistry, SOVEREIGN_REGISTRY

# ── Constants ──────────────────────────────────────────────────────────────────

PHI = 1.618033988749895
HEARTBEAT_MS = 873
WORKSPACE = Path(os.environ.get(
    "AIEOS_ROOT",
    os.path.expanduser("~/OneDrive/Documents/AIEOSpro")
))

# ── Initialize Core Systems ───────────────────────────────────────────────────

master_idx = MasterIndex(auto_scan=True)
char_registry = CharacterRegistry()
char_registry.load_agents_dir()

# Build model registry from sovereign_models.py
model_registry: dict[str, Any] = {}
for model in SOVEREIGN_REGISTRY:
    model_registry[model.model_id] = model

# ── FastAPI App ────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Sovereign Intelligence Dashboard",
    description="Real-time API for the Medina Sovereign OS - "
                "Master Index, Character AI, Sovereign Models, Organism Status",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Request/Response Models ────────────────────────────────────────────────────

class DispatchRequest(BaseModel):
    prompt: str
    priority: str = "NORMAL"
    context_files: list[str] = []


class InvokeRequest(BaseModel):
    success: bool = True
    latency_ms: float = 150.0


# ── Health / Root ──────────────────────────────────────────────────────────────

@app.get("/")
def root():
    idx_stats = master_idx.stats()
    agent_count = len(char_registry.agents)
    model_count = len(model_registry)
    return {
        "system": "Sovereign Intelligence Dashboard",
        "designation": "RSHIP-2026-DASHBOARD-001",
        "status": "online",
        "heartbeat_ms": HEARTBEAT_MS,
        "phi": PHI,
        "workspace": str(WORKSPACE),
        "master_index_entries": idx_stats.get("TOTAL", 0),
        "character_agents": agent_count,
        "sovereign_models": model_count,
        "index_breakdown": idx_stats,
        "uptime_seconds": round(time.time() - _start_time, 2),
    }

_start_time = time.time()

# ── Master Index Endpoints ─────────────────────────────────────────────────────

@app.get("/api/index")
def get_index(
    kind: Optional[str] = Query(None, description="Filter by kind: PROTOCOL, ENGINE_JULIA, CANISTER, etc."),
    language: Optional[str] = Query(None, description="Filter by language: python, julia, motoko"),
    ring: Optional[str] = Query(None, description="Filter by ring affinity"),
):
    results = master_idx.query(kind=kind, language=language, ring=ring)
    return {
        "total": len(results),
        "entries": [e.to_dict() for e in results],
    }


@app.get("/api/index/search")
def search_index(q: str = Query(..., description="Search term")):
    results = master_idx.search(q)
    return {
        "query": q,
        "total": len(results),
        "entries": [e.to_dict() for e in results],
    }


@app.get("/api/index/stats")
def index_stats():
    return master_idx.stats()


# ── Character AI Endpoints ─────────────────────────────────────────────────────

@app.get("/api/agents")
def list_agents():
    return {
        "total": len(char_registry.agents),
        "agents": [a.to_dict() for a in char_registry.list_agents()],
    }


@app.get("/api/agents/{name}")
def get_agent(name: str):
    agent = char_registry.get(name)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{name}' not found")
    return agent.to_dict()


@app.post("/api/agents/{name}/dispatch")
def dispatch_to_agent(name: str, req: DispatchRequest):
    agent = char_registry.get(name)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{name}' not found")

    try:
        priority = TaskPriority[req.priority.upper()]
    except KeyError:
        priority = TaskPriority.NORMAL

    task = agent.dispatch(req.prompt, priority, req.context_files)
    return {
        "task_id": task.task_id,
        "agent": name,
        "status": task.status,
        "result": task.result,
        "priority": priority.name,
    }


# ── Sovereign Models Endpoints ─────────────────────────────────────────────────

@app.get("/api/models")
def list_models():
    models_out = []
    for m in SOVEREIGN_REGISTRY:
        models_out.append({
            "model_id": m.model_id,
            "nomen_latinum": m.nomen_latinum,
            "nomen_breve": m.nomen_breve,
            "dominium": m.dominium.name,
            "status": m.status.name,
            "confidentia": m.confidentia,
            "latentia_ms": m.latentia_ms,
            "reputatio": round(m.reputatio, 4),
            "phi_score": round(m.phi_score, 4),
            "invocationes": m.invocationes,
            "successus": m.successus,
        })
    return {"total": len(models_out), "models": models_out}


@app.get("/api/models/{model_id}")
def get_model(model_id: str):
    m = model_registry.get(model_id)
    if not m:
        raise HTTPException(status_code=404, detail=f"Model '{model_id}' not found")
    return {
        "model_id": m.model_id,
        "nomen_latinum": m.nomen_latinum,
        "nomen_breve": m.nomen_breve,
        "dominium": m.dominium.name,
        "descriptio": m.descriptio,
        "capacitas": m.capacitas,
        "status": m.status.name,
        "confidentia": m.confidentia,
        "latentia_ms": m.latentia_ms,
        "reputatio": round(m.reputatio, 4),
        "phi_score": round(m.phi_score, 4),
        "invocationes": m.invocationes,
        "successus": m.successus,
        "success_rate": round(m.success_rate, 4),
    }


@app.post("/api/models/{model_id}/invoke")
def invoke_model(model_id: str, req: InvokeRequest):
    m = model_registry.get(model_id)
    if not m:
        raise HTTPException(status_code=404, detail=f"Model '{model_id}' not found")
    m.invoke(success=req.success, latency_ms=req.latency_ms)
    return {
        "model_id": m.model_id,
        "invocationes": m.invocationes,
        "reputatio": round(m.reputatio, 4),
        "phi_score": round(m.phi_score, 4),
    }


# ── Organism Architecture Endpoint ─────────────────────────────────────────────

@app.get("/api/organism")
def organism_status():
    organs = {}
    org_dir = WORKSPACE / "organism"
    if org_dir.exists():
        for sub in sorted(org_dir.iterdir()):
            if sub.is_dir():
                file_count = sum(1 for f in sub.rglob("*") if f.is_file())
                subdirs = [s.name for s in sub.iterdir() if s.is_dir()]
                organs[sub.name] = {
                    "path": str(sub),
                    "file_count": file_count,
                    "subdirectories": subdirs,
                }

    return {
        "designation": "RSHIP-2026-ORGANISM-5ORGAN-001",
        "architecture": "Door 4 - 5-Organ v1.0.0",
        "runtime": "Cross-Substrate (Cloudflare + ICP + Julia)",
        "protocol": "MCP Tool System",
        "organs": organs,
        "organ_count": len(organs),
    }


# ── Protocols Endpoint ─────────────────────────────────────────────────────────

@app.get("/api/protocols")
def list_protocols():
    protos = master_idx.query(kind="PROTOCOL")
    return {
        "total": len(protos),
        "protocols": [e.to_dict() for e in protos],
    }


@app.get("/api/protocols/{proto_id}")
def get_protocol(proto_id: str):
    entry = master_idx.get(proto_id)
    if not entry or entry.kind != EntryKind.PROTOCOL:
        raise HTTPException(status_code=404, detail=f"Protocol '{proto_id}' not found")
    return entry.to_dict()


# ── Run Server ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("  Sovereign Intelligence Dashboard")
    print(f"  Master Index: {master_idx.stats().get('TOTAL', 0)} entries")
    print(f"  Character Agents: {len(char_registry.agents)}")
    print(f"  Sovereign Models: {len(model_registry)}")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8888)
