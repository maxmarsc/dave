from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple

from .raw_entity import RawEntity
from .sample_type import SampleType


@dataclass
class RawIir(RawEntity):
    """
    A pickable representation of an IIR filter, sendable between the two dave process

    This should contains every piece of information needed by the GUI
    """

    coeffs: bytearray
    original_shape: Tuple[int, int]
    sample_type: SampleType

    def channels(self) -> int:
        return self.original_shape[0]

    class Layout(RawEntity.Layout):
        JUCE = "JUCE"
        SCIPY = "Scipy"
        ZPK = "ZPK"
        SOS = "SOS"
        BIQUAD = "BIQUAD"
        SVF = "SVF"

    @dataclass
    class InScopeUpdate(RawEntity.InScopeUpdate):
        """
        Used to send a data update to the GUI
        """

        id: int
        coeffs: bytearray
        shape: Tuple[int, int]

    def update(self, update: InScopeUpdate):
        assert self.id == update.id
        self.coeffs = update.coeffs
        self.original_shape = update.shape
