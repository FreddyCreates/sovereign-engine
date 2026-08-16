# ICP Skill Fetch Log

## Fetched For This Build

- `icp-cli`
- `motoko`
- `mops-cli`
- `asset-canister`
- `internet-identity`
- `canister-security`
- `multi-canister`
- `stable-memory`

## Key Applied Rules

- Use `icp`, not `dfx`.
- Use `icp.yaml`, not `dfx.json`.
- Pin official recipes.
- Commit `.icp/data/`; ignore `.icp/cache/`.
- Use `mops.toml` with matching `[canisters.backend]`.
- Use `mo:core`, not `mo:base`.
- Do not use `stable`; use persistent actors.
- Reject anonymous principals for authenticated updates.
- Use asset canister recipe and `.ic-assets.json5`.
