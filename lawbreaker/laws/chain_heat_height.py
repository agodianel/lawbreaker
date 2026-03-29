"""
Combined: Specific Heat → Gravitational PE — Q = mcΔT then h = Q/(mg)

Multi-step: Energy used to heat a mass could instead lift it.
How high could that energy lift the same mass?
Requires: Q = mcΔT, h = Q/(mg)

Traps:
  1. celsius_kelvin: temperature change given in context that
     confuses absolute temperature with temperature difference
  2. unit_confusion: mass given in grams
  3. anchoring_bias: suggests a wrong height
"""

from __future__ import annotations

from typing import Optional

from sympy import Rational, N as sympy_N

from lawbreaker.core.question import Question
from lawbreaker.laws.base import BaseLaw


class ChainHeatHeightLaw(BaseLaw):
    """Combined Specific Heat → PE height question generator."""

    LAW_NAME = "Heat → Height"
    G = 9.81

    # Specific heat of water in J/(kg·K)
    C_WATER = 4186

    _RANGES = {
        "easy": {"m": (0.5, 5), "dT": (1, 10)},
        "medium": {"m": (1, 20), "dT": (5, 50)},
        "hard": {"m": (5, 100), "dT": (10, 100)},
    }

    def generate(self, difficulty: str = "medium", seed: Optional[int] = None) -> Question:
        rng = self._rng(seed)
        ranges = self._RANGES.get(difficulty, self._RANGES["medium"])
        trap = rng.choice(["celsius_kelvin", "unit_confusion", "anchoring_bias"])

        m = round(rng.uniform(*ranges["m"]), 2)
        dT = round(rng.uniform(*ranges["dT"]), 1)

        if trap == "celsius_kelvin":
            return self._celsius_kelvin(m, dT, rng, difficulty)
        elif trap == "unit_confusion":
            return self._unit_confusion(m, dT, rng, difficulty)
        return self._anchoring(m, dT, rng, difficulty)

    def _compute(self, m, dT):
        Q = float(sympy_N(
            Rational(str(m)) * Rational(self.C_WATER) * Rational(str(dT))
        ))
        h = round(float(sympy_N(
            Rational(str(Q)) / (Rational(str(m)) * Rational(str(self.G)))
        )), 4)
        return round(Q, 4), h

    def _celsius_kelvin(self, m, dT, rng, difficulty):
        """Trap: gives initial and final T in °C, tempting conversion to K."""
        Q, h = self._compute(m, dT)
        T_initial = round(rng.uniform(15, 30), 1)
        T_final = round(T_initial + dT, 1)

        text = (
            f"{m}kg of water is heated from {T_initial}°C to {T_final}°C "
            f"(specific heat c = {self.C_WATER} J/(kg·K)). "
            f"If that same energy were used to lift the {m}kg of water "
            f"against gravity (g = {self.G} m/s²), how high could it go?"
        )
        return Question(
            law=self.LAW_NAME, trap_type="celsius_kelvin", question_text=text,
            correct_answer=h, correct_unit="m",
            variables={"m": m, "dT": dT, "T_initial": T_initial, "T_final": T_final},
            difficulty=difficulty,
            explanation=(
                f"Celsius/Kelvin trap: ΔT = {T_final} - {T_initial} = {dT}°C = {dT} K "
                f"(temperature differences are the same). LLMs may convert to absolute K. "
                f"Step 1: Q = mcΔT = {m}×{self.C_WATER}×{dT} = {Q} J. "
                f"Step 2: h = Q/(mg) = {Q}/({m}×{self.G}) = {h} m."
            ),
        )

    def _unit_confusion(self, m, dT, rng, difficulty):
        """Trap: mass given in grams."""
        Q, h = self._compute(m, dT)
        m_grams = round(m * 1000, 2)

        text = (
            f"{m_grams}g of water is heated by {dT}°C "
            f"(c = {self.C_WATER} J/(kg·K)). "
            f"Calculate the heat energy absorbed, then determine how high "
            f"this energy could lift the same mass against gravity "
            f"(g = {self.G} m/s²)."
        )
        return Question(
            law=self.LAW_NAME, trap_type="unit_confusion", question_text=text,
            correct_answer=h, correct_unit="m",
            variables={"m_kg": m, "m_grams": m_grams, "dT": dT},
            difficulty=difficulty,
            explanation=(
                f"Unit trap: {m_grams}g = {m}kg. "
                f"Step 1: Q = mcΔT = {m}×{self.C_WATER}×{dT} = {Q} J. "
                f"Step 2: h = Q/(mg) = {Q}/({m}×{self.G}) = {h} m."
            ),
        )

    def _anchoring(self, m, dT, rng, difficulty):
        """Trap: suggest a wrong height."""
        Q, h = self._compute(m, dT)
        wrong_h = round(h * rng.uniform(0.3, 0.7), 1)

        text = (
            f"{m}kg of water is heated by {dT}°C (c = {self.C_WATER} J/(kg·K)). "
            f"An estimate suggests this energy could lift the water to {wrong_h}m. "
            f"First compute the heat energy, then find the actual height "
            f"it could reach (g = {self.G} m/s²)."
        )
        return Question(
            law=self.LAW_NAME, trap_type="anchoring_bias", question_text=text,
            correct_answer=h, correct_unit="m",
            variables={"m": m, "dT": dT, "wrong_h": wrong_h},
            difficulty=difficulty,
            explanation=(
                f"Anchoring trap: {wrong_h}m is wrong. "
                f"Step 1: Q = mcΔT = {m}×{self.C_WATER}×{dT} = {Q} J. "
                f"Step 2: h = Q/(mg) = {Q}/({m}×{self.G}) = {h} m."
            ),
        )
