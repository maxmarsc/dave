from dataclasses import dataclass
from typing import Tuple, Union
from dave.common.raw_iir import RawIir
import numpy as np
from scipy import signal


@dataclass
class InternalNpy:
    sos: np.ndarray  # shape (sections, 6), a0 normalized

    @property
    def order(self) -> int:
        order = 0
        for section in self.sos:
            if abs(section[2]) > 1e-12 or abs(section[5]) > 1e-12:
                order += 2
            else:
                order += 1
        return order

    @property
    def zeros_poles(self) -> Tuple[int, int]:
        z, p, _ = signal.sos2zpk(self.sos)
        z = np.sum(np.abs(z) > 1e-12)
        p = np.sum(np.abs(p) > 1e-12)
        return (z, p)


def raw_to_npy(
    data: Union[RawIir.SOSCoeffs, RawIir.ZPKCoeffs, RawIir.SVFTPTCoeffs],
) -> InternalNpy:
    match type(data):
        case RawIir.SOSCoeffs:
            return __raw_sos_to_internal(data)
        case RawIir.ZPKCoeffs:
            return __raw_zpk_to_internal(data)
        case RawIir.SVFTPTCoeffs:
            return __raw_svf_tpt_to_internal(data)
        case _:
            if data is None:
                return np.zeros((0, 6))
            raise NotImplementedError("Unrecognised IIR coeffs")


def __raw_sos_to_internal(coeffs: RawIir.SOSCoeffs) -> InternalNpy:
    np_sections = np.zeros((len(coeffs.values), 6))
    for i, section in enumerate(coeffs.values):
        a0 = section[3]
        np_sections[i] = np.array(section) / a0
    return InternalNpy(np_sections)


def __raw_zpk_to_internal(coeffs: RawIir.ZPKCoeffs) -> InternalNpy:
    return InternalNpy(
        signal.zpk2sos(np.ndarray(coeffs.zeros), np.ndarray(coeffs.poles), coeffs.gain)
    )


def __raw_svf_tpt_to_internal(coeffs: RawIir.SVFTPTCoeffs) -> InternalNpy:
    """
    See https://www.dafx14.fau.de/papers/dafx14_aaron_wishnick_time_varying_filters_for_.pdf
    Equations 13a, 13b, 13c
    """
    # Calculate intermediate values
    g_sq = coeffs.g**2
    R2 = coeffs.r * 2

    # Denominator coefficients
    a0 = 1.0 + g_sq + R2 * coeffs.g
    a1 = 2.0 * g_sq - 2
    a2 = 1.0 + g_sq - R2 * coeffs.g

    match coeffs.ftype:
        case RawIir.SVFTPTCoeffs.FilterType.LP:
            b0 = g_sq
            b1 = 2.0 * g_sq
            b2 = g_sq
        case RawIir.SVFTPTCoeffs.FilterType.BP:
            b0 = coeffs.g
            b1 = 0
            b2 = -coeffs.g
        case RawIir.SVFTPTCoeffs.FilterType.HP:
            b0 = 1
            b1 = -2.0
            b2 = 1

    sections = np.array(((b0 / a0, b1 / a0, b2 / a0, 1.0, a1 / a0, a2 / a0),))

    return InternalNpy(sections)
