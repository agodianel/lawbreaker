"""
Tests for Newton's Second Law — generate 20 questions and verify correct_answer.
"""

import pytest
from lawbreaker.laws.newton_second import NewtonSecondLaw


class TestNewtonSecondLaw:
    """Verify Newton's Second Law question generation produces correct answers."""

    @pytest.fixture
    def law(self):
        """Return a NewtonSecondLaw instance."""
        return NewtonSecondLaw()

    def test_generate_20_questions(self, law):
        """Generate 20 seeded questions and verify each correct_answer."""
        for seed in range(20):
            q = law.generate(difficulty="medium", seed=seed)
            assert q.law == "Newton's Second Law"
            assert q.trap_type in ("weight_vs_mass", "anchoring_bias", "unit_confusion")
            assert q.correct_answer > 0
            assert q.correct_unit == "N"
            assert q.question_text
            assert q.explanation

            # Re-verify: F = ma (mass in kg × acceleration)
            if "m_kg" in q.variables:
                m = q.variables["m_kg"]
            elif "m" in q.variables:
                m = q.variables["m"]
            else:
                continue
            a = q.variables["a"]
            expected = m * a
            assert abs(q.correct_answer - expected) / expected < 0.01

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
            assert q.correct_answer > 0

    def test_verify_correct(self, law):
        """Verify method returns True for the correct answer."""
        q = law.generate(seed=7)
        assert law.verify(q.correct_answer, q) is True

    def test_verify_wrong(self, law):
        """Verify method returns False for a clearly wrong answer."""
        q = law.generate(seed=7)
        assert law.verify(q.correct_answer * 10, q) is False
