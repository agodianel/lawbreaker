"""
Coulomb's Law — F = k × q₁ × q₂ / r²

Traps:
  1. forget_r_squared: uses r instead of r²
  2. wrong_k_constant: suggests a wrong value for Coulomb's constant
  3. distance_unit_confusion: distance in cm vs metres
"""

from __future__ import annotations
from typing import Optional
from sympy import Rational, N as sympy_N
from lawbreaker.core.question import Question
from lawbreaker.laws.base import BaseLaw


class CoulombLaw(BaseLaw):
    """Coulomb's Law (F = kq₁q₂/r²) adversarial question generator."""

    LAW_NAME = "Coulomb's Law"
    K = 8.9875e9  # N·m²/C²

    _RANGES = {
        "easy": {"q": (1e-6, 10e-6), "r": (0.1, 1.0)},
        "medium": {"q": (1e-6, 100e-6), "r": (0.01, 1.0)},
        "hard": {"q": (1e-9, 1e-3), "r": (0.001, 1.0)},
    }

    def generate(self, difficulty: str = "medium", seed: Optional[int] = None) -> Question:
        """Generate an adversarial Coulomb's Law question."""
        rng = self._rng(seed)
        ranges = self._RANGES.get(difficulty, self._RANGES["medium"])
        trap = rng.choice(["forget_r_squared", "wrong_k_constant", "distance_unit_confusion"])
        q1 = rng.uniform(*ranges["q"])
        q2 = rng.uniform(*ranges["q"])
        r = round(rng.uniform(*ranges["r"]), 3)

        if trap == "forget_r_squared":
            return self._forget_r_squared(q1, q2, r, rng, difficulty)
        elif trap == "wrong_k_constant":
            return self._wrong_k(q1, q2, r, rng, difficulty)
        return self._distance_confusion(q1, q2, r, rng, difficulty)

    def _forget_r_squared(self, q1, q2, r, rng, difficulty):
        """Trap 1: Hint at using r instead of r²."""
        F = round(self.K * q1 * q2 / (r ** 2), 6)
        wrong_F = round(self.K * q1 * q2 / r, 6)
        q1_uC = round(q1 * 1e6, 4)
        q2_uC = round(q2 * 1e6, 4)
        text = (f"Two charges q₁ = {q1_uC}μC and q₂ = {q2_uC}μC are separated "
                f"by {r}m. A student divides by the distance. What is the force in N?")
        return Question(law=self.LAW_NAME, trap_type="forget_r_squared", question_text=text,
                        correct_answer=F, correct_unit="N",
                        variables={"q1": q1, "q2": q2, "r": r, "k": self.K},
                        difficulty=difficulty,
                        explanation=f"Must divide by r² not r. F = kq₁q₂/r² = {F}N.")

    def _wrong_k(self, q1, q2, r, rng, difficulty):
        """Trap 2: Suggest a wrong Coulomb constant."""
        F = round(self.K * q1 * q2 / (r ** 2), 6)
        wrong_k = round(self.K * rng.uniform(0.5, 0.8), 4)
        q1_uC = round(q1 * 1e6, 4)
        q2_uC = round(q2 * 1e6, 4)
        text = (f"q₁ = {q1_uC}μC, q₂ = {q2_uC}μC, r = {r}m. "
                f"Using k = {wrong_k:.4e} N·m²/C², a student gets a force. "
                f"Using the correct k = 8.9875×10⁹, what is the force?")
        return Question(law=self.LAW_NAME, trap_type="wrong_k_constant", question_text=text,
                        correct_answer=F, correct_unit="N",
                        variables={"q1": q1, "q2": q2, "r": r, "k": self.K, "wrong_k": wrong_k},
                        difficulty=difficulty,
                        explanation=f"Use k = 8.9875e9. F = kq₁q₂/r² = {F}N.")

    def _distance_confusion(self, q1, q2, r, rng, difficulty):
        """Trap 3: Distance given in cm."""
        r_cm = round(r * 100, 2)
        F = round(self.K * q1 * q2 / (r ** 2), 6)
        q1_uC = round(q1 * 1e6, 4)
        q2_uC = round(q2 * 1e6, 4)
        text = (f"Two charges q₁ = {q1_uC}μC, q₂ = {q2_uC}μC are {r_cm}cm apart. "
                f"What is the electrostatic force in Newtons?")
        return Question(law=self.LAW_NAME, trap_type="distance_unit_confusion",
                        question_text=text, correct_answer=F, correct_unit="N",
                        variables={"q1": q1, "q2": q2, "r_m": r, "r_cm": r_cm},
                        difficulty=difficulty,
                        explanation=f"{r_cm}cm = {r}m. F = kq₁q₂/r² = {F}N.")
