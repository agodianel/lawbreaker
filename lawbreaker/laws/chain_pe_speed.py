"""
Combined: Gravitational PE → Speed — mgh = ½mv²

Multi-step: Object dropped from height h, find speed at ground level.
Requires: mgh = ½mv² → v = √(2gh)  (mass cancels)

Traps:
  1. mass_distractor: mass is given but cancels — LLM may try to use it
  2. height_unit_confusion: height given in cm instead of m
  3. missing_sqrt: phrased so LLM forgets the square root
"""

from __future__ import annotations

import math
from typing import Optional

from sympy import Rational, sqrt as sym_sqrt, N as sympy_N

from lawbreaker.core.question import Question
from lawbreaker.laws.base import BaseLaw


class ChainPESpeedLaw(BaseLaw):
    """Combined PE → Speed multi-step question generator."""

    LAW_NAME = "PE → Speed"
    G = 9.81

    _RANGES = {
        "easy": {"h": (1, 10), "m": (1, 10)},
        "medium": {"h": (5, 50), "m": (1, 100)},
        "hard": {"h": (10, 200), "m": (5, 500)},
    }

    def generate(self, difficulty: str = "medium", seed: Optional[int] = None) -> Question:
        rng = self._rng(seed)
        ranges = self._RANGES.get(difficulty, self._RANGES["medium"])
        trap = rng.choice(["mass_distractor", "height_unit_confusion", "missing_sqrt"])

        h = round(rng.uniform(*ranges["h"]), 2)
        m = round(rng.uniform(*ranges["m"]), 2)

        if trap == "mass_distractor":
            return self._mass_distractor(h, m, rng, difficulty)
        elif trap == "height_unit_confusion":
            return self._height_confusion(h, m, rng, difficulty)
        return self._missing_sqrt(h, m, rng, difficulty)

    def _speed(self, h):
        """v = sqrt(2gh)"""
        return round(float(sympy_N(sym_sqrt(2 * Rational(str(self.G)) * Rational(str(h))))), 4)

    def _mass_distractor(self, h, m, rng, difficulty):
        """Trap: mass is given prominently but cancels in the derivation."""
        v = self._speed(h)
        PE = round(m * self.G * h, 4)

        text = (
            f"A {m}kg ball is dropped from a height of {h}m. "
            f"Its gravitational potential energy at the top is {PE}J. "
            f"Using energy conservation, what is its speed just before "
            f"hitting the ground? (Ignore air resistance.)"
        )
        return Question(
            law=self.LAW_NAME, trap_type="mass_distractor", question_text=text,
            correct_answer=v, correct_unit="m/s",
            variables={"h": h, "m": m, "PE": PE},
            difficulty=difficulty,
            explanation=(
                f"Mass distractor: mass cancels! mgh = ½mv² → v = √(2gh). "
                f"v = √(2 × {self.G} × {h}) = {v} m/s. "
                f"The mass {m}kg and PE {PE}J are distractors."
            ),
        )

    def _height_confusion(self, h, m, rng, difficulty):
        """Trap: height given in centimeters."""
        v = self._speed(h)
        h_cm = round(h * 100, 2)

        text = (
            f"A {m}kg object falls from a height of {h_cm} cm. "
            f"Using conservation of energy (PE converts to KE), "
            f"what is its speed in m/s just before impact?"
        )
        return Question(
            law=self.LAW_NAME, trap_type="height_unit_confusion", question_text=text,
            correct_answer=v, correct_unit="m/s",
            variables={"h_m": h, "h_cm": h_cm, "m": m},
            difficulty=difficulty,
            explanation=(
                f"Height unit trap: {h_cm} cm = {h} m. "
                f"v = √(2gh) = √(2 × {self.G} × {h}) = {v} m/s."
            ),
        )

    def _missing_sqrt(self, h, m, rng, difficulty):
        """Trap: phrasing nudges LLM to compute 2gh without the sqrt."""
        v = self._speed(h)
        v_squared = round(2 * self.G * h, 4)

        text = (
            f"A {m}kg object is dropped from {h}m. By energy conservation, "
            f"the speed squared equals twice the product of g and h. "
            f"What is the final speed in m/s?"
        )
        return Question(
            law=self.LAW_NAME, trap_type="missing_sqrt", question_text=text,
            correct_answer=v, correct_unit="m/s",
            variables={"h": h, "m": m, "v_squared": v_squared},
            difficulty=difficulty,
            explanation=(
                f"Missing-sqrt trap: v² = 2gh = {v_squared}, but the question asks "
                f"for speed, not speed squared. v = √{v_squared} = {v} m/s."
            ),
        )
