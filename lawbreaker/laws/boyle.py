"""
Boyle's Law — P₁V₁ = P₂V₂  (constant temperature)

Traps:
  1. unit_confusion: pressure in atm vs Pa
  2. volume_unit_confusion: volume in mL vs L
  3. anchoring_bias: suggests a wrong final volume
"""

from __future__ import annotations

from typing import Optional

from lawbreaker.core.question import Question
from lawbreaker.laws.base import BaseLaw


class BoyleLaw(BaseLaw):
    """Boyle's Law (P₁V₁ = P₂V₂) adversarial question generator."""

    LAW_NAME = "Boyle's Law"

    _RANGES = {
        "easy": {"P": (1, 5), "V": (1, 10)},
        "medium": {"P": (1, 20), "V": (0.5, 50)},
        "hard": {"P": (0.5, 100), "V": (0.1, 200)},
    }

    def generate(self, difficulty: str = "medium", seed: Optional[int] = None) -> Question:
        """Generate an adversarial Boyle's Law question."""
        rng = self._rng(seed)
        ranges = self._RANGES.get(difficulty, self._RANGES["medium"])
        trap = rng.choice(["unit_confusion", "volume_unit_confusion", "anchoring_bias"])

        P1 = round(rng.uniform(*ranges["P"]), 2)
        V1 = round(rng.uniform(*ranges["V"]), 2)
        P2 = round(rng.uniform(*ranges["P"]), 2)
        while abs(P2 - P1) < 0.5:
            P2 = round(rng.uniform(*ranges["P"]), 2)

        if trap == "unit_confusion":
            return self._unit_confusion(P1, V1, P2, rng, difficulty)
        elif trap == "volume_unit_confusion":
            return self._volume_confusion(P1, V1, P2, rng, difficulty)
        return self._anchoring(P1, V1, P2, rng, difficulty)

    def _unit_confusion(self, P1, V1, P2, rng, difficulty):
        """Trap 1: P₁ in atm, P₂ in kPa — LLM must use consistent units."""
        V2 = round(P1 * V1 / P2, 4)
        P2_kPa = round(P2 * 101.325, 2)

        text = (
            f"A gas at {P1} atm occupies {V1}L. The pressure changes to "
            f"{P2_kPa} kPa. What is the new volume in litres? "
            f"(1 atm = 101.325 kPa)"
        )
        return Question(
            law=self.LAW_NAME, trap_type="unit_confusion", question_text=text,
            correct_answer=V2, correct_unit="L",
            variables={"P1_atm": P1, "V1": V1, "P2_atm": P2, "P2_kPa": P2_kPa},
            difficulty=difficulty,
            explanation=f"P₂ = {P2_kPa}kPa = {P2}atm. V₂ = P₁V₁/P₂ = "
                        f"{P1}×{V1}/{P2} = {V2}L.",
        )

    def _volume_confusion(self, P1, V1, P2, rng, difficulty):
        """Trap 2: Volume in mL instead of L."""
        V2 = round(P1 * V1 / P2, 4)
        V1_mL = round(V1 * 1000, 1)

        text = (
            f"A gas at {P1} atm has volume {V1_mL} mL. "
            f"The pressure increases to {P2} atm. "
            f"What is the new volume in litres?"
        )
        return Question(
            law=self.LAW_NAME, trap_type="volume_unit_confusion", question_text=text,
            correct_answer=V2, correct_unit="L",
            variables={"P1": P1, "V1_L": V1, "V1_mL": V1_mL, "P2": P2},
            difficulty=difficulty,
            explanation=f"{V1_mL}mL = {V1}L. V₂ = P₁V₁/P₂ = "
                        f"{P1}×{V1}/{P2} = {V2}L.",
        )

    def _anchoring(self, P1, V1, P2, rng, difficulty):
        """Trap 3: Suggest a wrong final volume."""
        V2 = round(P1 * V1 / P2, 4)
        wrong_V2 = round(V2 * rng.uniform(1.3, 2.5), 2)

        text = (
            f"A gas at {P1} atm and {V1}L is compressed to {P2} atm. "
            f"A practice solution says V₂ = {wrong_V2}L. "
            f"What is the correct new volume?"
        )
        return Question(
            law=self.LAW_NAME, trap_type="anchoring_bias", question_text=text,
            correct_answer=V2, correct_unit="L",
            variables={"P1": P1, "V1": V1, "P2": P2, "wrong_V2": wrong_V2},
            difficulty=difficulty,
            explanation=f"V₂ = P₁V₁/P₂ = {P1}×{V1}/{P2} = {V2}L.",
        )
