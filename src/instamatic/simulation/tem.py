from __future__ import annotations

import numpy as np

from instamatic.camera.camera_base import CameraBase
from instamatic.microscope.base import MicroscopeBase

from .aperture import Aperture
from .deflector import Deflector
from .gun import ColdFEG
from .illumination import Illumination
from .lens import Lens
from .stage import Stage


class TEMSimulation(MicroscopeBase, CameraBase):
    streamable = True

    def __init__(self):
        CameraBase.__init__(self, 'simulate')
        self.gun = ColdFEG(acceleration_voltage=200_000)
        self.condenser_lens_1 = Lens(0.1, 0.01, 0.01, 0, 0, 0, 0)
        self.condenser_lens_2 = Lens(0.1, 0.01, 0.01, 0, 0, 0, 0)
        self.condenser_aperture = Aperture(0, 0, [0.1, 0.01])
        self.scanning_coil = Deflector()

        self.illumination = Illumination(
            self.gun,
            [
                self.condenser_lens_1,
                self.condenser_lens_2,
                self.condenser_aperture,
                self.scanning_coil,
            ],
        )
        self.stage = Stage()

    def _get_diffraction_pattern(self, exposure, binsize) -> np.ndarray:
        beam_on_stage = self.illumination.get_beam_on_stage()

        for sample in self.stage.samples:
            if not beam_on_stage.is_point_in_beam(sample.x, sample.y):
                continue
            # TODO use this^ instead

        ## OLD IMPLEMENTATION ##
        box = beam_on_stage.get_rectangular_external_box()
        x_min = min(b[0] for b in box)
        x_max = max(b[0] for b in box)
        y_min = min(b[1] for b in box)
        y_max = max(b[1] for b in box)
        shape_x, shape_y = self.get_camera_dimensions()
        shape = (shape_x // binsize, shape_y // binsize)
        return self.stage.get_diffraction_pattern(shape, x_min, x_max, y_min, y_max)

    def _get_image(self, exposure, binsize) -> np.ndarray:
        beam_on_stage = self.illumination.get_beam_on_stage()
        # TODO CTF
        # TODO get mapping of coordinates of camera pixels to sample, through projection system

        ## OLD IMPLEMENTATION ##
        box = beam_on_stage.get_rectangular_external_box()
        x_min = min(b[0] for b in box)
        x_max = max(b[0] for b in box)
        y_min = min(b[1] for b in box)
        y_max = max(b[1] for b in box)
        shape_x, shape_y = self.get_camera_dimensions()
        shape = (shape_x // binsize, shape_y // binsize)
        return self.stage.get_image(shape, x_min, x_max, y_min, y_max)

    def get_image(self, exposure=None, binsize=None, **kwargs):
        if exposure is None:
            exposure = self.default_exposure
        if binsize is None:
            binsize = self.default_binsize
        if self.getFunctionMode() == 'diff':
            return self._get_diffraction_pattern(exposure, binsize)
        else:
            return self._get_image(exposure, binsize)

    def establish_connection(self):
        pass

    def release_connection(self):
        pass

    # TODO implement all the abstract functions for the microscope,
    # using simulated lenses ect
