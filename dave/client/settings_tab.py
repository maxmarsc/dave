from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QScrollArea,
    QFrame,
    QGridLayout,
    QLabel,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QScrollBar,
    QSizePolicy,
)
from PySide6.QtCore import Qt, QObject, QEvent
from PySide6.QtGui import QFont
from typing import Dict, List, Tuple, Union, override

from dave.common.logger import Logger

from dave.client.entity.entity_model import EntityModel
from dave.client.global_settings import GlobalSettings

from .entity.entity_view import EntityView
from .in_scope_dict import InScopeSet


# ==============================   SettingsTab  =================================
class SettingsTab:
    """
    The settings tab contains a frame for the general settings, then a frame of
    settings for each entity
    """

    def __init__(
        self,
        parent: QWidget,
        entity_models: Dict[int, EntityModel],
        in_scope_models: InScopeSet,
        global_settings: GlobalSettings,
    ):
        self.__parent = parent
        self.__entity_models = entity_models
        self.__global_settings = global_settings
        self.__entity_settings: Dict[int, EntitySettings] = dict()
        self.__empty_label = None

        # Create font
        self.__bold_font = QFont()

        in_scope_models.scope_signal.connect(self._on_scope_signal)

        self._setup_layout()

    def _setup_layout(self):
        """Setup the main layout and widgets"""
        # Create main layout for the parent widget
        main_layout = QVBoxLayout()
        self.__parent.setLayout(main_layout)

        # Create global settings frame
        self.__global_settings_frame = GlobalSettingsFrame(
            self.__parent, self.__global_settings
        )
        main_layout.addWidget(self.__global_settings_frame)

        # Create separator
        self.__separator = QFrame()
        self.__separator.setFrameShape(QFrame.Shape.HLine)
        self.__separator.setFrameShadow(QFrame.Shadow.Sunken)
        self.__separator.setFixedHeight(6)

        main_layout.addWidget(self.__separator)

        # Create scrollable area
        self.__scroll_area = QScrollArea()
        self.__scroll_area.setWidgetResizable(True)
        self.__scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.__scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        # Create content widget for the scroll area
        self.__scroll_content = QWidget()
        self.__scroll_layout = QVBoxLayout()
        self.__scroll_layout.setDirection(QVBoxLayout.Direction.TopToBottom)
        self.__scroll_content.setLayout(self.__scroll_layout)

        # Make transparent
        self.__scroll_area.setStyleSheet(
            """
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            """
        )

        self.__scroll_content.setStyleSheet(
            """
            QWidget#settings_scroll_content {
                background-color: transparent;
            }
            """
        )
        self.__scroll_content.setObjectName("settings_scroll_content")

        # Force top alignment:
        self.__scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Set the content widget in the scroll area
        self.__scroll_area.setWidget(self.__scroll_content)

        # Add scroll area to main layout with stretch
        main_layout.addWidget(self.__scroll_area, 1)  # stretch factor 1

    def _on_scope_signal(self, ids: List[int], in_scope: bool):
        if in_scope:
            self.__add_models(ids)
        else:
            self.__remove_models(ids)

    def __add_models(self, ids: List[int]):
        assert len(ids) > 0

        if self.__empty_label is None:
            if self.__scroll_layout.count() != 0:
                # Delete the old stretch
                self.__scroll_layout.removeItem(
                    self.__scroll_layout.itemAt(self.__scroll_layout.count() - 1)
                )
        else:
            # Delete the label if any
            self.__scroll_layout.removeWidget(self.__empty_label)
            self.__empty_label.deleteLater()
            self.__empty_label = None

        for id in ids:
            # Get the model
            new_model = self.__entity_models[id]
            assert new_model.in_scope

            # Create entity settings widget
            entity_settings = EntitySettings(
                self.__scroll_content,
                new_model,
                self.__global_settings,
            )
            self.__entity_settings[id] = entity_settings

            # Add to layout
            self.__scroll_layout.addWidget(entity_settings)

        # Use stretching to anchor everything at the top
        self.__scroll_layout.addStretch(1)

    def __remove_models(self, ids: List[int]):
        assert len(ids) > 0
        assert self.__empty_label is None

        # Delete the old stretch
        self.__scroll_layout.removeItem(
            self.__scroll_layout.itemAt(self.__scroll_layout.count() - 1)
        )

        for id in ids:
            assert id in self.__entity_settings
            # Get the EntitySettings
            settings = self.__entity_settings[id]

            # Remove from layout
            self.__scroll_layout.removeWidget(settings)

            # Delete the widget
            settings.deleteLater()

            # Remove from our tracking dict
            del self.__entity_settings[id]

        # Handle empty state label
        if len(self.__entity_settings) == 0:
            self.__empty_label = QLabel("No entity in scope")
            self.__empty_label.setFont(self.__bold_font)
            self.__empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # Add to scroll layout
            self.__scroll_layout.addWidget(self.__empty_label)
        else:
            # Add stretching back
            self.__scroll_layout.addStretch(1)


