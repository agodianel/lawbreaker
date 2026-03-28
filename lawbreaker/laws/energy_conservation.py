"""
Energy Conservation — E_in >= E_out  (first law of thermodynamics constraint)

Traps:
  1. output_exceeds_input: claims output > input — LLM should flag as impossible
  2. efficiency_over_100: scenario with >100% efficiency
  3. missing_heat_loss: ignores heat dissipation in the energy balance
"""

from __future__ import annotations

from typing import Optional

from lawbreaker.core.question import Question
from lawbreaker.laws.base import BaseLaw


class EnergyConservationLaw(BaseLaw):
    """Energy Conservation adversarial question generator."""

    LAW_NAME = "Energy Conservation"

    _RANGES = {
        "easy": {"power": (10, 100), "time": (1, 10)},
        "medium": {"power": (50, 500), "time": (1, 60)},
        "hard": {"power": (100, 5000), "time": (1, 120)},
    }

    def generate(self, difficulty: str = "medium", seed: Optional[int] = None) -> Question:
        """Generate an adversarial energy conservation question.

        Args:
            difficulty: One of ``"easy"``, ``"medium"``, ``"hard"``.
            seed: Optional random seed.

        Returns:
            A ``Question`` with one of three trap types.
        """
        rng = self._rng(seed)
        ranges = self._RANGES.get(difficulty, self._RANGES["medium"])
        trap = rng.choice(["output_exceeds_input", "efficiency_over_100", "missing_heat_loss"])

        if trap == "output_exceeds_input":
            return self._output_exceeds_input(ranges, rng, difficulty)
        elif trap == "efficiency_over_100":
            return self._efficiency_over_100(ranges, rng, difficulty)
        else:
            return self._missing_heat_loss(ranges, rng, difficulty)

    def _output_exceeds_input(self, ranges: dict, rng, difficulty: str) -> Question:
        """Trap 1: Output greater than input — correct answer is that this is impossible."""
        E_in = round(rng.uniform(*ranges["power"]), 2)
        E_out = round(E_in * rng.uniform(1.1, 1.5), 2)
        # The maximum possible output equals the input
        max_output = E_in

        text = (
            f"A machine receives {E_in}J of energy input. "
            f"The manufacturer claims it produces {E_out}J of useful work output. "
            f"What is the maximum possible energy output of this machine?"
        )
        return Question(
            law=self.LAW_NAME,
            trap_type="output_exceeds_input",
            question_text=text,
            correct_answer=round(max_output, 4),
            correct_unit="J",
            variables={"E_in": E_in, "E_out_claimed": E_out},
            difficulty=difficulty,
            explanation=(
                f"Output exceeds input trap: the claim of {E_out}J output from "
                f"{E_in}J input violates energy conservation. "
                f"Maximum possible output = {max_output}J."
            ),
        )

    def _efficiency_over_100(self, ranges: dict, rng, difficulty: str) -> Question:
        """Trap 2: Efficiency stated as >100% — LLM must compute the real efficiency."""
        E_in = round(rng.uniform(*ranges["power"]), 2)
        real_efficiency = round(rng.uniform(0.5, 0.95), 2)
        E_useful = round(E_in * real_efficiency, 4)
        fake_efficiency = round(rng.uniform(1.05, 1.3), 2)

        text = (
            f"A motor receives {E_in}J and produces {E_useful}J of useful work. "
            f"A student calculated the efficiency as {fake_efficiency * 100:.0f}%. "
            f"What is the actual efficiency as a decimal (0 to 1)?"
        )
        return Question(
            law=self.LAW_NAME,
            trap_type="efficiency_over_100",
            question_text=text,
            correct_answer=round(real_efficiency, 4),
            correct_unit="",
            variables={
                "E_in": E_in,
                "E_useful": E_useful,
                "fake_efficiency": fake_efficiency,
            },
            difficulty=difficulty,
            explanation=(
                f"Efficiency >100% trap: student claimed {fake_efficiency * 100:.0f}% but "
                f"η = E_useful / E_in = {E_useful} / {E_in} = {round(real_efficiency, 4)}."
            ),
        )

    def _missing_heat_loss(self, ranges: dict, rng, difficulty: str) -> Question:
        """Trap 3: Heat loss omitted — LLM must subtract it to get useful work."""
        E_in = round(rng.uniform(*ranges["power"]), 2)
        heat_fraction = round(rng.uniform(0.1, 0.4), 2)
        heat_loss = round(E_in * heat_fraction, 4)
        E_useful = round(E_in - heat_loss, 4)

        text = (
            f"An engine receives {E_in}J of fuel energy. "
            f"It loses {heat_fraction * 100:.0f}% of its energy as heat. "
            f"How much useful work does the engine produce?"
        )
        return Question(
            law=self.LAW_NAME,
            trap_type="missing_heat_loss",
            question_text=text,
            correct_answer=E_useful,
            correct_unit="J",
            variables={"E_in": E_in, "heat_fraction": heat_fraction, "heat_loss": heat_loss},
            difficulty=difficulty,
            explanation=(
                f"Missing heat loss trap: heat loss = {heat_fraction * 100:.0f}% of {E_in} = "
                f"{heat_loss}J. Useful work = {E_in} − {heat_loss} = {E_useful}J."
            ),
        )
