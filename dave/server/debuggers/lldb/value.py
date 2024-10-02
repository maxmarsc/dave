from __future__ import annotations
from typing import Union
from ..value import AbstractValue
import lldb


class LldbValue(AbstractValue):
    __debugger = None  # type: Union[None, lldb.SBDebugger]

    def __init__(self, lldb_value: lldb.SBValue, varname: str):
        if lldb_value.type.IsReferenceType():
            lldb_value = lldb_value.Dereference()  # type: lldb.SBValue
        if not lldb_value.IsValid():
            raise RuntimeError("Invalid lldb SBValue")
        self.__value = lldb_value  # type: lldb.SBValue
        self.__varname = varname
        if LldbValue.__debugger is None:
            LldbValue.__debugger = lldb.debugger

    def typename(self) -> str:
        return self.__value.type.GetCanonicalType().name

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
        return self.__value.GetValueAsSigned()

    def in_scope(self) -> bool:
        # lldb.SBValue.is_in_scope is not affected by frame changes (like up,
        # down commands) so we need to recheck manually

        # Try to reparse the varname
        new_value = LldbValue.find_variable_robust(self.__varname)
        if new_value.IsValid() and new_value.addr == self.__value.addr:
            return True
        return False

    @staticmethod
    def readmemory(addr: int, bytesize: int) -> bytearray:
        assert LldbValue.__debugger is not None
        process = (
            LldbValue.__debugger.GetSelectedTarget().GetProcess()
        )  # type: lldb.SBProcess
        error = lldb.SBError()
        raw_mem = process.ReadMemory(addr, bytesize, error)
        if not error.Success():
            raise RuntimeError(f"Failed to read {bytesize} bytes from {addr}")

        return bytearray(raw_mem)

    @staticmethod
    def find_variable_robust(
        varname: str, frame: Union[lldb.SBFrame, None] = None
    ) -> lldb.SBValue:
        if frame is None:
            assert LldbValue.__debugger is not None
            frame = (
                LldbValue.__debugger.GetSelectedTarget()
                .GetProcess()
                .GetSelectedThread()
                .GetSelectedFrame()
            )  # type: lldb.SBFrame
        assert frame.IsValid()

        var = frame.FindVariable(varname)  # type: lldb.SBValue
        if not var.IsValid():
            # Try through 'this'
            var = frame.FindVariable("this").GetChildMemberWithName(varname)

        return var
