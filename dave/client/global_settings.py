from dataclasses import dataclass
import darkdetect

from PySide6.QtCore import QObject, Signal


class GlobalSettings(QObject):
    """
    Global settings for both the GUI and entities
    """

    samplerate_signal = Signal(int)

    # samplerate: int = 44100  # default samplerate
    # appearance: str = darkdetect.theme()
    # update_needed = False

    def __init__(self, samplerate: int = 44100, appearance: str = darkdetect.theme()):
        super().__init__()
        self.__samplerate = samplerate
        self.__appearance = appearance

    @property
    def samplerate(self) -> int:
        return self.__samplerate

    @samplerate.setter
    def samplerate(self, new_value: int):
        assert new_value > 0
        self.__samplerate = new_value
        self.samplerate_signal.emit(self.__samplerate)

    def validate_samplerate(self, value) -> bool:
        if isinstance(value, str):
            try:
                value = int(value)
            except ValueError:
                return False
        return value > 0
