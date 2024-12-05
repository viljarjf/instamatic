from __future__ import annotations

from abc import ABC, abstractmethod

from instamatic.simulation.beam import Beam


class OpticalComponent(ABC):
    @abstractmethod
    def propagate_beam(self, beam: Beam) -> Beam:
        return beam.copy()
