from dataclasses import dataclass
from enum import Enum
from tkinter import StringVar, ttk, filedialog, messagebox
from typing import Callable, Dict, List, Tuple
from pathlib import Path


import numpy as np
from multiprocessing.connection import Connection
import tkinter as tk
import customtkinter as ctk
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


@dataclass
class GlobalSettings:
    samplerate: int = 44100
    appearance: str = "System"
    update_needed = False

    def validate_samplerate(self, value) -> bool:
        if isinstance(value, str):
            try:
                value = int(value)
            except ValueError:
                return False
        return value > 0


def load_icon() -> tk.PhotoImage:
    import dave

    png_icon = Path(dave.__file__).parent.parent / ".pictures/dave_logo_v6.png"
    return tk.PhotoImage(file=png_icon)


class ContainerSettingsFrame(ctk.CTkFrame):
    """
    Holds all the settings of a container (not the actions buttons)

    This will always contains, left-to-right :
    - Layout selector
    - Channel selector/label
    - View type selector
    - View type settings
    - general settings (samplerate, delete button...)
    """

    def __init__(
        self, master: tk.Misc, model: ContainerModel, global_settings: GlobalSettings
    ) -> None:
        super().__init__(
            master,
            corner_radius=0,
            height=70,
        )
        # Forced to put the scrollable frame into another frame because of a
        # deletion bug https://github.com/TomSchimansky/CustomTkinter/issues/2443
        self.__scrollable_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=ctk.ThemeManager.theme["CTkFrame"]["top_fg_color"],
            height=70,
            orientation="horizontal",
        )
        self.grid_propagate(False)
        self.__model = model
        self.__bold_font = ctk.CTkFont(size=16, weight="bold")
        self.__font = ctk.CTkFont(size=15)
        # container name
        self.__name_label = ctk.CTkLabel(
            self.__scrollable_frame,
            text=f"{self.__model.variable_name} : ",
            font=self.__font,
            width=200,
            height=20,
            anchor="w",
        )
        self.__name_label.grid(row=0, column=0, sticky="w", padx=(5, 5), columnspan=5)

        # Layout selection
        self.__layout_var = tk.StringVar(value=self.__model.selected_layout.value)
        self.__layout_var.trace_add("write", self.layout_var_callback)
        self.__layout_menu = ctk.CTkOptionMenu(
            self.__scrollable_frame,
            values=[layout.value for layout in self.__model.possible_layouts],
            variable=self.__layout_var,
            font=self.__font,
            width=125,
        )
        # self.__layout_menu.configure(fg_color="red")
        Tooltip(self.__layout_menu, text="Select data layout of the container")
        self.__layout_menu.grid(row=1, column=0, sticky="w", padx=(5, 5))

        # Optionnal channel menu
        self.__channel_settings = ChannelSettingsFrame(
            self.__scrollable_frame, self.__model
        )
        # self.__channel_settings.configure(fg_color="yellow")
        self.__channel_settings.grid(row=1, column=1, sticky="w", padx=5)

        # View selection
        self.__view_menu = None
        self.__view_var = tk.StringVar(value=self.__model.selected_view)
        self.__view_var.trace_add("write", self.view_var_callback)
        self.__view_menu = ctk.CTkOptionMenu(
            self.__scrollable_frame,
            values=self.__model.possible_views,
            variable=self.__view_var,
            font=self.__font,
            width=125,
        )
        Tooltip(self.__view_menu, text="Select which view to render")
        # self.__view_menu.configure(fg_color="green")
        self.__view_menu.grid(row=1, column=2, sticky="w", padx=(5, 5))

        #  View settings
        self.__view_settings_frame = ViewSettingsFrame(
            self.__scrollable_frame, self.__model
        )
        # self.__view_settings_frame.configure(fg_color="orange")
        self.__view_settings_frame.grid(row=1, column=3, sticky="w", padx=(5, 5))

        # General section
        self.__general_settings_frame = GeneralSettingsFrame(
            self.__scrollable_frame, self.__model, global_settings
        )
        # self.__general_settings_frame.configure(fg_color="cyan")
        self.__general_settings_frame.grid(row=1, column=4, sticky="e", padx=(5, 5))

        # self.update()
        self.__scrollable_frame.grid_rowconfigure(0, weight=1)
        self.__scrollable_frame.grid_rowconfigure(1, weight=4)
        self.__scrollable_frame.grid_columnconfigure(0, weight=0)
        self.__scrollable_frame.grid_columnconfigure(1, weight=0)
        self.__scrollable_frame.grid_columnconfigure(2, weight=0)
        self.__scrollable_frame.grid_columnconfigure(3, weight=1)
        self.__scrollable_frame.grid_columnconfigure(4, weight=0)
        self.__scrollable_frame.pack(fill=tk.BOTH)
        self.pack(side=tk.TOP, fill=tk.BOTH, padx=2, pady=2)

    def layout_var_callback(self, *_):
        # Update the model
        self.__model.update_layout(DataLayout(self.__layout_var.get()))

        # Trigger a redraw
        self.update_widgets()

    def view_var_callback(self, *_):
        # Update the model
        self.__model.update_view_type(self.__view_var.get())

        # Trigger a redraw
        self.update_widgets()

    def update_widgets(self):
        # Update the layout selection
        self.__layout_menu.configure(
            values=[layout.value for layout in self.__model.possible_layouts]
        )

        # Update the channel menu
        self.__channel_settings.update_widgets()

        # Update the view selection
        if self.__view_var.get() not in self.__model.possible_views:
            self.__view_menu.configure(values=self.__model.possible_views)
            self.__view_var.set(self.__model.selected_view)

        # Update the view settings
        self.__view_settings_frame.update_widgets()


