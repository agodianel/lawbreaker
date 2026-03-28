"""
Centripetal Force — F = mv²/r

Traps:
  1. missing_v_squared: uses v instead of v²
  2. unit_confusion: radius in cm vs m
  3. anchoring_bias: suggests a wrong force value
"""

from __future__ import annotations

from typing import Optional

from lawbreaker.core.question import Question
from lawbreaker.laws.base import BaseLaw


class CentripetalForceLaw(BaseLaw):
    """Centripetal Force (F = mv²/r) adversarial question generator."""

    LAW_NAME = "Centripetal Force"

    _RANGES = {
        "easy": {"m": (0.5, 10), "v": (1, 10), "r": (0.5, 5)},
        "medium": {"m": (1, 100), "v": (2, 30), "r": (0.5, 20)},
        "hard": {"m": (10, 1000), "v": (5, 100), "r": (1, 100)},
    }

    def generate(self, difficulty: str = "medium", seed: Optional[int] = None) -> Question:
        """Generate an adversarial centripetal force question."""
        rng = self._rng(seed)
        ranges = self._RANGES.get(difficulty, self._RANGES["medium"])
        trap = rng.choice(["missing_v_squared", "unit_confusion", "anchoring_bias"])

        m = round(rng.uniform(*ranges["m"]), 2)
        v = round(rng.uniform(*ranges["v"]), 2)
        r = round(rng.uniform(*ranges["r"]), 2)

        if trap == "missing_v_squared":
            return self._missing_v_squared(m, v, r, rng, difficulty)
        elif trap == "unit_confusion":
            return self._unit_confusion(m, v, r, rng, difficulty)
        return self._anchoring(m, v, r, rng, difficulty)

    def _missing_v_squared(self, m, v, r, rng, difficulty):
        """Trap 1: Tempts using mv/r instead of mv²/r."""
        F = round(m * v**2 / r, 4)
        wrong_F = round(m * v / r, 4)

        text = (
            f"An object of mass {m}kg moves in a circle of radius {r}m "
            f"at speed {v} m/s. A student calculates F = mv/r = {wrong_F}N. "
            f"What is the correct centripetal force in N?"
        )
        return Question(
            law=self.LAW_NAME, trap_type="missing_v_squared", question_text=text,
            correct_answer=F, correct_unit="N",
            variables={"m": m, "v": v, "r": r},
            difficulty=difficulty,
            explanation=f"F = mv²/r, not mv/r. F = {m}×{v}²/{r} = {F}N.",
        )

    def _unit_confusion(self, m, v, r, rng, difficulty):
        """Trap 2: Radius in cm but formula needs metres."""
        r_cm = round(r * 100, 1)
        F = round(m * v**2 / r, 4)

        text = (
            f"A {m}kg mass moves at {v} m/s in a circle of radius {r_cm} cm. "
            f"What is the centripetal force in Newtons?"
        )
        return Question(
            law=self.LAW_NAME, trap_type="unit_confusion", question_text=text,
            correct_answer=F, correct_unit="N",
            variables={"m": m, "v": v, "r_m": r, "r_cm": r_cm},
            difficulty=difficulty,
            explanation=f"{r_cm}cm = {r}m. F = mv²/r = {m}×{v}²/{r} = {F}N.",
        )

    def _anchoring(self, m, v, r, rng, difficulty):
        """Trap 3: Suggest a plausible but wrong force."""
        F = round(m * v**2 / r, 4)
        wrong_F = round(F * rng.uniform(1.4, 2.5), 2)

        text = (
            f"A {m}kg object orbits at {v} m/s with radius {r}m. "
            f"An online calculator reports the force as {wrong_F}N. "
            f"What is the actual centripetal force?"
        )
        return Question(
            law=self.LAW_NAME, trap_type="anchoring_bias", question_text=text,
            correct_answer=F, correct_unit="N",
            variables={"m": m, "v": v, "r": r, "wrong_F": wrong_F},
            difficulty=difficulty,
            explanation=f"F = mv²/r = {m}×{v}²/{r} = {F}N, not {wrong_F}N.",
        )
