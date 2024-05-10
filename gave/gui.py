from enum import Enum
from typing import List
import gdb  # type: ignore
import gdb.types  # type: ignore

import threading
import queue
import tkinter as tk
import time
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np

from abc import ABC, abstractmethod

from . import future_gdb
from .singleton import SingletonMeta
from .container import Container
from .container_model import ContainerModel
from .data_model import DataModel
from .views import get_views_for_data_model


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
            axes: Axes = self.__fig.add_subplot(len(self.__container_models), 1, i + 1)
            model.draw_audio_view(axes)
            axes.set_title(model.variable_name)

        self.__canvas.draw_idle()


class DebuggerGUI(future_gdb.Thread, metaclass=SingletonMeta):
    def __init__(self, msg_queue: queue.Queue):
        threading.Thread.__init__(self)
        self.__msg_queue = msg_queue
        self.__window = None
        self.__should_stop = False
        self.__gui_active = False
        self.__models: List[ContainerModel] = []
        self.__update_needed = True
        self.__update_lock = threading.Lock()
        self.__update_tk_id = ""

    def __init_gui(self):
        self.__window = tk.Tk()
        self.__window.title("GDB Debugger Information")
        self.__window.minsize(400, 600)
        self.__window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.__audio_views = AudioViewsFrame(self.__window)

    def gdb_update_callback(self):
        if self.__gui_active:
            self.__update_lock.acquire()
            for model in self.__models:
                model.update_from_gdb()
            self.__update_needed = True
            self.__update_lock.release()

    def tkinter_update_callback(self):
        if self.__should_stop:
            self.on_closing()
            return
        self.__update_lock.acquire()
        if self.__poll_queue() or self.__update_needed:
            self.__audio_views.update_figures()
            self.__update_needed = False
        self.__update_lock.release()
        self.__update_tk_id = self.__window.after(20, self.tkinter_update_callback)

    def run(self):
        while not self.__should_stop:
            if self.__gui_active:
                if self.__window is None:
                    self.__init_gui()

                self.__update_tk_id = self.__window.after(
                    20, self.tkinter_update_callback
                )
                self.__window.mainloop()
                # # Check for model update
                # self.__update_lock.acquire()
                # if self.__poll_queue() and self.__update_needed == False:
                #     self.__update_needed = True
                # if self.__update_needed:
                #     self.__audio_views.update_figures()
                #     self.__update_needed = False
                # self.__update_lock.release()

                # # Update the GUI
                # self.__window.update_idletasks()
                # self.__window.update()
            else:
                time.sleep(0.05)
        print("[LOG] stopping thread routine")

    def __poll_queue(self) -> bool:
        update_needed = False
        while True:
            try:
                new_model = self.__msg_queue.get(block=False)
                self.__msg_queue.task_done()
                print("New model received")
                self.__models.append(new_model)
                self.__audio_views.add_audio_view(new_model)
                update_needed = True
            except queue.Empty:
                return update_needed

    def should_stop(self):
        self.__should_stop = True

    def is_gui_active(self) -> bool:
        return self.__gui_active

    def activate_gui(self):
        self.__gui_active = True

    def on_closing(self):
        self.__gui_active = False
        if self.__window:
            self.__window.quit()
            if self.__update_tk_id:
                self.__window.after_cancel(self.__update_tk_id)
            self.__window.destroy()
            self.__window = None
            self.__models = list()


# class DebuggerGUI(gdb.Thread):
#     def __init__(self, msg_queue):
#         threading.Thread.__init__(self)
#         self.msg_queue = msg_queue
#         self.window = None
#         self.active = False  # Flag to keep the thread running
#         self.__should_stop = False
#         self.start()

#     def start_gui(self):
#         self.active = True

#     def stop_gui(self):
#         self.active = False

#     def should_stop(self):
#         self.__should_stop = True

#     def is_gui_active(self) -> bool:
#         return self.active

#     def run(self):
#         while not self.__should_stop:
#             if self.active:
#                 self.init_window()
#                 self.routine()
#             else:
#                 time.sleep(0.05)
#         print("[LOG] exiting run")

#     def init_window(self):
#         print("[LOG] init_window")
#         self.window = tk.Tk()
#         self.window.title("GDB Debugger Information")
#         self.window.minsize(400, 600)
#         self.label = tk.Label(self.window, text="Waiting for data...")
#         self.label.pack(pady=20, padx=20)
#         # tk.Button(self.window, text="Close", command=self.window.destroy).pack(pady=10)
#         self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
#         # self.window.mainloop()

#     def routine(self):
#         print("[LOG] Entering routine")
#         while self.active:
#             self.window.update_idletasks()
#             self.window.update()
#         print("[LOG] Exiting routine")

#     def poll_queue(self):
#         pass
#         # print("poll_queue")
#         # if self.active:  # Check if the window is still active
#         #     try:
#         #         msg = self.msg_queue.get_nowait()
#         #         self.label.config(text=msg)
#         #         self.msg_queue.task_done()
#         #     except queue.Empty:
#         #         pass
#         #     finally:
#         #         self.window.after(100, self.poll_queue)  # Schedule the next poll

#     def on_closing(self):
#         self.active = False  # Set the flag to false to stop the thread
#         if self.window:
#             self.window.destroy()
