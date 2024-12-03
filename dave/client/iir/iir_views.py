from typing import Any, List
import numpy as np
from scipy import signal
from warnings import catch_warnings, warn

from matplotlib.axes import Axes

from dave.common.raw_iir import RawIir
from dave.common.logger import Logger
from .raw_to_numpy import InternalNpy

from ..entity.entity_view import EntityView

DEFAULT_COLOR = "#1f77b4"


# ===========================================================================
class IirView(EntityView):
    pass


# ==============================================================================
class MagnitudeResponseView(IirView):
    def __init__(self) -> None:
        self.__x_scale = EntityView.StringSetting("X scale", ("linear", "log"))
        self.__y_scale = EntityView.StringSetting("Y scale", ("linear", "log"))
        self.__resolution = EntityView.IntSetting("Resolution", 64, 4096, 512)
        self.__limit = EntityView.StringSetting("Limit", ("nyquist", "samplerate"))

    @staticmethod
    def name() -> str:
        return "Magnitude"

    def update_setting(self, setting_name: str, setting_value: Any):
        match setting_name:
            case self.__x_scale.name:
                self.__x_scale.value = setting_value
            case self.__y_scale.name:
                self.__y_scale.value = setting_value
            case self.__resolution.name:
                self.__resolution.value = setting_value
            case self.__limit.name:
                self.__limit.value = setting_value
            case _:
                raise RuntimeError(
                    f"{setting_name} is not a valid MagnitudeResponseView setting"
                )

    def render_view(self, axes: Axes, data: InternalNpy, samplerate: int, color=None):
        if color is None:
            color = DEFAULT_COLOR

        whole = self.__limit.value == "samplerate"
        w, h = signal.freqz_sos(data.sos, self.__resolution.value, whole, fs=samplerate)
        magnitude = np.abs(h)

        axes.plot(w, magnitude, color=color)
        axes.set_xscale(self.__x_scale.value)
        axes.set_yscale(self.__y_scale.value)
        axes.set_ylabel("Magnitude")
        axes.grid(visible=True, which="both")

    def get_settings(self) -> List[EntityView.Setting]:
        return [self.__x_scale, self.__y_scale, self.__resolution, self.__limit]


# ==============================================================================
class PhaseResponseView(IirView):
    def __init__(self) -> None:
        self.__x_scale = EntityView.StringSetting("X scale", ("linear", "log"))
        self.__resolution = EntityView.IntSetting("Resolution", 64, 4096, 512)
        self.__limit = EntityView.StringSetting("Limit", ("nyquist", "samplerate"))

    @staticmethod
    def name() -> str:
        return "Phase"

    def update_setting(self, setting_name: str, setting_value: Any):
        match setting_name:
            case self.__x_scale.name:
                self.__x_scale.value = setting_value
            case self.__resolution.name:
                self.__resolution.value = setting_value
            case self.__limit.name:
                self.__limit.value = setting_value
            case _:
                raise RuntimeError(
                    f"{setting_name} is not a valid PhaseResponseView setting"
                )

    def render_view(self, axes: Axes, data: InternalNpy, samplerate: int, color=None):
        if color is None:
            color = DEFAULT_COLOR

        whole = self.__limit.value == "samplerate"
        w, h = signal.freqz_sos(data.sos, self.__resolution.value, whole, fs=samplerate)

        axes.plot(w, np.angle(h), color=color)
        axes.set_ylim(-np.pi, np.pi)
        axes.set_xscale(self.__x_scale.value)
        axes.set_ylabel("Phase")
        axes.grid(visible=True, which="both")

    def get_settings(self) -> List[EntityView.Setting]:
        return [self.__x_scale, self.__resolution, self.__limit]
