from typing import Callable, Dict, List, Tuple


import tkinter as tk
import customtkinter as ctk

from dave.common.logger import Logger

from .entity.entity_view import EntityView

from .entity.entity_model import EntityModel
from .tooltip import Tooltip
from .global_settings import GlobalSettings


# ==============================   SettingsTab  =================================
class SettingsTab:
    """
    The settings tab contains a frame for the general settings, then a frame of
    settings for each entity
    """

    def __init__(
        self,
        master,
        entity_models: Dict[int, EntityModel],
        global_settings: GlobalSettings,
    ):
        self.__master = master
        self.__entity_models = entity_models
        self.__global_settings = global_settings
        self.__entity_settings: Dict[int, EntitySettings] = dict()
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
        self.__settings_scrollable_frame = ctk.CTkScrollableFrame(
            self.__master,
            corner_radius=0,
            orientation="vertical",
        )
        self.__separator.pack(side=tk.TOP, anchor=tk.N, pady=(3, 5))
        self.__settings_scrollable_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.update_widgets()

    def add_model(self, model: EntityModel):
        assert model.id not in self.__entity_settings
        assert model.id in self.__entity_models
        assert model.in_scope
        self.__entity_settings[model.id] = EntitySettings(
            self.__settings_scrollable_frame,
            model,
            self.__global_settings,
        )

    def delete_model(self, id: int):
        """
        Calling this will remove the SettingsFrame from the given entity.

        This will never delete the model itself, at is is the responsibility
        of the main GUI handler
        """
        # Warning : This will mark the container for deletion, this should
        # not be called when just being out of scope
        if id in self.__entity_settings:
            self.__entity_settings[id].destroy()
            del self.__entity_settings[id]

    def update_widgets(self):
        for id, container in self.__entity_models.items():
            if id not in self.__entity_settings and container.in_scope:
                # Back in scope, let's add it
                self.add_model(container)
            elif id in self.__entity_settings and not container.in_scope:
                # Left the scope, let's remove it
                self.__entity_settings[id].destroy()
                del self.__entity_settings[id]
            elif id in self.__entity_settings and container.in_scope:
                # Still in scope, let's update it
                self.__entity_settings[id].update_widgets()

        if len(self.__entity_settings) == 0 and self.__empty_label is None:
            self.__empty_label = ctk.CTkLabel(
                self.__master, text="No container in scope", font=self.__bold_font
            )
            self.__empty_label.pack(anchor=tk.CENTER, expand=True)
        elif len(self.__entity_settings) != 0 and self.__empty_label is not None:
            self.__empty_label.destroy()
            self.__empty_label = None


