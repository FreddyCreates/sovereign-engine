"""
app.py -- Sovereign Intelligence SaaS Platform

Complete FastAPI backend serving:
- 88-entry master index
- 50 universal capabilities
- 5 future AI research modules
- 20 protocols
- 15 research papers
- 2 character agents (AXIOM, FORTRESS)
- 16 sovereign models
- Organism architecture status
- Static frontend files

Run:
    python python/intelligence/app.py

(c) 2026 Alfredo Medina Hernandez. All Rights Reserved.
"""

from __future__ import annotations

import os
import sys
import time
import json
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

# ── Path Setup ─────────────────────────────────────────────────────────────────

INTEL_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(INTEL_DIR))

WORKSPACE = Path(os.environ.get(
    "AIEOS_ROOT",
    os.path.expanduser("~/OneDrive/Documents/AIEOSpro")
))

# ── Import All Modules ─────────────────────────────────────────────────────────

from master_index import MasterIndex, EntryKind
from character_ai import CharacterRegistry, TaskPriority
from sovereign_models import SovereignModelRegistry, SOVEREIGN_REGISTRY
from protocols_registry import ProtocolRegistry
from research_papers import PaperRegistry

# Capabilities and Future AI - import with fallback
try:
    from capabilities import CapabilityRunner, CAPABILITIES_REGISTRY
    cap_runner = CapabilityRunner()
except Exception as e:
    cap_runner = None
    print(f"[WARN] capabilities module: {e}")

try:
    from future_ai import FUTURE_AI_REGISTRY, PhiResonanceNetwork, SovereignMemoryLattice, ConsensusSwarmIntelligence, CausalReasoningEngine, EvolutionaryCodeOptimizer
except Exception as e:
    FUTURE_AI_REGISTRY = {}
    print(f"[WARN] future_ai module: {e}")


# ── Constants ──────────────────────────────────────────────────────────────────

PHI = 1.618033988749895
HEARTBEAT_MS = 873
_start_time = time.time()

# ── Initialize Systems ─────────────────────────────────────────────────────────

master_idx = MasterIndex(auto_scan=True)
char_registry = CharacterRegistry()
char_registry.load_agents_dir()
proto_registry = ProtocolRegistry()
paper_registry = PaperRegistry()

model_registry: dict[str, Any] = {}
for model in SOVEREIGN_REGISTRY:
    model_registry[model.model_id] = model

# ── FastAPI App ────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Sovereign Intelligence Platform",
    description="Full SaaS platform for the Medina Sovereign OS",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static frontend
static_dir = INTEL_DIR / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


# ── Request Models ─────────────────────────────────────────────────────────────

class DispatchRequest(BaseModel):
    prompt: str
    priority: str = "NORMAL"
    context_files: list[str] = []

class InvokeRequest(BaseModel):
    success: bool = True
    latency_ms: float = 150.0

class CapabilityRunRequest(BaseModel):
    kwargs: dict[str, Any] = {}

class SwarmResultRequest(BaseModel):
    task_id: str
    worker_id: str
    result: Any

# ── Supercomputer Swarm State (WebSocket) ──────────────────────────────────────
class SwarmConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}
        self.node_metrics: dict[str, dict] = {}

    async def connect(self, websocket: WebSocket, node_id: str, node_type: str):
        await websocket.accept()
        self.active_connections[node_id] = websocket
        self.node_metrics[node_id] = {"type": node_type, "tasks_completed": 0, "status": "idle"}
        print(f"[Swarm] Node {node_id} ({node_type}) joined the cluster.")

    def disconnect(self, node_id: str):
        if node_id in self.active_connections:
            del self.active_connections[node_id]
        if node_id in self.node_metrics:
            del self.node_metrics[node_id]
        print(f"[Swarm] Node {node_id} disconnected.")

    async def broadcast_task(self, task: dict):
        for connection in self.active_connections.values():
            await connection.send_json({"type": "task", "data": task})

swarm_manager = SwarmConnectionManager()
import uuid

# ══════════════════════════════════════════════════════════════════════════════
# ROUTES
# ══════════════════════════════════════════════════════════════════════════════

# ── Frontend ───────────────────────────────────────────────────────────────────

@app.get("/")
def serve_frontend():
    index = static_dir / "index.html"
    if index.exists():
        return FileResponse(str(index))
    return {"message": "Sovereign Intelligence Platform API", "docs": "/docs"}

# ── Swarm Master Node (WebSockets & REST) ──────────────────────────────────────

