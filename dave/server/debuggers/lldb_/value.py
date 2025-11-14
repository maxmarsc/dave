from __future__ import annotations
from typing import List, Union

from dave.common.logger import Logger
from ..value import AbstractValue, DebuggerMemoryError
import lldb
import os
import threading


def xcode_detected() -> bool:
    return (
        os.environ.get("DYLD_FRAMEWORK_PATH", None)
        == "/Applications/Xcode.app/Contents/SharedFrameworks"
    )


class LldbValue(AbstractValue):
    __debugger = None  # type: Union[None, lldb.SBDebugger]
    __debugger_tid = -1

    def __init__(self, lldb_value: lldb.SBValue, varname: str):
        if lldb_value.type.IsReferenceType():
            lldb_value = lldb_value.Dereference()  # type: lldb.SBValue
        if not lldb_value.IsValid():
            raise RuntimeError("Invalid lldb SBValue")
        self.__value = lldb_value  # type: lldb.SBValue
        self.__varname = varname
        if LldbValue.__debugger is None:
            LldbValue.__init_debugger_objects()

    @staticmethod
    def __init_debugger_objects():
        LldbValue.__debugger = lldb.debugger
        LldbValue.__debugger_tid = threading.get_native_id()

    @staticmethod
    def debugger() -> lldb.SBDebugger:
        if xcode_detected() and LldbValue.__debugger_tid == threading.get_native_id():
            return lldb.debugger
        assert LldbValue.__debugger is not None
        return LldbValue.__debugger

    def typename(self) -> str:
        return self.__value.type.GetCanonicalType().name

    def varname(self) -> str:
        return self.__varname

    def byte_size(self):
        return int(self.__value.GetByteSize())

    def attr(self, name: str) -> LldbValue:
        try:
            return LldbValue(
                self.__value.GetNonSyntheticValue().GetChildMemberWithName(name),
                f"{self.__varname}.{name}",
            )
        except RuntimeError as e:
            raise RuntimeError(
                f"Failed to access member {name} on {self.typename()}"
                f"\n\terror: {e.args}"
            )

    # def call_method(self, name: str, *args) -> LldbValue:
    #     args_str = ",".join([str(arg) for arg in args])
    #     ret = self.__value.EvaluateExpression(
    #         f"{name}({args_str})"
    #     )  # type: lldb.SBValue
    #     if ret.IsValid():
    #         return LldbValue(ret)
    #     raise RuntimeError(
    #         f"Failed to call method {name} with args {args} on {self.typename()}"
    #     )

    def address(self) -> int:
        return self.__value.address_of.GetValueAsSigned()

    def __getitem__(self, key: int) -> LldbValue:
        assert (
            self.__value.type.IsPointerType() or self.__value.type.IsArrayType()
        ) and isinstance(key, int)

        if self.__value.type.IsPointerType():
            pointee_type = self.__value.type.GetPointeeType()  # type: lldb.SBType
            address = int(self) + key * pointee_type.GetByteSize()
            return LldbValue(
                self.__value.CreateValueFromAddress(
                    f"{self.__value.name}[{key}]", address, pointee_type
                ),
                f"{self.__varname}[{key}]",
            )
        else:
            return LldbValue(
                self.__value.GetChildAtIndex(key), f"{self.__varname}[{key}]"
            )

    def __int__(self) -> int:
        try:
            return self.__value.GetValueAsSigned()
        except TypeError as e:
            raise DebuggerMemoryError(e.args)

    def __float__(self) -> float:
        assert self.typename() in ("float", "double")
        try:
            return float(self.__value.GetValue())
        except TypeError as e:
            raise DebuggerMemoryError(e.args)

    def in_scope(self) -> bool:
        # lldb.SBValue.is_in_scope is not affected by frame changes (like up,
        # down commands) so we need to recheck manually

        # Try to reparse the varname
        new_value = LldbValue.find_variable(self.__varname)
        if new_value.__value.IsValid() and new_value.__value.addr == self.__value.addr:
            return True
        return False

    @staticmethod
    def readmemory(addr: int, bytesize: int) -> bytearray:
        if bytesize < 0 or bytesize > 4 * (1024**3):
            raise DebuggerMemoryError(
                f"Failed to read {bytesize} bytes from 0x{addr:X}"
            )
        # assert LldbValue.__debugger is not None
        process = (
            LldbValue.debugger().GetSelectedTarget().GetProcess()
        )  # type: lldb.SBProcess
        error = lldb.SBError()
        if addr <= 0:
            raise DebuggerMemoryError(
                f"Failed to read {bytesize} bytes from 0x{addr:X}"
            )
        try:
            raw_mem = process.ReadMemory(addr, bytesize, error)
        except ValueError:
            if error.Success():
                error.SetErrorToGenericError()
        if not error.Success():
            raise DebuggerMemoryError(
                f"Failed to read {bytesize} bytes from 0x{addr:X}"
            )

        return bytearray(raw_mem)

    @staticmethod
    def find_variable(
        varname: str, where: Union[lldb.SBFrame, None] = None
    ) -> Union[LldbValue, None]:
        if where is None:
            where = (
                LldbValue.debugger()
                .GetSelectedTarget()
                .GetProcess()
                .GetSelectedThread()
                .GetSelectedFrame()
            )  # type: lldb.SBFrame
        assert where.IsValid()

        var = where.FindVariable(varname)  # type: lldb.SBValue
        if not var.IsValid():
            # Try through 'this'
            var = where.FindVariable("this").GetChildMemberWithName(varname)

        if var.IsValid():
            return LldbValue(var, varname)
        else:
            return None

    @staticmethod
    def find_all_variables(where: Union[lldb.SBFrame, None] = None) -> List[LldbValue]:
        if LldbValue.__debugger is None:
            LldbValue.__init_debugger_objects()

        if where is None:
            where = (
                LldbValue.debugger()
                .GetSelectedTarget()
                .GetProcess()
                .GetSelectedThread()
                .GetSelectedFrame()
            )  # type: lldb.SBFrame

        found = []

        all_variables: lldb.SBValueList = where.GetVariables(True, True, False, True)
        for variable in all_variables:
            found.append(LldbValue(variable, variable.name))

        return found
