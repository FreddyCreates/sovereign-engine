# Paper 1 Brief: A Symplectic Physics Substrate for Autonomous Agent Simulation

Authority state: `INTERNAL_RESEARCH`

Claim boundary: `partial_repo_verified`; current repo verifies a tick-based 3D simulation layer, while Velocity Verlet/N-body/relativistic claims remain evidence-gated.

## Abstract

This paper presents the numerical mechanics layer of Spatium Computationis v3, a proposed substrate for modeling autonomous agents as physically situated entities. The paper focuses on Velocity Verlet integration, pairwise gravitational and electromagnetic interactions, relativistic speed bounds, elastic collision handling, and conservation-law diagnostics. Its central claim is not that the system is fully validated in the supplied material, but that a symplectic mechanics layer provides a disciplined foundation for agent simulation when paired with measurable energy, momentum, angular-momentum, and causality checks. The paper defines the substrate, identifies its numerical invariants, and specifies the evidence required for public validation.

## Distinct Thesis

A symplectic physics engine can serve as the first layer of a physically grounded autonomous-agent substrate by making agent interaction, influence, collision, and propagation constraints measurable through numerical conservation diagnostics.

## Contribution Surface

- Velocity Verlet integration as the substrate's default time-stepping method.
- N-body force modeling with gravitational and Coulomb terms.
- Relativistic correction as a speed-bound mechanism.
- Elastic collision resolution for simulated entities.
- Conservation-law telemetry as runtime quality control.

## Bounded Claims

| Claim | Class | Proof posture | Public wording |
| --- | --- | --- | --- |
| Velocity Verlet is appropriate for long-running Hamiltonian-style simulation because its energy error is bounded under standard assumptions. | `C10` / `C9` | Supported by known numerical analysis; needs citation pass. | "Velocity Verlet is a standard symplectic method often used when bounded long-term energy behavior is desirable." |
| The packet's physics engine implements N-body gravitational and electromagnetic interactions. | Potential `C1` | Not located in inspected repo surface. | "The canonical design targets N-body gravitational and electromagnetic interactions; the inspected repo currently verifies a tick-based 3D entity simulation layer." |
| Relativistic corrections prevent simulated particles from exceeding `c`. | `C3` / potential `C1` | Needs implementation and test evidence. | "The design includes a relativistic speed-bound mechanism intended to constrain propagation speed." |
| Conservation diagnostics validate simulation quality. | `C3` / `C4` | Methodologically plausible; thresholds need logs. | "Conservation diagnostics are proposed as quality indicators for simulation runs." |

## Proposed Outline

1. Introduction: physical substrate for agent simulation.
2. Numerical mechanics requirements.
3. Velocity Verlet integration and error behavior.
4. Pairwise interaction model.
5. Relativistic speed-bound policy.
6. Collision model and conservation assumptions.
7. Conservation-law telemetry.
8. Validation plan and expected diagnostics.
9. Limits and relation to later series papers.

## Required Evidence Before Preprint Release

- Code references for integrator, force computation, collision resolution, and telemetry.
- Current repo-backed references: `spatium-computationis/simulation/engine.py`, `spatium-computationis/simulation/world.py`, and `spatium-computationis/simulation/routes.py` for tick-based 3D simulation.
- Energy, momentum, and angular-momentum drift plots across representative runs.
- Parameter table for time step, softening length, masses, charges, and units.
- Comparison against Euler or RK methods if claiming superior long-term behavior.
- Benchmark confirming scaling and practical particle limits.

## Minimized Overlap Rule

This paper may mention agents only as physical entities requiring a numerical substrate. It should not describe the 21-agent architecture, mini-verse topology catalog, or full differential-geometry machinery except as future layers.
