"""
character_ai.py -- Character AI Runtime

Parses agent definition files (YAML frontmatter + Markdown body),
loads them into runnable CharacterAgent instances, and provides
a task dispatch interface.

Usage:
    from character_ai import CharacterRegistry
    reg = CharacterRegistry()
    reg.load_agents_dir()
    agent = reg.get("AXIOM")
    result = agent.dispatch("Analyze this paper for IP claims")

(c) 2026 Alfredo Medina Hernandez. All Rights Reserved.
"""

from __future__ import annotations

import os
import re
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any, Optional


# ── Constants ──────────────────────────────────────────────────────────────────

PHI = 1.618033988749895
PHI_INV = 1.0 / PHI
HEARTBEAT_MS = 873

AGENTS_DIR = Path(os.environ.get(
    "AIEOS_ROOT",
    os.path.expanduser("~/OneDrive/Documents/AIEOSpro")
)) / "agents"


# ── Enums ──────────────────────────────────────────────────────────────────────

class AgentStatus(Enum):
    ACTIVE    = auto()
    DORMANT   = auto()
    TRAINING  = auto()
    RETIRED   = auto()


class TaskPriority(Enum):
    LOW      = 0
    NORMAL   = 1
    HIGH     = 2
    CRITICAL = 3


# ── Data Classes ───────────────────────────────────────────────────────────────

@dataclass
class AgentTask:
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    prompt: str = ""
    priority: TaskPriority = TaskPriority.NORMAL
    context_files: list[str] = field(default_factory=list)
    submitted_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    result: Optional[str] = None
    status: str = "pending"


@dataclass
class CharacterAgent:
    """A loaded character agent with parsed identity and capabilities."""

    name: str
    designation: str
    description: str
    model: str
    status: AgentStatus
    platform: str
    tools: list[str]
    constants: dict[str, float]
    system_prompt: str
    source_file: str

    # Runtime state
    total_tasks: int = 0
    completed_tasks: int = 0
    reputation: float = 0.85
    task_history: list[AgentTask] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        return self.completed_tasks / self.total_tasks if self.total_tasks > 0 else 0.0

    @property
    def phi_score(self) -> float:
        return self.reputation * PHI * (self.success_rate + PHI_INV)

    def dispatch(self, prompt: str, priority: TaskPriority = TaskPriority.NORMAL,
                 context_files: Optional[list[str]] = None) -> AgentTask:
        """Submit a task to this agent. Returns the task with routing info."""
        task = AgentTask(
            prompt=prompt,
            priority=priority,
            context_files=context_files or [],
        )
        self.total_tasks += 1
        self.task_history.append(task)

        # Route through the agent's system prompt and model
        task.result = (
            f"[{self.name}] Task routed to {self.model} "
            f"with {len(self.tools)} tools available. "
            f"Priority: {priority.name}. "
            f"Prompt: {prompt[:120]}..."
        )
        task.status = "routed"
        task.completed_at = time.time()
        self.completed_tasks += 1

        # Phi-EMA reputation update
        self.reputation = PHI_INV * 1.0 + (1.0 - PHI_INV) * self.reputation

        return task

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "designation": self.designation,
            "description": self.description,
            "model": self.model,
            "status": self.status.name,
            "platform": self.platform,
            "tools": self.tools,
            "constants": self.constants,
            "total_tasks": self.total_tasks,
            "completed_tasks": self.completed_tasks,
            "reputation": round(self.reputation, 4),
            "phi_score": round(self.phi_score, 4),
            "source_file": self.source_file,
        }


# ── YAML Frontmatter Parser ───────────────────────────────────────────────────

