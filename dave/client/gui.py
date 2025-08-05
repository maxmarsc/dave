from typing import Callable, Dict, List, Tuple
from pathlib import Path
from multiprocessing.connection import Connection
import tkinter as tk
import customtkinter as ctk


from dave.client.entity.model_factory import ModelFactory
from dave.common.logger import Logger

from dave.common.raw_entity import RawEntity, RawEntityList
from dave.server.process import DaveProcess

from dave.client.entity.entity_model import EntityModel

from .global_settings import GlobalSettings
from .settings_tab import SettingsTab
from .views_tab import AudioViewsTab


def load_icon() -> tk.PhotoImage:
    import dave

    png_icon = Path(dave.__file__).parent / "assets/dave_logo_v6.png"
    return tk.PhotoImage(file=png_icon)


class DaveGUI:
    """
    Main GUI class, will create the GUI windows and automatically fetches
    updates from the dave server (debugger)
    """

    def __init__(
        self,
        connection: Connection,
    ):
        # Refresh and quit settings
        self.__refresh_time_ms = 100
        self.__conn = connection

        # GUI settings
        self.__models: Dict[int, EntityModel] = dict()
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
        Logger().debug("Tkinter on_closing called")
        if self.__update_tk_id:
            self.__window.after_cancel(self.__update_tk_id)

        # Clear data first to prevent updates during destruction
        self.__models.clear()

        # Completely quit the application
        self.__window.quit()

    def run(self):
        self.__update_tk_id = self.__window.after(
            self.__refresh_time_ms, self.tkinter_update_callback
        )
        # self.__update_tk_id = self.__window.after(10000, self.on_closing)
        self.__window.mainloop()
        Logger().debug("Tkinter mainloop exiting")

    def __poll_queue(self) -> bool:
        update_needed = False

        while self.__conn.poll():
            try:
                msg = self.__conn.recv()

                if msg == DaveProcess.Message.STOP:
                    self.on_closing()
                    return False
                elif isinstance(msg, DaveProcess.DeleteMessage):
                    Logger().debug(f"Received delete message : {msg.id}")
                    self.__models[msg.id].signal_deletion()
                elif isinstance(msg, DaveProcess.FreezeMessage):
                    Logger().debug(f"Received freeze message : {msg.id}")
                    self.__models[msg.id].frozen = not self.__models[msg.id].frozen
                elif isinstance(msg, DaveProcess.ConcatMessage):
                    Logger().debug(f"Received concat message : {msg.id}")
                    self.__models[msg.id].concat = not self.__models[msg.id].concat
                elif isinstance(msg, RawEntityList):
                    Logger().debug(f"Received new entities")
                    tmp_update_needed = False
                    for raw_entity in msg.raw_entities:
                        tmp_update_needed = tmp_update_needed or raw_entity.in_scope
                        new_entity = ModelFactory().build(raw_entity)
                        self.__models[raw_entity.id] = new_entity
                        if new_entity.in_scope:
                            self.__settings_tab.add_model(new_entity)
                    update_needed = tmp_update_needed
                elif isinstance(msg, RawEntity.InScopeUpdate):
                    Logger().debug(f"Received data update : {msg.id}")
                    self.__models[msg.id].update_data(msg)
                    update_needed = True
                elif isinstance(msg, RawEntity.OutScopeUpdate):
                    Logger().debug(f"Received oos update : {msg.id}")
                    self.__models[msg.id].mark_as_out_of_scope()
                    update_needed = True
                else:
                    Logger().warning(f"Received unknown data {type(msg)}:{msg}")
            except EOFError:
                Logger().debug("Received EOF from debugger process, will shutdown")
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

        # We check every entity model for update
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
            self.__settings_tab.delete_model(id)
            self.__conn.send(DaveProcess.DeleteMessage(id))

        # If no entity left we close the gui
        if len(self.__models) == 0 and len(to_delete) != 0:
            Logger().debug("No entity left, closing the GUI")
            self.on_closing()
            return False

        return update_needed

    def tkinter_update_callback(self):
        self.__update_tk_id = ""

        # Check for new entities or model update
        if self.__poll_queue() or self.__check_model_for_updates():
            self.__audio_views_tab.update_widgets()
            self.__settings_tab.update_widgets()

        # Queue the next update
        self.__update_tk_id = self.__window.after(
            self.__refresh_time_ms, self.tkinter_update_callback
        )
