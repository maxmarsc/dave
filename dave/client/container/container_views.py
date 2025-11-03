from typing import Any, List
import numpy as np
from warnings import catch_warnings, warn

from matplotlib.axes import Axes

from dave.common.raw_container import RawContainer
from dave.common.logger import Logger

from ..entity.entity_view import EntityView

DEFAULT_COLOR = "#1f77b4"


# ===========================================================================
class ContainerView(EntityView):
    pass


# ===========================================================================
class WaveformView(ContainerView):
    def __init__(self) -> None:
        pass

    @staticmethod
    def name() -> str:
        return "Waveform"

    def update_setting(self, setting_name: str, setting_value: Any):
        pass

    def _render_view(self, axes: Axes, data: np.ndarray, samplerate: int, color=None):
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

        axes.grid(visible=True, which="both")
        if -max_y != max_y:
            axes.set_ylim(-max_y, max_y)
        if infs_time_vector.size > 0 or nans_time_vector.size > 0:
            axes.legend()

    def get_settings(self) -> List[EntityView.Setting]:
        return []
        # return [
        #     self.__y_scale,
        # ]


# ===========================================================================
class CurveView(ContainerView):
    def __init__(self) -> None:
        self.__x_scale = EntityView.StringSetting("X scale", ("linear", "log"))
        self.__y_scale = EntityView.StringSetting("Y scale", ("linear", "log"))

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

    def _render_view(self, axes: Axes, data: np.ndarray, samplerate: int, color=None):
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
        if infs_time_vector.size > 0 or nans_time_vector.size > 0:
            axes.legend()

    def get_settings(self) -> List[EntityView.Setting]:
        return [self.__x_scale, self.__y_scale]


# ===========================================================================
class SpectrogramView(ContainerView):
    def __init__(self) -> None:
        self.__nfft = EntityView.IntSetting("nfft", 16, 4096, 256)
        self.__overlap = EntityView.FloatSetting("overlap", 0.01, 0.99, 0.5)
        self.__window = EntityView.StringSetting(
            "window", ("hanning", "none", "blackman")
        )

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

    def get_settings(self) -> List[EntityView.Setting]:
        return (self.__nfft, self.__overlap, self.__window)

    def _render_view(self, axes: Axes, data: np.ndarray, samplerate: int, _=None):
        overlap = int(self.__overlap.value * self.__nfft.value)
        with catch_warnings(record=True) as w:
            axes.specgram(data, NFFT=self.__nfft.value, Fs=samplerate, noverlap=overlap)
        if w:
            Logger().warning("Divide by zero in Spectrogram rendering, skipping")


# ===========================================================================
class PSDView(ContainerView):
    def __init__(self) -> None:
        self.__nfft = EntityView.IntSetting("nfft", 16, 4096, 256)
        self.__overlap = EntityView.FloatSetting("overlap", 0.01, 0.99, 0.5)
        self.__window = EntityView.StringSetting(
            "window", ("hanning", "none", "blackman")
        )

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

    def get_settings(self) -> List[EntityView.Setting]:
        return (self.__nfft, self.__overlap, self.__window)

    def _render_view(self, axes: Axes, data: np.ndarray, samplerate: int, color=None):
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
class MagnitudeView(ContainerView):
    def __init__(self) -> None:
        pass

    @staticmethod
    def name() -> str:
        return "Magnitude"

    def update_setting(self, setting_name: str, setting_value: Any):
        pass

    def get_settings(self) -> List[EntityView.Setting]:
        return []

    def _render_view(self, axes: Axes, data: np.ndarray, samplerate: int, color=None):
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
class PhaseView(ContainerView):
    def __init__(self) -> None:
        pass

    @staticmethod
    def name() -> str:
        return "Phase"

    def update_setting(self, setting_name: str, setting_value: Any):
        pass

    def get_settings(self) -> List[EntityView.Setting]:
        return []

    def _render_view(self, axes: Axes, data: np.ndarray, samplerate: int, color=None):
        if color is None:
            color = DEFAULT_COLOR
        data = np.angle(data)

        x_vector = np.arange(data.shape[0])  # type: np.ndarray
        nans = np.isnan(data)
        infs = np.isinf(data)
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


def get_views_for_data_layout(model: RawContainer.Layout) -> List:
    if model in (RawContainer.Layout.REAL_1D, RawContainer.Layout.REAL_2D):
        return [WaveformView, CurveView, SpectrogramView, PSDView]
    else:
        return [MagnitudeView, PhaseView]
