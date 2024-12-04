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
    """[nm]"""

    def get_beam(self) -> Beam:
        """Get a beam object originating from this gun.

        Returns
        -------
        Beam
            Initial electron beam
        """
        # TODO
        return Beam()

    # TODO account for more parameters


# Below values from Table 5.1 in Transmission Electron Microscopy by David B. Williams, C. Barry Carter
# We assume constant parameter values for all acceleration voltages, as the table has values at 100kV


@dataclass(frozen=True)
class TungstenGun(Gun):
    energy_spread: float = 3
    crossover_size: float = 10e5


@dataclass(frozen=True)
class LaB6Gun(Gun):
    energy_spread: float = 1.5
    crossover_size: float = 10e4


@dataclass(frozen=True)
class SchottkyFEG(Gun):
    energy_spread: float = 0.7
    crossover_size: float = 15


@dataclass(frozen=True)
class ColdFEG(Gun):
    energy_spread: float = 0.3
    crossover_size: float = 3
