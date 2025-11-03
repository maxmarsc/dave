from typing import Any, Dict, List, Tuple
import numpy as np
from scipy import signal
from warnings import catch_warnings, warn

from matplotlib.axes import Axes
from matplotlib import patches

# from matplotlib.pyplot import axvline, axhline

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

    def _render_view(self, axes: Axes, data: InternalNpy, samplerate: int, color=None):
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

    def _render_view(self, axes: Axes, data: InternalNpy, samplerate: int, color=None):
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

    def _render_view(self, axes: Axes, data: InternalNpy, samplerate: int, color=None):
        if color is None:
            color = DEFAULT_COLOR

        # Add unit circle and zero axes
        unit_circle = patches.Circle(
            (0, 0), radius=1, fill=False, color="black", ls="solid", alpha=0.1
        )
        axes.add_patch(unit_circle)
        axes.axvline(0, color="0.7")
        axes.axhline(0, color="0.7")

        z, p, _ = signal.sos2zpk(data.sos)

        z_to_plot, z_duplicates = self.__find_duplicates(z)
        p_to_plot, p_duplicates = self.__find_duplicates(p)

        # Plot the poles and set marker properties
        axes.plot(p_to_plot.real, p_to_plot.imag, "x", markersize=9, color=color)

        # Plot the zeros and set marker properties
        axes.plot(
            z_to_plot.real,
            z_to_plot.imag,
            "o",
            markersize=9,
            color="none",
            markeredgecolor=color,
        )

        # Plot the duplicate markers
        for coords, count in z_duplicates.items():
            axes.text(
                coords.real,
                coords.imag,
                r" ${}^{" + str(count) + "}$",
                fontsize=13,
                color=color,
            )
        for coords, count in p_duplicates.items():
            axes.text(
                coords.real,
                coords.imag,
                r" ${}^{" + str(count) + "}$",
                fontsize=13,
                color=color,
            )

        axes.grid(visible=True, which="both")
        axes.set_aspect("equal", adjustable="box")

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
