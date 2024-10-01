from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, List
import numpy as np

from matplotlib.axes import Axes
from dave.common.data_layout import DataLayout
from .view_setting import (
    FloatSetting,
    IntSetting,
    Setting,
    StringSetting,
    BoolSetting,
)

import numpy as np

DEFAULT_COLOR = "#1f77b4"

# import matplotlib.pyplot as plt
# from matplotlib import scale as mscale
# from matplotlib.scale import ScaleBase
# from matplotlib.transforms import Transform
# from matplotlib.ticker import AutoLocator, NullFormatter


# class CustomSymLogTransform(Transform):
#     input_dims = output_dims = 1

#     def __init__(self, threshold):
#         super().__init__()
#         self.threshold = threshold

#     def transform_non_affine(self, a):
#         masked = np.ma.masked_where(a == 0, a)
#         sign = np.sign(masked)
#         loged = sign * np.log10(np.abs(masked) + self.threshold)
#         return np.ma.where(masked == 0, 0, loged)

#     def inverted(self):
#         return CustomSymLogInverseTransform(self.threshold)


# class CustomSymLogInverseTransform(Transform):
#     input_dims = output_dims = 1

#     def __init__(self, threshold):
#         super().__init__()
#         self.threshold = threshold

#     def transform_non_affine(self, a):
#         return np.sign(a) * (10 ** (np.abs(a)) - self.threshold)

#     def inverted(self):
#         return CustomSymLogTransform(self.threshold)


# class CustomSymmetricalLogScale(ScaleBase):
#     name = "customsymlog"

#     def __init__(self, axis, **kwargs):
#         super().__init__(axis)
#         self.threshold = kwargs.pop("threshold", 1e-5)

#     def get_transform(self):
#         return CustomSymLogTransform(self.threshold)

#     def set_default_locators_and_formatters(self, axis):
#         axis.set_major_locator(AutoLocator())
#         axis.set_major_formatter(NullFormatter())
#         axis.set_minor_locator(AutoLocator())
#         axis.set_minor_formatter(NullFormatter())

#     def limit_range_for_scale(self, vmin, vmax, minpos):
#         return max(vmin, -1), min(vmax, 1)


# Register the custom scale
# plt.register_scale(CustomSymmetricalLogScale)
# mscale.register_scale(CustomSymmetricalLogScale)


# ===========================================================================
class AudioView(ABC):
    def __init__(self, samplerate: float) -> None:
        self._sr = samplerate

    @staticmethod
    @abstractmethod
    def name() -> str:
        pass

    @staticmethod
    def is_superposable() -> bool:
        return True

    @abstractmethod
    def render_view(self, axes: Axes, data: np.ndarray, color=None):
        pass

    @abstractmethod
    def get_settings(self) -> List[Setting]:
        pass

    @abstractmethod
    def update_setting(self, setting_name: str, setting_value: Any):
        pass


# ===========================================================================
class WaveformView(AudioView):
    def __init__(self, samplerate: float) -> None:
        super().__init__(samplerate)
        # self.__y_scale = StringSetting("Y scale", ("linear", "log"))

    @staticmethod
    def name() -> str:
        return "Waveform"

    def update_setting(self, setting_name: str, setting_value: Any):
        pass
        # if setting_name == self.__y_scale.name:
        #     self.__y_scale.value = setting_value
        # else:
        #     raise RuntimeError(f"{setting_name} is not a valid WaveformView setting")

    def render_view(self, axes: Axes, data: np.ndarray, color=None):
        # # axes.set_yscale(self.__y_scale.value)
        # if self.__y_scale.value == "log":
        #     eps = 1e-5
        #     scale_fwd = lambda a: np.sign(a) * np.log10(np.abs(a) + eps)
        #     scale_inv = lambda a: np.sign(a) * (10 ** (np.abs(a)))
        #     # axes.set_yscale("customsymlog", threshold=1e-5)
        #     axes.set_yscale("function", function=(scale_fwd, scale_inv))

        if color is None:
            color = DEFAULT_COLOR
        axes.plot(data, color)
        max_y = np.max(np.abs(data)) * 1.2
        if max_y != 0.0:
            try:
                axes.set_ylim(-max_y, max_y)
            except ValueError:
                # Can fail with NaN/inf
                pass
        axes.grid(visible=True)

    def get_settings(self) -> List[Setting]:
        return []
        # return [
        #     self.__y_scale,
        # ]


