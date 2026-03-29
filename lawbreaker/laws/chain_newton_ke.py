"""
Combined: Newton's 2nd → Kinetic Energy — F=ma then KE=½mv²

Multi-step: Given force F, mass m, and time t (from rest), find kinetic energy.
Requires: a = F/m, v = a×t, KE = ½mv²

Traps:
  1. missing_half: phrased to make LLM forget the ½ factor in KE
  2. unit_confusion: mass given in grams
  3. intermediate_anchoring: suggests a wrong velocity
"""

from __future__ import annotations

from typing import Optional

from sympy import Rational, N as sympy_N

from lawbreaker.core.question import Question
from lawbreaker.laws.base import BaseLaw


class ChainNewtonKELaw(BaseLaw):
    """Combined Newton → KE multi-step question generator."""

    LAW_NAME = "Force → Kinetic Energy"

    _RANGES = {
        "easy": {"F": (5, 50), "m": (1, 10), "t": (1, 5)},
        "medium": {"F": (10, 200), "m": (5, 50), "t": (2, 10)},
        "hard": {"F": (50, 500), "m": (10, 200), "t": (3, 15)},
    }

    def generate(self, difficulty: str = "medium", seed: Optional[int] = None) -> Question:
        rng = self._rng(seed)
        ranges = self._RANGES.get(difficulty, self._RANGES["medium"])
        trap = rng.choice(["missing_half", "unit_confusion", "intermediate_anchoring"])

        F = round(rng.uniform(*ranges["F"]), 2)
        m = round(rng.uniform(*ranges["m"]), 2)
        t = round(rng.uniform(*ranges["t"]), 2)

        if trap == "missing_half":
            return self._missing_half(F, m, t, rng, difficulty)
        elif trap == "unit_confusion":
            return self._unit_confusion(F, m, t, rng, difficulty)
        return self._intermediate_anchoring(F, m, t, rng, difficulty)

    def _compute(self, F, m, t):
        """Compute intermediate and final values."""
        a = float(sympy_N(Rational(str(F)) / Rational(str(m))))
        v = float(sympy_N(Rational(str(a)) * Rational(str(t))))
        KE = round(float(sympy_N(
            Rational(1, 2) * Rational(str(m)) * Rational(str(v)) ** 2
        )), 4)
        return round(a, 4), round(v, 4), KE

    def _missing_half(self, F, m, t, rng, difficulty):
        """Trap: phrasing nudges LLM to forget ½ in KE = ½mv²."""
        a, v, KE = self._compute(F, m, t)
        wrong_KE = round(m * v ** 2, 4)

        text = (
            f"A {F}N net force acts on a {m}kg object initially at rest for {t}s. "
            f"Find the acceleration, then the final velocity, then compute "
            f"the kinetic energy (recall: KE depends on mass and velocity squared)."
        )
        return Question(
            law=self.LAW_NAME, trap_type="missing_half", question_text=text,
            correct_answer=KE, correct_unit="J",
            variables={"F": F, "m": m, "t": t, "a": a, "v": v, "wrong_KE": wrong_KE},
            difficulty=difficulty,
            explanation=(
                f"Missing-half trap: hint 'mass and velocity squared' tempts mv². "
                f"Step 1: a = F/m = {F}/{m} = {a} m/s². "
                f"Step 2: v = at = {a}×{t} = {v} m/s. "
                f"Step 3: KE = ½mv² = ½×{m}×{v}² = {KE} J (not {wrong_KE} J)."
            ),
        )

    def _unit_confusion(self, F, m, t, rng, difficulty):
        """Trap: mass given in grams."""
        a, v, KE = self._compute(F, m, t)
        m_grams = round(m * 1000, 2)

        text = (
            f"A {F}N force is applied to a {m_grams}g object at rest for {t} seconds. "
            f"Determine the acceleration using Newton's second law, "
            f"find the final velocity, and then calculate the kinetic energy in joules."
        )
        return Question(
            law=self.LAW_NAME, trap_type="unit_confusion", question_text=text,
            correct_answer=KE, correct_unit="J",
            variables={"F": F, "m_kg": m, "m_grams": m_grams, "t": t, "a": a, "v": v},
            difficulty=difficulty,
            explanation=(
                f"Unit trap: {m_grams}g = {m}kg. "
                f"Step 1: a = F/m = {F}/{m} = {a} m/s². "
                f"Step 2: v = at = {a}×{t} = {v} m/s. "
                f"Step 3: KE = ½mv² = {KE} J."
            ),
        )

    def _intermediate_anchoring(self, F, m, t, rng, difficulty):
        """Trap: suggest a wrong intermediate velocity."""
        a, v, KE = self._compute(F, m, t)
        wrong_v = round(v * rng.uniform(1.5, 3.0), 2)
        wrong_KE = round(0.5 * m * wrong_v ** 2, 2)

        text = (
            f"A {m}kg object starts from rest. A net force of {F}N acts for {t}s. "
            f"A student claims the final velocity is {wrong_v} m/s. "
            f"Calculate the correct velocity and then the kinetic energy."
        )
        return Question(
            law=self.LAW_NAME, trap_type="intermediate_anchoring", question_text=text,
            correct_answer=KE, correct_unit="J",
            variables={"F": F, "m": m, "t": t, "wrong_v": wrong_v, "wrong_KE": wrong_KE},
            difficulty=difficulty,
            explanation=(
                f"Intermediate anchor: student's v = {wrong_v} m/s is wrong. "
                f"Step 1: a = F/m = {F}/{m} = {a} m/s². "
                f"Step 2: v = at = {a}×{t} = {v} m/s. "
                f"Step 3: KE = ½mv² = {KE} J (not {wrong_KE} J)."
            ),
        )
