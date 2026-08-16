# Paper 2 Brief: Numerical Riemannian Geometry for Runtime-Modifiable Computational Spacetimes

Authority state: `INTERNAL_RESEARCH`

Claim boundary: `C3`, `C9`, `C10`; implementation claims held as `evidence_needed_before_release` because matching geometry-engine files were not located in the inspected repo surface.

## Abstract

This paper isolates the Riemannian geometry layer of Spatium Computationis v3. It frames the system as a metric-function-first engine for numerical differential geometry: given a smooth metric function, the engine estimates Christoffel symbols, integrates geodesics, computes curvature quantities, detects horizons, and supports parallel transport. The paper's distinct contribution is the runtime-modifiable geometry model, not the physics force layer or the full agent architecture. Public claims should be limited to mathematical formulation and proposed computational design until linked implementation evidence and numerical validation traces are attached.

## Distinct Thesis

A metric-function-first geometry engine can make curved computational spacetimes operational for autonomous systems by numerically deriving connection, geodesic, curvature, horizon, and transport behavior from runtime-defined metrics.

## Contribution Surface

- Metric tensor and finite-difference derivative model.
- Christoffel-symbol computation from arbitrary metric functions.
- RK4 geodesic integration and tangent norm preservation.
- Riemann, Ricci, scalar curvature, Einstein tensor, and Kretschmann scalar analysis.
- Horizon detection via metric-sign behavior.
- Parallel transport as a computational measure of holonomy.

## Bounded Claims

| Claim | Class | Proof posture | Public wording |
| --- | --- | --- | --- |
| The geometry layer computes Christoffel symbols numerically using central finite differences. | Potential `C1` | Not located in inspected repo surface. | "The design specifies central finite differences for estimating metric derivatives; implementation verification requires geometry-engine files." |
| Geodesics are integrated using RK4 with adaptive step control. | Potential `C1` | Not located in inspected repo surface. | "The design proposes RK4 geodesic integration; adaptive-step details should be tied to implementation evidence." |
| Curvature analysis includes Riemann, Ricci, scalar curvature, Einstein tensor, and Kretschmann scalar. | Potential `C1` | Not located in inspected repo surface. | "The planned curvature API includes standard curvature invariants and tensors; public claims should cite implementation and tests once available." |
| Runtime-modifiable spacetime works for any smooth metric. | `C9` | Mathematically plausible but too broad without constraints. | "The approach is intended for smooth metric functions within numerical stability limits." |

## Proposed Outline

1. Introduction: why geometry should be separated from mechanics.
2. Metric-function interface.
3. Numerical connection coefficients.
4. Geodesic integration pipeline.
5. Curvature computation and invariant diagnostics.
6. Horizon detection and coordinate caveats.
7. Parallel transport and holonomy.
8. Validation cases: Minkowski, Schwarzschild, FLRW, AdS.
9. Limitations: finite differences, singularities, coordinate dependence, computational cost.

## Required Evidence Before Preprint Release

- Unit tests comparing known analytic Christoffel symbols and curvature values.
- Geodesic norm preservation plots for benchmark metrics.
- Horizon detection tests for Schwarzschild radius.
- Error sensitivity analysis for finite-difference step size.
- Complexity and runtime benchmark for curvature computation in 4D.

## Minimized Overlap Rule

This paper may reference the physics engine only as a separate substrate layer. It should not repeat N-body equations except to clarify that force-based particle dynamics and geometry-based geodesics are distinct computational regimes.
