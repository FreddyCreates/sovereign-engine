# Byzantine-Robust Coordination Bounds for the Multi-Swarm Agency Protocol

### MSAP Subpaper IV

**Author:** Alfredo Medina Hernandez
**Affiliation:** Medina Tech, Dallas, Texas
**Date:** July 2026
**Classification:** cs.MA (Multi-Agent Systems), cs.DC (Distributed Computing), cs.CR (Cryptography and Security)
**Status:** Working paper — theoretical framework with controlled numerical validation. DOI to be assigned on Zenodo deposit.
**Relation to prior work:** Scrutinizes and refines the fault-tolerance claim in *Multi-Swarm Agency Protocol* (RSHIP-2026-MSAP-001), Assumption 3.3 and Section 5, which states the protocol tolerates *f < N/φ² Byzantine swarms* without specifying an adversary model or providing a derivation.

---

## Abstract

The original MSAP paper asserts a Byzantine fault tolerance threshold of $f < N/\varphi^2 \approx 0.382N$ but does not specify what the Byzantine swarms are assumed to do, nor derive the bound from an explicit attack model. We show this matters enormously. Under a **non-adaptive** attacker (Byzantine swarms broadcast uniformly random phases), naive coherence-weighted Kuramoto aggregation — the mechanism MSAP actually specifies — tolerates Byzantine fractions up to 50% with no measurable degradation in our tests, far exceeding the claimed bound. Under an **adaptive, worst-case** attacker (Byzantine swarms observe the honest cluster's current phase and broadcast the antipodal value every round), the same naive aggregation collapses well *before* the claimed threshold: success rate falls from 100% to 9% between $f=0$ and $f=0.3$, with the claimed safe boundary at $f=0.382$ already at 2.7% success. A trimmed-mean robust aggregator improves resilience at low attack fractions (holding 100% success at $f=0.1$ versus 79% for naive) but does not push the breakdown point meaningfully closer to the claimed bound. We conclude that MSAP's stated tolerance bound is real only against non-adaptive faults, is not supported against strategic adversaries, and needs either a stronger defense mechanism or a restated, adversary-qualified bound. All results are from controlled simulation, not production systems; full code and seeds are in Appendix A.

**Keywords:** Byzantine fault tolerance, adversarial multi-agent systems, Kuramoto synchronization, robust aggregation, distributed consensus, threat modeling

---

## 1. Introduction

MSAP's abstract states the protocol is "fault-tolerant, maintaining coordination properties even when up to $f < N/\varphi^2$ swarms experience Byzantine failures." Assumption 3.3 in the same paper defines Byzantine swarms only as exhibiting "arbitrary behavior" — it does not distinguish between a swarm that has crashed and broadcasts garbage, a swarm with a random hardware fault, and a swarm actively trying to prevent the rest of the cluster from synchronizing. This is not a pedantic distinction. Byzantine fault tolerance literature since Lamport, Shostak, and Pease (1982) has always depended on the strength of the adversary assumed; a bound proven against a benign-random fault model says nothing about resilience against a strategic one, and conflating the two is a common and consequential error in distributed systems claims.

This paper asks a direct question: does MSAP's coordination mechanism — coherence-weighted Kuramoto phase averaging, exactly as specified in the original paper's Definition 2.8 — actually tolerate $f < N/\varphi^2$ Byzantine swarms, and does the answer depend on what those swarms do?

## 2. Threat Models

We test two attacker strategies, both operating on a single synchronizing cluster of $N=16$ swarms.

**Non-adaptive (random) attacker.** Each Byzantine swarm, at every round, broadcasts a phase drawn uniformly at random from $[0, 2\pi)$, independent of the cluster's actual state. This models crash-adjacent faults, sensor noise, or non-strategic misbehavior.

**Adaptive (worst-case) attacker.** Each Byzantine swarm observes the current honest-cluster mean phase $\bar\Theta_{honest}$ and broadcasts the antipodal phase $\bar\Theta_{honest} + \pi$ every round, while also falsely claiming maximal coherence ($R=1$) to maximize its weight in the coherence-weighted average. This is close to the optimal disruption strategy for a phase-averaging consensus mechanism: it actively pulls the weighted mean away from consensus rather than merely adding noise.

Both attackers operate under the same assumption as the original paper: Byzantine swarms do not need to follow the honest phase-update dynamics and can broadcast anything.

## 3. Naive Aggregation Under Both Threat Models

Naive aggregation is MSAP's mechanism exactly as specified: each honest swarm computes its phase update using the coherence-weighted Kuramoto term from all reported neighbor phases, including Byzantine ones, with no filtering.

**Table 1.** Honest-cluster synchronization success rate vs. Byzantine fraction $f$ (150 trials per point, $N=16$, sustained synchronization required for 3 consecutive rounds).

| $f$ | Random (non-adaptive) attacker | Antipodal (adaptive) attacker |
|---|---|---|
| 0.0 | 100.0% | 100.0% |
| 0.1 | 100.0% | 79.3% |
| 0.2 | 100.0% | 50.7% |
| 0.3 | 100.0% | 8.7% |
| 0.35 | 100.0% | 2.7% |
| **0.382 (claimed bound)** | **100.0%** | **2.7%** |
| 0.4 | 100.0% | 2.7% |
| 0.45 | 100.0% | 1.3% |
| 0.5 | 100.0% | 4.0% |

The contrast is stark. Against random faults, naive aggregation is essentially unbreakable in this regime — coherence weighting means a swarm broadcasting incoherent random noise contributes negligible weight even before any explicit filtering, and the claimed $N/\varphi^2$ bound is not even being stress-tested at $f=0.5$. Against a strategic attacker exploiting the same weighting mechanism (by lying about its own coherence to gain weight, then using that weight to actively cancel the honest signal), the protocol fails well inside the claimed safe region. **The claimed bound is a description of the benign-fault case, not a Byzantine-fault-tolerance guarantee in the adversarial sense the term normally implies.**

## 4. Robust Aggregation Defense

We test one candidate mitigation: a **circular trimmed mean**. Each honest swarm computes the raw circular mean of its neighbors' reported phases, discards the 35% most angularly distant reports, and takes the coherence-weighted mean of the remainder before computing its Kuramoto coupling term (Algorithm 4.1).

**Algorithm 4.1 (Robust Coupling Term).**
```
ROBUST_COUPLING(my_theta, neighbor_phases, neighbor_weights, trim_frac):
    raw_mean <- angle(sum(exp(i * neighbor_phases)))
    distances <- [circular_distance(p, raw_mean) for p in neighbor_phases]
    keep_n <- ceil(len(neighbor_phases) * (1 - trim_frac))
    keep <- indices of the keep_n smallest distances
    agg_phase, agg_R <- coherence_weighted_mean(neighbor_phases[keep], neighbor_weights[keep])
    return mean(neighbor_coupling_strengths) * sin(agg_phase - my_theta) * agg_R
```

**Table 2.** Success rate under the antipodal adaptive attacker, naive vs. robust-trimmed aggregation.

| $f$ | Naive aggregation | Robust-trimmed aggregation |
|---|---|---|
| 0.0 | 100.0% | 100.0% |
| 0.1 | 79.3% | **100.0%** |
| 0.2 | 50.7% | 58.7% |
| 0.3 | 8.7% | 9.3% |
| 0.35 | 2.7% | 1.3% |
| 0.382 | 2.7% | 1.3% |

Trimming meaningfully helps at $f=0.1$ (full recovery to 100%) and modestly at $f=0.2$, but by $f=0.3$ the two schemes are statistically indistinguishable, and trimming provides no benefit at or above the claimed threshold. The reason is structural: once Byzantine swarms are a large enough fraction of the *reporting* neighbors, trimming 35% of the most-distant reports no longer reliably removes them — a sufficiently large coordinated bloc survives the trim and still dominates the weighted average.

## 5. Analysis

Three findings, stated precisely:

1. **The claimed bound $f < N/\varphi^2$ is unfalsified against non-adaptive faults** in the regime we tested — we could not break naive aggregation with random-phase faults even at $f=0.5$, well past the claimed threshold. Framed generously, the original paper's bound may be a valid (if untested) description of resilience to accidental faults.

2. **The claimed bound does not hold against an adaptive, coherence-lying attacker.** The mechanism that makes MSAP's coupling effective against honest heterogeneous swarms — weighting neighbors by their self-reported coherence — is exactly the mechanism a strategic attacker exploits, by claiming false coherence to gain influence. This is a design tension, not a tuning problem: the more you trust self-reported coherence, the more exploitable the protocol is to an attacker willing to lie about it.

3. **Trimmed-mean robustness buys a meaningfully wider safety margin at low attack fractions but does not restore the claimed bound.** This is a genuine, if partial, improvement — worth including in any real deployment — but should not be marketed as closing the gap identified in finding 2.

**Practical implication:** if MSAP is deployed in any setting where a compromised or malicious swarm operator is plausible — as opposed to a purely accidental-fault setting — the protocol needs either (a) a coherence attestation mechanism that cannot be self-reported (e.g., a third party or the receiving swarm computing it from raw phase history rather than trusting a broadcast value), or (b) a restated, lower, adversary-qualified tolerance bound until such a mechanism exists.

## 6. Limitations and Open Problems

- We tested one specific adaptive attack (antipodal phase, false-maximal-coherence claim). It is a strong and natural worst-case candidate for phase-averaging consensus, but it is not proven optimal; a more sophisticated attacker (e.g., one that adapts its claimed coherence dynamically rather than always claiming 1.0) might do better or worse against the trimmed defense.
- We did not test coherence attestation defenses (recomputing neighbor coherence from raw phase history rather than trusting the broadcast value), which Finding 3 suggests is the more promising direction than trimming alone.
- All results are for a single cluster of fixed size ($N=16$); we have not characterized how the breakdown point scales with $N$.
- This paper does not address composed/hierarchical settings (see Subpaper III) under adversarial constituents — that combination is an open problem.

## 7. Related Work

Lamport, Shostak, Pease (1982), *The Byzantine Generals Problem*, established the classical $f < N/3$ bound for consensus under authenticated Byzantine faults — a different problem (discrete agreement) from continuous phase synchronization, but the discipline of stating the bound relative to an explicit adversary model is the standard this paper is holding MSAP to. Robust statistics for distributed learning (Blanchard et al., *Machine Learning with Adversaries: Byzantine Tolerant Gradient Descent*, NeurIPS 2017) uses trimmed-mean and median-based aggregation for essentially the same reason we do here — coordinate-wise robust estimators degrade gracefully but have known limits once the adversarial fraction is large relative to the trim margin, consistent with what we observe in Section 4.

## 8. Conclusion

A fault-tolerance bound is only as meaningful as the adversary model it's proven against. MSAP's stated $f < N/\varphi^2$ tolerance holds, in our tests, against random non-adaptive faults, and fails well before that threshold against a strategic attacker exploiting the protocol's own coherence-weighting mechanism. Trimmed-mean aggregation is a real, worthwhile improvement at moderate attack fractions but does not restore the original bound. Anyone deploying MSAP in a setting with potentially adversarial (not just faulty) participants should treat the $N/\varphi^2$ figure as inapplicable until a non-self-reported coherence mechanism is built and tested.

---

## References

1. Medina Hernandez, A. (2026). *Multi-Swarm Agency Protocol*. RSHIP-2026-MSAP-001.
2. Lamport, L., Shostak, R., Pease, M. (1982). The Byzantine Generals Problem. *ACM Transactions on Programming Languages and Systems*, 4(3).
3. Blanchard, P., El Mhamdi, E.M., Guerraoui, R., Stainer, J. (2017). Machine Learning with Adversaries: Byzantine Tolerant Gradient Descent. *NeurIPS 2017*.
4. Kuramoto, Y. (1975). Self-entrainment of a population of coupled non-linear oscillators.

---

## Appendix A: Reproducibility

Python 3 / NumPy. Seeds 7000–7149 (150 trials per condition), $N=16$, $K_0=\varphi$, coupling scale 0.6, base noise $\sigma=0.15$, max 40 rounds, 3-round sustain requirement. Full script (both attacker models and both aggregation schemes) is available on request as `byz_sim.py`; core logic:

```python
import numpy as np
PHI = (1 + 5**0.5) / 2
PHI_INV = 1 / PHI

def circular_trimmed_mean_phase(phases, weights, trim_frac):
    n = len(phases)
    raw_mean = np.angle(np.sum(np.exp(1j*phases)))
    dist = np.array([min(abs(p-raw_mean), 2*np.pi-abs(p-raw_mean)) for p in phases])
    keep_n = max(1, int(np.ceil(n * (1 - trim_frac))))
    keep_idx = np.argsort(dist)[:keep_n]
    vec = np.sum(weights[keep_idx] * np.exp(1j*phases[keep_idx]))
    return np.angle(vec), np.abs(vec) / np.sum(weights[keep_idx])

# Adaptive attacker: broadcasts (honest_mean_phase + pi) every round, claims coherence 1.0.
# Random attacker: broadcasts uniform(0, 2*pi) every round, independent of cluster state.
# Naive aggregation: raw coherence-weighted Kuramoto coupling term, no filtering.
# Robust aggregation: circular_trimmed_mean_phase() with trim_frac=0.35 before computing coupling.
```
