"""
Conservation of Momentum — m₁v₁ + m₂v₂ = m₁v₁' + m₂v₂'

Simplified to perfectly inelastic collisions: m₁v₁ + m₂v₂ = (m₁+m₂)v_f

Traps:
  1. sign_confusion: ignoring direction (opposite velocities)
  2. mass_addition_error: forgetting combined mass in denominator
  3. anchoring_bias: suggests a wrong final velocity
"""

from __future__ import annotations

from typing import Optional

from lawbreaker.core.question import Question
from lawbreaker.laws.base import BaseLaw


class MomentumConservationLaw(BaseLaw):
    """Conservation of Momentum adversarial question generator."""

    LAW_NAME = "Conservation of Momentum"

    _RANGES = {
        "easy": {"m": (1, 10), "v": (1, 10)},
        "medium": {"m": (1, 50), "v": (1, 30)},
        "hard": {"m": (5, 500), "v": (5, 100)},
    }

    def generate(self, difficulty: str = "medium", seed: Optional[int] = None) -> Question:
        """Generate an adversarial momentum conservation question."""
        rng = self._rng(seed)
        ranges = self._RANGES.get(difficulty, self._RANGES["medium"])
        trap = rng.choice(["sign_confusion", "mass_addition_error", "anchoring_bias"])

        m1 = round(rng.uniform(*ranges["m"]), 2)
        m2 = round(rng.uniform(*ranges["m"]), 2)
        v1 = round(rng.uniform(*ranges["v"]), 2)
        v2 = round(rng.uniform(*ranges["v"]), 2)

        if trap == "sign_confusion":
            return self._sign_confusion(m1, m2, v1, v2, rng, difficulty)
        elif trap == "mass_addition_error":
            return self._mass_addition(m1, m2, v1, v2, rng, difficulty)
        return self._anchoring(m1, m2, v1, v2, rng, difficulty)

    def _sign_confusion(self, m1, m2, v1, v2, rng, difficulty):
        """Trap 1: Objects move in opposite directions; must subtract momenta."""
        # v2 is negative (opposite direction)
        v_f = round((m1 * v1 + m2 * (-v2)) / (m1 + m2), 4)

        text = (
            f"A {m1}kg object moving at {v1} m/s collides and sticks with a "
            f"{m2}kg object moving at {v2} m/s in the opposite direction. "
            f"What is the final velocity in m/s? "
            f"(Positive = direction of the first object)"
        )
        return Question(
            law=self.LAW_NAME, trap_type="sign_confusion", question_text=text,
            correct_answer=v_f, correct_unit="m/s",
            variables={"m1": m1, "m2": m2, "v1": v1, "v2": -v2},
            difficulty=difficulty,
            explanation=f"p = m₁v₁ + m₂(−v₂) = {m1}×{v1} + {m2}×(−{v2}). "
                        f"v_f = p/(m₁+m₂) = {v_f} m/s.",
        )

    def _mass_addition(self, m1, m2, v1, v2, rng, difficulty):
        """Trap 2: Objects same direction; LLM might forget combined mass."""
        v_f = round((m1 * v1 + m2 * v2) / (m1 + m2), 4)

        text = (
            f"Two objects ({m1}kg at {v1} m/s and {m2}kg at {v2} m/s, "
            f"same direction) collide and stick. A student divides total "
            f"momentum by m₁ only. What is the correct final velocity in m/s?"
        )
        return Question(
            law=self.LAW_NAME, trap_type="mass_addition_error", question_text=text,
            correct_answer=v_f, correct_unit="m/s",
            variables={"m1": m1, "m2": m2, "v1": v1, "v2": v2},
            difficulty=difficulty,
            explanation=f"v_f = (m₁v₁+m₂v₂)/(m₁+m₂) = "
                        f"({m1}×{v1}+{m2}×{v2})/({m1}+{m2}) = {v_f} m/s.",
        )

    def _anchoring(self, m1, m2, v1, v2, rng, difficulty):
        """Trap 3: Same direction collision with wrong velocity anchor."""
        v_f = round((m1 * v1 + m2 * v2) / (m1 + m2), 4)
        wrong_vf = round(v_f * rng.uniform(1.3, 2.0), 2)

        text = (
            f"A {m1}kg ball at {v1} m/s hits a {m2}kg ball at {v2} m/s "
            f"(same direction), and they stick together. A simulation says "
            f"v_f = {wrong_vf} m/s. What is the correct final velocity?"
        )
        return Question(
            law=self.LAW_NAME, trap_type="anchoring_bias", question_text=text,
            correct_answer=v_f, correct_unit="m/s",
            variables={"m1": m1, "m2": m2, "v1": v1, "v2": v2, "wrong_vf": wrong_vf},
            difficulty=difficulty,
            explanation=f"v_f = (m₁v₁+m₂v₂)/(m₁+m₂) = {v_f} m/s, not {wrong_vf}.",
        )
