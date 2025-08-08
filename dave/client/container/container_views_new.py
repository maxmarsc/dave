from typing import Any, List, Tuple, Union
import numpy as np
from warnings import catch_warnings, warn
import pyqtgraph as pg
from scipy import signal
from PySide6.QtGui import QTransform


from dave.common.raw_container import RawContainer
from dave.common.logger import Logger

from ..entity.entity_view import EntityView, hex_to_rgb_tuple

# DEFAULT_COLOR = "#1f77b4"

# def hex_to_rgb_tuple(hex_color: str) -> tuple:
#     """Convert matplotlib hex color to RGB tuple (0-255)"""
#     rgb_float = to_rgb(hex_color)
#     return tuple(int(c * 255) for c in rgb_float)


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

    def render_view(
        self,
        plot_widget: pg.PlotWidget,
        data: np.ndarray,
        samplerate: int,
        color: Union[None, str] = None,
    ):
        if color is None:
            color = self.DEFAULT_COLOR
        else:
            color: Tuple[int, int, int] = hex_to_rgb_tuple(color)

        # color_rgb = hex_to_rgb_tuple(color)
        plot_widget.plotItem.clear()
        assert len(data.shape) == 1

        full_time_vector: np.ndarray = np.arange(data.shape[0]) / samplerate
        nans = np.isnan(data)
        infs = np.isinf(data)
        finite_mask = ~nans & ~infs

        Logger().warning(
            f"Plotting {full_time_vector[finite_mask].size}x{data[finite_mask].size} values"
        )

        # Plot finite data
        if np.any(finite_mask):
            plot_widget.plotItem.plot(
                full_time_vector[finite_mask].astype(np.float64),
                data[finite_mask].astype(np.float64),
                pen=pg.mkPen(color),
                name="Waveform",
            )

            max_y = np.max(np.abs(data[finite_mask])) * 1.2

            # Add vertical lines for NaN values
            if np.any(nans):
                nans_time_vector = full_time_vector[nans]
                for t in nans_time_vector:
                    line = pg.InfiniteLine(
                        pos=t,
                        angle=90,
                        pen=pg.mkPen("r", style=pg.QtCore.Qt.PenStyle.DotLine),
                    )
                    plot_widget.plotItem.addItem(line)

            # Add vertical lines for Inf values
            if np.any(infs):
                infs_time_vector = full_time_vector[infs]
                for t in infs_time_vector:
                    line = pg.InfiniteLine(
                        pos=t,
                        angle=90,
                        pen=pg.mkPen("g", style=pg.QtCore.Qt.PenStyle.DotLine),
                    )
                    plot_widget.plotItem.addItem(line)

            # if -max_y != max_y:
            #     plot_widget.plotItem.setRange(yRange=[-max_y, max_y])

        plot_widget.plotItem.showGrid(x=True, y=True)
        plot_widget.plotItem.setLabel("bottom", "Time", "s")
        plot_widget.plotItem.setLabel("left", "Amplitude")

    def get_settings(self) -> List[EntityView.Setting]:
        return []


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

    def render_view(
        self,
        plot_widget: pg.PlotWidget,
        data: np.ndarray,
        samplerate: int,
        color: Union[None, str] = None,
    ):
        if color is None:
            color = self.DEFAULT_COLOR
        else:
            color: Tuple[int, int, int] = hex_to_rgb_tuple(color)

        plot_widget.plotItem.clear()

        full_time_vector = np.arange(data.shape[0]) / samplerate
        nans = np.isnan(data)
        infs = np.isinf(data)
        finite_mask = ~nans & ~infs

        # Plot finite data
        if np.any(finite_mask):
            plot_widget.plotItem.plot(
                full_time_vector[finite_mask],
                data[finite_mask],
                pen=pg.mkPen(color=color),
                name="Curve",
            )

            # Add vertical lines for NaN values
            if np.any(nans):
                nans_time_vector = full_time_vector[nans]
                for t in nans_time_vector:
                    line = pg.InfiniteLine(
                        pos=t,
                        angle=90,
                        pen=pg.mkPen("r", style=pg.QtCore.Qt.PenStyle.DotLine),
                    )
                    plot_widget.plotItem.addItem(line)

            # Add vertical lines for Inf values
            if np.any(infs):
                infs_time_vector = full_time_vector[infs]
                for t in infs_time_vector:
                    line = pg.InfiniteLine(
                        pos=t,
                        angle=90,
                        pen=pg.mkPen("g", style=pg.QtCore.Qt.PenStyle.DotLine),
                    )
                    plot_widget.plotItem.addItem(line)

        # Set log/linear scaling
        plot_widget.plotItem.setLogMode(
            x=(self.__x_scale.value == "log"), y=(self.__y_scale.value == "log")
        )

        plot_widget.plotItem.showGrid(x=True, y=True)
        plot_widget.plotItem.setLabel("bottom", "Time", "s")
        plot_widget.plotItem.setLabel("left", "Amplitude")

    def get_settings(self) -> List[EntityView.Setting]:
        return [self.__x_scale, self.__y_scale]


