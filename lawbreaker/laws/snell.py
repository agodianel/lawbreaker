"""
Snell's Law — n₁ sin(θ₁) = n₂ sin(θ₂)

Traps:
  1. degree_radian_confusion: angle given in degrees but LLM may use radians
  2. inverted_ratio: swapping n₁ and n₂
  3. anchoring_bias: suggests a wrong refracted angle
"""

from __future__ import annotations

import math
from typing import Optional

from lawbreaker.core.question import Question
from lawbreaker.laws.base import BaseLaw


class SnellLaw(BaseLaw):
    """Snell's Law (n₁ sinθ₁ = n₂ sinθ₂) adversarial question generator."""

    LAW_NAME = "Snell's Law"

    _RANGES = {
        "easy": {"n1": (1.0, 1.5), "n2": (1.3, 1.8), "theta": (10, 40)},
        "medium": {"n1": (1.0, 1.6), "n2": (1.3, 2.0), "theta": (10, 50)},
        "hard": {"n1": (1.0, 1.8), "n2": (1.3, 2.5), "theta": (5, 60)},
    }

    def generate(self, difficulty: str = "medium", seed: Optional[int] = None) -> Question:
        """Generate an adversarial Snell's Law question."""
        rng = self._rng(seed)
        ranges = self._RANGES.get(difficulty, self._RANGES["medium"])
        trap = rng.choice(["degree_radian_confusion", "inverted_ratio", "anchoring_bias"])

        n1 = round(rng.uniform(*ranges["n1"]), 2)
        n2 = round(rng.uniform(*ranges["n2"]), 2)
        while n1 == n2:
            n2 = round(rng.uniform(*ranges["n2"]), 2)
        theta1_deg = rng.randint(*ranges["theta"])

        # Ensure total internal reflection doesn't occur
        sin_theta2 = n1 * math.sin(math.radians(theta1_deg)) / n2
        if abs(sin_theta2) > 1:
            theta1_deg = rng.randint(5, 20)
            sin_theta2 = n1 * math.sin(math.radians(theta1_deg)) / n2

        if trap == "degree_radian_confusion":
            return self._degree_radian(n1, n2, theta1_deg, rng, difficulty)
        elif trap == "inverted_ratio":
            return self._inverted_ratio(n1, n2, theta1_deg, rng, difficulty)
        return self._anchoring(n1, n2, theta1_deg, rng, difficulty)

    def _degree_radian(self, n1, n2, theta1_deg, rng, difficulty):
        """Trap 1: Angle in degrees; LLM might use it directly in sin()."""
        sin_theta2 = n1 * math.sin(math.radians(theta1_deg)) / n2
        theta2_deg = round(math.degrees(math.asin(sin_theta2)), 2)

        text = (
            f"Light passes from a medium with n₁ = {n1} to n₂ = {n2}. "
            f"The angle of incidence is {theta1_deg}°. "
            f"What is the angle of refraction in degrees?"
        )
        return Question(
            law=self.LAW_NAME, trap_type="degree_radian_confusion",
            question_text=text,
            correct_answer=theta2_deg, correct_unit="degrees",
            variables={"n1": n1, "n2": n2, "theta1": theta1_deg},
            difficulty=difficulty,
            explanation=f"sin(θ₂) = n₁sin(θ₁)/n₂ = {n1}×sin({theta1_deg}°)/{n2}. "
                        f"θ₂ = {theta2_deg}°.",
        )

    def _inverted_ratio(self, n1, n2, theta1_deg, rng, difficulty):
        """Trap 2: Suggest swapping n₁ and n₂ in the formula."""
        sin_theta2 = n1 * math.sin(math.radians(theta1_deg)) / n2
        theta2_deg = round(math.degrees(math.asin(sin_theta2)), 2)

        wrong_sin = n2 * math.sin(math.radians(theta1_deg)) / n1
        wrong_sin = min(wrong_sin, 0.999)
        wrong_theta2 = round(math.degrees(math.asin(wrong_sin)), 2)

        text = (
            f"Light travels from n₁ = {n1} into n₂ = {n2} at θ₁ = {theta1_deg}°. "
            f"A student gets θ₂ = {wrong_theta2}° by swapping the indices. "
            f"What is the correct refracted angle in degrees?"
        )
        return Question(
            law=self.LAW_NAME, trap_type="inverted_ratio",
            question_text=text,
            correct_answer=theta2_deg, correct_unit="degrees",
            variables={"n1": n1, "n2": n2, "theta1": theta1_deg, "wrong_theta2": wrong_theta2},
            difficulty=difficulty,
            explanation=f"sin(θ₂) = (n₁/n₂)sin(θ₁), not (n₂/n₁). θ₂ = {theta2_deg}°.",
        )

    def _anchoring(self, n1, n2, theta1_deg, rng, difficulty):
        """Trap 3: Suggest a wrong refraction angle."""
        sin_theta2 = n1 * math.sin(math.radians(theta1_deg)) / n2
        theta2_deg = round(math.degrees(math.asin(sin_theta2)), 2)
        wrong_theta2 = round(theta2_deg * rng.uniform(1.3, 2.0), 2)
        wrong_theta2 = min(wrong_theta2, 89.0)

        text = (
            f"Light enters from medium n₁ = {n1} to n₂ = {n2} "
            f"at an incidence angle of {theta1_deg}°. "
            f"A lab report states θ₂ = {wrong_theta2}°. "
            f"What is the correct angle of refraction in degrees?"
        )
        return Question(
            law=self.LAW_NAME, trap_type="anchoring_bias",
            question_text=text,
            correct_answer=theta2_deg, correct_unit="degrees",
            variables={"n1": n1, "n2": n2, "theta1": theta1_deg,
                        "wrong_theta2": wrong_theta2},
            difficulty=difficulty,
            explanation=f"θ₂ = arcsin(n₁ sin θ₁ / n₂) = {theta2_deg}°, "
                        f"not {wrong_theta2}°.",
        )
