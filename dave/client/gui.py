from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow,
    QTabWidget,
    QWidget,
    QVBoxLayout,
    QApplication,
)
from PySide6.QtCore import QTimer, Signal, QObject
from PySide6.QtGui import QIcon, QCloseEvent

from typing import Dict, List
from multiprocessing.connection import Connection
from typing import override

from dave.common.logger import Logger
from dave.common.raw_entity import RawEntity, RawEntityList
from dave.client.entity.model_factory import ModelFactory
from dave.client.global_settings import GlobalSettings
from dave.server.process import DaveProcess
from dave.client.entity.entity_model import EntityModel

from dave.client.views_tab import AudioViewsTab
from dave.client.settings_tab import SettingsTab
from .in_scope_dict import InScopeSet


def load_icon() -> QIcon:
    import dave
    import os

    png_icon = Path(dave.__file__).parent / "assets/dave_logo_v6.png"
    assert os.path.isfile(png_icon)
    icon = QIcon()
    icon.addFile(str(png_icon))
    return icon


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
        self.__first_entity_received = False

        # GUI settings
        self.__models: Dict[int, EntityModel] = dict()
        self.__global_settings = GlobalSettings()
        self.__in_scope_models = InScopeSet()

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
        self.setWindowIcon(load_icon())

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
        self.__audio_views_tab = AudioViewsTab(
            views_tab, self.__models, self.__in_scope_models, self.__global_settings
        )
        self.__settings_tab = SettingsTab(
            settings_tab, self.__models, self.__in_scope_models, self.__global_settings
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
        app.exec()

    def _update_callback(self):
        """Timer callback for updates"""
        # The timer automatically repeats, no need to reschedule
        # Check for new entities or model update
        self._poll_queue()

        if self.__first_entity_received:
            # Check if we should close the window
            self.__check_for_close_condition()

    def _on_deletion_signal(self, model_id: int):
        # Remove from in_scope models first
        if self.__in_scope_models.has(model_id):
            self.__in_scope_models.remove(
                [
                    self.__models[model_id],
                ]
            )

        # Disconnect
        self.__models[model_id].deletion_signal.disconnect(self._on_deletion_signal)

        # Then delete the model object
        del self.__models[model_id]

    def _poll_queue(self):
        """Poll the connection for new messages"""

        while self.__conn.poll():
            try:
                msg = self.__conn.recv()

                if msg == DaveProcess.Message.STOP:
                    self.close()  # This triggers closeEvent
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
                    self.__first_entity_received = True
                    new_in_scope: List[EntityModel] = list()
                    for raw_entity in msg.raw_entities:
                        new_entity = ModelFactory().build(raw_entity)
                        self.__models[raw_entity.id] = new_entity
                        new_entity.deletion_signal.connect(self._on_deletion_signal)
                        if new_entity.in_scope:
                            new_in_scope.append(new_entity)
                    self.__in_scope_models.add(new_in_scope)
                elif isinstance(msg, RawEntity.InScopeUpdate):
                    Logger().debug(f"Received data update : {msg.id}")
                    self.__models[msg.id].update_data(msg)
                    if not self.__in_scope_models.has(msg.id):
                        self.__in_scope_models.add(
                            [
                                self.__models[msg.id],
                            ]
                        )
                elif isinstance(msg, RawEntity.OutScopeUpdate):
                    Logger().debug(f"Received oos update : {msg.id}")
                    self.__models[msg.id].mark_as_out_of_scope()
                    if self.__in_scope_models.has(msg.id):
                        self.__in_scope_models.remove(
                            [
                                self.__models[msg.id],
                            ]
                        )
                else:
                    Logger().warning(f"Received unknown data {type(msg)}:{msg}")
            except EOFError:
                Logger().debug("Received EOF from debugger process, will shutdown")
                self.close()
                return False

    def __check_for_close_condition(self):
        if len(self.__models) == 0:
            Logger().debug("No entity left, closing the GUI")
            self.close()
