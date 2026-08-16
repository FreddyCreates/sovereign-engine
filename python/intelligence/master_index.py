"""
master_index.py — Sovereign System Master Index

Runtime-queryable registry of EVERY system, protocol, engine, model,
canister, agent, and character AI across the entire Medina codebase.

This is the single source of truth. Import it, query it, extend it.

Usage:
    from master_index import MasterIndex
    idx = MasterIndex()
    idx.query("engines")
    idx.query("protocols", wire="intelligence-wire/srp")
    idx.search("quantum")
    idx.stats()

© 2026 Alfredo Medina Hernandez. All Rights Reserved.
"""

from __future__ import annotations

import csv
import json
import os
import re
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any, Optional


# ── Constants ──────────────────────────────────────────────────────────────────

PHI = 1.618033988749895
# Hardcode workspace roots — OneDrive path resolution is unreliable via __file__
WORKSPACE_AIEOS = Path(os.environ.get(
    "AIEOS_ROOT",
    os.path.expanduser("~/OneDrive/Documents/AIEOSpro")
))
WORKSPACE_TERMINALIS = Path(os.environ.get(
    "TERMINALIS_ROOT",
    os.path.expanduser("~/OneDrive/Documents/Terminalis_Native_Language_Runtime")
))


# ── Entry Types ────────────────────────────────────────────────────────────────

class EntryKind(Enum):
    PROTOCOL       = auto()
    ENGINE_JULIA   = auto()
    ENGINE_PYTHON  = auto()
    TRANSFORMER    = auto()
    SYNTHESIZER    = auto()
    CANISTER       = auto()
    MODEL          = auto()
    AGENT          = auto()
    ORGANISM_LAYER = auto()
    RUNTIME        = auto()


# ── Index Entry ────────────────────────────────────────────────────────────────

@dataclass
class IndexEntry:
    entry_id: str
    kind: EntryKind
    name: str
    file_path: str
    language: str
    ring: str = ""
    wire: str = ""
    status: str = "active"
    description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "entry_id": self.entry_id,
            "kind": self.kind.name,
            "name": self.name,
            "file_path": self.file_path,
            "language": self.language,
            "ring": self.ring,
            "wire": self.wire,
            "status": self.status,
            "description": self.description,
            "metadata": self.metadata,
        }


# ── Master Index ───────────────────────────────────────────────────────────────

