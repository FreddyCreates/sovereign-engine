# THESIS Verifier Scoring Rubric

## Dimensions

| Dimension | Weight | Question |
| --- | ---: | --- |
| Claim clarity | 15 | Is the claim specific enough to verify? |
| Evidence linkage | 25 | Is there direct evidence tied to the claim? |
| Reproducibility | 20 | Can the result be reproduced or inspected? |
| Test/validation quality | 15 | Are tests, logs, benchmarks, or citations present? |
| Release discipline | 10 | Are public/private/IP boundaries respected? |
| Overclaim risk | 15 | Does the language exceed the evidence? |

## Score Bands

- `85-100`: strong support
- `70-84`: supportable with conditions
- `50-69`: partially supported
- `30-49`: weakly supported
- `0-29`: not verified

## Required Downgrades

Downgrade immediately when:

- a repo is cited but no file, commit, or test is linked
- a benchmark is claimed but no benchmark output exists
- a paper claims implementation but only gives theory
- a public claim exposes private/internal mechanisms
- a legal, notary, or deployment status is claimed without external proof