class ChannelSettingsFrame(ctk.CTkFrame):
    def __init__(self, master: tk.Misc, model: ContainerModel):
        super().__init__(master, fg_color="transparent")
        self.__model = model
        self.__font = ctk.CTkFont(size=15)

        # Number of channels
        self.__channel_var = tk.StringVar(value=str(self.__model.channels))
        self.__channel_label = ctk.CTkLabel(self, text=f"channels :", font=self.__font)
        self.__channel_entry = ctk.CTkEntry(
            self,
            textvariable=self.__channel_var,
            width=40,
            placeholder_text=str(self.__model.channels),
            state=("normal" if self.channel_entry_enabled() else "disabled"),
        )
        self.__channel_entry.bind("<Return>", self.channel_var_callback)
        self.__channel_label.pack(side=tk.LEFT, padx=(5, 5))
        self.__channel_entry.pack(side=tk.LEFT, padx=(5, 5))

        # Interleaved switch
        self.__channel_interleaved_var = tk.BooleanVar(value=self.__model.interleaved)
        self.__channel_interleaved_var.trace_add("write", self.interleaved_var_callback)
        self.__channel_interleaved_switch = ctk.CTkSwitch(
            self,
            text="Interleaved",
            font=self.__font,
            variable=self.__channel_interleaved_var,
            onvalue=True,
            offvalue=False,
            state=("normal" if self.interleaved_enabled() else "disabled"),
        )
        self.__channel_interleaved_switch.pack(side=tk.LEFT, padx=(5, 5))

        # Mid/Side switch
        self.__channel_midside_var = tk.BooleanVar(value=self.__model.interleaved)
        self.__channel_midside_var.trace_add("write", self.midside_var_callback)
        self.__channel_mid_side_switch = ctk.CTkSwitch(
            self,
            text="Mid/Side",
            font=self.__font,
            variable=self.__channel_midside_var,
            onvalue=True,
            offvalue=False,
            state="normal" if self.__model.channels == 2 else "disabled",
        )
        self.__channel_mid_side_switch.pack(side=tk.LEFT, padx=(5, 5))

    def interleaved_var_callback(self, *_):
        self.__model.interleaved = self.__channel_interleaved_var.get()

    def midside_var_callback(self, *_):
        self.__model.mid_side = self.__channel_midside_var.get()

    def interleaved_enabled(self) -> bool:
        return not self.__model.is_channel_layout_fixed() and self.__model.channels != 1

    def channel_entry_enabled(self) -> bool:
        return (
            self.__model.is_layout_2D() and not self.__model.is_channel_layout_fixed()
        )

    def channel_var_callback(self, *_):
        new_val = self.__channel_var.get()
        if not self.__model.validate_and_update_channel(new_val):
            Logger().get().warning(
                f"{new_val} is not a valid channel number for this container"
            )
            self.__channel_var.set(str(self.__model.channels))

    def update_widgets(self):
        # Update channel selector
        self.__channel_entry.configure(
            state=("normal" if self.channel_entry_enabled() else "disabled"),
        )

        # Update interleaved switch
        self.__channel_interleaved_switch.configure(
            state=("normal" if self.interleaved_enabled() else "disabled")
        )
        # Update mid/side switch
        self.__channel_mid_side_switch.configure(
            state="normal" if self.__model.channels == 2 else "disabled"
        )


