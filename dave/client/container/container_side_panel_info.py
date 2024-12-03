import tkinter as tk
import customtkinter as ctk

from dave.client.entity.entity_side_panel_info import EntitySidePanelInfo
from .container_model import ContainerModel


class ContainerSidePanelInfo(EntitySidePanelInfo):
    """
    Small textbox with some information on the container

    It contains, top to bottom
    - channels
    - samples
    - amount of inf/NaN
    - concatenate switch
    - freeze switch
    - save button
    """

    def __init__(self, master: tk.Misc, container: ContainerModel) -> None:
        super().__init__(master)
        self.__container = container

        self.__channels_label = ctk.CTkLabel(
            self, text=f"channels: {self.__container.channels}", height=20
        )
        self.__samples_label = ctk.CTkLabel(
            self, text=f"samples: {self.__container.samples}", height=20
        )
        self.__values_label = ctk.CTkLabel(
            self,
            text=f"NaN: {self.__container.nan} Inf: {self.__container.inf}",
            height=20,
        )
        self.__channels_label.pack(side=tk.TOP, anchor="w")
        self.__samples_label.pack(side=tk.TOP, anchor="w")
        self.__values_label.pack(side=tk.TOP, anchor="w")

    def update_widgets(self):
        self.__channels_label.configure(text=f"channels: {self.__container.channels}")
        self.__samples_label.configure(text=f"samples: {self.__container.samples}")
        self.__values_label.configure(
            text=f"NaN: {self.__container.nan} Inf: {self.__container.inf}"
        )