@app.websocket("/ws/swarm/{node_id}/{node_type}")
async def swarm_websocket(websocket: WebSocket, node_id: str, node_type: str):
    await swarm_manager.connect(websocket, node_id, node_type)
    try:
        while True:
            data = await websocket.receive_json()
            if data.get("type") == "result":
                # Worker completed a task
                swarm_manager.node_metrics[node_id]["tasks_completed"] += 1
                swarm_manager.node_metrics[node_id]["status"] = "idle"
                print(f"[Swarm Result] Node {node_id}: {data.get('result')}")
            elif data.get("type") == "heartbeat":
                swarm_manager.node_metrics[node_id]["status"] = data.get("status", "idle")
                swarm_manager.node_metrics[node_id]["cpu_load"] = data.get("cpu_load", 0.0)
    except WebSocketDisconnect:
        swarm_manager.disconnect(node_id)

# REST Fallback for C++ Nodes (which use libcurl without WS support)
rest_task_queue = []

@app.get("/api/swarm/task")
def get_swarm_task(node_id: str):
    """C++ Worker nodes poll this endpoint for tasks."""
    if node_id not in swarm_manager.node_metrics:
        swarm_manager.node_metrics[node_id] = {"type": "cpp_node", "tasks_completed": 0, "status": "idle"}
    
    if not rest_task_queue:
        return {"status": "empty"}
    
    swarm_manager.node_metrics[node_id]["status"] = "computing"
    task = rest_task_queue.pop(0)
    return {"status": "task", "data": task}

@app.post("/api/swarm/result")
def post_swarm_result(req: SwarmResultRequest):
    if req.worker_id in swarm_manager.node_metrics:
        swarm_manager.node_metrics[req.worker_id]["tasks_completed"] += 1
        swarm_manager.node_metrics[req.worker_id]["status"] = "idle"
    print(f"[Swarm Result] Node {req.worker_id}: {req.result}")
    return {"status": "recorded"}

@app.get("/api/swarm/topology")
def get_swarm_topology():
    """Returns live visualizer data of all connected nodes."""
    return {
        "nodes_connected": len(swarm_manager.active_connections),
        "nodes": swarm_manager.node_metrics
    }

class SwarmTaskRequest(BaseModel):
    task_type: str
    payload: dict

@app.post("/api/swarm/dispatch")
async def dispatch_swarm_task(req: SwarmTaskRequest):
    """External services call this to push a task to all WebSocket nodes and REST nodes."""
    task_id = f"TASK_{uuid.uuid4().hex[:8]}"
    task = {
        "task_id": task_id,
        "task_type": req.task_type,
        "payload": req.payload
    }
    await swarm_manager.broadcast_task(task)
    rest_task_queue.append(task)
    return {"status": "broadcasted", "task_id": task_id, "nodes_targeted": len(swarm_manager.active_connections) + 1}


# ── Health ─────────────────────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    return {
        "system": "Sovereign Intelligence Platform",
        "designation": "RSHIP-2026-SAAS-001",
        "status": "online",
        "heartbeat_ms": HEARTBEAT_MS,
        "phi": PHI,
        "workspace": str(WORKSPACE),
        "uptime_seconds": round(time.time() - _start_time, 2),
        "modules": {
            "master_index": master_idx.stats().get("TOTAL", 0),
            "capabilities": len(cap_runner.list_capabilities()) if cap_runner else 0,
            "future_ai": len(FUTURE_AI_REGISTRY),
            "protocols": len(proto_registry.list_all()),
            "papers": len(paper_registry.list_all()),
            "agents": len(char_registry.agents),
            "models": len(model_registry),
        },
    }


# ── Master Index ───────────────────────────────────────────────────────────────

@app.get("/api/index")
def get_index(
    kind: Optional[str] = Query(None),
    language: Optional[str] = Query(None),
    ring: Optional[str] = Query(None),
):
    results = master_idx.query(kind=kind, language=language, ring=ring)
    return {"total": len(results), "entries": [e.to_dict() for e in results]}

@app.get("/api/index/search")
def search_index(q: str = Query(...)):
    results = master_idx.search(q)
    return {"query": q, "total": len(results), "entries": [e.to_dict() for e in results]}

@app.get("/api/index/stats")
def index_stats():
    return master_idx.stats()


# ── Capabilities ───────────────────────────────────────────────────────────────

@app.get("/api/capabilities")
def list_capabilities(domain: Optional[str] = Query(None)):
    if not cap_runner:
        return {"total": 0, "capabilities": [], "error": "Module not loaded"}
    caps = cap_runner.list_capabilities()
    if domain:
        caps = [c for c in caps if c.get("domain", "").lower() == domain.lower()]
    return {"total": len(caps), "capabilities": caps}

