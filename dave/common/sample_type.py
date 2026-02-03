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
        return r"(float|double|complex\s+float|complex\s+double|std::complex<float>|std::__1::complex<float>|std::complex<double>|std::__1::complex<double>|f32|f64|num_complex::Complex<float>|num_complex::Complex<double>|num_complex::Complex<f32>|num_complex::Complex<f64>)"

    @staticmethod
    def parse(name: str) -> SampleType:
        match name:
            case (
                "std::complex<float>"
                | "std::__1::complex<float>"
                | "complex float"
                | "num_complex::Complex<float>"
                | "num_complex::Complex<f32>"
            ):
                return SampleType.CPX_F
            case (
                "std::complex<double>"
                | "std::__1::complex<double>"
                | "complex double"
                | "num_complex::Complex<double>"
                | "num_complex::Complex<f64>"
            ):
                return SampleType.CPX_D
            case "float" | "f32":
                return SampleType.FLOAT
            case "double" | "f64":
                return SampleType.DOUBLE
            case _:
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

    def struct_fmt(self) -> str:
        return {
            SampleType.FLOAT: "f",
            SampleType.DOUBLE: "d",
            SampleType.CPX_F: "ff",
            SampleType.CPX_D: "dd",
        }[self]
