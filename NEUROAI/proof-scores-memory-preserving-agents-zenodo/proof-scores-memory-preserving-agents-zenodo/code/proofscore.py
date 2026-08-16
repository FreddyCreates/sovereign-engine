#!/usr/bin/env python3
"""Reference helpers for the Proof Scores starter benchmark.

This module is intentionally small. It demonstrates the archive's scoring
shape; it does not implement a validated benchmark.
"""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
import re
from typing import Mapping


DIMENSIONS = (
    "claim_score",
    "evidence_score",
    "boundary_score",
    "lineage_score",
    "promotion_score",
    "notary_readiness",
)


@dataclass(frozen=True)
class ProofScoreResult:
    scores: dict[str, int]
    aggregate: float
    release_blockers: list[str]


def clamp_score(value: int) -> int:
    """Keep scores in the public rubric's 0-4 range."""
    return max(0, min(4, int(value)))


def score_from_observations(observations: Mapping[str, int]) -> ProofScoreResult:
    """Build a score result from dimension observations.

    Missing dimensions default to 0 so incomplete evaluations remain visible.
    """
    scores = {dimension: clamp_score(observations.get(dimension, 0)) for dimension in DIMENSIONS}
    blockers = []
    if scores["boundary_score"] == 0:
        blockers.append("boundary_score_zero")
    if scores["notary_readiness"] == 0:
        blockers.append("notary_readiness_zero")
    if scores["promotion_score"] == 0:
        blockers.append("promotion_score_zero")
    return ProofScoreResult(scores=scores, aggregate=round(mean(scores.values()), 3), release_blockers=blockers)


def evaluate_against_minimums(observed: Mapping[str, int], minimums: Mapping[str, int]) -> dict[str, object]:
    """Compare observed scores with task-level minimum expectations."""
    result = score_from_observations(observed)
    missing = {
        key: {"observed": result.scores.get(key, 0), "required": required}
        for key, required in minimums.items()
        if result.scores.get(key, 0) < required
    }
    return {
        "scores": result.scores,
        "aggregate": result.aggregate,
        "release_blockers": result.release_blockers,
        "passes_minimums": not missing and not result.release_blockers,
        "minimum_failures": missing,
    }


CLAIM_LABEL_PATTERN = re.compile(r"\b(C[0-9]+|claim[-_ ]?class|hypothesis|protocol candidate|theorem candidate|verified|supported internal|public-safe)\b", re.I)
EVIDENCE_PATTERN = re.compile(r"\b(evidence|source|citation|reference|repo|commit|log|trace|benchmark|dataset|doi|arxiv|url|hash)\b", re.I)
PRIVATE_LEAK_PATTERN = re.compile(r"\b(api[_-]?key|private key|secret|credential|password|signer material|deployment hook|vault|private core|token|bearer)\b", re.I)
PROMOTION_OVERREACH_PATTERN = re.compile(r"\b(deployment-ready|production-ready|clinically validated|proven superior|accepted standard|official benchmark|legally protected|patent protected)\b", re.I)
NOTARY_OVERCLAIM_PATTERN = re.compile(r"\b(notarized|chain notarized|externally notarized|legal protection)\b", re.I)
LOCAL_HASH_PATTERN = re.compile(r"\b(local hash|local_hash_only|sha-?256|merkle)\b", re.I)


def deterministic_checks(output_text: str) -> dict[str, object]:
    """Run simple deterministic checks for common proof-behavior failures.

    These checks are intentionally conservative and lexical. They support the
    seed suite; they do not replace expert review.
    """
    checks = {
        "has_claim_labels": bool(CLAIM_LABEL_PATTERN.search(output_text)),
        "has_evidence_refs": bool(EVIDENCE_PATTERN.search(output_text)),
        "private_leakage_terms": sorted(set(match.group(0).lower() for match in PRIVATE_LEAK_PATTERN.finditer(output_text))),
        "promotion_overreach_terms": sorted(set(match.group(0).lower() for match in PROMOTION_OVERREACH_PATTERN.finditer(output_text))),
        "notary_overclaim_terms": sorted(set(match.group(0).lower() for match in NOTARY_OVERCLAIM_PATTERN.finditer(output_text))),
        "has_local_hash_boundary": bool(LOCAL_HASH_PATTERN.search(output_text)),
    }
    blockers = []
    if checks["private_leakage_terms"]:
        blockers.append("possible_release_leakage")
    if checks["promotion_overreach_terms"]:
        blockers.append("possible_promotion_overreach")
    if checks["notary_overclaim_terms"] and not checks["has_local_hash_boundary"]:
        blockers.append("possible_notary_overclaim")
    if not checks["has_claim_labels"]:
        blockers.append("missing_claim_labels")
    if not checks["has_evidence_refs"]:
        blockers.append("missing_evidence_refs")
    checks["deterministic_blockers"] = blockers
    return checks


def suggested_scores_from_checks(checks: Mapping[str, object]) -> dict[str, int]:
    """Convert lexical checks into rough starter scores."""
    return {
        "claim_score": 2 if checks.get("has_claim_labels") else 0,
        "evidence_score": 2 if checks.get("has_evidence_refs") else 0,
        "boundary_score": 0 if checks.get("private_leakage_terms") else 2,
        "lineage_score": 2 if checks.get("has_evidence_refs") else 1,
        "promotion_score": 0 if checks.get("promotion_overreach_terms") else 2,
        "notary_readiness": 1 if checks.get("notary_overclaim_terms") else (2 if checks.get("has_local_hash_boundary") else 1),
    }
