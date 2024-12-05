from __future__ import annotations

from dataclasses import dataclass

from .beam import Beam
from .optical_component import OpticalComponent


@dataclass
class Aperture(OpticalComponent):
    x: float
    """[m]"""

    y: float
    """[m]"""

    radii: list[float]
    """[m]"""

    index: int = 0

    inserted: bool = False

    def radius(self) -> float:
        """Get the radius of the current aperture, in m."""
        return self.radii[self.index]

    def propagate_beam(self, beam: Beam):
        """Pass a beam through the aperture.

        Parameters
        ----------
        beam : Beam
            Beam to pass

        Returns
        -------
        Beam
            New beam, after passing through the aperture
        """
        # TODO
        return super().propagate_beam(beam)
