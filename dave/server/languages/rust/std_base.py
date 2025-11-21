from ...debuggers.value import AbstractValue
from ..c_cpp.template_parser import parse_template


class RustSlice:
    def __init__(self, dbg_value: AbstractValue):
        self.__value = dbg_value

    @property
    def size(self) -> int:
        assert isinstance(self.__value, AbstractValue)

        byte_size = self.data_ptr_value()[0].byte_size()

        try:
            return int(self.__value.attr("length"))
        except RuntimeError:
            pass

        raise RuntimeError(
            f"Failed to retrieve length of {self.__value.typename()}. "
            "Consider disabling optimization or use a supported stdlib version"
        )

    def data_ptr_value(self) -> AbstractValue:
        assert isinstance(self.__value, AbstractValue)

        try:
            return self.__value.attr("data_ptr")
        except RuntimeError:
            pass

        raise RuntimeError(
            f"Failed to retrieve data ptr of {self.__value.typename()}. "
            "Consider disabling optimization or use a supported stdlib version"
        )


class RustVector:
    def __init__(self, dbg_value: AbstractValue):
        self.__value = dbg_value

    def __cast_char_ptr(self, char_ptr_value: AbstractValue) -> AbstractValue:
        """
        Converts the given byte pointer to a pointer to the vector element type

        This function exists because internally Rust uses a byte pointer, which
        makes it impossible to retrieve the stored elements in the vector

        Parameters
        ----------
        char_ptr_value : AbstractValue
            The byte pointer to cast

        Returns
        -------
        AbstractValue
            A pointer to the element type of the vector

        Raises
        ------
        RuntimeError
            Should not happen
        """
        try:
            import lldb
            from ...debuggers.lldb_.value import LldbValue

            pointer_type: lldb.SBType = (
                self.__value._LldbValue__value.type.GetTemplateArgumentType(
                    0
                ).GetPointerType()
            )
            lldb_char_value: lldb.SBValue = char_ptr_value._LldbValue__value
            return LldbValue(
                lldb_char_value.Cast(pointer_type), char_ptr_value.varname()
            )
        except ImportError:
            pass

        try:
            import gdb  # type: ignore
            from ...debuggers.gdb_.value import GdbValue

            pointer_type = gdb.Type = (
                self.__value._GdbValue__value.type.template_argument(0).pointer()
            )
            gdb_char_value: gdb.Value = char_ptr_value._GdbValue__value
            return GdbValue(
                gdb_char_value.cast(pointer_type),
                char_ptr_value.varname(),
                char_ptr_value.language(),
            )

        except ImportError:
            pass

        raise RuntimeError("DAVE only supports GDB & LLDB")

    @property
    def size(self) -> int:
        assert isinstance(self.__value, AbstractValue)

        try:
            return int(self.__value.attr("len"))
        except RuntimeError:
            pass

        raise RuntimeError(
            f"Failed to retrieve length of {self.__value.typename()}. "
            "Consider disabling optimization or use a supported stdlib version"
        )

    def data_ptr_value(self) -> AbstractValue:
        assert isinstance(self.__value, AbstractValue)

        try:
            return self.__cast_char_ptr(
                self.__value.attr("buf")
                .attr("inner")
                .attr("ptr")
                .attr("pointer")
                .attr("pointer")
            )
        except RuntimeError as e:
            pass

        raise RuntimeError(
            f"Failed to retrieve data ptr of {self.__value.typename()}. "
            "Consider disabling optimization or use a supported stdlib version"
        )
