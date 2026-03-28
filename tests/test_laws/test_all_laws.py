"""
Tests for all remaining laws — ensure generation and verification works.
"""

import pytest

from lawbreaker.laws.kirchhoff_current import KirchhoffCurrentLaw
from lawbreaker.laws.kirchhoff_voltage import KirchhoffVoltageLaw
from lawbreaker.laws.kinetic_energy import KineticEnergyLaw
from lawbreaker.laws.energy_conservation import EnergyConservationLaw
from lawbreaker.laws.ideal_gas import IdealGasLaw
from lawbreaker.laws.power import PowerLaw
from lawbreaker.laws.coulomb import CoulombLaw
from lawbreaker.laws.hooke import HookeLaw
from lawbreaker.laws.gravitational_force import GravitationalForceLaw
from lawbreaker.laws.snell import SnellLaw
from lawbreaker.laws.bernoulli import BernoulliLaw
from lawbreaker.laws.centripetal import CentripetalForceLaw
from lawbreaker.laws.momentum import MomentumConservationLaw
from lawbreaker.laws.capacitance import CapacitanceLaw
from lawbreaker.laws.wave_speed import WaveSpeedLaw
from lawbreaker.laws.pendulum import PendulumLaw
from lawbreaker.laws.thermal_expansion import ThermalExpansionLaw
from lawbreaker.laws.stefan_boltzmann import StefanBoltzmannLaw
from lawbreaker.laws.drag_force import DragForceLaw
from lawbreaker.laws.lens_equation import LensEquationLaw
from lawbreaker.laws.boyle import BoyleLaw
from lawbreaker.laws.rc_circuit import RCCircuitLaw
from lawbreaker.laws.magnetic_force import MagneticForceLaw
from lawbreaker.laws.work_energy import WorkEnergyLaw
from lawbreaker.laws.specific_heat import SpecificHeatLaw
from lawbreaker.laws.gravitational_pe import GravitationalPELaw


ALL_LAWS = [
    KirchhoffCurrentLaw,
    KirchhoffVoltageLaw,
    KineticEnergyLaw,
    EnergyConservationLaw,
    IdealGasLaw,
    PowerLaw,
    CoulombLaw,
    HookeLaw,
    GravitationalForceLaw,
    SnellLaw,
    BernoulliLaw,
    CentripetalForceLaw,
    MomentumConservationLaw,
    CapacitanceLaw,
    WaveSpeedLaw,
    PendulumLaw,
    ThermalExpansionLaw,
    StefanBoltzmannLaw,
    DragForceLaw,
    LensEquationLaw,
    BoyleLaw,
    RCCircuitLaw,
    MagneticForceLaw,
    WorkEnergyLaw,
    SpecificHeatLaw,
    GravitationalPELaw,
]


@pytest.mark.parametrize("LawClass", ALL_LAWS, ids=lambda c: c.LAW_NAME)
class TestAllLaws:
    """Generic tests applied to every law implementation."""

    def test_generate_returns_question(self, LawClass):
        """Generate a question and verify it has required fields."""
        law = LawClass()
        q = law.generate(seed=42)
        assert q.law == law.LAW_NAME
        assert q.trap_type
        assert q.question_text
        assert q.correct_unit is not None
        assert q.explanation

    def test_verify_correct_answer(self, LawClass):
        """Verify method accepts the correct answer."""
        law = LawClass()
        q = law.generate(seed=42)
        assert law.verify(q.correct_answer, q) is True

    def test_verify_wrong_answer(self, LawClass):
        """Verify method rejects a clearly wrong answer."""
        law = LawClass()
        q = law.generate(seed=42)
        wrong = q.correct_answer * 100 + 999
        assert law.verify(wrong, q) is False

    def test_reproducibility(self, LawClass):
        """Same seed produces the same question."""
        law = LawClass()
        q1 = law.generate(seed=99)
        q2 = law.generate(seed=99)
        assert q1.correct_answer == q2.correct_answer
        assert q1.question_text == q2.question_text

    def test_all_difficulties(self, LawClass):
        """All difficulty levels produce valid questions."""
        law = LawClass()
        for diff in ("easy", "medium", "hard"):
            q = law.generate(difficulty=diff, seed=10)
            assert q.difficulty == diff
