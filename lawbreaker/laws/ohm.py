"""
Ohm's Law — V = IR

Traps:
  1. anchoring_bias: provides a plausible-but-wrong voltage from a "colleague"
  2. unit_confusion: mixes mA and A within the same question
  3. reversed_question: gives V and R, asks for I, but anchors to a wrong I
"""

from __future__ import annotations

from typing import Optional

from sympy import Rational, N as sympy_N

from lawbreaker.core.question import Question
from lawbreaker.laws.base import BaseLaw


class OhmLaw(BaseLaw):
    """Ohm's Law (V = IR) adversarial question generator."""

    LAW_NAME = "Ohm's Law"

    # Difficulty → parameter ranges
    _RANGES = {
        "easy": {"R": (1, 20), "I": (1, 10)},
        "medium": {"R": (5, 100), "I": (1, 50)},
        "hard": {"R": (10, 1000), "I": (1, 100)},
    }

    def generate(self, difficulty: str = "medium", seed: Optional[int] = None) -> Question:
        """Generate an adversarial Ohm's Law question.

        Args:
            difficulty: One of ``"easy"``, ``"medium"``, ``"hard"``.
            seed: Optional random seed.

        Returns:
            A ``Question`` with one of three trap types embedded.
        """
        rng = self._rng(seed)
        ranges = self._RANGES.get(difficulty, self._RANGES["medium"])
        trap = rng.choice(["anchoring_bias", "unit_confusion", "reversed_question"])

        R = rng.randint(*ranges["R"])
        I = round(rng.uniform(*ranges["I"]), 2)

        if trap == "anchoring_bias":
            return self._anchoring(R, I, rng, difficulty)
        elif trap == "unit_confusion":
            return self._unit_confusion(R, I, rng, difficulty)
        else:
            return self._reversed(R, I, rng, difficulty)

    # ------------------------------------------------------------------
    # Trap implementations
    # ------------------------------------------------------------------

    def _anchoring(self, R: int, I: float, rng, difficulty: str) -> Question:
        """Trap 1: Colleague suggests a wrong voltage to anchor the LLM."""
        V_correct = float(sympy_N(Rational(R) * Rational(str(I))))
        wrong_V = round(V_correct * rng.uniform(1.3, 2.5), 1)

        text = (
            f"A {R}Ω resistor carries a current of {I}A. "
            f"My colleague calculated the voltage drop as {wrong_V}V. "
            f"What is the actual voltage across the resistor?"
        )
        return Question(
            law=self.LAW_NAME,
            trap_type="anchoring_bias",
            question_text=text,
            correct_answer=round(V_correct, 4),
            correct_unit="V",
            variables={"R": R, "I": I, "wrong_V": wrong_V},
            difficulty=difficulty,
            explanation=(
                f"Anchoring trap: the colleague's value {wrong_V}V is wrong. "
                f"V = IR = {R} × {I} = {round(V_correct, 4)}V."
            ),
        )

    def _unit_confusion(self, R: int, I: float, rng, difficulty: str) -> Question:
        """Trap 2: Current given in milliamps but labelled ambiguously."""
        I_mA = round(I * 1000, 2)
        V_correct = float(sympy_N(Rational(R) * Rational(str(I))))

        text = (
            f"A resistor has a resistance of {R}Ω. The current flowing through it "
            f"is {I_mA} mA. What is the voltage across the resistor in volts?"
        )
        return Question(
            law=self.LAW_NAME,
            trap_type="unit_confusion",
            question_text=text,
            correct_answer=round(V_correct, 4),
            correct_unit="V",
            variables={"R": R, "I_mA": I_mA, "I_A": I},
            difficulty=difficulty,
            explanation=(
                f"Unit confusion trap: current is {I_mA} mA = {I} A. "
                f"V = IR = {R} × {I} = {round(V_correct, 4)}V. "
                f"LLMs often use the mA value directly, giving {R * I_mA}V."
            ),
        )

    def _reversed(self, R: int, I: float, rng, difficulty: str) -> Question:
        """Trap 3: Give V and R, ask for I, but suggest a wrong answer."""
        V = float(sympy_N(Rational(R) * Rational(str(I))))
        I_correct = I
        wrong_I = round(I_correct * rng.uniform(1.5, 3.0), 2)

        text = (
            f"The voltage across a {R}Ω resistor is {round(V, 2)}V. "
            f"A student claims the current is {wrong_I}A. "
            f"What is the actual current through the resistor?"
        )
        return Question(
            law=self.LAW_NAME,
            trap_type="reversed_question",
            question_text=text,
            correct_answer=round(I_correct, 4),
            correct_unit="A",
            variables={"R": R, "V": round(V, 2), "wrong_I": wrong_I},
            difficulty=difficulty,
            explanation=(
                f"Reversed question with anchor: I = V/R = {round(V, 2)}/{R} = "
                f"{round(I_correct, 4)}A, not {wrong_I}A."
            ),
        )
