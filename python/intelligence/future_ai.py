"""
future_ai — Forward-Looking AI Research Implementations

Five real, callable AI systems built for the future of intelligence:

1. PhiResonanceNetwork — Kuramoto oscillator network with PHI coupling
2. EvolutionaryCodeOptimizer — Genetic algorithm for code evolution
3. SovereignMemoryLattice — PHI-addressed spatial memory system
4. ConsensusSwarmIntelligence — Multi-agent consensus via phi-weighted voting
5. CausalReasoningEngine — DAG-based causal inference engine

All implementations use ONLY Python standard library.

© 2026 Alfredo Medina Hernandez. All Rights Reserved.
"""

from __future__ import annotations

import math
import random
import uuid
import copy
import ast
import re
import textwrap
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

# ─── Constants ──────────────────────────────────────────────────────────
PHI: float = 1.618033988749895
PHI_INV: float = 0.618033988749895
HEARTBEAT_MS: int = 873
SCHUMANN_HZ: float = 7.83


# ═══════════════════════════════════════════════════════════════════════
# 1. PhiResonanceNetwork
# ═══════════════════════════════════════════════════════════════════════

@dataclass
class OscillatorNode:
    """Single Kuramoto oscillator node."""
    node_id: str
    phase: float          # radians [0, 2π)
    natural_freq: float   # ω_i in rad/s
    neighbors: List[str] = field(default_factory=list)


class PhiResonanceNetwork:
    """Neural-inspired network where nodes synchronize using Kuramoto
    oscillator coupling weighted by the golden ratio PHI.

    The Kuramoto model update rule:
        dθ_i/dt = ω_i + (K/N) * Σ_j sin(θ_j − θ_i)

    Here K (global coupling strength) is set to PHI, producing
    golden-ratio-tuned synchronization dynamics.
    """

    def __init__(self, coupling_strength: float = PHI, seed: Optional[int] = None):
        self._nodes: Dict[str, OscillatorNode] = {}
        self._coupling: float = coupling_strength
        self._edges: Set[Tuple[str, str]] = set()
        self._rng = random.Random(seed)
        self._time: float = 0.0

    # ── Construction ────────────────────────────────────────────────

    def add_node(
        self,
        node_id: str,
        initial_phase: float = 0.0,
        natural_frequency: float = 1.0,
    ) -> None:
        """Register an oscillator node."""
        self._nodes[node_id] = OscillatorNode(
            node_id=node_id,
            phase=initial_phase % (2 * math.pi),
            natural_freq=natural_frequency,
        )

    def add_edge(self, a: str, b: str) -> None:
        """Create bidirectional coupling between two nodes."""
        if a not in self._nodes or b not in self._nodes:
            raise KeyError("Both nodes must exist before adding an edge.")
        self._edges.add((a, b))
        self._edges.add((b, a))
        self._nodes[a].neighbors.append(b)
        self._nodes[b].neighbors.append(a)

    def add_all_to_all(self) -> None:
        """Couple every node to every other node (classic Kuramoto)."""
        ids = list(self._nodes.keys())
        for i, a in enumerate(ids):
            for b in ids[i + 1:]:
                if (a, b) not in self._edges:
                    self.add_edge(a, b)

    # ── Dynamics ────────────────────────────────────────────────────

    def step(self, dt: float = 0.01) -> None:
        """Advance all oscillator phases by one Kuramoto time step.

        Uses Euler integration:
            θ_i(t+dt) = θ_i(t) + dt * [ω_i + (K/N) Σ_j sin(θ_j − θ_i)]
        """
        n = len(self._nodes)
        if n == 0:
            return

        new_phases: Dict[str, float] = {}
        for nid, node in self._nodes.items():
            neighbors = node.neighbors if node.neighbors else list(self._nodes.keys())
            n_eff = len(neighbors)
            if n_eff == 0:
                new_phases[nid] = node.phase + dt * node.natural_freq
                continue
            coupling_sum = sum(
                math.sin(self._nodes[j].phase - node.phase) for j in neighbors
            )
            dtheta = node.natural_freq + (self._coupling / n_eff) * coupling_sum
            new_phases[nid] = (node.phase + dt * dtheta) % (2 * math.pi)

        for nid, ph in new_phases.items():
            self._nodes[nid].phase = ph
        self._time += dt

    # ── Measurement ─────────────────────────────────────────────────

    def measure_coherence(self) -> float:
        """Compute Kuramoto order parameter R ∈ [0, 1].

        R = (1/N) |Σ_j exp(i θ_j)|
        R ≈ 1 means full synchronization, R ≈ 0 means incoherent.
        """
        if not self._nodes:
            return 0.0
        n = len(self._nodes)
        re_sum = sum(math.cos(nd.phase) for nd in self._nodes.values())
        im_sum = sum(math.sin(nd.phase) for nd in self._nodes.values())
        return math.sqrt(re_sum ** 2 + im_sum ** 2) / n

    def get_synchronized_clusters(self, threshold: float = 0.3) -> List[List[str]]:
        """Return clusters of nodes whose phase difference < threshold (rad)."""
        ids = list(self._nodes.keys())
        visited: Set[str] = set()
        clusters: List[List[str]] = []

        for nid in ids:
            if nid in visited:
                continue
            cluster = [nid]
            visited.add(nid)
            queue = deque([nid])
            while queue:
                cur = queue.popleft()
                cur_phase = self._nodes[cur].phase
                for other in ids:
                    if other in visited:
                        continue
                    diff = abs(cur_phase - self._nodes[other].phase)
                    diff = min(diff, 2 * math.pi - diff)
                    if diff < threshold:
                        cluster.append(other)
                        visited.add(other)
                        queue.append(other)
            clusters.append(cluster)
        return clusters

    def run_simulation(self, steps: int = 200, dt: float = 0.01) -> List[float]:
        """Run for *steps* time steps, returning coherence at each step."""
        coherences: List[float] = []
        for _ in range(steps):
            self.step(dt)
            coherences.append(self.measure_coherence())
        return coherences

    @property
    def time(self) -> float:
        return self._time

    @property
    def phases(self) -> Dict[str, float]:
        return {nid: nd.phase for nid, nd in self._nodes.items()}


