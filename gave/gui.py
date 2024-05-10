from enum import Enum
from tkinter import ttk
from typing import Dict, List
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


from .container_model import ContainerModel
from .container import Container


# class SettingsFrame:
#     def __init__(self, master):
#         self.__container_models: List[ContainerModel] = []
#         self.__master = master


class SettingsTab:
    def __init__(self, master):
        self.__master = master
        self.container_models: Dict[uuid.uuid4, ContainerModel] = dict()
        self.frames: Dict[uuid.uuid4, tk.Frame]
        self.update_ui()

    def add_container(self, container: ContainerModel):
        assert container.id not in self.container_models
        self.container_models[container.id] = container

    def update_ui(self):
        # Delete previous items
        # for child in self.__master.winfo_children():
        #     child.destroy()
        for model in self.container_models.values():
            self.update_model_frame(model)

    def update_model_frame(self, model: ContainerModel):
        # Create a frame for each model
        model_frame = tk.Frame(self.__master, bd=2, relief=tk.RAISED, pady=5)
        model_frame.pack(fill=tk.X, expand=True)

        option_menu = model.create_views_menu(model_frame)
        option_menu.pack(side=tk.LEFT, padx=10, pady=10)


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
        for i, model in enumerate(self.__container_models):
            axes = self.__fig.add_subplot(len(self.__container_models), 1, i + 1)
            model.draw_audio_view(axes)
            axes.set_title(model.variable_name)

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

        update_needed = self.__poll_queue() or self.__check_model_for_updates()
        # update_needed = False
        # while True:
        #     try:
        #         msg = self.__msg_queue.get(block=False)
        #         if isinstance(msg, StopMessage):
        #             self.on_closing()
        #         elif isinstance(msg, Container.Raw):
        #             new_model = ContainerModel(msg, 44100)
        #             self.__models[msg.id] = new_model
        #             self.__audio_views.add_audio_view(new_model)
        #             update_needed = True
        #         elif isinstance(msg, ContainerModel.Update):
        #             self.__models[msg.id].update_data(msg.data)
        #             update_needed = True
        #     except queue.Empty:
        #         break

        if update_needed:
            self.__audio_views_tab.update_figures()
            self.__settings_tab.update_ui()

        self.__update_tk_id = self.__window.after(20, self.tkinter_update_callback)
