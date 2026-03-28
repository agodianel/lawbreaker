"""
Wave Speed Equation — v = fλ

Traps:
  1. unit_confusion: frequency in kHz vs Hz
  2. wavelength_confusion: wavelength in cm vs m
  3. anchoring_bias: suggests a wrong wave speed
"""

from __future__ import annotations

from typing import Optional

from lawbreaker.core.question import Question
from lawbreaker.laws.base import BaseLaw


class WaveSpeedLaw(BaseLaw):
    """Wave Speed (v = fλ) adversarial question generator."""

    LAW_NAME = "Wave Speed"

    _RANGES = {
        "easy": {"f": (100, 1000), "lam": (0.1, 5.0)},
        "medium": {"f": (500, 10000), "lam": (0.01, 10.0)},
        "hard": {"f": (1000, 1e6), "lam": (0.001, 50)},
    }

    def generate(self, difficulty: str = "medium", seed: Optional[int] = None) -> Question:
        """Generate an adversarial wave speed question."""
        rng = self._rng(seed)
        ranges = self._RANGES.get(difficulty, self._RANGES["medium"])
        trap = rng.choice(["unit_confusion", "wavelength_confusion", "anchoring_bias"])

        f = round(rng.uniform(*ranges["f"]), 2)
        lam = round(rng.uniform(*ranges["lam"]), 4)

        if trap == "unit_confusion":
            return self._unit_confusion(f, lam, rng, difficulty)
        elif trap == "wavelength_confusion":
            return self._wavelength_confusion(f, lam, rng, difficulty)
        return self._anchoring(f, lam, rng, difficulty)

    def _unit_confusion(self, f, lam, rng, difficulty):
        """Trap 1: Frequency in kHz but wavelength in m."""
        v = round(f * lam, 4)
        f_kHz = round(f / 1000, 4)

        text = (
            f"A wave has frequency {f_kHz} kHz and wavelength {lam}m. "
            f"What is the wave speed in m/s?"
        )
        return Question(
            law=self.LAW_NAME, trap_type="unit_confusion", question_text=text,
            correct_answer=v, correct_unit="m/s",
            variables={"f_Hz": f, "f_kHz": f_kHz, "lambda": lam},
            difficulty=difficulty,
            explanation=f"{f_kHz} kHz = {f} Hz. v = fλ = {f}×{lam} = {v} m/s.",
        )

    def _wavelength_confusion(self, f, lam, rng, difficulty):
        """Trap 2: Wavelength in cm; must convert to m."""
        v = round(f * lam, 4)
        lam_cm = round(lam * 100, 2)

        text = (
            f"A wave oscillates at {f} Hz with a wavelength of {lam_cm} cm. "
            f"What is the wave speed in m/s?"
        )
        return Question(
            law=self.LAW_NAME, trap_type="wavelength_confusion", question_text=text,
            correct_answer=v, correct_unit="m/s",
            variables={"f": f, "lambda_m": lam, "lambda_cm": lam_cm},
            difficulty=difficulty,
            explanation=f"{lam_cm}cm = {lam}m. v = fλ = {f}×{lam} = {v} m/s.",
        )

    def _anchoring(self, f, lam, rng, difficulty):
        """Trap 3: Suggest a wrong wave speed."""
        v = round(f * lam, 4)
        wrong_v = round(v * rng.uniform(1.3, 2.5), 2)

        text = (
            f"A wave has f = {f} Hz and λ = {lam}m. A textbook answer "
            f"says the speed is {wrong_v} m/s. What is the correct speed?"
        )
        return Question(
            law=self.LAW_NAME, trap_type="anchoring_bias", question_text=text,
            correct_answer=v, correct_unit="m/s",
            variables={"f": f, "lambda": lam, "wrong_v": wrong_v},
            difficulty=difficulty,
            explanation=f"v = fλ = {f}×{lam} = {v} m/s, not {wrong_v}.",
        )
