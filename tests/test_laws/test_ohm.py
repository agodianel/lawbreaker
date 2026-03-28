"""
Tests for Ohm's Law — generate 20 questions and verify correct_answer.
"""

import pytest
from lawbreaker.laws.ohm import OhmLaw


class TestOhmLaw:
    """Verify Ohm's Law question generation produces correct answers."""

    @pytest.fixture
    def law(self):
        """Return an OhmLaw instance."""
        return OhmLaw()

    def test_generate_20_questions(self, law):
        """Generate 20 seeded questions and verify each correct_answer."""
        for seed in range(20):
            q = law.generate(difficulty="medium", seed=seed)
            assert q.law == "Ohm's Law"
            assert q.trap_type in ("anchoring_bias", "unit_confusion", "reversed_question")
            assert q.correct_answer != 0
            assert q.correct_unit in ("V", "A")
            assert q.question_text
            assert q.explanation

            # Re-verify the answer from variables
            if q.trap_type in ("anchoring_bias", "unit_confusion"):
                if "I_A" in q.variables:
                    expected = q.variables["R"] * q.variables["I_A"]
                elif "I" in q.variables:
                    expected = q.variables["R"] * q.variables["I"]
                else:
                    continue
                assert abs(q.correct_answer - expected) < 0.01

            elif q.trap_type == "reversed_question":
                expected = q.variables["V"] / q.variables["R"]
                assert abs(q.correct_answer - expected) < 0.01

    def test_reproducibility(self, law):
        """Same seed produces identical questions."""
        q1 = law.generate(seed=42)
        q2 = law.generate(seed=42)
        assert q1.correct_answer == q2.correct_answer
        assert q1.question_text == q2.question_text

    def test_difficulty_levels(self, law):
        """All difficulty levels produce valid questions."""
        for diff in ("easy", "medium", "hard"):
            q = law.generate(difficulty=diff, seed=100)
            assert q.difficulty == diff
            assert q.correct_answer != 0

    def test_verify_correct(self, law):
        """Verify method returns True for the correct answer."""
        q = law.generate(seed=7)
        assert law.verify(q.correct_answer, q) is True

    def test_verify_wrong(self, law):
        """Verify method returns False for a clearly wrong answer."""
        q = law.generate(seed=7)
        assert law.verify(q.correct_answer * 5, q) is False
