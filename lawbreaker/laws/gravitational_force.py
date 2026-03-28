"""
Newton's Law of Universal Gravitation — F = Gm₁m₂/r²

Traps:
  1. forget_r_squared: divides by r instead of r²
  2. wrong_G: suggests an incorrect gravitational constant
  3. distance_unit_confusion: distance in km vs m
"""

from __future__ import annotations

from typing import Optional

from lawbreaker.core.question import Question
from lawbreaker.laws.base import BaseLaw


class GravitationalForceLaw(BaseLaw):
    """Newton's Law of Gravitation (F = Gm₁m₂/r²) adversarial question generator."""

    LAW_NAME = "Gravitational Force"
    G = 6.674e-11  # N·m²/kg²

    _RANGES = {
        "easy": {"m": (1e3, 1e6), "r": (1.0, 100.0)},
        "medium": {"m": (1e6, 1e12), "r": (10.0, 1e4)},
        "hard": {"m": (1e10, 1e24), "r": (1e3, 1e8)},
    }

    def generate(self, difficulty: str = "medium", seed: Optional[int] = None) -> Question:
        """Generate an adversarial gravitational force question."""
        rng = self._rng(seed)
        ranges = self._RANGES.get(difficulty, self._RANGES["medium"])
        trap = rng.choice(["forget_r_squared", "wrong_G", "distance_unit_confusion"])

        m1 = rng.uniform(*ranges["m"])
        m2 = rng.uniform(*ranges["m"])
        r = round(rng.uniform(*ranges["r"]), 2)

        if trap == "forget_r_squared":
            return self._forget_r_squared(m1, m2, r, rng, difficulty)
        elif trap == "wrong_G":
            return self._wrong_G(m1, m2, r, rng, difficulty)
        return self._distance_confusion(m1, m2, r, rng, difficulty)

    def _forget_r_squared(self, m1, m2, r, rng, difficulty):
        """Trap 1: Hint at dividing by r instead of r²."""
        F = round(self.G * m1 * m2 / (r ** 2), 6)
        text = (
            f"Two objects with masses {m1:.3e}kg and {m2:.3e}kg are {r}m apart. "
            f"A student divides by the distance. What is the gravitational force in N?"
        )
        return Question(
            law=self.LAW_NAME, trap_type="forget_r_squared", question_text=text,
            correct_answer=F, correct_unit="N",
            variables={"m1": m1, "m2": m2, "r": r, "G": self.G},
            difficulty=difficulty,
            explanation=f"F = Gm₁m₂/r² (not r). F = {F}N.",
        )

    def _wrong_G(self, m1, m2, r, rng, difficulty):
        """Trap 2: Suggest a wrong gravitational constant."""
        F = round(self.G * m1 * m2 / (r ** 2), 6)
        wrong_G = round(self.G * rng.uniform(1.5, 3.0), 14)
        text = (
            f"m₁ = {m1:.3e}kg, m₂ = {m2:.3e}kg, r = {r}m. "
            f"A textbook typo says G = {wrong_G:.4e} N·m²/kg². "
            f"Using the correct G = 6.674×10⁻¹¹, what is the force in N?"
        )
        return Question(
            law=self.LAW_NAME, trap_type="wrong_G", question_text=text,
            correct_answer=F, correct_unit="N",
            variables={"m1": m1, "m2": m2, "r": r, "G": self.G, "wrong_G": wrong_G},
            difficulty=difficulty,
            explanation=f"Use G = 6.674e-11. F = Gm₁m₂/r² = {F}N.",
        )

    def _distance_confusion(self, m1, m2, r, rng, difficulty):
        """Trap 3: Distance given in km instead of m."""
        r_km = round(r / 1000, 5)
        F = round(self.G * m1 * m2 / (r ** 2), 6)
        text = (
            f"Two masses {m1:.3e}kg and {m2:.3e}kg are separated by {r_km}km. "
            f"What is the gravitational force between them in Newtons?"
        )
        return Question(
            law=self.LAW_NAME, trap_type="distance_unit_confusion", question_text=text,
            correct_answer=F, correct_unit="N",
            variables={"m1": m1, "m2": m2, "r_m": r, "r_km": r_km},
            difficulty=difficulty,
            explanation=f"{r_km}km = {r}m. F = Gm₁m₂/r² = {F}N.",
        )
