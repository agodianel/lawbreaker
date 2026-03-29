"""
Combined: Ohm's Law → Power — V=IR then P=V²/R

Multi-step: Given voltage V and resistance R, find the power dissipated.
Requires: I = V/R, then P = V × I = V²/R

Traps:
  1. unit_confusion: resistance in kΩ (must convert to Ω)
  2. intermediate_anchoring: suggests a wrong current to anchor the LLM
  3. anchoring_bias: suggests a wrong power value
"""

from __future__ import annotations

from typing import Optional

from sympy import Rational, N as sympy_N

from lawbreaker.core.question import Question
from lawbreaker.laws.base import BaseLaw


class ChainOhmPowerLaw(BaseLaw):
    """Combined Ohm → Power multi-step question generator."""

    LAW_NAME = "Ohm → Power"

    _RANGES = {
        "easy": {"V": (5, 24), "R": (1, 20)},
        "medium": {"V": (12, 240), "R": (5, 100)},
        "hard": {"V": (100, 480), "R": (10, 1000)},
    }

    def generate(self, difficulty: str = "medium", seed: Optional[int] = None) -> Question:
        rng = self._rng(seed)
        ranges = self._RANGES.get(difficulty, self._RANGES["medium"])
        trap = rng.choice(["unit_confusion", "intermediate_anchoring", "anchoring_bias"])

        V = round(rng.uniform(*ranges["V"]), 2)
        R = rng.randint(*ranges["R"])

        if trap == "unit_confusion":
            return self._unit_confusion(V, R, rng, difficulty)
        elif trap == "intermediate_anchoring":
            return self._intermediate_anchoring(V, R, rng, difficulty)
        return self._anchoring(V, R, rng, difficulty)

    def _unit_confusion(self, V: float, R: int, rng, difficulty: str) -> Question:
        """Trap: R given in kΩ — must convert before computing power."""
        I = float(sympy_N(Rational(str(V)) / Rational(R)))
        P = round(float(sympy_N(Rational(str(V)) * Rational(str(I)))), 4)
        R_kOhm = round(R / 1000, 3)

        text = (
            f"A {V}V source is connected to a {R_kOhm} kΩ resistor. "
            f"First determine the current through the resistor using Ohm's law, "
            f"then calculate the power dissipated in watts."
        )
        return Question(
            law=self.LAW_NAME, trap_type="unit_confusion", question_text=text,
            correct_answer=P, correct_unit="W",
            variables={"V": V, "R_ohm": R, "R_kOhm": R_kOhm},
            difficulty=difficulty,
            explanation=(
                f"Unit trap: {R_kOhm} kΩ = {R} Ω. "
                f"Step 1: I = V/R = {V}/{R} = {round(I, 4)} A. "
                f"Step 2: P = VI = {V} × {round(I, 4)} = {P} W."
            ),
        )

    def _intermediate_anchoring(self, V: float, R: int, rng, difficulty: str) -> Question:
        """Trap: suggest a wrong intermediate current value."""
        I = float(sympy_N(Rational(str(V)) / Rational(R)))
        P = round(float(sympy_N(Rational(str(V)) * Rational(str(I)))), 4)
        wrong_I = round(I * rng.uniform(1.5, 3.0), 2)
        wrong_P = round(V * wrong_I, 2)

        text = (
            f"A {R}Ω resistor is connected to a {V}V supply. "
            f"A student calculated the current as {wrong_I}A. "
            f"Using the correct current, what is the power dissipated?"
        )
        return Question(
            law=self.LAW_NAME, trap_type="intermediate_anchoring", question_text=text,
            correct_answer=P, correct_unit="W",
            variables={"V": V, "R": R, "wrong_I": wrong_I, "wrong_P": wrong_P},
            difficulty=difficulty,
            explanation=(
                f"Intermediate anchor: the student's I = {wrong_I}A is wrong. "
                f"Step 1: I = V/R = {V}/{R} = {round(I, 4)} A. "
                f"Step 2: P = VI = {V} × {round(I, 4)} = {P} W (not {wrong_P} W)."
            ),
        )

    def _anchoring(self, V: float, R: int, rng, difficulty: str) -> Question:
        """Trap: suggest a wrong final power value."""
        I = float(sympy_N(Rational(str(V)) / Rational(R)))
        P = round(float(sympy_N(Rational(str(V)) * Rational(str(I)))), 4)
        wrong_P = round(P * rng.uniform(1.3, 2.5), 1)

        text = (
            f"A {V}V battery drives current through a {R}Ω resistor. "
            f"An engineer estimates the power dissipation at {wrong_P}W. "
            f"Find the current first, then compute the actual power dissipated."
        )
        return Question(
            law=self.LAW_NAME, trap_type="anchoring_bias", question_text=text,
            correct_answer=P, correct_unit="W",
            variables={"V": V, "R": R, "wrong_P": wrong_P},
            difficulty=difficulty,
            explanation=(
                f"Anchoring trap: {wrong_P}W is wrong. "
                f"Step 1: I = V/R = {V}/{R} = {round(I, 4)} A. "
                f"Step 2: P = VI = {V} × {round(I, 4)} = {P} W."
            ),
        )