class GeneralSettingsFrame(ctk.CTkFrame):
    def __init__(
        self, master: tk.Misc, model: ContainerModel, global_settings: GlobalSettings
    ):
        super().__init__(master, fg_color="transparent")
        self.__model = model
        self.__global_settings = global_settings
        self.__font = ctk.CTkFont(size=15)

        # Delete button
        self.__delete_button = ctk.CTkButton(
            self, text="X", command=self.delete_button_callback, width=28
        )

        # Samplerate
        self.__samplerate_label = ctk.CTkLabel(
            self, text="samplerate:", font=self.__font
        )
        self.__samplerate_var = tk.StringVar(
            value=(
                self.__model.samplerate
                if self.__model.samplerate is not None
                else self.__global_settings.samplerate
            )
        )
        self.__samplerate_entry = ctk.CTkEntry(
            self,
            textvariable=self.__samplerate_var,
            placeholder_text=f"{self.__global_settings.samplerate}",
            width=80,
            font=self.__font,
        )
        self.__samplerate_entry.bind("<Return>", self.samplerate_var_callback)
        self.__samplerate_label.pack(side=tk.LEFT, padx=3)
        self.__samplerate_entry.pack(side=tk.LEFT, padx=3)

        self.__delete_button.pack(side=tk.RIGHT, anchor=tk.CENTER, padx=3)

    def delete_button_callback(self):
        self.__model.mark_for_deletion()
        self.master.destroy()

    def samplerate_var_callback(self, *_):
        new_val = self.__samplerate_var.get()
        if new_val == "":
            # Field is validated empty, let's use the global setting
            self.__model.samplerate = None
            self.__samplerate_var.set(self.__global_settings.samplerate)
        elif not self.__model.validate_and_update_samplerate(new_val):
            # Value is not valid, let's rollback
            Logger().get().warning(f"{new_val} is not a valid samplerate")
            self.__samplerate_var.set(
                self.__model.samplerate
                if self.__model.samplerate is not None
                else self.__global_settings.samplerate
            )
        # Else the samplerate has been updated in the model


class GlobalSettingsFrame(ctk.CTkFrame):
    def __init__(self, master: tk.Misc, global_settings: GlobalSettings):
        super().__init__(
            master,
            fg_color=ctk.ThemeManager.theme["CTkFrame"]["top_fg_color"],
        )
        self.__settings = global_settings
        self.__font = ctk.CTkFont(size=15)

        # Appearance selector
        self.__appearance_label = ctk.CTkLabel(
            self, text="Appeareance :", font=self.__font
        )
        self.__appearance_var = tk.StringVar(value=self.__settings.appearance)
        self.__appearance_var.trace_add("write", self.appearance_var_callback)
        self.__appearance_menu = ctk.CTkOptionMenu(
            self,
            values=("System", "Dark", "Light"),
            variable=self.__appearance_var,
            font=self.__font,
            width=100,
        )
        self.__appearance_label.pack(side=tk.LEFT, pady=5, padx=5)
        self.__appearance_menu.pack(side=tk.LEFT, pady=5, padx=5)

        # Samplerate entry
        self.__samplerate_label = ctk.CTkLabel(
            self, text="samplerate :", font=self.__font
        )
        self.__samplerate_var = tk.StringVar(value=self.__settings.samplerate)
        self.__samplerate_entry = ctk.CTkEntry(
            self,
            textvariable=self.__samplerate_var,
            placeholder_text="samplerate",
            width=80,
            font=self.__font,
        )
        self.__samplerate_entry.bind("<Return>", self.samplerate_var_callback)
        self.__samplerate_entry.pack(side=tk.RIGHT, pady=5, padx=5)
        self.__samplerate_label.pack(side=tk.RIGHT, pady=5, padx=5)

    def appearance_var_callback(self, *_):
        self.__settings.appearance = self.__appearance_var.get()
        ctk.set_appearance_mode(self.__settings.appearance)

    def samplerate_var_callback(self, *_):
        new_val = self.__samplerate_var.get()
        if not self.__settings.validate_samplerate(new_val):
            Logger().get().warning(f"{new_val} is not a valid samplerate")
            self.__samplerate_var.set(self.__settings.samplerate)
        else:
            self.__settings.samplerate = int(new_val)
            self.__settings.update_needed = True


