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
from typing import Dict, List
import pyqtgraph as pg

# Your existing imports
from dave.client.entity.entity_model import EntityModel
from dave.client.global_settings import GlobalSettings
from dave.client.side_panel import SidePanel
from dave.common.logger import Logger


class ViewRow(QFrame):
    """
    A horizontal row containing plots for ALL channels of one entity and its corresponding side panel
    Replaces the old [all plots on left | all panels on right] layout

    Each ViewRow handles one complete entity with all its channels:
    - If model.frozen=True and model.is_view_superposable=False:
      Height = 2 * channels * 200px (separate live/frozen plots per channel)
    - If model.frozen=True and model.is_view_superposable=True:
      Height = channels * 200px (overlaid live+frozen plots per channel)
    - If model.frozen=False:
      Height = channels * 200px (live plots per channel)
    """

    def __init__(
        self, parent: QWidget, model: EntityModel, global_settings: GlobalSettings
    ) -> None:
        super().__init__(parent)

        self.__model = model
        self.__global_settings = global_settings

        # Track current plot structure to detect when recreation is needed
        self.__current_frozen_state = model.frozen
        self.__current_superposable_state = model.is_view_superposable
        self.__current_channels = model.channels

        # Create horizontal layout for [Plot Area | SidePanel]
        layout = QHBoxLayout()
        self.setLayout(layout)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        self._create_widgets(layout)
        self._update_height()  # Set initial height

    def _calculate_required_height(self) -> int:
        """Calculate the required minimum height based on current model state"""
        base_height_per_channel = 200
        if self.__model.frozen and not self.__model.is_view_superposable:
            # Need space for both live and frozen plots per channel
            return 2 * self.__model.channels * base_height_per_channel
        else:
            # Either not frozen, or frozen but superposable (overlaid)
            return self.__model.channels * base_height_per_channel

    def _update_height(self) -> None:
        """Update the minimum height based on current model state"""
        required_height = self._calculate_required_height()
        self.setMinimumHeight(required_height)

    def _create_widgets(self, layout: QHBoxLayout) -> None:
        """Create plot area with all channel plots and side panel"""

        # Create plot area container (left side)
        plot_area = QFrame()
        plot_area_layout = QVBoxLayout()
        plot_area.setLayout(plot_area_layout)
        plot_area_layout.setContentsMargins(0, 0, 0, 0)
        plot_area_layout.setSpacing(2)

        # Store plot widgets for each channel
        self.__plot_widgets = []

        # Create plots for each channel
        for channel in range(self.__model.channels):
            channel_plots = self._create_channel_plots(channel, plot_area)
            self.__plot_widgets.extend(channel_plots)

            # Add channel plots to plot area
            for plot_widget in channel_plots:
                plot_area_layout.addWidget(plot_widget)

        # Create side panel (right side)
        self.__side_panel = SidePanel(self, self.__model)
        self.__side_panel.setFixedWidth(60)  # Match original width

        # Add to main layout: [Plot Area (expandable) | SidePanel (fixed width)]
        layout.addWidget(plot_area, 1)  # stretch factor 1
        layout.addWidget(self.__side_panel, 0)  # fixed size

    def _create_channel_plots(
        self, channel: int, parent: QWidget
    ) -> List[pg.PlotWidget]:
        """Create plot widget(s) for a specific channel"""
        plots = []
        base_title = self.__model.channel_name(channel)

        if self.__model.frozen and not self.__model.is_view_superposable:
            # Create 2 plots per channel: live + frozen (non-superposable)

            # Live plot
            live_plot = pg.PlotWidget(parent)
            live_plot.setMinimumHeight(200)
            live_plot.setLabel("left", base_title)
            plots.append(live_plot)

            # Frozen plot
            frozen_plot = pg.PlotWidget(parent)
            frozen_plot.setMinimumHeight(200)
            frozen_plot.setLabel("left", base_title + " (f)")
            plots.append(frozen_plot)

        else:
            # Create 1 plot per channel (live only, or live+frozen superposed)
            plot = pg.PlotWidget(parent)
            plot.setMinimumHeight(200)
            plot.setLabel("left", base_title)
            plots.append(plot)

        return plots

    def update_view(self) -> None:
        """Update the plot with current model data"""
        # Clear previous plot
        self.__plot_widget.clear()

        # This will be replaced with PyQtGraph-specific drawing
        # For now, placeholder for the model's draw method
        try:
            # TODO: Replace with PyQtGraph equivalent of model.draw_view()
            # The drawing logic needs to be updated to handle:
            # - self.__is_frozen_view: whether this plot shows frozen data
            # - model.is_view_superposable: whether live+frozen can be overlaid

            # Original matplotlib logic was:
            # if model.frozen and not model.is_view_superposable:
            #     axes = subplots_axes[i : i + 2]  # 2 separate axes for live + frozen
            # else:
            #     axes = subplots_axes[i : i + 1]  # 1 axis (live or superposed)
            # model.draw_view(axes, samplerate, channel=channel)

            # In PyQtGraph version, we'll need something like:
            # if self.__is_frozen_view:
            #     # Draw only frozen data on this plot
            #     self.__model.draw_pyqtgraph_view(self.__plot_widget, self.__global_settings.samplerate,
            #                                      channel=self.__channel, show_frozen_only=True)
            # else:
            #     # Draw live data (and frozen too if superposable)
            #     self.__model.draw_pyqtgraph_view(self.__plot_widget, self.__global_settings.samplerate,
            #                                      channel=self.__channel, show_frozen_only=False)

            # Placeholder: just set title for now
            title = self.__model.channel_name(self.__channel)
            if self.__is_frozen_view:
                title += " (f)"
            self.__plot_widget.setLabel("left", title)

        except Exception as e:
            Logger().warning(
                f"Failed to update view for {self.__model.variable_name}: {e}"
            )

    def update_widgets(self) -> None:
        """Update both plot and side panel"""
        self.update_view()

        # Only update side panel for non-frozen views (frozen views don't have real side panels)
        if not self.__is_frozen_view and hasattr(self.__side_panel, "update_widgets"):
            self.__side_panel.update_widgets()

    @property
    def model_id(self) -> int:
        return self.__model.id

    @property
    def model(self) -> EntityModel:
        return self.__model

    @property
    def plot_widgets(self) -> List[pg.PlotWidget]:
        """Access to all PyQtGraph plot widgets for drawing operations"""
        return self.__plot_widgets

    def get_plots_for_channel(self, channel: int) -> List[pg.PlotWidget]:
        """Get the plot widget(s) for a specific channel based on current model state"""
        if channel >= self.__model.channels:
            return []

        if self.__model.frozen and not self.__model.is_view_superposable:
            # 2 plots per channel: live + frozen
            start_index = channel * 2
            if start_index + 1 < len(self.__plot_widgets):
                return self.__plot_widgets[start_index : start_index + 2]
            else:
                return []
        else:
            # 1 plot per channel
            if channel < len(self.__plot_widgets):
                return [self.__plot_widgets[channel]]
            else:
                return []


