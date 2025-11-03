from typing import Any, Dict, List, Tuple, Union
import numpy as np
from scipy import signal
from warnings import catch_warnings, warn
import pyqtgraph as pg

from ..entity.entity_view import EntityView, hex_to_rgb_tuple


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

        whole = self.__limit.value == "samplerate"
        w, h = signal.freqz_sos(data, self.__resolution.value, whole, fs=samplerate)
        magnitude = np.abs(h)

        plot_widget.plotItem.plot(w, magnitude, pen=pg.mkPen(color, width=2))
        plot_widget.plotItem.setLogMode(
            x=(self.__x_scale.value == "log"), y=(self.__y_scale.value == "log")
        )
        plot_widget.plotItem.setLabel("left", "Magnitude", pen=fg_color)
        plot_widget.plotItem.setLabel("bottom", "Frequency", "Hz", pen=fg_color)
        plot_widget.plotItem.showGrid(x=True, y=True)

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

        whole = self.__limit.value == "samplerate"
        w, h = signal.freqz_sos(data, self.__resolution.value, whole, fs=samplerate)

        plot_widget.plotItem.plot(w, np.angle(h), pen=pg.mkPen(color, width=2))
        plot_widget.plotItem.setRange(yRange=[-np.pi, np.pi])
        plot_widget.plotItem.setLogMode(x=(self.__x_scale.value == "log"), y=False)
        plot_widget.plotItem.setLabel("left", "Phase", "radians", pen=fg_color)
        plot_widget.plotItem.setLabel("bottom", "Frequency", "Hz", pen=fg_color)
        plot_widget.plotItem.showGrid(x=True, y=True)

    def get_settings(self) -> List[EntityView.Setting]:
        return [self.__x_scale, self.__resolution, self.__limit]


# ==============================================================================
class PolesZerosView(IirView):
    """
    Based on https://gist.github.com/endolith/4625838
    """

    def __init__(self) -> None:
        self.__dup_eps = EntityView.FloatSetting(
            "Duplicate Epsilon", 0.0, np.inf, 1e-12
        )

    @staticmethod
    def name() -> str:
        return "Poles/Zeros"

    def update_setting(self, setting_name: str, setting_value: Any):
        match setting_name:
            case self.__dup_eps.name:
                self.__dup_eps.value = setting_value
            case _:
                raise RuntimeError(
                    f"{setting_name} is not a valid PolesZerosView setting"
                )

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

        # Add unit circle
        circle = pg.CircleROI(
            [0, 0],
            size=[2, 2],
            movable=False,
            rotatable=False,
            resizable=False,
            pen=pg.mkPen("white", width=1),
        )
        circle.removeHandle(0)
        circle.setPos([-1, -1])  # Center at origin
        plot_widget.plotItem.addItem(circle)

        # Add zero axes (vertical and horizontal lines through origin)
        vline = pg.InfiniteLine(
            pos=0, angle=90, pen=pg.mkPen(color=(180, 180, 180), width=1)
        )
        hline = pg.InfiniteLine(
            pos=0, angle=0, pen=pg.mkPen(color=(180, 180, 180), width=1)
        )
        plot_widget.plotItem.addItem(vline)
        plot_widget.plotItem.addItem(hline)

        z, p, _ = signal.sos2zpk(data)

        z_to_plot, z_duplicates = self.__find_duplicates(z)
        p_to_plot, p_duplicates = self.__find_duplicates(p)

        # Plot poles as X markers
        if len(p_to_plot) > 0:
            poles_scatter = pg.ScatterPlotItem(
                pos=np.column_stack([p_to_plot.real, p_to_plot.imag]),
                symbol="x",
                size=12,
                pen=pg.mkPen(color),
                brush=pg.mkBrush(color),
            )
            plot_widget.plotItem.addItem(poles_scatter)

        # Plot zeros as O markers
        if len(z_to_plot) > 0:
            zeros_scatter = pg.ScatterPlotItem(
                pos=np.column_stack([z_to_plot.real, z_to_plot.imag]),
                symbol="o",
                size=12,
                pen=pg.mkPen(color, width=3),
                brush=None,  # Hollow circles
            )
            plot_widget.plotItem.addItem(zeros_scatter)

        # Add duplicate markers as text
        for coords, count in z_duplicates.items():
            text_item = pg.TextItem(f"^{count}", anchor=(0, 0), color=color)
            text_item.setPos(coords.real, coords.imag)
            plot_widget.plotItem.addItem(text_item)

        for coords, count in p_duplicates.items():
            text_item = pg.TextItem(f"^{count}", anchor=(0, 0), color=color)
            text_item.setPos(coords.real, coords.imag)
            plot_widget.plotItem.addItem(text_item)

        # Create legend
        legend = pg.LegendItem(offset=(10, 10), pen="white")
        legend.setParentItem(plot_widget.plotItem)
        legend.anchor((1, 0), (0.90, 0.05))  # Top right corner

        # Add legend entries
        legend.addItem(
            pg.ScatterPlotItem(
                symbol="x", size=12, pen=pg.mkPen(color), brush=pg.mkBrush(color)
            ),
            "poles",
        )
        legend.addItem(
            pg.ScatterPlotItem(symbol="o", size=12, pen=pg.mkPen(color), brush=None),
            "zeros",
        )

        plot_widget.plotItem.showGrid(x=True, y=True)
        plot_widget.plotItem.setAspectLocked(True)
        plot_widget.plotItem.setLabel("bottom", "Real Part", pen=fg_color)
        plot_widget.plotItem.setLabel("left", "Imaginary Part", pen=fg_color)

    def __find_duplicates(
        self, complex_points: np.ndarray[np.complex128]
    ) -> Tuple[np.ndarray[np.complex128], Dict[np.complex128, int]]:
        to_plot = [complex_points[0]]
        duplicated: Dict[np.complex128, int] = dict()

        for candidate in complex_points[1:]:
            # Compute the distance of the candidate to every other already selected points
            distances = np.linalg.norm(candidate - np.array(to_plot), keepdims=True)
            duplicate = False
            for i, dist in enumerate(distances):
                # If it is close enough to any point, we mark it as duplicate
                if dist < self.__dup_eps.value:
                    to_duplicate = to_plot[i]
                    duplicate = True
                    if to_duplicate in duplicated:
                        duplicated[to_duplicate] += 1
                    else:
                        duplicated[to_duplicate] = 2

                    # No need to check for other points
                    break

            # Else we select it
            if not duplicate:
                to_plot.append(candidate)

        return (np.array(to_plot), duplicated)

    def get_settings(self) -> List[EntityView.Setting]:
        return [
            self.__dup_eps,
        ]
