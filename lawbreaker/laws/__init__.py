"""
Laws module — physics law implementations for adversarial question generation.

Each law subclasses BaseLaw and knows how to generate trap-laden questions
and verify answers symbolically.
"""

from lawbreaker.laws.base import BaseLaw
from lawbreaker.laws.ohm import OhmLaw
from lawbreaker.laws.kirchhoff_current import KirchhoffCurrentLaw
from lawbreaker.laws.kirchhoff_voltage import KirchhoffVoltageLaw
from lawbreaker.laws.newton_second import NewtonSecondLaw
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

# Combined / multi-step law chains
from lawbreaker.laws.chain_ohm_power import ChainOhmPowerLaw
from lawbreaker.laws.chain_newton_ke import ChainNewtonKELaw
from lawbreaker.laws.chain_pe_speed import ChainPESpeedLaw
from lawbreaker.laws.chain_ohm_kvl import ChainOhmKVLLaw
from lawbreaker.laws.chain_spring_launch import ChainSpringLaunchLaw
from lawbreaker.laws.chain_heat_height import ChainHeatHeightLaw

# Registry mapping short names to law classes
LAW_REGISTRY: dict[str, type[BaseLaw]] = {
    "ohm": OhmLaw,
    "kirchhoff_current": KirchhoffCurrentLaw,
    "kirchhoff_voltage": KirchhoffVoltageLaw,
    "newton_second": NewtonSecondLaw,
    "kinetic_energy": KineticEnergyLaw,
    "energy_conservation": EnergyConservationLaw,
    "ideal_gas": IdealGasLaw,
    "power": PowerLaw,
    "coulomb": CoulombLaw,
    "hooke": HookeLaw,
    "gravitational_force": GravitationalForceLaw,
    "snell": SnellLaw,
    "bernoulli": BernoulliLaw,
    "centripetal": CentripetalForceLaw,
    "momentum": MomentumConservationLaw,
    "capacitance": CapacitanceLaw,
    "wave_speed": WaveSpeedLaw,
    "pendulum": PendulumLaw,
    "thermal_expansion": ThermalExpansionLaw,
    "stefan_boltzmann": StefanBoltzmannLaw,
    "drag_force": DragForceLaw,
    "lens_equation": LensEquationLaw,
    "boyle": BoyleLaw,
    "rc_circuit": RCCircuitLaw,
    "magnetic_force": MagneticForceLaw,
    "work_energy": WorkEnergyLaw,
    "specific_heat": SpecificHeatLaw,
    "gravitational_pe": GravitationalPELaw,
    # Combined / multi-step chains
    "chain_ohm_power": ChainOhmPowerLaw,
    "chain_newton_ke": ChainNewtonKELaw,
    "chain_pe_speed": ChainPESpeedLaw,
    "chain_ohm_kvl": ChainOhmKVLLaw,
    "chain_spring_launch": ChainSpringLaunchLaw,
    "chain_heat_height": ChainHeatHeightLaw,
}

ALL_LAWS = list(LAW_REGISTRY.values())

__all__ = [
    "BaseLaw",
    "OhmLaw",
    "KirchhoffCurrentLaw",
    "KirchhoffVoltageLaw",
    "NewtonSecondLaw",
    "KineticEnergyLaw",
    "EnergyConservationLaw",
    "IdealGasLaw",
    "PowerLaw",
    "CoulombLaw",
    "HookeLaw",
    "GravitationalForceLaw",
    "SnellLaw",
    "BernoulliLaw",
    "CentripetalForceLaw",
    "MomentumConservationLaw",
    "CapacitanceLaw",
    "WaveSpeedLaw",
    "PendulumLaw",
    "ThermalExpansionLaw",
    "StefanBoltzmannLaw",
    "DragForceLaw",
    "LensEquationLaw",
    "BoyleLaw",
    "RCCircuitLaw",
    "MagneticForceLaw",
    "WorkEnergyLaw",
    "SpecificHeatLaw",
    "GravitationalPELaw",
    "ChainOhmPowerLaw",
    "ChainNewtonKELaw",
    "ChainPESpeedLaw",
    "ChainOhmKVLLaw",
    "ChainSpringLaunchLaw",
    "ChainHeatHeightLaw",
    "LAW_REGISTRY",
    "ALL_LAWS",
]
