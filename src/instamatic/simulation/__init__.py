from __future__ import annotations

from typing import Tuple

from instamatic.camera.videostream import VideoStream
from instamatic.simulation.tem import TEMSimulation


def get_simulation_instances() -> Tuple[TEMSimulation, VideoStream]:
    """Initialize simulated camera and microscope.

    Returns
    -------
    Tuple[CameraSimulation, MicroscopeSimulation]
    """
    tem = TEMSimulation()
    cam = VideoStream(tem)
    return cam, tem