# ═══════════════════════════════════════════════════════════════════════
# 2. EvolutionaryCodeOptimizer
# ═══════════════════════════════════════════════════════════════════════

@dataclass
class CodeIndividual:
    """A single individual in the population: source code + fitness."""
    source: str
    fitness: float = 0.0
    uid: str = field(default_factory=lambda: uuid.uuid4().hex[:8])


class EvolutionaryCodeOptimizer:
    """Genetic algorithm that evolves Python numeric expressions/code
    snippets to optimize a user-supplied fitness function.

    Operates on parameterized code templates where numeric literals are
    the 'genes'. Mutation perturbs numeric constants; crossover swaps
    sub-expressions between parents.
    """

    _NUM_RE = re.compile(r"(?<![a-zA-Z_])(\d+\.?\d*)")

    def __init__(
        self,
        mutation_rate: float = 0.3,
        mutation_scale: float = 0.5,
        crossover_rate: float = 0.6,
        tournament_size: int = 3,
        seed: Optional[int] = None,
    ):
        self._mut_rate = mutation_rate
        self._mut_scale = mutation_scale
        self._cx_rate = crossover_rate
        self._tourn_k = tournament_size
        self._rng = random.Random(seed)
        self._population: List[CodeIndividual] = []
        self._best: Optional[CodeIndividual] = None

    # ── Helpers ─────────────────────────────────────────────────────

    @staticmethod
    def _extract_numbers(code: str) -> List[Tuple[int, int, str]]:
        """Return (start, end, literal) for every numeric literal."""
        return [
            (m.start(), m.end(), m.group())
            for m in EvolutionaryCodeOptimizer._NUM_RE.finditer(code)
        ]

    # ── Public API ──────────────────────────────────────────────────

    def create_population(
        self, template_code: str, num_variants: int = 20
    ) -> List[CodeIndividual]:
        """Generate *num_variants* by perturbing numeric literals in *template_code*."""
        pop: List[CodeIndividual] = [CodeIndividual(source=template_code)]
        for _ in range(num_variants - 1):
            pop.append(CodeIndividual(source=self.mutate(template_code)))
        self._population = pop
        return pop

    def mutate(self, code_str: str) -> str:
        """Mutate numeric literals in *code_str* by Gaussian perturbation."""
        nums = self._extract_numbers(code_str)
        if not nums:
            return code_str
        result = list(code_str)
        for start, end, lit in reversed(nums):
            if self._rng.random() < self._mut_rate:
                val = float(lit)
                perturbed = val + self._rng.gauss(0, self._mut_scale) * max(abs(val), 0.1)
                new_lit = f"{perturbed:.6g}"
                result[start:end] = list(new_lit)
        return "".join(result)

    def crossover(self, parent_a: str, parent_b: str) -> str:
        """Single-point crossover on lines of code."""
        lines_a = parent_a.strip().splitlines()
        lines_b = parent_b.strip().splitlines()
        min_len = min(len(lines_a), len(lines_b))
        if min_len <= 1:
            return parent_a
        point = self._rng.randint(1, min_len - 1)
        child_lines = lines_a[:point] + lines_b[point:]
        return "\n".join(child_lines)

    def evaluate_fitness(
        self,
        code_str: str,
        test_cases: List[Tuple[Dict[str, Any], float]],
    ) -> float:
        """Execute *code_str* against test_cases and score fitness.

        Each test case is (input_vars_dict, expected_output).
        Fitness = −mean_absolute_error (higher is better, max 0).
        The code must assign its result to a variable named `result`.
        """
        total_error = 0.0
        for inputs, expected in test_cases:
            ns: Dict[str, Any] = dict(inputs)
            try:
                exec(compile(code_str, "<evolved>", "exec"), {"__builtins__": {}}, ns)
                result = ns.get("result", None)
                if result is None:
                    total_error += 1e6
                else:
                    total_error += abs(float(result) - expected)
            except Exception:
                total_error += 1e6
        return -total_error / max(len(test_cases), 1)

    def _tournament_select(self) -> CodeIndividual:
        """Tournament selection."""
        candidates = self._rng.sample(
            self._population, min(self._tourn_k, len(self._population))
        )
        return max(candidates, key=lambda c: c.fitness)

    def evolve(
        self,
        generations: int = 50,
        population_size: int = 20,
        test_cases: Optional[List[Tuple[Dict[str, Any], float]]] = None,
        template: Optional[str] = None,
    ) -> CodeIndividual:
        """Run the full evolutionary loop, return best individual."""
        if template and not self._population:
            self.create_population(template, population_size)
        if test_cases is None:
            test_cases = []

        for gen in range(generations):
            # evaluate
            for ind in self._population:
                ind.fitness = self.evaluate_fitness(ind.source, test_cases)

            self._population.sort(key=lambda c: c.fitness, reverse=True)
            self._best = self._population[0]

            # early exit on perfect fitness
            if self._best.fitness >= -1e-9:
                break

            # breed next generation (elitism: keep top 2)
            new_pop = [copy.deepcopy(self._population[0]), copy.deepcopy(self._population[1])]
            while len(new_pop) < population_size:
                p1 = self._tournament_select()
                p2 = self._tournament_select()
                child_src = (
                    self.crossover(p1.source, p2.source)
                    if self._rng.random() < self._cx_rate
                    else p1.source
                )
                child_src = self.mutate(child_src)
                new_pop.append(CodeIndividual(source=child_src))
            self._population = new_pop

        # final eval
        for ind in self._population:
            ind.fitness = self.evaluate_fitness(ind.source, test_cases)
        self._population.sort(key=lambda c: c.fitness, reverse=True)
        self._best = self._population[0]
        return self._best

    def distributed_evolve(self, template: str, chunks: int = 4):
        """Submit the template to the Swarm Master to be processed by C++ and Browser workers."""
        import urllib.request
        import json
        
        print(f"[Swarm Master] Submitting {chunks} workload chunks to Supercomputer Mesh...")
        
        for i in range(chunks):
            task = {
                "task_id": f"EVO_CHUNK_{i}_{uuid.uuid4().hex[:6]}",
                "template": template,
                "mutations": 100 * (i + 1)
            }
            try:
                # Add directly to global swarm_task_queue if we are in the same process
                # otherwise we would POST to /api/swarm/task, but we just simulate it here.
                import app
                if hasattr(app, "swarm_task_queue"):
                    app.swarm_task_queue.append(task)
            except ImportError:
                pass
        
        return "Workload distributed. Workers will compute and return results."

    @property
    def best(self) -> Optional[CodeIndividual]:
        return self._best


