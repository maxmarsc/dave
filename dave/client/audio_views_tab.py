from tkinter import filedialog, messagebox
from typing import Callable, Dict, List, Tuple

import numpy as np
from multiprocessing.connection import Connection
import tkinter as tk
import customtkinter as ctk
import wave
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from dave.common.logger import Logger
from .container_model import ContainerModel
from .tooltip import Tooltip
from .global_settings import GlobalSettings


# ===========================  AudioViewsTab  ==================================
class AudioViewsTab:
    """
    The Views tab of the dave GUI

    This will contain audio views for each containers, concat/freeze switches,
    the matplotlib toolbar...
    """

    def __init__(
        self,
        master,
        container_models: Dict[int, ContainerModel],
        global_settings: GlobalSettings,
    ):
        self.__container_models = container_models
        self.__global_settings = global_settings
        self.__master = master

        # Audio view rendering
        self.__central_frame_scrollable = ctk.CTkScrollableFrame(
            self.__master,
            corner_radius=0,
            orientation="vertical",
        )

        self.__figures_frame = ctk.CTkFrame(self.__central_frame_scrollable)
        self.__fig = Figure()
        self.__canvas = FigureCanvasTkAgg(self.__fig, master=self.__figures_frame)
        self.__canvas_widget = self.__canvas.get_tk_widget()
        self.__canvas_widget.pack(fill=tk.BOTH, expand=True)
        self.__left_margin_px = 65
        self.__right_margin_px = 40
        self.__top_margin_px = 40
        self.__bottom_margin_px = 40
        self.__prev_canvas_dimensions = (1, 1)

        # Containers Actions
        self.__containers_actions_buttons_frame = ContainersActionsGridFrame(
            self.__central_frame_scrollable, self.__container_models
        )

        # Matplotlib toolbar at the bottom
        self.__toolbar_frame = ctk.CTkFrame(
            self.__master, corner_radius=0, fg_color="transparent", height=45
        )
        self.__toolbar = NavigationToolbar2Tk(self.__canvas, self.__toolbar_frame)
        self.__toolbar.update()
        self.__toolbar.pack()
        self.__toolbar_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # frame packing
        self.__central_frame_scrollable.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.__containers_actions_buttons_frame.pack(
            side=tk.RIGHT,
            fill="y",
            pady=(self.__top_margin_px, 0),
        )
        self.__figures_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.__master.bind("<Configure>", self.on_resize)

    def __subplots_hratios(self) -> List[int]:
        hratios = []
        for model in self.__container_models.values():
            if not model.in_scope:
                continue
            if model.channels > 16:
                Logger().warning(
                    f"Too many channels, skipping container : {model.channels}"
                )
                continue
            if model.frozen and not model.is_view_superposable:
                # If the view is not superposable, we need a subplot for both
                # frozen and live signal - we make them thinner
                hratios.extend([1 for _ in range(model.channels * 2)])
            else:
                # If the view is superposable, just a subplot per channel
                hratios.extend([2 for _ in range(model.channels)])

        return hratios

    def on_resize(self, event):
        # Compute the minimum required height for subplots
        min_height_per_channel = 200  # example height in pixels
        total_channels = sum(
            model.channels
            for model in self.__container_models.values()
            if model.in_scope
        )
        min_height = total_channels * min_height_per_channel

        # Get the current height of the scrollable frame
        current_height = self.__master.winfo_height() - 45

        # Determine the new height to apply
        new_height = max(min_height, current_height)

        # Apply the new height to the figures frame and containers actions frame
        self.__figures_frame.configure(height=new_height)
        self.__containers_actions_buttons_frame.configure(height=new_height)
        self.__canvas_widget.configure(
            height=new_height
        )  # Adjust canvas height accordingly
        self.__canvas.draw_idle()  # Redraw the canvas with the new configuration

        # Update layout adjustments
        self.__master.update_idletasks()  # Force layout update

        # Force the frame to update its size
        self.update_canva_adjustement()

    def update_canva_adjustement(self):
        # Get the canvas width and height in pixels
        dimensions = (
            self.__canvas_widget.winfo_width(),
            self.__canvas_widget.winfo_height(),
        )
        if dimensions == self.__prev_canvas_dimensions:
            return

        # Convert the margin sizes from pixels to inches
        dpi = self.__fig.get_dpi()
        left_margin_in = self.__left_margin_px / dpi
        right_margin_in = self.__right_margin_px / dpi
        top_margin_in = self.__top_margin_px / dpi
        bottom_margin_in = self.__bottom_margin_px / dpi

        # Compute the figure width and height in inches
        figure_width_in = dimensions[0] / dpi
        figure_height_in = dimensions[1] / dpi

        # Calculate subplot adjustments based on fixed margins
        left = left_margin_in / figure_width_in
        right = 1 - (right_margin_in / figure_width_in)
        top = 1 - (top_margin_in / figure_height_in)
        bottom = bottom_margin_in / figure_height_in

        self.__fig.subplots_adjust(left=left, right=right, top=top, bottom=bottom)
        self.__prev_canvas_dimensions = dimensions
        self.__canvas.draw_idle()

    def update_widgets(self):
        self.__update_figures()
        self.__containers_actions_buttons_frame.update_widgets()

    def __update_figures(self):
        self.__fig.clear()
        hratios = self.__subplots_hratios()
        nrows = len(hratios)
        if nrows == 0:
            self.__fig.text(
                0.5, 0.5, "No container in scope", fontsize=14, ha="center", va="center"
            )
            self.__canvas.draw_idle()
            return
        subplots_axes = self.__fig.subplots(
            nrows=nrows, ncols=1, gridspec_kw={"height_ratios": hratios}
        )  # type: List[Axes]
        if isinstance(subplots_axes, Axes):
            subplots_axes = np.array([subplots_axes])
        i = 0
        for model in self.__container_models.values():
            if not model.in_scope or model.channels > 16:
                continue
            for channel in range(model.channels):
                title = (
                    f"channel {channel}"
                    if not model.mid_side
                    else " {}".format("mid" if channel == 0 else "side")
                )

                if model.frozen and not model.is_view_superposable:
                    axes = subplots_axes[i : i + 2]
                    axes[1].yaxis.set_label_position("right")
                    axes[1].set_ylabel(
                        title + " (f)", rotation=270, labelpad=10, va="bottom"
                    )
                    i += 2
                else:
                    axes = subplots_axes[i : i + 1]
                    i += 1

                axes[0].yaxis.set_label_position("right")
                axes[0].set_ylabel(title, rotation=270, labelpad=10, va="bottom")
                model.draw_audio_view(axes, channel, self.__global_settings.samplerate)
        self.__canvas.draw_idle()
        self.on_resize(None)


