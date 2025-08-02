from __future__ import annotations
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, List, Set, Tuple, Union

from matplotlib.axes import Axes
import numpy as np
import pyqtgraph as pg

from PySide6.QtCore import QObject, Signal

from dave.common.raw_entity import RawEntity

from .entity_view import EntityView
from .entity_settings_frame import EntitySettingsFrame
from .entity_side_panel_info import EntitySidePanelInfo


class EntityModel(QObject):
    # Settings signals to send when a specific part has been updated
    data_signal = Signal()
    possible_views_signal = Signal()
    view_signal = Signal(str)
    view_settings_signal = Signal()
    frozen_signal = Signal(bool)
    concat_signal = Signal(bool)
    channels_signal = Signal(int)
    samplerate_signal = Signal(int)
    # Signal to send when the model is to be deleted
    deletion_signal = Signal(int)
    # Signal when the model has been updated and the view should be updated
    update_signal = Signal(str)

    def __init__(self, raw: RawEntity):
        super().__init__()
        self._raw = raw
        self._data: Any = None
        self._frozen_data = None
        self._sr = None
        self._channels = raw.channels()
        self._in_scope = raw.in_scope
        self._view: EntityView = self.possible_views[0]()

        # Connect all settings signal to the update signal
        self.data_signal.connect(lambda: self._emit_update("data"))
        self.view_signal.connect(lambda: self._emit_update("view"))
        self.view_settings_signal.connect(lambda: self._emit_update("view_settings"))
        self.frozen_signal.connect(lambda: self._emit_update("frozen"))
        self.concat_signal.connect(lambda: self._emit_update("concat"))
        self.channels_signal.connect(lambda: self._emit_update("channel"))
        self.samplerate_signal.connect(lambda: self._emit_update("samplerate"))

    # ==========================================================================
    def _emit_update(self, source: str):
        """
        This method will emit an update signal for the corresponding view to update
        """
        self.update_signal.emit(source)

    # ==========================================================================
    @staticmethod
    @abstractmethod
    def compatible_concatenate() -> bool:
        pass

    @staticmethod
    @abstractmethod
    def settings_frame_class() -> type[EntitySettingsFrame]:
        pass

    @staticmethod
    @abstractmethod
    def side_panel_info_class() -> type[EntitySidePanelInfo]:
        pass

    # ==========================================================================
    @property
    def in_scope(self) -> bool:
        return self._in_scope

    @property
    @abstractmethod
    def possible_views(self) -> List[EntityView]:
        pass

    @property
    def possible_views_names(self) -> List[str]:
        return [view.name() for view in self.possible_views]

    @property
    def selected_view(self) -> str:
        return self._view.name()

    @property
    def view_settings(self) -> List[EntityView.Setting]:
        return self._view.get_settings()

    @property
    def variable_name(self) -> str:
        return self._raw.name

    @property
    def id(self) -> int:
        return self._raw.id

    @property
    def frozen(self) -> bool:
        return self._frozen_data is not None

    @frozen.setter
    def frozen(self, freeze: bool):
        if freeze == self.frozen:
            return
        if freeze:
            self._frozen_data = self._data
        else:
            self._frozen_data = None
        self.frozen_signal.emit(self.frozen)

    @property
    @abstractmethod
    def concat(self) -> bool:
        pass

    @property
    def is_view_superposable(self) -> bool:
        return self._view.is_superposable()

    @property
    def are_dimensions_fixed(self) -> bool:
        """
        Returns True if the entity somehow supports multiple dimension layouts

        example: a std::vector could be used to represent mono/stereo or plain/interleaved
        samples, a JUCE buffer couldn't, hence its dimensions are fixed
        """
        pass

    @property
    def channels(self) -> int:
        """
        Channels property, not editable

        A specific entity might require to have channels editable (like containers)
        in which case you should implement a validate_and_update_channel method

        Returns the number of channels for this entity
        """
        return self._channels

    @property
    def samplerate(self) -> Union[None, int]:
        """
        Samplerate property, not editable

        To validate and update a new samplerate use the validate_and_update_samplerate method

        Returns None if no specific samplerate has been forced on this entity
        (ie: use the default), the specified samplerate otherwise
        """
        return self._sr

    def validate_and_update_samplerate(self, value: int) -> bool:
        if isinstance(value, str):
            try:
                value = int(value)
            except ValueError:
                return False
        if value > 0:
            if value != self.samplerate:
                self._sr = value
                self.samplerate_signal(self.samplerate)
            return True
        return False

    def update_view_type(self, view_name: str):
        for view_type in self.possible_views:
            if view_type.name() == view_name:
                self._view = view_type()
                self.view_signal.emit(view_name)
                break

    def update_view_settings(self, setting_name: str, setting_value: Any):
        self._view.update_setting(setting_name, setting_value)
        self.view_settings_signal.emit()

    # ==========================================================================
    def _live_render_data(self) -> np.ndarray:
        """
        Returns the live data as it should be drawn
        """
        return self._data

    def _frozen_render_data(self) -> np.ndarray:
        assert self._frozen_data is not None
        return self._frozen_data

    # ==========================================================================
    @abstractmethod
    def serialize_types(self) -> List[Tuple[str, str]]:
        """
        Returns the possible file formats for serialization of this concept.

        Returns
        -------
        List[Tuple[str, str]]
            A List of tuple of 2 strings: first is the humand readable name of the
            file format, second is the file extension.
        """
        pass

    @abstractmethod
    def serialize(self, filename: Path):
        pass

    # ==========================================================================
    def signal_deletion(self):
        self.deletion_signal.emit(self.id)

    @abstractmethod
    def update_data(self, update: RawEntity.InScopeUpdate):
        """
        Updates the model by reading the incoming raw update

        THIS MUST SIGNAL ON data_signal
        """
        pass

    def mark_as_out_of_scope(self):
        self._in_scope = False

    # ==========================================================================
    # @abstractmethod
    def draw_view(
        self, plots: List[pg.PlotWidget], default_sr: int, channel: int, base_name: str
    ):
        """
        Draw the view of the audio entity.

        If the entity is frozen, both frozen and live data will be drawn.
        If the entity is frozen and the current selected view type does not support
        superposable data (eg: spectrogram), then the caller must provide two Axes to draw

        Parameters
        ----------
        plots : List[pg.PlotWidget]
            Either a single pg.PlotWidget in a list, or two if the entity is frozen
            with a non-superposable view type
        default_sr : int
            The default samplerate to use RawEntityif not set in this specific model
        channel : int
            The channel to draw
        kwargs: additional parameters for the concrete class's method
        """
        # pass
        samplerate = self._sr if self._sr is not None else default_sr

        if self.frozen and not self.is_view_superposable:
            # Render frozen and live data on different subplots
            assert len(plots) == 2
            self._view.render_view(
                plots[0],
                self._live_render_data()[channel],
                samplerate,
                base_name + " (Live)",
            )
            self._view.render_view(
                plots[1],
                self._frozen_render_data()[channel],
                samplerate,
                base_name + " (Frozen)",
            )
        else:
            # Render live data
            assert len(plots) == 1
            if self.frozen:
                # Render frozen data on same subplot
                self._view.render_view(
                    plots[0],
                    self._frozen_render_data()[channel],
                    samplerate,
                    base_name,
                    color="#ff7f0e",
                )
            self._view.render_view(
                plots[0], self._live_render_data()[channel], samplerate, base_name
            )

    def channel_name(_, channel: int) -> str:
        return f"channel {channel}"
