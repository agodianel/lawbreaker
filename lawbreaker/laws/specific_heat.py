"""
Specific Heat — Q = mcΔT

Traps:
  1. celsius_kelvin_confusion: ΔT is the same in °C and K (LLM may convert)
  2. mass_unit_confusion: mass in grams vs kg
  3. anchoring_bias: suggests a wrong heat value
"""

from __future__ import annotations

from typing import Optional

from lawbreaker.core.question import Question
from lawbreaker.laws.base import BaseLaw


class SpecificHeatLaw(BaseLaw):
    """Specific Heat (Q = mcΔT) adversarial question generator."""

    LAW_NAME = "Specific Heat"

    _MATERIALS = {
        "water": 4186,
        "iron": 449,
        "copper": 385,
        "aluminium": 897,
        "lead": 128,
        "glass": 840,
    }

    _RANGES = {
        "easy": {"m": (0.1, 5), "dT": (5, 30)},
        "medium": {"m": (0.1, 20), "dT": (5, 100)},
        "hard": {"m": (0.5, 100), "dT": (10, 500)},
    }

    def generate(self, difficulty: str = "medium", seed: Optional[int] = None) -> Question:
        """Generate an adversarial specific heat question."""
        rng = self._rng(seed)
        ranges = self._RANGES.get(difficulty, self._RANGES["medium"])
        trap = rng.choice(["celsius_kelvin_confusion", "mass_unit_confusion", "anchoring_bias"])

        material = rng.choice(list(self._MATERIALS.keys()))
        c = self._MATERIALS[material]
        m = round(rng.uniform(*ranges["m"]), 3)
        dT = rng.randint(*ranges["dT"])

        if trap == "celsius_kelvin_confusion":
            return self._celsius_kelvin(material, c, m, dT, rng, difficulty)
        elif trap == "mass_unit_confusion":
            return self._mass_confusion(material, c, m, dT, rng, difficulty)
        return self._anchoring(material, c, m, dT, rng, difficulty)

    def _celsius_kelvin(self, material, c, m, dT, rng, difficulty):
        """Trap 1: Temperatures in °C but ΔT is unchanged by conversion."""
        Q = round(m * c * dT, 4)
        T1 = rng.randint(10, 50)
        T2 = T1 + dT

        text = (
            f"{m}kg of {material} (c = {c} J/kg·°C) is heated from "
            f"{T1}°C to {T2}°C. A student first converts to Kelvin: "
            f"{T1+273}K to {T2+273}K. What is the heat required in joules?"
        )
        return Question(
            law=self.LAW_NAME, trap_type="celsius_kelvin_confusion",
            question_text=text,
            correct_answer=Q, correct_unit="J",
            variables={"m": m, "c": c, "dT": dT, "material": material},
            difficulty=difficulty,
            explanation=f"ΔT = {dT}°C = {dT}K (difference is same). "
                        f"Q = mcΔT = {m}×{c}×{dT} = {Q}J.",
        )

    def _mass_confusion(self, material, c, m, dT, rng, difficulty):
        """Trap 2: Mass in grams but c is in J/(kg·°C)."""
        Q = round(m * c * dT, 4)
        m_g = round(m * 1000, 1)

        text = (
            f"How much heat is needed to raise {m_g}g of {material} "
            f"(c = {c} J/kg·°C) by {dT}°C?"
        )
        return Question(
            law=self.LAW_NAME, trap_type="mass_unit_confusion",
            question_text=text,
            correct_answer=Q, correct_unit="J",
            variables={"m_kg": m, "m_g": m_g, "c": c, "dT": dT},
            difficulty=difficulty,
            explanation=f"{m_g}g = {m}kg. Q = mcΔT = {m}×{c}×{dT} = {Q}J.",
        )

    def _anchoring(self, material, c, m, dT, rng, difficulty):
        """Trap 3: Suggest a wrong heat value."""
        Q = round(m * c * dT, 4)
        wrong_Q = round(Q * rng.uniform(1.5, 3.0), 2)

        text = (
            f"To heat {m}kg of {material} (c = {c} J/kg·°C) by {dT}°C, "
            f"an answer key says Q = {wrong_Q}J. "
            f"What is the correct value?"
        )
        return Question(
            law=self.LAW_NAME, trap_type="anchoring_bias", question_text=text,
            correct_answer=Q, correct_unit="J",
            variables={"m": m, "c": c, "dT": dT, "wrong_Q": wrong_Q},
            difficulty=difficulty,
            explanation=f"Q = mcΔT = {m}×{c}×{dT} = {Q}J.",
        )
