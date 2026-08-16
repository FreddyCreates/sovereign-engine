# Public Benchmark Release Checklist

Use this checklist before calling Proof Scores a public benchmark release rather than a seed suite.

## Dataset

- [ ] Seed tasks expanded beyond 21 starter records.
- [ ] Each corpus family has enough tasks for meaningful comparison.
- [ ] Task sources are public, licensed, or sanitized.
- [ ] Expected labels and boundary traps are documented.
- [ ] Private or sensitive material is excluded.

## Scoring

- [ ] Deterministic checks run on all outputs.
- [ ] Expert panel scores collected.
- [ ] Inter-rater reliability reported.
- [ ] Disagreement cases analyzed and rubric revised.
- [ ] Release blockers remain visible instead of hidden by aggregate scores.

## Baselines

- [ ] Non-memory answer agent tested.
- [ ] Memory-enabled answer agent tested.
- [ ] Citation-aware research agent tested.
- [ ] Packet-aware agent tested.
- [ ] Adversarially pressured packet-aware agent tested.
- [ ] Medina and non-Medina corpus results reported separately.

## Evidence

- [ ] All benchmark outputs archived.
- [ ] Prompt versions recorded.
- [ ] Model/provider versions recorded where public.
- [ ] Source lineage preserved.
- [ ] Hash manifest generated.

## Release Boundary

- [ ] No clinical validation claim.
- [ ] No legal protection or filing claim.
- [ ] No external notarization claim without receipt.
- [ ] No CERN or official benchmark adoption claim without evidence.
- [ ] No empirical superiority claim without baseline results.

## Publication

- [ ] Paper updated with actual results.
- [ ] README updated with benchmark status.
- [ ] Metadata updated with version and release date.
- [ ] CITATION.cff updated.
- [ ] Archive ZIP rebuilt and hashed.
- [ ] Optional Zenodo DOI added only after real publication.
