"""
Combined: Hooke's Law → Kinetic Energy — ½kx² = ½mv²

Multi-step: Spring with constant k compressed by x launches mass m.
Find the launch speed.
Requires: ½kx² = ½mv² → v = x√(k/m)

Traps:
  1. unit_confusion: compression given in cm
  2. missing_sqrt: phrased to make LLM compute kx²/m without sqrt
  3. anchoring_bias: suggests a wrong launch speed
"""

from __future__ import annotations

from typing import Optional

from sympy import Rational, sqrt as sym_sqrt, N as sympy_N

from lawbreaker.core.question import Question
from lawbreaker.laws.base import BaseLaw


class ChainSpringLaunchLaw(BaseLaw):
    """Combined Spring → KE launch speed question generator."""

    LAW_NAME = "Spring → Speed"

    _RANGES = {
        "easy": {"k": (50, 500), "x": (0.01, 0.1), "m": (0.1, 2)},
        "medium": {"k": (100, 2000), "x": (0.02, 0.3), "m": (0.5, 10)},
        "hard": {"k": (500, 10000), "x": (0.05, 0.5), "m": (1, 50)},
    }

    def generate(self, difficulty: str = "medium", seed: Optional[int] = None) -> Question:
        rng = self._rng(seed)
        ranges = self._RANGES.get(difficulty, self._RANGES["medium"])
        trap = rng.choice(["unit_confusion", "missing_sqrt", "anchoring_bias"])

        k = round(rng.uniform(*ranges["k"]), 1)
        x = round(rng.uniform(*ranges["x"]), 3)
        m = round(rng.uniform(*ranges["m"]), 2)

        if trap == "unit_confusion":
            return self._unit_confusion(k, x, m, rng, difficulty)
        elif trap == "missing_sqrt":
            return self._missing_sqrt(k, x, m, rng, difficulty)
        return self._anchoring(k, x, m, rng, difficulty)

    def _speed(self, k, x, m):
        """v = x * sqrt(k/m) = sqrt(kx²/m)"""
        return round(float(sympy_N(
            sym_sqrt(Rational(str(k)) * Rational(str(x)) ** 2 / Rational(str(m)))
        )), 4)

    def _unit_confusion(self, k, x, m, rng, difficulty):
        """Trap: compression given in cm instead of m."""
        v = self._speed(k, x, m)
        x_cm = round(x * 100, 2)

        text = (
            f"A spring with constant k = {k} N/m is compressed by {x_cm} cm. "
            f"It launches a {m}kg ball. First find the elastic potential energy "
            f"stored in the spring, then determine the launch speed of the ball."
        )
        return Question(
            law=self.LAW_NAME, trap_type="unit_confusion", question_text=text,
            correct_answer=v, correct_unit="m/s",
            variables={"k": k, "x_m": x, "x_cm": x_cm, "m": m},
            difficulty=difficulty,
            explanation=(
                f"Unit trap: {x_cm} cm = {x} m. "
                f"Step 1: PE = ½kx² = ½×{k}×{x}² = {round(0.5*k*x**2, 4)} J. "
                f"Step 2: ½mv² = PE → v = √(kx²/m) = {v} m/s."
            ),
        )

    def _missing_sqrt(self, k, x, m, rng, difficulty):
        """Trap: phrased to make LLM compute kx²/m without taking sqrt."""
        v = self._speed(k, x, m)
        v_squared = round(k * x ** 2 / m, 4)

        text = (
            f"A {m}kg mass sits against a spring (k = {k} N/m) compressed {x}m. "
            f"The spring launches the mass. The speed squared equals kx²/m. "
            f"What is the launch speed in m/s?"
        )
        return Question(
            law=self.LAW_NAME, trap_type="missing_sqrt", question_text=text,
            correct_answer=v, correct_unit="m/s",
            variables={"k": k, "x": x, "m": m, "v_squared": v_squared},
            difficulty=difficulty,
            explanation=(
                f"Missing-sqrt trap: v² = kx²/m = {v_squared}. "
                f"Question asks for speed, not speed squared. v = √{v_squared} = {v} m/s."
            ),
        )

    def _anchoring(self, k, x, m, rng, difficulty):
        """Trap: suggest a wrong launch speed."""
        v = self._speed(k, x, m)
        wrong_v = round(v * rng.uniform(1.5, 3.0), 2)

        text = (
            f"A spring (k = {k} N/m) is compressed {x}m and releases a {m}kg object. "
            f"An estimate puts the launch speed at {wrong_v} m/s. "
            f"Calculate the elastic PE first, then find the actual launch speed."
        )
        return Question(
            law=self.LAW_NAME, trap_type="anchoring_bias", question_text=text,
            correct_answer=v, correct_unit="m/s",
            variables={"k": k, "x": x, "m": m, "wrong_v": wrong_v},
            difficulty=difficulty,
            explanation=(
                f"Anchoring trap: {wrong_v} m/s is wrong. "
                f"PE = ½kx² = {round(0.5*k*x**2, 4)} J. "
                f"v = √(kx²/m) = {v} m/s."
            ),
        )
