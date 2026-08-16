# THESIS Hub

Release state: `workspace_blueprint`

## Purpose

THESIS Hub is the workspace face of THESIS.

It gives researchers and reviewers one place to see:

- papers
- repositories
- claims
- evidence
- proof gaps
- PDFs
- hash manifests
- review state
- release boundaries

## Core Views

| View | Purpose |
| --- | --- |
| Workspace Dashboard | Current packets, risk, proof state, print state |
| Repository Ledger | Repos scanned, commits inspected, evidence found |
| Claims Board | Claims by class, proof posture, release boundary |
| Evidence Matrix | Claim-to-file/log/test/citation mapping |
| Paper Builder | Paper outline, abstract, sections, export state |
| Print Room | PDF, DOCX, packet, archive, manifest outputs |
| Verifier Reports | Third-party diligence reports and scoring |

## Hub Object Model

See `workspace_schema.json`.

## MVP

- Static dashboard generated from JSON packet files.
- Markdown and JSON packet storage.
- Export queue for PDF/DOCX.
- Hash manifest view.
- Manual review states.

## Long-Term

- Multi-user research teams.
- GitHub/GitLab/local repo connectors.
- Zenodo archive export.
- Reviewer/funder portals.
- Public/private derivative generator.
