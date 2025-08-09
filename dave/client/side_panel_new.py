from pathlib import Path
from warnings import catch_warnings

from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QCheckBox,
    QPushButton,
    QGridLayout,
    QFileDialog,
    QMessageBox,
    QSizePolicy,
)
from PySide6.QtCore import Signal
from PySide6.QtGui import QFont

from .container.container_model import ContainerModel


# =========================  SidePanel  ============================
class SidePanel(QFrame):
    """
    Holds some information about the entity, and the action widgets
    (Freeze, Concatenate, Save)
    """

    def __init__(self, parent, model: ContainerModel) -> None:
        super().__init__(parent)
        self.__entity = model
        self.__font = QFont()
        # self.__font.setPointSize(15)

        # Set frame properties
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.setFixedWidth(140)

        # Create layout
        layout = QGridLayout(self)

        # Create name label
        self.__name_label = QLabel(self.__entity.variable_name)
        self.__name_label.setFont(self.__font)
        self.__name_label.setToolTip(self.__entity.variable_name)

        # Create infos
        # self.__infos = model.side_panel_info_class()(self, self.__entity)

        # Create freeze checkbox
        self.__freeze_button = QCheckBox("Freeze")
        self.__freeze_button.setFont(self.__font)
        self.__freeze_button.setChecked(self.__entity.frozen)
        self.__freeze_button.toggled.connect(self.__freeze_button_clicked)
        model.frozen_signal.connect(self.__on_frozen_signal)

        # Create concat checkbox
        self.__concat_button = QCheckBox("Concat")
        self.__concat_button.setFont(self.__font)
        self.__concat_button.setEnabled(self.__entity.compatible_concatenate())
        if self.__entity.compatible_concatenate():
            self.__concat_button.setChecked(self.__entity.concat)
            self.__concat_button.toggled.connect(self.__concat_button_clicked)
            model.concat_signal.connect(self.__on_concat_signal)

        # Create save button
        self.__save_button = QPushButton("Save to disc")
        self.__save_button.setFont(self.__font)
        self.__save_button.setFixedWidth(120)
        self.__save_button.clicked.connect(self.__save_button_clicked)
        self.__save_button.setToolTip("Save to disc")

        # Add widgets to layout
        layout.addWidget(self.__name_label, 0, 0)
        # layout.addWidget(self.__infos, 1, 0)
        layout.addWidget(self.__freeze_button, 2, 0)
        layout.addWidget(self.__concat_button, 3, 0)
        layout.addWidget(self.__save_button, 4, 0)

        # Set layout properties
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Set column and row stretch
        layout.setColumnStretch(0, 1)
        layout.setRowStretch(0, 1)
        layout.setRowStretch(1, 3)
        layout.setRowStretch(2, 3)
        layout.setRowStretch(3, 3)
        layout.setRowStretch(4, 3)

    def __freeze_button_clicked(self, checked: bool):
        self.__entity.frozen = checked

    def __concat_button_clicked(self, checked: bool):
        self.__entity.concat = checked

    def __on_frozen_signal(self, frozen: bool):
        self.__freeze_button.setChecked(frozen)

    def __on_concat_signal(self, concat: bool):
        self.__concat_button.setChecked(concat)

    def __save_button_clicked(self):
        filetypes = self.__entity.serialize_types()
        qt_filter = ";;".join([f"{desc} ({pattern})" for desc, pattern in filetypes])

        filename, _ = QFileDialog.getSaveFileName(self, "Save File", "", qt_filter)

        if not filename:
            return

        with catch_warnings(record=True) as w:
            self.__entity.serialize(Path(filename))

        if w:
            QMessageBox.warning(self, "Saving to file", str(w[0].message))
