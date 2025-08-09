from PySide6.QtWidgets import (
    QLabel,
    QVBoxLayout,
)

from dave.client.entity.entity_side_panel_info import EntitySidePanelInfo
from .iir_model import IirModel


class IirSidePanelInfo(EntitySidePanelInfo):
    """
    Small textbox with some information on the container

    It contains, top to bottom:
    - zeros, poles
    """

    def __init__(self, parent, iir: IirModel):
        super().__init__(parent)
        self.__iir = iir

        self.__setup_layout()

    def __setup_layout(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Create Z/P label
        z, p = self.__iir.zeros_poles
        self.__zp_labels = QLabel(f"Zeros: {z} Poles: {p}")

        # Create Order label
        order = self.__iir.order
        self.__order_label = QLabel(f"Order: {order}")

        # Adjust layout
        layout.addWidget(self.__zp_labels)
        layout.addWidget(self.__order_label)
        layout.addStretch(1)

        # Connect signals
        self.__iir.data_signal.connect(self.__on_data_signal)

    def __on_data_signal(self, *_):
        z, p = self.__iir.zeros_poles
        self.__zp_labels.setText(f"Zeros: {z} Poles: {p}")

        order = self.__iir.order
        self.__order_label.setText(f"Order: {order}")
