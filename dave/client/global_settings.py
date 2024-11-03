from dataclasses import dataclass


@dataclass
class GlobalSettings:
    """
    Global settings for both the GUI and containers
    """

    samplerate: int = 44100  # default samplerate
    appearance: str = "System"
    update_needed = False

    def validate_samplerate(self, value) -> bool:
        if isinstance(value, str):
            try:
                value = int(value)
            except ValueError:
                return False
        return value > 0
