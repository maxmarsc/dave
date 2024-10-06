from ...debuggers.value import AbstractValue


class StdVector:
    def __init__(self, dbg_value: AbstractValue):
        self.__value = dbg_value

    @property
    def size(self) -> int:
        assert isinstance(self.__value, AbstractValue)

        byte_size = self.data_ptr_value()[0].byte_size()

        # via libstdc++ (GNU) members
        try:
            diff = int(self.__value.attr("_M_impl").attr("_M_finish")) - int(
                self.__value.attr("_M_impl").attr("_M_start")
            )
            return int(diff / byte_size)
        except RuntimeError:
            pass

        # via libc++ (LLVM) members
        try:
            diff = int(self.__value.attr("__end_")) - int(self.__value.attr("__begin_"))
            return int(diff / byte_size)
        except RuntimeError:
            pass

        raise RuntimeError(
            f"Failed to retrieve size of {self.__value.typename()}. "
            "Consider disabling optimization or use a supported stdlib version"
        )

    def data_ptr_value(self) -> AbstractValue:
        assert isinstance(self.__value, AbstractValue)

        # via libstdc++ (GNU) members
        try:
            return self.__value.attr("_M_impl").attr("_M_start")
        except RuntimeError:
            pass

        # via libc++ (LLVM) members
        try:
            return self.__value.attr("__begin_")
        except RuntimeError:
            pass

        raise RuntimeError(
            f"Failed to retrieve data ptr of {self.__value.typename()}. "
            "Consider disabling optimization or use a supported stdlib version"
        )


class StdSpan:
    DYNAMIC_EXTENT = 18446744073709551615

    def __init__(self, dbg_value: AbstractValue, extent: int):
        self.__value = dbg_value
        self.__extent = extent

    @property
    def size(self) -> int:
        assert isinstance(self.__value, AbstractValue)
        if self.__extent != StdSpan.DYNAMIC_EXTENT:
            return self.__extent

        # via libstdc++ (GNU) members
        try:
            return int(self.__value.attr("_M_extent").attr("_M_extent_value"))
        except:
            pass

        # via libc++ (LLVM) members
        try:
            return int(self.__value.attr("__size_"))
        except:
            pass

        # via GSL span members
        try:
            return int(self.__value.attr("storage_").attr("size_"))
        except:
            pass

        raise RuntimeError(
            f"Failed to retrieve size of {self.__value.typename()}. "
            "Consider disabling optimization or use a supported stdlib version"
        )

    def data_ptr_value(self) -> AbstractValue:
        assert isinstance(self.__value, AbstractValue)

        # via libstdc++ (GNU) members
        try:
            return self.__value.attr("_M_ptr")
        except RuntimeError:
            pass

        # via libc++ (LLVM) members
        try:
            return self.__value.attr("__data_")
        except RuntimeError:
            pass

        # via GSL members
        try:
            return self.__value.attr("storage_").attr("data_")
        except RuntimeError:
            pass

        raise RuntimeError(
            f"Failed to retrieve data ptr of {self.__value.typename()}. "
            "Consider disabling optimizations or use a supported stdlib version"
        )
