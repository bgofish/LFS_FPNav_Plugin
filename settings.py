"""
Persistent settings for fp_navigation.
Saves/loads keybindings and step sizes to a JSON file next to the plugin.
"""

import json
import pathlib
import lichtfeld as lf

_SETTINGS_PATH = pathlib.Path(__file__).resolve().parent / "FPN_settings.json"

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
    "move_step":    0.25,
    "yaw_step":     5.0,
    "pitch_step":   3.0,
    "floor_y":      0.0,
    "show_coords":  False,
    "home_eye":     None,
    "home_target":  None,
    "home_up":      None,
    "views":        [None] * 6,
}


def load() -> dict:
    """Load settings from JSON, falling back to defaults."""
    lf.log.info(f"fp_navigation: looking for settings at {_SETTINGS_PATH}")
    try:
        if _SETTINGS_PATH.exists():
            data = json.loads(_SETTINGS_PATH.read_text(encoding="utf-8"))
            if "bindings" in data:
                data["bindings"] = {int(k): v for k, v in data["bindings"].items()}
            lf.log.info(f"fp_navigation: loaded move_step={data.get('move_step')} yaw_step={data.get('yaw_step')} from {_SETTINGS_PATH}")
            return data
        else:
            lf.log.warn(f"fp_navigation: FPN_settings.json NOT FOUND at {_SETTINGS_PATH}")
    except Exception as e:
        lf.log.warn(f"fp_navigation: could not load settings: {e}")
    return {}


def save(bindings: dict, state) -> None:
    """Save current bindings and step values to JSON."""
    def _tup(v):
        return list(v) if v is not None else None

    data = {
        "bindings":     {str(k): v for k, v in bindings.items()},
        "move_step":    state.move_step,
        "yaw_step":     state.yaw_step,
        "pitch_step":   state.pitch_step,
        "floor_y":      state.floor_y,
        "show_coords":  state.show_coords,
        "home_eye":     _tup(state.home_eye),
        "home_target":  _tup(state.home_target),
        "home_up":      _tup(state.home_up),
        "views":        [
            [_tup(v[0]), _tup(v[1]), _tup(v[2])] if v else None
            for v in (state.views or [None]*6)
        ],
        "views_locked":  state.views_locked,
        "numpad_locked": state.numpad_locked,
        "numpad_views": {
            k: [_tup(v[0]), _tup(v[1]), _tup(v[2])] if v else None
            for k, v in (state.numpad_views or {}).items()
        },
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

    state.move_step   = data.get("move_step",   DEFAULT_STATE["move_step"])
    state.yaw_step    = data.get("yaw_step",    DEFAULT_STATE["yaw_step"])
    state.pitch_step  = data.get("pitch_step",  DEFAULT_STATE["pitch_step"])
    state.floor_y     = data.get("floor_y",     DEFAULT_STATE["floor_y"])
    state.show_coords = data.get("show_coords", DEFAULT_STATE["show_coords"])

    def _load_tup(v):
        return tuple(v) if v is not None else None

    state.home_eye    = _load_tup(data.get("home_eye"))
    state.home_target = _load_tup(data.get("home_target"))
    state.home_up     = _load_tup(data.get("home_up"))

    raw_views = data.get("views", [None]*6)
    state.views = []
    for slot in raw_views:
        if slot and slot[0] is not None:
            state.views.append((_load_tup(slot[0]), _load_tup(slot[1]), _load_tup(slot[2])))
        else:
            state.views.append(None)
    # Pad to 6 if file had fewer
    while len(state.views) < 6:
        state.views.append(None)

    state.views_locked  = data.get("views_locked",  False)
    state.numpad_locked = data.get("numpad_locked", False)

    # Numpad views
    from .operators.nav_ops import NUMPAD_SLOTS
    raw_nv = data.get("numpad_views", {})
    state.numpad_views = {}
    for slot in NUMPAD_SLOTS.values():
        raw = raw_nv.get(slot)
        if raw and raw[0] is not None:
            state.numpad_views[slot] = (_load_tup(raw[0]), _load_tup(raw[1]), _load_tup(raw[2]))
        else:
            state.numpad_views[slot] = None