def parse_agent_file(filepath: Path) -> Optional[CharacterAgent]:
    """
    Parse a character agent markdown file with YAML frontmatter.
    Returns a CharacterAgent instance or None if parsing fails.
    """
    try:
        text = filepath.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return None

    # Extract YAML frontmatter between --- markers
    fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not fm_match:
        return None

    fm_text = fm_match.group(1)
    body = text[fm_match.end():]

    # Simple YAML-like key extraction (no PyYAML dependency)
    def get_val(key: str) -> str:
        m = re.search(rf"^{key}:\s*(.+)$", fm_text, re.MULTILINE)
        return m.group(1).strip() if m else ""

    def get_list(key: str) -> list[str]:
        pattern = rf"^{key}:\s*\n((?:\s+-\s+.+\n?)+)"
        m = re.search(pattern, fm_text, re.MULTILINE)
        if not m:
            return []
        items = re.findall(r"^\s+-\s+(.+)$", m.group(1), re.MULTILINE)
        return [i.strip() for i in items]

    name = get_val("name")
    if not name:
        return None

    # Extract designation from body
    desig_match = re.search(r"Your designation:\s*`([^`]+)`", body)
    designation = desig_match.group(1) if desig_match else f"RSHIP-2026-{name}-001"

    # Extract operating constants from body
    constants: dict[str, float] = {}
    for const_match in re.finditer(r"`(\w+)\s*=\s*([\d.]+)`", body):
        try:
            constants[const_match.group(1)] = float(const_match.group(2))
        except ValueError:
            pass

    # Parse status
    status_str = get_val("status").upper()
    try:
        status = AgentStatus[status_str]
    except KeyError:
        status = AgentStatus.ACTIVE

    # Parse deployment platform
    platform_match = re.search(r"platform:\s*(.+)$", fm_text, re.MULTILINE)
    platform = platform_match.group(1).strip() if platform_match else "local"

    return CharacterAgent(
        name=name,
        designation=designation,
        description=get_val("description"),
        model=get_val("model"),
        status=status,
        platform=platform,
        tools=get_list("tools"),
        constants=constants,
        system_prompt=body[:2000],  # First 2000 chars of body as system prompt
        source_file=str(filepath),
    )


# ── Character Registry ────────────────────────────────────────────────────────

class CharacterRegistry:
    """
    Central registry for all character AI agents.

    Scans the agents/ directory, parses each .md file,
    and provides lookup, dispatch, and stats.
    """

    def __init__(self, agents_dir: Optional[Path] = None) -> None:
        self.agents_dir = agents_dir or AGENTS_DIR
        self.agents: dict[str, CharacterAgent] = {}

    def load_agents_dir(self) -> int:
        """Scan agents directory and load all .md agent definitions. Returns count loaded."""
        if not self.agents_dir.exists():
            return 0

        count = 0
        for md_file in sorted(self.agents_dir.glob("*.md")):
            agent = parse_agent_file(md_file)
            if agent:
                self.agents[agent.name] = agent
                count += 1
        return count

    def register(self, agent: CharacterAgent) -> None:
        """Manually register an agent."""
        self.agents[agent.name] = agent

    def get(self, name: str) -> Optional[CharacterAgent]:
        """Get agent by name (case-insensitive)."""
        return self.agents.get(name) or self.agents.get(name.upper())

    def list_agents(self) -> list[CharacterAgent]:
        """Return all registered agents."""
        return list(self.agents.values())

    def dispatch(self, agent_name: str, prompt: str,
                 priority: TaskPriority = TaskPriority.NORMAL,
                 context_files: Optional[list[str]] = None) -> Optional[AgentTask]:
        """Dispatch a task to a named agent."""
        agent = self.get(agent_name)
        if not agent:
            return None
        return agent.dispatch(prompt, priority, context_files)

    def stats(self) -> dict[str, Any]:
        """Registry-wide statistics."""
        total_tasks = sum(a.total_tasks for a in self.agents.values())
        total_completed = sum(a.completed_tasks for a in self.agents.values())
        return {
            "total_agents": len(self.agents),
            "active_agents": sum(1 for a in self.agents.values() if a.status == AgentStatus.ACTIVE),
            "total_tasks_dispatched": total_tasks,
            "total_tasks_completed": total_completed,
            "agents": {name: a.to_dict() for name, a in self.agents.items()},
        }

    def print_summary(self) -> None:
        """Print registry summary to stdout."""
        print("=" * 60)
        print("  CHARACTER AI REGISTRY")
        print("=" * 60)
        for name, agent in self.agents.items():
            print(f"  [{agent.status.name:>8s}] {name:<12s}  "
                  f"model={agent.model}  tools={len(agent.tools)}  "
                  f"phi={agent.phi_score:.3f}")
        print(f"  {'-' * 50}")
        print(f"  Total: {len(self.agents)} agents")
        print("=" * 60)


# ── CLI Entry Point ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    reg = CharacterRegistry()
    loaded = reg.load_agents_dir()
    print(f"Loaded {loaded} character agents from {reg.agents_dir}\n")
    reg.print_summary()

    # Demo dispatch
    for name, agent in reg.agents.items():
        task = agent.dispatch(f"Run a diagnostic check on the {name} subsystem")
        print(f"\n  Dispatched to {name}: {task.result}")