# ============================  EntitySettings  =================================
class EntitySettings(QFrame):
    """
    Holds all the settings of an entity

    This will always contains, left-to-right :
    - Entity-specific settings
    - View type selector
    - View type settings
    - general settings (samplerate, delete button...)
    """

    def __init__(
        self, parent: QWidget, model: EntityModel, global_settings: GlobalSettings
    ) -> None:
        super().__init__(parent)

        # Store references
        self.__model = model
        self.__global_settings = global_settings

        # Create fonts
        self.__bold_font = QFont()
        # self.__bold_font.setPointSize(16)
        # self.__bold_font.setBold(True)

        self.__font = QFont()
        # self.__font.setPointSize(15)

        # Set fixed height
        self.setFixedHeight(70)
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)

        self._setup_layout()

    def _setup_layout(self):
        """Setup the scrollable layout and widgets"""
        # Create main layout for this frame
        main_layout = QGridLayout()
        self.setLayout(main_layout)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Create horizontal scroll area
        self.__scroll_area = QScrollArea()
        self.__scroll_area.setWidgetResizable(True)
        self.__scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.__scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.__scroll_area.horizontalScrollBar().installEventFilter(self)

        # Create content widget for scroll area
        self.__scroll_content = QWidget()
        self.__scroll_layout = QGridLayout()
        self.__scroll_content.setLayout(self.__scroll_layout)
        self.__scroll_content.setSizePolicy(
            QSizePolicy.Policy.Expanding,  # Allow horizontal expansion
            QSizePolicy.Policy.Fixed,  # Keep vertical size fixed
        )

        # Set content in scroll area
        self.__scroll_area.setWidget(self.__scroll_content)
        main_layout.addWidget(self.__scroll_area)

        self._create_widgets()
        self._setup_grid_layout()

    def _create_widgets(self):
        """Create all child widgets"""
        # Entity name label
        self.__name_label = QLabel(f"{self.__model.variable_name} : ")
        self.__name_label.setFont(self.__font)
        self.__name_label.setFixedWidth(200)
        self.__name_label.setFixedHeight(20)
        self.__name_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )

        # Entity-specific settings frame
        settings_frame_class = self.__model.settings_frame_class()
        self.__entity_settings_frame = settings_frame_class(
            self.__scroll_content, self.__model
        )

        # View selection dropdown
        self.__view_menu = QComboBox()
        self.__view_menu.setFont(self.__font)
        self.__view_menu.setFixedWidth(95)
        self.__view_menu.addItems(self.__model.possible_views_names)
        self.__view_menu.setCurrentText(self.__model.selected_view)

        # Connect signal
        self.__view_menu.currentTextChanged.connect(self._on_view_change)
        self.__model.possible_views_signal.connect(self._on_possible_views_signal)

        # Add tooltip
        self.__view_menu.setToolTip("Select which view to render")

        # View settings frame
        self.__view_settings_frame = ViewSettingsFrame(
            self.__scroll_content, self.__model
        )

        # General settings frame
        self.__general_settings_frame = GeneralSettingsFrame(
            self.__scroll_content, self.__model, self.__global_settings
        )

    def _setup_grid_layout(self):
        """Setup the grid layout"""
        # Add widgets to grid layout
        # Row 0: Entity name (spans 5 columns)
        self.__scroll_layout.addWidget(self.__name_label, 0, 0, 1, 5)

        # Row 1: All settings components
        self.__scroll_layout.addWidget(self.__entity_settings_frame, 1, 0)
        self.__scroll_layout.addWidget(self.__view_menu, 1, 1)
        self.__scroll_layout.addWidget(self.__view_settings_frame, 1, 2)
        self.__scroll_layout.addWidget(self.__general_settings_frame, 1, 3)

        # Configure row/column stretching
        self.__scroll_layout.setRowStretch(0, 1)  # weight=1
        self.__scroll_layout.setRowStretch(1, 4)  # weight=4

        self.__scroll_layout.setColumnStretch(0, 0)  # weight=0 (fixed size)
        self.__scroll_layout.setColumnStretch(1, 0)  # weight=0 (fixed size)
        self.__scroll_layout.setColumnStretch(2, 1)  # weight=1 (expandable)
        self.__scroll_layout.setColumnStretch(3, 0)  # weight=0 (fixed size)

        # Set margins and spacing
        self.__scroll_layout.setContentsMargins(5, 5, 5, 5)
        self.__scroll_layout.setHorizontalSpacing(5)
        self.__scroll_layout.setVerticalSpacing(5)

    @override
    def eventFilter(self, object: QObject, event: QEvent):
        """Monitor horizontal scrollbar show/hide events"""
        if object == self.__scroll_area.horizontalScrollBar():
            if event.type() == QEvent.Type.Show:
                # Scrollbar appeared
                scrollbar_height = self.__scroll_area.horizontalScrollBar().height()
                self.setFixedHeight(70 + scrollbar_height)
                return False
            elif event.type() == QEvent.Type.Hide:
                # Scrollbar disappeared
                self.setFixedHeight(70)
                return False

        return super().eventFilter(object, event)

    def _on_view_change(self, new_view: str):
        """Handle view selection change"""
        # Update the model
        self.__model.update_view_type(new_view)

    def _on_possible_views_signal(self):
        # Temporarily disconnect signal to avoid recursion
        self.__view_menu.currentTextChanged.disconnect()

        possibles_views = self.__model.possible_views_names

        # Update dropdown items
        self.__view_menu.clear()
        self.__view_menu.addItems(possibles_views)
        self.__view_menu.setCurrentText(self.__model.selected_view)

        # Reconnect signal
        self.__view_menu.currentTextChanged.connect(self._on_view_change)


