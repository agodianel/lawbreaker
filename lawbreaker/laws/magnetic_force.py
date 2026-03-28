"""
Magnetic Force on a Moving Charge — F = qvBsinθ

Traps:
  1. missing_sin_theta: uses F = qvB when θ ≠ 90°
  2. unit_confusion: charge in μC vs C
  3. angle_confusion: degrees vs radians
"""

from __future__ import annotations

import math
from typing import Optional

from lawbreaker.core.question import Question
from lawbreaker.laws.base import BaseLaw


class MagneticForceLaw(BaseLaw):
    """Magnetic Force (F = qvBsinθ) adversarial question generator."""

    LAW_NAME = "Magnetic Force"

    _RANGES = {
        "easy": {"q_uC": (1, 100), "v": (100, 1000), "B": (0.01, 1.0), "theta": (15, 90)},
        "medium": {"q_uC": (0.1, 1000), "v": (100, 10000), "B": (0.001, 2.0), "theta": (10, 90)},
        "hard": {"q_uC": (0.01, 10000), "v": (1000, 1e6), "B": (0.001, 5.0), "theta": (5, 90)},
    }

    def generate(self, difficulty: str = "medium", seed: Optional[int] = None) -> Question:
        """Generate an adversarial magnetic force question."""
        rng = self._rng(seed)
        ranges = self._RANGES.get(difficulty, self._RANGES["medium"])
        trap = rng.choice(["missing_sin_theta", "unit_confusion", "angle_confusion"])

        q_uC = round(rng.uniform(*ranges["q_uC"]), 4)
        v = round(rng.uniform(*ranges["v"]), 2)
        B = round(rng.uniform(*ranges["B"]), 4)
        theta = rng.randint(*ranges["theta"])

        if trap == "missing_sin_theta":
            return self._missing_sin(q_uC, v, B, theta, rng, difficulty)
        elif trap == "unit_confusion":
            return self._unit_confusion(q_uC, v, B, theta, rng, difficulty)
        return self._angle_confusion(q_uC, v, B, theta, rng, difficulty)

    def _missing_sin(self, q_uC, v, B, theta, rng, difficulty):
        """Trap 1: Ignores sinθ and just uses F = qvB."""
        q = q_uC * 1e-6
        F = round(q * v * B * math.sin(math.radians(theta)), 6)
        wrong_F = round(q * v * B, 6)

        text = (
            f"A charge of {q_uC}μC moves at {v} m/s through a magnetic field "
            f"of {B}T at an angle of {theta}° to the field. A student uses "
            f"F = qvB = {wrong_F}N, ignoring the angle. "
            f"What is the correct force?"
        )
        return Question(
            law=self.LAW_NAME, trap_type="missing_sin_theta", question_text=text,
            correct_answer=F, correct_unit="N",
            variables={"q_uC": q_uC, "q_C": q, "v": v, "B": B, "theta": theta},
            difficulty=difficulty,
            explanation=f"F = qvBsinθ = {q}×{v}×{B}×sin({theta}°) = {F}N.",
        )

    def _unit_confusion(self, q_uC, v, B, theta, rng, difficulty):
        """Trap 2: Charge in μC — must convert to C."""
        q = q_uC * 1e-6
        F = round(q * v * B * math.sin(math.radians(theta)), 6)

        text = (
            f"A particle with charge {q_uC}μC travels at {v} m/s "
            f"perpendicular to a {B}T field (θ = {theta}°). "
            f"What is the magnetic force in Newtons?"
        )
        return Question(
            law=self.LAW_NAME, trap_type="unit_confusion", question_text=text,
            correct_answer=F, correct_unit="N",
            variables={"q_uC": q_uC, "q_C": q, "v": v, "B": B, "theta": theta},
            difficulty=difficulty,
            explanation=f"{q_uC}μC = {q}C. F = qvBsinθ = {F}N. "
                        f"Using μC directly would give wrong answer.",
        )

    def _angle_confusion(self, q_uC, v, B, theta, rng, difficulty):
        """Trap 3: Student uses radians directly instead of converting."""
        q = q_uC * 1e-6
        F = round(q * v * B * math.sin(math.radians(theta)), 6)
        wrong_F = round(q * v * B * math.sin(theta), 6)  # theta used as radians

        text = (
            f"A {q_uC}μC charge moves at {v} m/s at {theta}° to a {B}T field. "
            f"Using sin({theta}) directly (in radians), someone gets "
            f"{wrong_F}N. What is the correct force using degrees?"
        )
        return Question(
            law=self.LAW_NAME, trap_type="angle_confusion", question_text=text,
            correct_answer=F, correct_unit="N",
            variables={"q_uC": q_uC, "q_C": q, "v": v, "B": B, "theta_deg": theta},
            difficulty=difficulty,
            explanation=f"Must convert {theta}° to radians for sin(). "
                        f"F = qvBsin({theta}°) = {F}N.",
        )