# =======================  ContainersActionsGridFrame  =========================
class ContainersActionsGridFrame(ctk.CTkFrame):
    """
    Holds the ActionButtonsFrame for every (in scope) container
    """

    def __init__(self, master: tk.Misc, container_models: Dict[int, ContainerModel]):
        super().__init__(master, width=60, corner_radius=0, fg_color="transparent")
        self.__container_models = container_models
        self.__container_actions_frame: Dict[int, ContainerActionsFrame] = dict()
        self.grid_columnconfigure(0, weight=1)

    def update_widgets(self):
        # First delete old occurences
        to_delete = []
        for id, button_frame in self.__container_actions_frame.items():
            if (
                id not in self.__container_models
                or not self.__container_models[id].in_scope
            ):
                # Reset the weight of its grid
                self.grid_rowconfigure(index=button_frame.grid_info()["row"], weight=0)
                button_frame.destroy()
                to_delete.append(id)

        for id in to_delete:
            del self.__container_actions_frame[id]

        # Then update the position of the left occurences
        for i, button_frame in enumerate(self.__container_actions_frame.values()):
            # First reset its old row to weight 0
            self.grid_rowconfigure(index=button_frame.grid_info()["row"], weight=0)
            button_frame.grid(row=i, column=0, sticky="ew", padx=(5, 5))
            button_frame.update_widgets()

        # Then add new containers
        for id, container in self.__container_models.items():
            if id not in self.__container_actions_frame and container.in_scope:
                idx = len(self.__container_actions_frame)
                self.__container_actions_frame[id] = ContainerActionsFrame(
                    self, container
                )
                # Place the new button frame
                self.__container_actions_frame[id].grid(
                    row=idx, column=0, sticky="ew", padx=(5, 0)
                )

        self.__update_row_weights()

    def __update_row_weights(self):
        for i, id in enumerate(self.__container_actions_frame):
            weight = self.__container_models[id].channels
            self.grid_rowconfigure(index=i, weight=weight)


