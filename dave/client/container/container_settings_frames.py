from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QLineEdit,
    QCheckBox,
    QWidget,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from typing import TYPE_CHECKING

from dave.client.container.container_model import ContainerModel
from dave.common.logger import Logger


class ContainerSettingsFrame(QFrame):
    """
    Contains all settings specific to a container
    """

    def __init__(self, parent: QWidget, model: ContainerModel):
        super().__init__(parent)

        # Store model reference
        self.__model = model

        # Create font (assuming _font was available in parent)
        self._font = QFont()

        # Set transparent background to match other settings frames
        self.setStyleSheet("ContainerSettingsFrame { background-color: transparent; }")

        self._setup_layout()

    def _setup_layout(self) -> None:
        """Setup horizontal layout and widgets"""
        # Create horizontal layout (replaces pack with side=LEFT)
        layout = QHBoxLayout()
        self.setLayout(layout)

        # Set margins and spacing to match tkinter padding
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        self._create_widgets(layout)

    def _create_widgets(self, layout: QHBoxLayout) -> None:
        """Create all widgets and add to layout"""

        # Layout selection dropdown (replaces CTkOptionMenu)
        self.__layout_menu = QComboBox()
        self.__layout_menu.setFont(self._font)
        self.__layout_menu.setFixedWidth(95)
        layout_values = [layout.value for layout in self.__model.possible_layouts]
        self.__layout_menu.addItems(layout_values)
        self.__layout_menu.setCurrentText(self.__model.selected_layout.value)
        self.__layout_menu.setToolTip("Select data layout of the container")

        # Connect signal (replaces StringVar trace)
        self.__layout_menu.currentTextChanged.connect(self._layout_changed)

        layout.addWidget(self.__layout_menu)

        # Number of channels label and entry
        self.__channel_label = QLabel("channels :")
        self.__channel_label.setFont(self._font)

        self.__channel_entry = QLineEdit()
        self.__channel_entry.setFont(self._font)
        self.__channel_entry.setFixedWidth(40)
        self.__channel_entry.setText(str(self.__model.channels))
        self.__channel_entry.setPlaceholderText(str(self.__model.channels))
        self.__channel_entry.setEnabled(self._channel_entry_enabled())

        # Connect Return key (replaces bind("<Return>"))
        self.__channel_entry.returnPressed.connect(self._channel_changed)
        self.__model.channels_signal.connect(self._on_channels_signal)

        layout.addWidget(self.__channel_label)
        layout.addWidget(self.__channel_entry)

        # Interleaved checkbox (replaces CTkSwitch)
        self.__channel_interleaved_switch = QCheckBox("Interleaved")
        self.__channel_interleaved_switch.setFont(self._font)
        self.__channel_interleaved_switch.setChecked(self.__model.interleaved)
        self.__channel_interleaved_switch.setEnabled(self._interleaved_enabled())

        # Connect signal (replaces BooleanVar trace)
        self.__channel_interleaved_switch.stateChanged.connect(
            self._interleaved_changed
        )

        layout.addWidget(self.__channel_interleaved_switch)

        # Mid/Side checkbox (replaces CTkSwitch)
        self.__channel_mid_side_switch = QCheckBox("Mid/Side")
        self.__channel_mid_side_switch.setFont(self._font)
        self.__channel_mid_side_switch.setChecked(self.__model.mid_side)
        self.__channel_mid_side_switch.setEnabled(self.__model.channels == 2)

        # Connect signal (replaces BooleanVar trace)
        self.__channel_mid_side_switch.stateChanged.connect(self._midside_changed)

        layout.addWidget(self.__channel_mid_side_switch)

    def _layout_changed(self, new_layout: str) -> None:
        """Handle layout dropdown change (replaces layout_var_callback)"""
        # Update the model
        self.__model.update_layout(new_layout)

        # Trigger a redraw
        self.__update_widgets()

    def _interleaved_changed(self, state: int) -> None:
        """Handle interleaved checkbox change (replaces interleaved_var_callback)"""
        self.__model.interleaved = bool(state == Qt.CheckState.Checked.value)

    def _midside_changed(self, state: int) -> None:
        """Handle mid/side checkbox change (replaces midside_var_callback)"""
        self.__model.mid_side = bool(state == Qt.CheckState.Checked.value)

    def _interleaved_enabled(self) -> bool:
        """Check if interleaved switch should be enabled"""
        return not self.__model.are_dimensions_fixed and self.__model.channels != 1

    def _channel_entry_enabled(self) -> bool:
        """Check if channel entry should be enabled"""
        return not self.__model.are_dimensions_fixed

    def _channel_changed(self) -> None:
        """Handle channel entry Return key"""
        new_val = self.__channel_entry.text().strip()

        # Temporarily disconnect signal to avoid recursion
        self.__model.channels_signal.disconnect(self._on_channels_signal)
        if not self.__model.validate_and_update_channel(new_val):
            Logger().warning(
                f"{new_val} is not a valid channel number for this container"
            )
            # Rollback to previous value
            self.__channel_entry.setText(str(self.__model.channels))

        self.__model.channels_signal.connect(self._on_channels_signal)

        # Trigger a redraw
        self.__update_widgets()

    def _on_channels_signal(self, new_value: int):
        """Handle channel change from model side"""
        self.__channel_entry.setText(str(new_value))
        # Trigger a redraw
        self.__update_widgets()

    def __update_widgets(self) -> None:
        """Update widgets when model state changes"""

        # Update channel entry state
        self.__channel_entry.setEnabled(self._channel_entry_enabled())

        # Update interleaved switch state
        self.__channel_interleaved_switch.setEnabled(self._interleaved_enabled())

        # Update mid/side switch state
        self.__channel_mid_side_switch.setEnabled(self.__model.channels == 2)

        # Update checkbox states if model values changed
        self.__channel_interleaved_switch.setChecked(self.__model.interleaved)
        self.__channel_mid_side_switch.setChecked(self.__model.mid_side)