class MasterIndex:
    """
    Runtime-queryable master index of the entire Medina sovereign codebase.

    Scans real files on disk and parses the AI_Protocols_Register.csv
    to build a unified, searchable catalog.
    """

    def __init__(self, auto_scan: bool = True) -> None:
        self.entries: list[IndexEntry] = []
        if auto_scan:
            self._scan_protocols()
            self._scan_julia_engines()
            self._scan_julia_transformers()
            self._scan_julia_synthesizers()
            self._scan_python_intelligence()
            self._scan_canisters()
            self._scan_agents()
            self._scan_organism_layers()
            self._scan_terminalis_runtime()

    # ── Protocol Scanner (CSV) ─────────────────────────────────────────────

    def _scan_protocols(self) -> None:
        csv_path = WORKSPACE_AIEOS / "AI_Protocols_Register.csv"
        if not csv_path.exists():
            return
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.entries.append(IndexEntry(
                    entry_id=row.get("protocol_id", ""),
                    kind=EntryKind.PROTOCOL,
                    name=row.get("protocol_name", ""),
                    file_path=str(csv_path),
                    language="multi",
                    ring=row.get("ring_affinity", ""),
                    wire=row.get("wire_protocol", ""),
                    status=row.get("status", "active"),
                    description=row.get("primary_function", ""),
                    metadata={
                        "intelligence_class": row.get("intelligence_class", ""),
                        "engines_wired": row.get("engines_wired", ""),
                        "protocol_type": row.get("protocol_type", ""),
                        "modalities": row.get("modalities", ""),
                        "uses_encryption": row.get("uses_encryption", ""),
                        "organism_placement": row.get("organism_placement", ""),
                        "secondary_functions": row.get("secondary_functions", ""),
                    },
                ))

    # ── Julia Engine Scanner ───────────────────────────────────────────────

    def _scan_julia_engines(self) -> None:
        engines_dir = WORKSPACE_AIEOS / "julia" / "engines"
        if not engines_dir.exists():
            return
        for jl_file in sorted(engines_dir.glob("*.jl")):
            module_name = self._extract_julia_module(jl_file)
            self.entries.append(IndexEntry(
                entry_id=f"JL-ENG-{jl_file.stem.upper()}",
                kind=EntryKind.ENGINE_JULIA,
                name=module_name or jl_file.stem,
                file_path=str(jl_file),
                language="julia",
                ring="Sovereign Ring",
                description=f"Julia engine: {jl_file.stem}",
            ))

    def _scan_julia_transformers(self) -> None:
        t_dir = WORKSPACE_AIEOS / "julia" / "transformers"
        if not t_dir.exists():
            return
        for jl_file in sorted(t_dir.glob("*.jl")):
            module_name = self._extract_julia_module(jl_file)
            self.entries.append(IndexEntry(
                entry_id=f"JL-TFM-{jl_file.stem.upper()}",
                kind=EntryKind.TRANSFORMER,
                name=module_name or jl_file.stem,
                file_path=str(jl_file),
                language="julia",
                ring="Geometry Ring",
                description=f"Julia transformer: {jl_file.stem}",
            ))

    def _scan_julia_synthesizers(self) -> None:
        s_dir = WORKSPACE_AIEOS / "julia" / "synthesizers"
        if not s_dir.exists():
            return
        for jl_file in sorted(s_dir.glob("*.jl")):
            module_name = self._extract_julia_module(jl_file)
            self.entries.append(IndexEntry(
                entry_id=f"JL-SYN-{jl_file.stem.upper()}",
                kind=EntryKind.SYNTHESIZER,
                name=module_name or jl_file.stem,
                file_path=str(jl_file),
                language="julia",
                ring="Sovereign Ring",
                description=f"Julia synthesizer: {jl_file.stem}",
            ))

    @staticmethod
    def _extract_julia_module(filepath: Path) -> str:
        try:
            text = filepath.read_text(encoding="utf-8", errors="ignore")
            m = re.search(r"^module\s+(\w+)", text, re.MULTILINE)
            return m.group(1) if m else ""
        except Exception:
            return ""

    # ── Python Intelligence Scanner ────────────────────────────────────────

    def _scan_python_intelligence(self) -> None:
        py_dir = WORKSPACE_AIEOS / "python" / "intelligence"
        if not py_dir.exists():
            return
        for py_file in sorted(py_dir.glob("*.py")):
            if py_file.name.startswith("__"):
                continue
            docstring = self._extract_python_docstring(py_file)
            self.entries.append(IndexEntry(
                entry_id=f"PY-INT-{py_file.stem.upper()}",
                kind=EntryKind.ENGINE_PYTHON,
                name=py_file.stem,
                file_path=str(py_file),
                language="python",
                ring=self._extract_ring_from_docstring(docstring),
                wire=self._extract_wire_from_docstring(docstring),
                description=docstring[:200] if docstring else "",
            ))

    @staticmethod
    def _extract_python_docstring(filepath: Path) -> str:
        try:
            text = filepath.read_text(encoding="utf-8", errors="ignore")
            m = re.search(r'"""(.*?)"""', text, re.DOTALL)
            return m.group(1).strip() if m else ""
        except Exception:
            return ""

    @staticmethod
    def _extract_ring_from_docstring(doc: str) -> str:
        m = re.search(r"Ring:\s*(.+?)(?:\||$)", doc)
        return m.group(1).strip() if m else ""

    @staticmethod
    def _extract_wire_from_docstring(doc: str) -> str:
        m = re.search(r"Wire:\s*(.+?)(?:\n|$)", doc)
        return m.group(1).strip() if m else ""

    # ── Canister Scanner ───────────────────────────────────────────────────

    def _scan_canisters(self) -> None:
        for canister_dir in ["canister", "canisters"]:
            c_dir = WORKSPACE_AIEOS / canister_dir
            if not c_dir.exists():
                continue
            for mo_file in sorted(c_dir.rglob("*.mo")):
                actor_name = self._extract_motoko_actor(mo_file)
                self.entries.append(IndexEntry(
                    entry_id=f"MO-CAN-{mo_file.stem.upper()}",
                    kind=EntryKind.CANISTER,
                    name=actor_name or mo_file.stem,
                    file_path=str(mo_file),
                    language="motoko",
                    ring="Sovereign Ring",
                    description=f"Motoko canister: {mo_file.stem}",
                ))

    @staticmethod
    def _extract_motoko_actor(filepath: Path) -> str:
        try:
            text = filepath.read_text(encoding="utf-8", errors="ignore")
            m = re.search(r"actor\s+(?:class\s+)?(\w+)", text)
            return m.group(1) if m else ""
        except Exception:
            return ""

    # ── Agent Scanner ──────────────────────────────────────────────────────

    def _scan_agents(self) -> None:
        agents_dir = WORKSPACE_AIEOS / "agents"
        if not agents_dir.exists():
            return
        for agent_file in sorted(agents_dir.glob("*")):
            if agent_file.is_file():
                self.entries.append(IndexEntry(
                    entry_id=f"AGENT-{agent_file.stem.upper().replace('-', '_')}",
                    kind=EntryKind.AGENT,
                    name=agent_file.stem.replace("-", " ").title(),
                    file_path=str(agent_file),
                    language="markdown" if agent_file.suffix == ".md" else "unknown",
                    ring="Counsel Ring",
                    description=f"Character agent: {agent_file.stem}",
                ))

    # ── Organism Layer Scanner ─────────────────────────────────────────────

    def _scan_organism_layers(self) -> None:
        org_dir = WORKSPACE_AIEOS / "organism"
        if not org_dir.exists():
            return
        for sub in sorted(org_dir.iterdir()):
            if sub.is_dir():
                file_count = sum(1 for _ in sub.rglob("*") if _.is_file())
                self.entries.append(IndexEntry(
                    entry_id=f"ORG-LAYER-{sub.name.upper()}",
                    kind=EntryKind.ORGANISM_LAYER,
                    name=sub.name,
                    file_path=str(sub),
                    language="multi",
                    ring="Sovereign Ring",
                    description=f"Organism layer: {sub.name} ({file_count} files)",
                ))

    # ── Terminalis Runtime Scanner ─────────────────────────────────────────

    def _scan_terminalis_runtime(self) -> None:
        for scan_dir in [
            WORKSPACE_TERMINALIS / "terminalis_native_language",
            WORKSPACE_TERMINALIS / "SRC",
        ]:
            if not scan_dir.exists():
                continue
            for py_file in sorted(scan_dir.rglob("*.py")):
                self.entries.append(IndexEntry(
                    entry_id=f"TERM-{py_file.stem.upper()}",
                    kind=EntryKind.RUNTIME,
                    name=py_file.stem,
                    file_path=str(py_file),
                    language="python",
                    ring="Sovereign Ring",
                    description=f"Terminalis runtime module: {py_file.stem}",
                ))

    # ── Query Interface ────────────────────────────────────────────────────

    def query(
        self,
        kind: Optional[str] = None,
        ring: Optional[str] = None,
        wire: Optional[str] = None,
        language: Optional[str] = None,
        status: Optional[str] = None,
    ) -> list[IndexEntry]:
        """Filter entries by kind, ring, wire, language, or status."""
        results = self.entries
        if kind:
            kind_upper = kind.upper()
            results = [e for e in results if kind_upper in e.kind.name]
        if ring:
            results = [e for e in results if ring.lower() in e.ring.lower()]
        if wire:
            results = [e for e in results if wire.lower() in e.wire.lower()]
        if language:
            results = [e for e in results if e.language == language.lower()]
        if status:
            results = [e for e in results if e.status == status.lower()]
        return results

    def search(self, term: str) -> list[IndexEntry]:
        """Full-text search across name, description, wire, and ring."""
        t = term.lower()
        return [
            e for e in self.entries
            if t in e.name.lower()
            or t in e.description.lower()
            or t in e.wire.lower()
            or t in e.ring.lower()
            or t in e.entry_id.lower()
        ]

    def get(self, entry_id: str) -> Optional[IndexEntry]:
        """Get a single entry by its ID."""
        for e in self.entries:
            if e.entry_id == entry_id:
                return e
        return None

    # ── Stats ──────────────────────────────────────────────────────────────

    def stats(self) -> dict[str, int]:
        """Count entries by kind."""
        counts: dict[str, int] = {}
        for e in self.entries:
            key = e.kind.name
            counts[key] = counts.get(key, 0) + 1
        counts["TOTAL"] = len(self.entries)
        return counts

    # ── Export ──────────────────────────────────────────────────────────────

    def export_json(self, filepath: Optional[str] = None) -> str:
        """Export the full index to JSON."""
        data = {
            "designation": "RSHIP-2026-MASTER-INDEX-001",
            "total_entries": len(self.entries),
            "stats": self.stats(),
            "entries": [e.to_dict() for e in self.entries],
        }
        payload = json.dumps(data, indent=2)
        if filepath:
            Path(filepath).write_text(payload, encoding="utf-8")
        return payload

    def export_csv(self, filepath: str) -> None:
        """Export the full index to CSV."""
        if not self.entries:
            return
        fieldnames = [
            "entry_id", "kind", "name", "language",
            "ring", "wire", "status", "file_path", "description",
        ]
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for e in self.entries:
                writer.writerow({
                    "entry_id": e.entry_id,
                    "kind": e.kind.name,
                    "name": e.name,
                    "language": e.language,
                    "ring": e.ring,
                    "wire": e.wire,
                    "status": e.status,
                    "file_path": e.file_path,
                    "description": e.description[:120],
                })

    # ── Display ────────────────────────────────────────────────────────────

    def print_summary(self) -> None:
        """Print a formatted summary to stdout."""
        print("=" * 72)
        print("  SOVEREIGN MASTER INDEX - All Systems & Character AI")
        print("=" * 72)
        st = self.stats()
        for k, v in sorted(st.items()):
            if k != "TOTAL":
                print(f"  {k:<20s} {v:>4d}")
        print(f"  {'-' * 30}")
        print(f"  {'TOTAL':<20s} {st['TOTAL']:>4d}")
        print("=" * 72)


# ── CLI Entry Point ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    idx = MasterIndex()
    idx.print_summary()

    # Export JSON + CSV alongside this script
    out_dir = Path(__file__).resolve().parent
    json_path = out_dir / "master_index_export.json"
    csv_path = out_dir / "master_index_export.csv"

    idx.export_json(str(json_path))
    idx.export_csv(str(csv_path))

    print(f"\n  Exported JSON -> {json_path}")
    print(f"  Exported CSV  -> {csv_path}")

    # Optional search from CLI args
    if len(sys.argv) > 1:
        term = " ".join(sys.argv[1:])
        results = idx.search(term)
        print(f"\n  Search: '{term}' → {len(results)} results")
        for r in results:
            print(f"    [{r.kind.name}] {r.entry_id}: {r.name}")
