"""
Ideal Gas Law — PV = nRT

Traps:
  1. celsius_trap: temperature given in Celsius — must convert to Kelvin
  2. pressure_unit_confusion: pressure in atm vs Pa
  3. anchoring_bias: suggests a wrong temperature value
"""

from __future__ import annotations

from typing import Optional

from sympy import Rational, N as sympy_N

from lawbreaker.core.question import Question
from lawbreaker.laws.base import BaseLaw


class IdealGasLaw(BaseLaw):
    """Ideal Gas Law (PV = nRT) adversarial question generator."""

    LAW_NAME = "Ideal Gas Law"
    R_CONST = 8.314  # J/(mol·K)
    R_ATM = 0.08206  # L·atm/(mol·K)

    _RANGES = {
        "easy": {"n": (1, 5), "T_C": (20, 100)},
        "medium": {"n": (1, 20), "T_C": (0, 500)},
        "hard": {"n": (1, 50), "T_C": (-50, 1000)},
    }

    def generate(self, difficulty: str = "medium", seed: Optional[int] = None) -> Question:
        """Generate an adversarial Ideal Gas Law question.

        Args:
            difficulty: One of ``"easy"``, ``"medium"``, ``"hard"``.
            seed: Optional random seed.

        Returns:
            A ``Question`` with one of three trap types.
        """
        rng = self._rng(seed)
        ranges = self._RANGES.get(difficulty, self._RANGES["medium"])
        trap = rng.choice(["celsius_trap", "pressure_unit_confusion", "anchoring_bias"])

        n = round(rng.uniform(*ranges["n"]), 2)
        T_C = round(rng.uniform(*ranges["T_C"]), 1)
        T_K = round(T_C + 273.15, 2)

        if trap == "celsius_trap":
            return self._celsius_trap(n, T_C, T_K, rng, difficulty)
        elif trap == "pressure_unit_confusion":
            return self._pressure_confusion(n, T_C, T_K, rng, difficulty)
        else:
            return self._anchoring(n, T_C, T_K, rng, difficulty)

    def _celsius_trap(self, n: float, T_C: float, T_K: float, rng, difficulty: str) -> Question:
        """Trap 1: Temperature given in Celsius — LLM must convert to Kelvin."""
        P = round(rng.uniform(1, 10), 2)  # atm
        # V = nRT/P in litres (using R in L·atm/(mol·K))
        V_correct = round(float(sympy_N(
            Rational(str(n)) * Rational(str(self.R_ATM)) * Rational(str(T_K)) / Rational(str(P))
        )), 4)

        text = (
            f"{n} moles of an ideal gas are at a pressure of {P} atm and a "
            f"temperature of {T_C}°C. What is the volume of the gas in litres?"
        )
        return Question(
            law=self.LAW_NAME,
            trap_type="celsius_trap",
            question_text=text,
            correct_answer=V_correct,
            correct_unit="L",
            variables={"n": n, "P_atm": P, "T_C": T_C, "T_K": T_K, "R": self.R_ATM},
            difficulty=difficulty,
            explanation=(
                f"Celsius trap: T must be in Kelvin. {T_C}°C = {T_K}K. "
                f"V = nRT/P = {n} × {self.R_ATM} × {T_K} / {P} = {V_correct}L. "
                f"Using °C directly would give a wildly wrong answer."
            ),
        )

    def _pressure_confusion(self, n: float, T_C: float, T_K: float, rng, difficulty: str) -> Question:
        """Trap 2: Pressure in atm but R constant in SI (Pa) — unit mismatch."""
        P_atm = round(rng.uniform(1, 5), 2)
        P_Pa = round(P_atm * 101325, 2)
        # Use SI units: V in m³
        V_correct = round(float(sympy_N(
            Rational(str(n)) * Rational(str(self.R_CONST)) * Rational(str(T_K)) / Rational(str(P_Pa))
        )), 6)

        text = (
            f"{n} moles of gas at {T_K}K and {P_atm} atm. "
            f"Using R = {self.R_CONST} J/(mol·K), what is the volume in m³?"
        )
        return Question(
            law=self.LAW_NAME,
            trap_type="pressure_unit_confusion",
            question_text=text,
            correct_answer=V_correct,
            correct_unit="m³",
            variables={"n": n, "P_atm": P_atm, "P_Pa": P_Pa, "T_K": T_K},
            difficulty=difficulty,
            explanation=(
                f"Pressure unit trap: P must be in Pa when using R = 8.314. "
                f"{P_atm} atm = {P_Pa} Pa. V = nRT/P = {V_correct} m³. "
                f"Using atm directly with SI R gives a wrong result."
            ),
        )

    def _anchoring(self, n: float, T_C: float, T_K: float, rng, difficulty: str) -> Question:
        """Trap 3: Anchor to a wrong temperature for the PV calculation."""
        P = round(rng.uniform(1, 10), 2)
        V_correct = round(float(sympy_N(
            Rational(str(n)) * Rational(str(self.R_ATM)) * Rational(str(T_K)) / Rational(str(P))
        )), 4)
        wrong_T = round(T_K * rng.uniform(0.5, 0.8), 1)

        text = (
            f"{n} moles of gas at {P} atm. The temperature is {T_K}K, although "
            f"an earlier reading showed {wrong_T}K. What is the volume in litres?"
        )
        return Question(
            law=self.LAW_NAME,
            trap_type="anchoring_bias",
            question_text=text,
            correct_answer=V_correct,
            correct_unit="L",
            variables={"n": n, "P_atm": P, "T_K": T_K, "wrong_T": wrong_T},
            difficulty=difficulty,
            explanation=(
                f"Anchoring trap: use {T_K}K not {wrong_T}K. "
                f"V = nRT/P = {n} × {self.R_ATM} × {T_K} / {P} = {V_correct}L."
            ),
        )
