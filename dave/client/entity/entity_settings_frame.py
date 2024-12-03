from abc import ABC, abstractmethod
import customtkinter as ctk
import tkinter as tk


class EntitySettingsFrame(ctk.CTkFrame, ABC):
    """
    Base class for the subframe of the settings specific to an entity

    The settings (sub)frame is located between the layout selector and the view selector
    It should only be one line of height
    """

    def __init__(self, master: tk.Misc):
        super().__init__(master, fg_color="transparent")
        self._font = ctk.CTkFont(size=15)

    @abstractmethod
    def update_widgets(self):
        pass
