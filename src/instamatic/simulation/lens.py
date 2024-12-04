from __future__ import annotations

from dataclasses import dataclass

from .beam import Beam
from .optical_component import OpticalComponent


@dataclass(frozen=True)
class Lens(OpticalComponent):
    focal_length: float
    """[mm]"""

    collection_angle: float
    """[rad]"""

    # TODO the angles are related to the focal length?
    convergence_angle: float
    """[rad]"""

    # TODO: use the abberation and beta values to calculate radii,
    # and convolve image with a gaussian with that radius.
    # pp. 107 in Williams and Carter

    spherical_abberation: float
    """[mm]"""

    chromatic_abberation: float
    """[mm]"""

    astigmatism_x: float
    astigmatism_y: float

    # TODO add higher-order abberations

    @property
    def astigmatism(self) -> tuple[float, float]:
        return (self.astigmatism_x, self.astigmatism_y)

    @property
    def magnificaion(self) -> float:
        # TODO this is much easier to get from real microscopes.
        # Therefore, the angles should depend on focal length + magnification, instead
        return self.collection_angle / self.convergence_angle

    def propagate_beam(self, beam: Beam) -> Beam:
        """Pass a beam through the lens.

        Parameters
        ----------
        beam : Beam
            Beam to pass

        Returns
        -------
        Beam
            New beam, after passing through the lens
        """
        # TODO
        return super().propagate_beam(beam)