# ===========================  GeneralSettingsFrame  ===========================
class GeneralSettingsFrame(QFrame):
    """
    Frame containing general settings like sample rate and delete button
    """

    def __init__(self, parent, model: EntityModel, global_settings: GlobalSettings):
        super().__init__(parent)

        # Store references
        self.__model = model
        self.__global_settings = global_settings

        # Create font
        self.__font = QFont()
        # self.__font.setPointSize(15)

        self._setup_layout()

    def _setup_layout(self):
        """Setup horizontal layout and widgets"""
        # Create horizontal layout
        layout = QHBoxLayout()
        self.setLayout(layout)

        # Set margins
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(3)

        # Create samplerate label
        self.__samplerate_label = QLabel("samplerate:")
        self.__samplerate_label.setFont(self.__font)

        # Create samplerate entry field
        self.__samplerate_entry = QLineEdit()
        self.__samplerate_entry.setFont(self.__font)
        self.__samplerate_entry.setFixedWidth(80)

        # Set initial value and placeholder
        initial_value = (
            str(self.__model.samplerate)
            if self.__model.samplerate is not None
            else str(self.__global_settings.samplerate)
        )
        self.__samplerate_entry.setText(initial_value)
        self.__samplerate_entry.setPlaceholderText(
            str(self.__global_settings.samplerate)
        )

        # Connect Return key to callback
        self.__samplerate_entry.returnPressed.connect(self._samplerate_changed)

        # Create delete button
        self.__delete_button = QPushButton("X")
        self.__delete_button.setFixedWidth(28)

        # Connect button click (replaces command parameter)
        self.__delete_button.clicked.connect(self._delete_button_clicked)

        # Add widgets to layout (left to right)
        layout.addWidget(self.__samplerate_label)  # side=LEFT
        layout.addWidget(self.__samplerate_entry)  # side=LEFT
        layout.addStretch()  # Push delete button to the right
        layout.addWidget(self.__delete_button)  # side=RIGHT

    def _delete_button_clicked(self):
        """Handle delete button click (replaces delete_button_callback)"""
        self.__model.signal_deletion()

    def _samplerate_changed(self):
        """Handle samplerate entry Return key (replaces samplerate_var_callback)"""
        new_val = self.__samplerate_entry.text().strip()

        if new_val == "":
            # Field is empty, use the global setting
            self.__model.samplerate = None
            self.__samplerate_entry.setText(str(self.__global_settings.samplerate))
        elif not self.__model.validate_and_update_samplerate(new_val):
            # Value is not valid, rollback
            Logger().warning(f"{new_val} is not a valid samplerate")
            rollback_value = (
                str(self.__model.samplerate)
                if self.__model.samplerate is not None
                else str(self.__global_settings.samplerate)
            )
            self.__samplerate_entry.setText(rollback_value)
        # Else the samplerate has been updated in the model


