from enum import Enum
import numpy as np


class DataLayout(Enum):
    REAL_1D = "Scalar 1D"
    REAL_2D = "Scalar 2D"
    CPX_1D = "Complex 1D"
    CPX_2D = "Complex 2D"

    @staticmethod
    def __complexify(dtype: np.dtype) -> np.dtype:
        if dtype == np.float32:
            return np.complex64
        elif dtype == np.float64:
            return np.complex128
        elif dtype == np.float128:
            return np.complex256
        else:
            raise RuntimeError(f"{dtype} is not a supported type")

    @staticmethod
    def __realify(dtype: np.dtype) -> np.dtype:
        if dtype == np.complex64:
            return np.float32
        elif dtype == np.complex128:
            return np.float64
        elif dtype == np.complex256:
            return np.float128
        else:
            raise RuntimeError(f"{dtype} is not a supported type")

    def convert_to_layout(self, data: np.ndarray) -> np.ndarray:
        if self in (DataLayout.REAL_1D, DataLayout.REAL_2D):
            return self.__convert_to_real(data)
        else:
            return self.__convert_to_cpx(data)

    def __convert_to_real(self, data: np.ndarray) -> np.ndarray:
        if data.dtype.kind == "f":
            return data
        else:
            print("Converting to real")
            return data.view(dtype=DataLayout.__realify(data.dtype))

    def __convert_to_cpx(self, data: np.ndarray) -> np.ndarray:
        if data.dtype.kind == "c":
            return data
        else:
            print("Converting to cpx")
            return data.view(dtype=DataLayout.__complexify(data.dtype))