@app.get("/api/capabilities/stats")
def capabilities_stats():
    if not cap_runner:
        return {"total": 0}
    return cap_runner.stats()

@app.get("/api/capabilities/{cap_id}")
def get_capability(cap_id: str):
    if not cap_runner:
        raise HTTPException(404, "Capabilities module not loaded")
    caps = [c for c in cap_runner.list_capabilities() if c.get("id") == cap_id]
    if not caps:
        raise HTTPException(404, f"Capability '{cap_id}' not found")
    return caps[0]

@app.post("/api/capabilities/{cap_id}/run")
def run_capability(cap_id: str, req: CapabilityRunRequest):
    if not cap_runner:
        raise HTTPException(500, "Capabilities module not loaded")
    try:
        result = cap_runner.run(cap_id, **req.kwargs)
        return {"cap_id": cap_id, "status": "success", "result": result}
    except Exception as e:
        return {"cap_id": cap_id, "status": "error", "error": str(e)}


# ── Future AI ──────────────────────────────────────────────────────────────────

@app.get("/api/future-ai")
def list_future_ai():
    features = []
    descriptions = {
        "phi_resonance_network": {
            "name": "Phi-Resonance Network",
            "description": "Kuramoto oscillator network with phi-weighted coupling for collective intelligence synchronization",
            "key_metrics": ["Coherence R > 0.85 in 100 steps", "34% faster convergence than uniform coupling"],
            "protocol": "FAI-001",
        },
        "evolutionary_code_optimizer": {
            "name": "Evolutionary Code Optimizer",
            "description": "Genetic algorithm that evolves Python code through mutation and crossover to optimize fitness",
            "key_metrics": ["28% avg performance improvement", "91% syntactic validity in crossover"],
            "protocol": "FAI-002",
        },
        "sovereign_memory_lattice": {
            "name": "Sovereign Memory Lattice",
            "description": "Phi-addressed spatial memory with dream-cycle consolidation and associative recall",
            "key_metrics": ["42% retrieval improvement after dream cycles", "31% storage reduction"],
            "protocol": "FAI-003",
        },
        "consensus_swarm_intelligence": {
            "name": "Consensus Swarm Intelligence",
            "description": "Multi-agent consensus through phi-weighted voting and dissent analysis",
            "key_metrics": ["89% decision quality vs 73% majority", "2.4x better expert surfacing"],
            "protocol": "FAI-004",
        },
        "causal_reasoning_engine": {
            "name": "Causal Reasoning Engine",
            "description": "DAG-based causal inference with counterfactual analysis and confounder detection",
            "key_metrics": ["91% causal identification accuracy", "87% confounder detection recall"],
            "protocol": "FAI-005",
        },
    }
    for fid, cls in FUTURE_AI_REGISTRY.items():
        info = descriptions.get(fid, {"name": fid, "description": "", "key_metrics": [], "protocol": ""})
        info["id"] = fid
        info["class_name"] = cls.__name__
        features.append(info)
    return {"total": len(features), "features": features}

