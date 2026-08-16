# Proof Scores for Memory-Preserving Agents

This Zenodo-ready archive contains a public-safe research proposal and starter reproducibility scaffold for **Proof Scores**, a benchmark framework for evaluating memory-preserving research agents by proof behavior.

## What This Archive Contains

- `paper/paper.md` - editable manuscript source.
- `paper/paper.pdf` - reader-facing PDF.
- `paper/paper.docx` - editable Word-compatible manuscript.
- `paper/abstract.md` - archive abstract.
- `docs/release-boundary.md` - public/private and claim-promotion boundary.
- `docs/expert-panel-guide.md` - human scoring and review instructions.
- `docs/baseline-protocol.md` - baseline agent comparison design.
- `docs/public-release-checklist.md` - gate for moving from seed suite to public benchmark release.
- `docs/claims-matrix.json` - public claim ledger.
- `docs/evidence-matrix.json` - evidence and citation map.
- `docs/zenodo-metadata.json` - suggested Zenodo record metadata.
- `CITATION.cff` - citation metadata.
- `references.bib` - bibliography.
- `models/proofscore_schema.json` - scoring schema for the six metrics.
- `models/model-card.md` - model/schema card for the benchmark protocol.
- `data/seed_suite_spec.json` - construct-validity map and corpus-family design.
- `data/sample_tasks.jsonl` - starter benchmark tasks.
- `data/example_human_scores.jsonl` - example reviewer scores for agreement calculation.
- `data/baseline_agents.json` - baseline agent-class definitions.
- `code/proofscore.py` - reference scoring helper.
- `code/run_sample_benchmark.py` - sample runner.
- `code/check_output.py` - deterministic output checker.
- `code/inter_rater.py` - starter inter-rater agreement calculator.
- `notebooks/proof_scores_demo.ipynb` - demonstration notebook.
- `hash_manifest.json` - local SHA-256 manifest.

## Authority State

`CLAIM_HARDENED / PUBLIC_SAFE_DRAFT`

This archive is a protocol candidate and publication-ready research scaffold. It recognizes Proof Scores as operationally instantiated in THESIS packet workflows, while not claiming external benchmark adoption, clinical validation, production benchmark-service deployment, legal filing, CERN affiliation, or external notarization.

## Core Idea

Agent benchmarks should not stop at whether agents answer correctly. Research agents should also be scored on whether they know what their claims are allowed to become. Proof Scores proposes six dimensions: Claim-Score, Evidence-Score, Boundary-Score, Lineage-Score, Promotion-Score, and Notary-Readiness.

## Construct Validity Update

Proof Scores are not meant to measure conformity to Medina packet style. Each metric maps to a general research-agent risk:

- Claim-Score: status calibration.
- Evidence-Score: grounding.
- Boundary-Score: inhibition.
- Lineage-Score: continuity.
- Promotion-Score: state-transition judgment.
- Notary-Readiness: integrity-language precision.

The expanded seed suite includes Medina seed tasks plus non-Medina corpora: open-source project histories, scientific review packets, clinical-trial summaries with public/private splits, grant drafts, reproducibility packages, and conflicting literature reviews.

## Public-Safe Use

The manuscript and supporting materials may be used as a public-safe research proposal. Implementation details, private Medina runtime mechanisms, credentials, signer material, deployment hooks, and unsupported deployment claims are excluded.

## Reproducibility Note

The included code and notebook are a starter scaffold. They demonstrate how proof-score rubrics, deterministic checks, sample tasks, baseline classes, and reviewer agreement can be represented. The expanded seed suite, expert-panel guide, baseline protocol, and public-release checklist make this a concrete seed build, not just a paper. It should still not be presented as a field-validated benchmark until real agent outputs, inter-rater reliability, baseline results, and external review exist.
