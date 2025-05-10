from dataclasses import dataclass
import darkdetect


@dataclass
class GlobalSettings:
    """
    Global settings for both the GUI and entities
    """

    samplerate: int = 44100  # default samplerate
    appearance: str = darkdetect.theme()
    update_needed = False

    def validate_samplerate(self, value) -> bool:
        if isinstance(value, str):
            try:
                value = int(value)
            except ValueError:
                return False
        return value > 0
