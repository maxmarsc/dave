from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple, TypeAlias, Union
from enum import Enum

from .raw_entity import RawEntity
from .sample_type import SampleType


@dataclass
class RawIir(RawEntity):
    """
    A pickable representation of an IIR filter, sendable between the two dave process

    This should contains every piece of information needed by the GUI
    """

    @dataclass
    class SOSCoeffs:
        # One tuple per section
        values: List[Tuple[float, float, float, float, float, float]]

    @dataclass
    class ZPKCoeffs:
        zeros: List[complex]
        poles: List[complex]
        gain: float

    @dataclass
    class SVFTPTCoeffs:
        """
        See :
         - https://www.native-instruments.com/fileadmin/ni_media/downloads/pdf/VAFilterDesign_1.1.1.pdf
         - https://www.dafx14.fau.de/papers/dafx14_aaron_wishnick_time_varying_filters_for_.pdf

        For definitions of g and r
        """

        class FilterType(Enum):
            LP = "Low-Pass"
            BP = "Band-Pass"
            HP = "High-Pass"

        g: float
        r: float
        ftype: FilterType

    coeffs: Union[SOSCoeffs, ZPKCoeffs, SVFTPTCoeffs]

    def channels(self) -> int:
        # Only support mono filter so far - multichannel with same
        # coefficients on each channel
        return 1

    @staticmethod
    def supports_concat() -> bool:
        return False

    @dataclass
    class InScopeUpdate(RawEntity.InScopeUpdate):
        """
        Used to send a data update to the GUI
        """

        id: int
        coeffs: RawIirCoeffs

    def update(self, update: InScopeUpdate):
        assert self.id == update.id
        self.coeffs = update.coeffs

    def as_update(self) -> InScopeUpdate:
        return RawIir.InScopeUpdate(self.id, self.coeffs)
