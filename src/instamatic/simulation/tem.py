from __future__ import annotations

from typing import Tuple

import numpy as np

from instamatic.camera.camera_base import CameraBase
from instamatic.exceptions import TEMValueError
from instamatic.microscope.base import MicroscopeBase

from .aperture import Aperture
from .beam import Beam
from .deflector import Deflector
from .gun import ColdFEG
from .lens import Lens
from .optical_component import OpticalComponent
from .stage import Stage

FUNCTION_MODES = ('mag1', 'mag2', 'lowmag', 'samag', 'diff')


class TEMSimulation(MicroscopeBase, CameraBase):
    streamable = True

    def __init__(self):
        CameraBase.__init__(self, 'simulate')

        self.mode = FUNCTION_MODES[0]  # "mag1"

        self.gun = ColdFEG(acceleration_voltage=200_000)
        self.gun_shift_deflector = Deflector()
        self.condenser_lens_1 = Lens(0.1, 0.01, 0.01, 0, 0, 0, 0)
        self.condenser_lens_2 = Lens(0.1, 0.01, 0.01, 0, 0, 0, 0)
        self.condenser_aperture = Aperture(0, 0, [0.1, 0.01])
        self.beam_shift_deflector = Deflector()
        self.pre_sample_components: list[OpticalComponent] = [
            self.gun_shift_deflector,
            self.condenser_lens_1,
            self.condenser_lens_2,
            self.condenser_aperture,
            # TODO STEM scan coils?
        ]
        self.stage = Stage()
        self.objective_lens = Lens(0.1, 0.01, 0.01, 0, 0, 0, 0)
        self.objective_aperture = Aperture(0, 0, [0.1, 0.01])
        self.image_shift_deflector = Deflector()
        self.selected_area_aperture = Aperture(0, 0, [0.1, 0.01])
        self.intermediate_lens = Lens(0.1, 0.01, 0.01, 0, 0, 0, 0)
        self.projector_lens = Lens(0.1, 0.01, 0.01, 0, 0, 0, 0)
        self.post_sample_components: list[OpticalComponent] = [
            self.objective_lens,
            self.objective_aperture,
            self.image_shift_deflector,
            self.selected_area_aperture,
            self.intermediate_lens,
            self.projector_lens,
        ]

    def get_beam_on_stage(self) -> Beam:
        beam = self.gun.get_beam()
        for comp in self.pre_sample_components:
            beam = comp.propagate_beam(beam)
        return beam

    def get_beam_on_detector(self) -> Beam:
        beam_on_stage = self.get_beam_on_stage()
        return self.get_beam_on_detector_from_stage(beam_on_stage)

    def get_beam_on_detector_from_stage(self, beam: Beam) -> Beam:
        for comp in self.post_sample_components:
            beam = comp.propagate_beam(beam)
        return beam

    def _get_diffraction_pattern(self, exposure, binsize) -> np.ndarray:
        beam_on_stage = self.get_beam_on_stage()

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
        beam_on_stage = self.get_beam_on_stage()
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
    def getBeamShift(self) -> Tuple[int, int]:
        return self.gun_shift_deflector.position

    def getBeamTilt(self) -> Tuple[int]:
        # TODO
        return (0, 0)

    def getBrightness(self) -> int:
        # TODO, this wants the illuminated area on the sample I think
        return self.gun.brightness

    def getCondensorLensStigmator(self) -> Tuple[int]:
        # TODO handle stigmators
        return self.condenser_lens_1.astigmatism

    def getCurrentDensity(self) -> float:
        return self.gun.current_density

    def getDiffFocus(self, confirm_mode: bool = False) -> int:
        if confirm_mode:
            if self.getFunctionMode() != 'diff':
                raise TEMValueError(
                    'TEM must be in diffraction mode when setting diffraction focus'
                )
        # TODO how is this done?
        self.projector_lens.focus

    def getDiffShift(self) -> Tuple[int]:
        # TODO is this correct?
        return self.image_shift_deflector.position

    def getFunctionMode(self) -> str:
        return self.mode

    def getGunShift(self) -> Tuple[int]:
        return self.gun_shift_deflector.position

    def getGunTilt(self) -> Tuple[int]:
        # TODO
        return (0, 0)

    def getHTValue(self) -> float:
        return self.gun.acceleration_voltage

    def getImageShift1(self) -> Tuple[int]:
        return self.image_shift_deflector.position

    def getImageShift2(self) -> Tuple[int]:
        # TODO
        return (0, 0)

    def getIntermediateLensStigmator(self) -> Tuple[int]:
        # TODO
        return self.intermediate_lens.astigmatism

    def getMagnification(self) -> int:
        # TODO is this correct? Should be total for all post-sample system I think?
        return self.objective_lens.magnificaion

    def getMagnificationAbsoluteIndex(self) -> int:
        # TODO
        raise NotImplementedError(stacklevel=2)

    def getMagnificationIndex(self) -> int:
        # TODO
        return 0

    def getMagnificationRanges(self) -> dict:
        # TODO
        raise NotImplementedError(stacklevel=2)

    def getObjectiveLensStigmator(self) -> Tuple[int]:
        # TODO
        return self.objective_lens.astigmatism

    def getScreenPosition(self) -> str:
        return 'up'

    def getSpotSize(self) -> int:
        # TODO what is this measuring?
        # Assume diameter of beam on sample, I guess
        # Assume a ~ b ~ r
        beam = self.get_beam_on_stage()
        return beam._a + beam._b

    def getStagePosition(self) -> Tuple[int]:
        return self.stage.get_position()

    def isBeamBlanked(self) -> bool:
        # TODO
        return False

    def isStageMoving(self) -> bool:
        # TODO
        return False

    def setBeamBlank(self, mode: bool) -> None:
        # TODO
        pass

    def setBeamShift(self, x: int, y: int) -> None:
        self.beam_shift_deflector.x = x
        self.beam_shift_deflector.y = y

    def setBeamTilt(self, x: int, y: int) -> None:
        # TODO
        pass

    def setBrightness(self, value: int) -> None:
        # TODO. Need to figure out what this really is, and how to set
        pass

    def setCondensorLensStigmator(self, x: int, y: int) -> None:
        # TODO need to make actual stigmator coils
        pass

    def setDiffFocus(self, value: int, confirm_mode: bool) -> None:
        if confirm_mode:
            if self.getFunctionMode() != 'diff':
                raise TEMValueError('TEM must be in diffraction mode to set diffraction focus')
        # TODO proper
        self.objective_lens.focus = value

    def setDiffShift(self, x: int, y: int) -> None:
        # TODO is this correct?
        self.image_shift_deflector.x = x
        self.image_shift_deflector.y = y

    def setFunctionMode(self, value: int) -> None:
        if value not in FUNCTION_MODES:
            raise TEMValueError(f'Mode {value} not available')
        self.mode = value

    def setGunShift(self, x: int, y: int) -> None:
        self.gun_shift_deflector.x = x
        self.gun_shift_deflector.y = y

    def setGunTilt(self, x: int, y: int) -> None:
        # TODO
        pass

    def setImageShift1(self, x: int, y: int) -> None:
        self.image_shift_deflector.x = x
        self.image_shift_deflector.y = y

    def setImageShift2(self, x: int, y: int) -> None:
        # TODO
        pass

    def setIntermediateLensStigmator(self, x: int, y: int) -> None:
        # TODO
        pass

    def setMagnification(self, value: int) -> None:
        # TODO
        pass

    def setMagnificationIndex(self, index: int) -> None:
        # TODO
        pass

    def setObjectiveLensStigmator(self, x: int, y: int) -> None:
        # TODO
        pass

    def setScreenPosition(self, value: str) -> None:
        pass

    def setSpotSize(self, value: int) -> None:
        # TODO
        pass

    def setStagePosition(self, x: int, y: int, z: int, a: int, b: int, wait: bool) -> None:
        self.stage.set_position(x=x, y=y, z=z, alpha_tilt=a, beta_tilt=b)

    def stopStage(self) -> None:
        pass
