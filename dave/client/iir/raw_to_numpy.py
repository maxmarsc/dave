from dataclasses import dataclass
from typing import Tuple, Union
from dave.common.raw_iir import RawIir
import numpy as np
from scipy import signal

# from dave.client.entity.raw_to_numpy


# @dataclass
# class ZPKNumpy:
#     zeros: np.ndarray
#     poles: np.ndarray
#     gain: float
@dataclass
class InternalNpy:
    sos: np.ndarray

    # @property
    # def order(self):
    @property
    def zeros_poles(self) -> Tuple[int, int]:
        z, p, _ = signal.sos2zpk(self.sos)
        z = np.sum(np.abs(z) > 1e-12)
        p = np.sum(np.abs(p) > 1e-12)
        return (z, p)


def raw_to_npy(data: Union[RawIir.SOSCoeffs, RawIir.ZPKCoeffs]) -> InternalNpy:
    match type(data):
        case RawIir.SOSCoeffs:
            return __raw_sos_to_internal(data)
        case RawIir.ZPKCoeffs:
            return __raw_zpk_to_internal(data)
        case _:
            raise NotImplementedError("Unrecognised IIR coeffs")


def __raw_sos_to_internal(coeffs: RawIir.SOSCoeffs) -> InternalNpy:
    np_sections = np.zeros((len(coeffs.values), 6))
    for i, section in enumerate(coeffs.values):
        np_sections[i] = np.array(section)
    return InternalNpy(np_sections)


def __raw_zpk_to_internal(coeffs: RawIir.ZPKCoeffs) -> InternalNpy:
    return InternalNpy(
        signal.zpk2sos(np.ndarray(coeffs.zeros), np.ndarray(coeffs.poles), coeffs.gain)
    )
