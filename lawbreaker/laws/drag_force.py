"""
Drag Force — F = ½CρAv²

Traps:
  1. missing_half: forgets the ½ factor
  2. velocity_squared: uses v instead of v²
  3. area_unit_confusion: area in cm² vs m²
"""

from __future__ import annotations

from typing import Optional

from lawbreaker.core.question import Question
from lawbreaker.laws.base import BaseLaw


class DragForceLaw(BaseLaw):
    """Drag Force (F = ½CρAv²) adversarial question generator."""

    LAW_NAME = "Drag Force"

    _RANGES = {
        "easy": {"C": (0.3, 1.0), "rho": (1.1, 1.3), "A": (0.01, 1.0), "v": (1, 10)},
        "medium": {"C": (0.2, 1.5), "rho": (1.0, 1.3), "A": (0.01, 5.0), "v": (5, 50)},
        "hard": {"C": (0.1, 2.0), "rho": (0.5, 1.3), "A": (0.01, 10.0), "v": (10, 200)},
    }

    def generate(self, difficulty: str = "medium", seed: Optional[int] = None) -> Question:
        """Generate an adversarial drag force question."""
        rng = self._rng(seed)
        ranges = self._RANGES.get(difficulty, self._RANGES["medium"])
        trap = rng.choice(["missing_half", "velocity_squared", "area_unit_confusion"])

        C = round(rng.uniform(*ranges["C"]), 2)
        rho = round(rng.uniform(*ranges["rho"]), 3)
        A = round(rng.uniform(*ranges["A"]), 4)
        v = round(rng.uniform(*ranges["v"]), 2)

        if trap == "missing_half":
            return self._missing_half(C, rho, A, v, rng, difficulty)
        elif trap == "velocity_squared":
            return self._velocity_squared(C, rho, A, v, rng, difficulty)
        return self._area_confusion(C, rho, A, v, rng, difficulty)

    def _missing_half(self, C, rho, A, v, rng, difficulty):
        """Trap 1: Tempts LLM to use CρAv² instead of ½CρAv²."""
        F = round(0.5 * C * rho * A * v**2, 4)
        wrong_F = round(C * rho * A * v**2, 4)

        text = (
            f"An object (C_d = {C}, A = {A}m²) moves at {v} m/s through air "
            f"(ρ = {rho} kg/m³). A student uses F = CρAv² = {wrong_F}N. "
            f"What is the correct drag force?"
        )
        return Question(
            law=self.LAW_NAME, trap_type="missing_half", question_text=text,
            correct_answer=F, correct_unit="N",
            variables={"C": C, "rho": rho, "A": A, "v": v},
            difficulty=difficulty,
            explanation=f"F = ½CρAv², not CρAv². F = 0.5×{C}×{rho}×{A}×{v}² = {F}N.",
        )

    def _velocity_squared(self, C, rho, A, v, rng, difficulty):
        """Trap 2: Uses v instead of v²."""
        F = round(0.5 * C * rho * A * v**2, 4)
        wrong_F = round(0.5 * C * rho * A * v, 4)

        text = (
            f"A vehicle (C_d = {C}, frontal area {A}m²) travels at {v} m/s "
            f"in air (ρ = {rho} kg/m³). Someone computes drag using v "
            f"instead of v² and gets {wrong_F}N. What is the correct drag force?"
        )
        return Question(
            law=self.LAW_NAME, trap_type="velocity_squared", question_text=text,
            correct_answer=F, correct_unit="N",
            variables={"C": C, "rho": rho, "A": A, "v": v},
            difficulty=difficulty,
            explanation=f"F = ½CρAv², must use v². F = {F}N, not {wrong_F}N.",
        )

    def _area_confusion(self, C, rho, A, v, rng, difficulty):
        """Trap 3: Area in cm² instead of m²."""
        F = round(0.5 * C * rho * A * v**2, 4)
        A_cm2 = round(A * 1e4, 1)

        text = (
            f"An object (C_d = {C}) has a cross-section of {A_cm2}cm² moving "
            f"at {v} m/s in air (ρ = {rho} kg/m³). "
            f"What is the drag force in Newtons?"
        )
        return Question(
            law=self.LAW_NAME, trap_type="area_unit_confusion", question_text=text,
            correct_answer=F, correct_unit="N",
            variables={"C": C, "rho": rho, "A_m2": A, "A_cm2": A_cm2, "v": v},
            difficulty=difficulty,
            explanation=f"{A_cm2}cm² = {A}m². F = ½CρAv² = {F}N.",
        )
