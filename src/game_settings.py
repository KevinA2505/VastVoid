import json
from pathlib import Path

# Default settings
DEFAULT_SETTINGS = {
    "zoom_with_wheel": True,
}

SETTINGS = DEFAULT_SETTINGS.copy()

_FILE_PATH = Path(__file__).resolve().parent.parent / "saves" / "settings.json"


def load_settings() -> None:
    """Load settings from ``saves/settings.json`` if present."""
    global SETTINGS
    if _FILE_PATH.exists():
        try:
            data = json.loads(_FILE_PATH.read_text())
        except Exception:
            return
        for name, value in data.items():
            if name in DEFAULT_SETTINGS:
                SETTINGS[name] = bool(value)
    else:
        SETTINGS = DEFAULT_SETTINGS.copy()


def save_settings() -> None:
    """Persist settings to ``saves/settings.json``."""
    _FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    _FILE_PATH.write_text(json.dumps(SETTINGS, indent=2))


def get_setting(name: str):
    """Return the current value of ``name`` from SETTINGS."""
    return SETTINGS.get(name, DEFAULT_SETTINGS.get(name))


def set_setting(name: str, value) -> None:
    """Update ``name`` with ``value``."""
    SETTINGS[name] = value
