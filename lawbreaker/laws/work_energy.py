"""
Work–Energy Theorem — W = Fd cosθ

Traps:
  1. missing_cos_theta: ignores angle, uses W = Fd
  2. angle_in_radians: θ given in degrees but used as radians
  3. unit_confusion: force in kN vs N
"""

from __future__ import annotations

import math
from typing import Optional

from lawbreaker.core.question import Question
from lawbreaker.laws.base import BaseLaw


class WorkEnergyLaw(BaseLaw):
    """Work–Energy Theorem (W = Fd cosθ) adversarial question generator."""

    LAW_NAME = "Work-Energy Theorem"

    _RANGES = {
        "easy": {"F": (10, 100), "d": (1, 10), "theta": (0, 60)},
        "medium": {"F": (10, 500), "d": (1, 50), "theta": (0, 75)},
        "hard": {"F": (50, 5000), "d": (1, 200), "theta": (0, 85)},
    }

    def generate(self, difficulty: str = "medium", seed: Optional[int] = None) -> Question:
        """Generate an adversarial work-energy question."""
        rng = self._rng(seed)
        ranges = self._RANGES.get(difficulty, self._RANGES["medium"])
        trap = rng.choice(["missing_cos_theta", "angle_in_radians", "unit_confusion"])

        F = round(rng.uniform(*ranges["F"]), 2)
        d = round(rng.uniform(*ranges["d"]), 2)
        theta = rng.randint(*ranges["theta"])

        if trap == "missing_cos_theta":
            return self._missing_cos(F, d, theta, rng, difficulty)
        elif trap == "angle_in_radians":
            return self._angle_radians(F, d, theta, rng, difficulty)
        return self._unit_confusion(F, d, theta, rng, difficulty)

    def _missing_cos(self, F, d, theta, rng, difficulty):
        """Trap 1: Ignore cosθ entirely."""
        W = round(F * d * math.cos(math.radians(theta)), 4)
        wrong_W = round(F * d, 4)

        text = (
            f"A force of {F}N is applied at {theta}° to the displacement "
            f"of {d}m. A student computes W = Fd = {wrong_W}J. "
            f"What is the correct work done?"
        )
        return Question(
            law=self.LAW_NAME, trap_type="missing_cos_theta", question_text=text,
            correct_answer=W, correct_unit="J",
            variables={"F": F, "d": d, "theta": theta},
            difficulty=difficulty,
            explanation=f"W = Fd cosθ = {F}×{d}×cos({theta}°) = {W}J.",
        )

    def _angle_radians(self, F, d, theta, rng, difficulty):
        """Trap 2: θ in degrees, but student uses it as radians in cos()."""
        W = round(F * d * math.cos(math.radians(theta)), 4)
        wrong_W = round(F * d * math.cos(theta), 4)

        text = (
            f"A {F}N force acts over {d}m at an angle of {theta}°. "
            f"Someone uses cos({theta}) directly (treating as radians) "
            f"and gets {wrong_W}J. What is the correct work?"
        )
        return Question(
            law=self.LAW_NAME, trap_type="angle_in_radians", question_text=text,
            correct_answer=W, correct_unit="J",
            variables={"F": F, "d": d, "theta": theta},
            difficulty=difficulty,
            explanation=f"Convert {theta}° to radians. W = Fd cos({theta}°) = {W}J.",
        )

    def _unit_confusion(self, F, d, theta, rng, difficulty):
        """Trap 3: Force in kN instead of N."""
        W = round(F * d * math.cos(math.radians(theta)), 4)
        F_kN = round(F / 1000, 4)

        text = (
            f"A force of {F_kN}kN acts over {d}m at {theta}° to the "
            f"direction of motion. What is the work done in joules?"
        )
        return Question(
            law=self.LAW_NAME, trap_type="unit_confusion", question_text=text,
            correct_answer=W, correct_unit="J",
            variables={"F_N": F, "F_kN": F_kN, "d": d, "theta": theta},
            difficulty=difficulty,
            explanation=f"{F_kN}kN = {F}N. W = Fd cosθ = {F}×{d}×cos({theta}°) = {W}J.",
        )
