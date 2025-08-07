from typing import Dict, List, Set
from dave.common.singleton import SingletonMeta
from ...container import Container
from ...entity_factory import EntityFactory
from .value import LldbValue
import lldb
import re


def summary_provider(valobj: lldb.SBValue, _) -> str:
    lldb_value = LldbValue(valobj, "")
    container = EntityFactory().build(lldb_value, lldb_value.typename(), "")
    try:
        return container.compute_summary()
    except RuntimeError:
        # Fails randomly on Xcode
        return "Failed to fetch dave summary (random xcode bug sory)"


class SyntheticChildrenProvider:
    def __init__(self, valobj: lldb.SBValue, _):
        self.__sparklines: List[str] = list()
        self.__num_channels = 0
        self.__valobj = valobj
        lldb_value = LldbValue(valobj, valobj.path)
        # For some weird reason, Xcode will ask for the synthetic children twice
        # Once with the object itself
        # Then with a pointer to the object
        try:
            self.__container = EntityFactory().build(
                lldb_value, lldb_value.typename(), valobj.name
            )
        except TypeError:
            deref = valobj.Dereference()
            lldb_value = LldbValue(deref, deref.path)
            self.__container = EntityFactory().build(
                lldb_value, lldb_value.typename(), valobj.name
            )

    def num_children(self) -> int:
        if self.__container.sample_type.is_complex():
            return self.__valobj.num_children
        return self.__num_channels + self.__valobj.num_children

    def get_child_index(self, name: str) -> int:
        if self.__container.sample_type.is_complex():
            return self.__valobj.GetIndexOfChildWithName(name)
        if str.startswith(name, "dSparkline"):
            return int(name.lstrip("[").rstrip("]"))
        else:
            return self.__valobj.GetIndexOfChildWithName(name) + self.__num_channels

    def get_child_at_index(self, index: int) -> lldb.SBValue:
        if self.__container.sample_type.is_complex():
            return self.__valobj.GetChildAtIndex(index)
        if index < self.__num_channels:
            return self.__sparkline_value(index)
        else:
            return self.__valobj.GetChildAtIndex(index - self.__num_channels)

    def update(self):
        if not self.__container.sample_type.is_complex():
            try:
                self.__sparklines = self.__container.compute_sparklines()
                self.__num_channels = len(self.__sparklines)
            except RuntimeError:
                self.__sparklines = []
                self.__num_channels = 0

    def has_children(self) -> bool:
        return True

    def __sparkline_value(self, channel: int) -> lldb.SBValue:
        string = self.__sparklines[channel]
        # Shamelessly stolen from Sudara's
        # https://github.com/sudara/melatonin_audio_sparklines/blob/main/sparklines.py#L181

        # SBValue creation for a string took a while to figure out
        # Unfortunately I couldn't just use an lldb expression because of a bug with quotes in Clion:
        # https://youtrack.jetbrains.com/issue/CPP-25517
        #
        # Once resolved, the below code could be replaced with:
        # return self.valobj.CreateValueFromExpression("sparkline", '(char *) "hello world"') # clion quotes escaping doesn't work
        #
        # I also tried creating via Address before I realized Array types existed
        # https://stackoverflow.com/a/64473058
        #
        # Other examples of SBValue creation:
        # https://github.com/llvm-mirror/lldb/blob/master/examples/synthetic/bitfield/example.py
        # https://dev.to/vejmartin/prettifying-debug-variables-in-c-with-lldb-34lf
        #
        # Let's first "reach through" our root object to access the type system
        # https://lldb.llvm.org/python_reference/lldb.SBData-class.html
        child_type = self.__valobj.target.GetBasicType(lldb.eBasicTypeChar)
        byte_order = self.__valobj.GetData().GetByteOrder()
        data = lldb.SBData.CreateDataFromCString(
            byte_order, child_type.GetByteSize(), string
        )

        # Took me a while to figure out GetArrayType even existed!
        # https://invent.kde.org/tcanabrava/kdevelop/blob/5bd8475f3e0893fb8af299ea1f99042c2c2324bd/plugins/lldb/formatters/helpers.py#L279-281
        return self.__valobj.CreateValueFromData(
            f"dSparkline[{channel}]",
            data,
            child_type.GetArrayType(data.GetByteSize()),
        )