# ========================  ContainerSettingsFrame  =============================
class EntitySettings(ctk.CTkFrame):
    """
    Holds all the settings of an entity

    This will always contains, left-to-right :
    - Entity-specific settings
    - View type selector
    - View type settings
    - general settings (samplerate, delete button...)
    """

    def __init__(
        self, master: tk.Misc, model: EntityModel, global_settings: GlobalSettings
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

        # Entity-specific settings frame
        self.__entity_settings_frame = self.__model.settings_frame_class()(
            self.__scrollable_frame, self.__model
        )
        self.__entity_settings_frame.grid(row=1, column=0, sticky="w")

        # View selection
        self.__view_menu = None
        self.__view_var = tk.StringVar(value=self.__model.selected_view)
        self.__view_var.trace_add("write", self.view_var_callback)
        self.__view_menu = ctk.CTkOptionMenu(
            self.__scrollable_frame,
            values=self.__model.possible_views_names,
            variable=self.__view_var,
            font=self.__font,
            width=125,
        )
        Tooltip(self.__view_menu, text="Select which view to render")
        self.__view_menu.grid(row=1, column=1, sticky="w", padx=(5, 5))

        #  View settings
        self.__view_settings_frame = ViewSettingsFrame(
            self.__scrollable_frame, self.__model
        )
        self.__view_settings_frame.grid(row=1, column=2, sticky="w", padx=(5, 0))

        # General section
        self.__general_settings_frame = GeneralSettingsFrame(
            self.__scrollable_frame, self.__model, global_settings
        )
        self.__general_settings_frame.grid(row=1, column=3, sticky="e", padx=(0, 5))

        self.__scrollable_frame.grid_rowconfigure(0, weight=1)
        self.__scrollable_frame.grid_rowconfigure(1, weight=4)
        self.__scrollable_frame.grid_columnconfigure(0, weight=0)
        self.__scrollable_frame.grid_columnconfigure(1, weight=0)
        self.__scrollable_frame.grid_columnconfigure(2, weight=1)
        self.__scrollable_frame.grid_columnconfigure(3, weight=0)
        # self.__scrollable_frame.grid_columnconfigure(4, weight=0)
        self.__scrollable_frame.pack(fill=tk.BOTH)
        self.pack(side=tk.TOP, fill=tk.BOTH, padx=2, pady=2)

    def view_var_callback(self, *_):
        # Update the model
        self.__model.update_view_type(self.__view_var.get())

        # Trigger a redraw
        self.update_widgets()

    def update_widgets(self):
        # Update the channel menu
        self.__entity_settings_frame.update_widgets()

        # Update the view selection
        if self.__view_var.get() not in self.__model.possible_views_names:
            self.__view_menu.configure(values=self.__model.possible_views_names)
            self.__view_var.set(self.__model.selected_view)

        # Update the view settings
        self.__view_settings_frame.update_widgets()


# ===========================  GeneralSettingsFrame  ===========================
class GeneralSettingsFrame(ctk.CTkFrame):
    def __init__(
        self, master: tk.Misc, model: EntityModel, global_settings: GlobalSettings
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

    def __init__(self, master: tk.Misc, model: EntityModel) -> None:
        super().__init__(master, height=28, fg_color="transparent")
        self.__model = model
        self.__entity_suffix = "_" + str(model.id)
        self.__vars: Dict[str, Tuple[tk.Variable, EntityView.Setting]] = dict()
        self.__widgets: List[tk.Misc] = list()
        self.__font = ctk.CTkFont(size=15)
        self.__width = 0
        self.__crt_view_type = self.__model.selected_view
        self.__create_selectors()

    def __create_selectors(self):
        assert len(self.__widgets) == 0
        self.__width = 0
        for setting in self.__model.view_settings:
            if isinstance(setting, EntityView.StringSetting):
                self.create_string_selector(setting)
            elif isinstance(setting, EntityView.IntSetting):
                self.create_int_selector(setting)
            elif isinstance(setting, EntityView.FloatSetting):
                self.create_float_selector(setting)
            else:
                raise NotImplementedError()
        self.configure(width=self.__width)

    def create_string_selector(self, setting: EntityView.StringSetting):
        # Create the StringVar to keep updated of changes
        var_name = setting.name + self.__entity_suffix
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

    def create_float_selector(self, setting: EntityView.FloatSetting):
        # Create the Var to keep the entry value before validating it
        var_name = setting.name + self.__entity_suffix
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

    def create_int_selector(self, setting: EntityView.IntSetting):
        # Create the Var to keep the entry value before validating it
        var_name = setting.name + self.__entity_suffix
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
        assert isinstance(setting, EntityView.FloatSetting) or isinstance(
            setting, EntityView.IntSetting
        )
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
        setting_name = var_name[: -len(self.__entity_suffix)]
        var, setting = self.__vars[var_name]
        try:
            self.__model.update_view_settings(setting_name, setting.parse_tkvar(var))
        except tk.TclError:
            # Might fail when tk update the var with an empty string
            pass

    def update_widgets(self):
        if self.__crt_view_type != self.__model.selected_view:
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
            self.__crt_view_type = self.__model.selected_view
            self.__create_selectors()