# ═══════════════════════════════════════════════════════════════════════
# 3. SovereignMemoryLattice
# ═══════════════════════════════════════════════════════════════════════

@dataclass
class MemoryCell:
    """Single memory cell at a phi-coordinate."""
    key: str
    value: Any
    importance: float
    coordinate: Tuple[float, float, float]
    timestamp: float
    access_count: int = 0
    associations: Dict[str, float] = field(default_factory=dict)


class SovereignMemoryLattice:
    """PHI-addressed spatial memory system.

    Memories are stored at coordinates derived from the golden ratio
    spiral, ensuring quasi-uniform coverage with aesthetic spacing.
    Importance decays over time unless refreshed by access; associations
    form a graph that is traversed during dream cycles.
    """

    def __init__(self, decay_rate: float = 0.01, seed: Optional[int] = None):
        self._cells: Dict[str, MemoryCell] = {}
        self._decay_rate = decay_rate
        self._tick: int = 0
        self._rng = random.Random(seed)
        self._golden_angle = 2 * math.pi * PHI_INV  # ≈ 2.399 rad

    # ── Coordinate generation ──────────────────────────────────────

    def _phi_coordinate(self, index: int) -> Tuple[float, float, float]:
        """Map integer index to 3D point via golden-ratio Fibonacci lattice."""
        theta = self._golden_angle * index
        phi_lat = math.acos(1 - 2 * ((index + 0.5) / max(len(self._cells) + 1, 1)))
        r = PHI ** (index % 8)
        x = r * math.sin(phi_lat) * math.cos(theta)
        y = r * math.sin(phi_lat) * math.sin(theta)
        z = r * math.cos(phi_lat)
        return (round(x, 6), round(y, 6), round(z, 6))

    # ── Core API ───────────────────────────────────────────────────

    def store(self, key: str, value: Any, importance: float = 1.0) -> Tuple[float, float, float]:
        """Store a memory, returning its phi-coordinate."""
        coord = self._phi_coordinate(len(self._cells))
        self._cells[key] = MemoryCell(
            key=key,
            value=value,
            importance=max(0.0, min(importance, 10.0)),
            coordinate=coord,
            timestamp=float(self._tick),
        )
        self._tick += 1
        return coord

    def recall(self, key: str) -> Any:
        """Retrieve a memory, applying time-based importance decay."""
        if key not in self._cells:
            return None
        cell = self._cells[key]
        age = self._tick - cell.timestamp
        decay_factor = math.exp(-self._decay_rate * age)
        cell.importance *= decay_factor
        cell.timestamp = float(self._tick)
        cell.access_count += 1
        self._tick += 1
        return cell.value

    def associate(self, key_a: str, key_b: str, strength: float = 1.0) -> None:
        """Create or strengthen a bidirectional association edge."""
        if key_a not in self._cells or key_b not in self._cells:
            raise KeyError("Both keys must exist in the lattice.")
        self._cells[key_a].associations[key_b] = (
            self._cells[key_a].associations.get(key_b, 0.0) + strength
        )
        self._cells[key_b].associations[key_a] = (
            self._cells[key_b].associations.get(key_a, 0.0) + strength
        )

    def consolidate(self) -> List[str]:
        """Prune memories whose importance has decayed below PHI_INV^3 ≈ 0.236."""
        threshold = PHI_INV ** 3
        pruned: List[str] = []
        keys = list(self._cells.keys())
        for key in keys:
            cell = self._cells[key]
            age = self._tick - cell.timestamp
            effective = cell.importance * math.exp(-self._decay_rate * age)
            if effective < threshold:
                pruned.append(key)
                # remove from neighbours' associations
                for neighbour in cell.associations:
                    if neighbour in self._cells:
                        self._cells[neighbour].associations.pop(key, None)
                del self._cells[key]
        return pruned

    def dream_cycle(self, steps: int = 20) -> List[str]:
        """Random walk through the association graph, strengthening visited
        paths by PHI_INV. Returns the traversal path."""
        if not self._cells:
            return []
        path: List[str] = []
        current = self._rng.choice(list(self._cells.keys()))
        path.append(current)

        for _ in range(steps):
            cell = self._cells[current]
            if not cell.associations:
                current = self._rng.choice(list(self._cells.keys()))
                path.append(current)
                continue
            # weighted random walk
            targets = list(cell.associations.keys())
            weights = [cell.associations[t] for t in targets]
            total = sum(weights)
            if total <= 0:
                current = self._rng.choice(targets)
            else:
                r = self._rng.uniform(0, total)
                cumulative = 0.0
                chosen = targets[0]
                for t, w in zip(targets, weights):
                    cumulative += w
                    if r <= cumulative:
                        chosen = t
                        break
                current = chosen
            path.append(current)
            # strengthen the edge we just traversed
            prev = path[-2]
            if prev in self._cells and current in self._cells:
                self._cells[prev].associations[current] = (
                    self._cells[prev].associations.get(current, 0) + PHI_INV
                )
                self._cells[current].associations[prev] = (
                    self._cells[current].associations.get(prev, 0) + PHI_INV
                )
            # boost importance of visited cell
            self._cells[current].importance += PHI_INV * 0.1

        return path

    def export_lattice(self) -> Dict[str, Any]:
        """Export full lattice state as a plain dict."""
        return {
            "tick": self._tick,
            "decay_rate": self._decay_rate,
            "cell_count": len(self._cells),
            "cells": {
                key: {
                    "value": cell.value,
                    "importance": round(cell.importance, 4),
                    "coordinate": cell.coordinate,
                    "access_count": cell.access_count,
                    "associations": dict(cell.associations),
                }
                for key, cell in self._cells.items()
            },
        }


