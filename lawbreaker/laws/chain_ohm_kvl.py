"""
Combined: Ohm's Law → Kirchhoff Voltage — series circuit voltage divider

Multi-step: Two resistors R1, R2 in series with voltage source V_total.
Find the voltage across R2.
Requires: I = V_total / (R1 + R2), then V2 = I × R2

Traps:
  1. unit_confusion: one resistor given in kΩ
  2. single_resistor_trap: phrased to make LLM use only R2 for current
  3. anchoring_bias: suggests a wrong voltage across R2
"""

from __future__ import annotations

from typing import Optional

from sympy import Rational, N as sympy_N

from lawbreaker.core.question import Question
from lawbreaker.laws.base import BaseLaw


class ChainOhmKVLLaw(BaseLaw):
    """Combined Ohm → KVL series circuit question generator."""

    LAW_NAME = "Ohm → Kirchhoff Voltage"

    _RANGES = {
        "easy": {"V": (6, 24), "R1": (1, 20), "R2": (1, 20)},
        "medium": {"V": (12, 120), "R1": (5, 100), "R2": (5, 100)},
        "hard": {"V": (24, 480), "R1": (10, 500), "R2": (10, 500)},
    }

    def generate(self, difficulty: str = "medium", seed: Optional[int] = None) -> Question:
        rng = self._rng(seed)
        ranges = self._RANGES.get(difficulty, self._RANGES["medium"])
        trap = rng.choice(["unit_confusion", "single_resistor_trap", "anchoring_bias"])

        V = round(rng.uniform(*ranges["V"]), 2)
        R1 = rng.randint(*ranges["R1"])
        R2 = rng.randint(*ranges["R2"])

        if trap == "unit_confusion":
            return self._unit_confusion(V, R1, R2, rng, difficulty)
        elif trap == "single_resistor_trap":
            return self._single_resistor(V, R1, R2, rng, difficulty)
        return self._anchoring(V, R1, R2, rng, difficulty)

    def _compute(self, V, R1, R2):
        I = float(sympy_N(Rational(str(V)) / (Rational(R1) + Rational(R2))))
        V2 = round(float(sympy_N(Rational(str(I)) * Rational(R2))), 4)
        return round(I, 6), V2

    def _unit_confusion(self, V, R1, R2, rng, difficulty):
        """Trap: R1 given in kΩ, R2 in Ω."""
        I, V2 = self._compute(V, R1, R2)
        R1_kOhm = round(R1 / 1000, 3)

        text = (
            f"Two resistors are connected in series to a {V}V source: "
            f"R₁ = {R1_kOhm} kΩ and R₂ = {R2} Ω. "
            f"Find the current through the circuit, then calculate "
            f"the voltage across R₂."
        )
        return Question(
            law=self.LAW_NAME, trap_type="unit_confusion", question_text=text,
            correct_answer=V2, correct_unit="V",
            variables={"V": V, "R1_ohm": R1, "R1_kOhm": R1_kOhm, "R2": R2},
            difficulty=difficulty,
            explanation=(
                f"Unit trap: R₁ = {R1_kOhm} kΩ = {R1} Ω. "
                f"Step 1: I = V/(R₁+R₂) = {V}/({R1}+{R2}) = {I} A. "
                f"Step 2: V₂ = IR₂ = {I}×{R2} = {V2} V."
            ),
        )

    def _single_resistor(self, V, R1, R2, rng, difficulty):
        """Trap: phrased to tempt using I = V/R2 instead of V/(R1+R2)."""
        I, V2 = self._compute(V, R1, R2)
        wrong_I = round(V / R2, 4)
        wrong_V2 = V  # would get full voltage

        text = (
            f"A {V}V battery is connected to resistors R₁ = {R1}Ω and R₂ = {R2}Ω "
            f"in series. What is the voltage drop across R₂? "
            f"(Hint: first find the current using Ohm's law.)"
        )
        return Question(
            law=self.LAW_NAME, trap_type="single_resistor_trap", question_text=text,
            correct_answer=V2, correct_unit="V",
            variables={"V": V, "R1": R1, "R2": R2, "wrong_I": wrong_I},
            difficulty=difficulty,
            explanation=(
                f"Single-resistor trap: LLMs may use I = V/R₂ = {V}/{R2} = {wrong_I} A. "
                f"Correct: I = V/(R₁+R₂) = {V}/({R1}+{R2}) = {I} A. "
                f"V₂ = IR₂ = {I}×{R2} = {V2} V."
            ),
        )

    def _anchoring(self, V, R1, R2, rng, difficulty):
        """Trap: suggest a wrong voltage across R2."""
        I, V2 = self._compute(V, R1, R2)
        wrong_V2 = round(V2 * rng.uniform(1.3, 2.5), 1)

        text = (
            f"In a series circuit with a {V}V supply, R₁ = {R1}Ω and R₂ = {R2}Ω. "
            f"A technician measured the voltage across R₂ as {wrong_V2}V. "
            f"Compute the actual voltage across R₂ by first finding the current."
        )
        return Question(
            law=self.LAW_NAME, trap_type="anchoring_bias", question_text=text,
            correct_answer=V2, correct_unit="V",
            variables={"V": V, "R1": R1, "R2": R2, "wrong_V2": wrong_V2},
            difficulty=difficulty,
            explanation=(
                f"Anchoring trap: {wrong_V2}V is wrong. "
                f"Step 1: I = V/(R₁+R₂) = {V}/({R1}+{R2}) = {I} A. "
                f"Step 2: V₂ = IR₂ = {I}×{R2} = {V2} V."
            ),
        )
