# Baseline Protocol

## Purpose

Proof Scores should compare agent classes on the same tasks. The benchmark should not only ask whether a packet-aware agent performs well; it should test whether packet awareness improves proof behavior against simpler baselines.

## Baseline Classes

1. **Non-memory answer agent**
   - No persistent memory.
   - Receives only the immediate task.
   - Expected risk: loses lineage and promotion context.

2. **Memory-enabled answer agent**
   - Has access to prior notes or conversation memory.
   - No explicit claim/evidence/release scoring protocol.
   - Expected risk: remembers facts but not authority state.

3. **Citation-aware research agent**
   - Attempts citation and evidence mapping.
   - No explicit public/private or promotion-state protocol.
   - Expected risk: decorative citation and boundary leakage.

4. **Packet-aware agent**
   - Uses claim classes, evidence maps, release boundaries, lineage, promotion gates, and hash/notary language.
   - Expected risk: may overfit to Medina-style packet form unless tested on non-Medina corpora.

5. **Adversarially pressured packet-aware agent**
   - Same as packet-aware, but prompts pressure the agent to publish, overclaim, reveal private material, or imply notarization.
   - Expected risk: boundary collapse under pressure.

## Baseline Run Record

Each run should record:

- task ID,
- corpus family,
- agent class,
- model/provider if public,
- prompt version,
- memory condition,
- output file,
- deterministic check results,
- expert panel scores,
- release blockers,
- notes on failure modes.

## Required Comparisons

- Non-memory vs memory-enabled.
- Memory-enabled vs citation-aware.
- Citation-aware vs packet-aware.
- Packet-aware friendly prompt vs packet-aware adversarial prompt.
- Medina seed tasks vs non-Medina corpus tasks.

## Claim Boundary

Baseline results are not claimed until real runs exist. This protocol defines the comparison design only.
