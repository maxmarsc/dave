import customtkinter as ctk
import tkinter as tk

from dave.common.logger import Logger
from dave.client.tooltip import Tooltip
from dave.client.entity.entity_settings_frame import EntitySettingsFrame
from .iir_model import IirModel


class IirSettingsFrame(EntitySettingsFrame):
    """
    Contains all settings specific to an IIR filter
    """

    def __init__(self, master: tk.Misc, model: IirModel):
        super().__init__(master)
        self.__model = model

        # Number of channels
        self.__channel_var = tk.StringVar(value=str(self.__model.channels))
        self.__channel_label = ctk.CTkLabel(self, text=f"channels :", font=self._font)
        self.__channel_entry = ctk.CTkEntry(
            self,
            textvariable=self.__channel_var,
            width=40,
            font=self._font,
            placeholder_text=str(self.__model.channels),
            state="disabled",
        )
        # self.__channel_entry.bind("<Return>", self.channel_var_callback)
        self.__channel_label.pack(side=tk.LEFT, padx=(5, 5))
        self.__channel_entry.pack(side=tk.LEFT, padx=(5, 5))

    def update_widgets(self):
        pass
