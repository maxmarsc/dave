from enum import Enum
from tkinter import StringVar, ttk
from typing import Dict, List, Tuple
import gdb  # type: ignore
import gdb.types  # type: ignore
import uuid

import threading
import multiprocessing
import queue
import tkinter as tk
import time
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np

from .data_layout import DataLayout
from .container_model import ContainerModel
from .container import Container
from .view_setting import FloatSetting, IntSetting, Setting, StringSetting


# class SettingsFrame:
#     def __init__(self, master):
#         self.__container_models: List[ContainerModel] = []
#         self.__master = master


class ContainerSettingsFrame:
    def __init__(self, master: tk.Misc, model: ContainerModel) -> None:
        self.__model = model
        self.__master = master
        self.__frame = tk.Frame(self.__master, bd=2, relief=tk.RAISED, pady=5)
        # Label
        self.__name_label = tk.Label(
            self.__frame, text=f"{self.__model.variable_name} : ", font="bold"
        )
        self.__name_label.pack(side=tk.LEFT, fill="y")
        ttk.Separator(self.__frame, orient="vertical").pack(side=tk.LEFT, fill="y")
        # Layout selection
        self.__layout_menu = None
        self.__layout_separator = None
        self.__layout_var = tk.StringVar(value=self.__model.selected_layout.value)
        self.__layout_var.trace_add("write", self.layout_var_callback)
        # Optionnal channel menu
        self.__channel_label = None
        self.__channel_entry = None
        # self.__channel_var = None
        self.__channel_separator = None
        # View selection
        self.__view_menu = None
        self.__view_separator = None
        self.__view_var = tk.StringVar(value=self.__model.selected_view)
        self.__view_var.trace_add("write", self.view_var_callback)
        # Settings selection
        self.__view_settings_frame = None
        self.__view_settings = None

        self.update()
        self.__frame.pack(side=tk.TOP, fill="x")

    def view_var_callback(self, *_):
        # Update the model
        self.__model.update_view_type(self.__view_var.get())
        # Reset the settings of the view
        self.__view_settings_frame.destroy()
        self.__view_settings_frame = None
        self.__view_settings = None
        # Trigger a redraw
        self.update()

    def layout_var_callback(self, *_):
        # Update the model
        self.__model.update_layout(DataLayout(self.__layout_var.get()))
        # Reset the view selector
        self.__view_menu.destroy()
        self.__view_separator.destroy()
        self.__view_menu = None
        if self.__channel_label:
            self.__channel_label.destroy()
            if self.__channel_entry:
                self.__channel_entry.destroy()
            self.__channel_separator.destroy()
            self.__channel_label = None
        # Update the view type -> this will trigger the view_var_callback
        self.__view_var.set(value=self.__model.selected_view)

    def update(self):
        # Create the layout menu
        if not self.__layout_menu:
            possible_layouts_name = [
                layout.value for layout in self.__model.possible_layouts
            ]
            self.__layout_menu = tk.OptionMenu(
                self.__frame, self.__layout_var, *possible_layouts_name
            )
            self.__layout_menu.pack(side=tk.LEFT, padx=10, pady=10)
            self.__layout_separator = ttk.Separator(self.__frame, orient="vertical")
            self.__layout_separator.pack(side=tk.LEFT, fill="y")

        # Create the channel menu
        if self.__model.is_layout_2D() and not self.__channel_label:
            if self.__model.is_channel_layout_fixed():
                # If the number of channels is fixed, we only display it
                self.__channel_label = tk.Label(
                    self.__frame, text=f"channels : {self.__model.channels}"
                )
                self.__channel_label.pack(side=tk.LEFT, padx=5)
            else:
                vcmd = (self.__master.register(self.__model.update_channel), "%P")
                self.__channel_label = tk.Label(self.__frame, text=f"channels :")
                self.__channel_entry = tk.Entry(
                    self.__frame,
                    validate="focusout",
                    validatecommand=vcmd,
                )
                self.__channel_entry.insert(0, f"{self.__model.channels}")
                self.__channel_label.pack(side=tk.LEFT, padx=5)
                self.__channel_entry.pack(side=tk.LEFT)
            self.__channel_separator = ttk.Separator(self.__frame, orient="vertical")
            self.__channel_separator.pack(side=tk.LEFT, fill="y")

        # Create the view menu
        if not self.__view_menu:
            self.__view_menu = tk.OptionMenu(
                self.__frame, self.__view_var, *self.__model.possible_views
            )
            self.__view_menu.pack(side=tk.LEFT, padx=10, pady=10)
            self.__view_separator = ttk.Separator(self.__frame, orient="vertical")
            self.__view_separator.pack(side=tk.LEFT, fill="y")
        # Create the settings menu
        if not self.__view_settings_frame:
            self.__view_settings_frame = tk.Frame(self.__frame)
            self.__view_settings_frame.pack(side=tk.LEFT, fill="both")
        if not self.__view_settings:
            self.__view_settings = ViewSettingsFrame(
                self.__view_settings_frame, self.__model
            )


