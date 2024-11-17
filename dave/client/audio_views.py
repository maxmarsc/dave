from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, List
import numpy as np
from warnings import catch_warnings, warn

from matplotlib.axes import Axes
from dave.common.data_layout import DataLayout
from dave.common.logger import Logger
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
    def render_view(self, axes: Axes, data: np.ndarray, samplerate: int, color=None):
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

    def render_view(self, axes: Axes, data: np.ndarray, samplerate: int, color=None):
        # # axes.set_yscale(self.__y_scale.value)
        # if self.__y_scale.value == "log":
        #     eps = 1e-5
        #     scale_fwd = lambda a: np.sign(a) * np.log10(np.abs(a) + eps)
        #     scale_inv = lambda a: np.sign(a) * (10 ** (np.abs(a)))
        #     # axes.set_yscale("customsymlog", threshold=1e-5)
        #     axes.set_yscale("function", function=(scale_fwd, scale_inv))

        if color is None:
            color = DEFAULT_COLOR
        assert len(data.shape) == 1
        full_time_vector = np.arange(data.shape[0]) / samplerate  # type: np.ndarray
        nans = np.isnan(data)
        infs = np.isinf(data)
        finite_mask = ~nans & ~infs
        nans_time_vector = full_time_vector[nans]
        infs_time_vector = full_time_vector[infs]

        axes.plot(full_time_vector[finite_mask], data[finite_mask], color)
        max_y = np.max(np.abs(data[finite_mask])) * 1.2

        if nans_time_vector.size > 0:
            axes.vlines(
                nans_time_vector,
                -max_y,
                max_y,
                colors="red",
                linestyles="dotted",
                label="NaN",
            )
        if infs_time_vector.size > 0:
            axes.vlines(
                infs_time_vector,
                -max_y,
                max_y,
                colors="green",
                linestyles="dotted",
                label="Inf",
            )

        axes.set_ylim(-max_y, max_y)
        axes.grid(visible=True)
        axes.legend()

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

    def render_view(self, axes: Axes, data: np.ndarray, samplerate: int, color=None):
        if color is None:
            color = DEFAULT_COLOR

        full_time_vector = np.arange(data.shape[0]) / samplerate  # type: np.ndarray
        nans = np.isnan(data)
        infs = np.isinf(data)
        finite_mask = ~nans & ~infs
        nans_time_vector = full_time_vector[nans]
        infs_time_vector = full_time_vector[infs]

        axes.plot(full_time_vector[finite_mask], data[finite_mask], color)
        ylim = axes.get_ylim()

        if nans_time_vector.size > 0:
            axes.vlines(
                nans_time_vector,
                ylim[0],
                ylim[1],
                colors="red",
                linestyles="dotted",
                label="NaN",
            )
        if infs_time_vector.size > 0:
            axes.vlines(
                infs_time_vector,
                ylim[0],
                ylim[1],
                colors="green",
                linestyles="dotted",
                label="Inf",
            )

        axes.set_xscale(self.__x_scale.value)
        axes.set_yscale(self.__y_scale.value)
        axes.grid(visible=True)
        axes.legend()

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

    def render_view(self, axes: Axes, data: np.ndarray, samplerate: int, _=None):
        overlap = int(self.__overlap.value * self.__nfft.value)
        with catch_warnings(record=True) as w:
            axes.specgram(data, NFFT=self.__nfft.value, Fs=samplerate, noverlap=overlap)
        if w:
            Logger().warning("Divide by zero in Spectrogram rendering, skipping")


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

    def render_view(self, axes: Axes, data: np.ndarray, samplerate: int, color=None):
        if color is None:
            color = DEFAULT_COLOR
        if any(np.isnan(data)) or any(np.isinf(data)):
            axes.text(
                0.5,
                0.5,
                "Non finite values, cannot compute PSD",
                fontsize=14,
                ha="center",
                va="center",
            )
            return

        overlap = int(self.__overlap.value * self.__nfft.value)
        with catch_warnings(record=True) as w:
            axes.psd(
                data,
                color=color,
                NFFT=self.__nfft.value,
                Fs=samplerate,
                noverlap=overlap,
            )
        if w:
            Logger().warning("Divide by zero in PSD rendering, skipping")


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

    def render_view(self, axes: Axes, data: np.ndarray, samplerate: int, color=None):
        if color is None:
            color = DEFAULT_COLOR
        data = np.abs(data)

        full_x_vector = np.arange(data.shape[0])  # type: np.ndarray
        nans = np.isnan(data)
        infs = np.isinf(data)
        finite_mask = ~nans & ~infs
        nans_x_vector = full_x_vector[nans]
        infs_x_vector = full_x_vector[infs]

        axes.plot(
            full_x_vector[finite_mask], data[finite_mask], color, label="magnitude"
        )
        ylim = axes.get_ylim()

        if nans_x_vector.size > 0:
            axes.vlines(
                nans_x_vector,
                ylim[0],
                ylim[1],
                colors="red",
                linestyles="dotted",
                label="NaN",
            )
        if infs_x_vector.size > 0:
            axes.vlines(
                infs_x_vector,
                ylim[0],
                ylim[1],
                colors="green",
                linestyles="dotted",
                label="Inf",
            )

        axes.grid(visible=True)
        axes.legend()


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

    def render_view(self, axes: Axes, data: np.ndarray, samplerate: int, color=None):
        if color is None:
            color = DEFAULT_COLOR
        data = np.angle(data)

        x_vector = np.arange(data.shape[0])  # type: np.ndarray
        nans = np.isnan(data)
        infs = np.isinf(data)
        print(f"nans {data[nans]}")
        print(f"infs {data[infs]}")
        finite_mask = ~nans & ~infs
        nans_x_vector = x_vector[nans]
        infs_x_vector = x_vector[infs]

        axes.plot(x_vector[finite_mask], data[finite_mask], color, label="phase")
        ylim = axes.get_ylim()

        if nans_x_vector.size > 0:
            axes.vlines(
                nans_x_vector,
                ylim[0],
                ylim[1],
                colors="red",
                linestyles="dotted",
                label="NaN",
            )
        if infs_x_vector.size > 0:
            axes.vlines(
                infs_x_vector,
                ylim[0],
                ylim[1],
                colors="green",
                linestyles="dotted",
                label="Inf",
            )

        axes.grid(visible=True)
        axes.legend()


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
