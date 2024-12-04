from __future__ import annotations

from .beam import Beam
from .optical_component import OpticalComponent


class Deflector(OpticalComponent):
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
        # TODO
        return beam.copy()