class ViewSettingsFrame:
    def __init__(self, master: tk.Misc, container: ContainerModel) -> None:
        self.__master = master
        self.__container = container
        self.__container_suffix = "_" + str(container.id)
        self.__vars: Dict[str, tk.Variable] = dict()
        for setting in container.view_settings:
            if isinstance(setting, StringSetting):
                self.create_string_selector(setting)
            elif isinstance(setting, IntSetting):
                self.create_int_selector(setting)
            elif isinstance(setting, FloatSetting):
                self.create_float_selector(setting)
            else:
                raise NotImplementedError()

    def create_string_selector(self, setting: StringSetting):
        # Create the StringVar to keep updated of changes
        var_name = setting.name + self.__container_suffix
        var = tk.StringVar(value=setting.value, name=var_name)
        self.__vars[var_name] = var
        var.trace_add("write", self.var_callback)
        # Create the option menu & the label
        label = tk.Label(self.__master, text=setting.name)
        menu = tk.OptionMenu(self.__master, var, *setting.possible_values())
        label.pack(side=tk.LEFT, padx=5)
        menu.pack(side=tk.LEFT)

    def create_float_selector(self, setting: FloatSetting):
        # Create the DoubleVar to keep updated of changes
        var_name = setting.name + self.__container_suffix
        var = tk.DoubleVar(value=setting.value, name=var_name)
        self.__vars[var_name] = var
        vcmd = (self.__master.register(setting.validate), "%P")
        # Create the entry and the label
        label = tk.Label(self.__master, text=setting.name)
        entry = tk.Entry(
            self.__master,
            textvariable=var,
            validate="focusout",
            validatecommand=vcmd,
        )
        label.pack(side=tk.LEFT, padx=5)
        entry.pack(side=tk.LEFT)
        var.trace_add("write", self.var_callback)

    def create_int_selector(self, setting: IntSetting):
        # Create the DoubleVar to keep updated of changes
        var_name = setting.name + self.__container_suffix
        var = tk.IntVar(value=setting.value, name=var_name)
        self.__vars[var_name] = var
        vcmd = (self.__master.register(setting.validate), "%P")
        # Create the entry and the label
        label = tk.Label(self.__master, text=setting.name)
        entry = tk.Entry(
            self.__master,
            textvariable=var,
            validate="focusout",
            validatecommand=vcmd,
        )
        label.pack(side=tk.LEFT, padx=5)
        entry.pack(side=tk.LEFT)
        var.trace_add("write", self.var_callback)

    def var_callback(self, var_name: str, *_):
        assert var_name in self.__vars
        setting_name = var_name[: -len(self.__container_suffix)]
        try:
            self.__container.update_view_settings(
                setting_name, self.__vars[var_name].get()
            )
        except tk.TclError:
            # Might fail when tk update the var with an empty string
            pass


class SettingsTab:
    def __init__(self, master):
        self.__master = master
        self.containers_settings: Dict[uuid.uuid4, ContainerSettingsFrame] = dict()
        # self.frames: Dict[uuid.uuid4, tk.Frame]
        self.update_ui()

    def add_container(self, container: ContainerModel):
        assert container.id not in self.containers_settings
        self.containers_settings[container.id] = ContainerSettingsFrame(
            self.__master, container
        )

    def update_ui(self):
        for settings_frame in self.containers_settings.values():
            settings_frame.update()


