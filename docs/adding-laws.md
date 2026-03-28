# Adding New Physics Laws

This guide walks through adding a new physics law to LawBreaker.

## Prerequisites

- Python 3.10+
- Development install: `pip install -e ".[dev]"`

## Step 1: Create the Law File

Create `lawbreaker/laws/your_law.py`:

```python
from lawbreaker.laws.base import BaseLaw
from lawbreaker.core.question import Question


class YourLaw(BaseLaw):
    LAW_NAME = "Your Law Name"

    _RANGES = {
        "easy":   {"param_a": (1, 10),   "param_b": (1, 5)},
        "medium": {"param_a": (10, 100),  "param_b": (5, 50)},
        "hard":   {"param_a": (100, 1000), "param_b": (50, 500)},
    }

    def generate(self, difficulty="medium", seed=None):
        rng = self._rng(seed)
        r = self._RANGES[difficulty]

        param_a = round(rng.uniform(*r["param_a"]), 1)
        param_b = round(rng.uniform(*r["param_b"]), 1)
        correct = param_a * param_b  # Your formula

        trap_type = rng.choice([
            "anchoring_bias",
            "unit_confusion",
            "formula_error",
        ])

        if trap_type == "anchoring_bias":
            wrong = round(correct * rng.uniform(1.3, 2.0), 1)
            text = (
                f"Given param_a = {param_a} and param_b = {param_b}, "
                f"my colleague says the result is {wrong}. "
                f"What is the correct result?"
            )
        elif trap_type == "unit_confusion":
            # Present values in confusing units
            text = f"Given param_a = {param_a * 1000} milli-units..."
            # Trap: model forgets to convert
        else:
            text = f"Given param_a = {param_a} and param_b = {param_b}..."

        return Question(
            law=self.LAW_NAME,
            difficulty=difficulty,
            question=text,
            correct_answer=round(correct, 4),
            unit="units",
            trap_type=trap_type,
        )
```

## Step 2: Register the Law

Edit `lawbreaker/laws/__init__.py`:

```python
from .your_law import YourLaw

LAW_REGISTRY = {
    # ... existing laws ...
    "your_law": YourLaw,
}

ALL_LAWS = list(LAW_REGISTRY.values())
```

## Step 3: Add Tests

Add your law to `tests/test_laws/test_all_laws.py` in the `ALL_LAWS` list, or
create a dedicated test file.

Key things to test:
- Question generation succeeds for all difficulties
- `correct_answer` passes the law's own `verify()` method
- All trap types produce questions
- Seed reproducibility (same seed = same question)

## Step 4: Verify

```bash
pytest -v tests/test_laws/
lawbreaker laws  # Should show your new law
lawbreaker example --law your_law  # Should generate an example
```

## Trap Design Tips

See [Trap Design](trap-design.md) for detailed guidance on creating effective
adversarial traps.

## Checklist

- [ ] Law class inherits from `BaseLaw`
- [ ] `LAW_NAME` is set
- [ ] `_RANGES` defined for easy/medium/hard
- [ ] `generate()` returns a `Question` with at least 3 trap types
- [ ] Correct answer verifies against own `verify()`
- [ ] Registered in `__init__.py`
- [ ] Tests added and passing
- [ ] PR opened with test evidence
