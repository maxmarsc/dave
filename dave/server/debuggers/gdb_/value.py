from __future__ import annotations
from ..value import AbstractValue
import gdb  # type: ignore


class GdbValue(AbstractValue):
    def __init__(self, gdb_value: gdb.Value, varname: str) -> None:
        self.__value = gdb_value
        self.__varname = varname

    def typename(self) -> str:
        return str(gdb.types.get_basic_type(self.__value.type).strip_typedefs())

    def byte_size(self) -> int:
        return self.__value.type.sizeof

    def attr(self, name: str) -> GdbValue:
        try:
            return GdbValue(self.__value[name], f"{self.__varname}.{name}")
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
        return GdbValue(self.__value[key], f"{self.__varname}[{key}]")

    def in_scope(self) -> bool:
        # Try to reparse the varname
        try:
            value = gdb.parse_and_eval(self.__varname)
            in_scope = value.address == self.__value.address
        except gdb.error:
            in_scope = False

        return in_scope

    @staticmethod
    def readmemory(addr: int, bytesize: int) -> bytearray:
        inferior = gdb.selected_inferior()
        return bytearray(inferior.read_memory(addr, bytesize))
