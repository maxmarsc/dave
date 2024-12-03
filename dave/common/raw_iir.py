from __future__ import annotations
from dataclasses import dataclass

from .raw_entity import RawEntity


@dataclass
class RawIir(RawEntity):
    """
    A pickable representation of an IIR filter, sendable between the two dave process

    This should contains every piece of information needed by the GUI
    """

    coeffs: bytearray
