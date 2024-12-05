from __future__ import annotations

from dataclasses import dataclass

from .beam import Beam


@dataclass(frozen=True)
class Gun:
    """Class to store gun parameters."""

    acceleration_voltage: float
    """[V]"""

    energy_spread: float
    """[eV]"""

    crossover_size: float
    """[m]"""

    brightness: float
    """[A/m^2sr]"""

    current_density: float
    """[A/m^2]"""

    def get_beam(self) -> Beam:
        """Get a beam object originating from this gun.

        Returns
        -------
        Beam
            Initial electron beam
        """
        # TODO
        return Beam(a=self.crossover_size / 2, b=self.crossover_size / 2, t=0, x0=0, y0=0)

    # TODO account for more parameters


# Below values from Table 5.1 in Transmission Electron Microscopy by David B. Williams, C. Barry Carter
# We assume constant parameter values for all acceleration voltages, as the table has values at 100kV


@dataclass(frozen=True)
class TungstenGun(Gun):
    energy_spread: float = 3
    crossover_size: float = 1e-4
    brightness: float = 1e10
    current_density: float = 5


@dataclass(frozen=True)
class LaB6Gun(Gun):
    energy_spread: float = 1.5
    crossover_size: float = 1e-5
    brightness: float = 5e11
    current_density: float = 1e2


@dataclass(frozen=True)
class SchottkyFEG(Gun):
    energy_spread: float = 0.7
    crossover_size: float = 15e-9
    brightness: float = 5e12
    current_density: float = 1e5


@dataclass(frozen=True)
class ColdFEG(Gun):
    energy_spread: float = 0.3
    crossover_size: float = 3e-9
    brightness: float = 1e13
    current_density: float = 1e6
