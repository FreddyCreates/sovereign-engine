# A Benchmark Methodology for Decentralized Multi-Agent Coordination Protocols

### MSAP Subpaper V

**Author:** Alfredo Medina Hernandez
**Affiliation:** Medina Tech, Dallas, Texas
**Date:** July 2026
**Classification:** cs.MA (Multi-Agent Systems), cs.DC (Distributed Computing)
**Status:** Working paper — methodology and self-audit. DOI to be assigned on Zenodo deposit.
**Relation to prior work:** Motivated directly by two problems encountered while producing Subpapers III and IV of this series: a finite-size measurement artifact and an adversary-model-dependent bound that is meaningless without specifying the adversary.

---

## Abstract

Multi-agent coordination papers, including the original MSAP paper in this series, commonly report point-estimate success rates and latencies without specifying random seeds, trial counts, synchronization-detection criteria, or — when fault tolerance is claimed — the adversary model the bound was tested against. This paper proposes a minimal reporting standard for this subfield and demonstrates why it matters using two concrete, quantified failure modes we hit ourselves. First, we show that the standard Kuramoto order-parameter threshold test for "synchronization" produces false positives from pure chance at a rate of 14.6% for a 5-swarm cluster and 4.2% for an 8-swarm cluster, dropping below 0.03% only once cluster size reaches roughly 16 swarms or a multi-round sustain criterion is applied — meaning several small-N results in the literature (and in an earlier draft of our own Subpaper III) risk measuring noise, not synchronization. Second, we show a Byzantine fault-tolerance bound reported without an adversary model (as in the original MSAP paper) can be simultaneously true against benign faults and false against strategic ones, as demonstrated empirically in Subpaper IV. We propose a five-point reporting checklist and re-audit our own two prior subpapers against it.

**Keywords:** benchmark methodology, reproducibility, multi-agent systems, statistical validity, finite-size effects, adversarial evaluation

---

## 1. Introduction

The original MSAP paper reports "94.7% coordination success rate (σ = 2.3%)" across "47 production deployments spanning six industries" with a specific DOI and page count. Papers in this general style are common in the field: precise-sounding statistics, no seeds, no methodology for how the "production deployments" were selected or measured, and no distinction between what was actually run and what was extrapolated. Our own Subpapers III and IV of this series, produced with actual numerical simulation rather than assertion, still nearly repeated a version of the same mistake — not through misrepresentation, but through an initial parameter choice (a 5-swarm cluster) that happened to make the measurement itself unreliable, which we only caught by checking the null-hypothesis behavior of our own synchronization test. This paper writes down what we learned from that, as a checklist for anyone — including our future selves — writing the next paper in this series.

## 2. A Minimal Reporting Standard

We propose that any empirical claim about a multi-agent coordination protocol state, at minimum:

1. **Parameters** — cluster size(s) tested, coupling scheme and constants, noise model, round limits.
2. **Trial count and seeds** — how many independent trials, and either the exact seed range or a statement that seeds were not fixed (with justification).
3. **Detection criterion** — the exact rule used to declare "synchronized," including whether a single-round threshold crossing counts or a sustained criterion is required, and why.
4. **Statistical uncertainty** — standard error or confidence interval, not a bare point estimate.
5. **Adversary model, if fault tolerance is claimed** — an explicit description of what the faulty/Byzantine participants are assumed to do (crash, random noise, worst-case adaptive, colluding), since, as we show below, the same tolerance bound can be simultaneously true and false depending on this alone.

None of these are novel individually — they are standard practice in adjacent fields (systems benchmarking, adversarial ML robustness evaluation). The contribution here is applying them specifically to swarm/multi-agent coordination claims, where we found them frequently missing, including in earlier work in this series.

## 3. The Finite-Size False-Positive Problem

### 3.1 The Mechanism

The Kuramoto order parameter for $N$ phases $\theta_1, \ldots, \theta_N$ is $R = \left|\frac{1}{N}\sum_j e^{i\theta_j}\right|$. MSAP declares synchronization when $R > \varphi^{-1} \approx 0.618$. But $R$ is a random variable even when phases are drawn **independently and uniformly** — i.e., with no coordination at all — and its variance scales as $O(1/N)$. For small $N$, $R$ crosses the synchronization threshold purely by chance at a non-trivial rate.

### 3.2 Quantified False-Positive Rates

We drew $\theta_1, \ldots, \theta_N$ independently and uniformly at random (200,000 trials per cluster size, no dynamics, no coupling — the null hypothesis of "no real synchronization occurring") and measured how often $R$ alone would trigger a false "synchronized" declaration.

**Table 1.** False-positive rate of the instantaneous threshold test $R > \varphi^{-1}$, by cluster size $N$, under the null hypothesis of independent uniform phases.

| $N$ | False-positive rate |
|---|---|
| 3 | 35.4% |
| 5 | 14.6% |
| 8 | 4.2% |
| 10 | 1.8% |
| 16 | 0.15% |
| 20 | 0.02% |
| 30 | ~0% |

This is a serious effect at small $N$. A researcher benchmarking a 5-swarm cluster with a single-round threshold test will see "synchronization" nearly one time in seven even if the swarms are doing nothing but broadcasting random noise.

### 3.3 The Sustain Correction

Requiring the threshold to hold for $k$ consecutive rounds sharply reduces the false-positive rate, since independent per-round draws must all exceed threshold together:

**Table 2.** False-positive rate with a 3-round sustain requirement (40-round window, independent resampling each round — i.e., testing the detector, not a real dynamical system).