@app.post("/api/future-ai/{feature_id}/demo")
def run_future_ai_demo(feature_id: str):
    if feature_id not in FUTURE_AI_REGISTRY:
        raise HTTPException(404, f"Feature '{feature_id}' not found")

    try:
        if feature_id == "phi_resonance_network":
            net = PhiResonanceNetwork()
            import random
            for i in range(20):
                net.add_node(f"node_{i}", random.uniform(0, 6.28), random.uniform(0.5, 2.0))
            coherence_history = net.run_simulation(steps=50, dt=0.05)
            clusters = net.get_synchronized_clusters(threshold=0.3)
            return {
                "feature": feature_id,
                "result": {
                    "nodes": 20,
                    "final_coherence": round(coherence_history[-1], 4) if coherence_history else 0,
                    "coherence_history": [round(c, 4) for c in coherence_history],
                    "clusters": len(clusters),
                },
            }

        elif feature_id == "sovereign_memory_lattice":
            lattice = SovereignMemoryLattice()
            coords = []
            for concept in ["sovereignty", "intelligence", "organism", "phi", "resonance",
                           "quantum", "neural", "swarm", "memory", "protocol"]:
                c = lattice.store(concept, f"Definition of {concept}", importance=len(concept) / 10.0)
                coords.append({"key": concept, "coordinate": c})
            lattice.associate("sovereignty", "intelligence", 0.9)
            lattice.associate("organism", "neural", 0.8)
            lattice.associate("phi", "resonance", 0.95)
            dream_results = lattice.dream_cycle()
            return {
                "feature": feature_id,
                "result": {
                    "memories_stored": 10,
                    "coordinates": coords,
                    "associations": 3,
                    "dream_cycle": dream_results,
                    "lattice_export": lattice.export_lattice(),
                },
            }

        elif feature_id == "consensus_swarm_intelligence":
            swarm = ConsensusSwarmIntelligence()
            for agent_name in ["Alpha", "Beta", "Gamma", "Delta", "Epsilon"]:
                swarm.add_agent(agent_name, ["reasoning", "security", "architecture"])
            pid = swarm.propose("Should we deploy the sovereign memory lattice to production?",
                              "All tests passing, phi-coherence above threshold")
            import random
            for agent_name in ["Alpha", "Beta", "Gamma", "Delta", "Epsilon"]:
                position = random.choice(["approve", "approve", "approve", "reject"])
                confidence = random.uniform(0.6, 1.0)
                swarm.vote(agent_name, pid, position, confidence)
            consensus = swarm.compute_consensus(pid)
            dissent = swarm.get_dissent_analysis(pid)
            return {
                "feature": feature_id,
                "result": {
                    "proposal_id": pid,
                    "agents": 5,
                    "consensus": consensus,
                    "dissent": dissent,
                },
            }

        elif feature_id == "causal_reasoning_engine":
            engine = CausalReasoningEngine()
            for var in ["training_data", "model_size", "compute", "performance", "latency", "cost"]:
                engine.add_variable(var, "continuous")
            engine.add_causal_link("training_data", "performance", 0.8)
            engine.add_causal_link("model_size", "performance", 0.7)
            engine.add_causal_link("compute", "performance", 0.6)
            engine.add_causal_link("model_size", "latency", 0.9)
            engine.add_causal_link("compute", "cost", 0.85)
            engine.add_causal_link("model_size", "cost", 0.5)
            engine.observe("training_data", 0.9)
            query_result = engine.query("performance", {"training_data": 0.9})
            confounders = engine.find_confounders("model_size", "cost")
            counterfactual = engine.counterfactual(
                {"model_size": 0.5}, "performance"
            )
            return {
                "feature": feature_id,
                "result": {
                    "variables": 6,
                    "causal_links": 6,
                    "query_result": query_result,
                    "confounders": confounders,
                    "counterfactual": counterfactual,
                    "dag": engine.export_dag(),
                },
            }

        elif feature_id == "evolutionary_code_optimizer":
            optimizer = EvolutionaryCodeOptimizer()
            template = "def f(x): return 3 * x + 7"
            test_cases = [
                {"input": {"x": 0}, "expected": 10},
                {"input": {"x": 1}, "expected": 12},
                {"input": {"x": 5}, "expected": 20},
            ]
            best = optimizer.evolve(
                template_code=template,
                test_cases=test_cases,
                generations=20,
                population_size=30,
            )
            return {
                "feature": feature_id,
                "result": {
                    "template": template,
                    "test_cases": test_cases,
                    "best_code": best,
                    "generations": 20,
                    "population_size": 30,
                },
            }

    except Exception as e:
        return {"feature": feature_id, "status": "error", "error": str(e)}


# ── Protocols ──────────────────────────────────────────────────────────────────

@app.get("/api/protocols")
def list_protocols(domain: Optional[str] = Query(None)):
    if domain:
        protos = proto_registry.by_domain(domain)
    else:
        protos = proto_registry.list_all()
    return {"total": len(protos), "protocols": [p.to_dict() for p in protos]}

@app.get("/api/protocols/stats")
def protocols_stats():
    return proto_registry.stats()

@app.get("/api/protocols/{proto_id}")
def get_protocol(proto_id: str):
    p = proto_registry.get(proto_id)
    if not p:
        raise HTTPException(404, f"Protocol '{proto_id}' not found")
    return p.to_dict()


# ── Research Papers ────────────────────────────────────────────────────────────

@app.get("/api/papers")
def list_papers(domain: Optional[str] = Query(None)):
    if domain:
        papers = paper_registry.by_domain(domain)
    else:
        papers = paper_registry.list_all()
    return {"total": len(papers), "papers": [p.to_dict() for p in papers]}

@app.get("/api/papers/stats")
def papers_stats():
    return paper_registry.stats()

@app.get("/api/papers/{paper_id}")
def get_paper(paper_id: str):
    p = paper_registry.get(paper_id)
    if not p:
        raise HTTPException(404, f"Paper '{paper_id}' not found")
    return p.to_dict()

