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
from .buffer import Buffer


# class BufferHandler:
#     def __init__(self, buffer: Buffer):
#         self.__buffer = buffer
class Setting:
    pass


class AudioView(ABC):
    def __init__(self, samplerate: float) -> None:
        self.__sr = samplerate

    @abstractmethod
    @property
    def name(self) -> str:
        pass

    @abstractmethod
    def render_view(self, axes: Axes, data: np.ndarray):
        pass

    @abstractmethod
    def get_settings(self) -> List[Setting]:
        pass


class WaveformView(AudioView):
    @property
    def name(self) -> str:
        return "Waveform"

    def render_view(self, axes: Axes, data: np.ndarray):
        axes.plot(data)

    def get_settings(self) -> List[Setting]:
        return []


class BufferView:
    def __init__(self, buffer: Buffer):
        self.__buffer = buffer
        self.__data: np.ndarray = None
        # self.__settings = None


# class View:
class ViewFrame:
    def __init__(self, master):
        self.__buffer_views = []
        self.__master = master
        self.__fig = None
        self.__canva = None

    def __update_figures(self):
        self.__fig = Figure()
        self.__canva = FigureCanvasTkAgg(self.__fig, master=self.__master)
        # self.__axs = self.__fig.subplots(len(self.__buffer_views))
        for i, buffer_view in enumerate(self.__buffer_views):
            axes: Axes = self.__fig.add_subplot(len(self.__buffers), 1, i)
            buffer_view.draw(axes)


class DebuggerGUI(future_gdb.Thread, metaclass=SingletonMeta):
    def __init__(self, msg_queue):
        threading.Thread.__init__(self)
        self.__msg_queue = msg_queue
        self.__window = None
        self.__should_stop = False
        self.__gui_active = False
        self.__buffers = []

    def __init_window(self):
        self.__window = tk.Tk()
        self.__window.title("GDB Debugger Information")
        self.__window.minsize(400, 600)
        # self.__fig = Figure()
        # self.__canva =
        self.__window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def __update_figures(self):
        self.__fig = Figure()
        self.__canva = FigureCanvasTkAgg(self.__fig, master=self.__window)
        for i, buffer in enumerate(self.__buffers):
            ax = self.__fig.add_subplot(len(self.__buffers), 1, i)
            ax.plot()
        # self.__fig.add_subplot(len(self.__buffers), 1)

    def run(self):
        print("[LOG] starting thread routine")
        while not self.__should_stop:
            if self.__gui_active:
                if self.__window is None:
                    self.__init_window()
                self.__window.update_idletasks()
                self.__window.update()
            else:
                time.sleep(0.05)
        print("[LOG] stopping thread routine")

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
            self.__window.destroy()
            self.__window = None


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