class AudioViewsTab:
    """
    The Views tab of the dave GUI - PySide6 version with new layout

    New layout: Vertical stack of horizontal [Plot Area | SidePanel] rows
    instead of [all plots | all sidepanels] layout

    Structure:
    - One ViewRow per entity (not per channel)
    - Each ViewRow contains ALL channels for that entity
    - Plot area height = channels * 200px (or 2 * channels * 200px if frozen non-superposable)

    Frozen Views Logic:
    - If model.frozen=True and model.is_view_superposable=False:
      Each channel gets 2 PlotWidgets (live + frozen), total height = 2 * channels * 200px
    - If model.frozen=True and model.is_view_superposable=True:
      Each channel gets 1 PlotWidget (live+frozen overlaid), total height = channels * 200px
    - If model.frozen=False:
      Each channel gets 1 PlotWidget (live only), total height = channels * 200px

    The frozen state is read directly from the EntityModel - no duplication of state.
    """

    def __init__(
        self,
        parent: QWidget,
        entity_models: Dict[int, EntityModel],
        global_settings: GlobalSettings,
    ) -> None:
        self.__parent = parent
        self.__entity_models = entity_models
        self.__global_settings = global_settings

        # Store view rows (one per model/channel combination)
        self.__view_rows: List[ViewRow] = []

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
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.__scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        # Create content widget for scroll area
        self.__scroll_content = QWidget()
        self.__scroll_layout = QVBoxLayout()
        self.__scroll_content.setLayout(self.__scroll_layout)
        self.__scroll_content.setObjectName("scroll_content")

        # Set scroll content
        self.__scroll_area.setWidget(self.__scroll_content)

        # Add scroll area to main layout
        main_layout.addWidget(self.__scroll_area, 1)  # stretch factor 1

        # Create toolbar frame at bottom (placeholder for now)
        self.__toolbar_frame = QFrame()
        self.__toolbar_frame.setFixedHeight(45)
        # TODO: Add PyQtGraph or matplotlib toolbar here

        main_layout.addWidget(self.__toolbar_frame)

        # Initial update
        self.update_widgets()

    def _create_view_rows(self) -> List[ViewRow]:
        """Create ViewRow widgets for all in-scope models (one ViewRow per entity)"""
        view_rows = []

        for model in self.__entity_models.values():
            if not model.in_scope:
                continue

            if model.channels > 16:
                Logger().warning(
                    f"Too many channels, skipping entity: {model.channels}"
                )
                continue

            # Create one ViewRow per entity (contains all channels for that entity)
            view_row = ViewRow(self.__scroll_content, model, self.__global_settings)
            view_rows.append(view_row)

        return view_rows

    def _clear_view_rows(self) -> None:
        """Remove all existing view rows"""
        for view_row in self.__view_rows:
            self.__scroll_layout.removeWidget(view_row)
            view_row.deleteLater()

        self.__view_rows.clear()

    def update_widgets(self) -> None:
        """Update all view rows based on current model states"""
        # Clear existing rows
        self._clear_view_rows()

        # Create new rows for current in-scope models
        self.__view_rows = self._create_view_rows()

        if not self.__view_rows:
            # Show "no entity in scope" message
            self._show_empty_message()
        else:
            # Add all view rows to layout
            for view_row in self.__view_rows:
                self.__scroll_layout.addWidget(view_row)
                view_row.update_widgets()

        # Add stretch to push content to top
        self.__scroll_layout.addStretch()

    def _show_empty_message(self) -> None:
        """Show message when no entities are in scope"""
        empty_label = QLabel("No entity in scope")
        empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        font = QFont()
        font.setPointSize(14)
        empty_label.setFont(font)

        self.__scroll_layout.addWidget(empty_label)

    def on_resize(self, event) -> None:
        """Handle resize events (simplified from original)"""
        # With the new layout, individual ViewRows handle their own sizing
        # The scroll area automatically handles overflow
        pass
