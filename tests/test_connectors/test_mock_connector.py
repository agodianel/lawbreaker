"""
Mock connector tests — verify the runner correctly scores 0% and 100%.

Uses a MockConnector that returns configurable answers to exercise
the full pipeline (generate → query → extract → verify → report).
"""

import pytest

from lawbreaker.connectors.base import BaseConnector, SYSTEM_PROMPT
from lawbreaker.core.question import Question
from lawbreaker.runner import BenchmarkRunner


class MockConnectorWrong(BaseConnector):
    """Mock connector that always returns a wrong answer."""

    @property
    def model_name(self) -> str:
        """Return mock model name."""
        return "mock-wrong"

    def query(self, question_text: str, system_prompt: str = SYSTEM_PROMPT) -> str:
        """Return an answer that is always wrong (a huge number)."""
        return "999999999.99 X"


class MockConnectorPerfect(BaseConnector):
    """Mock connector that returns the correct answer.

    Requires being given the correct answer before each query.
    """

    def __init__(self):
        """Initialise with no pending answer."""
        self._answer: str = "0"

    def set_answer(self, value: float, unit: str):
        """Set the answer to return on next query.

        Args:
            value: Numeric answer.
            unit: Unit string.
        """
        self._answer = f"{value} {unit}"

    @property
    def model_name(self) -> str:
        """Return mock model name."""
        return "mock-perfect"

    def query(self, question_text: str, system_prompt: str = SYSTEM_PROMPT) -> str:
        """Return the pre-set correct answer."""
        return self._answer


class TestMockConnectorWrong:
    """Verify that a wrong-answer connector scores 0%."""

    def test_all_fail(self):
        """Run benchmark with wrong answers — every question should fail."""
        connector = MockConnectorWrong()
        runner = BenchmarkRunner(
            connector=connector,
            laws=["ohm"],
            n_questions=5,
            seed=42,
        )
        report = runner.run()
        assert report.total_passed == 0
        assert report.overall_score == 0.0
        assert report.model_name == "mock-wrong"
        assert report.total_questions == 5
        for qr in report.questions:
            assert qr.passed is False


class TestMockConnectorPerfect:
    """Verify that a perfect-answer connector scores 100%."""

    def test_all_pass(self):
        """Run individual questions with correct answers — all should pass."""
        connector = MockConnectorPerfect()
        runner = BenchmarkRunner(
            connector=connector,
            laws=["ohm"],
            n_questions=5,
            seed=42,
        )
        # Generate questions and run them one by one with correct answers
        from lawbreaker.laws.ohm import OhmLaw
        import random

        law = OhmLaw()
        rng = random.Random(42)
        results = []
        for i in range(5):
            q_seed = rng.randint(0, 2**31)
            difficulty = rng.choice(["easy", "medium", "hard"])
            q = law.generate(difficulty=difficulty, seed=q_seed)
            connector.set_answer(q.correct_answer, q.correct_unit)
            result = runner.run_single(q)
            results.append(result)
            assert result.passed is True, (
                f"Question {i} failed: expected {q.correct_answer}, "
                f"got {result.extracted_answer}"
            )

        assert all(r.passed for r in results)