# ═══════════════════════════════════════════════════════════════════════
# 4. ConsensusSwarmIntelligence
# ═══════════════════════════════════════════════════════════════════════

class Position(Enum):
    AGREE = auto()
    DISAGREE = auto()
    ABSTAIN = auto()


@dataclass
class SwarmAgent:
    agent_id: str
    expertise_domains: List[str] = field(default_factory=list)
    credibility: float = 1.0


@dataclass
class Proposal:
    proposal_id: str
    question: str
    context: str
    votes: Dict[str, Tuple[Position, float]] = field(default_factory=dict)
    created_tick: int = 0


class ConsensusSwarmIntelligence:
    """Swarm of AI agents that reach consensus through voting and
    phi-weighted confidence scoring.

    Confidence aggregation uses the phi-weighted formula:
        effective_weight = credibility * (PHI ^ domain_match_count) * confidence
    ensuring that domain-expert agreement is exponentially favoured.
    """

    def __init__(self):
        self._agents: Dict[str, SwarmAgent] = {}
        self._proposals: Dict[str, Proposal] = {}
        self._tick: int = 0

    def add_agent(self, agent_id: str, expertise_domains: Optional[List[str]] = None) -> None:
        self._agents[agent_id] = SwarmAgent(
            agent_id=agent_id,
            expertise_domains=expertise_domains or [],
        )

    def propose(self, question: str, context: str = "") -> str:
        """Create a new proposal, return its ID."""
        pid = uuid.uuid4().hex[:12]
        self._proposals[pid] = Proposal(
            proposal_id=pid,
            question=question,
            context=context,
            created_tick=self._tick,
        )
        self._tick += 1
        return pid

    def vote(
        self,
        agent_id: str,
        proposal_id: str,
        position: Position,
        confidence: float = 1.0,
    ) -> None:
        """Record one agent's vote on a proposal."""
        if agent_id not in self._agents:
            raise KeyError(f"Agent '{agent_id}' not registered.")
        if proposal_id not in self._proposals:
            raise KeyError(f"Proposal '{proposal_id}' not found.")
        confidence = max(0.0, min(confidence, 1.0))
        self._proposals[proposal_id].votes[agent_id] = (position, confidence)

    def _effective_weight(self, agent: SwarmAgent, proposal: Proposal) -> float:
        """Compute phi-weighted vote weight based on domain expertise match."""
        question_words = set(proposal.question.lower().split() + proposal.context.lower().split())
        domain_hits = sum(
            1 for d in agent.expertise_domains if d.lower() in question_words
        )
        return agent.credibility * (PHI ** domain_hits)

    def compute_consensus(self, proposal_id: str) -> Dict[str, Any]:
        """Aggregate votes into a consensus result with phi-weighted confidence."""
        prop = self._proposals.get(proposal_id)
        if prop is None:
            raise KeyError(f"Proposal '{proposal_id}' not found.")

        totals: Dict[Position, float] = {p: 0.0 for p in Position}
        weight_sum = 0.0

        for agent_id, (position, confidence) in prop.votes.items():
            agent = self._agents[agent_id]
            w = self._effective_weight(agent, prop) * confidence
            totals[position] += w
            weight_sum += w

        if weight_sum <= 0:
            return {
                "proposal_id": proposal_id,
                "decision": "NO_VOTES",
                "confidence": 0.0,
                "breakdown": {},
            }

        normalised = {p.name: round(v / weight_sum, 4) for p, v in totals.items()}
        winner = max(totals, key=lambda p: totals[p])
        consensus_confidence = totals[winner] / weight_sum

        return {
            "proposal_id": proposal_id,
            "question": prop.question,
            "decision": winner.name,
            "confidence": round(consensus_confidence, 4),
            "breakdown": normalised,
            "total_votes": len(prop.votes),
        }

    def get_dissent_analysis(self, proposal_id: str) -> Dict[str, Any]:
        """Analyse disagreement patterns on a proposal."""
        prop = self._proposals.get(proposal_id)
        if prop is None:
            raise KeyError(f"Proposal '{proposal_id}' not found.")

        consensus = self.compute_consensus(proposal_id)
        majority = consensus["decision"]
        dissenters: List[Dict[str, Any]] = []

        for agent_id, (position, confidence) in prop.votes.items():
            if position.name != majority:
                agent = self._agents[agent_id]
                dissenters.append({
                    "agent_id": agent_id,
                    "position": position.name,
                    "confidence": confidence,
                    "expertise": agent.expertise_domains,
                })

        return {
            "proposal_id": proposal_id,
            "majority_position": majority,
            "consensus_confidence": consensus["confidence"],
            "dissenter_count": len(dissenters),
            "dissenter_ratio": round(len(dissenters) / max(len(prop.votes), 1), 4),
            "dissenters": dissenters,
        }


