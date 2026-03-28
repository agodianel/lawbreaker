"""
Stefan–Boltzmann Law — P = σAT⁴

Traps:
  1. celsius_trap: temperature in °C instead of K
  2. forget_t4: uses T instead of T⁴
  3. area_unit_confusion: area in cm² vs m²
"""

from __future__ import annotations

from typing import Optional

from lawbreaker.core.question import Question
from lawbreaker.laws.base import BaseLaw


class StefanBoltzmannLaw(BaseLaw):
    """Stefan–Boltzmann Law (P = σAT⁴) adversarial question generator."""

    LAW_NAME = "Stefan-Boltzmann Law"
    SIGMA = 5.670374419e-8  # W·m⁻²·K⁻⁴

    _RANGES = {
        "easy": {"T_C": (100, 500), "A": (0.01, 1.0)},
        "medium": {"T_C": (200, 1500), "A": (0.001, 5.0)},
        "hard": {"T_C": (500, 5000), "A": (0.0001, 10.0)},
    }

    def generate(self, difficulty: str = "medium", seed: Optional[int] = None) -> Question:
        """Generate an adversarial Stefan-Boltzmann question."""
        rng = self._rng(seed)
        ranges = self._RANGES.get(difficulty, self._RANGES["medium"])
        trap = rng.choice(["celsius_trap", "forget_t4", "area_unit_confusion"])

        T_C = rng.randint(*ranges["T_C"])
        A = round(rng.uniform(*ranges["A"]), 4)
        T_K = T_C + 273.15

        if trap == "celsius_trap":
            return self._celsius_trap(T_C, T_K, A, rng, difficulty)
        elif trap == "forget_t4":
            return self._forget_t4(T_C, T_K, A, rng, difficulty)
        return self._area_confusion(T_C, T_K, A, rng, difficulty)

    def _celsius_trap(self, T_C, T_K, A, rng, difficulty):
        """Trap 1: Temperature given in °C; must convert to K for T⁴."""
        P = round(self.SIGMA * A * T_K**4, 4)

        text = (
            f"A blackbody with surface area {A}m² has a temperature of "
            f"{T_C}°C. What is the total radiated power in watts? "
            f"(σ = 5.67×10⁻⁸ W·m⁻²·K⁻⁴)"
        )
        return Question(
            law=self.LAW_NAME, trap_type="celsius_trap", question_text=text,
            correct_answer=P, correct_unit="W",
            variables={"T_C": T_C, "T_K": T_K, "A": A, "sigma": self.SIGMA},
            difficulty=difficulty,
            explanation=f"Must convert to Kelvin: {T_C}°C = {T_K}K. "
                        f"P = σAT⁴ = {P}W.",
        )

    def _forget_t4(self, T_C, T_K, A, rng, difficulty):
        """Trap 2: Uses T instead of T⁴."""
        P = round(self.SIGMA * A * T_K**4, 4)
        wrong_P = round(self.SIGMA * A * T_K, 4)

        text = (
            f"A body (A = {A}m², T = {T_K}K) radiates. A student uses "
            f"P = σAT = {wrong_P}W. What is the correct power using "
            f"P = σAT⁴?"
        )
        return Question(
            law=self.LAW_NAME, trap_type="forget_t4", question_text=text,
            correct_answer=P, correct_unit="W",
            variables={"T_K": T_K, "A": A, "sigma": self.SIGMA},
            difficulty=difficulty,
            explanation=f"P = σAT⁴, not σAT. P = {self.SIGMA:.4e}×{A}×{T_K}⁴ = {P}W.",
        )

    def _area_confusion(self, T_C, T_K, A, rng, difficulty):
        """Trap 3: Area in cm² instead of m²."""
        P = round(self.SIGMA * A * T_K**4, 4)
        A_cm2 = round(A * 1e4, 2)

        text = (
            f"A surface of {A_cm2}cm² at {T_K}K radiates as a blackbody. "
            f"What is the power emitted in watts? "
            f"(σ = 5.67×10⁻⁸ W·m⁻²·K⁻⁴)"
        )
        return Question(
            law=self.LAW_NAME, trap_type="area_unit_confusion", question_text=text,
            correct_answer=P, correct_unit="W",
            variables={"T_K": T_K, "A_m2": A, "A_cm2": A_cm2},
            difficulty=difficulty,
            explanation=f"{A_cm2}cm² = {A}m². P = σAT⁴ = {P}W.",
        )
