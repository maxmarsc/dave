from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QLineEdit, QWidget
from PySide6.QtGui import QFont
from typing import TYPE_CHECKING

from dave.client.iir.iir_model import IirModel


class IirSettingsFrame(QFrame):
    """
    Contains all settings specific to an IIR filter
    """

    def __init__(self, parent: QWidget, model: IirModel) -> None:
        super().__init__(parent)

        # Store model reference
        self.__model = model

        # Create font (assuming _font was available in parent)
        self._font = QFont()

        # Set transparent background to match other settings frames
        self.setStyleSheet("IirSettingsFrame { background-color: transparent; }")

        self._setup_layout()

    def _setup_layout(self) -> None:
        """Setup horizontal layout and widgets"""
        # Create horizontal layout (replaces pack with side=LEFT)
        layout = QHBoxLayout()
        self.setLayout(layout)

        # Set margins and spacing to match tkinter padding
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Create channel label
        self.__channel_label = QLabel("channels :")
        self.__channel_label.setFont(self._font)

        # Create channel entry (disabled, display-only)
        self.__channel_entry = QLineEdit()
        self.__channel_entry.setFont(self._font)
        self.__channel_entry.setFixedWidth(40)
        self.__channel_entry.setText(str(self.__model.channels))
        self.__channel_entry.setPlaceholderText(str(self.__model.channels))
        self.__channel_entry.setEnabled(False)  # Always disabled for IIR filters

        # Add widgets to layout
        layout.addWidget(self.__channel_label)
        layout.addWidget(self.__channel_entry)
