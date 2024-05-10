from abc import ABC, abstractmethod
from typing import List
import numpy as np

from matplotlib.axes import Axes
from .data_model import DataModel


class Setting:
    pass


class AudioView(ABC):
    def __init__(self, samplerate: float) -> None:
        self.__sr = samplerate

    @staticmethod
    @abstractmethod
    def name() -> str:
        pass

    @abstractmethod
    def render_view(self, axes: Axes, data: np.ndarray):
        pass

    @abstractmethod
    def get_settings(self) -> List[Setting]:
        pass


class WaveformView(AudioView):
    def __init__(self, samplerate: float) -> None:
        super().__init__(samplerate)
        self.__line = None

    @staticmethod
    def name() -> str:
        return "Waveform"

    def render_view(self, axes: Axes, data: np.ndarray):
        axes.plot(data)
        axes.grid()

    def get_settings(self) -> List[Setting]:
        return []


class CurveView(AudioView):
    def __init__(self, samplerate: float) -> None:
        super().__init__(samplerate)

    @staticmethod
    def name() -> str:
        return "Curve"

    def render_view(self, axes: Axes, data: np.ndarray):
        axes.plot(data)

    def get_settings(self) -> List[Setting]:
        return []


VIEWS = {WaveformView.name(): WaveformView, CurveView.name(): CurveView}


def get_view_from_name(name: str):
    return VIEWS[name]


def get_views_for_data_model(model: DataModel) -> List:
    if model == DataModel.REAL_1D:
        return [WaveformView, CurveView]
    else:
        return []
