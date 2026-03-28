"""
Hooke's Law — F = kx

Traps:
  1. sign_confusion: spring force direction vs magnitude
  2. unit_confusion: cm vs m for displacement
  3. anchoring_bias: suggests a plausible but wrong force
"""

from __future__ import annotations

from typing import Optional

from sympy import Rational, N as sympy_N

from lawbreaker.core.question import Question
from lawbreaker.laws.base import BaseLaw


class HookeLaw(BaseLaw):
    """Hooke's Law (F = kx) adversarial question generator."""

    LAW_NAME = "Hooke's Law"

    _RANGES = {
        "easy": {"k": (10, 100), "x": (0.01, 0.5)},
        "medium": {"k": (50, 500), "x": (0.01, 1.0)},
        "hard": {"k": (100, 5000), "x": (0.001, 2.0)},
    }

    def generate(self, difficulty: str = "medium", seed: Optional[int] = None) -> Question:
        """Generate an adversarial Hooke's Law question."""
        rng = self._rng(seed)
        ranges = self._RANGES.get(difficulty, self._RANGES["medium"])
        trap = rng.choice(["sign_confusion", "unit_confusion", "anchoring_bias"])

        k = rng.randint(*ranges["k"])
        x = round(rng.uniform(*ranges["x"]), 4)

        if trap == "sign_confusion":
            return self._sign_confusion(k, x, rng, difficulty)
        elif trap == "unit_confusion":
            return self._unit_confusion(k, x, rng, difficulty)
        return self._anchoring(k, x, rng, difficulty)

    def _sign_confusion(self, k, x, rng, difficulty):
        """Trap 1: Asks for magnitude but mentions restoring force direction."""
        F = round(float(sympy_N(Rational(k) * Rational(str(x)))), 4)

        text = (
            f"A spring with spring constant {k} N/m is stretched {x}m from "
            f"equilibrium. The restoring force acts in the negative direction. "
            f"What is the magnitude of the spring force in Newtons?"
        )
        return Question(
            law=self.LAW_NAME, trap_type="sign_confusion", question_text=text,
            correct_answer=F, correct_unit="N",
            variables={"k": k, "x": x},
            difficulty=difficulty,
            explanation=f"Magnitude is |F| = kx = {k} × {x} = {F}N. "
                        f"The negative sign indicates direction, not magnitude.",
        )

    def _unit_confusion(self, k, x, rng, difficulty):
        """Trap 2: Displacement given in cm but spring constant in N/m."""
        x_cm = round(x * 100, 2)
        F = round(float(sympy_N(Rational(k) * Rational(str(x)))), 4)

        text = (
            f"A spring has a constant of {k} N/m. It is compressed by {x_cm} cm. "
            f"What is the force exerted by the spring in Newtons?"
        )
        return Question(
            law=self.LAW_NAME, trap_type="unit_confusion", question_text=text,
            correct_answer=F, correct_unit="N",
            variables={"k": k, "x_m": x, "x_cm": x_cm},
            difficulty=difficulty,
            explanation=f"Convert {x_cm}cm = {x}m. F = kx = {k} × {x} = {F}N. "
                        f"Using cm directly gives {round(k * x_cm, 4)}N (wrong).",
        )

    def _anchoring(self, k, x, rng, difficulty):
        """Trap 3: A colleague suggests the wrong force value."""
        F = round(float(sympy_N(Rational(k) * Rational(str(x)))), 4)
        wrong_F = round(F * rng.uniform(1.5, 3.0), 2)

        text = (
            f"A spring (k = {k} N/m) is extended by {x}m. A lab partner "
            f"calculated the force as {wrong_F}N. What is the correct force?"
        )
        return Question(
            law=self.LAW_NAME, trap_type="anchoring_bias", question_text=text,
            correct_answer=F, correct_unit="N",
            variables={"k": k, "x": x, "wrong_F": wrong_F},
            difficulty=difficulty,
            explanation=f"F = kx = {k} × {x} = {F}N, not {wrong_F}N.",
        )
