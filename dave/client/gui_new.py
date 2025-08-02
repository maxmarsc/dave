from PySide6.QtWidgets import (
    QMainWindow,
    QTabWidget,
    QWidget,
    QVBoxLayout,
    QApplication,
)
from PySide6.QtCore import QTimer, Signal, QObject
from PySide6.QtGui import QIcon, QCloseEvent

from typing import Dict
from multiprocessing.connection import Connection
from typing import override

from dave.common.logger import Logger
from dave.common.raw_entity import RawEntity, RawEntityList
from dave.client.entity.model_factory import ModelFactory
from dave.client.global_settings import GlobalSettings
from dave.server.process import DaveProcess
from dave.client.entity.entity_model import EntityModel

# from dave.client.views_tab import AudioViewsTab
from dave.client.settings_tab_new import SettingsTab


class DaveGUI(QMainWindow):
    """
    Main GUI class, will create the GUI windows and automatically fetches
    updates from the dave server (debugger)
    """

    def __init__(self, connection: Connection):
        super().__init__()

        # Store connection and settings
        self.__refresh_time_ms = 100
        self.__conn = connection

        # GUI settings
        self.__models: Dict[int, EntityModel] = dict()
        self.__global_settings = GlobalSettings()

        # Setup the main window
        self._setup_window()

        # Setup the timer for polling
        self.__update_timer = QTimer()
        self.__update_timer.timeout.connect(self._update_callback)
        self.__update_timer.setSingleShot(False)  # Repeat automatically

    def _setup_window(self):
        """Setup the main window and widgets"""
        # Window properties
        self.setWindowTitle("Dave")
        self.setMinimumSize(900, 600)

        # Set window icon
        # self.setWindowIcon(QIcon(load_icon()))  # You'll need to adapt load_icon()

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Create tab widget (replaces CTkTabview)
        self.__notebook = QTabWidget()
        layout.addWidget(self.__notebook)

        # Create tab pages
        views_tab = QWidget()
        settings_tab = QWidget()

        self.__notebook.addTab(views_tab, "Views")
        self.__notebook.addTab(settings_tab, "Settings")
        self.__notebook.setCurrentIndex(0)  # Set "Views" as default

        # Create tab content (you'll need to adapt these classes)
        # self.__audio_views_tab = AudioViewsTab(
        #     views_tab, self.__models, self.__global_settings
        # )
        self.__settings_tab = SettingsTab(
            settings_tab, self.__models, self.__global_settings
        )

    @override
    def closeEvent(self, event: QCloseEvent):
        """Handle window close event"""
        Logger().debug("Qt closeEvent called")

        # Stop the timer
        if self.__update_timer.isActive():
            self.__update_timer.stop()

        # Clear data first to prevent updates during destruction
        self.__models.clear()

        # Accept the close event
        event.accept()

        # Quit the application
        QApplication.quit()

    def run(self):
        """Start the GUI (replaces mainloop)"""
        # Start the update timer
        self.__update_timer.start(self.__refresh_time_ms)

        # Show the window
        self.show()

        Logger().debug("Qt GUI started")

    @staticmethod
    def start(connection: Connection):
        app = QApplication([])  # Create QApplication
        gui = DaveGUI(connection)
        gui.run()

        # Start Qt event loop
        app.exec()  # This replaces tkinter's mainloop()

    def _update_callback(self):
        """Timer callback for updates (replaces tkinter_update_callback)"""
        # The timer automatically repeats, no need to reschedule

        # Check for new entities or model update
        if self._poll_queue() or self._check_model_for_updates():
            # pass
            # self.__audio_views_tab.update_widgets()
            self.__settings_tab.update_widgets()

        # Timer will automatically trigger again after refresh_time_ms

    def _poll_queue(self) -> bool:
        """Poll the connection for new messages (unchanged logic)"""
        update_needed = False

        while self.__conn.poll():
            try:
                msg = self.__conn.recv()

                if msg == DaveProcess.Message.STOP:
                    self.close()  # This triggers closeEvent
                    return False
                elif isinstance(msg, DaveProcess.DeleteMessage):
                    Logger().debug(f"Received delete message : {msg.id}")
                    self.__models[msg.id].mark_for_deletion()
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
                        # self.__settings_tab.add_model(new_entity)
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
                self.close()
                return False

        return update_needed

    def _check_model_for_updates(self) -> bool:
        """Check models for updates (unchanged logic)"""
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
            self.close()
            return False

        return update_needed
