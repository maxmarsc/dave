from abc import ABC, abstractmethod
import tkinter as tk
import customtkinter as ctk


class EntitySidePanelInfo(ABC, ctk.CTkFrame):
    """
    A small textbox with information on the entity.

    It should not exceed 60 pixels of height
    """

    def __init__(self, master: tk.Misc) -> None:
        super().__init__(
            master,
            fg_color="transparent",
            bg_color="transparent",
        )

    @abstractmethod
    def update_widgets(self):
        pass
