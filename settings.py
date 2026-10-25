"""Validated, per-user SoundKeeper preferences (no audio or UI dependencies)."""

import json
import os
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Union

# Source defaults: edit these before building a customized executable.
# Valid JSON preferences override these values; missing/invalid fields use them.
# Automatic: "auto". Manual: an unquoted integer, e.g. 44100 or 48000.
# Manual rates must be between 8000 and 192000 Hz and supported by the device.
DEFAULT_SAMPLE_RATE = "auto"
DEFAULT_DURATION = 1.0  # 0.001 to 10 seconds
DEFAULT_INTERVAL = 55  # 0.1 to 86400 seconds, measured after playback
DEFAULT_AMPLITUDE = 0.0001  # 0 to 1; larger values may be audible
# "auto" follows Windows UI preferences, falling back to English.
# Manual language codes: "en", "zh-Hans", "fr", "ru", "es", "ar".
DEFAULT_LANGUAGE = "auto"

WAIT_OPTIONS = (30, 55, 295, 595, 895)
DURATION_OPTIONS = (0.01, 0.1, 1.0)
LANGUAGE_NAMES = {
    "en": "English",
    "zh-Hans": "简体中文",
    "fr": "Français",
    "ru": "Русский",
    "es": "Español",
    "ar": "العربية",
}


@dataclass(frozen=True)
class Settings:
    wait_seconds: float = DEFAULT_INTERVAL
    duration_seconds: float = DEFAULT_DURATION
    amplitude: float = DEFAULT_AMPLITUDE
    sample_rate: Union[str, int] = DEFAULT_SAMPLE_RATE
    language: str = DEFAULT_LANGUAGE


def valid_number(value, minimum, maximum):
    """Reject booleans, non-finite numbers, and excessive audio allocations."""
    return type(value) in (int, float) and minimum <= value <= maximum


def config_path():
    """Keep preferences independent of the executable's location."""
    appdata = os.environ.get("APPDATA")
    base = Path(appdata) if appdata else Path.home() / "AppData" / "Roaming"
    return base / "SoundKeeper" / "config.json"


def load_settings(path):
    """Use defaults for missing, damaged, unsupported, or invalid settings."""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return Settings()
    if not isinstance(data, dict):
        return Settings()

    defaults = Settings()
    wait = data.get("wait_seconds")
    duration = data.get("duration_seconds")
    amplitude = data.get("amplitude")
    sample_rate = data.get("sample_rate")
    language = data.get("language")
    return Settings(
        wait_seconds=wait if valid_number(wait, 0.1, 86400) else defaults.wait_seconds,
        duration_seconds=(
            float(duration)
            if valid_number(duration, 0.001, 10)
            else defaults.duration_seconds
        ),
        amplitude=amplitude if valid_number(amplitude, 0, 1) else defaults.amplitude,
        sample_rate=sample_rate
        if sample_rate == "auto"
        or (type(sample_rate) is int and 8000 <= sample_rate <= 192000)
        else defaults.sample_rate,
        language=(
            language
            if isinstance(language, str) and language in ("auto", *LANGUAGE_NAMES)
            else defaults.language
        ),
    )


def save_settings(path, settings):
    """Replace the file atomically; never leave a partially written JSON file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent, suffix=".tmp", delete=False
        ) as stream:
            temporary = Path(stream.name)
            json.dump(asdict(settings), stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