# ===========================================================================
class CurveView(AudioView):
    def __init__(self, samplerate: float) -> None:
        super().__init__(samplerate)
        self.__x_scale = StringSetting("X scale", ("linear", "log"))
        self.__y_scale = StringSetting("Y scale", ("linear", "log"))

    @staticmethod
    def name() -> str:
        return "Curve"

    def update_setting(self, setting_name: str, setting_value: Any):
        if setting_name == self.__y_scale.name:
            self.__y_scale.value = setting_value
        elif setting_name == self.__x_scale.name:
            self.__x_scale.value = setting_value
        else:
            raise RuntimeError(f"{setting_name} is not a valid CurveView setting")

    def render_view(self, axes: Axes, data: np.ndarray, color=None):
        if color is None:
            color = DEFAULT_COLOR
        axes.plot(data, color)
        axes.set_xscale(self.__x_scale.value)
        axes.set_yscale(self.__y_scale.value)
        axes.grid(visible=True)

    def get_settings(self) -> List[Setting]:
        return [self.__x_scale, self.__y_scale]


# ===========================================================================
class SpectrogramView(AudioView):
    def __init__(self, samplerate: float) -> None:
        super().__init__(samplerate)
        self.__nfft = IntSetting("nfft", 16, 4096, 256)
        self.__overlap = FloatSetting("overlap", 0.01, 0.99, 0.5)
        self.__window = StringSetting("window", ("hanning", "none", "blackman"))

    @staticmethod
    def name() -> str:
        return "Spectrogram"

    @staticmethod
    def is_superposable() -> bool:
        return False

    def update_setting(self, setting_name: str, setting_value: Any):
        if setting_name == self.__nfft.name:
            self.__nfft.value = setting_value
        elif setting_name == self.__overlap.name:
            self.__overlap.value = setting_value
        elif setting_name == self.__window.name:
            self.__window.value = setting_value
        else:
            raise RuntimeError(f"{setting_name} is not a valid Spectrogram setting")

    def get_settings(self) -> List[Setting]:
        return (self.__nfft, self.__overlap, self.__window)

    def render_view(self, axes: Axes, data: np.ndarray, color=None):
        overlap = int(self.__overlap.value * self.__nfft.value)
        axes.specgram(data, NFFT=self.__nfft.value, Fs=self._sr, noverlap=overlap)


# ===========================================================================
class PSDView(AudioView):
    def __init__(self, samplerate: float) -> None:
        super().__init__(samplerate)
        self.__nfft = IntSetting("nfft", 16, 4096, 256)
        self.__overlap = FloatSetting("overlap", 0.01, 0.99, 0.5)
        self.__window = StringSetting("window", ("hanning", "none", "blackman"))

    @staticmethod
    def name() -> str:
        return "PSD"

    def update_setting(self, setting_name: str, setting_value: Any):
        if setting_name == self.__nfft.name:
            self.__nfft.value = setting_value
        elif setting_name == self.__overlap.name:
            self.__overlap.value = setting_value
        elif setting_name == self.__window.name:
            self.__window.value = setting_value
        else:
            raise RuntimeError(f"{setting_name} is not a valid PSD setting")

    def get_settings(self) -> List[Setting]:
        return (self.__nfft, self.__overlap, self.__window)

    def render_view(self, axes: Axes, data: np.ndarray, color=None):
        if color is None:
            color = DEFAULT_COLOR
        overlap = int(self.__overlap.value * self.__nfft.value)
        axes.psd(
            data, color=color, NFFT=self.__nfft.value, Fs=self._sr, noverlap=overlap
        )


# ===========================================================================
class MagnitudeView(AudioView):
    def __init__(self, samplerate: float) -> None:
        super().__init__(samplerate)

    @staticmethod
    def name() -> str:
        return "Magnitude"

    def update_setting(self, setting_name: str, setting_value: Any):
        pass

    def get_settings(self) -> List[Setting]:
        return []

    def render_view(self, axes: Axes, data: np.ndarray, color=None):
        if color is None:
            color = DEFAULT_COLOR
        axes.plot(np.abs(data), color)
        axes.grid(visible=True)
        axes.set_ylabel("Magnitude")


# ===========================================================================
class PhaseView(AudioView):
    def __init__(self, samplerate: float) -> None:
        super().__init__(samplerate)

    @staticmethod
    def name() -> str:
        return "Phase"

    def update_setting(self, setting_name: str, setting_value: Any):
        pass

    def get_settings(self) -> List[Setting]:
        return []

    def render_view(self, axes: Axes, data: np.ndarray, color=None):
        if color is None:
            color = DEFAULT_COLOR
        axes.plot(np.angle(data), color)
        axes.grid(visible=True)
        axes.set_ylabel("Phase")


# ===========================================================================


def get_view_from_name(name: str):
    views = {
        WaveformView.name(): WaveformView,
        CurveView.name(): CurveView,
        SpectrogramView.name(): SpectrogramView,
        PSDView.name(): PSDView,
        MagnitudeView.name(): MagnitudeView,
        PhaseView.name(): PhaseView,
    }
    return views[name]


def get_views_for_data_layout(model: DataLayout) -> List:
    if model in (DataLayout.REAL_1D, DataLayout.REAL_2D):
        return [WaveformView, CurveView, SpectrogramView, PSDView]
    else:
        return [MagnitudeView, PhaseView]