class ViewSettingsFrame(ctk.CTkFrame):
    """
    A frame containing the selector for every view setting of a model.

    Each type of view has its set of settings. This will create a frame in which
    the user can define the value for each of the settings of the currently
    selected view type
    """

    def __init__(self, master: tk.Misc, container: ContainerModel) -> None:
        super().__init__(master, height=28, fg_color="transparent")
        self.__container = container
        self.__container_suffix = "_" + str(container.id)
        self.__vars: Dict[str, Tuple[tk.Variable, Setting]] = dict()
        self.__widgets: List[tk.Misc] = list()
        self.__font = ctk.CTkFont(size=15)
        self.__width = 0
        self.__crt_view_type = self.__container.selected_view
        self.__create_selectors()

    def __create_selectors(self):
        assert len(self.__widgets) == 0
        self.__width = 0
        for setting in self.__container.view_settings:
            if isinstance(setting, StringSetting):
                self.create_string_selector(setting)
            elif isinstance(setting, IntSetting):
                self.create_int_selector(setting)
            elif isinstance(setting, FloatSetting):
                self.create_float_selector(setting)
            else:
                raise NotImplementedError()
        self.configure(width=self.__width)

    def create_string_selector(self, setting: StringSetting):
        # Create the StringVar to keep updated of changes
        var_name = setting.name + self.__container_suffix
        var = tk.StringVar(value=setting.value, name=var_name)
        self.__vars[var_name] = (var, setting)
        var.trace_add("write", self.update_setting)
        # Create the option menu & the label
        label = ctk.CTkLabel(self, text=setting.name)
        menu = ctk.CTkOptionMenu(
            self,
            values=setting.possible_values(),
            variable=var,
            font=self.__font,
            width=125,
        )
        self.__width += 130
        label.pack(side=tk.LEFT, padx=5)
        menu.pack(side=tk.LEFT)
        self.__widgets.append(label)
        self.__widgets.append(menu)

    def create_float_selector(self, setting: FloatSetting):
        # Create the Var to keep the entry value before validating it
        var_name = setting.name + self.__container_suffix
        var = tk.StringVar(value=str(setting.value), name=var_name)
        self.__vars[var_name] = (var, setting)
        # Create the entry and the label
        label = ctk.CTkLabel(self, text=setting.name, font=self.__font)
        entry = ctk.CTkEntry(
            self,
            textvariable=var,
            width=60,
            placeholder_text=setting.name,
        )
        validate_lambda = lambda event, name=f"{var_name}": self.entry_var_callback(
            name, event
        )
        self.__width += 65
        entry.bind("<Return>", validate_lambda)
        label.pack(side=tk.LEFT, padx=5)
        entry.pack(side=tk.LEFT)
        self.__widgets.append(label)
        self.__widgets.append(entry)

    def create_int_selector(self, setting: IntSetting):
        # Create the Var to keep the entry value before validating it
        var_name = setting.name + self.__container_suffix
        var = tk.StringVar(value=str(setting.value), name=var_name)
        self.__vars[var_name] = (var, setting)
        # Create the entry and the label
        label = ctk.CTkLabel(self, text=setting.name, font=self.__font)
        entry = ctk.CTkEntry(
            self,
            textvariable=var,
            width=60,
            placeholder_text=setting.name,
        )
        validate_lambda = lambda event, name=f"{var_name}": self.entry_var_callback(
            name, event
        )
        self.__width += 65
        entry.bind("<Return>", validate_lambda)
        label.pack(side=tk.LEFT, padx=5)
        entry.pack(side=tk.LEFT)
        self.__widgets.append(label)
        self.__widgets.append(entry)

    def entry_var_callback(self, varname, _):
        var, setting = self.__vars[varname]
        assert isinstance(setting, FloatSetting) or isinstance(setting, IntSetting)
        try:
            if setting.validate(setting.parse_tkvar(var)):
                # New input was validated
                self.update_setting(varname)
            else:
                # bad input, rollback
                self.__vars[varname][0].set(setting.value)
        except tk.TclError:
            # Might fail when tk update the var with an empty string
            pass
        except ValueError:
            # bad input, rollback
            self.__vars[varname][0].set(setting.value)

    def update_setting(self, var_name: str, *_):
        """
        To be called when a variable has been modified, and validated if concerned
        by validation
        """
        assert var_name in self.__vars
        setting_name = var_name[: -len(self.__container_suffix)]
        var, setting = self.__vars[var_name]
        try:
            self.__container.update_view_settings(
                setting_name, setting.parse_tkvar(var)
            )
        except tk.TclError:
            # Might fail when tk update the var with an empty string
            pass

    def update_widgets(self):
        if self.__crt_view_type != self.__container.selected_view:
            # Delete old widgets & vars
            for widget in self.__widgets:
                widget.destroy()
            self.__widgets.clear()
            # Delete the update_setting trace before deleting the var
            for var, _ in self.__vars.values():
                for trace_type, trace_name in var.trace_info():
                    if trace_name.endswith("update_setting"):
                        var.trace_remove(trace_type, trace_name)
            # Delete the vars
            self.__vars.clear()

            # Recreate new widgets
            self.__crt_view_type = self.__container.selected_view
            self.__create_selectors()


