"""
Tests for the uncertainty scoring module — Wilson CI, error stats,
relative error, two-proportion z-test, and Benjamini-Hochberg correction.
"""

import math

import pytest

from lawbreaker.core.uncertainty import (
    benjamini_hochberg,
    compute_error_stats,
    compute_relative_error,
    two_proportion_z_test,
    wilson_ci,
)


class TestWilsonCI:
    """Tests for Wilson score confidence interval."""

    def test_perfect_score(self):
        """k=n: upper bound should be 1.0, lower should be high."""
        lower, upper = wilson_ci(10, 10)
        assert upper == 1.0
        assert lower > 0.65

    def test_zero_score(self):
        """k=0: lower bound should be 0.0, upper should be low."""
        lower, upper = wilson_ci(0, 10)
        assert lower == 0.0
        assert upper < 0.35

    def test_empty(self):
        """n=0: should return (0.0, 1.0) — maximum uncertainty."""
        assert wilson_ci(0, 0) == (0.0, 1.0)

    def test_single_pass(self):
        """k=1, n=1: wide interval."""
        lower, upper = wilson_ci(1, 1)
        assert lower > 0.0
        assert upper == 1.0

    def test_single_fail(self):
        """k=0, n=1: interval from 0 to something less than 1."""
        lower, upper = wilson_ci(0, 1)
        assert lower == 0.0
        assert upper < 1.0

    def test_half_pass(self):
        """k=5, n=10: should be centred around 0.5."""
        lower, upper = wilson_ci(5, 10)
        assert lower < 0.5
        assert upper > 0.5
        # Verify symmetry: midpoint should be near 0.5
        mid = (lower + upper) / 2
        assert abs(mid - 0.5) < 0.05

    def test_large_n_tight_interval(self):
        """Large n should give tighter interval than small n."""
        _, upper_small = wilson_ci(8, 10)
        lower_small, _ = wilson_ci(8, 10)
        width_small = upper_small - lower_small

        _, upper_large = wilson_ci(80, 100)
        lower_large, _ = wilson_ci(80, 100)
        width_large = upper_large - lower_large

        assert width_large < width_small

    def test_bounds_are_valid(self):
        """Bounds should be in [0, 1] and lower <= upper."""
        for k in range(11):
            lower, upper = wilson_ci(k, 10)
            assert 0.0 <= lower <= upper <= 1.0


class TestComputeRelativeError:
    """Tests for relative error computation."""

    def test_exact_match(self):
        """Zero error when extracted equals correct."""
        assert compute_relative_error(10.0, 10.0) == 0.0

    def test_positive_error(self):
        """10% overestimate."""
        err = compute_relative_error(11.0, 10.0)
        assert abs(err - 0.1) < 1e-10

    def test_negative_error(self):
        """Error is always non-negative (absolute)."""
        err = compute_relative_error(9.0, 10.0)
        assert err == pytest.approx(0.1)

    def test_zero_correct(self):
        """When correct is 0, returns absolute value of extracted."""
        assert compute_relative_error(5.0, 0.0) == 5.0
        assert compute_relative_error(0.0, 0.0) == 0.0

    def test_large_error(self):
        """Model off by 10x."""
        err = compute_relative_error(100.0, 10.0)
        assert err == pytest.approx(9.0)


class TestComputeErrorStats:
    """Tests for error statistics aggregation."""

    def test_empty_list(self):
        """All stats should be None for empty input."""
        stats = compute_error_stats([])
        assert stats["mean"] is None
        assert stats["median"] is None
        assert stats["max"] is None
        assert stats["std"] is None

    def test_single_value(self):
        """Single value: mean=median=max=value, std=0."""
        stats = compute_error_stats([0.5])
        assert stats["mean"] == pytest.approx(0.5)
        assert stats["median"] == pytest.approx(0.5)
        assert stats["max"] == pytest.approx(0.5)
        assert stats["std"] == pytest.approx(0.0)

    def test_two_values(self):
        """Two values: median is average."""
        stats = compute_error_stats([0.2, 0.8])
        assert stats["mean"] == pytest.approx(0.5)
        assert stats["median"] == pytest.approx(0.5)
        assert stats["max"] == pytest.approx(0.8)

    def test_odd_count_median(self):
        """Odd count: median is middle value."""
        stats = compute_error_stats([0.1, 0.5, 0.9])
        assert stats["median"] == pytest.approx(0.5)

    def test_std_nonzero(self):
        """Standard deviation for spread-out values."""
        stats = compute_error_stats([0.0, 1.0])
        assert stats["std"] == pytest.approx(0.5)

    def test_all_same(self):
        """Identical values: std=0."""
        stats = compute_error_stats([0.3, 0.3, 0.3])
        assert stats["std"] == pytest.approx(0.0)


