# THESIS

THESIS is a research proof operating system for the JOURNAL workspace.

It is not only a paper writer. It is a proof, publication, repository, and packet engine.

## Four Lanes

1. `gpt-marketplace/` - GPT Marketplace release material.
2. `julia-terminal/` - local terminal scaffold for repo and paper audits.
3. `hub/` - workspace model for papers, repos, PDFs, packets, and proof ledgers.
4. `verifier/` - claim verification mode for third-party diligence.

## Packet Backbone

Every THESIS packet should carry:

- packet id
- source artifact
- repo or document evidence
- claim classes
- evidence state
- release boundary
- proof gaps
- output artifacts
- hash manifest
- review state

## Claim States

- `verified`: implementation or evidence inspected.
- `supported`: plausible and backed by partial evidence.
- `hypothesis`: research claim needing validation.
- `strategic_thesis`: framing or business/product claim.
- `private_internal`: not public-safe.
- `blocked`: should not be promoted.

## Default Workflow

```text
intake -> classify -> scan evidence -> map claims -> identify gaps -> build packet -> print/export -> hash
```
