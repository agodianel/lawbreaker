"""
Linear Thermal Expansion — ΔL = α L₀ ΔT

Traps:
  1. celsius_kelvin_confusion: ΔT is the same in °C and K, but LLM may convert
  2. unit_confusion: length in mm vs m
  3. anchoring_bias: suggests a wrong expansion value
"""

from __future__ import annotations

from typing import Optional

from lawbreaker.core.question import Question
from lawbreaker.laws.base import BaseLaw


class ThermalExpansionLaw(BaseLaw):
    """Linear Thermal Expansion (ΔL = αL₀ΔT) adversarial question generator."""

    LAW_NAME = "Thermal Expansion"

    # Common coefficients (1/°C)
    _MATERIALS = {
        "steel": 12e-6,
        "aluminium": 23e-6,
        "copper": 17e-6,
        "brass": 19e-6,
        "iron": 12e-6,
    }

    _RANGES = {
        "easy": {"L": (0.5, 5), "dT": (10, 50)},
        "medium": {"L": (0.5, 20), "dT": (10, 200)},
        "hard": {"L": (1, 100), "dT": (50, 500)},
    }

    def generate(self, difficulty: str = "medium", seed: Optional[int] = None) -> Question:
        """Generate an adversarial thermal expansion question."""
        rng = self._rng(seed)
        ranges = self._RANGES.get(difficulty, self._RANGES["medium"])
        trap = rng.choice(["celsius_kelvin_confusion", "unit_confusion", "anchoring_bias"])

        material = rng.choice(list(self._MATERIALS.keys()))
        alpha = self._MATERIALS[material]
        L0 = round(rng.uniform(*ranges["L"]), 3)
        dT = rng.randint(*ranges["dT"])

        if trap == "celsius_kelvin_confusion":
            return self._celsius_kelvin(material, alpha, L0, dT, rng, difficulty)
        elif trap == "unit_confusion":
            return self._unit_confusion(material, alpha, L0, dT, rng, difficulty)
        return self._anchoring(material, alpha, L0, dT, rng, difficulty)

    def _celsius_kelvin(self, material, alpha, L0, dT, rng, difficulty):
        """Trap 1: States temp in °C. For ΔT, °C and K are equivalent."""
        dL = round(alpha * L0 * dT, 8)
        T1 = rng.randint(20, 100)
        T2 = T1 + dT

        text = (
            f"A {material} rod ({L0}m, α = {alpha:.1e}/°C) is heated from "
            f"{T1}°C to {T2}°C. A student converts to Kelvin first, making "
            f"ΔT = {T2 + 273} − {T1 + 273} = {dT}K. "
            f"What is the change in length in metres?"
        )
        return Question(
            law=self.LAW_NAME, trap_type="celsius_kelvin_confusion",
            question_text=text,
            correct_answer=dL, correct_unit="m",
            variables={"alpha": alpha, "L0": L0, "dT": dT, "material": material},
            difficulty=difficulty,
            explanation=f"ΔT is the same in °C and K. ΔL = αL₀ΔT = "
                        f"{alpha:.1e}×{L0}×{dT} = {dL}m.",
        )

    def _unit_confusion(self, material, alpha, L0, dT, rng, difficulty):
        """Trap 2: Length in mm, answer expected in metres."""
        dL = round(alpha * L0 * dT, 8)
        L0_mm = round(L0 * 1000, 1)

        text = (
            f"A {L0_mm}mm {material} rod (α = {alpha:.1e}/°C) undergoes "
            f"a temperature change of {dT}°C. "
            f"What is the change in length in metres?"
        )
        return Question(
            law=self.LAW_NAME, trap_type="unit_confusion", question_text=text,
            correct_answer=dL, correct_unit="m",
            variables={"alpha": alpha, "L0_m": L0, "L0_mm": L0_mm, "dT": dT},
            difficulty=difficulty,
            explanation=f"{L0_mm}mm = {L0}m. ΔL = {alpha:.1e}×{L0}×{dT} = {dL}m.",
        )

    def _anchoring(self, material, alpha, L0, dT, rng, difficulty):
        """Trap 3: Suggest a wrong change in length."""
        dL = round(alpha * L0 * dT, 8)
        wrong_dL = round(dL * rng.uniform(2, 10), 8)

        text = (
            f"A {material} bar ({L0}m, α = {alpha:.1e}/°C) is heated by "
            f"{dT}°C. A reference says ΔL = {wrong_dL:.6e}m. "
            f"What is the correct ΔL?"
        )
        return Question(
            law=self.LAW_NAME, trap_type="anchoring_bias", question_text=text,
            correct_answer=dL, correct_unit="m",
            variables={"alpha": alpha, "L0": L0, "dT": dT, "wrong_dL": wrong_dL},
            difficulty=difficulty,
            explanation=f"ΔL = αL₀ΔT = {alpha:.1e}×{L0}×{dT} = {dL}m.",
        )