class TestTwoProportionZTest:
    """Tests for the two-proportion z-test."""

    def test_identical_proportions(self):
        """Same pass rate → p-value near 0.5 (no evidence of regression)."""
        p = two_proportion_z_test(8, 10, 8, 10)
        assert p is not None
        assert abs(p - 0.5) < 0.01

    def test_clear_regression(self):
        """Large drop → small p-value."""
        p = two_proportion_z_test(90, 100, 50, 100)
        assert p is not None
        assert p < 0.001

    def test_clear_improvement(self):
        """Large improvement → large p-value (one-sided for regression)."""
        p = two_proportion_z_test(50, 100, 90, 100)
        assert p is not None
        assert p > 0.99

    def test_zero_n_returns_none(self):
        """Test is undefined with zero samples."""
        assert two_proportion_z_test(0, 0, 5, 10) is None
        assert two_proportion_z_test(5, 10, 0, 0) is None

    def test_all_pass_returns_none(self):
        """Pooled proportion of 1.0 → undefined."""
        assert two_proportion_z_test(10, 10, 10, 10) is None

    def test_all_fail_returns_none(self):
        """Pooled proportion of 0.0 → undefined."""
        assert two_proportion_z_test(0, 10, 0, 10) is None

    def test_small_regression(self):
        """Small drop at small n → p-value not significant."""
        p = two_proportion_z_test(8, 10, 6, 10)
        assert p is not None
        # At n=10, a 20% drop is not significant at p<0.05
        assert p > 0.05


class TestBenjaminiHochberg:
    """Tests for Benjamini-Hochberg FDR correction."""

    def test_empty_input(self):
        """No p-values → empty result."""
        assert benjamini_hochberg({}) == {}

    def test_all_none(self):
        """All None p-values → empty result."""
        assert benjamini_hochberg({"a": None, "b": None}) == {}

    def test_single_significant(self):
        """Single p-value below alpha → significant."""
        result = benjamini_hochberg({"law_a": 0.01}, alpha=0.05)
        assert result["law_a"]["significant"] is True
        assert result["law_a"]["adjusted_p"] == pytest.approx(0.01)

    def test_single_not_significant(self):
        """Single p-value above alpha → not significant."""
        result = benjamini_hochberg({"law_a": 0.10}, alpha=0.05)
        assert result["law_a"]["significant"] is False

    def test_multiple_correction(self):
        """Adjusted p-values should be >= raw p-values."""
        pvals = {"a": 0.01, "b": 0.03, "c": 0.04, "d": 0.80}
        result = benjamini_hochberg(pvals, alpha=0.05)
        for name, info in result.items():
            assert info["adjusted_p"] >= info["p_value"]

    def test_monotonicity(self):
        """Adjusted p-values should be monotonically non-decreasing by rank."""
        pvals = {"a": 0.01, "b": 0.02, "c": 0.03, "d": 0.04, "e": 0.05}
        result = benjamini_hochberg(pvals)
        sorted_by_rank = sorted(result.values(), key=lambda x: x["rank"])
        for i in range(1, len(sorted_by_rank)):
            assert sorted_by_rank[i]["adjusted_p"] >= sorted_by_rank[i - 1]["adjusted_p"]

    def test_controls_false_discoveries(self):
        """With many non-significant p-values, few should survive correction."""
        # Simulate: 1 real signal + 19 null (p ~ 0.5)
        pvals = {f"law_{i}": 0.5 for i in range(19)}
        pvals["real_signal"] = 0.001
        result = benjamini_hochberg(pvals, alpha=0.05)
        significant = [k for k, v in result.items() if v["significant"]]
        assert "real_signal" in significant
        # Very unlikely that null p=0.5 survives BH at alpha=0.05
        assert len(significant) <= 2

    def test_none_values_skipped(self):
        """None p-values should not appear in results."""
        pvals = {"a": 0.01, "b": None, "c": 0.03}
        result = benjamini_hochberg(pvals)
        assert "b" not in result
        assert len(result) == 2

    def test_adjusted_p_capped_at_1(self):
        """Adjusted p-values should never exceed 1.0."""
        pvals = {"a": 0.8, "b": 0.9}
        result = benjamini_hochberg(pvals)
        for info in result.values():
            assert info["adjusted_p"] <= 1.0
