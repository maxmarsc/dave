from typing import Any, List
from matplotlib.axes import Axes

from .view_setting import Setting
from .container import Container
from .data_layout import DataLayout
from .views import get_views_for_data_layout, AudioView, get_view_from_name

from dataclasses import dataclass
import numpy as np

# import gdb
import tkinter as tk
import uuid


class ContainerModel:
    @dataclass
    class Update:
        id: uuid.uuid4
        data: np.ndarray

    def __init__(self, raw: Container.Raw, samplerate: float):
        self.__raw = raw
        self.__sr = samplerate
        if not issubclass(raw.container_cls, Container):
            raise RuntimeError(f"{raw.container_cls} is not a valid container class")
        # First as default
        self.__data_layout = self.__raw.container_cls.available_data_layouts()[0]
        # First as default
        self.__view: AudioView = get_views_for_data_layout(self.__data_layout)[0](
            self.__sr
        )
        self.__update_pending = True

    # ==============================================================================
    @property
    def possible_layouts(self) -> List[DataLayout]:
        return self.__raw.container_cls.available_data_layouts()

    @property
    def selected_layout(self) -> DataLayout:
        return self.__data_layout

    @property
    def possible_views(self) -> List[str]:
        # print(f"possible_view : {get_views_for_data_layout(self.__data_layout)}")
        return [view.name() for view in get_views_for_data_layout(self.__data_layout)]

    @property
    def selected_view(self) -> str:
        return self.__view.name()

    @property
    def view_settings(self) -> List[Setting]:
        return self.__view.get_settings()

    @property
    def variable_name(self) -> str:
        return self.__raw.name

    @property
    def id(self) -> uuid.uuid4:
        return self.__raw.id

    # ==============================================================================
    def check_for_update(self) -> bool:
        return self.__update_pending

    def reset_update_flag(self):
        self.__update_pending = False

    def draw_audio_view(self, axes: Axes):
        self.__view.render_view(axes, self.__raw.data)

    # ==============================================================================
    def update_data(self, new_data: np.ndarray):
        self.__raw.data = new_data
        self.__update_pending = True

    def update_layout(self, new_layout: DataLayout):
        assert new_layout in self.possible_layouts
        self.__data_layout = new_layout
        self.__view: AudioView = get_views_for_data_layout(self.__data_layout)[0](
            self.__sr
        )
        self.__update_pending = True

    def update_view_type(self, view_name: str):
        possibles_views = get_views_for_data_layout(self.__data_layout)
        for view_type in possibles_views:
            if view_type.name() == view_name:
                self.__view = view_type(self.__sr)
                self.__update_pending = True
                break

    def update_view_settings(self, setting_name: str, setting_value: Any):
        self.__view.update_setting(setting_name, setting_value)
        self.__update_pending = True

    # def show_settings(self, master):
    #     pass
