# CAPSULA ICP Platform Architecture

## Layers

1. CAPSULA package layer
2. Motoko backend registry canister
3. asset canister dashboard
4. NERVUS deployment chain
5. Nexus deployment registry
6. mainnet deployment gate

## Canisters

### backend
Stores capsule records, incidents, chain IDs, and governance status.

### frontend
Hosts dashboard assets and future Internet Identity flow.

## Future Canisters

- `registry_service`: shared Nexus registry
- `proof_service`: chain/hash proof surface
- `governance_service`: protocol adjudication

## Design Decision
Start single-backend plus asset canister. Split only when storage, governance, or upgrade boundaries justify multi-canister complexity.
