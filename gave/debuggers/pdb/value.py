from ..value import AbstractValue


class PdbValue(AbstractValue):
    def __init__(self, pdb_value: object) -> None:
        super().__init__()
        self.__value = pdb_value

    def get(self) -> object:
        return self.__value
