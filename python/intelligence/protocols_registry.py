"""
protocols_registry.py -- Universal Protocol Registry

Registers a formal protocol for every capability and AI-future feature.
Each protocol has an ID, wire format, ring affinity, and integration spec.

(c) 2026 Alfredo Medina Hernandez. All Rights Reserved.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any, Optional


PHI = 1.618033988749895
HEARTBEAT_MS = 873


class Ring(Enum):
    SOVEREIGN = "Sovereign Ring"
    INTERFACE = "Interface Ring"
    MEMORY    = "Memory Ring"
    TRANSPORT = "Transport Ring"
    COUNSEL   = "Counsel Ring"
    GEOMETRY  = "Geometry Ring"


class ProtocolStatus(Enum):
    ACTIVE    = auto()
    DRAFT     = auto()
    PROPOSED  = auto()
    RETIRED   = auto()


@dataclass
class Protocol:
    protocol_id: str
    name: str
    short_name: str
    domain: str
    ring: Ring
    wire: str
    description: str
    capabilities: list[str] = field(default_factory=list)
    modalities: str = "text / structured"
    uses_encryption: bool = False
    adaptive_behavior: str = ""
    status: ProtocolStatus = ProtocolStatus.ACTIVE

    def to_dict(self) -> dict:
        return {
            "protocol_id": self.protocol_id,
            "name": self.name,
            "short_name": self.short_name,
            "domain": self.domain,
            "ring": self.ring.value,
            "wire": self.wire,
            "description": self.description,
            "capabilities": self.capabilities,
            "modalities": self.modalities,
            "uses_encryption": self.uses_encryption,
            "adaptive_behavior": self.adaptive_behavior,
            "status": self.status.name,
        }


# ── All Protocols ──────────────────────────────────────────────────────────────

PROTOCOLS: list[Protocol] = [
    # ── Code Generation Protocols ──────────────────────────────────────────
    Protocol(
        protocol_id="UCAP-001", name="Code Scaffold Generation Protocol",
        short_name="CSGP", domain="code_generation", ring=Ring.INTERFACE,
        wire="capability-wire/csgp",
        description="Generate production-ready code scaffolds for FastAPI, Flask, CLI tools",
        capabilities=["cap_001", "cap_002", "cap_003"],
        adaptive_behavior="Learns preferred frameworks from generation history",
    ),
    Protocol(
        protocol_id="UCAP-002", name="Container Build Protocol",
        short_name="CBP", domain="code_generation", ring=Ring.TRANSPORT,
        wire="capability-wire/cbp",
        description="Generate Dockerfiles, Makefiles, and build configurations",
        capabilities=["cap_004", "cap_005"],
        adaptive_behavior="Adapts base images and targets from project analysis",
    ),

    # ── Business & Planning Protocols ──────────────────────────────────────
    Protocol(
        protocol_id="UCAP-003", name="Business Intelligence Synthesis Protocol",
        short_name="BISP", domain="business", ring=Ring.COUNSEL,
        wire="capability-wire/bisp",
        description="Generate business plans, pitch decks, competitive analysis",
        capabilities=["cap_006", "cap_007", "cap_009"],
        adaptive_behavior="Refines industry templates from completed plans",
    ),
    Protocol(
        protocol_id="UCAP-004", name="Financial Modeling Protocol",
        short_name="FMP", domain="business", ring=Ring.SOVEREIGN,
        wire="capability-wire/fmp",
        description="Calculate runway, burn rate, revenue projections",
        capabilities=["cap_008", "cap_010"],
        uses_encryption=True,
        adaptive_behavior="Adjusts projections from actual vs predicted deltas",
    ),

    # ── Document Assembly Protocols ────────────────────────────────────────
    Protocol(
        protocol_id="UCAP-005", name="Document Composition Protocol",
        short_name="DCP", domain="documents", ring=Ring.MEMORY,
        wire="capability-wire/dcp",
        description="Assemble structured documents, invoices, contracts, READMEs",
        capabilities=["cap_011", "cap_012", "cap_013", "cap_014", "cap_015"],
        adaptive_behavior="Learns document format preferences from user edits",
    ),

    # ── File Indexing Protocols ────────────────────────────────────────────
    Protocol(
        protocol_id="UCAP-006", name="Filesystem Intelligence Protocol",
        short_name="FIP", domain="indexing", ring=Ring.MEMORY,
        wire="capability-wire/fip",
        description="Index directories, search file contents, detect duplicates",
        capabilities=["cap_016", "cap_017", "cap_018", "cap_019", "cap_020"],
        adaptive_behavior="Caches index results, updates incrementally on file changes",
    ),

    # ── Agent Building Protocols ───────────────────────────────────────────
    Protocol(
        protocol_id="UCAP-007", name="Agent Definition Protocol",
        short_name="ADP-U", domain="agents", ring=Ring.SOVEREIGN,
        wire="capability-wire/adp-u",
        description="Create agent definitions, system prompts, tool manifests",
        capabilities=["cap_021", "cap_022", "cap_023"],
        adaptive_behavior="Evolves prompt templates from agent performance metrics",
    ),
    Protocol(
        protocol_id="UCAP-008", name="Agent Workflow Orchestration Protocol",
        short_name="AWOP", domain="agents", ring=Ring.INTERFACE,
        wire="capability-wire/awop",
        description="Generate multi-step agent workflows and evaluation suites",
        capabilities=["cap_024", "cap_025"],
        adaptive_behavior="Optimizes workflow step ordering from execution traces",
    ),

    # ── Data Processing Protocols ──────────────────────────────────────────
    Protocol(
        protocol_id="UCAP-009", name="Data Transformation Protocol",
        short_name="DTP", domain="data", ring=Ring.GEOMETRY,
        wire="capability-wire/dtp",
        description="Convert, merge, pivot, and deduplicate data formats",
        capabilities=["cap_026", "cap_027", "cap_028", "cap_029", "cap_030"],
        adaptive_behavior="Learns column mapping preferences from repeated transforms",
    ),

    # ── API & Networking Protocols ─────────────────────────────────────────
    Protocol(
        protocol_id="UCAP-010", name="API Scaffold Protocol",
        short_name="ASP", domain="networking", ring=Ring.TRANSPORT,
        wire="capability-wire/asp",
        description="Generate OpenAPI specs, REST clients, webhook handlers",
        capabilities=["cap_031", "cap_032", "cap_033"],
        adaptive_behavior="Adapts endpoint patterns from API usage statistics",
    ),
    Protocol(
        protocol_id="UCAP-011", name="Network Security Protocol",
        short_name="NSP-U", domain="networking", ring=Ring.SOVEREIGN,
        wire="capability-wire/nsp-u",
        description="Rate limiting, port scanning, network hardening",
        capabilities=["cap_034", "cap_035"],
        uses_encryption=True,
        adaptive_behavior="Tunes rate limits from traffic pattern analysis",
    ),

    # ── Security Protocols ─────────────────────────────────────────────────
    Protocol(
        protocol_id="UCAP-012", name="Cryptographic Operations Protocol",
        short_name="COP", domain="security", ring=Ring.SOVEREIGN,
        wire="capability-wire/cop",
        description="File hashing, password generation, secret keys, CSP headers",
        capabilities=["cap_036", "cap_037", "cap_038", "cap_039", "cap_040"],
        uses_encryption=True,
        adaptive_behavior="Rotates key lengths based on threat-level signals",
    ),

    # ── DevOps Protocols ───────────────────────────────────────────────────
    Protocol(
        protocol_id="UCAP-013", name="CI/CD Pipeline Protocol",
        short_name="CPP", domain="devops", ring=Ring.TRANSPORT,
        wire="capability-wire/cpp",
        description="GitHub Actions workflows, Nginx configs, Docker Compose",
        capabilities=["cap_041", "cap_042", "cap_043", "cap_044"],
        adaptive_behavior="Learns deployment patterns from pipeline run history",
    ),
    Protocol(
        protocol_id="UCAP-014", name="System Health Monitor Protocol",
        short_name="SHMP", domain="devops", ring=Ring.INTERFACE,
        wire="capability-wire/shmp",
        description="Real-time system health checks and diagnostics",
        capabilities=["cap_045"],
        adaptive_behavior="Establishes baselines and alerts on anomalies",
    ),

    # ── Research & Knowledge Protocols ─────────────────────────────────────
    Protocol(
        protocol_id="UCAP-015", name="Research Synthesis Protocol",
        short_name="RSP", domain="research", ring=Ring.COUNSEL,
        wire="capability-wire/rsp",
        description="Literature reviews, research protocols, citation management",
        capabilities=["cap_046", "cap_047", "cap_048", "cap_049", "cap_050"],
        adaptive_behavior="Refines keyword extraction from citation feedback loops",
    ),

    # ── Future AI Protocols ────────────────────────────────────────────────
    Protocol(
        protocol_id="FAI-001", name="Phi-Resonance Synchronization Protocol",
        short_name="PRSP-F", domain="future_ai", ring=Ring.SOVEREIGN,
        wire="future-wire/prsp-f",
        description="Kuramoto oscillator network with phi-weighted coupling for collective intelligence",
        capabilities=["phi_resonance_network"],
        modalities="numerical / telemetry / resonance",
        adaptive_behavior="Self-adjusts coupling K when coherence R drops below phi-inverse",
    ),
    Protocol(
        protocol_id="FAI-002", name="Evolutionary Code Optimization Protocol",
        short_name="ECOP", domain="future_ai", ring=Ring.GEOMETRY,
        wire="future-wire/ecop",
        description="Genetic algorithm for evolving and optimizing code through mutation and crossover",
        capabilities=["evolutionary_code_optimizer"],
        modalities="code / fitness / population",
        adaptive_behavior="Adjusts mutation rate from fitness plateau detection",
    ),
    Protocol(
        protocol_id="FAI-003", name="Sovereign Memory Lattice Protocol",
        short_name="SMLP", domain="future_ai", ring=Ring.MEMORY,
        wire="future-wire/smlp",
        description="Phi-addressed spatial memory with dream-cycle consolidation",
        capabilities=["sovereign_memory_lattice"],
        modalities="spatial / temporal / associative",
        uses_encryption=True,
        adaptive_behavior="Prunes low-importance memories, strengthens paths during dream cycles",
    ),
    Protocol(
        protocol_id="FAI-004", name="Consensus Swarm Intelligence Protocol",
        short_name="CSIP", domain="future_ai", ring=Ring.SOVEREIGN,
        wire="future-wire/csip",
        description="Multi-agent consensus through phi-weighted voting and dissent analysis",
        capabilities=["consensus_swarm_intelligence"],
        modalities="vote / score / consensus",
        adaptive_behavior="Re-weights agent expertise from consensus accuracy history",
    ),
    Protocol(
        protocol_id="FAI-005", name="Causal Reasoning Protocol",
        short_name="CRP", domain="future_ai", ring=Ring.COUNSEL,
        wire="future-wire/crp",
        description="DAG-based causal inference with counterfactual reasoning",
        capabilities=["causal_reasoning_engine"],
        modalities="graph / inference / counterfactual",
        adaptive_behavior="Discovers hidden confounders from observational data patterns",
    ),
]


# ── Protocol Registry Class ───────────────────────────────────────────────────

class ProtocolRegistry:
    def __init__(self) -> None:
        self._protocols: dict[str, Protocol] = {}
        for p in PROTOCOLS:
            self._protocols[p.protocol_id] = p

    def get(self, protocol_id: str) -> Optional[Protocol]:
        return self._protocols.get(protocol_id)

    def list_all(self) -> list[Protocol]:
        return list(self._protocols.values())

    def by_domain(self, domain: str) -> list[Protocol]:
        return [p for p in self._protocols.values() if p.domain == domain]

    def by_ring(self, ring: Ring) -> list[Protocol]:
        return [p for p in self._protocols.values() if p.ring == ring]

    def by_capability(self, cap_id: str) -> list[Protocol]:
        return [p for p in self._protocols.values() if cap_id in p.capabilities]

    def search(self, term: str) -> list[Protocol]:
        t = term.lower()
        return [
            p for p in self._protocols.values()
            if t in p.name.lower() or t in p.description.lower()
            or t in p.wire.lower() or t in p.domain.lower()
        ]

    def stats(self) -> dict[str, Any]:
        by_domain: dict[str, int] = {}
        by_ring: dict[str, int] = {}
        for p in self._protocols.values():
            by_domain[p.domain] = by_domain.get(p.domain, 0) + 1
            by_ring[p.ring.value] = by_ring.get(p.ring.value, 0) + 1
        return {
            "total_protocols": len(self._protocols),
            "by_domain": by_domain,
            "by_ring": by_ring,
            "encrypted_count": sum(1 for p in self._protocols.values() if p.uses_encryption),
        }

    def export_json(self, filepath: Optional[str] = None) -> str:
        data = {
            "designation": "RSHIP-2026-UNIVERSAL-PROTOCOL-REGISTRY",
            "total_protocols": len(self._protocols),
            "stats": self.stats(),
            "protocols": [p.to_dict() for p in self._protocols.values()],
        }
        payload = json.dumps(data, indent=2)
        if filepath:
            Path(filepath).write_text(payload, encoding="utf-8")
        return payload

    def print_summary(self) -> None:
        print("=" * 72)
        print("  UNIVERSAL PROTOCOL REGISTRY")
        print("=" * 72)
        for p in self._protocols.values():
            enc = "[ENC]" if p.uses_encryption else "     "
            print(f"  {p.protocol_id:<10s} {enc} {p.short_name:<8s} "
                  f"{p.ring.value:<18s} {p.name}")
        st = self.stats()
        print(f"\n  Total: {st['total_protocols']} protocols "
              f"({st['encrypted_count']} encrypted)")
        print("=" * 72)


if __name__ == "__main__":
    reg = ProtocolRegistry()
    reg.print_summary()

    out_dir = Path(__file__).resolve().parent
    json_path = out_dir / "protocols_registry_export.json"
    reg.export_json(str(json_path))
    print(f"\n  Exported -> {json_path}")
