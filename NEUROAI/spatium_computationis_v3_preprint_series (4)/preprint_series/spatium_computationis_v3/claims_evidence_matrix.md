# Claims and Evidence Matrix

Authority state: `CLAIM_HARDENED_DRAFT`

Overall proof posture: `partial_repo_verified`

Reason: The uploaded packet contains mathematical exposition and architecture description, and the public repository was inspected at commit `a756fa39e39342dc2443c6c7d9335f4c9d68455c`. The repository verifies the operational app, defense/platform architecture, tick-based 3D simulation, and deployment scaffolding. Advanced physics, Riemannian geometry, mini-verse cosmology, and numerical validation claims remain evidence-gated because matching implementation files were not located in the inspected surface.

## Claim Review Table

| ID | Paper | Claim summary | Claim class | Current posture | Risk | Needed support | Recommended wording |
| --- | --- | --- | --- | --- | --- | --- | --- |
| C-001 | Series | Spatium Computationis models autonomous agents as physical entities in simulated spacetime. | `C4`, potential `C1` for current 3D simulation substrate | Repo-backed for tick-based 3D entity simulation; advanced spacetime claims remain design/theory. | Medium | Cite `simulation/world.py`, `simulation/engine.py`, `simulation/routes.py`; add formal model for stronger claims. | "Spatium Computationis implements a tick-based 3D simulation substrate for agents, signals, threats, zones, and data packets; broader spacetime claims remain part of the research framing." |
| C-002 | Paper 1 | The physics engine implements Velocity Verlet integration. | Potential `C1` | Not located in inspected repo surface. | High | Specific physics-engine file, tests, and run logs. | "The canonical paper proposes a Velocity Verlet physics layer; the inspected repo currently verifies a tick-based 3D simulation layer." |
| C-003 | Paper 1 | Verlet integration yields bounded energy error for Hamiltonian systems. | `C10`, `C9` | Externally supportable with citations. | Low | Cite Verlet and geometric numerical integration sources. | "Under standard assumptions, symplectic methods such as Velocity Verlet are used for bounded long-term energy behavior." |
| C-004 | Paper 1 | The system enforces a hard speed bound at `c`. | `C3`, potential `C1` | Not located in inspected repo surface. | High | Relativistic update tests and edge-case traces. | "The research design includes a relativistic correction intended to bound simulated propagation speed." |
| C-005 | Paper 1 | Conservation error remains below `10^-6` for typical time steps. | Potential `C1` | Not located in inspected repo surface. | High | Run logs, plots, parameter definitions. | "Validation should report conservation error under specified time-step and parameter regimes." |
| C-006 | Paper 2 | Geometry quantities are computed numerically from metric functions. | Potential `C1`, `C9` | Not located in inspected repo surface. | High | Code and benchmark metrics. | "The geometry design uses metric functions as the interface for numerical differential geometry." |
| C-007 | Paper 2 | The engine works for any smooth metric. | `C9` | Overbroad without numerical constraints. | High | Stability domain, convergence tests, singularity handling. | "The approach targets smooth metric functions within defined numerical stability limits." |
| C-008 | Paper 2 | Horizon detection can be performed by scanning sign changes in `g_tt`. | `C10`, potential `C1` | Conceptually supported but coordinate-sensitive. | Medium | Benchmark metrics and caveat discussion. | "For suitable coordinates, horizon candidates may be detected by monitoring metric component behavior such as sign changes in `g_tt`." |
| C-009 | Paper 3 | Mini-verses can use configurable constants and topologies. | `C8`, potential `C1` | Not located in inspected repo surface. | High | Schema, examples, tests. | "The research architecture defines mini-verse instances with configurable constants and topology choices." |
| C-010 | Paper 3 | Entropy tracking provides a thermodynamic arrow of time. | `C3`, `C9` | Needs formalization. | Medium | Entropy model and numeric examples. | "Entropy accounting is proposed as an indicator of thermodynamic directionality." |
| C-011 | Paper 3 | Inter-verse channels enforce causality through bandwidth limits. | `C8`, `C3` | Not located in inspected repo surface. | High | Transfer model, tests, causal proof sketch. | "The architecture specifies bandwidth-limited inter-verse channels intended to constrain transfer." |
| C-012 | Paper 4 | Agents interact through physical forces where attraction models influence and electromagnetic forces model communication. | `C4`, `C9` | Metaphorical/protocol claim. | Medium | Formal mapping from physical variables to operational semantics. | "The architecture uses physical analogies to represent influence and communication relationships." |
| C-013 | Paper 4 | The battleground architecture contains cooperative, hostile, and shadow routing tiers. | `C5`, `C8`, partial `C1` for documented routes | Repo-backed architecture and route surfaces; release-gated for sensitive details. | Medium | Cite `README.md`, `main.py`, `defense/honeypot/routes.py`, `platform_router.py`. | "A tiered battleground architecture is documented and partially implemented through defense, honeypot, platform, and simulation routes." |
| C-014 | Series | The system is production-grade. | Potential `C1` | Deployment scaffolding is repo-backed; production operation still needs live deployment/CI run evidence. | Medium | Workflow run status, release artifact, deployment URL, operational logs. | "The repository contains production-oriented deployment scaffolding, including Docker, compose, and CI build/test workflow; live production status requires runtime evidence." |

## Citation and Evidence Gaps

Missing external citations:

- Symplectic integration and long-term energy behavior.
- Numerical differential geometry and finite-difference curvature computation.
- General relativity references for benchmark metrics and invariants.
- Cosmological evolution and entropy references.
- Agent-based modeling, cyber range, sandbox, and immune-system-inspired defense literature.

Repository evidence status:

- Repository identified by operator: `https://github.com/FreddyCreates/pegasus-battleops`.
- Runtime access status: GitHub connector succeeded; shell clone remained blocked by the container network.
- Commit inspected: `a756fa39e39342dc2443c6c7d9335f4c9d68455c`.
- Promotion rule: implementation claims may be upgraded only when tied to specific files, commits, tests, and logs.

Missing internal evidence still needing inspection:

- File-level implementation evidence for advanced physics, geometry, and mini-verse claims.
- Test suite contents and actual output logs.
- Benchmark results.
- Diagrams or screenshots of the runtime/visualization if visual claims are retained.

Missing experiments or validations:

- Energy/momentum/angular momentum conservation traces.
- Geodesic norm preservation and analytic comparison tests.
- Horizon detection benchmark.
- Mini-verse topology behavior examples.
- Agent routing and containment simulation traces.

Claims to remove or downgrade before public release:

- "production-grade" should be narrowed to "production-oriented deployment scaffolding" unless live deployment, passing CI run, or operational evidence is attached.
- "all implementations use real SI units" unless unit tests or code evidence are attached.
- "validated conservation laws" unless actual validation output is included.
- "proper differential geometric constructions" should be reframed as "standard mathematical constructions are specified" unless implementation tests are attached.

## Next Proof Move

Use the repo-backed architecture and simulation evidence to strengthen Paper 4 immediately, and either locate the missing advanced engine files or reframe Papers 1-3 as staged theory/design papers aligned with the current tick-based 3D simulation substrate.
