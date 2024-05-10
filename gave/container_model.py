from matplotlib.axes import Axes
from .container import Container
from .data_model import DataModel
from .views import get_views_for_data_model, AudioView, get_view_from_name

import gdb
import tkinter as tk


class ContainerModel:
    def __init__(self, container: Container, samplerate: float):
        self.__gdb_container = container
        self.__data = container.read_from_gdb()
        self.__sr = samplerate
        # First as default
        self.__data_model = container.available_data_models()[0]
        # First as default
        self.__view: AudioView = get_views_for_data_model(self.__data_model)[0](
            self.__sr
        )

    # def view_var_callback(self, *args):
    #     new_view = self.__view_var.get()
    #     self.__view =

    @property
    def variable_name(self) -> str:
        return self.__gdb_container.name

    def draw_audio_view(self, axes: Axes):
        self.__view.render_view(axes, self.__data)

    def update_from_gdb(self):
        self.__data = self.__gdb_container.read_from_gdb()

    def show_settings(self, master):
        pass
