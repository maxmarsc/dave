from typing import Union
from dave.common.logger import Logger
import gdb  # type: ignore
from ...container import Container
from ...entity_factory import EntityFactory, EntityBuildError
from .value import GdbValue


class ContainerPrettyPrinter:
    __PREFIX = None

    def __init__(self, val: gdb.Value, container: Container):
        self.__val = val
        self.__container = container

        if ContainerPrettyPrinter.__PREFIX is None:
            ContainerPrettyPrinter.__PREFIX = (
                ""
                if check_for_chartable_printer(gdb.Value("test"))
                else SparklinePrinter.PREFIX
            )

    def children(self):
        if not self.__container.sample_type.is_complex():
            # Add synthetic children
            sparklines = self.__container.compute_sparklines()
            for channel, sparkline in enumerate(sparklines):
                yield f"dSparkline[{channel}]", gdb.Value(
                    ContainerPrettyPrinter.__PREFIX + sparkline
                )

        # Iterate over real children
        for field in self.__val.type.fields():
            yield field.name, self.__val[field.name]

    def to_string(self) -> str:
        return self.__container.compute_summary()

    @staticmethod
    def prefix() -> Union[None, str]:
        return ContainerPrettyPrinter.__PREFIX


class SparklinePrinter:
    PREFIX = "===DAVE==="

    def __init__(self, val: gdb.Value):
        if val.type.code != gdb.TYPE_CODE_ARRAY or val.type.target().name != "char":
            raise TypeError

        try:
            string = val.string()
        except gdb.error:
            raise TypeError

        if not string.startswith(SparklinePrinter.PREFIX):
            raise TypeError

        self.__str = string[len(SparklinePrinter.PREFIX) :]

    def to_string(self):
        return self.__str

    def display_hint(self):
        return "string"


def check_for_chartable_printer(valobj: gdb.Value):
    if valobj.type.code != gdb.TYPE_CODE_ARRAY and valobj.type.target().name != "char":
        Logger().warning("Calling chartable printer check on non char table")

    for printer in gdb.pretty_printers:
        if printer(valobj):
            return True
    return False


def dave_printer(valobj: gdb.Value):
    if ContainerPrettyPrinter.prefix() is not None:
        # If the current setup has no pretty-printer for char[] we create one
        try:
            return SparklinePrinter(valobj)
        except TypeError:
            pass

    gdb_value = GdbValue(valobj, "")
    try:
        container = EntityFactory().build(gdb_value, gdb_value.typename(), "")
        if container.formatter_compatible():
            return ContainerPrettyPrinter(valobj, container)
        return None
    except (EntityBuildError, TypeError):
        return None
