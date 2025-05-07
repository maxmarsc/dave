from __future__ import annotations
from pathlib import Path
from typing import Any, List, Tuple, Union
import warnings
from matplotlib.axes import Axes
import numpy as np

from dave.client.entity.model_factory import ModelFactory
from dave.common.raw_iir import RawIir

from dave.client.entity.entity_model import EntityModel
from dave.client.entity.entity_settings_frame import EntitySettingsFrame
from dave.client.entity.entity_side_panel_info import EntitySidePanelInfo

from .raw_to_numpy import InternalNpy, raw_to_npy
from .iir_views import IirView, MagnitudeResponseView, PhaseResponseView, PolesZerosView


class IirModel(EntityModel):

    def __init__(self, raw: RawIir):
        assert isinstance(raw, RawIir)
        super().__init__(raw)
        self._data: InternalNpy = raw_to_npy(raw.coeffs)

    # ==========================================================================
    @staticmethod
    def compatible_concatenate() -> bool:
        return RawIir.supports_concat()

    @staticmethod
    def settings_frame_class() -> type[EntitySettingsFrame]:
        from .iir_settings_frame import IirSettingsFrame

        return IirSettingsFrame

    @staticmethod
    def side_panel_info_class() -> type[EntitySidePanelInfo]:
        from .iir_side_panel_info import IirSidePanelInfo

        return IirSidePanelInfo

    # ==========================================================================
    @property
    def possible_views(self) -> List[type[IirView]]:
        return [MagnitudeResponseView, PhaseResponseView, PolesZerosView]

    @property
    def concat(self) -> bool:
        # IIR does not supports concatenation over time
        assert RawIir.supports_concat() == False
        return False

    @property
    def are_dimensions_fixed(self) -> bool:
        return True

    @property
    def zeros_poles(self) -> Tuple[int, int]:
        return self._data.zeros_poles

    @property
    def order(self) -> int:
        return self._data.order

    # ==========================================================================
    def serialize_types(self) -> List[Tuple[str, str]]:
        return [
            ("Numpy file (SOS)", ".npy"),
        ]

    def serialize(self, filename: Path):
        match filename.suffix:
            case ".npy":
                self.__save_as_npy(filename)
            case _:
                raise RuntimeError(f"Unsupported extension : {filename.suffix}")

    def __save_as_npy(self, filename: Path):
        np.save(filename, self._data.sos)

    # ==========================================================================
    def update_data(self, update: RawIir.InScopeUpdate):
        self._raw.update(update)
        self._data = raw_to_npy(self._raw.coeffs)
        self._in_scope = True
        self._mark_for_update()

    # ==========================================================================
    def draw_view(self, axes: List[Axes], default_sr: int, **kwargs):
        """
        Draw the filter view

        If the filter is frozen, both frozen and live data will be drawn
        If the filter is frozen and the current selected view type does not support
        superposable data (eg: spectrogram), then the caller must provide two Axes to draw

        Parameters
        ----------
        axes : List[Axes]
            Either a single Axes in a list, or two if the filter is frozen
            with a non-superposable view type
        default_sr: int
            The default samplerate to use if not set in this specific model
        """
        assert isinstance(self._view, IirView)
        samplerate = self._sr if self._sr is not None else default_sr

        if self.frozen and not self.is_view_superposable:
            # Render frozen and live data on different subplots
            assert len(axes) == 2
            self._view.render_view(axes[0], self._data, samplerate)
            self._view.render_view(axes[0], self._frozen_data, samplerate)
        else:
            # Render live data
            assert len(axes) == 1
            if self.frozen:
                self._view.render_view(
                    axes[0], self._frozen_data, samplerate, "#ff7f0e"
                )
            self._view.render_view(axes[0], self._data, samplerate)
