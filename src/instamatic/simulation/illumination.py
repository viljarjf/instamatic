from __future__ import annotations

from .beam import Beam
from .gun import Gun
from .optical_component import OpticalComponent


class Illumination:
    def __init__(self, gun: Gun, optical_components: list[OpticalComponent]):
        self.gun = gun
        self.optical_components = optical_components

    def get_beam_on_stage(self) -> Beam:
        """Calculate the area of the sample which is illuminated. This is
        returned as a point (x, y), and a radius r, all in meters. The
        z-coordinate, if useful, is 0.

        Returns
        -------
        tuple[float, float, float]
            x, y, r
        """
        beam = self.gun.get_beam()
        for component in self.optical_components:
            beam = component.propagate_beam(beam)
        return beam