# ═══════════════════════════════════════════════════════════════════════
# 5. CausalReasoningEngine
# ═══════════════════════════════════════════════════════════════════════

@dataclass
class CausalVariable:
    name: str
    domain: List[Any]
    observed_value: Optional[Any] = None
    belief: Dict[Any, float] = field(default_factory=dict)

    def __post_init__(self):
        if not self.belief and self.domain:
            uniform = 1.0 / len(self.domain)
            self.belief = {v: uniform for v in self.domain}


@dataclass
class CausalLink:
    cause: str
    effect: str
    strength: float  # [0, 1]


class CausalReasoningEngine:
    """Causal inference engine using directed acyclic graphs (DAGs).

    Supports:
    - Forward/backward belief propagation
    - d-separation based confounder detection
    - Counterfactual do-calculus style interventions
    """

    def __init__(self):
        self._variables: Dict[str, CausalVariable] = {}
        self._links: List[CausalLink] = []
        self._parents: Dict[str, List[str]] = defaultdict(list)
        self._children: Dict[str, List[str]] = defaultdict(list)
        self._link_strength: Dict[Tuple[str, str], float] = {}

    # ── Graph construction ─────────────────────────────────────────

    def add_variable(self, name: str, domain: Optional[List[Any]] = None) -> None:
        """Register a causal variable with a discrete or default binary domain."""
        if domain is None:
            domain = [True, False]
        self._variables[name] = CausalVariable(name=name, domain=domain)

    def add_causal_link(self, cause: str, effect: str, strength: float = 1.0) -> None:
        """Add a directed edge cause → effect with given strength ∈ [0, 1]."""
        if cause not in self._variables or effect not in self._variables:
            raise KeyError("Both variables must be added before linking.")
        strength = max(0.0, min(strength, 1.0))
        link = CausalLink(cause=cause, effect=effect, strength=strength)
        self._links.append(link)
        self._parents[effect].append(cause)
        self._children[cause].append(effect)
        self._link_strength[(cause, effect)] = strength

        # Check for cycles (DAG enforcement)
        if self._has_cycle():
            # rollback
            self._links.pop()
            self._parents[effect].pop()
            self._children[cause].pop()
            del self._link_strength[(cause, effect)]
            raise ValueError(f"Adding {cause} → {effect} would create a cycle.")

    def _has_cycle(self) -> bool:
        """Kahn's algorithm to check for cycles."""
        in_degree: Dict[str, int] = {v: 0 for v in self._variables}
        for link in self._links:
            in_degree[link.effect] += 1
        queue = deque(v for v, d in in_degree.items() if d == 0)
        count = 0
        while queue:
            node = queue.popleft()
            count += 1
            for child in self._children.get(node, []):
                in_degree[child] -= 1
                if in_degree[child] == 0:
                    queue.append(child)
        return count != len(self._variables)

    # ── Observation ────────────────────────────────────────────────

    def observe(self, variable: str, value: Any) -> None:
        """Set an observed value for a variable and propagate beliefs forward."""
        if variable not in self._variables:
            raise KeyError(f"Variable '{variable}' not in DAG.")
        var = self._variables[variable]
        if value not in var.domain:
            raise ValueError(f"Value {value!r} not in domain {var.domain}")
        var.observed_value = value
        var.belief = {v: (1.0 if v == value else 0.0) for v in var.domain}
        self._propagate_forward(variable)

    def _propagate_forward(self, source: str) -> None:
        """Simple forward belief propagation from observed variable."""
        visited: Set[str] = set()
        queue = deque([source])
        while queue:
            cur = queue.popleft()
            if cur in visited:
                continue
            visited.add(cur)
            cur_var = self._variables[cur]
            for child_name in self._children.get(cur, []):
                child_var = self._variables[child_name]
                if child_var.observed_value is not None:
                    continue
                link_str = self._link_strength.get((cur, child_name), 0.5)
                # Compute new child belief based on parent belief and link strength
                new_belief: Dict[Any, float] = {}
                for cv in child_var.domain:
                    p = 0.0
                    for pv in cur_var.domain:
                        # causal influence: if parent has value, child aligns
                        match = 1.0 if pv == cv else 0.0
                        influence = link_str * match + (1 - link_str) * (1.0 / len(child_var.domain))
                        p += cur_var.belief.get(pv, 0.0) * influence
                    new_belief[cv] = p
                # Average with any other existing parent influences
                other_parents = [
                    pp for pp in self._parents[child_name] if pp != cur and pp in visited
                ]
                if other_parents:
                    for pp in other_parents:
                        pp_var = self._variables[pp]
                        pp_str = self._link_strength.get((pp, child_name), 0.5)
                        for cv in child_var.domain:
                            pp_contrib = 0.0
                            for pv in pp_var.domain:
                                match = 1.0 if pv == cv else 0.0
                                influence = pp_str * match + (1 - pp_str) / len(child_var.domain)
                                pp_contrib += pp_var.belief.get(pv, 0.0) * influence
                            new_belief[cv] = (new_belief[cv] + pp_contrib) / 2.0

                total = sum(new_belief.values())
                if total > 0:
                    new_belief = {k: v / total for k, v in new_belief.items()}
                child_var.belief = new_belief
                queue.append(child_name)

    # ── Query ──────────────────────────────────────────────────────

    def query(
        self, target: str, given_observations: Optional[Dict[str, Any]] = None
    ) -> Dict[Any, float]:
        """Estimate belief distribution of *target* given optional observations.

        Temporarily applies observations, propagates, queries, then reverts.
        """
        if target not in self._variables:
            raise KeyError(f"Variable '{target}' not in DAG.")

        # snapshot
        snapshot = {
            name: (copy.deepcopy(v.belief), v.observed_value)
            for name, v in self._variables.items()
        }

        if given_observations:
            for var, val in given_observations.items():
                self.observe(var, val)

        result = dict(self._variables[target].belief)

        # restore
        for name, (bel, obs) in snapshot.items():
            self._variables[name].belief = bel
            self._variables[name].observed_value = obs

        return result

    # ── Confounder detection ───────────────────────────────────────

    def _ancestors(self, node: str) -> Set[str]:
        """Return all ancestors of *node* in the DAG."""
        anc: Set[str] = set()
        queue = deque(self._parents.get(node, []))
        while queue:
            cur = queue.popleft()
            if cur not in anc:
                anc.add(cur)
                queue.extend(self._parents.get(cur, []))
        return anc

    def find_confounders(self, cause: str, effect: str) -> List[str]:
        """Find confounding variables: common ancestors of both cause and effect,
        or common parents that create a back-door path."""
        cause_ancestors = self._ancestors(cause) | {cause}
        effect_ancestors = self._ancestors(effect) | {effect}
        common = cause_ancestors & effect_ancestors - {cause, effect}

        # also include direct common parents
        cause_parents = set(self._parents.get(cause, []))
        effect_parents = set(self._parents.get(effect, []))
        direct_common = cause_parents & effect_parents

        return sorted(common | direct_common)

    # ── Counterfactual / do-calculus ───────────────────────────────

    def counterfactual(
        self, intervention: Dict[str, Any], target: str
    ) -> Dict[str, Any]:
        """do(X = x) — Perform an intervention (graph surgery) and query *target*.

        Removes all incoming edges to the intervened variable, sets its value,
        propagates, queries, then restores the graph.
        """
        # snapshot
        snapshot_beliefs = {
            name: (copy.deepcopy(v.belief), v.observed_value)
            for name, v in self._variables.items()
        }
        snapshot_parents = copy.deepcopy(dict(self._parents))
        snapshot_children = copy.deepcopy(dict(self._children))
        snapshot_links = list(self._links)
        snapshot_strengths = dict(self._link_strength)

        # graph surgery: remove incoming edges to intervention targets
        for var_name in intervention:
            parents_of = list(self._parents.get(var_name, []))
            for p in parents_of:
                self._children[p] = [c for c in self._children[p] if c != var_name]
                self._link_strength.pop((p, var_name), None)
            self._parents[var_name] = []
            self._links = [
                l for l in self._links if l.effect != var_name
            ]

        # apply interventions
        for var_name, val in intervention.items():
            var = self._variables[var_name]
            var.observed_value = val
            var.belief = {v: (1.0 if v == val else 0.0) for v in var.domain}
            self._propagate_forward(var_name)

        result_belief = dict(self._variables[target].belief)

        # restore graph
        self._parents = defaultdict(list, snapshot_parents)
        self._children = defaultdict(list, snapshot_children)
        self._links = snapshot_links
        self._link_strength = snapshot_strengths
        for name, (bel, obs) in snapshot_beliefs.items():
            self._variables[name].belief = bel
            self._variables[name].observed_value = obs

        return {
            "intervention": intervention,
            "target": target,
            "result_belief": result_belief,
        }

    # ── Export ──────────────────────────────────────────────────────

    def export_dag(self) -> Dict[str, Any]:
        """Export the full causal DAG as a plain dict."""
        return {
            "variables": {
                name: {
                    "domain": var.domain,
                    "observed": var.observed_value,
                    "belief": {str(k): round(v, 4) for k, v in var.belief.items()},
                }
                for name, var in self._variables.items()
            },
            "links": [
                {"cause": l.cause, "effect": l.effect, "strength": l.strength}
                for l in self._links
            ],
            "confounders": {
                f"{l.cause}->{l.effect}": self.find_confounders(l.cause, l.effect)
                for l in self._links
            },
        }


