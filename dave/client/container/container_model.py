from __future__ import annotations
from pathlib import Path
from typing import Any, List, Tuple, Union, override
import warnings

# from matplotlib.axes import Axes

from PySide6.QtCore import Signal

import pyqtgraph as pg

# from dave.common.data_layout import RawContainer.Layout
from dave.common.logger import Logger
from dave.common.raw_container import RawContainer

from dave.client.entity.entity_model import EntityModel
from dave.client.entity.model_factory import ModelFactory
from dave.client.entity.entity_settings_frame import EntitySettingsFrame
from dave.client.entity.entity_side_panel_info import EntitySidePanelInfo
from .raw_to_numpy import (
    convert_container_data_to_layout,
    raw_container_to_numpy,
)

from .container_views import (
    ContainerView,
    WaveformView,
    CurveView,
    SpectrogramView,
    PSDView,
    MagnitudeView,
    PhaseView,
)


from dataclasses import dataclass
import numpy as np

import tkinter as tk
import wave


class ContainerModel(EntityModel):
    interleaved_signal = Signal(bool)
    mid_side_signal = Signal(bool)

    def __init__(self, raw: RawContainer):
        assert isinstance(raw, RawContainer)
        self.__data_layout: RawContainer.Layout = raw.default_layout
        super().__init__(raw)
        self._data = raw_container_to_numpy(raw)
        self.__count_special_values()
        self.__concat = False
        self.__interleaved = raw.interleaved
        self.__mid_side = False

        # Connect all settings signal to the update signal
        self.interleaved_signal.connect(lambda: self._emit_update("interleaved"))
        self.mid_side_signal.connect(lambda: self._emit_update("mid_side"))

    # ==============================================================================
    @staticmethod
    def compatible_concatenate() -> bool:
        return RawContainer.supports_concat()

    @staticmethod
    def get_views_for_layout(layout: RawContainer.Layout) -> List[type[ContainerView]]:
        if layout in (RawContainer.Layout.REAL_1D, RawContainer.Layout.REAL_2D):
            return [WaveformView, CurveView, SpectrogramView, PSDView]
        else:
            return [MagnitudeView, PhaseView]

    @staticmethod
    def settings_frame_class() -> type[EntitySettingsFrame]:
        from .container_settings_frames import ContainerSettingsFrame

        return ContainerSettingsFrame

    @staticmethod
    def side_panel_info_class() -> type[EntitySidePanelInfo]:
        from .container_side_panel_info import ContainerSidePanelInfo

        return ContainerSidePanelInfo

    # ==============================================================================
    @property
    def possible_layouts(self) -> List[RawContainer.Layout]:
        assert isinstance(self._raw, RawContainer)
        return self._raw.possible_layout

    @property
    def selected_layout(self) -> RawContainer.Layout:
        return self.__data_layout

    @property
    def possible_views(self) -> List[type[ContainerView]]:
        return self.get_views_for_layout(self.__data_layout)

    @property
    def concat(self) -> bool:
        return self.__concat

    @concat.setter
    def concat(self, concat: bool):
        if concat == self.concat:
            return
        self.__concat = concat
        self.concat_signal.emit(concat)

    @property
    def samples(self) -> int:
        """
        Num of samples per channel, not editable. Forced to 0 if channels is set to zero
        """
        if self._channels == 0:
            return None
        return int(self._data.size / self._channels)

    @property
    def interleaved(self) -> bool:
        return self.__interleaved

    @interleaved.setter
    def interleaved(self, value: bool):
        assert not self.are_dimensions_fixed
        if self.interleaved != value:
            self.__interleaved = value
            self.interleaved_signal.emit(value)

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
            self.mid_side_signal.emit(value)

    @property
    def nan(self):
        return self.__nan

    @property
    def inf(self):
        return self.__inf

    @property
    def are_dimensions_fixed(self) -> bool:
        assert isinstance(self._raw, RawContainer)
        if self._raw.dimensions_fixed:
            return True
        elif self.__data_layout in (
            RawContainer.Layout.REAL_1D,
            RawContainer.Layout.CPX_1D,
        ):
            return True
        else:
            return False

    # ==========================================================================
    @override
    def _live_render_data(self) -> np.ndarray:
        """
        Returns the live data as it should be drawn
        """
        return self.__compute_render_array(self._data)

    @override
    def _frozen_render_data(self) -> np.ndarray:
        assert self._frozen_data is not None
        return self.__compute_render_array(self._frozen_data)

    # ==============================================================================
    def serialize_types(self) -> List[Tuple[str, str]]:
        filetypes = [("Numpy file", ".npy")]
        if self.selected_layout.is_real:
            filetypes.append(("Wave - 16bit PCM", ".wav"))
        return filetypes

    def serialize(self, filename: Path):
        match (filename.suffix):
            case ".wav":
                self.__save_as_wave(filename)
            case ".npy":
                self.__save_as_npy(filename)
            case _:
                raise RuntimeError(f"Unsupported extension : {filename.suffix}")

    def __save_as_wave(self, filename: Path):
        # Should it be self.__data to be saved instead ?
        interleaved_data = self.__compute_render_array(self._raw.data).T
        if np.max(np.abs(interleaved_data)) > 1.0:
            warnings.warn(
                "Values outside the [-1;1] range were detected, values will be truncated",
            )
            # Truncate values
            interleaved_data[np.where(interleaved_data < -1.0)] = -1.0
            interleaved_data[np.where(interleaved_data > 1.0)] = 1.0
        pcm_data = np.int16(interleaved_data * (2**15 - 1))

        with wave.open(str(filename), "w") as f:
            f.setnchannels(self.channels)
            # 2 bytes per sample.
            f.setsampwidth(2)
            f.setframerate(self.samplerate)
            f.writeframes(pcm_data.tobytes())

    def __save_as_npy(self, filename: Path):
        np.save(filename, self.__compute_render_array(self._data))

    # ==========================================================================
    def update_data(self, update: RawContainer.InScopeUpdate):
        """
        Updates the container data, by loading the bytes into numpy and stores
        it accordingly
        """
        self._raw.update(update)

        new_data = convert_container_data_to_layout(
            raw_container_to_numpy(self._raw), self.__data_layout
        )
        if self.concat:
            self._data = np.concatenate((self._data, new_data), -1)
        else:
            self._data = new_data
        self._channels = self._raw.channels()
        self._in_scope = True
        self.data_signal.emit()

    def update_layout(self, new_layout: Union[str, RawContainer.Layout]):
        if isinstance(new_layout, str):
            new_layout = self._raw.Layout(new_layout)
        assert new_layout in self.possible_layouts
        if new_layout != self.__data_layout:
            self.__data_layout = new_layout
            self._data = convert_container_data_to_layout(self._data, new_layout)
            if self.frozen:
                self._frozen_data = convert_container_data_to_layout(
                    self._frozen_data, new_layout
                )
            # Update the view since the layout dictates possible views
            self._view = self.possible_views[0]()
            self.possible_views_signal.emit()
            self.view_signal.emit(self._view.name())

    # ==========================================================================
    def __compute_render_array(self, data: np.ndarray) -> np.ndarray:
        """
        Produces the array needed for rendering

        Performs (de)interleaving, reshaping, mid/side computing

        Parameters
        ----------
        data : np.ndarray
            The original np.ndarray as seen by the debugger

        Returns
        -------
        np.ndarray
            The transformed array corresponding to the rendering parameters
        """
        total_samples = data.shape[0] * data.shape[1]
        render_shape = (self._channels, int(total_samples / self._channels))
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

    def channel_name(self, channel):
        return (
            f"channel {channel}"
            if not self.mid_side
            else " {}".format("mid" if channel == 0 else "side")
        )

    # ==============================================================================

    def __count_special_values(self):
        """
        Checks the container data for special values : NaN, +inf, -inf

        Will update self.__nan and self.__inf
        """
        self.__nan = int(np.sum(np.isnan(self._data)))
        self.__inf = int(np.sum(np.isinf(self._data)))

    def validate_and_update_channel(self, value: int) -> bool:
        if isinstance(value, str):
            try:
                value = int(value)
            except ValueError:
                return False
        if (
            value > 0
            and value <= self._data.shape[1]
            and self._data.shape[1] % value == 0
        ):
            if value != self.channels:
                self._channels = value
                self.channels_signal.emit(value)
            return True
        return False
