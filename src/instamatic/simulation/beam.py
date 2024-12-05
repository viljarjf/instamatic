from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class Beam:
    # TODO
    # Handle convergence angle (focal length),
    # crossover
    # sphere of least confusion
    # Astigmatism
    # Energy + spread (wavelength)

    # TODO the other params, this is just for the ellipse
    a: float = 1
    b: float = 1
    t: float = 0
    x0: float = 0
    y0: float = 0

    def __post_init__(self):
        # Using https://en.wikipedia.org/wiki/Ellipse#General_ellipse
        # no excentricity

        st = np.sin(self.t)
        ct = np.cos(self.t)
        a2 = self.a**2
        b2 = self.b**2
        self.A = a2 + st**2 + b2 * ct**2
        self.B = 2 * (b2 - a2) * st * ct
        self.C = a2 * ct**2 + b2 * ct**2
        self.D = -2 * self.A * self.x0 - self.B * self.y0
        self.E = -self.B * self.x0 - 2 * self.C * self.y0
        self.F = (
            self.A * self.x0**2 + self.B * self.x0 * self.y0 + self.C * self.y0**2 - a2 * b2
        )

    def is_point_in_beam(self, x: float, y: float) -> bool:
        return (
            self.A * x**2 + self.B * x * y + self.C * y**2 + self.D * x + self.E * y
        ) < -self.F

    def get_rectangular_internal_box(
        self,
    ) -> tuple[
        tuple[float, float], tuple[float, float], tuple[float, float], tuple[float, float]
    ]:
        """Get four corners of a box inside the elliptical beam.

        Returns
        -------
        tuple[tuple[float, float], tuple[float, float], tuple[float, float], tuple[float, float]]
            Four corners, in counterclockwise order
        """
        t0 = 1 * np.pi / 4
        t1 = 3 * np.pi / 4
        t2 = 5 * np.pi / 4
        t3 = 7 * np.pi / 4
        return (
            self._get_coordinates_from_polar(t0),
            self._get_coordinates_from_polar(t1),
            self._get_coordinates_from_polar(t2),
            self._get_coordinates_from_polar(t3),
        )

    def get_rectangular_external_box(
        self,
    ) -> tuple[
        tuple[float, float], tuple[float, float], tuple[float, float], tuple[float, float]
    ]:
        """Get four corners of a box encompassing the elliptical beam.

        Returns
        -------
        tuple[tuple[float, float], tuple[float, float], tuple[float, float], tuple[float, float]]
            Four corners, in counterclockwise order
        """
        t0 = 0
        t1 = np.pi
        x0, y0 = self._get_coordinates_from_polar(t0)
        x1, y1 = self._get_coordinates_from_polar(t1)
        x0 -= self.x0
        y0 -= self.y0
        x1 -= self.x0
        y1 -= self.y0
        # x0, y0: vector from center to major axis
        # x1, y1: vector from center to minor axis
        return (
            (self.x0 + x0 + x1, self.y0 + y0 + y1),  # +major, +minor
            (self.x0 - x0 + x1, self.y0 - y0 + y1),  # -major, +minor
            (self.x0 - x0 - x1, self.y0 - y0 - y1),  # -major, -minor
            (self.x0 + x0 - x1, self.y0 + y0 - y1),  # +major, -minor
        )

    def _get_coordinates_from_polar(self, theta) -> tuple[float, float]:
        r = (
            self.a
            * self.b
            / ((self.a * np.sin(theta) ** 2) ** 2 + (self.b * np.cos(theta) ** 2) ** 2) ** 0.5
        )
        st = np.sin(theta + self.t)
        ct = np.cos(theta + self.t)
        x = r * ct
        y = r * st
        return x + self.x0, y + self.y0

    def copy(self) -> 'Beam':
        return Beam(
            a=self.a,
            b=self.b,
            t=self.t,
            x0=self.x0,
            y0=self.y0,
        )
