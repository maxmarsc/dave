from dataclasses import dataclass
from enum import Enum
from tkinter import StringVar, ttk, filedialog, messagebox
from typing import Dict, List, Tuple


import numpy as np
from multiprocessing.connection import Connection
import tkinter as tk
import wave
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from dave.common.data_layout import DataLayout
from dave.common.logger import Logger
from dave.common.raw_container import RawContainer
from dave.server.container import Container
from dave.server.process import DaveProcess
from .container_model import ContainerModel
from .view_setting import FloatSetting, IntSetting, Setting, StringSetting
from .tooltip import Tooltip


class ContainerSettingsFrame:
    """
    Holds all the settings of a container (not the actions buttons)

    This will always contains, left-to-right :
    - Layout selector
    - Channel selector/label
    - View type selector
    - View type settings
    """

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
        self.__channel_interleaved_button = None
        self.__channel_mid_side_button = None
        self.__channel_separator = None
        # View selection
        self.__view_menu = None
        self.__view_separator = None
        self.__view_var = tk.StringVar(value=self.__model.selected_view)
        self.__view_var.trace_add("write", self.view_var_callback)
        # Settings selection
        self.__view_settings_frame = None
        self.__view_settings = None
        # General section
        self.__general_section_frame = None
        self.__general_section_separator = None
        self.__delete_button = None

        self.update()
        self.__frame.pack(side=tk.TOP, fill="x")

    def layout_var_callback(self, *_):
        # Update the model
        self.__model.update_layout(DataLayout(self.__layout_var.get()))
        # Reset the old gui widgets
        self.reset_channel_menu()
        self.reset_view_menu()
        self.reset_view_settings()
        # Update the view_var with the default view of the layout
        self.__view_var.set(self.__model.selected_view)
        # Trigger a redraw
        self.update()

    def view_var_callback(self, *_):
        # Update the model
        self.__model.update_view_type(self.__view_var.get())
        # Reset the settings of the view
        self.reset_view_settings()
        # Trigger a redraw
        self.update()

    def reset_view_menu(self):
        # Reset the view selector
        if self.__view_menu:
            self.__view_menu.destroy()
            self.__view_separator.destroy()
            self.__view_menu = None

    def reset_view_settings(self):
        # Reset the settings of the view
        if self.__view_settings_frame:
            self.__view_settings_frame.destroy()
            self.__view_settings_frame = None
            self.__view_settings = None

    def reset_channel_menu(self):
        if self.__channel_label:
            self.__channel_label.destroy()
            if self.__channel_entry:
                self.__channel_entry.destroy()
            self.__channel_separator.destroy()
            self.__channel_label = None
            if self.__channel_interleaved_button:
                self.__channel_interleaved_button.destroy()
                self.__channel_interleaved_button = None
            if self.__channel_mid_side_button:
                self.__channel_mid_side_button.destroy()
                self.__channel_mid_side_button = None

    def interleaved_button_callback(self, *_):
        # Update the model
        self.__model.interleaved = not self.__model.interleaved
        # Update the button
        self.__channel_interleaved_button.config(
            relief=tk.SUNKEN if self.__model.interleaved else tk.RAISED
        )

    def mid_side_button_callback(self, *_):
        # Update the model
        self.__model.mid_side = not self.__model.mid_side
        # Update the button
        self.__channel_mid_side_button.config(
            relief=tk.SUNKEN if self.__model.mid_side else tk.RAISED
        )

    def delete_button_callback(self):
        self.__model.mark_for_deletion()
        self.__frame.destroy()

    def destroy(self):
        self.__frame.destroy()

    def update(self):
        # Create the layout menu
        if not self.__layout_menu:
            possible_layouts_name = [
                layout.value for layout in self.__model.possible_layouts
            ]
            self.__layout_menu = tk.OptionMenu(
                self.__frame, self.__layout_var, *possible_layouts_name
            )
            Tooltip(self.__layout_menu, text="Select data layout of the container")
            self.__layout_menu.pack(side=tk.LEFT, padx=10, pady=10)
            self.__layout_separator = ttk.Separator(self.__frame, orient="vertical")
            self.__layout_separator.pack(side=tk.LEFT, fill="y")

        # If the mid/side button should be added or removed, we force the update
        # by deleting the channel menu
        if (self.__model.channels == 2 and self.__channel_mid_side_button is None) or (
            self.__model.channels != 2 and self.__channel_mid_side_button is not None
        ):
            self.reset_channel_menu()
            self.reset_view_menu()
            self.reset_view_settings()

        # Create the channel menu
        if self.__model.is_layout_2D() and not self.__channel_label:
            if self.__model.is_channel_layout_fixed():
                # If the number of channels is fixed, we only display it
                self.__channel_label = tk.Label(
                    self.__frame, text=f"channels : {self.__model.channels}"
                )
                self.__channel_label.pack(side=tk.LEFT, padx=5)
            else:
                # If the number of channel is not fixed, it might be interleaved
                vcmd = (self.__master.register(self.__model.update_channel), "%P")
                self.__channel_label = tk.Label(self.__frame, text=f"channels :")
                self.__channel_entry = tk.Entry(
                    self.__frame, validate="focus", validatecommand=vcmd, width=4
                )
                self.__channel_entry.insert(0, f"{self.__model.channels}")
                self.__channel_interleaved_button = tk.Button(
                    self.__frame,
                    text="interleaved",
                    relief=tk.SUNKEN if self.__model.interleaved else tk.RAISED,
                    command=self.interleaved_button_callback,
                )
                self.__channel_label.pack(side=tk.LEFT, padx=5)
                self.__channel_entry.pack(side=tk.LEFT)
                self.__channel_interleaved_button.pack(side=tk.LEFT, padx=3)

            if self.__model.channels == 2:
                self.__channel_mid_side_button = tk.Button(
                    self.__frame,
                    text="mid/side",
                    relief=tk.SUNKEN if self.__model.mid_side else tk.RAISED,
                    command=self.mid_side_button_callback,
                )
                self.__channel_mid_side_button.pack(side=tk.LEFT, padx=3)

            self.__channel_separator = ttk.Separator(self.__frame, orient="vertical")
            self.__channel_separator.pack(side=tk.LEFT, fill="y")

        # Create the view menu
        if not self.__view_menu:
            self.__view_menu = tk.OptionMenu(
                self.__frame, self.__view_var, *self.__model.possible_views
            )
            Tooltip(self.__view_menu, text="Select which view to render")
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

        # Create the general menu
        if not self.__general_section_frame:
            self.__general_section_frame = tk.Frame(self.__frame)
            self.__delete_button = tk.Button(
                self.__general_section_frame,
                text="X",
                command=self.delete_button_callback,
            )
            self.__general_section_separator = ttk.Separator(
                self.__frame, orient="vertical"
            )
            self.__general_section_frame.pack(side=tk.RIGHT, fill="y")
            self.__general_section_separator.pack(side=tk.RIGHT, fill="y")
            self.__delete_button.pack(side=tk.RIGHT, anchor=tk.CENTER, padx=[2, 2])


