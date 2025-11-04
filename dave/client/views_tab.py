from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QScrollArea,
    QFrame,
    QLabel,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from typing import Dict, List, Union
import pyqtgraph as pg

from dave.client.entity.entity_model import EntityModel
from dave.client.global_settings import GlobalSettings

from dave.client.side_panel import SidePanel
from dave.client.in_scope_dict import InScopeSet
from dave.common.logger import Logger


class EntityPlots(QFrame):
    """
    An vertical box contains all the plots of an entity.

    At least one per channel, or two per channel (live + frozen) if the view is
    frozen and the view type is not superposable
    """

    MINIMUM_PLOT_HEIGHT = 220

    def __init__(
        self, parent: QWidget, model: EntityModel, global_settings: GlobalSettings
    ):
        super().__init__(parent)
        self.__model = model
        self.__plots: List[pg.PlotWidget] = []
        self.__global_settings = global_settings

        # Setup the widgets and layout
        self.__setup_layout()
        self.__update_widgets()

        # Connect to model signals
        self.__model.update_signal.connect(self.__on_model_signal)

    def __setup_layout(self):
        # Create the frame
        self.__layout = QVBoxLayout()
        self.setLayout(self.__layout)
        self.__layout.setContentsMargins(0, 0, 0, 0)
        self.__layout.setSpacing(2)

    # def compute_num_plots(self) -> int:
    #     if self.__model.frozen and not self.__model.is_view_superposable:
    #         # Need space for both live and frozen plots per channel
    #         return 2 * self.__model.channels
    #     else:
    #         # Either not frozen, or frozen but superposable (overlaid)
    #         return self.__model.channels

    def __on_model_signal(self, source: str):
        Logger().debug(
            f"View redraw requested from {source} for model {self.__model.id}"
        )
        self.__update_widgets()

    def __update_widgets(self):
        # Delete the previous plots
        for old_plot in self.__plots:
            self.__layout.removeWidget(old_plot)
            old_plot.deleteLater()
        self.__plots = []

        if self.__model.frozen and not self.__model.is_view_superposable:
            # Create 2 plots per channel: live + frozen (non-superposable)
            for channel in range(self.__model.channels):
                title = self.__model.channel_name(channel)

                # live plot
                live_plot = pg.PlotWidget(self)
                live_plot.setMinimumHeight(self.MINIMUM_PLOT_HEIGHT)

                self.__plots.append(live_plot)
                self.__layout.addWidget(live_plot)

                # frozen plot
                frozen_plot = pg.PlotWidget(self)
                frozen_plot.setMinimumHeight(self.MINIMUM_PLOT_HEIGHT)
                self.__plots.append(frozen_plot)
                self.__layout.addWidget(frozen_plot)

                self.__model.draw_view(
                    [live_plot, frozen_plot],
                    self.__global_settings.samplerate,
                    channel=channel,
                    base_name=title,
                )
        else:
            # Create 1 plot per channel: live + frozen
            for channel in range(self.__model.channels):
                title = self.__model.channel_name(channel)

                # live plot
                live_plot = pg.PlotWidget(self)
                live_plot.setMinimumHeight(self.MINIMUM_PLOT_HEIGHT)
                self.__plots.append(live_plot)
                self.__layout.addWidget(live_plot)
                self.__model.draw_view(
                    [
                        live_plot,
                    ],
                    self.__global_settings.samplerate,
                    channel=channel,
                    base_name=title,
                )

        self.setMinimumHeight(self.MINIMUM_PLOT_HEIGHT * len(self.__plots))


class EntityRow(QFrame):
    """
    A horizontal row containing plots for all channels of one entity and its corresponding side panel

    Each ViewRow handles one complete entity with all its channels
    """

    def __init__(
        self, parent: QWidget, model: EntityModel, global_settings: GlobalSettings
    ) -> None:
        super().__init__(parent)

        self.__model = model
        self.__setup_layout(global_settings)

    def __setup_layout(self, global_settings: GlobalSettings):
        """Setup the main layout and widgets"""
        # Create horizontal layout for [Plot Area | SidePanel]
        self.__layout = QHBoxLayout()
        self.setLayout(self.__layout)
        self.__layout.setContentsMargins(0, 0, 0, 0)
        self.__layout.setSpacing(5)

        # Create plot frame
        self.__plot_frame = EntityPlots(self, self.__model, global_settings)

        # Create side panel (right side)
        self.__side_panel = SidePanel(self, self.__model)

        # Add to main layout: [Plot Area (expandable) | SidePanel (fixed width)]
        self.__layout.addWidget(self.__plot_frame, 1)  # stretch factor 1
        self.__layout.addWidget(self.__side_panel, 0)  # fixed size


class AudioViewsTab:
    """
    The Views tab of the dave GUI

    Structure:
    - One EntityRow per entity
    - Each ViewRow contains all channels for that entity
    """

    def __init__(
        self,
        parent: QWidget,
        entity_models: Dict[int, EntityModel],
        in_scope_models: InScopeSet,
        global_settings: GlobalSettings,
    ) -> None:
        self.__parent = parent
        self.__entity_models = entity_models
        self.__global_settings = global_settings
        self.__empty_label: Union[None, QLabel] = None

        # Store entity rows (one per model)
        self.__entity_rows: Dict[int, EntityRow] = dict()

        # Connect to scope updates
        in_scope_models.scope_signal.connect(self._on_scope_signal)

        self._setup_layout()

    def _setup_layout(self) -> None:
        """Setup the main layout with scrollable area"""
        # Create main layout for parent
        main_layout = QVBoxLayout()
        self.__parent.setLayout(main_layout)

        # Create scrollable area for view rows
        self.__scroll_area = QScrollArea()
        self.__scroll_area.setWidgetResizable(True)
        self.__scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.__scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        # Create content widget for scroll area
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
            QWidget#views_scroll_content {
                background-color: transparent;
            }
            """
        )
        self.__scroll_content.setObjectName("views_scroll_content")

        # Set scroll content
        self.__scroll_area.setWidget(self.__scroll_content)

        # Add scroll area to main layout
        main_layout.addWidget(self.__scroll_area, 1)  # stretch factor 1

    def _on_scope_signal(self, ids: List[int], in_scope: bool):
        if in_scope:
            self.__add_models(ids)
        else:
            self.__remove_models(ids)

    def __add_models(self, ids: List[int]):
        assert len(ids) > 0

        if self.__empty_label is not None:
            self.__scroll_layout.removeWidget(self.__empty_label)
            self.__empty_label.deleteLater()
            self.__empty_label = None

        for id in ids:
            # Get the model
            new_model = self.__entity_models[id]
            assert new_model.in_scope

            # Create entity row
            entity_row = EntityRow(
                self.__scroll_content, new_model, self.__global_settings
            )
            self.__entity_rows[id] = entity_row

            # Add to layout
            self.__scroll_layout.addWidget(entity_row)

    def __remove_models(self, ids: List[int]):
        assert len(ids) > 0
        assert self.__empty_label is None

        for id in ids:
            assert id in self.__entity_rows
            # Get the EntitySettings
            row = self.__entity_rows[id]

            # Remove from layout
            self.__scroll_layout.removeWidget(row)

            # Delete the widget
            row.deleteLater()

            # Remove from our tracking dict
            del self.__entity_rows[id]
