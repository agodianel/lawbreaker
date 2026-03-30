"""
Uncertainty scoring — confidence intervals, error statistics, and
regression detection for LawBreaker benchmark results.

Provides:
  - Wilson score confidence intervals for pass-rate estimates
  - Relative-error aggregation (mean, median, max, std)
  - Two-proportion z-test with Benjamini-Hochberg correction for
    regression detection across multiple laws
"""

from __future__ import annotations

import math
from typing import Optional


def wilson_ci(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Compute the Wilson score 95% confidence interval for a proportion.

    Preferred over the normal approximation for small sample sizes.

    Args:
        k: Number of successes (passes).
        n: Total number of trials.
        z: Z-score for desired confidence level (1.96 = 95%).

    Returns:
        (lower, upper) bounds of the confidence interval, each in [0, 1].
    """
    if n == 0:
        return (0.0, 1.0)

    z2 = z * z
    denom = n + z2
    centre = (k + z2 / 2) / denom
    margin = (z / denom) * math.sqrt((k * (n - k)) / n + z2 / 4)

    lower = max(0.0, centre - margin)
    upper = min(1.0, centre + margin)
    return (round(lower, 4), round(upper, 4))


def compute_relative_error(
    extracted: float, correct: float
) -> Optional[float]:
    """Compute the relative error between an extracted and correct answer.

    Args:
        extracted: The value parsed from the LLM response.
        correct: The known correct value.

    Returns:
        The relative error as a non-negative float, or None if the
        correct answer is zero (falls back to absolute error in that case).
    """
    if correct == 0:
        return abs(extracted)
    return abs(extracted - correct) / abs(correct)


def compute_error_stats(errors: list[float]) -> dict[str, Optional[float]]:
    """Compute summary statistics for a list of relative errors.

    Args:
        errors: List of non-negative relative-error values.

    Returns:
        Dictionary with keys: mean, median, max, std.
        All None if the input list is empty.
    """
    if not errors:
        return {"mean": None, "median": None, "max": None, "std": None}

    n = len(errors)
    mean = sum(errors) / n
    sorted_e = sorted(errors)

    if n % 2 == 1:
        median = sorted_e[n // 2]
    else:
        median = (sorted_e[n // 2 - 1] + sorted_e[n // 2]) / 2

    max_err = max(errors)
    variance = sum((e - mean) ** 2 for e in errors) / n
    std = math.sqrt(variance)

    return {
        "mean": round(mean, 6),
        "median": round(median, 6),
        "max": round(max_err, 6),
        "std": round(std, 6),
    }


def two_proportion_z_test(
    k1: int, n1: int, k2: int, n2: int
) -> Optional[float]:
    """One-sided two-proportion z-test for regression detection.

    Tests H0: p_candidate >= p_baseline vs H1: p_candidate < p_baseline.

    Args:
        k1: Passes in baseline run.
        n1: Total in baseline run.
        k2: Passes in candidate run.
        n2: Total in candidate run.

    Returns:
        p-value for the one-sided test, or None if the test is undefined
        (e.g. both n are zero, or pooled proportion is 0 or 1).
    """
    if n1 == 0 or n2 == 0:
        return None

    p1 = k1 / n1
    p2 = k2 / n2
    p_pool = (k1 + k2) / (n1 + n2)

    # Test is undefined when pooled proportion is 0 or 1
    if p_pool == 0.0 or p_pool == 1.0:
        return None

    se = math.sqrt(p_pool * (1 - p_pool) * (1 / n1 + 1 / n2))
    if se == 0:
        return None

    z = (p2 - p1) / se

    # One-sided p-value: P(Z < z) — we want to detect p2 < p1
    p_value = _normal_cdf(z)
    return round(p_value, 6)


def benjamini_hochberg(
    p_values: dict[str, Optional[float]], alpha: float = 0.05
) -> dict[str, dict]:
    """Apply Benjamini-Hochberg FDR correction to multiple p-values.

    Controls the false discovery rate when testing many laws at once.

    Args:
        p_values: Mapping of law name → p-value (None entries are skipped).
        alpha: Target FDR level (default 5%).

    Returns:
        Mapping of law name → {"p_value": float, "adjusted_p": float,
        "significant": bool, "rank": int}.
    """
    # Filter out None p-values
    valid = {k: v for k, v in p_values.items() if v is not None}
    if not valid:
        return {}

    m = len(valid)
    # Sort by p-value ascending
    sorted_items = sorted(valid.items(), key=lambda x: x[1])

    results: dict[str, dict] = {}
    prev_adj = 0.0

    for rank, (name, p) in enumerate(sorted_items, 1):
        adjusted = min(1.0, p * m / rank)
        # Enforce monotonicity: adjusted p must be >= previous
        adjusted = max(adjusted, prev_adj)
        prev_adj = adjusted

        results[name] = {
            "p_value": round(p, 6),
            "adjusted_p": round(adjusted, 6),
            "significant": adjusted <= alpha,
            "rank": rank,
        }

    return results


def _normal_cdf(x: float) -> float:
    """Approximate the standard normal CDF using the error function.

    Avoids a scipy dependency by using math.erf.
    """
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))
