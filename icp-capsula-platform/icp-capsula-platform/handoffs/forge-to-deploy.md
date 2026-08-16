# Forge to Deploy Handoff

## Built Artifacts

- `src/backend/main.mo`
- `src/backend/types.mo`
- `src/backend/lib/Capsule.mo`
- `src/backend/lib/Guard.mo`
- `src/backend/capsula.did`
- `src/frontend/src/main.ts`
- `schemas/capsule.schema.json`
- `scripts/nervus-predeploy.mjs`
- `scripts/mainnet-gate.mjs`

## Required Deploy Checks

1. `node scripts/nervus-predeploy.mjs`
2. `node scripts/validate-capsule.mjs`
3. `mops check`
4. `mops build`
5. `icp network start -d`
6. `icp deploy`

Mainnet requires:

```bash
node scripts/mainnet-gate.mjs --env ic --reason "specific promotion reason"
icp deploy -e ic
```

## Promotion Decision

- `branch`: code exists but has not completed local deployment.
- `trunkCandidate`: local checks pass and Nexus registration plan exists.
- `active`: deployed and registered.
- `quarantined`: failed validation or deployment gate.
