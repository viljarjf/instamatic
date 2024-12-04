from __future__ import annotations

import numpy as np


class Beam:
    # TODO
    # Handle convergence angle (focal length),
    # crossover
    # sphere of least confusion
    # Astigmatism
    # Energy + spread (wavelength)

    def __init__(
        self,
        # TODO the other params, this is just for the ellipse
        a: float = 1,
        b: float = 1,
        t: float = 0,
        x0: float = 0,
        y0: float = 0,
    ):
        # Using https://en.wikipedia.org/wiki/Ellipse#General_ellipse
        # no excentricity
        self._a = a
        self._b = b
        # Aligned with x-axis
        self._t = t
        # Centered
        self._x0 = x0
        self._y0 = y0

        st = np.sin(self._t)
        ct = np.cos(self._t)
        a2 = self._a**2
        b2 = self._b**2
        self.A = a2 + st**2 + b2 * ct**2
        self.B = 2 * (b2 - a2) * st * ct
        self.C = a2 * ct**2 + b2 * ct**2
        self.D = -2 * self.A * self._x0 - self.B * self._y0
        self.E = -self.B * self._x0 - 2 * self.C * self._y0
        self.F = (
            self.A * self._x0**2 + self.B * self._x0 * self._y0 + self.C * self._y0**2 - a2 * b2
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
        x0 -= self._x0
        y0 -= self._y0
        x1 -= self._x0
        y1 -= self._y0
        # x0, y0: vector from center to major axis
        # x1, y1: vector from center to minor axis
        return (
            (self._x0 + x0 + x1, self._y0 + y0 + y1),  # +major, +minor
            (self._x0 - x0 + x1, self._y0 - y0 + y1),  # -major, +minor
            (self._x0 - x0 - x1, self._y0 - y0 - y1),  # -major, -minor
            (self._x0 + x0 - x1, self._y0 + y0 - y1),  # +major, -minor
        )

    def _get_coordinates_from_polar(self, theta) -> tuple[float, float]:
        r = (
            self._a
            * self._b
            / ((self._a * np.sin(theta) ** 2) ** 2 + (self._b * np.cos(theta) ** 2) ** 2) ** 0.5
        )
        st = np.sin(theta + self._t)
        ct = np.cos(theta + self._t)
        x = r * ct
        y = r * st
        return x + self._x0, y + self._y0

    def copy(self) -> 'Beam':
        return Beam(
            a=self._a,
            b=self._b,
            t=self._t,
            x0=self._x0,
            y0=self._y0,
        )
