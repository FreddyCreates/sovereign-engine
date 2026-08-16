# Source to Forge Handoff

## Inputs

- Fetched ICP skill rules from `https://skills.internetcomputer.org/llms.txt`.
- Existing memory-book packages and NERVUS chain doctrine.
- CAPSULA runtime seed and ICP native skill vault artifacts.

## Source Rules

- Use `icp`, not `dfx`, for deployment commands.
- Use Motoko persistent actors and `mo:core`.
- Keep `.icp/data/` commit-safe and `.icp/cache/` ignored.
- Reject anonymous update callers in backend logic.
- Treat hashes, chain ids, and capsule manifests as first-class source objects.

## Forge Contract

Forge must produce:

- Motoko backend canister code,
- asset-canister frontend,
- schema for capsule manifests,
- NERVUS predeploy fingerprint output,
- route object and deployment docs.

Forge may not promote artifacts to mainnet without Deploy Surface gate checks.
