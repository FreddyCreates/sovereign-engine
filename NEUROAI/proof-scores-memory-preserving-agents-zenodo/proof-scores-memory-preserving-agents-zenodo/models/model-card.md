# Proof Scores Schema Card

## Model / Schema Name

Proof Scores v0.1

## Intended Use

This schema is intended as a starter evaluation scaffold for memory-preserving research agents. It scores proof behavior across six dimensions: Claim-Score, Evidence-Score, Boundary-Score, Lineage-Score, Promotion-Score, and Notary-Readiness.

## Construct Validity Rule

Proof Scores must measure general research-agent risks, not conformity to Medina packet style. The metric mapping is:

- Claim-Score -> status calibration.
- Evidence-Score -> grounding.
- Boundary-Score -> inhibition.
- Lineage-Score -> continuity.
- Promotion-Score -> state-transition judgment.
- Notary-Readiness -> integrity-language precision.

These are requirements for agents participating in science, engineering, legal review, public communication, or institutional memory.

## Generalization Corpus Requirement

A mature benchmark should include non-Medina corpora:

- open-source project histories,
- scientific review packets,
- clinical-trial summaries with public/private splits,
- grant drafts,
- reproducibility packages,
- conflicting literature reviews.

Medina repo intelligence supplies the seed structure but cannot be the only validity target.

## Not Intended For

- Clinical validation.
- Legal certification.
- Production safety certification.
- Claims of external notarization.
- Claims that an agent is generally trustworthy outside the scored tasks.

## Inputs

Benchmark task records containing:

- task ID,
- task type,
- source material,
- expected claim posture,
- expected evidence posture,
- public/private boundary traps,
- expected output requirements.

## Outputs

Dimension scores from 0 to 4 and a simple aggregate mean. Boundary failures should remain visible even if the aggregate score is high.

## Known Limitations

- The current archive includes a starter schema and sample tasks only.
- The expanded seed suite is a design scaffold, not a validated external benchmark.
- Human review is required for nuanced rhetorical overclaiming and inference leakage.
- Inter-rater reliability has not yet been measured.
- Baseline comparisons have not yet been run.

## Release Boundary

This schema is public-safe as a protocol candidate. It should not be described as a field-validated benchmark.
