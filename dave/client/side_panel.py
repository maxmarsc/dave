from pathlib import Path
from tkinter import filedialog, messagebox
from warnings import catch_warnings

import tkinter as tk
import customtkinter as ctk


from .container.container_model import ContainerModel
from .tooltip import Tooltip


# =========================  SidePanel  ============================
class SidePanel(ctk.CTkFrame):
    """
    Holds some information about the entity, and the action widgets
    (Freeze, Concatenate, Save)
    """

    def __init__(self, master: tk.Misc, model: ContainerModel) -> None:
        # self.__master = master
        super().__init__(
            master,
            fg_color=ctk.ThemeManager.theme["CTkFrame"]["top_fg_color"],
            # fg_color="orange",
            height=200,
        )
        self.__entity = model
        self.__freeze_var = tk.BooleanVar(value=self.__entity.frozen)
        self.__concat_var = tk.BooleanVar(value=self.__entity.concat)
        self.__freeze_var.trace_add("write", self.freeze_button_clicked)
        if self.__entity.compatible_concatenate():
            self.__concat_var.trace_add("write", self.concat_button_clicked)
        self.__font = ctk.CTkFont(size=15)

        # Create name label
        self.__name_label = ctk.CTkLabel(
            self, text=self.__entity.variable_name, font=self.__font
        )

        # Create infos
        self.__infos = model.side_panel_info_class()(self, self.__entity)

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
            state=("normal" if self.__entity.compatible_concatenate() else "disabled"),
        )
        self.__save_button = ctk.CTkButton(
            self,
            text="Save",
            width=120,
            command=self.__save_button_clicked,
            font=self.__font,
        )

        # Create tooltips
        Tooltip(self.__save_button, text="Save to disc")
        # Make available the full name
        Tooltip(self.__name_label, text=self.__entity.variable_name)

        # Packing
        self.__name_label.grid(row=0, column=0, padx=(5, 5), pady=(5, 2))
        self.__infos.grid(row=1, column=0, padx=(5, 5), sticky="W")
        self.__freeze_button.grid(row=2, column=0, padx=(5, 5))
        self.__concat_button.grid(row=3, column=0, padx=(5, 5))
        self.__save_button.grid(row=4, column=0, padx=(5, 5), pady=(5, 5))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=3)
        self.rowconfigure(2, weight=3)
        self.rowconfigure(3, weight=3)
        self.rowconfigure(4, weight=3)

    def update_widgets(self):
        self.__freeze_var.set(self.__entity.frozen)
        self.__concat_var.set(self.__entity.concat)
        self.__infos.update_widgets()

    def freeze_button_clicked(self, *_):
        self.__entity.frozen = self.__freeze_var.get()

    def concat_button_clicked(self, *_):
        self.__entity.concat = self.__concat_var.get()

    def __save_button_clicked(self):
        filetypes = self.__entity.serialize_types()
        filename: str = filedialog.asksaveasfilename(parent=self, filetypes=filetypes)
        if not filename:
            return
        else:
            with catch_warnings(record=True) as w:
                self.__entity.serialize(Path(filename))
            if w:
                messagebox.showwarning(
                    title="Saving to file",
                    message=w[0].message,
                )
