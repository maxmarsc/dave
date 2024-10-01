from abc import ABC, abstractmethod
from typing import List


class Setting(ABC):
    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> bool:
        return self._name

    @property
    @abstractmethod
    def value(self):
        pass


class BoolSetting(Setting):
    def __init__(self, name: str, value: bool = None):
        super().__init__(name)
        if value:
            self.value = value
        else:
            self.value = self.possible_values()[0]

    @property
    def value(self) -> bool:
        return self.__value

    @value.setter
    def value(self, value: bool):
        self.__value = value

    @staticmethod
    def possible_values() -> List[bool]:
        return (True, False)


class IntSetting(Setting):
    def __init__(
        self, name: str, min: int, max: int, default: int, value: int = None
    ) -> None:
        super().__init__(name)
        self.__default = default
        self.__min = min
        self.__max = max
        if value:
            self.__value = value
        else:
            self.__value = self.default_value()

    def default_value(self) -> int:
        return self.__default

    def validate(self, value) -> bool:
        if isinstance(value, str):
            try:
                value = int(value)
            except ValueError:
                return False
        return value >= self.__min and value <= self.__max

    @property
    def value(self) -> int:
        return self.__value

    @value.setter
    def value(self, new_value: int):
        if new_value < self.__min:
            self.__value = self.__min
        elif new_value > self.__max:
            self.__value = self.__max
        else:
            self.__value = new_value


class FloatSetting(Setting):
    def __init__(
        self, name: str, min: float, max: float, default: float, value: float = None
    ) -> None:
        super().__init__(name)
        self.__default = default
        self.__min = min
        self.__max = max
        if value:
            self.__value = value
        else:
            self.__value = self.default_value()

    def default_value(self) -> float:
        return self.__default

    @property
    def value(self) -> float:
        return self.__value

    def validate(self, value) -> bool:
        if isinstance(value, str):
            try:
                value = float(value)
            except ValueError:
                return False
        return value >= self.__min and value <= self.__max

    @value.setter
    def value(self, new_value: float):
        if new_value < self.__min:
            self.__value = self.__min
        elif new_value > self.__max:
            self.__value = self.__max
        else:
            self.__value = new_value


class StringSetting(Setting):
    def __init__(self, name: str, values: List[str], value: str = None) -> None:
        super().__init__(name)
        self.__possible_values = values
        if value:
            self.value = value
        else:
            self.value = self.possible_values()[0]

    @property
    def value(self) -> str:
        return self.__value

    @value.setter
    def value(self, new_value: str):
        assert new_value in self.possible_values()
        self.__value = new_value

    def possible_values(self) -> List[str]:
        return self.__possible_values


# class ScaleSetting(StringSetting):
#     def __init__(self, name: str, value: str = None) -> None:
#         super().__init__(name, value)

#     @staticmethod
#     def possible_values() -> List[str]:
#         return ["linear", "log"]
