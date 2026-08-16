# THESIS Verifier Mode

Release state: `research_audit_blueprint`

## Purpose

Verifier Mode is the outside examiner for research.

It is for:

- funders
- accelerators
- labs
- journals
- reviewers
- technical partners
- researchers checking other researchers

## Core Question

How much of this research is real, supported, missing, exaggerated, or unverified?

## Verifier Workflow

1. Intake source material: paper, repo, logs, claims, citations, demos.
2. Extract major claims.
3. Classify each claim.
4. Inspect evidence surfaces.
5. Map claims to files, tests, logs, citations, datasets, or demos.
6. Identify missing proof.
7. Assign risk and confidence.
8. Produce a verifier report.

## Output

- verification summary
- claim review table
- repo evidence map
- missing proof queue
- overclaim warnings
- reviewer questions
- funding/review posture

## Non-Negotiable Rule

Do not use a repository host's own AI summary as final validation of repository evidence. THESIS must inspect files, commits, tests, logs, artifacts, or externally supplied proof substrate directly.