class ContainersActionsGridFrame(ctk.CTkFrame):
    """
    Holds the ActionButtonsFrame for every (in scope) container
    """

    def __init__(self, master: tk.Misc, container_models: Dict[int, ContainerModel]):
        super().__init__(master, width=130)
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
            button_frame.grid(row=i, column=0, sticky="ew", padx=(5, 0))

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


class ContainerActionsFrame(ctk.CTkFrame):
    """
    Holds the action buttons (Freeze, Concatenate ...) of a single container
    """

    def __init__(self, master: tk.Misc, container: ContainerModel) -> None:
        # self.__master = master
        super().__init__(master)
        self.__container = container
        self.__freeze_var = tk.BooleanVar(value=self.__container.frozen)
        self.__concat_var = tk.BooleanVar(value=self.__container.concat)
        self.__freeze_var.trace_add("write", self.freeze_button_clicked)
        self.__concat_var.trace_add("write", self.concat_button_clicked)
        self.__font = ctk.CTkFont(size=15)

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
            command=self.__save_button_clicked,
            font=self.__font,
        )

        # Create tooltips

        Tooltip(self.__save_button, text="Save to disc")

        # Packing
        self.__freeze_button.grid(row=0, column=0, padx=(5, 5), pady=(5, 5))
        self.__concat_button.grid(row=1, column=0, padx=(5, 5), pady=(5, 5))
        self.__save_button.grid(row=2, column=0, padx=(5, 5), pady=(5, 5))
        self.columnconfigure(0, weight=1)

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


class SettingsTab:
    def __init__(
        self,
        master,
        container_models: Dict[int, ContainerModel],
        global_settings: GlobalSettings,
    ):
        self.__master = master
        self.__container_models = container_models
        self.__global_settings = global_settings
        self.__containers_settings: Dict[int, ContainerSettingsFrame] = dict()
        self.__empty_label = None
        self.__bold_font = ctk.CTkFont(size=18, weight="bold")
        self.__global_settings_frame = GlobalSettingsFrame(
            self.__master, global_settings
        )
        self.__global_settings_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        self.__separator = ctk.CTkFrame(
            self.__master,
            fg_color=ctk.ThemeManager.theme["CTkFrame"]["top_fg_color"],
            width=100,
            height=6,
            corner_radius=3,
        )
        self.__separator.pack(side=tk.TOP, anchor=tk.N, pady=(3, 5))
        self.update_widgets()

    def add_container(self, container: ContainerModel):
        assert container.id not in self.__containers_settings
        assert container.id in self.__container_models
        assert container.in_scope
        self.__containers_settings[container.id] = ContainerSettingsFrame(
            self.__master, container, self.__global_settings
        )

    def delete_container(self, id: int):
        """
        Calling this will remove the ContainerSettingsFrame from the given container.

        This will never delete the containermodel itself, at is is the responsibility
        of the main GUI handler
        """
        # Warning : This will mark the container for deletion, this should
        # not be called when just being out of scope
        if id in self.__containers_settings:
            self.__containers_settings[id].destroy()
            del self.__containers_settings[id]

    def update_widgets(self):
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
                self.__containers_settings[id].update_widgets()

        if len(self.__containers_settings) == 0 and self.__empty_label is None:
            self.__empty_label = ctk.CTkLabel(
                self.__master, text="No container in scope", font=self.__bold_font
            )
            self.__empty_label.pack(anchor=tk.CENTER, expand=True)
        elif len(self.__containers_settings) != 0 and self.__empty_label is not None:
            self.__empty_label.destroy()
            self.__empty_label = None