class ViewSettingsFrame:
    """
    A frame containing the selector for every view setting of a model.

    Each type of view has its set of settings. This will create a frame in which
    the user can define the value for each of the settings of the currently
    selected view type
    """

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


class ContainersActionsButtonsFrames:
    """
    Holds the ActionButtonsFrame for every (in scope) container
    """

    def __init__(self, master: tk.Misc, container_models: Dict[int, ContainerModel]):
        self.__master = master
        self.__container_models = container_models
        self.__container_buttons_frame: Dict[int, tk.Frame] = dict()
        self.__container_buttons: Dict[int, ActionButtonsFrame] = dict()

    def update(self):
        # First delete old occurences
        to_delete = []
        for id, buttons_frame in self.__container_buttons_frame.items():
            if (
                id not in self.__container_models
                or not self.__container_models[id].in_scope
            ):
                buttons_frame.destroy()
                to_delete.append(id)

        for id in to_delete:
            del self.__container_buttons[id]
            del self.__container_buttons_frame[id]

        # Then add new containers
        for id, container in self.__container_models.items():
            if id not in self.__container_buttons_frame and container.in_scope:
                idx = len(self.__container_buttons)
                self.__container_buttons_frame[id] = tk.Frame(self.__master)
                self.__container_buttons[id] = ActionButtonsFrame(
                    self.__container_buttons_frame[id], container
                )
                # Place the new button frame
                self.__container_buttons_frame[id].grid(row=idx, column=0)
                self.__master.grid_rowconfigure(index=idx, weight=container.channels)

        # Finally update everyone
        for widget in self.__container_buttons.values():
            widget.update()


