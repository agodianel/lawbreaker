"""
Electrical Power — P = VI

Traps:
  1. power_factor: confuses W with VA
  2. unit_confusion: mixes mW and W
  3. anchoring_bias: suggests wrong power value
"""

from __future__ import annotations
from typing import Optional
from sympy import Rational, N as sympy_N
from lawbreaker.core.question import Question
from lawbreaker.laws.base import BaseLaw


class PowerLaw(BaseLaw):
    """Electrical Power (P = VI) adversarial question generator."""

    LAW_NAME = "Power"
    _RANGES = {
        "easy": {"V": (5, 24), "I": (1, 5)},
        "medium": {"V": (12, 240), "I": (1, 20)},
        "hard": {"V": (100, 480), "I": (1, 50)},
    }

    def generate(self, difficulty: str = "medium", seed: Optional[int] = None) -> Question:
        """Generate an adversarial electrical power question."""
        rng = self._rng(seed)
        ranges = self._RANGES.get(difficulty, self._RANGES["medium"])
        trap = rng.choice(["power_factor", "unit_confusion", "anchoring_bias"])
        V = round(rng.uniform(*ranges["V"]), 2)
        I = round(rng.uniform(*ranges["I"]), 2)
        if trap == "power_factor":
            return self._power_factor(V, I, rng, difficulty)
        elif trap == "unit_confusion":
            return self._unit_confusion(V, I, rng, difficulty)
        return self._anchoring(V, I, rng, difficulty)

    def _power_factor(self, V, I, rng, difficulty):
        """Trap 1: Apparent power given but real power requested."""
        P_app = round(float(sympy_N(Rational(str(V)) * Rational(str(I)))), 4)
        pf = round(rng.uniform(0.6, 0.95), 2)
        P_real = round(P_app * pf, 4)
        text = (f"A load draws {I}A at {V}V with a power factor of {pf}. "
                f"The apparent power is {P_app} VA. What is the real power in watts?")
        return Question(law=self.LAW_NAME, trap_type="power_factor", question_text=text,
                        correct_answer=P_real, correct_unit="W",
                        variables={"V": V, "I": I, "pf": pf, "P_apparent": P_app},
                        difficulty=difficulty,
                        explanation=f"P_real = {P_app} × {pf} = {P_real}W.")

    def _unit_confusion(self, V, I, rng, difficulty):
        """Trap 2: Current given in mA."""
        I_mA = round(I * 1000, 2)
        P = round(float(sympy_N(Rational(str(V)) * Rational(str(I)))), 4)
        text = (f"A device operates at {V}V with a current of {I_mA} mA. "
                f"What is the power consumption in watts?")
        return Question(law=self.LAW_NAME, trap_type="unit_confusion", question_text=text,
                        correct_answer=P, correct_unit="W",
                        variables={"V": V, "I_mA": I_mA, "I_A": I},
                        difficulty=difficulty,
                        explanation=f"{I_mA} mA = {I} A. P = {V} × {I} = {P}W.")

    def _anchoring(self, V, I, rng, difficulty):
        """Trap 3: Suggest a wrong power value."""
        P = round(float(sympy_N(Rational(str(V)) * Rational(str(I)))), 4)
        wrong_P = round(P * rng.uniform(1.3, 2.5), 1)
        text = (f"A circuit at {V}V draws {I}A. An engineer estimates {wrong_P}W. "
                f"What is the actual power?")
        return Question(law=self.LAW_NAME, trap_type="anchoring_bias", question_text=text,
                        correct_answer=P, correct_unit="W",
                        variables={"V": V, "I": I, "wrong_P": wrong_P},
                        difficulty=difficulty,
                        explanation=f"P = VI = {V} × {I} = {P}W, not {wrong_P}W.")
