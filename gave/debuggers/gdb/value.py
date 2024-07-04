from ..value import AbstractValue

import gdb  # type: ignore


class GdbValue(AbstractValue):
    def __init__(self, gdb_value: gdb.Value) -> None:
        super().__init__()
        self.__value = gdb_value

    def get(self) -> gdb.Value:
        return self.__value
