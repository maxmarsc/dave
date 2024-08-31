from __future__ import annotations
from ..value import AbstractValue
import numpy as np
import lldb


class LldbValue(AbstractValue):
    def __init__(self, lldb_value=lldb.SBValue):
        if lldb_value.type.IsReferenceType():
            lldb_value = lldb_value.Dereference()  # type: lldb.SBValue
        if not lldb_value.IsValid():
            raise RuntimeError("Invalid lldb SBValue")
        self.__value = lldb_value  # type: lldb.SBValue

    def typename(self) -> str:
        return self.__value.type.GetCanonicalType().name

    def byte_size(self):
        return int(self.__value.GetByteSize())

    def attr(self, name: str) -> LldbValue:
        try:
            return LldbValue(
                self.__value.GetNonSyntheticValue().GetChildMemberWithName(name)
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
                )
            )
        else:
            return LldbValue(self.__value.GetChildAtIndex(key))

    def __int__(self) -> int:
        return self.__value.GetValueAsSigned()

    def in_scope(self) -> bool:
        return self.__value.is_in_scope

    @staticmethod
    def readmemory(addr: int, bytesize: int, dtype: np.dtype) -> np.ndarray:
        process = lldb.debugger.GetSelectedTarget().GetProcess()  # type: lldb.SBProcess
        error = lldb.SBError()
        raw_mem = process.ReadMemory(addr, bytesize, error)
        if not error.Success():
            raise RuntimeError(f"Failed to read {bytesize} bytes from {addr}")

        return np.frombuffer(raw_mem, dtype=dtype)
