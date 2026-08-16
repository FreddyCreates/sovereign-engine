# THESIS Hub Dashboard Blueprint

## First Screen

The first screen should be the active research workspace, not a marketing page.

Core panels:

- Active packets
- Claims by proof state
- Repositories inspected
- Missing evidence queue
- Print/export queue
- Hash manifest status

## Data Widgets

| Widget | Source |
| --- | --- |
| Claim state count | `claims/*.json` |
| Evidence gap queue | `proof_gaps/*.json` |
| Repo inspection ledger | `repositories/*.json` |
| Print outputs | `outputs/` |
| Hash manifests | `hashes/` |

## Main Actions

- New packet
- Audit repo
- Import paper
- Build claims matrix
- Print PDF
- Create hash manifest
- Create verifier report

## Visual Rule

Quiet, dense, and review-focused. This is a research cockpit, not a decorative landing page.
