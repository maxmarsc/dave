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

    @property
    @abstractmethod
    def name(self) -> str:
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

    @property
    def name(self) -> str:
        return "Waveform"

    def render_view(self, axes: Axes, data: np.ndarray):
        axes.plot(data)

    def get_settings(self) -> List[Setting]:
        return []


def get_views_for_data_model(model: DataModel) -> List:
    if model == DataModel.REAL_1D:
        return [WaveformView]
    else:
        return []
