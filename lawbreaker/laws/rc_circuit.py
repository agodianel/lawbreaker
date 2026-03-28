"""
RC Time Constant — τ = RC, V(t) = V₀(1 − e^(−t/τ)) for charging

Traps:
  1. unit_confusion: capacitance in μF, resistance in kΩ
  2. discharge_vs_charge: confusing charge and discharge formulas
  3. anchoring_bias: suggests a wrong time constant
"""

from __future__ import annotations

import math
from typing import Optional

from lawbreaker.core.question import Question
from lawbreaker.laws.base import BaseLaw


class RCCircuitLaw(BaseLaw):
    """RC Circuit (τ = RC) adversarial question generator."""

    LAW_NAME = "RC Time Constant"

    _RANGES = {
        "easy": {"R_ohm": (100, 10000), "C_uF": (1, 100)},
        "medium": {"R_ohm": (100, 100000), "C_uF": (0.1, 1000)},
        "hard": {"R_ohm": (10, 1000000), "C_uF": (0.01, 10000)},
    }

    def generate(self, difficulty: str = "medium", seed: Optional[int] = None) -> Question:
        """Generate an adversarial RC circuit question."""
        rng = self._rng(seed)
        ranges = self._RANGES.get(difficulty, self._RANGES["medium"])
        trap = rng.choice(["unit_confusion", "discharge_vs_charge", "anchoring_bias"])

        R = rng.randint(*ranges["R_ohm"])
        C_uF = round(rng.uniform(*ranges["C_uF"]), 2)

        if trap == "unit_confusion":
            return self._unit_confusion(R, C_uF, rng, difficulty)
        elif trap == "discharge_vs_charge":
            return self._discharge_charge(R, C_uF, rng, difficulty)
        return self._anchoring(R, C_uF, rng, difficulty)

    def _unit_confusion(self, R, C_uF, rng, difficulty):
        """Trap 1: R in kΩ, C in μF — must convert to base units."""
        C_F = C_uF * 1e-6
        tau = round(R * C_F, 8)
        R_kOhm = round(R / 1000, 3)

        text = (
            f"An RC circuit has R = {R_kOhm}kΩ and C = {C_uF}μF. "
            f"What is the time constant τ in seconds?"
        )
        return Question(
            law=self.LAW_NAME, trap_type="unit_confusion", question_text=text,
            correct_answer=tau, correct_unit="s",
            variables={"R_ohm": R, "R_kOhm": R_kOhm, "C_uF": C_uF, "C_F": C_F},
            difficulty=difficulty,
            explanation=f"{R_kOhm}kΩ = {R}Ω, {C_uF}μF = {C_F}F. "
                        f"τ = RC = {R}×{C_F} = {tau}s.",
        )

    def _discharge_charge(self, R, C_uF, rng, difficulty):
        """Trap 2: Asks for voltage at time t during charging — not discharge."""
        C_F = C_uF * 1e-6
        tau = R * C_F
        V0 = round(rng.uniform(5, 50), 1)
        t_multiples = rng.choice([1, 2, 3])
        t = round(tau * t_multiples, 8)
        # Charging: V = V0(1 - e^(-t/tau))
        V_charge = round(V0 * (1 - math.exp(-t / tau)), 4)
        # Discharge: V = V0 * e^(-t/tau) — the wrong formula
        V_discharge = round(V0 * math.exp(-t / tau), 4)

        text = (
            f"An RC circuit (R = {R}Ω, C = {C_uF}μF) charges from V₀ = {V0}V. "
            f"After t = {t_multiples}τ, a student uses the discharge formula "
            f"V = V₀e^(−t/τ) = {V_discharge}V. "
            f"What is the correct voltage during charging?"
        )
        return Question(
            law=self.LAW_NAME, trap_type="discharge_vs_charge",
            question_text=text,
            correct_answer=V_charge, correct_unit="V",
            variables={"R": R, "C_uF": C_uF, "V0": V0, "t": t, "tau": tau},
            difficulty=difficulty,
            explanation=f"Charging: V = V₀(1−e^(−t/τ)) = {V0}×(1−e^(−{t_multiples})) "
                        f"= {V_charge}V.",
        )

    def _anchoring(self, R, C_uF, rng, difficulty):
        """Trap 3: Suggest a wrong time constant."""
        C_F = C_uF * 1e-6
        tau = round(R * C_F, 8)
        wrong_tau = round(tau * rng.uniform(2, 10), 8)

        text = (
            f"An RC circuit has R = {R}Ω and C = {C_uF}μF. "
            f"A calculator gives τ = {wrong_tau:.6e}s. "
            f"What is the correct time constant?"
        )
        return Question(
            law=self.LAW_NAME, trap_type="anchoring_bias", question_text=text,
            correct_answer=tau, correct_unit="s",
            variables={"R": R, "C_uF": C_uF, "C_F": C_F, "wrong_tau": wrong_tau},
            difficulty=difficulty,
            explanation=f"τ = RC = {R}×{C_F} = {tau}s.",
        )
