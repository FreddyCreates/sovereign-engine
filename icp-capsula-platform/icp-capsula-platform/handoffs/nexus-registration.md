# Nexus Registration Handoff

## Registry Object

```yaml
object_name: CAPSULA ICP Platform
object_type: icp_native_platform_repo
parent_system: CIVOS / CAPSULA / NERVUS
status: trunk-candidate
route_id: ROUTE-CAPSULA-ICP-20260616
expected_canisters:
  - backend
  - frontend
required_registration:
  - route object
  - predeploy chain id
  - sha256 file fingerprints
  - canister ids after deployment
  - operator identity
  - deployment environment
  - incident notes
```

## Post-Deploy Writeback

After successful deploy, update the Nexus registry with:

- backend canister id,
- frontend canister id,
- deployment URL,
- environment,
- predeploy chain digest,
- package hash,
- timestamp,
- operator identity.

Until this writeback exists, the repo remains a trunk-candidate rather than an active
deployment.