# ===========================  GlobalSettingsFrame  ===========================
class GlobalSettingsFrame(QFrame):
    """
    Frame containing global application settings like appearance and default samplerate
    """

    def __init__(self, parent: QWidget, global_settings: GlobalSettings):
        super().__init__(parent)

        # Store reference
        self.__settings = global_settings

        # Create font
        self.__font = QFont()
        # self.__font.setPointSize(15)

        self._setup_layout()

    def _setup_layout(self):
        """Setup horizontal layout with samplerate controls"""
        # Create horizontal layout
        layout = QHBoxLayout()
        self.setLayout(layout)

        # Set margins and spacing
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Add stretch to push samplerate controls to the right
        layout.addStretch()

        # Samplerate controls
        self._create_samplerate_controls(layout)

    def _create_samplerate_controls(self, layout: QHBoxLayout):
        """Create samplerate label and entry"""
        # Samplerate label
        self.__samplerate_label = QLabel("samplerate :")
        self.__samplerate_label.setFont(self.__font)

        # Samplerate entry
        self.__samplerate_entry = QLineEdit()
        self.__samplerate_entry.setFont(self.__font)
        self.__samplerate_entry.setFixedWidth(80)
        self.__samplerate_entry.setText(str(self.__settings.samplerate))
        self.__samplerate_entry.setPlaceholderText("samplerate")

        # Connect Return key
        self.__samplerate_entry.returnPressed.connect(self._samplerate_changed)

        # Add to layout
        layout.addWidget(self.__samplerate_label)
        layout.addWidget(self.__samplerate_entry)

    def _samplerate_changed(self):
        """Handle samplerate entry Return key"""
        new_val = self.__samplerate_entry.text().strip()

        if not self.__settings.validate_samplerate(new_val):
            Logger().warning(f"{new_val} is not a valid samplerate")
            # Rollback to previous value
            self.__samplerate_entry.setText(str(self.__settings.samplerate))
        else:
            # Update the setting
            self.__settings.samplerate = int(new_val)


