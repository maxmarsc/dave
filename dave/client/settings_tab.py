from typing import Callable, Dict, List, Tuple


import tkinter as tk
import customtkinter as ctk

from dave.common.data_layout import DataLayout
from dave.common.logger import Logger
from .container_model import ContainerModel
from .view_setting import FloatSetting, IntSetting, Setting, StringSetting
from .tooltip import Tooltip
from .global_settings import GlobalSettings


# ==============================   SettingsTab  =================================
class SettingsTab:
    """
    The settings tab contains a frame for the general settings, then a frame of
    settings for each container
    """

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
        self.__container_settings_scrollable_frame = ctk.CTkScrollableFrame(
            self.__master,
            corner_radius=0,
            orientation="vertical",
        )
        self.__separator.pack(side=tk.TOP, anchor=tk.N, pady=(3, 5))
        self.__container_settings_scrollable_frame.pack(
            side=tk.TOP, fill=tk.BOTH, expand=True
        )
        self.update_widgets()

    def add_container(self, container: ContainerModel):
        assert container.id not in self.__containers_settings
        assert container.id in self.__container_models
        assert container.in_scope
        self.__containers_settings[container.id] = ContainerSettingsFrame(
            self.__container_settings_scrollable_frame,
            container,
            self.__global_settings,
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


# ========================  ContainerSettingsFrame  =============================
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
        self.__channel_settings.grid(row=1, column=1, sticky="w")

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
        self.__view_menu.grid(row=1, column=2, sticky="w", padx=(5, 5))

        #  View settings
        self.__view_settings_frame = ViewSettingsFrame(
            self.__scrollable_frame, self.__model
        )
        self.__view_settings_frame.grid(row=1, column=3, sticky="w", padx=(5, 0))

        # General section
        self.__general_settings_frame = GeneralSettingsFrame(
            self.__scrollable_frame, self.__model, global_settings
        )
        self.__general_settings_frame.grid(row=1, column=4, sticky="e", padx=(0, 5))

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


# ===========================  ChannelSettingsFrame  ===========================
class ChannelSettingsFrame(ctk.CTkFrame):
    """
    Contains all the channels settings of a container
    """

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
        self.__channel_midside_var = tk.BooleanVar(value=self.__model.mid_side)
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
            Logger().warning(
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


# ===========================  GeneralSettingsFrame  ===========================
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
            Logger().warning(f"{new_val} is not a valid samplerate")
            self.__samplerate_var.set(
                self.__model.samplerate
                if self.__model.samplerate is not None
                else self.__global_settings.samplerate
            )
        # Else the samplerate has been updated in the model


# ===========================  GlobalSettingsFrame  ===========================
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
            Logger().warning(f"{new_val} is not a valid samplerate")
            self.__samplerate_var.set(self.__settings.samplerate)
        else:
            self.__settings.samplerate = int(new_val)
            self.__settings.update_needed = True


# ===========================  ViewSettingsFrame  ===========================
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
