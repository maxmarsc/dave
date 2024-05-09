import re
import gdb  # type: ignore
from typing import List, Dict, Union

from .singleton import SingletonMeta
from .buffer import Buffer


class BufferFactory(metaclass=SingletonMeta):
    def __init__(self) -> None:
        self.__buffer_list = {}

    def register(self, cls):
        if not issubclass(cls, Buffer):
            raise gdb.GdbError(f"Error : {cls} is not a subclass of gave.Buffer")
        if cls not in self.__buffer_list:
            self.__buffer_list[cls] = cls.regex_name()
        else:
            raise gdb.GdbError(
                f"Error : {cls} was already registered in the buffer dispatcher"
            )

    def build(self, gdb_value: gdb.Value, name: str) -> Buffer:
        typename = str(gdb.types.get_basic_type(gdb_value.type))
        for cls, regex in self.__buffer_list.items():
            if regex.match(typename) is not None:
                return cls(gdb_value, name)

        raise gdb.GdbError(
            f"Error : {typename} did not match any registered Buffer class"
        )
