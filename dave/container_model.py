from typing import Any, List
from matplotlib.axes import Axes

from .view_setting import Setting
from .container import Container, Container2D
from .data_layout import DataLayout
from .views import get_views_for_data_layout, AudioView, get_view_from_name

from dataclasses import dataclass
import numpy as np

# import gdb
import tkinter as tk

# import uuid


class ContainerModel:
    @dataclass
    class InScopeUpdate:
        id: int
        data: np.ndarray

    @dataclass
    class OutScopeUpdate:
        id: int

    def __init__(self, raw: Container.Raw, samplerate: float):
        self.__raw = raw
        self.__sr = samplerate
        self.__frozen_data = None
        self.__concat = False
        self.__channels = self.__raw.data.shape[0]
        self.__in_scope = True
        self.__interleaved = False
        self.__mid_side = False
        if not issubclass(raw.container_cls, Container):
            raise RuntimeError(f"{raw.container_cls} is not a valid container class")
        self.__data_layout: DataLayout = self.__raw.default_layout
        # First as default
        self.__view: AudioView = get_views_for_data_layout(self.__data_layout)[0](
            self.__sr
        )
        self.__update_pending = True
        self.__deletion_pending = False

    # ==============================================================================
    @property
    def in_scope(self) -> bool:
        return self.__in_scope

    @property
    def data(self) -> np.ndarray:
        return self.__compute_render_array(self.__raw.data)

    @property
    def possible_layouts(self) -> List[DataLayout]:
        return self.__raw.container_cls.available_data_layouts()

    @property
    def selected_layout(self) -> DataLayout:
        return self.__data_layout

    @property
    def possible_views(self) -> List[str]:
        return [view.name() for view in get_views_for_data_layout(self.__data_layout)]

    @property
    def selected_view(self) -> str:
        return self.__view.name()

    @property
    def view_settings(self) -> List[Setting]:
        return self.__view.get_settings()

    @property
    def variable_name(self) -> str:
        return self.__raw.name

    @property
    def id(self) -> int:
        return self.__raw.id

    @property
    def frozen(self) -> bool:
        return self.__frozen_data is not None

    @frozen.setter
    def frozen(self, freeze: bool):
        if freeze == self.frozen:
            return
        if freeze:
            self.__frozen_data = self.__raw.data
        else:
            self.__frozen_data = None
        self.__update_pending = True

    @property
    def concat(self) -> bool:
        return self.__concat

    @concat.setter
    def concat(self, concat: bool):
        if concat == self.concat:
            return
        self.__concat = concat
        self.__update_pending = True

    @property
    def is_view_superposable(self) -> bool:
        return self.__view.is_superposable()

    @property
    def channels(self) -> int:
        return self.__channels

    @channels.setter
    def channels(self, value: int):
        assert not self.is_channel_layout_fixed()
        if self.channels != value:
            self.__channels = value
            self.__update_pending = True

    @property
    def interleaved(self) -> bool:
        if self.is_channel_layout_fixed():
            return False
        return self.__interleaved

    @interleaved.setter
    def interleaved(self, value: bool):
        assert not self.is_channel_layout_fixed()
        if self.interleaved != value:
            self.__interleaved = value
            self.__update_pending = True

    @property
    def mid_side(self) -> bool:
        if self.channels != 2:
            return False
        return self.__mid_side

    @mid_side.setter
    def mid_side(self, value: bool):
        assert self.channels == 2
        if self.mid_side != value:
            self.__mid_side = value
            self.__update_pending = True

    def is_layout_2D(self):
        if self.__data_layout in (DataLayout.REAL_2D, DataLayout.CPX_2D):
            return True
        return False

    def is_channel_layout_fixed(self):
        if issubclass(self.__raw.container_cls, Container2D):
            return True
        return False

    # ==============================================================================
    def mark_for_deletion(self):
        self.__deletion_pending = True

    def check_for_deletion(self) -> bool:
        return self.__deletion_pending

    def check_for_update(self) -> bool:
        return self.__update_pending

    def reset_update_flag(self):
        self.__update_pending = False

    def __compute_render_array(self, data: np.ndarray) -> np.ndarray:
        total_samples = data.shape[0] * data.shape[1]
        render_shape = (self.__channels, int(total_samples / self.__channels))
        if self.interleaved:
            interleaved_shape = render_shape[::-1]
            render_data = data.reshape(interleaved_shape).T
        else:
            render_data = data.reshape(render_shape)

        if not self.mid_side:
            return render_data
        else:
            # Requires a rewrite in memory
            mid_side_data = np.array(render_data)
            mid_side_data[0] = (render_data[0][:] + render_data[1][:]) / 2.0
            mid_side_data[1] = (render_data[0][:] - render_data[1][:]) / 2.0
            return mid_side_data

    def draw_audio_view(self, axes: List[Axes], channel: int):
        """
        Draw the audio view of the given channel

        If the container is frozen, both frozen and live data will be drawn.
        If the container is frozen and the current selected view type does not support
        superposable data (eg: spectrogram), then the caller must provide two Axes to draw

        Parameters
        ----------
        axes : List[Axes]
            Either a single Axes in a list, or two if the container is frozen
            with a non-superposable view type
        channel : int
            The channel to draw
        """
        # Compute the rendering shape
        live_data = self.__compute_render_array(self.__raw.data)
        if self.frozen:
            frozen_data = self.__compute_render_array(self.__frozen_data)

        if self.frozen and not self.is_view_superposable:
            # Render frozen and live data on different subplots
            assert len(axes) == 2
            self.__view.render_view(axes[0], live_data[channel])
            self.__view.render_view(axes[1], frozen_data[channel])
        else:
            # Render live data
            assert len(axes) == 1
            self.__view.render_view(axes[0], live_data[channel])
            if self.frozen:
                # Render frozen data on same subplot
                self.__view.render_view(axes[0], frozen_data[channel], "#ff7f0e")

    # ==============================================================================
    def update_data(self, new_data: np.ndarray):
        new_data = self.__data_layout.convert_to_layout(new_data)
        if self.concat:
            self.__raw.data = np.concatenate((self.__raw.data, new_data), -1)
        else:
            self.__raw.data = new_data
        self.__in_scope = True
        self.__update_pending = True

    def mark_as_out_of_scope(self):
        self.__in_scope = False

    def update_channel(self, value: int) -> bool:
        if isinstance(value, str):
            try:
                value = int(value)
            except ValueError:
                return False
        if (
            value > 0
            and value <= self.__raw.data.shape[1]
            and self.__raw.data.shape[1] % value == 0
        ):
            if value != self.channels:
                self.channels = value
            return True
        return False

    def update_layout(self, new_layout: DataLayout):
        assert new_layout in self.possible_layouts
        self.__data_layout = new_layout
        self.__raw.data = self.__data_layout.convert_to_layout(self.__raw.data)
        if self.frozen:
            self.__frozen_data = self.__data_layout.convert_to_layout(
                self.__frozen_data
            )
        self.__view: AudioView = get_views_for_data_layout(self.__data_layout)[0](
            self.__sr
        )
        self.__channels = self.__raw.data.shape[0]
        self.__update_pending = True

    def update_view_type(self, view_name: str):
        possibles_views = get_views_for_data_layout(self.__data_layout)
        for view_type in possibles_views:
            if view_type.name() == view_name:
                self.__view = view_type(self.__sr)
                self.__update_pending = True
                break

    def update_view_settings(self, setting_name: str, setting_value: Any):
        self.__view.update_setting(setting_name, setting_value)
        self.__update_pending = True
