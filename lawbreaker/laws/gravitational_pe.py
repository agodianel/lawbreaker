"""
Gravitational Potential Energy — U = mgh

Traps:
  1. weight_vs_mass: given weight (in N), LLM multiplies by g again
  2. height_unit_confusion: height in cm vs m
  3. anchoring_bias: suggests a wrong energy value
"""

from __future__ import annotations

from typing import Optional

from lawbreaker.core.question import Question
from lawbreaker.laws.base import BaseLaw


class GravitationalPELaw(BaseLaw):
    """Gravitational PE (U = mgh) adversarial question generator."""

    LAW_NAME = "Gravitational PE"
    G = 9.81

    _RANGES = {
        "easy": {"m": (1, 20), "h": (1, 10)},
        "medium": {"m": (1, 100), "h": (1, 50)},
        "hard": {"m": (5, 1000), "h": (5, 200)},
    }

    def generate(self, difficulty: str = "medium", seed: Optional[int] = None) -> Question:
        """Generate an adversarial gravitational PE question."""
        rng = self._rng(seed)
        ranges = self._RANGES.get(difficulty, self._RANGES["medium"])
        trap = rng.choice(["weight_vs_mass", "height_unit_confusion", "anchoring_bias"])

        m = round(rng.uniform(*ranges["m"]), 2)
        h = round(rng.uniform(*ranges["h"]), 2)

        if trap == "weight_vs_mass":
            return self._weight_vs_mass(m, h, rng, difficulty)
        elif trap == "height_unit_confusion":
            return self._height_confusion(m, h, rng, difficulty)
        return self._anchoring(m, h, rng, difficulty)

    def _weight_vs_mass(self, m, h, rng, difficulty):
        """Trap 1: Given weight in N; LLM might multiply by g again."""
        U = round(m * self.G * h, 4)
        W = round(m * self.G, 2)

        text = (
            f"An object weighing {W}N is lifted to a height of {h}m. "
            f"What is the gravitational potential energy in joules? "
            f"(g = {self.G} m/s²)"
        )
        return Question(
            law=self.LAW_NAME, trap_type="weight_vs_mass", question_text=text,
            correct_answer=U, correct_unit="J",
            variables={"m": m, "W": W, "h": h, "g": self.G},
            difficulty=difficulty,
            explanation=f"Weight = mg = {W}N, so m = {m}kg. "
                        f"U = mgh = {m}×{self.G}×{h} = {U}J. "
                        f"Or equivalently U = Wh = {W}×{h} = {U}J.",
        )

    def _height_confusion(self, m, h, rng, difficulty):
        """Trap 2: Height given in cm."""
        U = round(m * self.G * h, 4)
        h_cm = round(h * 100, 1)

        text = (
            f"A {m}kg object is at a height of {h_cm}cm. "
            f"What is its gravitational PE in joules? (g = {self.G} m/s²)"
        )
        return Question(
            law=self.LAW_NAME, trap_type="height_unit_confusion", question_text=text,
            correct_answer=U, correct_unit="J",
            variables={"m": m, "h_m": h, "h_cm": h_cm, "g": self.G},
            difficulty=difficulty,
            explanation=f"{h_cm}cm = {h}m. U = mgh = {m}×{self.G}×{h} = {U}J.",
        )

    def _anchoring(self, m, h, rng, difficulty):
        """Trap 3: Suggest a wrong PE value."""
        U = round(m * self.G * h, 4)
        wrong_U = round(U * rng.uniform(1.5, 3.0), 2)

        text = (
            f"A {m}kg mass is at height {h}m. A worksheet says "
            f"U = {wrong_U}J. What is the correct gravitational PE? "
            f"(g = {self.G} m/s²)"
        )
        return Question(
            law=self.LAW_NAME, trap_type="anchoring_bias", question_text=text,
            correct_answer=U, correct_unit="J",
            variables={"m": m, "h": h, "g": self.G, "wrong_U": wrong_U},
            difficulty=difficulty,
            explanation=f"U = mgh = {m}×{self.G}×{h} = {U}J.",
        )
