"""
Kinetic Energy — KE = 0.5 × m × v²

Traps:
  1. missing_half: omits the 0.5 factor (very common LLM mistake)
  2. velocity_direction: confuses speed/velocity, implies direction matters
  3. anchoring_to_v: anchors to v instead of v², leading to linear error
"""

from __future__ import annotations

from typing import Optional

from sympy import Rational, N as sympy_N

from lawbreaker.core.question import Question
from lawbreaker.laws.base import BaseLaw


class KineticEnergyLaw(BaseLaw):
    """Kinetic Energy (KE = ½mv²) adversarial question generator."""

    LAW_NAME = "Kinetic Energy"

    _RANGES = {
        "easy": {"m": (1, 10), "v": (1, 10)},
        "medium": {"m": (5, 50), "v": (5, 30)},
        "hard": {"m": (10, 200), "v": (10, 100)},
    }

    def generate(self, difficulty: str = "medium", seed: Optional[int] = None) -> Question:
        """Generate an adversarial kinetic energy question.

        Args:
            difficulty: One of ``"easy"``, ``"medium"``, ``"hard"``.
            seed: Optional random seed.

        Returns:
            A ``Question`` with one of three trap types.
        """
        rng = self._rng(seed)
        ranges = self._RANGES.get(difficulty, self._RANGES["medium"])
        trap = rng.choice(["missing_half", "velocity_direction", "anchoring_to_v"])

        m = round(rng.uniform(*ranges["m"]), 2)
        v = round(rng.uniform(*ranges["v"]), 2)

        if trap == "missing_half":
            return self._missing_half(m, v, rng, difficulty)
        elif trap == "velocity_direction":
            return self._velocity_direction(m, v, rng, difficulty)
        else:
            return self._anchoring_to_v(m, v, rng, difficulty)

    def _missing_half(self, m: float, v: float, rng, difficulty: str) -> Question:
        """Trap 1: Question phrased to make LLMs forget the ½ factor."""
        KE = round(float(sympy_N(Rational(1, 2) * Rational(str(m)) * Rational(str(v)) ** 2)), 4)
        wrong_KE = round(m * v ** 2, 4)

        text = (
            f"A {m}kg object moves at {v} m/s. "
            f"Compute its kinetic energy. "
            f"(Recall: kinetic energy depends on mass and the square of velocity.)"
        )
        return Question(
            law=self.LAW_NAME,
            trap_type="missing_half",
            question_text=text,
            correct_answer=KE,
            correct_unit="J",
            variables={"m": m, "v": v, "wrong_KE_no_half": wrong_KE},
            difficulty=difficulty,
            explanation=(
                f"Missing half trap: the hint 'mass and square of velocity' tempts "
                f"LLMs to compute m×v² = {wrong_KE}J. Correct: KE = ½mv² = {KE}J."
            ),
        )

    def _velocity_direction(self, m: float, v: float, rng, difficulty: str) -> Question:
        """Trap 2: Velocity given with direction — KE uses speed (magnitude)."""
        KE = round(float(sympy_N(Rational(1, 2) * Rational(str(m)) * Rational(str(v)) ** 2)), 4)
        direction = rng.choice(["north", "east", "at 30° above horizontal", "downward"])

        text = (
            f"A {m}kg ball is thrown at {v} m/s {direction}. "
            f"What is its kinetic energy? Does the direction affect the answer?"
        )
        return Question(
            law=self.LAW_NAME,
            trap_type="velocity_direction",
            question_text=text,
            correct_answer=KE,
            correct_unit="J",
            variables={"m": m, "v": v, "direction": direction},
            difficulty=difficulty,
            explanation=(
                f"Direction trap: KE = ½mv² = ½ × {m} × {v}² = {KE}J. "
                f"Direction does NOT affect kinetic energy — only speed matters."
            ),
        )

    def _anchoring_to_v(self, m: float, v: float, rng, difficulty: str) -> Question:
        """Trap 3: Anchor LLM to v (linear) instead of v² (quadratic)."""
        KE = round(float(sympy_N(Rational(1, 2) * Rational(str(m)) * Rational(str(v)) ** 2)), 4)
        wrong_KE = round(0.5 * m * v, 4)  # linear in v

        text = (
            f"A {m}kg object is moving at {v} m/s. "
            f"A quick estimate gives kinetic energy ≈ {wrong_KE}J. "
            f"What is the correct kinetic energy?"
        )
        return Question(
            law=self.LAW_NAME,
            trap_type="anchoring_to_v",
            question_text=text,
            correct_answer=KE,
            correct_unit="J",
            variables={"m": m, "v": v, "wrong_KE_linear": wrong_KE},
            difficulty=difficulty,
            explanation=(
                f"Anchoring-to-v trap: the estimate {wrong_KE}J used ½mv not ½mv². "
                f"Correct: KE = ½ × {m} × {v}² = {KE}J."
            ),
        )
