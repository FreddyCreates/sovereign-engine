# Repository Evidence Map

Authority state: `REPO_EVIDENCE_PARTIAL`

Repository: `https://github.com/FreddyCreates/pegasus-battleops`

Commit inspected: `a756fa39e39342dc2443c6c7d9335f4c9d68455c`

Access route: GitHub connector. Local `git clone` remained blocked by the container network, but connector file fetches succeeded.

## Verified Repository Surfaces

| Evidence target | Repository file | Verification state | Notes |
| --- | --- | --- | --- |
| Public repo identity | Repository metadata | `verified` | Repo is public, default branch `main`, size reported as 58490, clone URL available. |
| Top-level system description | `README.md` | `repo_verified_architecture` | Describes Spatium Computationis as AI intelligence battleground, organism defense, autonomous agent ecosystem, with 21 agents and 53 protocols. |
| Furniture/interiors intelligence layer | `spatium-computationis/README.md` | `repo_verified_architecture` | Documents FastAPI app, 5-protocol intelligence pipeline, 7-agent operational layer, API endpoints, and Nova Sovereign runtime configuration. |
| FastAPI application entrypoint | `spatium-computationis/main.py` | `repo_verified_implementation_surface` | Defines FastAPI app version `0.5.0`, mounts static files, includes defense, marketing, platform, simulation, and frontend routers, and exposes `/`, `/ingest`, `/field-update`, `/memory/recall`, direct agent endpoints, and defense webhook/WebSocket endpoints. |
| Pipeline behavior | `spatium-computationis/main.py` | `repo_verified_implementation_surface` | `/ingest` executes `ingressus -> compressio -> ordinatio -> actio`; `/field-update` executes Reductus feedback processing. |
| Deployment scaffold | `Dockerfile` and `docker-compose.yml` | `repo_verified_deployment_scaffold` | Dockerfile builds Python 3.12 app and runs `uvicorn`; compose exposes port `8000`, passes Nova env vars, and defines a healthcheck. |
| CI/deployment workflow | `.github/workflows/deploy-app.yml` | `repo_verified_ci_scaffold` | Workflow installs dependencies, runs `pytest tests/`, runs `tests/test_maesi_smoke.py`, then builds and pushes a Docker image to GHCR. |
| Honeypot defense endpoints | `spatium-computationis/defense/honeypot/routes.py` | `repo_verified_implementation_surface` | Defines fake `.env`, config, admin, WordPress, login, API, and service endpoints; collects fingerprints and records honeypot triggers. |
| Platform agent/task router | `spatium-computationis/platform_router.py` | `repo_verified_implementation_surface` | Exposes platform agent discovery, agent health, task queue, delegation, buses, taxis, and layer endpoints. |
| 3D simulation API | `spatium-computationis/simulation/routes.py` | `repo_verified_implementation_surface` | Exposes `/simulation/state`, `/stats`, `/start`, `/stop`, `/events`, `/zones`, entity lookup, entity injection, and WebSocket streaming. |
| Tick-based simulation engine | `spatium-computationis/simulation/engine.py` | `repo_verified_implementation_surface` | Defines `TICK_RATE = 20`, resident agents, honeypot nodes, defense nodes, procedural spawning of signals/threats/data packets, subscriber broadcasting, injection, state, and stats APIs. |
| 3D world model | `spatium-computationis/simulation/world.py` | `repo_verified_implementation_surface` | Defines `Vector3`, `EntityType`, `EntityState`, `ZoneType`, bounded zones, entities, movement toward targets, state serialization, deltas, and event logs. |
| Agent/glyph mapping | `spatium-computationis/glyphs/glyph_map.py` | `repo_verified_implementation_surface` | Maps operational glyphs to regions and agents, including defense, shadow, gatekeeper, adversary, and research agents. |

## Claims Upgraded By Repo Evidence

- The system has a public repository with a FastAPI application surface.
- The operational architecture includes organism defense, honeypots, platform routing, task queues, agent discovery, and direct agent endpoints.
- The repo contains a tick-based 3D simulation substrate with entities, zones, resident agents, procedural signal/threat/data-packet spawning, and WebSocket streaming.
- Deployment scaffolding exists through Docker, docker-compose, and a GitHub Actions workflow that runs tests and builds/pushes a container image.
- Paper 4 can now be treated as the strongest repo-backed paper in the series.

## Claims Still Evidence-Gated

The following pasted-paper claims were not located in the inspected repository surface and should not be promoted to verified implementation claims yet:

- Velocity Verlet integration.
- N-body gravitational and electromagnetic interactions.
- Relativistic correction with hard speed bound at `c`.
- Conservation-law tracking with numerical error thresholds.
- Riemannian metric engine, Christoffel symbols, geodesic RK4 integration, curvature tensors, Einstein tensor, Kretschmann scalar, horizon detection, and parallel transport.
- Mini-verse constants, topology catalog implementation, Friedmann evolution, entropy accounting, and inter-verse channels.

## Recommended Series Revision

- Keep Paper 4 as repo-backed architecture paper.
- Reframe Paper 1 as the current tick-based 3D simulation substrate unless matching physics-engine files are supplied.
- Reframe Papers 2 and 3 as theory/design roadmap papers unless geometry and mini-verse implementation files are located.
- Add a repo-backed appendix citing the inspected files and commit.
