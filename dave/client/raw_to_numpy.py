from __future__ import annotations
from typing import Tuple

import numpy as np

from dave.common.data_layout import DataLayout
from dave.common.sample_type import SampleType
from dave.common.raw_container import RawContainer


def to_dtype(sample_type: SampleType) -> np.dtype:
    return {
        SampleType.FLOAT: np.float32,
        SampleType.DOUBLE: np.float64,
        SampleType.CPX_F: np.complex64,
        SampleType.CPX_D: np.complex128,
    }[sample_type]


def to_sampletype(dtype: np.dtype) -> SampleType:
    return {
        np.float32: SampleType.FLOAT,
        np.float64: SampleType.DOUBLE,
        np.complex64: SampleType.CPX_F,
        np.complex128: SampleType.CPX_D,
    }[dtype.type]


def __complexify_layout(dtype: np.dtype) -> np.dtype:
    if dtype == np.float32:
        return np.complex64
    elif dtype == np.float64:
        return np.complex128
    elif dtype == np.float128:
        return np.complex256
    else:
        raise RuntimeError(f"{dtype} is not a supported type")


def __realify_layout(dtype: np.dtype) -> np.dtype:
    if dtype == np.complex64:
        return np.float32
    elif dtype == np.complex128:
        return np.float64
    elif dtype == np.complex256:
        return np.float128
    else:
        raise RuntimeError(f"{dtype} is not a supported type")


def __convert_to_real(data: np.ndarray) -> np.ndarray:
    if data.dtype.kind == "f":
        return data
    else:
        return data.view(dtype=__realify_layout(data.dtype))


def __convert_to_cpx(data: np.ndarray) -> np.ndarray:
    if data.dtype.kind == "c":
        return data
    else:
        return data.view(dtype=__complexify_layout(data.dtype))


def convert_data_to_layout(data: np.ndarray, layout: DataLayout) -> np.ndarray:
    if layout in (DataLayout.REAL_1D, DataLayout.REAL_2D):
        return __convert_to_real(data)
    else:
        return __convert_to_cpx(data)


def raw_to_numpy(raw_container: RawContainer):
    array = np.frombuffer(raw_container.data, dtype=to_dtype(raw_container.sample_type))
    return array.reshape(raw_container.original_shape)
