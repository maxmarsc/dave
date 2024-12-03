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

from .entity.entity_model import EntityModel
from .global_settings import GlobalSettings
from .side_panel import SidePanel


# ===========================  AudioViewsTab  ==================================
class AudioViewsTab:
    """
    The Views tab of the dave GUI

    This will contain audio views for each entity, concat/freeze switches,
    the matplotlib toolbar...
    """

    def __init__(
        self,
        master: tk.Misc,
        entity_models: Dict[int, EntityModel],
        global_settings: GlobalSettings,
    ):
        self.__entity_models = entity_models
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
        self.__containers_actions_buttons_frame = SidePanels(
            self.__central_frame_scrollable, self.__entity_models
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
            pady=(0, self.__bottom_margin_px),
        )
        self.__figures_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.__master.bind("<Configure>", self.on_resize)

    def __subplots_hratios(self) -> List[int]:
        hratios = []
        for model in self.__entity_models.values():
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
        min_height_per_channel = 200  # height in pixels
        total_channels = sum(
            model.channels for model in self.__entity_models.values() if model.in_scope
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
        for model in self.__entity_models.values():
            if not model.in_scope or model.channels > 16:
                continue
            for channel in range(model.channels):
                title = model.channel_name(channel)

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
                model.draw_view(
                    axes, self.__global_settings.samplerate, channel=channel
                )
        self.__canvas.draw_idle()
        self.on_resize(None)


# =======================  ContainersActionsGridFrame  =========================
class SidePanels(ctk.CTkFrame):
    """
    Holds the side panel for each (in-scope) entity
    """

    def __init__(self, master: tk.Misc, entity_models: Dict[int, EntityModel]):
        super().__init__(master, width=60, corner_radius=0, fg_color="transparent")
        self.__entity_models = entity_models
        self.__side_panels: Dict[int, SidePanel] = dict()
        self.grid_columnconfigure(0, weight=1)

    def update_widgets(self):
        # First delete old occurences
        to_delete = []
        for id, button_frame in self.__side_panels.items():
            if id not in self.__entity_models or not self.__entity_models[id].in_scope:
                # Reset the weight of its grid
                self.grid_rowconfigure(index=button_frame.grid_info()["row"], weight=0)
                button_frame.destroy()
                to_delete.append(id)

        for id in to_delete:
            del self.__side_panels[id]

        # Then update the position of the left occurences
        for i, button_frame in enumerate(self.__side_panels.values()):
            # First reset its old row to weight 0
            self.grid_rowconfigure(index=button_frame.grid_info()["row"], weight=0)
            button_frame.grid(row=i, column=0, sticky="ew", padx=(5, 5))
            button_frame.update_widgets()

        # Then add new containers
        for id, container in self.__entity_models.items():
            if id not in self.__side_panels and container.in_scope:
                idx = len(self.__side_panels)
                self.__side_panels[id] = SidePanel(self, container)
                # Place the new button frame
                self.__side_panels[id].grid(row=idx, column=0, sticky="ew", padx=(5, 0))

        self.__update_row_weights()

    def __update_row_weights(self):
        for i, id in enumerate(self.__side_panels):
            weight = self.__entity_models[id].channels
            self.grid_rowconfigure(index=i, weight=weight)
