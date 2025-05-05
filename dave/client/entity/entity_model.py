from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, List, Tuple, Union

from matplotlib.axes import Axes
import numpy as np


from dave.common.raw_entity import RawEntity

from .entity_view import EntityView
from .entity_settings_frame import EntitySettingsFrame
from .entity_side_panel_info import EntitySidePanelInfo


class EntityModel:
    def __init__(self, raw: RawEntity):
        self._raw = raw
        self._data: Any = None
        self._frozen_data = None
        self._sr = None
        self._channels = raw.channels()
        self._in_scope = True
        self.__update_pending = False
        self._deletion_pending = False
        self._view: EntityView = self.possible_views[0]()

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
        self._mark_for_update()

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

        A specific concept might require to have channels editable (like containers)
        in which case you should implement a validate_and_update_channel method

        Returns the number of channels for this concept
        """
        return self._channels

    @property
    def samplerate(self) -> Union[None, int]:
        """
        Samplerate property, not editable

        To validate and update a new samplerate use the validate_and_update_samplerate method

        Returns None if no specific samplerate has been forced on this concept
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
                self._mark_for_update()
            return True
        return False

    def update_view_type(self, view_name: str):
        for view_type in self.possible_views:
            if view_type.name() == view_name:
                self._view = view_type()
                self._mark_for_update()
                break

    def update_view_settings(self, setting_name: str, setting_value: Any):
        self._view.update_setting(setting_name, setting_value)
        self._mark_for_update()

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
    def serialize(self, filename: str):
        pass

    # ==========================================================================
    def mark_for_deletion(self):
        self._deletion_pending = True

    def check_for_deletion(self) -> bool:
        return self._deletion_pending

    def _mark_for_update(self):
        self.__update_pending = True

    def check_for_update(self) -> bool:
        return self.__update_pending

    def reset_update_flag(self):
        self.__update_pending = False

    @abstractmethod
    def update_data(self, update: RawEntity.InScopeUpdate):
        """
        Updates the model by reading the incoming raw update
        """
        pass

    def mark_as_out_of_scope(self):
        self._in_scope = False

    # ==========================================================================
    @abstractmethod
    def draw_view(self, axes: List[Axes], default_sr: int, **kwargs):
        """
        Draw the view of the audio entity.

        If the entity is frozen, both frozen and live data will be drawn.
        If the entity is frozen and the current selected view type does not support
        superposable data (eg: spectrogram), then the caller must provide two Axes to draw

        Parameters
        ----------
        axes : List[Axes]
            Either a single Axes in a list, or two if the container is frozen
            with a non-superposable view type
        default_sr : int
            The default samplerate to use RawEntityif not set in this specific model
        kwargs: additional parameters for the concrete class's method
        """
        pass

    def channel_name(_, channel: int) -> str:
        return f"channel {channel}"
