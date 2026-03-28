"""
Thin Lens Equation — 1/f = 1/dₒ + 1/dᵢ

Traps:
  1. sign_confusion: diverging lens (negative f) vs converging
  2. unit_confusion: focal length in cm, distances in m
  3. anchoring_bias: suggests a wrong image distance
"""

from __future__ import annotations

from typing import Optional

from lawbreaker.core.question import Question
from lawbreaker.laws.base import BaseLaw


class LensEquationLaw(BaseLaw):
    """Thin Lens Equation (1/f = 1/dₒ + 1/dᵢ) adversarial question generator."""

    LAW_NAME = "Thin Lens Equation"

    _RANGES = {
        "easy": {"f": (5, 30), "do": (10, 50)},
        "medium": {"f": (5, 50), "do": (10, 100)},
        "hard": {"f": (2, 100), "do": (5, 200)},
    }

    def generate(self, difficulty: str = "medium", seed: Optional[int] = None) -> Question:
        """Generate an adversarial thin lens equation question."""
        rng = self._rng(seed)
        ranges = self._RANGES.get(difficulty, self._RANGES["medium"])
        trap = rng.choice(["sign_confusion", "unit_confusion", "anchoring_bias"])

        f = round(rng.uniform(*ranges["f"]), 2)
        do = round(rng.uniform(f + 1, ranges["do"][1] + f), 2)  # ensure do > f for real image

        if trap == "sign_confusion":
            return self._sign_confusion(f, do, rng, difficulty)
        elif trap == "unit_confusion":
            return self._unit_confusion(f, do, rng, difficulty)
        return self._anchoring(f, do, rng, difficulty)

    def _sign_confusion(self, f, do, rng, difficulty):
        """Trap 1: Diverging lens with negative focal length."""
        f_neg = -f
        # 1/di = 1/f - 1/do = -1/f_abs - 1/do
        di = round(1.0 / (1.0 / f_neg - 1.0 / do), 4)

        text = (
            f"A diverging lens has focal length f = {f}cm (negative). "
            f"An object is placed {do}cm from the lens. "
            f"What is the image distance in cm? "
            f"(Use sign convention: diverging lens has negative f)"
        )
        return Question(
            law=self.LAW_NAME, trap_type="sign_confusion", question_text=text,
            correct_answer=di, correct_unit="cm",
            variables={"f": f_neg, "do": do},
            difficulty=difficulty,
            explanation=f"1/dᵢ = 1/f − 1/dₒ = 1/({f_neg}) − 1/{do}. dᵢ = {di} cm "
                        f"(negative = virtual image).",
        )

    def _unit_confusion(self, f, do, rng, difficulty):
        """Trap 2: Focal length in mm, object distance in cm."""
        di = round(1.0 / (1.0 / f - 1.0 / do), 4)
        f_mm = round(f * 10, 1)

        text = (
            f"A converging lens has focal length {f_mm}mm. An object is "
            f"placed {do}cm from the lens. What is the image distance in cm?"
        )
        return Question(
            law=self.LAW_NAME, trap_type="unit_confusion", question_text=text,
            correct_answer=di, correct_unit="cm",
            variables={"f_cm": f, "f_mm": f_mm, "do": do},
            difficulty=difficulty,
            explanation=f"{f_mm}mm = {f}cm. 1/dᵢ = 1/{f} − 1/{do}. dᵢ = {di}cm.",
        )

    def _anchoring(self, f, do, rng, difficulty):
        """Trap 3: Suggest a wrong image distance."""
        di = round(1.0 / (1.0 / f - 1.0 / do), 4)
        wrong_di = round(di * rng.uniform(1.3, 2.5), 2)

        text = (
            f"A lens (f = {f}cm) forms an image of an object at {do}cm. "
            f"A student says dᵢ = {wrong_di}cm. "
            f"What is the correct image distance?"
        )
        return Question(
            law=self.LAW_NAME, trap_type="anchoring_bias", question_text=text,
            correct_answer=di, correct_unit="cm",
            variables={"f": f, "do": do, "wrong_di": wrong_di},
            difficulty=difficulty,
            explanation=f"1/dᵢ = 1/f − 1/dₒ = 1/{f} − 1/{do}. dᵢ = {di}cm.",
        )
