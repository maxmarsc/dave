from typing import List
from matplotlib.axes import Axes
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
        # self.__view_var = tk.StringVar(value=self.__view.name())
        # self.__view_var.trace_add("write", self.view_var_callback)

    # ==============================================================================
    @property
    def possible_views(self) -> List[str]:
        return [view.name() for view in get_views_for_data_layout(self.__data_layout)]

    @property
    def selected_view(self) -> str:
        return self.__view.name()

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

    # def view_var_callback(self, *args):
    #     new_view_name = self.__view_var.get()
    #     possibles_views = get_views_for_data_layout(self.__data_layout)
    #     for view_type in possibles_views:
    #         if view_type.name() == new_view_name:
    #             # print("\tUpdating to ")
    #             self.__view = view_type(self.__sr)
    #             self.__update_pending = True
    #             break

    # def create_views_menu(self, master) -> tk.OptionMenu:
    #     options = [
    #         view.name() for view in get_views_for_data_layout(self.__data_layout)
    #     ]
    #     return tk.OptionMenu(master, self.__view_var, *options)

    # def get_views_name_for_data_layout(self) -> List[str]:
    #     return [view.name for view in get_views_for_data_layout(self.__data_layout)]

    def draw_audio_view(self, axes: Axes):
        self.__view.render_view(axes, self.__raw.data)

    # ==============================================================================
    def update_data(self, new_data: np.ndarray):
        self.__raw.data = new_data
        self.__update_pending = True

    def update_view_type(self, view_name: str):
        possibles_views = get_views_for_data_layout(self.__data_layout)
        for view_type in possibles_views:
            if view_type.name() == view_name:
                self.__view = view_type(self.__sr)
                self.__update_pending = True
                break

    def show_settings(self, master):
        pass
