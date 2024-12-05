from __future__ import annotations

from dataclasses import dataclass

from .beam import Beam
from .optical_component import OpticalComponent


@dataclass
class Deflector(OpticalComponent):
    x: float = 0
    """[m]"""

    y: float = 0
    """[m]"""

    @property
    def position(self) -> tuple[float, float]:
        return (self.x, self.y)

    def propagate_beam(self, beam: Beam) -> Beam:
        """Pass a beam through the deflector.

        Parameters
        ----------
        beam : Beam
            Beam to pass

        Returns
        -------
        Beam
            New beam, after passing through the deflector
        """
        out = beam.copy()
        # TODO tilt
        # TODO propagation length? Or just handle from previous lens instead?
        out._x0 = self.x
        out._y0 = self.y
        return out
