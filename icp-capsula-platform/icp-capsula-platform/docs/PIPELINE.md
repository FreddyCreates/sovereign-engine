# CAPSULA ICP Deployment Pipeline

This repo is organized around a source -> forge -> deploy -> nexus flow.

## Pipeline Stages

### 1. Skill Refresh

Fetch current ICP build skills before changing deployment code:

```bash
curl -L https://skills.internetcomputer.org/llms.txt
```

Required skills for this repo:

- `icp-cli`
- `motoko`
- `mops-cli`
- `asset-canister`
- `internet-identity`
- `canister-security`
- `multi-canister`
- `stable-memory`

### 2. Local Verification

```bash
node --check scripts/nervus-predeploy.mjs
node --check scripts/mainnet-gate.mjs
node scripts/nervus-predeploy.mjs
node scripts/mainnet-gate.mjs --env local --reason "local smoke test"
```

When ICP tools are installed:

```bash
mops check
mops build
icp network start -d
icp deploy
```

### 3. Promotion Gate

Mainnet promotion must include a reason and must not bypass fingerprinting:

```bash
node scripts/mainnet-gate.mjs --env ic --reason "capsule release candidate"
icp deploy -e ic
```

### 4. Nexus Registration

After deployment, write back:

- canister ids,
- deployment environment,
- chain id,
- predeploy digest,
- commit or package hash,
- operator identity,
- incident notes if any.

## Failure Policy

If any gate fails, keep the capsule in `branch` or `quarantined` status. Do not
mark it `active` until the local deployment and Nexus registration both pass.
