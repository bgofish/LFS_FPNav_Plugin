"""Keymap bindings for fp_navigation walk mode via modal event callback."""

import lichtfeld as lf
from . import settings as _cfg

_BASE = "lfs_plugins.fp_navigation.operators.nav_ops."

# Live bindings dict — mutated by rebind UI and persisted to JSON
BINDINGS: dict[int, str] = dict(_cfg.DEFAULT_BINDINGS)

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
    # Load saved settings
    from .operators.nav_ops import STATE
    data = _cfg.load()
    _cfg.apply(data, BINDINGS, STATE)
    _rebuild_op_key_label()

    try:
        lf.ui.set_modal_event_callback(_handle_event)
        _registered = True
        lf.log.info("fp_navigation: modal event callback registered")
    except Exception as e:
        lf.log.warn(f"fp_navigation: could not register event callback: {e}")


def unregister_keymaps() -> None:
    global _registered
    if _registered:
        # Save on unload too
        from .operators.nav_ops import STATE
        _cfg.save(BINDINGS, STATE)
        try:
            lf.ui.set_modal_event_callback(lambda e: False)
        except Exception as e:
            lf.log.warn(f"fp_navigation: could not unregister event callback: {e}")
        _registered = False
