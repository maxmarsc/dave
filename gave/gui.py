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


class SettingsFrame:
    def __init__(self, master):
        self.__container_models: List[ContainerModel] = []
        self.__master = master


class AudioViewsFrame:
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
        self.__window = tk.Tk()
        self.__window.title("GDB Debugger Information")
        self.__window.minsize(400, 600)
        self.__window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.__audio_views = AudioViewsFrame(self.__window)
        self.__models: Dict[uuid.uuid4, ContainerModel] = dict()
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

    def tkinter_update_callback(self):
        self.__update_tk_id = ""
        update_needed = False
        while True:
            try:
                msg = self.__msg_queue.get(block=False)
                if isinstance(msg, StopMessage):
                    self.on_closing()
                elif isinstance(msg, ContainerModel):
                    self.__models[msg.id] = msg
                    self.__audio_views.add_audio_view(msg)
                    update_needed = True
                elif isinstance(msg, ContainerModel.Update):
                    self.__models[msg.id].update_data(msg.data)
                    update_needed = True
            except queue.Empty:
                break

        if update_needed:
            self.__audio_views.update_figures()

        self.__update_tk_id = self.__window.after(20, self.tkinter_update_callback)
