import customtkinter as ctk
import tkinter as tk

from dave.common.logger import Logger
from dave.client.entity.entity_settings_frame import EntitySettingsFrame
from .container_model import ContainerModel


class ContainerSettingsFrame(EntitySettingsFrame):
    """
    Contains all settings specific to a container
    """

    def __init__(self, master: tk.Misc, model: ContainerModel):
        super().__init__(master)
        self.__model = model

        # Number of channels
        self.__channel_var = tk.StringVar(value=str(self.__model.channels))
        self.__channel_label = ctk.CTkLabel(self, text=f"channels :", font=self._font)
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
            font=self._font,
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
            font=self._font,
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
        return not self.__model.are_dimensions_fixed and self.__model.channels != 1

    def channel_entry_enabled(self) -> bool:
        return not self.__model.are_dimensions_fixed

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
