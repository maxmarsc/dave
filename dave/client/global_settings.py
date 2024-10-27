from dataclasses import dataclass


@dataclass
class GlobalSettings:
    samplerate: int = 44100
    appearance: str = "System"
    update_needed = False

    def validate_samplerate(self, value) -> bool:
        if isinstance(value, str):
            try:
                value = int(value)
            except ValueError:
                return False
        return value > 0
