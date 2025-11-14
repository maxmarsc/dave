from __future__ import annotations
from typing import List, Union
from ..value import AbstractValue, DebuggerMemoryError
import gdb  # type: ignore


class GdbValue(AbstractValue):
    def __init__(self, gdb_value: gdb.Value, varname: str) -> None:
        self.__value = gdb_value
        self.__varname = varname

    def typename(self) -> str:
        return str(gdb.types.get_basic_type(self.__value.type).strip_typedefs())

    def varname(self) -> str:
        return self.__varname

    def byte_size(self) -> int:
        return self.__value.type.sizeof

    def attr(self, name: str) -> GdbValue:
        try:
            return GdbValue(self.__value[name], f"{self.__varname}.{name}")
        except gdb.MemoryError as e:
            raise DebuggerMemoryError(e.args)
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
        try:
            return int(self.__value)
        except (TypeError, gdb.MemoryError) as e:
            raise DebuggerMemoryError(e.args)

    def __float__(self) -> float:
        assert self.__value.type.code == gdb.TYPE_CODE_FLT
        try:
            return float(self.__value)
        except (TypeError, gdb.MemoryError) as e:
            raise DebuggerMemoryError(e.args)

    def __getitem__(self, key: int) -> GdbValue:
        """
        Access value by index. Only available for pointer types
        """
        assert isinstance(key, int)
        try:
            return GdbValue(self.__value[key], f"{self.__varname}[{key}]")
        except gdb.MemoryError as e:
            raise DebuggerMemoryError(e.args)

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
        if bytesize < 0 or bytesize > 4 * (1024**3):
            raise DebuggerMemoryError(
                f"Failed to read {bytesize} bytes from 0x{addr:X}"
            )
        inferior = gdb.selected_inferior()
        try:
            return bytearray(inferior.read_memory(addr, bytesize))
        except gdb.MemoryError:
            raise DebuggerMemoryError(
                f"Failed to read {bytesize} bytes from 0x{addr:X}"
            )

    @staticmethod
    def find_variable(
        varname: str, where: Union[gdb.Frame, None] = None
    ) -> Union[GdbValue, None]:
        if where is None:
            try:
                return GdbValue(gdb.parse_and_eval(varname), varname)
            except gdb.GdbError:
                return None

        assert isinstance(where, gdb.Frame)
        try:
            return GdbValue(where.read_var(varname), varname)
        except gdb.GdbError:
            return None

    @staticmethod
    def find_all_variables(where: Union[gdb.Frame, None] = None) -> List[GdbValue]:
        if where is None:
            where = gdb.selected_frame()

        found = []
        block = where.block()

        # Traverse all blocks until we leave the function
        while block and not block.is_static:
            for symbol in block:
                if symbol.is_variable or symbol.is_argument:
                    try:
                        value = where.read_var(symbol.name)
                        found.append(GdbValue(value, symbol.name))
                    except gdb.GdbError:
                        continue

            # Go up a block
            block = block.superblock

        return found