# ===========================================================================
class SpectrogramView(ContainerView):
    def __init__(self) -> None:
        self.__nfft = EntityView.IntSetting("nfft", 16, 4096, 256)
        self.__overlap = EntityView.FloatSetting("overlap", 0.01, 0.99, 0.5)
        self.__window = EntityView.StringSetting(
            "window", ("hann", "boxcar", "blackman", "hamming")
        )

    @staticmethod
    def name() -> str:
        return "Spectrogram"

    @staticmethod
    def is_superposable() -> bool:
        return False

    def update_setting(self, setting_name: str, setting_value: Any):
        Logger().warning(f"SpectrogramView::update_setting")
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

    def render_view(
        self, plot_widget: pg.PlotWidget, data: np.ndarray, samplerate: int, _=None
    ):
        plot_widget.plotItem.clear()

        Logger().warning(f"Plotting spectrogram")

        overlap = int(self.__overlap.value * self.__nfft.value)
        window_name = self.__window.value
        # window_name = self.__window.value if self.__window.value != "none" else None

        try:
            with catch_warnings(record=True) as w:
                # Compute spectrogram (one-sided for audio is typical)
                f, t, Sxx = signal.spectrogram(
                    data,
                    fs=samplerate,
                    nperseg=self.__nfft.value,
                    noverlap=overlap,
                    window=window_name,
                    return_onesided=True,
                    scaling="density",
                )

            if w:
                Logger().warning("Warning in Spectrogram computation")

            # Apply window correction factor for accurate power measurements
            correction_factor = self._get_window_correction_factor(
                window_name, self.__nfft.value
            )
            Sxx_corrected = Sxx * correction_factor

            # Convert to dB, handle zeros/negatives
            Sxx_db = 10 * np.log10(np.maximum(Sxx_corrected, 1e-12))

            # Create transform to map array indices to real time/frequency values
            tr = QTransform()
            tr.translate(t[0], f[0])  # Start at first time/freq values
            tr.scale(
                (t[-1] - t[0]) / (len(t) - 1),  # Time scaling
                (f[-1] - f[0]) / (len(f) - 1),
            )  # Frequency scaling

            # Create and configure ImageItem
            img = pg.ImageItem()
            img.setImage(Sxx_db, levels=[np.min(Sxx_db), np.max(Sxx_db)])
            img.setTransform(tr)

            # Optional: Add colormap
            cmap = pg.colormap.get("viridis")
            img.setColorMap(cmap)

            plot_widget.plotItem.addItem(img)
            plot_widget.plotItem.setLabel("bottom", "Time", "s")
            plot_widget.plotItem.setLabel("left", "Frequency", "Hz")

            # Set proper axis ranges
            # plot_widget.plotItem.setRange(xRange=[t[0], t[-1]], yRange=[f[0], f[-1]])

        except Exception as e:
            Logger().warning(f"Error in Spectrogram rendering: {e}")

    def _get_window_correction_factor(self, window_name: str, nfft: int) -> float:
        """
        Get power correction factor for window functions.

        For power spectral density measurements, we need to compensate for the
        power loss introduced by windowing.
        """
        # Generate the actual window to compute correction factor
        match window_name:
            case "boxcar":
                return 1.0
            case "hann":
                window = signal.windows.hann(nfft)
            case "hamming":
                window = signal.windows.hamming(nfft)
            case "blackman":
                window = signal.windows.blackman(nfft)
            case _:
                raise NotImplementedError()

        # Power correction factor = 1 / (mean of window squared)
        # This compensates for the power loss due to windowing
        power_correction = 1.0 / np.mean(window**2)

        return power_correction


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

    def render_view(
        self,
        plot_widget: pg.PlotWidget,
        data: np.ndarray,
        samplerate: int,
        color: Union[None, str] = None,
    ):
        if color is None:
            color = self.DEFAULT_COLOR
        else:
            color: Tuple[int, int, int] = hex_to_rgb_tuple(color)

        plot_widget.plotItem.clear()

        if np.any(np.isnan(data)) or np.any(np.isinf(data)):
            # PyQtGraph doesn't have direct text plotting, so we'll use a TextItem
            text = pg.TextItem(
                "Non finite values, cannot compute PSD", anchor=(0.5, 0.5)
            )
            plot_widget.plotItem.addItem(text)
            text.setPos(0.5, 0.5)  # Center position
            return

        overlap = int(self.__overlap.value * self.__nfft.value)
        window_name = self.__window.value if self.__window.value != "none" else None

        try:
            with catch_warnings(record=True) as w:
                f, Pxx = signal.welch(
                    data,
                    fs=samplerate,
                    nperseg=self.__nfft.value,
                    noverlap=overlap,
                    window=window_name,
                )

            if w:
                Logger().warning("Warning in PSD computation")

            # Convert to dB
            Pxx_db = 10 * np.log10(Pxx + 1e-12)

            plot_widget.plotItem.plot(f, Pxx_db, pen=pg.mkPen(color), name="PSD")
            plot_widget.plotItem.setLogMode(x=True, y=False)  # Log frequency axis
            plot_widget.plotItem.showGrid(x=True, y=True)
            plot_widget.plotItem.setLabel("bottom", "Frequency", "Hz")
            plot_widget.plotItem.setLabel("left", "PSD", "dB/Hz")

        except Exception as e:
            Logger().warning(f"Error in PSD rendering: {e}")


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

    def render_view(
        self,
        plot_widget: pg.PlotWidget,
        data: np.ndarray,
        samplerate: int,
        color: Union[None, str] = None,
    ):
        if color is None:
            color = self.DEFAULT_COLOR
        else:
            color: Tuple[int, int, int] = hex_to_rgb_tuple(color)

        plot_widget.plotItem.clear()
        data = np.abs(data)

        full_x_vector = np.arange(data.shape[0])
        nans = np.isnan(data)
        infs = np.isinf(data)
        finite_mask = ~nans & ~infs

        # Plot finite data
        if np.any(finite_mask):
            plot_widget.plotItem.plot(
                full_x_vector[finite_mask],
                data[finite_mask],
                pen=pg.mkPen(color),
                name="Magnitude",
            )

            # Add vertical lines for NaN values
            if np.any(nans):
                nans_x_vector = full_x_vector[nans]
                for x in nans_x_vector:
                    line = pg.InfiniteLine(
                        pos=x,
                        angle=90,
                        pen=pg.mkPen("r", style=pg.QtCore.Qt.PenStyle.DotLine),
                    )
                    plot_widget.plotItem.addItem(line)

            # Add vertical lines for Inf values
            if np.any(infs):
                infs_x_vector = full_x_vector[infs]
                for x in infs_x_vector:
                    line = pg.InfiniteLine(
                        pos=x,
                        angle=90,
                        pen=pg.mkPen("g", style=pg.QtCore.Qt.PenStyle.DotLine),
                    )
                    plot_widget.plotItem.addItem(line)

        plot_widget.plotItem.showGrid(x=True, y=True)
        plot_widget.plotItem.setLabel("bottom", "Sample")
        plot_widget.plotItem.setLabel("left", "Magnitude")


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

    def render_view(
        self,
        plot_widget: pg.PlotWidget,
        data: np.ndarray,
        samplerate: int,
        color: Union[None, str] = None,
    ):
        if color is None:
            color = self.DEFAULT_COLOR
        else:
            color: Tuple[int, int, int] = hex_to_rgb_tuple(color)

        plot_widget.plotItem.clear()
        data = np.angle(data)

        x_vector = np.arange(data.shape[0])
        nans = np.isnan(data)
        infs = np.isinf(data)
        finite_mask = ~nans & ~infs

        # Plot finite data
        if np.any(finite_mask):
            plot_widget.plotItem.plot(
                x_vector[finite_mask],
                data[finite_mask],
                pen=pg.mkPen(color),
                name="Phase",
            )

            # Add vertical lines for NaN values
            if np.any(nans):
                nans_x_vector = x_vector[nans]
                for x in nans_x_vector:
                    line = pg.InfiniteLine(
                        pos=x,
                        angle=90,
                        pen=pg.mkPen("r", style=pg.QtCore.Qt.PenStyle.DotLine),
                    )
                    plot_widget.plotItem.addItem(line)

            # Add vertical lines for Inf values
            if np.any(infs):
                infs_x_vector = x_vector[infs]
                for x in infs_x_vector:
                    line = pg.InfiniteLine(
                        pos=x,
                        angle=90,
                        pen=pg.mkPen("g", style=pg.QtCore.Qt.PenStyle.DotLine),
                    )
                    plot_widget.plotItem.addItem(line)

        plot_widget.plotItem.showGrid(x=True, y=True)
        plot_widget.plotItem.setLabel("bottom", "Sample")
        plot_widget.plotItem.setLabel("left", "Phase", "radians")


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