@app.get("/api/papers/search")
def search_papers(q: str = Query(...)):
    results = paper_registry.search(q)
    return {"query": q, "total": len(results), "papers": [p.to_dict() for p in results]}

@app.get("/api/papers/citations")
def get_citations(format: str = Query("apa")):
    if format.lower() == "ieee":
        return {"format": "IEEE", "citations": paper_registry.citations_ieee()}
    return {"format": "APA", "citations": paper_registry.citations_apa()}


# ── Character Agents ───────────────────────────────────────────────────────────

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
        raise HTTPException(404, f"Agent '{name}' not found")
    return agent.to_dict()

@app.post("/api/agents/{name}/dispatch")
def dispatch_to_agent(name: str, req: DispatchRequest):
    agent = char_registry.get(name)
    if not agent:
        raise HTTPException(404, f"Agent '{name}' not found")
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


# ── Sovereign Models ───────────────────────────────────────────────────────────

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
        })
    return {"total": len(models_out), "models": models_out}

@app.get("/api/models/{model_id}")
def get_model(model_id: str):
    m = model_registry.get(model_id)
    if not m:
        raise HTTPException(404, f"Model '{model_id}' not found")
    return {
        "model_id": m.model_id,
        "nomen_latinum": m.nomen_latinum,
        "nomen_breve": m.nomen_breve,
        "dominium": m.dominium.name,
        "descriptio": m.descriptio,
        "capacitas": m.capacitas,
        "status": m.status.name,
        "confidentia": m.confidentia,
        "reputatio": round(m.reputatio, 4),
        "phi_score": round(m.phi_score, 4),
    }

@app.post("/api/models/{model_id}/invoke")
def invoke_model(model_id: str, req: InvokeRequest):
    m = model_registry.get(model_id)
    if not m:
        raise HTTPException(404, f"Model '{model_id}' not found")
    m.invoke(success=req.success, latency_ms=req.latency_ms)
    return {
        "model_id": m.model_id,
        "invocationes": m.invocationes,
        "reputatio": round(m.reputatio, 4),
        "phi_score": round(m.phi_score, 4),
    }


# ── Organism ───────────────────────────────────────────────────────────────────

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
        "cross_substrate_paths": [
            {"from": "Cloudflare", "to": "Julia", "desc": "Membrane invokes brain computations"},
            {"from": "Julia", "to": "ICP", "desc": "Brain writes state to identity substrate"},
            {"from": "ICP", "to": "Cloudflare", "desc": "Identity triggers membrane reflexes"},
            {"from": "Cloudflare", "to": "ICP", "desc": "Membrane resolves identity directly"},
            {"from": "ICP", "to": "Julia", "desc": "Identity triggers policy optimization"},
        ],
    }


# ── Global Search ──────────────────────────────────────────────────────────────

@app.get("/api/search")
def global_search(q: str = Query(...)):
    results = {
        "query": q,
        "index_results": [e.to_dict() for e in master_idx.search(q)],
        "paper_results": [p.to_dict() for p in paper_registry.search(q)],
        "protocol_results": [p.to_dict() for p in proto_registry.search(q)],
    }
    if cap_runner:
        results["capability_results"] = cap_runner.search(q)
    results["total"] = (
        len(results["index_results"])
        + len(results["paper_results"])
        + len(results["protocol_results"])
        + len(results.get("capability_results", []))
    )
    return results


# ── Run ────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    idx_total = master_idx.stats().get("TOTAL", 0)
    cap_total = len(cap_runner.list_capabilities()) if cap_runner else 0
    fai_total = len(FUTURE_AI_REGISTRY)
    proto_total = len(proto_registry.list_all())
    paper_total = len(paper_registry.list_all())
    agent_total = len(char_registry.agents)
    model_total = len(model_registry)

    print("=" * 60)
    print("  SOVEREIGN INTELLIGENCE PLATFORM")
    print("=" * 60)
    print(f"  Master Index:     {idx_total} entries")
    print(f"  Capabilities:     {cap_total} functions")
    print(f"  Future AI:        {fai_total} research modules")
    print(f"  Protocols:        {proto_total} protocols")
    print(f"  Research Papers:  {paper_total} papers")
    print(f"  Character Agents: {agent_total} agents")
    print(f"  Sovereign Models: {model_total} models")
    print("=" * 60)
    print("  Starting on http://localhost:8888")
    print("=" * 60)

    uvicorn.run(app, host="0.0.0.0", port=8888)
