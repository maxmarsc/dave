from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, List, Tuple, Union

from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPalette, QColor

import pyqtgraph as pg


def hex_to_rgb_tuple(hex_color: str) -> Tuple[int, int, int]:
    """Convert matplotlib hex color to RGB tuple (0-255)"""
    assert len(hex_color) == 7 and hex_color[0] == "#"
    return (
        int(hex_color[1:3], 16),
        int(hex_color[3:5], 16),
        int(hex_color[5:7], 16),
    )


class EntityView(ABC):
    DEFAULT_COLOR = hex_to_rgb_tuple("#1f76b4")

    @staticmethod
    @abstractmethod
    def name() -> str:
        pass

    @staticmethod
    def is_superposable() -> bool:
        return True

    @abstractmethod
    def _render_view(
        self,
        plot_widget: pg.PlotWidget,
        data: Any,
        samplerate: int,
        color: Union[None, str] = None,
    ):
        pass

    def render_view(
        self,
        plot_widget: pg.PlotWidget,
        data: Any,
        samplerate: int,
        name: str,
        color: Union[None, str] = None,
    ):
        # Plot the graph
        self._render_view(plot_widget, data, samplerate, color)

        # Get default colors
        bg_color, mid_color, fg_color = self.palette_colors(plot_widget)

        # Setup axis colors
        plot_widget.plotItem.getAxis("left").setPen(mid_color)
        plot_widget.plotItem.getAxis("right").setPen(mid_color)
        plot_widget.plotItem.getAxis("bottom").setPen(mid_color)

        # Set background color
        plot_widget.setBackground(bg_color)

        # Setup graph name
        plot_widget.plotItem.setLabel("right", name, pen=fg_color)

    @abstractmethod
    def get_settings(self) -> List[EntityView.Setting]:
        pass

    @abstractmethod
    def update_setting(self, setting_name: str, setting_value: Any):
        pass

    @staticmethod
    def palette_colors(
        widget: QWidget,
    ) -> Tuple[Tuple[int, int, int], Tuple[int, int, int]]:
        palette = widget.palette()
        bg_color = hex_to_rgb_tuple(palette.color(QPalette.ColorRole.Window).name())
        mid_color = hex_to_rgb_tuple(palette.color(QPalette.ColorRole.Mid).name())
        fg_color = hex_to_rgb_tuple(palette.color(QPalette.ColorRole.WindowText).name())

        return (bg_color, mid_color, fg_color)

    # ==========================================================================
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