# ===========================  ViewSettingsFrame  ===========================
class ViewSettingsFrame(QFrame):
    """
    A frame containing the selector for every view setting of a model.

    Each type of view has its set of settings. This will create a frame in which
    the user can define the value for each of the settings of the currently
    selected view type
    """

    def __init__(self, parent: QWidget, model: "EntityModel") -> None:
        super().__init__(parent)

        self.__model = model
        self.__entity_suffix = "_" + str(model.id)

        # Store widget references and their associated settings
        self.__setting_widgets: Dict[
            str, Tuple[Union[QComboBox, QLineEdit], EntityView.Setting]
        ] = dict()
        self.__widgets: List[QWidget] = list()

        # Create font
        self.__font = QFont()
        # self.__font.setPointSize(15)

        # Track current view type for updates
        self.__current_view_type = self.__model.selected_view

        self.setFixedHeight(28)

        # Create layout
        self.__layout = QHBoxLayout()
        self.setLayout(self.__layout)
        self.__layout.setContentsMargins(0, 0, 0, 0)
        self.__layout.setSpacing(5)
        self.__layout.setSizeConstraint(QHBoxLayout.SizeConstraint.SetMinimumSize)

        self._create_selectors()
        self.__model.view_signal.connect(self._on_view_signal)

    def _create_selectors(self) -> None:
        """Create selector widgets for current view settings"""
        assert len(self.__widgets) == 0

        total_width = 0
        for setting in self.__model.view_settings:
            match type(setting):
                case EntityView.StringSetting:
                    total_width += self._create_string_selector(setting)
                case EntityView.IntSetting:
                    total_width += self._create_int_selector(setting)
                case EntityView.FloatSetting:
                    total_width += self._create_float_selector(setting)
                case _:
                    raise NotImplementedError(f"Unknown setting type: {type(setting)}")

        # Set minimum width based on content
        self.setMinimumWidth(total_width)
        self.__layout.addStretch(1)

    def _create_string_selector(self, setting: "EntityView.StringSetting") -> int:
        """Create label and dropdown for string setting"""
        var_name = setting.name + self.__entity_suffix

        # Create label
        label = QLabel(setting.name)
        label.setFont(self.__font)

        # Create dropdown
        menu = QComboBox()
        menu.setFont(self.__font)
        menu.setFixedWidth(95)
        menu.addItems(setting.possible_values())
        menu.setCurrentText(str(setting.value))

        # Connect signal (replaces StringVar trace)
        menu.currentTextChanged.connect(
            lambda value, name=var_name: self._update_setting(name, value)
        )

        # Store references
        self.__setting_widgets[var_name] = (menu, setting)
        self.__widgets.extend([label, menu])

        # Add to layout
        self.__layout.addWidget(label)
        self.__layout.addWidget(menu)

        return 100  # Width used

    def _create_float_selector(self, setting: "EntityView.FloatSetting") -> int:
        """Create label and entry for float setting"""
        var_name = setting.name + self.__entity_suffix

        # Create label
        label = QLabel(setting.name)
        label.setFont(self.__font)

        # Create entry
        entry = QLineEdit()
        entry.setFont(self.__font)
        entry.setFixedWidth(60)
        entry.setText(str(setting.value))
        entry.setPlaceholderText(setting.name)

        # Connect return key for validation (replaces bind("<Return>"))
        entry.returnPressed.connect(
            lambda name=var_name: self._entry_validation_callback(name)
        )

        # Store references
        self.__setting_widgets[var_name] = (entry, setting)
        self.__widgets.extend([label, entry])

        # Add to layout
        self.__layout.addWidget(label)
        self.__layout.addWidget(entry)

        return 65  # Width used

    def _create_int_selector(self, setting: "EntityView.IntSetting") -> int:
        """Create label and entry for int setting"""
        var_name = setting.name + self.__entity_suffix

        # Create label
        label = QLabel(setting.name)
        label.setFont(self.__font)

        # Create entry
        entry = QLineEdit()
        entry.setFont(self.__font)
        entry.setFixedWidth(60)
        entry.setText(str(setting.value))
        entry.setPlaceholderText(setting.name)

        # Connect return key for validation (replaces bind("<Return>"))
        entry.returnPressed.connect(
            lambda name=var_name: self._entry_validation_callback(name)
        )

        # Store references
        self.__setting_widgets[var_name] = (entry, setting)
        self.__widgets.extend([label, entry])

        # Add to layout
        self.__layout.addWidget(label)
        self.__layout.addWidget(entry)

        return 65  # Width used

    def _entry_validation_callback(self, var_name: str) -> None:
        """Handle entry validation for int/float settings (replaces entry_var_callback)"""
        if var_name not in self.__setting_widgets:
            return

        widget, setting = self.__setting_widgets[var_name]
        assert isinstance(widget, QLineEdit)
        assert isinstance(setting, (EntityView.FloatSetting, EntityView.IntSetting))

        current_text = widget.text().strip()

        try:
            # Parse the value (equivalent to setting.parse_tkvar(var))
            if isinstance(setting, EntityView.IntSetting):
                parsed_value = int(current_text) if current_text else None
            elif isinstance(setting, EntityView.FloatSetting):
                parsed_value = float(current_text) if current_text else None
            else:
                parsed_value = current_text

            if parsed_value is not None and setting.validate(parsed_value):
                # New input was validated
                self._update_setting(var_name, current_text)
            else:
                # Bad input, rollback
                widget.setText(str(setting.value))
        except ValueError:
            # Bad input (equivalent to TclError + ValueError), rollback
            widget.setText(str(setting.value))

    def _update_setting(self, var_name: str, value: str) -> None:
        """
        Update model setting when widget value changes
        (replaces update_setting)
        """
        if var_name not in self.__setting_widgets:
            return

        setting_name = var_name[: -len(self.__entity_suffix)]
        widget, setting = self.__setting_widgets[var_name]

        try:
            if isinstance(widget, QComboBox):
                # String setting
                self.__model.update_view_settings(setting_name, value)
            elif isinstance(widget, QLineEdit):
                # Int/Float setting
                if isinstance(setting, EntityView.IntSetting):
                    parsed_value = int(value) if value.strip() else None
                elif isinstance(setting, EntityView.FloatSetting):
                    parsed_value = float(value) if value.strip() else None
                else:
                    parsed_value = value

                if parsed_value is not None:
                    self.__model.update_view_settings(setting_name, parsed_value)
        except ValueError:
            # Parse error, ignore
            pass

    def _on_view_signal(self, view_name: str):
        if self.__current_view_type != view_name:
            # Clear old widgets and connections
            self._clear_widgets()

            # Recreate widgets for new view type
            self.__current_view_type = view_name
            self._create_selectors()

    def _clear_widgets(self) -> None:
        """Clear all widgets and disconnect signals"""
        # Disconnect all signals to prevent callbacks during destruction
        for var_name, (widget, setting) in self.__setting_widgets.items():
            if isinstance(widget, QComboBox):
                widget.currentTextChanged.disconnect()
            elif isinstance(widget, QLineEdit):
                widget.returnPressed.disconnect()

        # Remove widgets from layout and schedule deletion
        for widget in self.__widgets:
            self.__layout.removeWidget(widget)
            widget.deleteLater()

        # Remove stretch
        self.__layout.removeItem(self.__layout.itemAt(0))

        # Clear tracking dictionaries
        self.__widgets.clear()
        self.__setting_widgets.clear()