class ActionButtonsFrame:
    """
    Holds the action buttons (Freeze, Concatenate ...) of a single container
    """

    def __init__(self, master: tk.Misc, container: ContainerModel) -> None:
        self.__master = master
        self.__container = container

        # Create buttons
        self.__freeze_button = tk.Button(
            self.__master,
            text="F",
            command=self.__freeze_button_clicked,
            relief="raised",
        )
        self.__concat_button = tk.Button(
            self.__master,
            text="C",
            command=self.__concat_button_clicked,
            relief="raised",
        )
        self.__save_button = tk.Button(
            self.__master, text="S", command=self.__save_button_clicked, relief="raised"
        )

        # Create tooltips
        Tooltip(self.__freeze_button, text="Freeze")
        Tooltip(self.__concat_button, text="Concatenate")
        Tooltip(self.__save_button, text="Save to disc")

        # Packing
        self.__freeze_button.pack(anchor=tk.CENTER, fill=tk.X)
        self.__concat_button.pack(anchor=tk.CENTER, fill=tk.X)
        self.__save_button.pack(anchor=tk.CENTER, fill=tk.X)

        self.update()

    def __freeze_button_clicked(self):
        self.__container.frozen = not self.__container.frozen

    def __concat_button_clicked(self):
        self.__container.concat = not self.__container.concat

    def __save_button_clicked(self):
        filetypes = [("Numpy file", ".npy")]
        if self.__container.selected_layout.is_real:
            filetypes.append(("Wave - 16bit PCM", ".wav"))
        filename: str = filedialog.asksaveasfilename(
            parent=self.__master, filetypes=filetypes
        )
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

    def update(self):
        self.__freeze_button.config(
            relief="sunken" if self.__container.frozen else "raised"
        )
        self.__concat_button.config(
            relief="sunken" if self.__container.concat else "raised"
        )


class SettingsTab:
    def __init__(self, master, container_models: Dict[int, ContainerModel]):
        self.__master = master
        self.__container_models = container_models
        self.__containers_settings: Dict[int, ContainerSettingsFrame] = dict()
        self.__empty_label = None
        self.update_ui()

    def add_container(self, container: ContainerModel):
        assert container.id not in self.__containers_settings
        assert container.id in self.__container_models
        assert container.in_scope
        self.__containers_settings[container.id] = ContainerSettingsFrame(
            self.__master, container
        )

    def delete_container(self, id: int):
        # Warning : This will mark the container for deletion, this should
        # not be called when just being out of scope
        if id in self.__containers_settings:
            self.__containers_settings[id].delete_button_callback()
            del self.__containers_settings[id]

    def update_ui(self):
        for id, container in self.__container_models.items():
            if id not in self.__containers_settings and container.in_scope:
                # Back in scope, let's add it
                self.add_container(container)
            elif id in self.__containers_settings and not container.in_scope:
                # Left the scope, let's remove it
                self.__containers_settings[id].destroy()
                del self.__containers_settings[id]
            elif id in self.__containers_settings and container.in_scope:
                # Still in scope, let's update it
                self.__containers_settings[id].update()

        if len(self.__containers_settings) == 0 and self.__empty_label is None:
            self.__empty_label = tk.Label(
                self.__master, text="No container in scope", font="bold"
            )
            self.__empty_label.pack(anchor=tk.CENTER, expand=True)
        elif len(self.__containers_settings) != 0 and self.__empty_label is not None:
            self.__empty_label.destroy()
            self.__empty_label = None


class AudioViewsTab:
    def __init__(self, master, container_models: Dict[int, ContainerModel]):
        self.__container_models = container_models
        self.__master = master
        # Audio view rendering
        self.__view_frame = tk.Frame(self.__master)
        self.__fig = Figure()
        self.__canvas = FigureCanvasTkAgg(self.__fig, master=self.__view_frame)
        self.__canvas_widget = self.__canvas.get_tk_widget()
        self.__canvas_widget.pack(fill=tk.BOTH, expand=True)
        self.__toolbar = NavigationToolbar2Tk(self.__canvas, self.__view_frame)
        self.__toolbar.update()
        self.__toolbar.pack()
        # Button rendering
        self.__buttons_frame = tk.Frame(self.__master, width=30, relief=tk.SUNKEN)
        self.__buttons_frame.pack_propagate(False)
        self.__containers_actions_buttons_frame = ContainersActionsButtonsFrames(
            self.__buttons_frame, self.__container_models
        )
        # frame packing
        self.__buttons_frame.pack(side=tk.RIGHT, fill="y", pady=(0, 45))
        self.__view_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def __subplots_hratios(self) -> List[int]:
        hratios = []
        for model in self.__container_models.values():
            if not model.in_scope:
                continue
            if model.frozen and not model.is_view_superposable:
                # If the view is not superposable, we need a subplot for both
                # frozen and live signal - we make them thinner
                hratios.extend([1 for _ in range(model.channels * 2)])
            else:
                # If the view is superposable, just a subplot per channel
                hratios.extend([2 for _ in range(model.channels)])

        return hratios

    def update(self):
        self.update_figures()
        self.__containers_actions_buttons_frame.update()

    def update_figures(self):
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
            if not model.in_scope:
                continue
            for channel in range(model.channels):
                title = (
                    f"{model.variable_name} channel {channel}"
                    if not model.mid_side
                    else " {}".format("mid" if channel == 0 else "side")
                )

                if model.frozen and not model.is_view_superposable:
                    title += " (frozen)"
                    axes = subplots_axes[i : i + 2]
                    axes[1].set_title(title)
                    i += 2
                else:
                    axes = subplots_axes[i : i + 1]
                    i += 1
                axes[0].set_title(title)
                model.draw_audio_view(axes, channel)
        roffset = 0.08
        self.__fig.subplots_adjust(
            left=roffset, bottom=roffset, right=1.0 - roffset + 0.01, top=1.0 - roffset
        )
        self.__canvas.draw_idle()