class AudioViewsTab:
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
        self.__view_frame = ctk.CTkFrame(self.__master)
        self.__fig = Figure()
        self.__canvas = FigureCanvasTkAgg(self.__fig, master=self.__view_frame)
        self.__canvas_widget = self.__canvas.get_tk_widget()
        self.__canvas_widget.pack(fill=tk.BOTH, expand=True)
        self.__canvas_widget.pack()
        self.__toolbar = NavigationToolbar2Tk(self.__canvas, self.__view_frame)
        self.__toolbar.update()
        self.__toolbar.pack()
        # Button rendering
        self.__containers_actions_buttons_frame = ContainersActionsGridFrame(
            self.__master, self.__container_models
        )
        # frame packing
        self.__containers_actions_buttons_frame.pack(
            side=tk.RIGHT, fill="y", pady=(0, 45)
        )
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
            if not model.in_scope:
                continue
            for channel in range(model.channels):
                title = (
                    f"{model.variable_name} channel {channel}"
                    if not model.mid_side
                    else " {}".format("mid" if channel == 0 else "side")
                )

                if model.frozen and not model.is_view_superposable:
                    axes = subplots_axes[i : i + 2]
                    axes[1].set_title(title + " (frozen)")
                    i += 2
                else:
                    axes = subplots_axes[i : i + 1]
                    i += 1
                axes[0].set_title(title)
                model.draw_audio_view(axes, channel, self.__global_settings.samplerate)
        roffset = 0.08
        self.__fig.subplots_adjust(
            left=roffset, bottom=roffset, right=1.0 - roffset + 0.01, top=1.0 - roffset
        )
        self.__canvas.draw_idle()


class DaveGUI:

    def __init__(
        self,
        connection: Connection,
    ):
        # Refresh and quit settings
        self.__refresh_time_ms = 20
        self.__conn = connection

        # GUI settings
        self.__models: Dict[int, ContainerModel] = dict()
        self.__global_settings = GlobalSettings()

        ctk.set_appearance_mode(self.__global_settings.appearance)
        self.__window = ctk.CTk()
        self.__window.tk.call("wm", "iconphoto", self.__window._w, load_icon())
        self.__window.title("Dave")
        self.__window.minsize(900, 600)
        self.__window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.__notebook = ctk.CTkTabview(self.__window)
        self.__notebook.pack(fill="both", expand=True)
        self.__notebook.add("Views")
        self.__notebook.add("Settings")
        self.__notebook.set("Views")

        self.__audio_views_tab = AudioViewsTab(
            self.__notebook.tab("Views"), self.__models, self.__global_settings
        )
        self.__settings_tab = SettingsTab(
            self.__notebook.tab("Settings"), self.__models, self.__global_settings
        )
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
                    new_model = ContainerModel(msg)
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
                Logger().get().debug(
                    "Received EOF from debugger process, will shutdown"
                )
                self.on_closing()
                return

        return update_needed

    def __check_model_for_updates(self) -> bool:
        update_needed = False
        to_delete = []

        # Check global settings
        if self.__global_settings.update_needed:
            update_needed = True
            self.__global_settings.update_needed = False

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
            self.__audio_views_tab.update_widgets()
            self.__settings_tab.update_widgets()

        # Queue the next update
        self.__update_tk_id = self.__window.after(
            self.__refresh_time_ms, self.tkinter_update_callback
        )
