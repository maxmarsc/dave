from typing import Any, List, Tuple, Union
import numpy as np
from warnings import catch_warnings, warn
import pyqtgraph as pg
from scipy import signal
from PySide6.QtGui import QTransform


from dave.common.raw_container import RawContainer
from dave.common.logger import Logger

from ..entity.entity_view import EntityView, hex_to_rgb_tuple


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

    def _render_view(
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

        assert len(data.shape) == 1

        fg_color = self.palette_colors(plot_widget)[2]

        full_time_vector: np.ndarray = np.arange(data.shape[0]) / samplerate
        nans = np.isnan(data)
        infs = np.isinf(data)
        finite_mask = ~nans & ~infs

        # Plot finite data
        if np.any(finite_mask):
            plot_widget.plotItem.plot(
                full_time_vector[finite_mask].astype(np.float64),
                data[finite_mask].astype(np.float64),
                pen=pg.mkPen(color, width=2),
                name="Waveform",
            )

            max_y = np.float64(np.max(np.abs(data[finite_mask])) * 1.2)

            # Center Y axis on zero
            if max_y != 0:
                plot_widget.plotItem.setRange(yRange=[-max_y, max_y])

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

        plot_widget.plotItem.showGrid(x=True, y=True)
        plot_widget.plotItem.setLabel("bottom", "Time", "s", pen=fg_color)
        plot_widget.plotItem.setLabel("left", "Amplitude", pen=fg_color)

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

    def _render_view(
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

        fg_color = self.palette_colors(plot_widget)[2]

        full_time_vector = np.arange(data.shape[0]) / samplerate
        nans = np.isnan(data)
        infs = np.isinf(data)
        finite_mask = ~nans & ~infs

        # Plot finite data
        if np.any(finite_mask):
            plot_widget.plotItem.plot(
                full_time_vector[finite_mask],
                data[finite_mask],
                pen=pg.mkPen(color=color, width=2),
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
        plot_widget.plotItem.setLabel("bottom", "Time", "s", pen=fg_color)
        plot_widget.plotItem.setLabel("left", "Amplitude", pen=fg_color)

    def get_settings(self) -> List[EntityView.Setting]:
        return [self.__x_scale, self.__y_scale]


# ===========================================================================
class SpectrogramView(ContainerView):
    __WINDOW_CORRECTION_FACTOR = {
        "hann": 1.63,
        "blackman": 1.97,
        "hamming": 1.59,
        "boxcar": 1.0,
    }

    def __init__(self) -> None:
        self.__nfft = EntityView.IntSetting("nfft", 16, 4096, 256)
        self.__overlap = EntityView.FloatSetting("overlap", 0.01, 0.99, 0.5)
        self.__window = EntityView.StringSetting(
            "window", ("hann", "boxcar", "blackman", "hamming")
        )
        self.__color_map = EntityView.StringSetting("colormap", ("magma", "viridis"))

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
        elif setting_name == self.__color_map.name:
            self.__color_map.value = setting_value
        else:
            raise RuntimeError(f"{setting_name} is not a valid Spectrogram setting")

    def get_settings(self) -> List[EntityView.Setting]:
        return (self.__nfft, self.__overlap, self.__window, self.__color_map)

    def _render_view(
        self, plot_widget: pg.PlotWidget, data: np.ndarray, samplerate: int, _=None
    ):

        overlap = int(self.__overlap.value * self.__nfft.value)
        window_name = self.__window.value

        try:
            with catch_warnings(record=True) as w:
                # Compute spectrogram
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

            fg_color = self.palette_colors(plot_widget)[2]

            # Apply window correction factor for accurate power measurements
            correction_factor = self.__WINDOW_CORRECTION_FACTOR[window_name]
            Sxx_corrected = Sxx * correction_factor

            # Convert to dB, handle zeros/negatives
            Sxx_db = 10 * np.log10(np.maximum(Sxx_corrected, 1e-12))

            # Create and configure ImageItem
            img = pg.ImageItem()
            img.setImage(Sxx_db.T, levels=[np.min(Sxx_db), np.max(Sxx_db)])

            # Create transform to map array indices to real time/frequency values
            tr = QTransform()
            tr.translate(0, 0)  # Start at first time/freq values
            tr.scale(
                (
                    (self.__nfft.value / samplerate)
                    if len(t) == 1
                    else (t[-1] - t[0]) / (len(t) - 1)
                ),  # Time scaling
                (f[-1] - f[0]) / (len(f) - 1),  # Frequency scaling
            )
            img.setTransform(tr)

            # Add colormap
            cmap = pg.colormap.get(self.__color_map.value)
            img.setColorMap(cmap)

            # Add colorbar
            colorbar = pg.ColorBarItem(
                interactive=True,
                values=(np.min(Sxx_db), np.max(Sxx_db)),
                colorMap=cmap,
                label="Power (dB)",
                width=15,
            )
            colorbar.setImageItem(img, insert_in=plot_widget.plotItem)

            plot_widget.plotItem.addItem(img)
            plot_widget.plotItem.setLabel("bottom", "Time", "s", pen=fg_color)
            plot_widget.plotItem.setLabel("left", "Frequency", "Hz", pen=fg_color)

        except Exception as e:
            Logger().warning(f"Error in Spectrogram rendering: {e}")


# ===========================================================================
class PSDView(ContainerView):
    def __init__(self) -> None:
        self.__nfft = EntityView.IntSetting("nfft", 16, 4096, 256)
        self.__overlap = EntityView.FloatSetting("overlap", 0.01, 0.99, 0.5)
        self.__window = EntityView.StringSetting(
            "window", ("hann", "boxcar", "blackman", "hamming")
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

    def _render_view(
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

        fg_color = self.palette_colors(plot_widget)[2]

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

            plot_widget.plotItem.plot(
                f, Pxx_db, pen=pg.mkPen(color, width=2), name="PSD"
            )
            plot_widget.plotItem.setLogMode(x=True, y=False)  # Log frequency axis
            plot_widget.plotItem.showGrid(x=True, y=True)
            plot_widget.plotItem.setLabel("bottom", "Frequency", "Hz", pen=fg_color)
            plot_widget.plotItem.setLabel("left", "PSD", "dB/Hz", pen=fg_color)

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

    def _render_view(
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

        fg_color = self.palette_colors(plot_widget)[2]

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
                pen=pg.mkPen(color, width=2),
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
        plot_widget.plotItem.setLabel("bottom", "Sample", pen=fg_color)
        plot_widget.plotItem.setLabel("left", "Magnitude", pen=fg_color)


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

    def _render_view(
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

        fg_color = self.palette_colors(plot_widget)[2]

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
                pen=pg.mkPen(color, width=2),
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
        plot_widget.plotItem.setLabel("bottom", "Sample", pen=fg_color)
        plot_widget.plotItem.setLabel("left", "Phase", "radians", pen=fg_color)


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
