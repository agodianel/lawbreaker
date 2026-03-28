"""
Simple Pendulum Period — T = 2π√(L/g)

Traps:
  1. forget_sqrt: uses L/g instead of √(L/g)
  2. unit_confusion: length in cm vs m
  3. mass_distractor: includes mass as a red herring (period is mass-independent)
"""

from __future__ import annotations

import math
from typing import Optional

from lawbreaker.core.question import Question
from lawbreaker.laws.base import BaseLaw


class PendulumLaw(BaseLaw):
    """Simple Pendulum (T = 2π√(L/g)) adversarial question generator."""

    LAW_NAME = "Pendulum Period"
    G = 9.81

    _RANGES = {
        "easy": {"L": (0.5, 3.0)},
        "medium": {"L": (0.1, 10.0)},
        "hard": {"L": (0.01, 50.0)},
    }

    def generate(self, difficulty: str = "medium", seed: Optional[int] = None) -> Question:
        """Generate an adversarial pendulum period question."""
        rng = self._rng(seed)
        ranges = self._RANGES.get(difficulty, self._RANGES["medium"])
        trap = rng.choice(["forget_sqrt", "unit_confusion", "mass_distractor"])

        L = round(rng.uniform(*ranges["L"]), 3)

        if trap == "forget_sqrt":
            return self._forget_sqrt(L, rng, difficulty)
        elif trap == "unit_confusion":
            return self._unit_confusion(L, rng, difficulty)
        return self._mass_distractor(L, rng, difficulty)

    def _forget_sqrt(self, L, rng, difficulty):
        """Trap 1: Tempts LLM to use T = 2πL/g instead of T = 2π√(L/g)."""
        T = round(2 * math.pi * math.sqrt(L / self.G), 4)
        wrong_T = round(2 * math.pi * L / self.G, 4)

        text = (
            f"A pendulum has length {L}m. A student calculates "
            f"T = 2πL/g = {wrong_T}s. What is the correct period in seconds?"
        )
        return Question(
            law=self.LAW_NAME, trap_type="forget_sqrt", question_text=text,
            correct_answer=T, correct_unit="s",
            variables={"L": L, "g": self.G},
            difficulty=difficulty,
            explanation=f"T = 2π√(L/g), not 2πL/g. T = 2π√({L}/{self.G}) = {T}s.",
        )

    def _unit_confusion(self, L, rng, difficulty):
        """Trap 2: Length in cm instead of m."""
        T = round(2 * math.pi * math.sqrt(L / self.G), 4)
        L_cm = round(L * 100, 1)

        text = (
            f"A simple pendulum is {L_cm}cm long. "
            f"What is its period in seconds? (g = {self.G} m/s²)"
        )
        return Question(
            law=self.LAW_NAME, trap_type="unit_confusion", question_text=text,
            correct_answer=T, correct_unit="s",
            variables={"L_m": L, "L_cm": L_cm, "g": self.G},
            difficulty=difficulty,
            explanation=f"{L_cm}cm = {L}m. T = 2π√({L}/{self.G}) = {T}s.",
        )

    def _mass_distractor(self, L, rng, difficulty):
        """Trap 3: Includes mass as a distractor (period is independent of mass)."""
        T = round(2 * math.pi * math.sqrt(L / self.G), 4)
        m = round(rng.uniform(0.1, 10), 2)

        text = (
            f"A pendulum bob of mass {m}kg hangs from a {L}m string. "
            f"What is the period in seconds? (g = {self.G} m/s²)"
        )
        return Question(
            law=self.LAW_NAME, trap_type="mass_distractor", question_text=text,
            correct_answer=T, correct_unit="s",
            variables={"L": L, "m": m, "g": self.G},
            difficulty=difficulty,
            explanation=f"Period is independent of mass. T = 2π√(L/g) = {T}s. "
                        f"The mass {m}kg is irrelevant.",
        )