class AudioViewsTab:
    def __init__(self, master):
        self.__container_models: List[ContainerModel] = []
        self.__master = master
        self.__fig = Figure()
        self.__canvas = FigureCanvasTkAgg(self.__fig, master=self.__master)
        self.__canvas_widget = self.__canvas.get_tk_widget()
        self.__canvas_widget.pack(fill=tk.BOTH, expand=True)
        self.__toolbar = NavigationToolbar2Tk(self.__canvas, self.__master)
        self.__toolbar.update()
        self.__toolbar.pack()

    def add_audio_view(self, model: ContainerModel):
        self.__container_models.append(model)

    def update_figures(self):
        self.__fig.clear()
        total_figures = sum([model.channels for model in self.__container_models])
        i = 1
        for model in self.__container_models:
            for channel in range(model.channels):
                axes = self.__fig.add_subplot(total_figures, 1, i)
                model.draw_audio_view(axes, channel)
                axes.set_title(model.variable_name + f" channel {channel}")
                i += 1

        self.__canvas.draw_idle()


class StopMessage:
    pass


class GaveGUI:
    def __init__(self, msg_queue: multiprocessing.Queue):
        self.__msg_queue = msg_queue
        self.__models: Dict[uuid.uuid4, ContainerModel] = dict()
        self.__window = tk.Tk()
        self.__window.title("GDB Debugger Information")
        self.__window.minsize(400, 600)
        self.__window.protocol("WM_DELETE_WINDOW", self.on_closing)
        # self.__audio_views = AudioViewsFrame(self.__window)
        self.__notebook = ttk.Notebook(self.__window)
        self.__notebook.pack(fill="both", expand=True)
        self.__audio_tabframe = ttk.Frame(self.__notebook)
        self.__notebook.add(self.__audio_tabframe, text="Views")
        self.__settings_tabframe = ttk.Frame(self.__notebook)
        self.__notebook.add(self.__settings_tabframe, text="Settings")
        self.__audio_views_tab = AudioViewsTab(self.__audio_tabframe)
        self.__settings_tab = SettingsTab(self.__settings_tabframe)
        self.__update_tk_id = ""

    @staticmethod
    def create_and_run(msg_queue: multiprocessing.Queue):
        gui = GaveGUI(msg_queue)
        gui.run()

    def on_closing(self):
        if self.__update_tk_id:
            self.__window.after_cancel(self.__update_tk_id)
        self.__window.destroy()
        self.__models = dict()

    def run(self):
        self.__update_tk_id = self.__window.after(20, self.tkinter_update_callback)
        self.__window.mainloop()

    def __poll_queue(self) -> bool:
        update_needed = False
        while True:
            try:
                msg = self.__msg_queue.get(block=False)
                if isinstance(msg, StopMessage):
                    self.on_closing()
                elif isinstance(msg, Container.Raw):
                    new_model = ContainerModel(msg, 44100)
                    self.__models[msg.id] = new_model
                    self.__audio_views_tab.add_audio_view(new_model)
                    self.__settings_tab.add_container(new_model)
                    update_needed = True
                elif isinstance(msg, ContainerModel.Update):
                    self.__models[msg.id].update_data(msg.data)
                    update_needed = True
            except queue.Empty:
                break

        return update_needed

    def __check_model_for_updates(self) -> bool:
        update_needed = False
        for model in self.__models.values():
            if model.check_for_update():
                update_needed = True
                model.reset_update_flag()
        return update_needed

    def tkinter_update_callback(self):
        self.__update_tk_id = ""

        # Check for new containers
        if self.__poll_queue():
            self.__audio_views_tab.update_figures()
            self.__settings_tab.update_ui()
        elif self.__check_model_for_updates():
            self.__audio_views_tab.update_figures()

        self.__update_tk_id = self.__window.after(20, self.tkinter_update_callback)