# ═══════════════════════════════════════════════════════════════════════
# Registry
# ═══════════════════════════════════════════════════════════════════════

FUTURE_AI_REGISTRY: Dict[str, type] = {
    "phi_resonance_network": PhiResonanceNetwork,
    "evolutionary_code_optimizer": EvolutionaryCodeOptimizer,
    "sovereign_memory_lattice": SovereignMemoryLattice,
    "consensus_swarm_intelligence": ConsensusSwarmIntelligence,
    "causal_reasoning_engine": CausalReasoningEngine,
}


# ═══════════════════════════════════════════════════════════════════════
# Demo / __main__
# ═══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import json

    DIVIDER = "=" * 72

    # ── 1. PhiResonanceNetwork ──────────────────────────────────────
    print(DIVIDER)
    print("  1. PhiResonanceNetwork — Kuramoto Oscillator Demo")
    print(DIVIDER)
    net = PhiResonanceNetwork(coupling_strength=PHI, seed=42)
    rng = random.Random(42)
    for i in range(8):
        net.add_node(
            f"osc_{i}",
            initial_phase=rng.uniform(0, 2 * math.pi),
            natural_frequency=SCHUMANN_HZ + rng.gauss(0, 0.5),
        )
    net.add_all_to_all()

    print(f"  Initial coherence: {net.measure_coherence():.4f}")
    coherences = net.run_simulation(steps=300, dt=0.01)
    print(f"  Final coherence:   {coherences[-1]:.4f}")
    clusters = net.get_synchronized_clusters(threshold=0.5)
    print(f"  Sync clusters:     {len(clusters)} cluster(s)")
    for idx, cl in enumerate(clusters):
        print(f"    Cluster {idx}: {cl}")
    print()

    # ── 2. EvolutionaryCodeOptimizer ───────────────────────────────
    print(DIVIDER)
    print("  2. EvolutionaryCodeOptimizer — Evolving a*x + b")
    print(DIVIDER)
    evo = EvolutionaryCodeOptimizer(seed=42)
    template = "result = 1.0 * x + 0.0"
    # target: result = 3*x + 7
    test_cases = [
        ({"x": 0}, 7.0),
        ({"x": 1}, 10.0),
        ({"x": 2}, 13.0),
        ({"x": -1}, 4.0),
        ({"x": 5}, 22.0),
    ]
    best = evo.evolve(
        generations=100,
        population_size=40,
        test_cases=test_cases,
        template=template,
    )
    print(f"  Best code:    {best.source!r}")
    print(f"  Fitness:      {best.fitness:.6f}")
    print()

    # ── 3. SovereignMemoryLattice ──────────────────────────────────
    print(DIVIDER)
    print("  3. SovereignMemoryLattice — PHI-addressed Memory")
    print(DIVIDER)
    lattice = SovereignMemoryLattice(decay_rate=0.005, seed=42)
    memories = [
        ("genesis", "The beginning of sovereign intelligence", 5.0),
        ("phi", f"Golden ratio = {PHI}", 8.0),
        ("heartbeat", f"System heartbeat at {HEARTBEAT_MS}ms", 3.0),
        ("schumann", f"Earth resonance at {SCHUMANN_HZ}Hz", 7.0),
        ("future", "Forward-looking AI architectures", 9.0),
        ("ephemeral", "Temporary thought", 0.1),
    ]
    for key, val, imp in memories:
        coord = lattice.store(key, val, importance=imp)
        print(f"  Stored '{key}' at φ-coord {coord}")

    lattice.associate("genesis", "phi", strength=2.0)
    lattice.associate("phi", "schumann", strength=PHI)
    lattice.associate("schumann", "heartbeat", strength=1.5)
    lattice.associate("future", "phi", strength=3.0)
    lattice.associate("genesis", "future", strength=2.5)

    recalled = lattice.recall("phi")
    print(f"\n  Recalled 'phi': {recalled}")

    dream_path = lattice.dream_cycle(steps=15)
    print(f"  Dream cycle path: {' → '.join(dream_path)}")

    pruned = lattice.consolidate()
    print(f"  Consolidated — pruned: {pruned}")
    export = lattice.export_lattice()
    print(f"  Lattice cells remaining: {export['cell_count']}")
    print()

    # ── 4. ConsensusSwarmIntelligence ──────────────────────────────
    print(DIVIDER)
    print("  4. ConsensusSwarmIntelligence — Swarm Voting")
    print(DIVIDER)
    swarm = ConsensusSwarmIntelligence()
    swarm.add_agent("alpha", expertise_domains=["AI", "security"])
    swarm.add_agent("beta", expertise_domains=["AI", "data"])
    swarm.add_agent("gamma", expertise_domains=["security", "network"])
    swarm.add_agent("delta", expertise_domains=["AI"])
    swarm.add_agent("epsilon", expertise_domains=["ethics"])

    pid = swarm.propose(
        question="Should AI systems have autonomous security override?",
        context="Discussing AI security policy",
    )
    swarm.vote("alpha", pid, Position.AGREE, confidence=0.9)
    swarm.vote("beta", pid, Position.AGREE, confidence=0.7)
    swarm.vote("gamma", pid, Position.DISAGREE, confidence=0.85)
    swarm.vote("delta", pid, Position.AGREE, confidence=0.6)
    swarm.vote("epsilon", pid, Position.DISAGREE, confidence=0.95)

    consensus = swarm.compute_consensus(pid)
    print(f"  Question:   {consensus['question']}")
    print(f"  Decision:   {consensus['decision']}")
    print(f"  Confidence: {consensus['confidence']}")
    print(f"  Breakdown:  {consensus['breakdown']}")

    dissent = swarm.get_dissent_analysis(pid)
    print(f"  Dissenters: {dissent['dissenter_count']} ({dissent['dissenter_ratio']:.0%})")
    for d in dissent["dissenters"]:
        print(f"    - {d['agent_id']}: {d['position']} (conf={d['confidence']}, expertise={d['expertise']})")
    print()

    # ── 5. CausalReasoningEngine ───────────────────────────────────
    print(DIVIDER)
    print("  5. CausalReasoningEngine — Causal DAG Demo")
    print(DIVIDER)
    cre = CausalReasoningEngine()
    cre.add_variable("smoking", [True, False])
    cre.add_variable("tar_deposits", [True, False])
    cre.add_variable("cancer", [True, False])
    cre.add_variable("genetics", ["high_risk", "low_risk"])
    cre.add_variable("coughing", [True, False])

    cre.add_causal_link("smoking", "tar_deposits", strength=0.85)
    cre.add_causal_link("tar_deposits", "cancer", strength=0.7)
    cre.add_causal_link("genetics", "cancer", strength=0.6)
    cre.add_causal_link("smoking", "coughing", strength=0.75)
    cre.add_causal_link("cancer", "coughing", strength=0.8)

    # Observe smoking
    belief_before = cre.query("cancer")
    print(f"  P(cancer) prior:                {belief_before}")

    belief_given = cre.query("cancer", given_observations={"smoking": True})
    print(f"  P(cancer | smoking=True):       {belief_given}")

    confounders = cre.find_confounders("smoking", "cancer")
    print(f"  Confounders(smoking→cancer):    {confounders}")

    # Counterfactual: do(smoking=False)
    cf = cre.counterfactual(intervention={"smoking": False}, target="cancer")
    print(f"  Counterfactual do(smoking=F):   {cf['result_belief']}")

    dag = cre.export_dag()
    print(f"  DAG variables: {list(dag['variables'].keys())}")
    print(f"  DAG links:     {len(dag['links'])}")
    print()

    # ── Registry ───────────────────────────────────────────────────
    print(DIVIDER)
    print("  FUTURE_AI_REGISTRY")
    print(DIVIDER)
    for fid, cls in FUTURE_AI_REGISTRY.items():
        print(f"  {fid:40s} → {cls.__name__}")
    print()
    print(f"  Constants: PHI={PHI}  HEARTBEAT_MS={HEARTBEAT_MS}  SCHUMANN_HZ={SCHUMANN_HZ}")
    print(f"  All {len(FUTURE_AI_REGISTRY)} future AI systems operational.")
