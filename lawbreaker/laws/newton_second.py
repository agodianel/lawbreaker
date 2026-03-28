"""
Newton's Second Law — F = ma

Traps:
  1. weight_vs_mass: confuses weight (force due to gravity) with mass
  2. anchoring_bias: suggests a plausible-but-wrong force value
  3. unit_confusion: mixes kg and grams within the same question
"""

from __future__ import annotations

from typing import Optional

from sympy import Rational, N as sympy_N

from lawbreaker.core.question import Question
from lawbreaker.laws.base import BaseLaw


class NewtonSecondLaw(BaseLaw):
    """Newton's Second Law (F = ma) adversarial question generator."""

    LAW_NAME = "Newton's Second Law"

    _RANGES = {
        "easy": {"m": (1, 20), "a": (1, 10)},
        "medium": {"m": (5, 100), "a": (1, 30)},
        "hard": {"m": (10, 500), "a": (1, 50)},
    }

    def generate(self, difficulty: str = "medium", seed: Optional[int] = None) -> Question:
        """Generate an adversarial Newton's Second Law question.

        Args:
            difficulty: One of ``"easy"``, ``"medium"``, ``"hard"``.
            seed: Optional random seed.

        Returns:
            A ``Question`` with one of three trap types.
        """
        rng = self._rng(seed)
        ranges = self._RANGES.get(difficulty, self._RANGES["medium"])
        trap = rng.choice(["weight_vs_mass", "anchoring_bias", "unit_confusion"])

        m = round(rng.uniform(*ranges["m"]), 2)
        a = round(rng.uniform(*ranges["a"]), 2)

        if trap == "weight_vs_mass":
            return self._weight_vs_mass(m, a, rng, difficulty)
        elif trap == "anchoring_bias":
            return self._anchoring(m, a, rng, difficulty)
        else:
            return self._unit_confusion(m, a, rng, difficulty)

    def _weight_vs_mass(self, m: float, a: float, rng, difficulty: str) -> Question:
        """Trap 1: Give weight and ask for force — LLM may confuse mass and weight."""
        g = 9.81
        weight = round(m * g, 2)
        F_correct = round(float(sympy_N(Rational(str(m)) * Rational(str(a)))), 4)

        text = (
            f"An object has a mass of {m}kg (weight = {weight}N on Earth). "
            f"It accelerates at {a} m/s². "
            f"What is the net force applied to the object?"
        )
        return Question(
            law=self.LAW_NAME,
            trap_type="weight_vs_mass",
            question_text=text,
            correct_answer=F_correct,
            correct_unit="N",
            variables={"m": m, "a": a, "weight": weight, "g": g},
            difficulty=difficulty,
            explanation=(
                f"Weight vs mass trap: the weight {weight}N is a distractor. "
                f"F = ma = {m} × {a} = {F_correct}N."
            ),
        )

    def _anchoring(self, m: float, a: float, rng, difficulty: str) -> Question:
        """Trap 2: Suggest a wrong force to anchor the LLM."""
        F_correct = round(float(sympy_N(Rational(str(m)) * Rational(str(a)))), 4)
        wrong_F = round(F_correct * rng.uniform(1.5, 3.0), 1)

        text = (
            f"A {m}kg object accelerates at {a} m/s². "
            f"A textbook example suggests the force should be around {wrong_F}N. "
            f"What is the actual net force?"
        )
        return Question(
            law=self.LAW_NAME,
            trap_type="anchoring_bias",
            question_text=text,
            correct_answer=F_correct,
            correct_unit="N",
            variables={"m": m, "a": a, "wrong_F": wrong_F},
            difficulty=difficulty,
            explanation=(
                f"Anchoring trap: the textbook value {wrong_F}N is wrong. "
                f"F = ma = {m} × {a} = {F_correct}N."
            ),
        )

    def _unit_confusion(self, m: float, a: float, rng, difficulty: str) -> Question:
        """Trap 3: Mass given in grams, not kilograms."""
        m_grams = round(m * 1000, 2)
        F_correct = round(float(sympy_N(Rational(str(m)) * Rational(str(a)))), 4)

        text = (
            f"An object with a mass of {m_grams}g accelerates at {a} m/s². "
            f"What is the net force in Newtons?"
        )
        return Question(
            law=self.LAW_NAME,
            trap_type="unit_confusion",
            question_text=text,
            correct_answer=F_correct,
            correct_unit="N",
            variables={"m_kg": m, "m_grams": m_grams, "a": a},
            difficulty=difficulty,
            explanation=(
                f"Unit confusion trap: mass is {m_grams}g = {m}kg. "
                f"F = ma = {m} × {a} = {F_correct}N. "
                f"Using grams directly would give {round(m_grams * a, 4)}, which is wrong."
            ),
        )
