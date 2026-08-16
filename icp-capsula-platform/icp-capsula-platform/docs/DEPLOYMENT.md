# Deployment

## Local

```bash
npm install
mops install
icp network start -d
icp deploy
```

## Mainnet

```bash
icp identity default <named-identity>
icp token balance -n ic
icp cycles balance -n ic
npm run nervus:predeploy
npm run deploy:ic
```

## Required Mainnet Records

- NERVUS predeploy chain
- Nexus deployment record
- `.icp/data/mappings/ic.ids.json`
- backup controller decision
- cycles/freezing threshold review
