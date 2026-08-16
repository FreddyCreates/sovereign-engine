# CAPSULA ICP Platform

## Status
Full ICP-native repo skeleton

## Purpose
CAPSULA ICP Platform turns memory-book capsules into Internet Computer canister applications. It combines:

- Motoko backend canister for capsule registry and governance state
- asset canister frontend dashboard
- NERVUS chain records and Nexus registry metadata
- capsule manifest validation
- local and mainnet deployment pipeline

## Build Law
Before modifying this repo, fetch relevant ICP skills:

- `icp-cli`
- `motoko`
- `mops-cli`
- `asset-canister`
- `internet-identity`
- `canister-security`
- `stable-memory`
- `multi-canister` when splitting canisters

## Quickstart

```bash
npm install -g @icp-sdk/icp-cli @icp-sdk/ic-wasm ic-mops
npm install
mops install
icp network start -d
icp deploy
```

Open the frontend URL from:

```bash
icp network status --json
```

## Repo Layout

```text
icp.yaml
mops.toml
src/backend/
src/frontend/
schemas/
scripts/
docs/
.github/workflows/
```

## Mainnet Gate
Never deploy to mainnet until:

1. named identity is active
2. cycles balance is verified
3. `.icp/data/` is committed
4. `NERVUS` pre-deploy chain is emitted
5. `Nexus` deployment record is written
6. controller backup is decided

## Native Thesis
This repo is the first bridge from CAPSULA memory books to native ICP canister infrastructure.
