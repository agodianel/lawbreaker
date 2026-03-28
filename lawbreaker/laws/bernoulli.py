"""
Bernoulli's Equation — P₁ + ½ρv₁² + ρgh₁ = P₂ + ½ρv₂² + ρgh₂

Traps:
  1. missing_half: forgets the ½ in kinetic term
  2. unit_confusion: pressure in kPa vs Pa
  3. height_sign_error: confuses height direction
"""

from __future__ import annotations

from typing import Optional

from lawbreaker.core.question import Question
from lawbreaker.laws.base import BaseLaw


class BernoulliLaw(BaseLaw):
    """Bernoulli's Equation adversarial question generator."""

    LAW_NAME = "Bernoulli's Equation"
    G = 9.81  # m/s²

    _RANGES = {
        "easy": {"P": (100000, 200000), "rho": (900, 1100), "v": (1, 5), "h": (0, 5)},
        "medium": {"P": (80000, 300000), "rho": (800, 1200), "v": (1, 20), "h": (0, 20)},
        "hard": {"P": (50000, 500000), "rho": (700, 1300), "v": (1, 50), "h": (0, 50)},
    }

    def generate(self, difficulty: str = "medium", seed: Optional[int] = None) -> Question:
        """Generate an adversarial Bernoulli equation question."""
        rng = self._rng(seed)
        ranges = self._RANGES.get(difficulty, self._RANGES["medium"])
        trap = rng.choice(["missing_half", "unit_confusion", "height_sign_error"])

        P1 = rng.randint(*ranges["P"])
        rho = rng.randint(*ranges["rho"])
        v1 = round(rng.uniform(*ranges["v"]), 2)
        v2 = round(rng.uniform(*ranges["v"]), 2)
        h1 = round(rng.uniform(*ranges["h"]), 2)
        h2 = round(rng.uniform(*ranges["h"]), 2)

        if trap == "missing_half":
            return self._missing_half(P1, rho, v1, v2, h1, h2, rng, difficulty)
        elif trap == "unit_confusion":
            return self._unit_confusion(P1, rho, v1, v2, h1, h2, rng, difficulty)
        return self._height_sign(P1, rho, v1, v2, h1, h2, rng, difficulty)

    def _missing_half(self, P1, rho, v1, v2, h1, h2, rng, difficulty):
        """Trap 1: Tempts LLM to forget ½ in kinetic energy term."""
        P2 = round(P1 + 0.5 * rho * (v1**2 - v2**2) + rho * self.G * (h1 - h2), 2)

        text = (
            f"Water (ρ = {rho} kg/m³) flows in a pipe. At point 1: "
            f"P₁ = {P1} Pa, v₁ = {v1} m/s, h₁ = {h1}m. "
            f"At point 2: v₂ = {v2} m/s, h₂ = {h2}m. "
            f"A student computes P₂ using ρv² instead of ½ρv². "
            f"What is the correct P₂ in Pa?"
        )
        return Question(
            law=self.LAW_NAME, trap_type="missing_half", question_text=text,
            correct_answer=P2, correct_unit="Pa",
            variables={"P1": P1, "rho": rho, "v1": v1, "v2": v2, "h1": h1, "h2": h2},
            difficulty=difficulty,
            explanation=f"P₂ = P₁ + ½ρ(v₁²−v₂²) + ρg(h₁−h₂) = {P2} Pa. "
                        f"The ½ factor is essential.",
        )

    def _unit_confusion(self, P1, rho, v1, v2, h1, h2, rng, difficulty):
        """Trap 2: Pressure given in kPa but answer expected in Pa."""
        P2 = round(P1 + 0.5 * rho * (v1**2 - v2**2) + rho * self.G * (h1 - h2), 2)
        P1_kPa = round(P1 / 1000, 3)

        text = (
            f"Fluid (ρ = {rho} kg/m³) flows through a system. "
            f"P₁ = {P1_kPa} kPa, v₁ = {v1} m/s, h₁ = {h1}m. "
            f"At point 2, v₂ = {v2} m/s, h₂ = {h2}m. "
            f"What is P₂ in Pascals?"
        )
        return Question(
            law=self.LAW_NAME, trap_type="unit_confusion", question_text=text,
            correct_answer=P2, correct_unit="Pa",
            variables={"P1_Pa": P1, "P1_kPa": P1_kPa, "rho": rho,
                        "v1": v1, "v2": v2, "h1": h1, "h2": h2},
            difficulty=difficulty,
            explanation=f"P₁ = {P1_kPa} kPa = {P1} Pa. P₂ = {P2} Pa.",
        )

    def _height_sign(self, P1, rho, v1, v2, h1, h2, rng, difficulty):
        """Trap 3: Confusion about height being measured up or down."""
        P2 = round(P1 + 0.5 * rho * (v1**2 - v2**2) + rho * self.G * (h1 - h2), 2)

        text = (
            f"Fluid (ρ = {rho} kg/m³) flows from height {h1}m to {h2}m. "
            f"P₁ = {P1} Pa, v₁ = {v1} m/s, v₂ = {v2} m/s. "
            f"A student says the height difference is {round(h2 - h1, 2)}m "
            f"(swapping the sign). What is the correct P₂ in Pa?"
        )
        return Question(
            law=self.LAW_NAME, trap_type="height_sign_error", question_text=text,
            correct_answer=P2, correct_unit="Pa",
            variables={"P1": P1, "rho": rho, "v1": v1, "v2": v2, "h1": h1, "h2": h2},
            difficulty=difficulty,
            explanation=f"Height term is ρg(h₁−h₂), not ρg(h₂−h₁). P₂ = {P2} Pa.",
        )
