# CAPSULA ICP Security Posture

## Current Controls

- Anonymous update calls are rejected in backend guards.
- Owner-only status promotion prevents arbitrary activation.
- Incidents are preserved as first-class governance events.
- Mainnet deployment requires an explicit reason through `scripts/mainnet-gate.mjs`.
- Predeploy fingerprints are generated before release.

## Required Before Production

- Generate frontend bindings from Candid instead of using demo data.
- Replace demo identity button with Internet Identity through `@icp-sdk/auth`.
- Add tests for anonymous caller rejection and owner-only status updates.
- Add cycle monitoring and alarm thresholds.
- Add a backup controller controlled outside the primary operator identity.
- Add deployment output registration into Nexus after `icp deploy -e ic`.

## Threat Model

The first threat is not only code exploitation. It is lineage corruption:
unfingerprinted artifacts, wrong source packages, stale generated bindings, or
deployment without registry writeback. The deployment pipeline therefore treats
integrity drift as a security failure.
