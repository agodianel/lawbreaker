"""
Kirchhoff's Voltage Law (KVL) — the sum of voltages around any closed loop
in a circuit equals zero.

Traps:
  1. missing_drop: implies one voltage drop is negligible when it is not
  2. polarity_confusion: mixes up voltage rise vs drop polarities
  3. anchoring_bias: suggests a wrong missing voltage
"""

from __future__ import annotations

from typing import Optional

from lawbreaker.core.question import Question
from lawbreaker.laws.base import BaseLaw


class KirchhoffVoltageLaw(BaseLaw):
    """KVL adversarial question generator."""

    LAW_NAME = "Kirchhoff's Voltage Law"

    _RANGES = {
        "easy": (1, 12),
        "medium": (5, 50),
        "hard": (10, 200),
    }

    def generate(self, difficulty: str = "medium", seed: Optional[int] = None) -> Question:
        """Generate an adversarial KVL question.

        Args:
            difficulty: One of ``"easy"``, ``"medium"``, ``"hard"``.
            seed: Optional random seed.

        Returns:
            A ``Question`` with one of three trap types.
        """
        rng = self._rng(seed)
        lo, hi = self._RANGES.get(difficulty, self._RANGES["medium"])
        trap = rng.choice(["missing_drop", "polarity_confusion", "anchoring_bias"])

        if trap == "missing_drop":
            return self._missing_drop(lo, hi, rng, difficulty)
        elif trap == "polarity_confusion":
            return self._polarity_confusion(lo, hi, rng, difficulty)
        else:
            return self._anchoring(lo, hi, rng, difficulty)

    def _missing_drop(self, lo: int, hi: int, rng, difficulty: str) -> Question:
        """Trap 1: One drop is labelled 'negligible' but is actually significant."""
        v_source = round(rng.uniform(lo * 2, hi), 2)
        v1 = round(rng.uniform(lo, v_source * 0.4), 2)
        v2 = round(rng.uniform(lo, v_source * 0.3), 2)
        v3_correct = round(v_source - v1 - v2, 4)

        text = (
            f"A series circuit has a {v_source}V source and three resistors. "
            f"The voltage drops across the first two resistors are {v1}V and {v2}V. "
            f"The technician says the third resistor's drop is negligible. "
            f"What is the actual voltage drop across the third resistor?"
        )
        return Question(
            law=self.LAW_NAME,
            trap_type="missing_drop",
            question_text=text,
            correct_answer=v3_correct,
            correct_unit="V",
            variables={"V_source": v_source, "V1": v1, "V2": v2},
            difficulty=difficulty,
            explanation=(
                f"Missing drop trap: V₃ = V_source − V₁ − V₂ = "
                f"{v_source} − {v1} − {v2} = {v3_correct}V, not negligible."
            ),
        )

    def _polarity_confusion(self, lo: int, hi: int, rng, difficulty: str) -> Question:
        """Trap 2: Describe all elements as 'voltage rises' to create sign ambiguity."""
        v_source = round(rng.uniform(lo * 2, hi), 2)
        v1 = round(rng.uniform(lo, v_source * 0.5), 2)
        v2_correct = round(v_source - v1, 4)

        text = (
            f"In a closed loop, a battery provides a voltage rise of {v_source}V. "
            f"Resistor R₁ causes a voltage rise of −{v1}V (i.e., a drop). "
            f"What is the voltage drop across resistor R₂?"
        )
        return Question(
            law=self.LAW_NAME,
            trap_type="polarity_confusion",
            question_text=text,
            correct_answer=v2_correct,
            correct_unit="V",
            variables={"V_source": v_source, "V1": v1},
            difficulty=difficulty,
            explanation=(
                f"Polarity trap: V₂ = V_source − V₁ = {v_source} − {v1} = {v2_correct}V."
            ),
        )

    def _anchoring(self, lo: int, hi: int, rng, difficulty: str) -> Question:
        """Trap 3: Suggest a wrong voltage for the unknown drop."""
        v_source = round(rng.uniform(lo * 2, hi), 2)
        v1 = round(rng.uniform(lo, v_source * 0.4), 2)
        v2 = round(rng.uniform(lo, v_source * 0.3), 2)
        v3_correct = round(v_source - v1 - v2, 4)
        wrong_v3 = round(v3_correct * rng.uniform(1.3, 2.0), 2)

        text = (
            f"A series loop has a {v_source}V source. The drops across R₁ and R₂ "
            f"are {v1}V and {v2}V respectively. A classmate says R₃ drops {wrong_v3}V. "
            f"What is the actual voltage drop across R₃?"
        )
        return Question(
            law=self.LAW_NAME,
            trap_type="anchoring_bias",
            question_text=text,
            correct_answer=v3_correct,
            correct_unit="V",
            variables={"V_source": v_source, "V1": v1, "V2": v2, "wrong_V3": wrong_v3},
            difficulty=difficulty,
            explanation=(
                f"Anchoring trap: V₃ = {v_source} − {v1} − {v2} = {v3_correct}V, "
                f"not {wrong_v3}V."
            ),
        )
