from __future__ import annotations
from numpy import ndarray
from ..value import AbstractValue
import gdb  # type: ignore
import numpy as np


class GdbValue(AbstractValue):
    def __init__(self, gdb_value: gdb.Value) -> None:
        self.__value = gdb_value

    def typename(self) -> str:
        return str(gdb.types.get_basic_type(self.__value.type).strip_typedefs())

    def byte_size(self) -> int:
        return self.__value.type.sizeof

    def attr(self, name: str) -> GdbValue:
        try:
            return GdbValue(self.__value[name])
        except gdb.error as e:
            raise RuntimeError(
                f"Failed to access member {name} on {self.__value.type.name}"
                f"\n\terror: {e.args}"
            )

    # def call_method(self, name: str, *args) -> GdbValue:
    #     method_full_name = f"'{self.typename()}::{name}'"
    #     try:
    #         fn = gdb.parse_and_eval(method_full_name)
    #         return GdbValue(fn(*[self.__value.address, *args]))
    #     except gdb.error as e:
    #         raise RuntimeError(
    #             f"Failed to call method {name} with args {args} on {self.__value.type.name}"
    #             f"\n\terror: {e.args}"
    #         )

    def address(self) -> int:
        return int(self.__value.address)

    def __int__(self) -> int:
        return int(self.__value)

    def __getitem__(self, key: int) -> GdbValue:
        """
        Access value by index. Only available for pointer types
        """
        assert isinstance(key, int)
        return GdbValue(self.__value[key])

    @staticmethod
    def readmemory(addr: int, bytesize: int, dtype: np.dtype) -> ndarray:
        inferior = gdb.selected_inferior()
        return np.frombuffer(inferior.read_memory(addr, bytesize), dtype=dtype)
