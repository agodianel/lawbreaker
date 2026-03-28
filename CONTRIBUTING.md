# Contributing to LawBreaker

Thank you for your interest in contributing! This guide will help you get started.

## What You Can Contribute

### New Physics Laws
Add a new adversarial physics law under `lawbreaker/laws/`:
1. Subclass `BaseLaw` in a new file (e.g., `lawbreaker/laws/your_law.py`).
2. Implement `generate()` with at least 3 trap types.
3. Define `_RANGES` for `easy`, `medium`, and `hard` difficulties.
4. Register the law in `lawbreaker/laws/__init__.py`.
5. Add tests in `tests/test_laws/`.

### New LLM Connectors
Add support for additional LLM APIs under `lawbreaker/connectors/`:
1. Subclass `BaseConnector` in a new file.
2. Implement the `query()` method.
3. Add the connector to `lawbreaker/connectors/__init__.py`.
4. Add an example script in `examples/`.

### New Trap Types
Improve existing laws with more creative adversarial traps:
1. Study the existing trap patterns (anchoring bias, unit confusion, sign errors).
2. Add new trap types to an existing law's `generate()` method.
3. Ensure the trap has a plausible wrong answer and a correct answer.
4. Add corresponding tests.

### Bug Fixes and Documentation
Always welcome! Please include test evidence when applicable.

## Development Setup

```bash
# Clone the repository
git clone https://github.com/lawbreaker-benchmark/lawbreaker.git
cd lawbreaker

# Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install for development
pip install -e ".[dev]"

# Run tests
pytest -v
```

## Pull Request Process

1. Fork the repository and create a feature branch.
2. Make your changes following the coding standards below.
3. Add or update tests as needed.
4. Run the full test suite: `pytest -v`
5. Update documentation if applicable.
6. Submit a PR with:
   - Clear description of the change.
   - Test evidence (command output or screenshots).
   - Any notes on new trap types or physics formulas.

## Code Style

- **Python**: PEP 8, type hints where helpful, clear variable names.
- **Laws**: Each law must self-verify — `correct_answer` must pass its own `verify()`.
- **Traps**: Each trap must have a plausible wrong answer distinct from the correct one.
- **Markdown**: ATX-style headers, consistent formatting, no trailing whitespace.

## Adding a New Law — Step by Step

```python
from lawbreaker.laws.base import BaseLaw
from lawbreaker.core.question import Question

class MyNewLaw(BaseLaw):
    LAW_NAME = "My New Law"

    _RANGES = {
        "easy":   {"param1": (1, 10), "param2": (1, 5)},
        "medium": {"param1": (10, 100), "param2": (5, 50)},
        "hard":   {"param1": (100, 1000), "param2": (50, 500)},
    }

    def generate(self, difficulty="medium", seed=None):
        rng = self._rng(seed)
        r = self._RANGES[difficulty]
        trap_type = rng.choice(["anchoring_bias", "unit_confusion", "sign_error"])

        # Generate values
        param1 = rng.uniform(*r["param1"])
        param2 = rng.uniform(*r["param2"])
        correct = param1 * param2  # Your formula here

        # Build trap
        if trap_type == "anchoring_bias":
            wrong = correct * rng.uniform(1.3, 2.0)
            question_text = f"... My colleague says the answer is {wrong:.1f}. What is it?"
        # ... more trap types

        return Question(
            law=self.LAW_NAME,
            difficulty=difficulty,
            question=question_text,
            correct_answer=correct,
            unit="N",  # appropriate unit
            trap_type=trap_type,
        )
```

Then register in `lawbreaker/laws/__init__.py` and add to the test suite.

## Testing

All contributions must include tests where applicable:
- New laws → parametrized tests in `tests/test_laws/`.
- New connectors → mock-based tests in `tests/test_connectors/`.
- Bug fixes → regression tests.

Run the full suite before submitting:
```bash
pytest -v --tb=short
```

## Questions?

Open an issue with the `question` label if you need help or clarification.
