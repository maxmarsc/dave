from enum import Enum


class DataLayout(Enum):
    REAL_1D = "Scalar 1D"
    REAL_2D = "Scalar 2D"
    CPX_1D = "Complex 1D"
    CPX_2D = "Complex 2D"

    @property
    def is_real(self) -> bool:
        return self in (DataLayout.REAL_1D, DataLayout.REAL_2D)

