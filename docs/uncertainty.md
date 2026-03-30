# Uncertainty Scoring & Regression Detection

## Overview

LawBreaker includes built-in statistical uncertainty scoring so that benchmark
results come with confidence intervals, error statistics, and regression
detection — no external stats libraries required.

## Wilson Score Confidence Intervals

Every pass rate (per-law, per-trap, overall) includes a **Wilson score 95% CI**.
Wilson intervals are preferred over normal approximation because they behave
correctly at boundary values (0% and 100%) and with small sample sizes.

```python
from lawbreaker.core.uncertainty import wilson_ci

# 4 out of 5 questions passed
lower, upper = wilson_ci(k=4, n=5, z=1.96)
# → (0.366, 0.964)
```

Results JSON includes these automatically:

```json
{
  "per_law_ci": {
    "Ohm's Law": [0.366, 0.964],
    "Kinetic Energy": [0.168, 0.832]
  }
}
```

## Relative Error Tracking

Each question now records the **relative error** between the extracted answer
and the correct answer: `|extracted - correct| / |correct|`.

This quantifies *how wrong* a model is, not just pass/fail. A model that
answers 19.8V instead of 20V (1% error) is doing better than one that
answers 35V (75% error), even though both fail a strict tolerance check.

Per-law error statistics (mean, median, max, std) are included in report JSON.

## Regression Detection

The `lawbreaker compare` CLI command detects regressions between two benchmark
runs using a **two-proportion z-test** per law.

Because 34 laws are tested simultaneously, raw p-values are corrected using the
**Benjamini-Hochberg** procedure to control the false discovery rate (FDR).

```bash
lawbreaker compare baseline.json candidate.json --alpha 0.05
```

### Why Benjamini-Hochberg?

With 34 laws tested at α=0.05, you'd expect ~1.7 false positives by chance.
Benjamini-Hochberg controls the **expected proportion of false discoveries**
among rejected hypotheses, providing a practical balance between sensitivity
and false alarm rate.

### Low-N Warning

With the default 5 questions per law, statistical power is limited. The compare
command displays a warning when sample sizes are small. For statistically
meaningful regression detection, use `--questions 20` or higher.

## API Reference

```python
from lawbreaker.core.uncertainty import (
    wilson_ci,              # Wilson score CI for a proportion
    compute_relative_error, # |extracted - correct| / |correct|
    compute_error_stats,    # mean, median, max, std of errors
    two_proportion_z_test,  # z-test for two pass rates
    benjamini_hochberg,     # FDR correction for multiple tests
)
```
