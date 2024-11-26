from __future__ import annotations

import numpy as np
from scipy.spatial.transform import Rotation

from instamatic.camera.simulate.crystal import Crystal
from instamatic.camera.simulate.grid import Grid
from instamatic.camera.simulate.sample import Sample


class Stage:
    def __init__(
        self,
        num_crystals: int = 10_000,
        min_crystal_size: float = 100,
        max_crystal_size: float = 1000,
        random_seed: int = 100,
    ) -> None:
        self.x = 0
        self.y = 0
        self.z = 0
        self.alpha_tilt = 0
        self.beta_tilt = 0
        self.in_plane_rotation = 0  # TODO change this with focus/magnification
        self.rotation_matrix = np.eye(3)
        self.origin = np.array([0, 0, 0])

        # TODO parameters
        self.grid = Grid()

        self.rng = np.random.Generator(np.random.PCG64(random_seed))

        # TODO parameters
        self.crystal = Crystal(*self.rng.uniform(5, 25, 3), *self.rng.uniform(80, 110, 3))

        self.samples = [
            Sample(
                x=self.rng.uniform(-self.grid.radius_nm, self.grid.radius_nm),
                y=self.rng.uniform(-self.grid.radius_nm, self.grid.radius_nm),
                r=self.rng.uniform(min_crystal_size, max_crystal_size),
                euler_angle_phi_1=self.rng.uniform(0, 2 * np.pi),
                euler_angle_psi=self.rng.uniform(0, np.pi),
                euler_angle_phi_2=self.rng.uniform(0, 2 * np.pi),
            )
            for _ in range(num_crystals)
        ]

    def set_position(
        self,
        x: float = None,
        y: float = None,
        z: float = None,
        alpha_tilt: float = None,
        beta_tilt: float = None,
    ):
        if x is not None:
            self.x = x
        if y is not None:
            self.y = y
        if z is not None:
            self.z = z
        if alpha_tilt is not None:
            self.alpha_tilt = alpha_tilt
        if beta_tilt is not None:
            self.beta_tilt = beta_tilt

        self.rotation_matrix = Rotation.from_euler(
            'ZXY',
            [self.in_plane_rotation, self.alpha_tilt, self.beta_tilt],
            degrees=True,
        ).as_matrix()

    def image_extent_to_sample_coordinates(
        self,
        shape: tuple[int, int],
        x_min: float,
        x_max: float,
        y_min: float,
        y_max: float,
    ) -> tuple[np.ndarray, np.ndarray]:
        # https://en.wikipedia.org/wiki/Line%E2%80%93plane_intersection
        n = self.rotation_matrix @ np.array([0, 0, 1])
        p0 = self.origin
        l = np.array([0, 0, 1])  # noqa: E741
        l0 = np.array(
            [
                p.flatten()
                for p in np.meshgrid(
                    np.linspace(x_min, x_max, shape[1]),
                    np.linspace(y_min, y_max, shape[0]),
                    [0],
                )
            ]
        )

        p = l0 + np.array([0, 0, 1])[:, np.newaxis] * np.dot(-l0.T + p0, n) / np.dot(l, n)

        x, y, z = self.rotation_matrix.T @ p
        x = x.reshape(shape)
        y = y.reshape(shape)
        return x, y

    def get_image(
        self,
        shape: tuple[int, int],
        x_min: float,
        x_max: float,
        y_min: float,
        y_max: float,
    ) -> np.ndarray:
        """Get image array for given ranges. (x, y) = (0, 0) is in the center
        of the grid.

        Parameters
        ----------
        shape : tuple[int, int]
            Output shape
        x_min : float
            [nm] Lower bound for x (left)
        x_max : float
            [nm] Upper bound for x (right)
        y_min : float
            [nm] Lower bound for y (bottom)
        y_max : float
            [nm] Upper bound for y (top)

        Returns
        -------
        np.ndarray
            Image
        """
        x, y = self.image_extent_to_sample_coordinates(
            shape=shape, x_min=x_min, x_max=x_max, y_min=y_min, y_max=y_max
        )

        grid_mask = self.grid.array_from_coords(x, y)

        sample_data = np.zeros(shape)
        for ind, sample in enumerate(self.samples):
            # TODO improve estimate here to account for stage rotation
            if (sample.x - self.x) ** 2 + (sample.y - self.y) ** 2 > 1.5 * (x_max - x_min) ** 2:
                continue
            # TODO get actual crystal here, not just index
            sample_data[sample.pixel_contains_crystal(x, y)] = ind

        # TODO
        sample_data[grid_mask] += 1000

        return sample_data

    def get_diffraction_pattern(
        self,
        shape: tuple[int, int],
        x_min: float,
        x_max: float,
        y_min: float,
        y_max: float,
    ) -> np.ndarray:
        """Get diffraction pattern array for given ranges. (x, y) = (0, 0) is
        in the center of the grid.

        Parameters
        ----------
        shape : tuple[int, int]
            Output shape
        x_min : float
            [nm] Lower bound for x (left)
        x_max : float
            [nm] Upper bound for x (right)
        y_min : float
            [nm] Lower bound for y (bottom)
        y_max : float
            [nm] Upper bound for y (top)

        Returns
        -------
        np.ndarray
            diffraction pattern
        """
        x, y = self.image_extent_to_sample_coordinates(
            shape=shape, x_min=x_min, x_max=x_max, y_min=y_min, y_max=y_max
        )
        d_min = 1.0  # Determines scale of diffraction pattern, length from center to edge

        grid_mask = self.grid.array_from_coords(x, y)

        reflections = np.zeros(shape, dtype=bool)
        for crystal in self.samples:
            if not crystal.is_in_rectangle(x_min=x_min, x_max=x_max, y_min=y_min, y_max=y_max):
                continue

            pos = crystal.pixel_contains_crystal(x, y)
            if np.all(grid_mask[pos]):
                # Crystal is completely on the grid
                continue

            reflections |= self.crystal.diffraction_pattern_mask(
                shape,
                d_min=d_min,
                rotation_matrix=self.rotation_matrix @ crystal.rotation_matrix,
                wavelength=0.02,
                excitation_error=0.01,
            )

        # Simple scaling
        # TODO improve, proper form factors maybe
        kx, ky = np.meshgrid(
            np.linspace(-1 / d_min, 1 / d_min, shape[1]),
            np.linspace(-1 / d_min, 1 / d_min, shape[0]),
        )
        k_squared = kx**2 + ky**2
        scale = 1 / (3 * k_squared + 1)

        scale[~reflections] = 0

        return scale