# ruff: noqa: E402
from __future__ import annotations

import warnings

from instamatic.utils.deprecated import VisibleDeprecationWarning, deprecated

warnings.warn(
    'The `TEMController` module is deprecated since version 2.0.6. Use the `controller`-module instead',
    VisibleDeprecationWarning,
    stacklevel=2,
)


from instamatic.controller import get_instance, initialize
from instamatic.microscope.base import MicroscopeBase


@deprecated(since='2.0.6', alternative='instamatic.microscope.get_microscope')
def Microscope(name: str = None, use_server: bool = False) -> MicroscopeBase:
    from instamatic.microscope import get_microscope

    return get_microscope(name=name, use_server=use_server)