# =========================  ContainerActionsFrame  ============================
class ContainerActionsFrame(ctk.CTkFrame):
    """
    Holds the action switches (Freeze, Concatenate ...) of a single container
    """

    def __init__(self, master: tk.Misc, container: ContainerModel) -> None:
        # self.__master = master
        super().__init__(
            master, fg_color=ctk.ThemeManager.theme["CTkFrame"]["top_fg_color"]
        )
        self.__container = container
        self.__freeze_var = tk.BooleanVar(value=self.__container.frozen)
        self.__concat_var = tk.BooleanVar(value=self.__container.concat)
        self.__freeze_var.trace_add("write", self.freeze_button_clicked)
        self.__concat_var.trace_add("write", self.concat_button_clicked)
        self.__font = ctk.CTkFont(size=15)

        # Create label
        self.__name_label = ctk.CTkLabel(
            self, text=self.__container.variable_name, font=self.__font
        )

        # Create buttons
        self.__freeze_button = ctk.CTkSwitch(
            self,
            text="Freeze",
            variable=self.__freeze_var,
            onvalue=True,
            offvalue=False,
            font=self.__font,
        )
        self.__concat_button = ctk.CTkSwitch(
            self,
            text="Concat",
            variable=self.__concat_var,
            onvalue=True,
            offvalue=False,
            font=self.__font,
        )
        self.__save_button = ctk.CTkButton(
            self,
            text="Save",
            width=120,
            command=self.__save_button_clicked,
            font=self.__font,
        )

        # Create tooltips
        Tooltip(self.__save_button, text="Save to disc")
        # Make available the full name
        Tooltip(self.__name_label, text=self.__container.variable_name)

        # Packing
        self.__name_label.grid(row=0, column=0, padx=(5, 5), pady=(5, 5))
        self.__freeze_button.grid(row=1, column=0, padx=(5, 5), pady=(5, 5))
        self.__concat_button.grid(row=2, column=0, padx=(5, 5), pady=(5, 5))
        self.__save_button.grid(row=3, column=0, padx=(5, 5), pady=(5, 5))
        self.columnconfigure(0, weight=1)

    def update_widgets(self):
        self.__freeze_var.set(self.__container.frozen)
        self.__concat_var.set(self.__container.concat)

    def freeze_button_clicked(self, *_):
        self.__container.frozen = self.__freeze_var.get()

    def concat_button_clicked(self, *_):
        self.__container.concat = self.__concat_var.get()

    def __save_button_clicked(self):
        filetypes = [("Numpy file", ".npy")]
        if self.__container.selected_layout.is_real:
            filetypes.append(("Wave - 16bit PCM", ".wav"))
        filename: str = filedialog.asksaveasfilename(parent=self, filetypes=filetypes)
        if not filename:
            return
        if filename.endswith(".wav"):
            self.__save_as_wave(filename)
        elif filename.endswith(".npy"):
            self.__save_as_npy(filename)
        else:
            raise RuntimeError(f"Unsupported extension : {filename}")

    def __save_as_wave(self, filename: str):
        data = self.__container.data.T
        if np.max(np.abs(data)) > 1.0:
            messagebox.showwarning(
                title="Saturation detected",
                message="Values outside the [-1;1] range were detected, values will be truncated",
            )
            # Truncate values
            data[np.where(data < -1.0)] = -1.0
            data[np.where(data > 1.0)] = 1.0
        pcm_data = np.int16(data * (2**15 - 1))

        with wave.open(filename, "w") as f:
            f.setnchannels(self.__container.channels)
            # 2 bytes per sample.
            f.setsampwidth(2)
            f.setframerate(44100)
            f.writeframes(pcm_data.tobytes())

    def __save_as_npy(self, filename: str):
        np.save(filename, self.__container.data)
