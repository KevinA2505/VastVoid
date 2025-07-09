import json
from pathlib import Path
import pygame

# Default key bindings for player actions
DEFAULT_BINDINGS: dict[str, int] = {
    "move_up": pygame.K_w,
    "move_down": pygame.K_s,
    "move_left": pygame.K_a,
    "move_right": pygame.K_d,
    "boost": pygame.K_LSHIFT,
    "open_inventory": pygame.K_i,
    "open_weapons": pygame.K_f,
    "open_artifacts": pygame.K_g,
    "open_market": pygame.K_m,
    "dock": pygame.K_c,
    "load_ship": pygame.K_l,
    "fire": pygame.K_SPACE,
    "cancel": pygame.K_ESCAPE,
    "toggle_boat": pygame.K_b,
    "camera_left": pygame.K_LEFT,
    "camera_right": pygame.K_RIGHT,
    "camera_up": pygame.K_UP,
    "camera_down": pygame.K_DOWN,
}

# Active bindings used by the game
BINDINGS: dict[str, int] = DEFAULT_BINDINGS.copy()

_FILE_PATH = Path(__file__).resolve().parent.parent / "saves" / "controls.json"


def load_bindings() -> None:
    """Load bindings from ``saves/controls.json`` if present."""
    global BINDINGS
    if _FILE_PATH.exists():
        try:
            data = json.loads(_FILE_PATH.read_text())
        except Exception:
            return
        for action, name in data.items():
            try:
                BINDINGS[action] = pygame.key.key_code(name)
            except Exception:
                BINDINGS[action] = DEFAULT_BINDINGS.get(action, 0)
    else:
        BINDINGS = DEFAULT_BINDINGS.copy()


def save_bindings() -> None:
    """Save the current bindings to ``saves/controls.json``."""
    data = {action: pygame.key.name(code) for action, code in BINDINGS.items()}
    _FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    _FILE_PATH.write_text(json.dumps(data, indent=2))


def get_key(action: str) -> int:
    """Return the key code mapped to ``action``."""
    return BINDINGS.get(action, 0)


def set_key(action: str, keycode: int) -> None:
    """Update the key code for ``action``."""
    BINDINGS[action] = keycode
