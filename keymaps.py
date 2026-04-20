"""Keymap bindings for fp_navigation walk mode via modal event callback."""

import lichtfeld as lf
from . import settings as _cfg

# Derive the operator base path dynamically from this module's package name.
# e.g. if installed as "fp_navigation" -> "lfs_plugins.fp_navigation.operators.nav_ops."
#      if installed as "LFS_FPNav_Plugin-main" -> "lfs_plugins.LFS_FPNav_Plugin-main.operators.nav_ops."
_PKG = __name__.rsplit(".", 1)[0]  # e.g. "lfs_plugins.fp_navigation"
_BASE = f"{_PKG}.operators.nav_ops."

def _make_default_bindings() -> dict[int, str]:
    return {
        265: _BASE + "FPNavMoveForward",
        264: _BASE + "FPNavMoveBackward",
        263: _BASE + "FPNavYawLeft",
        262: _BASE + "FPNavYawRight",
        81:  _BASE + "FPNavPitchUp",
        69:  _BASE + "FPNavPitchDown",
    }

# Live bindings dict — mutated by rebind UI and persisted to JSON
BINDINGS: dict[int, str] = _make_default_bindings()

# Human-readable key names for display
KEY_NAMES: dict[int, str] = {
    265: "↑", 264: "↓", 263: "←", 262: "→",
    81: "Q", 69: "E",
}

# Reverse map: operator id -> key display label
OP_KEY_LABEL: dict[str, str] = {v: KEY_NAMES[k] for k, v in BINDINGS.items()}

_registered = False


def _rebuild_op_key_label():
    OP_KEY_LABEL.clear()
    for k, v in BINDINGS.items():
        OP_KEY_LABEL[v] = KEY_NAMES.get(k, str(k))


def _remap_bindings(loaded: dict[int, str]) -> dict[int, str]:
    """Fix up operator IDs from JSON in case the plugin folder was renamed.
    Strips whatever base path was saved and applies the current _BASE."""
    remapped = {}
    for k, op_id in loaded.items():
        # Extract just the class name (e.g. "FPNavMoveForward")
        class_name = op_id.split(".")[-1]
        remapped[k] = _BASE + class_name
    return remapped


def _handle_event(event) -> bool:
    if event.type != lf.ui.ModalEventType.Key:
        return False
    if event.action != 1:
        return False
    if event.over_gui:
        return False
    op_id = BINDINGS.get(event.key)
    if op_id:
        lf.ui.ops.invoke(op_id)
        return True
    return False


def register_keymaps() -> None:
    global _registered
    from .operators.nav_ops import STATE
    data = _cfg.load()
    # Remap any saved bindings to use the current install path
    if "bindings" in data:
        data["bindings"] = _remap_bindings(data["bindings"])
    _cfg.apply(data, BINDINGS, STATE)
    # If apply gave us defaults, replace with correctly-pathed defaults
    if not BINDINGS:
        BINDINGS.update(_make_default_bindings())
    _rebuild_op_key_label()

    try:
        lf.ui.set_modal_event_callback(_handle_event)
        _registered = True
        lf.log.info(f"fp_navigation: loaded, base={_BASE}")
    except Exception as e:
        lf.log.warn(f"fp_navigation: could not register event callback: {e}")


def unregister_keymaps() -> None:
    global _registered
    if _registered:
        from .operators.nav_ops import STATE
        _cfg.save(BINDINGS, STATE)
        try:
            lf.ui.set_modal_event_callback(lambda e: False)
        except Exception as e:
            lf.log.warn(f"fp_navigation: could not unregister event callback: {e}")
        _registered = False
