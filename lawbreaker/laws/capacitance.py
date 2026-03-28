"""
Capacitance — Q = CV

Traps:
  1. unit_confusion: capacitance in μF vs F
  2. anchoring_bias: suggests a wrong charge value
  3. series_parallel_confusion: series vs parallel capacitance mistake
"""

from __future__ import annotations

from typing import Optional

from lawbreaker.core.question import Question
from lawbreaker.laws.base import BaseLaw


class CapacitanceLaw(BaseLaw):
    """Capacitance (Q = CV) adversarial question generator."""

    LAW_NAME = "Capacitance"

    _RANGES = {
        "easy": {"C_uF": (1, 100), "V": (1, 20)},
        "medium": {"C_uF": (1, 1000), "V": (5, 100)},
        "hard": {"C_uF": (0.1, 10000), "V": (10, 500)},
    }

    def generate(self, difficulty: str = "medium", seed: Optional[int] = None) -> Question:
        """Generate an adversarial capacitance question."""
        rng = self._rng(seed)
        ranges = self._RANGES.get(difficulty, self._RANGES["medium"])
        trap = rng.choice(["unit_confusion", "anchoring_bias", "series_parallel_confusion"])

        C_uF = round(rng.uniform(*ranges["C_uF"]), 2)
        V = round(rng.uniform(*ranges["V"]), 2)

        if trap == "unit_confusion":
            return self._unit_confusion(C_uF, V, rng, difficulty)
        elif trap == "anchoring_bias":
            return self._anchoring(C_uF, V, rng, difficulty)
        return self._series_parallel(C_uF, V, rng, difficulty)

    def _unit_confusion(self, C_uF, V, rng, difficulty):
        """Trap 1: Capacitance in μF; answer in coulombs."""
        C_F = C_uF * 1e-6
        Q = round(C_F * V, 10)

        text = (
            f"A capacitor of {C_uF}μF is charged to {V}V. "
            f"What is the charge stored in coulombs?"
        )
        return Question(
            law=self.LAW_NAME, trap_type="unit_confusion", question_text=text,
            correct_answer=Q, correct_unit="C",
            variables={"C_uF": C_uF, "C_F": C_F, "V": V},
            difficulty=difficulty,
            explanation=f"{C_uF}μF = {C_F}F. Q = CV = {C_F}×{V} = {Q}C. "
                        f"Using μF directly gives wrong result.",
        )

    def _anchoring(self, C_uF, V, rng, difficulty):
        """Trap 2: Suggest a wrong charge."""
        C_F = C_uF * 1e-6
        Q = round(C_F * V, 10)
        wrong_Q = round(Q * rng.uniform(2, 5), 10)

        text = (
            f"A {C_uF}μF capacitor is connected to {V}V. "
            f"An answer key says Q = {wrong_Q:.6e}C. "
            f"What is the correct charge in coulombs?"
        )
        return Question(
            law=self.LAW_NAME, trap_type="anchoring_bias", question_text=text,
            correct_answer=Q, correct_unit="C",
            variables={"C_uF": C_uF, "C_F": C_F, "V": V, "wrong_Q": wrong_Q},
            difficulty=difficulty,
            explanation=f"Q = CV = {C_F}×{V} = {Q}C, not {wrong_Q}C.",
        )

    def _series_parallel(self, C_uF, V, rng, difficulty):
        """Trap 3: Two capacitors in series; hint at using parallel formula."""
        C1_uF = C_uF
        C2_uF = round(rng.uniform(1, C_uF * 2), 2)
        # Series: 1/C_total = 1/C1 + 1/C2
        C1_F = C1_uF * 1e-6
        C2_F = C2_uF * 1e-6
        C_total_F = (C1_F * C2_F) / (C1_F + C2_F)
        Q = round(C_total_F * V, 10)

        parallel_C = C1_F + C2_F
        wrong_Q = round(parallel_C * V, 10)

        text = (
            f"Two capacitors ({C1_uF}μF and {C2_uF}μF) are connected in "
            f"series across {V}V. A student adds them (parallel formula) "
            f"to get Q = {wrong_Q:.6e}C. What is the correct charge?"
        )
        return Question(
            law=self.LAW_NAME, trap_type="series_parallel_confusion",
            question_text=text,
            correct_answer=Q, correct_unit="C",
            variables={"C1_uF": C1_uF, "C2_uF": C2_uF, "V": V,
                        "C_total_F": C_total_F},
            difficulty=difficulty,
            explanation=f"Series: 1/C = 1/C₁+1/C₂. C_total = {C_total_F:.6e}F. "
                        f"Q = CV = {Q}C.",
        )
