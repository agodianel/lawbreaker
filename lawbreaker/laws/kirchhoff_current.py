"""
Kirchhoff's Current Law (KCL) — the sum of currents entering a node equals
the sum of currents leaving it.

Traps:
  1. missing_branch: implies a 4th branch current is zero when it is not
  2. sign_confusion: all currents described as "flowing in"
  3. anchoring_bias: anchors to a plausible-but-wrong missing current
"""

from __future__ import annotations

from typing import Optional

from lawbreaker.core.question import Question
from lawbreaker.laws.base import BaseLaw


class KirchhoffCurrentLaw(BaseLaw):
    """KCL adversarial question generator."""

    LAW_NAME = "Kirchhoff's Current Law"

    _RANGES = {
        "easy": (1, 10),
        "medium": (1, 30),
        "hard": (1, 100),
    }

    def generate(self, difficulty: str = "medium", seed: Optional[int] = None) -> Question:
        """Generate an adversarial KCL question.

        Args:
            difficulty: One of ``"easy"``, ``"medium"``, ``"hard"``.
            seed: Optional random seed.

        Returns:
            A ``Question`` with one of three trap types.
        """
        rng = self._rng(seed)
        lo, hi = self._RANGES.get(difficulty, self._RANGES["medium"])
        trap = rng.choice(["missing_branch", "sign_confusion", "anchoring_bias"])

        if trap == "missing_branch":
            return self._missing_branch(lo, hi, rng, difficulty)
        elif trap == "sign_confusion":
            return self._sign_confusion(lo, hi, rng, difficulty)
        else:
            return self._anchoring(lo, hi, rng, difficulty)

    def _missing_branch(self, lo: int, hi: int, rng, difficulty: str) -> Question:
        """Trap 1: Three currents given, fourth needed, but question implies it could be zero."""
        i1 = round(rng.uniform(lo, hi), 2)
        i2 = round(rng.uniform(lo, hi), 2)
        i3 = round(rng.uniform(lo, hi), 2)
        # i1 flows in, i2 flows in, i3 flows out, i4 flows out
        i4_correct = round(i1 + i2 - i3, 4)

        text = (
            f"At a node in a circuit, three branch currents are measured: "
            f"I₁ = {i1}A flows in, I₂ = {i2}A flows in, and I₃ = {i3}A flows out. "
            f"There is a fourth branch that the technician says carries negligible current. "
            f"What is the actual current in the fourth branch (positive = flowing out)?"
        )
        return Question(
            law=self.LAW_NAME,
            trap_type="missing_branch",
            question_text=text,
            correct_answer=i4_correct,
            correct_unit="A",
            variables={"I1": i1, "I2": i2, "I3": i3},
            difficulty=difficulty,
            explanation=(
                f"Missing branch trap: the technician says it's negligible but "
                f"I₄ = I₁ + I₂ − I₃ = {i1} + {i2} − {i3} = {i4_correct}A."
            ),
        )

    def _sign_confusion(self, lo: int, hi: int, rng, difficulty: str) -> Question:
        """Trap 2: All currents described as flowing in, violating KCL unless one flows out."""
        i1 = round(rng.uniform(lo, hi), 2)
        i2 = round(rng.uniform(lo, hi), 2)
        i3 = round(rng.uniform(lo, hi), 2)
        # If all truly flow in, the net outgoing current must equal their sum
        i_out_correct = round(i1 + i2 + i3, 4)

        text = (
            f"At a junction, three wires each carry current INTO the node: "
            f"I₁ = {i1}A, I₂ = {i2}A, I₃ = {i3}A. "
            f"A single wire carries current away from the node. "
            f"What is the current in that wire?"
        )
        return Question(
            law=self.LAW_NAME,
            trap_type="sign_confusion",
            question_text=text,
            correct_answer=i_out_correct,
            correct_unit="A",
            variables={"I1": i1, "I2": i2, "I3": i3},
            difficulty=difficulty,
            explanation=(
                f"Sign confusion trap: all currents flow in so the outgoing current "
                f"must equal the total: {i1} + {i2} + {i3} = {i_out_correct}A."
            ),
        )

    def _anchoring(self, lo: int, hi: int, rng, difficulty: str) -> Question:
        """Trap 3: A plausible-but-wrong suggestion for the missing current."""
        i1 = round(rng.uniform(lo, hi), 2)
        i2 = round(rng.uniform(lo, hi), 2)
        i3 = round(rng.uniform(lo, hi), 2)
        i4_correct = round(i1 + i2 - i3, 4)
        wrong_i4 = round(i4_correct * rng.uniform(1.3, 2.0), 2)

        text = (
            f"At a circuit node: I₁ = {i1}A (in), I₂ = {i2}A (in), I₃ = {i3}A (out). "
            f"An online calculator suggests the fourth branch current is {wrong_i4}A (out). "
            f"What is the correct current in the fourth branch (positive = out)?"
        )
        return Question(
            law=self.LAW_NAME,
            trap_type="anchoring_bias",
            question_text=text,
            correct_answer=i4_correct,
            correct_unit="A",
            variables={"I1": i1, "I2": i2, "I3": i3, "wrong_I4": wrong_i4},
            difficulty=difficulty,
            explanation=(
                f"Anchoring trap: the calculator is wrong. "
                f"I₄ = I₁ + I₂ − I₃ = {i1} + {i2} − {i3} = {i4_correct}A."
            ),
        )