| $N$ | Sustain-3 false-positive rate |
|---|---|
| 5 | 9.9% |
| 8 | 0.43% |
| 16 | < 0.03% (0/3000 trials) |

The sustain requirement does not fully eliminate the problem at very small $N$ (5-swarm clusters still show a 9.9% false-positive rate even with sustain-3), but it is a substantial improvement, and combined with $N \geq 8$ it brings the false-positive rate to a level most empirical work would consider acceptable.

### 3.4 Self-Audit

Our own Subpaper III's numerical validation uses $N=8$ per cluster with a 3-round sustain requirement — a false-positive rate of approximately 0.43% per the table above, which we consider acceptable but note explicitly here rather than leaving implicit. An earlier internal draft of that simulation used $N=5$, which we discarded specifically because of the false-positive rate quantified in Table 1 — this paper is, in part, the writeup of why we made that change.

## 4. Adversary-Model Dependence

Subpaper IV demonstrates the second failure mode directly: MSAP's claimed Byzantine tolerance bound $f < N/\varphi^2$ held, in our tests, against a non-adaptive random-broadcast attacker up to the maximum fraction tested (50%), while collapsing well before the claimed threshold (down to 8.7% success at $f=0.3$) against an adaptive attacker exploiting the protocol's coherence-weighting mechanism. Reporting "the protocol tolerates $f < N/\varphi^2$ Byzantine swarms" without stating which of these two regimes was tested makes the claim unfalsifiable in the wrong way — it can be defended as true by pointing to the easy case, or attacked as false by pointing to the hard case, and neither party is wrong given how little the original claim specifies.

**Recommendation:** any Byzantine tolerance claim should name the attacker class explicitly (e.g., "tolerates $f < X$ under a non-adaptive random-fault model" vs. "tolerates $f < X$ under an adaptive worst-case model"), and ideally report both if only one is inconvenient to omit.

## 5. Reference Workload Generator

To make comparisons across studies possible, we propose a minimal parametrized generator rather than ad hoc setups:

```
GENERATE_CLUSTER(N, coupling_scale, noise_sigma, natural_freq_std, seed):
    rng <- seeded_random(seed)
    theta_0 <- rng.uniform(0, 2*pi, N)          // initial phases
    omega <- rng.normal(0, natural_freq_std, N) // heterogeneous natural frequencies
    K <- zeros(N, N)
    for i, j in pairs(N):
        overlap <- rng.uniform(0, 1)             // domain overlap, per MSAP Def. 2.6
        compat  <- rng.uniform(0.5, 1.0)         // objective compatibility, per Def. 2.5
        K[i,j] = K[j,i] <- coupling_scale * phi^(-overlap) * compat
    return theta_0, omega, K
```

Reporting the generator parameters (as we do in Appendices A of Subpapers III and IV) means any reader can regenerate the exact clusters tested, not just re-read a summary statistic.

## 6. Discussion

This is a narrow methodology paper, deliberately: it does not propose a new coordination protocol, and it does not claim MSAP or its extensions are wrong in their design, only that some of the ways their properties get reported and tested need tightening. The broader point generalizes past this paper series. Multi-agent and swarm-coordination research is easy to over-claim in, precisely because "synchronization," "success," and "fault tolerance" all sound like binary, obviously-measured properties when they are actually threshold judgments on noisy statistics, sensitive to a handful of design choices (cluster size, detection window, adversary model) that are cheap to state and easy to omit.

## 7. Conclusion

We recommend that any future paper in this series — and, more broadly, any empirical multi-agent coordination paper — report cluster size alongside its associated false-positive rate for whatever synchronization test is used, state explicitly whether a fault-tolerance claim is benign-fault or adversarial, and publish generator parameters and seeds sufficient for independent replication. All three recommendations cost the author little and cost the reader a great deal if omitted.

---

## References

1. Medina Hernandez, A. (2026). *Multi-Swarm Agency Protocol*. RSHIP-2026-MSAP-001.
2. Medina Hernandez, A. (2026). *Hierarchical Swarm-of-Swarms Composition in the Multi-Swarm Agency Protocol*. MSAP Subpaper III.
3. Medina Hernandez, A. (2026). *Byzantine-Robust Coordination Bounds for the Multi-Swarm Agency Protocol*. MSAP Subpaper IV.
4. Sculley, D. et al. (2018). Winner's Curse? On Pace, Progress, and Empirical Rigor. *ICLR Workshop*.
5. Henderson, P. et al. (2018). Deep Reinforcement Learning that Matters. *AAAI*.

---

## Appendix A: Reproducibility

Python 3 / NumPy. Null-hypothesis false-positive rates (Table 1): 200,000 trials per $N$, independent uniform phase draws, seed 123. Sustain-3 rates (Table 2): 3,000 trials per $N$, 40-round window, seed 999, independent resampling each round (i.e., testing the detector against pure noise, not a real dynamical system).

```python
import numpy as np
PHI_INV = 2 / (1 + 5**0.5)

def instant_false_positive_rate(N, trials, rng):
    thetas = rng.uniform(0, 2*np.pi, size=(trials, N))
    R = np.abs(np.mean(np.exp(1j*thetas), axis=1))
    return np.mean(R > PHI_INV)

def sustain_false_positive_rate(N, sustain, rounds, trials, rng):
    count = 0
    for t in range(trials):
        streak = 0
        for r in range(rounds):
            theta = rng.uniform(0, 2*np.pi, N)
            R = np.abs(np.mean(np.exp(1j*theta)))
            if R > PHI_INV:
                streak += 1
                if streak >= sustain:
                    count += 1
                    break
            else:
                streak = 0
    return count / trials
```
