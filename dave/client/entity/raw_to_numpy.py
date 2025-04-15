from __future__ import annotations
from typing import Tuple

import numpy as np

from dave.common.sample_type import SampleType
from dave.common.raw_container import RawEntity


def to_dtype(sample_type: SampleType) -> np.dtype:
    """
    Convert a SampleType enum to the equivalent numpy dtype
    """
    return {
        SampleType.FLOAT: np.float32,
        SampleType.DOUBLE: np.float64,
        SampleType.CPX_F: np.complex64,
        SampleType.CPX_D: np.complex128,
    }[sample_type]


def to_sampletype(dtype: np.dtype) -> SampleType:
    """
    Convert a numpy dtype to the equivalent SampleType enum
    """
    return {
        np.float32: SampleType.FLOAT,
        np.float64: SampleType.DOUBLE,
        np.complex64: SampleType.CPX_F,
        np.complex128: SampleType.CPX_D,
    }[dtype.type]


def complexify_dtype(dtype: np.dtype) -> np.dtype:
    if dtype == np.float32:
        return np.complex64
    elif dtype == np.float64:
        return np.complex128
    elif dtype == np.float128:
        return np.complex256
    else:
        raise RuntimeError(f"Cannot complexify {dtype}")


def realify_dtype(dtype: np.dtype) -> np.dtype:
    if dtype == np.complex64:
        return np.float32
    elif dtype == np.complex128:
        return np.float64
    elif dtype == np.complex256:
        return np.float128
    else:
        raise RuntimeError(f"Cannot realify {dtype}")


def realify_array(data: np.ndarray) -> np.ndarray:
    """
    Cast a complex fp array into a fp array by splitting complex
    values into two fp value in the last dimension.

    If the array is already using a fp type this does nothing
    """
    if data.dtype.kind == "f":
        return data
    else:
        return data.view(dtype=realify_dtype(data.dtype))


def complexify_array(data: np.ndarray) -> np.ndarray:
    """
    Cast a fp array into a complex array by pairing fp values
    on the last dimension.

    If the array is already using a complex type this does nothing
    """
    if data.dtype.kind == "c":
        return data
    else:
        return data.view(dtype=complexify_dtype(data.dtype))
