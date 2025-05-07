import tkinter as tk
import customtkinter as ctk

from dave.client.entity.entity_side_panel_info import EntitySidePanelInfo
from .iir_model import IirModel


class IirSidePanelInfo(EntitySidePanelInfo):
    """
    Small textbox with some information on the container

    It contains, top to bottom:
    - zeros, poles
    """

    def __init__(self, master: tk.Misc, model: IirModel) -> None:
        super().__init__(master)
        self.__model = model

        z, p = self.__model.zeros_poles
        self.__zp_labels = ctk.CTkLabel(
            self,
            text=f"Zeros: {z} Poles: {p}",
            height=20,
        )
        order = self.__model.order
        self.__order_label = ctk.CTkLabel(
            self,
            text=f"Order: {order}",
            height=20,
        )
        self.__zp_labels.pack(side=tk.TOP, anchor="w")
        self.__order_label.pack(side=tk.TOP, anchor="w")

    def update_widgets(self):
        z, p = self.__model.zeros_poles
        order = self.__model.order
        self.__zp_labels.configure(text=f"Zeros: {z} Poles: {p}")
        self.__order_label.configure(text=f"Order: {order}")