class DaveGUI:

    def __init__(
        self,
        connection : Connection,
    ):

        # Refresh and quit settings
        self.__refresh_time_ms = 20
        self.__conn = connection

        # GUI settings
        self.__models: Dict[int, ContainerModel] = dict()
        self.__window = tk.Tk()
        self.__window.title("Dave")
        self.__window.minsize(400, 600)
        self.__window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.__notebook = ttk.Notebook(self.__window)
        self.__notebook.pack(fill="both", expand=True)
        self.__audio_tabframe = ttk.Frame(self.__notebook)
        self.__notebook.add(self.__audio_tabframe, text="Views")
        self.__settings_tabframe = ttk.Frame(self.__notebook)
        self.__notebook.add(self.__settings_tabframe, text="Settings")
        self.__audio_views_tab = AudioViewsTab(self.__audio_tabframe, self.__models)
        self.__settings_tab = SettingsTab(self.__settings_tabframe, self.__models)
        self.__update_tk_id = ""


    def on_closing(self):
        if self.__update_tk_id:
            self.__window.after_cancel(self.__update_tk_id)
        self.__window.destroy()
        self.__models.clear()

    def run(self):
        self.__update_tk_id = self.__window.after(
            self.__refresh_time_ms, self.tkinter_update_callback
        )
        self.__window.mainloop()
        Logger().get().debug("Tkinter mainloop exiting")

    def __poll_queue(self) -> bool:
        update_needed = False

        while self.__conn.poll():
            try:
                msg = self.__conn.recv()

                if msg == DaveProcess.Message.STOP:
                    self.on_closing()
                    return False
                elif isinstance(msg, DaveProcess.DeleteMessage):
                    Logger().get().debug(f"Received delete message : {msg.id}")
                    self.__models[msg.id].mark_for_deletion()
                elif isinstance(msg, DaveProcess.FreezeMessage):
                    Logger().get().debug(f"Received freeze message : {msg.id}")
                    self.__models[msg.id].frozen = not self.__models[msg.id].frozen
                elif isinstance(msg, DaveProcess.ConcatMessage):
                    Logger().get().debug(f"Received concat message : {msg.id}")
                    self.__models[msg.id].concat = not self.__models[msg.id].concat
                elif isinstance(msg, RawContainer):
                    Logger().get().debug(f"Received new container : {msg.id}")
                    new_model = ContainerModel(msg, 44100)
                    self.__models[msg.id] = new_model
                    self.__settings_tab.add_container(new_model)
                    update_needed = True
                elif isinstance(msg, RawContainer.InScopeUpdate):
                    Logger().get().debug(f"Received data update : {msg.id}")
                    self.__models[msg.id].update_data(msg)
                    update_needed = True
                elif isinstance(msg, RawContainer.OutScopeUpdate):
                    Logger().get().debug(f"Received oos update : {msg.id}")
                    self.__models[msg.id].mark_as_out_of_scope()
                    update_needed = True
            except EOFError:
                Logger().get().debug("Received EOF from debugger process, will shutdown")
                self.on_closing()
                return

        return update_needed

    def __check_model_for_updates(self) -> bool:
        update_needed = False
        to_delete = []

        # We check every container model for update
        for model in self.__models.values():
            if model.check_for_deletion():
                update_needed = True
                to_delete.append(model.id)
            elif model.check_for_update():
                update_needed = True
                model.reset_update_flag()

        # Delete the ones marked for delete
        for id in to_delete:
            del self.__models[id]
            self.__settings_tab.delete_container(id)
            self.__conn.send(DaveProcess.DeleteMessage(id))

        # If no container left we close the gui
        if len(self.__models) == 0 and len(to_delete) != 0:
            Logger().get().debug("No container left, closing the GUI")
            self.on_closing()
            return False

        return update_needed

    def tkinter_update_callback(self):
        self.__update_tk_id = ""

        # Check for new containers or model update
        if self.__poll_queue() or self.__check_model_for_updates():
            self.__audio_views_tab.update()
            self.__settings_tab.update_ui()

        # Queue the next update
        self.__update_tk_id = self.__window.after(
            self.__refresh_time_ms, self.tkinter_update_callback
        )
