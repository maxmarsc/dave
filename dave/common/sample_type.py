from __future__ import annotations
from enum import Enum
from typing import Any, Callable, List, Tuple, Type, Union


class SampleType(Enum):
    FLOAT = "float"
    DOUBLE = "double"
    CPX_F = "complex float"
    CPX_D = "complex double"

    @staticmethod
    def regex() -> str:
        return r"(float|double|complex\s+float|complex\s+double|std::complex<float>|std::complex<double>)"

    @staticmethod
    def parse(name: str) -> SampleType:
        if name == "std::complex<float>":
            return SampleType("complex float")
        elif name == "std::complex<double>":
            return SampleType("complex double")
        else:
            return SampleType(name)

    def byte_size(self) -> int:
        return {
            SampleType.FLOAT: 4,
            SampleType.DOUBLE: 8,
            SampleType.CPX_F: 8,
            SampleType.CPX_D: 16,
        }[self]

    def is_complex(self) -> bool:
        if self in (SampleType.CPX_F, SampleType.CPX_D):
            return True
        return False