# CAPSULA ICP Operating System

CAPSULA ICP is the deployable canister layer for CIVOS memory-book artifacts.
Its job is to turn vault packets, papers, protocols, hashes, and registry objects
into living Internet Computer applications without losing lineage.

## Runtime Layers

1. Source Engine
   - Receives doctrine, repository intelligence, fetched ICP skills, and vault packets.
   - Produces source-qualified capsule inputs with provenance and proof state.

2. Forge Surface
   - Converts source material into Motoko canister records, asset-canister UI, schemas,
     and predeploy manifests.
   - Emits NERVUS fingerprints before deployment.

3. Deploy Surface
   - Runs local network deployment, verifies canister bindings, checks mainnet gates,
     and promotes only hash-verified artifacts.

4. Nexus Registry
   - Registers capsule ids, chain ids, artifact hashes, deployment targets, and incident
     history for future agents and GitHub updates.

## Native Objects

- `Capsule`: a deployable memory-book unit.
- `NERVUS Chain`: a fingerprint chain binding source files to deployment intent.
- `Deployment Gate`: a promotion decision, not just a command.
- `Incident`: a governance event that blocks or annotates promotion.
- `Registry Link`: the cross-system identity binding for future repos, agents, and canisters.

## Continuity Law

No capsule should move to mainnet unless:

- its source files have current sha256 fingerprints,
- its source-to-forge and forge-to-deploy handoff files are present,
- anonymous update calls are rejected,
- the caller identity has been checked at the canister boundary,
- the mainnet gate has a human-readable promotion reason,
- the deployment output is registered back into Nexus.

## Product Shape

The first product is a capsule registry app: a frontend that shows deployable vault
objects and a Motoko backend that preserves their chain identity. Later slices should
add Candid-generated bindings, Internet Identity sessions, canister-to-canister registry
replication, and GitHub issue/PR handoffs.
