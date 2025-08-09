from PySide6.QtWidgets import (
    QLabel,
    QVBoxLayout,
)

from .container_model import ContainerModel

from dave.client.entity.entity_side_panel_info import EntitySidePanelInfo


class ContainerSidePanelInfo(EntitySidePanelInfo):
    """
    Small textbox with some information on the container

    It contains, top to bottom
    - channels
    - samples
    - amount of inf/NaN
    """

    def __init__(self, parent, container: ContainerModel):
        super().__init__(parent)
        self.__container = container

        self.__setup_layout()

    def __setup_layout(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Create channel label
        self.__channels_label = QLabel(f"channels: {self.__container.channels}")

        # Create sample label
        self.__sample_label = QLabel(f"samples: {self.__container.samples}")

        # Create value label
        self.__values_label = QLabel(
            f"NaN: {self.__container.nan} Inf: {self.__container.inf}"
        )

        # Adjust layout
        layout.addWidget(self.__channels_label)
        layout.addWidget(self.__sample_label)
        layout.addWidget(self.__values_label)
        layout.addStretch(1)

        # connect signals
        self.__container.channels_signal.connect(self.__on_channels_signal)
        self.__container.data_signal.connect(self.__on_data_signal)

    def __on_channels_signal(self, channels: int):
        self.__channels_label.setText(f"channels: {channels}")

    def __on_data_signal(self, *_):
        self.__sample_label.setText(f"samples: {self.__container.samples}")
        self.__values_label.setText(
            f"NaN: {self.__container.nan} Inf: {self.__container.inf}"
        )
