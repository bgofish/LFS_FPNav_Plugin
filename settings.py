"""
Persistent settings for fp_navigation.
Saves/loads keybindings and step sizes to a JSON file next to the plugin.
"""

import json
import pathlib
import lichtfeld as lf

_SETTINGS_PATH = pathlib.Path(__file__).parent / "settings.json"

# Default bindings use bare class names — keymaps.py prepends the correct base
DEFAULT_BINDINGS = {
    265: "FPNavMoveForward",
    264: "FPNavMoveBackward",
    263: "FPNavYawLeft",
    262: "FPNavYawRight",
    81:  "FPNavPitchUp",
    69:  "FPNavPitchDown",
}

DEFAULT_STATE = {
    "move_step":  0.25,
    "yaw_step":   5.0,
    "pitch_step": 3.0,
    "floor_y":    0.0,
}


def load() -> dict:
    """Load settings from JSON, falling back to defaults."""
    try:
        if _SETTINGS_PATH.exists():
            data = json.loads(_SETTINGS_PATH.read_text(encoding="utf-8"))
            if "bindings" in data:
                data["bindings"] = {int(k): v for k, v in data["bindings"].items()}
            lf.log.info(f"fp_navigation: settings loaded from {_SETTINGS_PATH}")
            return data
    except Exception as e:
        lf.log.warn(f"fp_navigation: could not load settings: {e}")
    return {}


def save(bindings: dict, state) -> None:
    """Save current bindings and step values to JSON."""
    data = {
        "bindings": {str(k): v for k, v in bindings.items()},
        "move_step":  state.move_step,
        "yaw_step":   state.yaw_step,
        "pitch_step": state.pitch_step,
        "floor_y":    state.floor_y,
    }
    try:
        _SETTINGS_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
        lf.log.info(f"fp_navigation: settings saved to {_SETTINGS_PATH}")
    except Exception as e:
        lf.log.warn(f"fp_navigation: could not save settings: {e}")


def apply(data: dict, bindings: dict, state) -> None:
    """Apply loaded data onto live bindings dict and STATE object."""
    if "bindings" in data:
        bindings.clear()
        bindings.update(data["bindings"])
    # Note: if no bindings in data, keymaps.py will fill in the correct defaults

    state.move_step  = data.get("move_step",  DEFAULT_STATE["move_step"])
    state.yaw_step   = data.get("yaw_step",   DEFAULT_STATE["yaw_step"])
    state.pitch_step = data.get("pitch_step", DEFAULT_STATE["pitch_step"])
    state.floor_y    = data.get("floor_y",    DEFAULT_STATE["floor_y"])
