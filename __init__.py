"""
fp_navigation — fly mode + ground lock for LichtFeld Studio.
"""

import lichtfeld as lf
from .panels.nav_panel import FPNavPanel, register_loc
from .operators.nav_ops import (
    FPNavYawLeft, FPNavYawRight,
    FPNavMoveForward, FPNavMoveBackward,
    FPNavPitchUp, FPNavPitchDown,
    FPNavSetFloor,
    FPNavSetHome, FPNavResetHome,
    FPNavToggleCoords,
)
from .keymaps import register_keymaps, unregister_keymaps

_OPERATORS = (
    FPNavYawLeft, FPNavYawRight,
    FPNavMoveForward, FPNavMoveBackward,
    FPNavPitchUp, FPNavPitchDown,
    FPNavSetFloor,
    FPNavSetHome, FPNavResetHome,
    FPNavToggleCoords,
)

def on_load():
    register_loc()

    # Try all known registration patterns
    for op in _OPERATORS:
        for method in ("register_operator", "register_class"):
            fn = getattr(lf, method, None) or getattr(lf.ui, method, None)
            if fn:
                try:
                    fn(op)
                    break
                except Exception:
                    pass

    try:
        lf.register_class(FPNavPanel)
    except Exception:
        pass

    register_keymaps()

    # Explicit load after keymaps so STATE values are confirmed in the log
    from . import settings as _cfg
    from .operators.nav_ops import STATE
    from .keymaps import BINDINGS
    data = _cfg.load()
    if data:
        _cfg.apply(data, BINDINGS, STATE)
        lf.log.info(f"fp_navigation: STATE after load — move_step={STATE.move_step} yaw_step={STATE.yaw_step} pitch_step={STATE.pitch_step} floor_y={STATE.floor_y}")
    else:
        lf.log.warn("fp_navigation: no settings loaded — using defaults")

    lf.log.info("fp_navigation: loaded — ← → ↑ ↓ Q E + floor lock")

    # Return operator classes — some plugin managers auto-register return value
    return list(_OPERATORS) + [FPNavPanel]


def on_unload():
    unregister_keymaps()

    for op in reversed(_OPERATORS):
        for method in ("unregister_operator", "unregister_class"):
            fn = getattr(lf, method, None) or getattr(lf.ui, method, None)
            if fn:
                try:
                    fn(op)
                    break
                except Exception:
                    pass

    try:
        lf.unregister_class(FPNavPanel)
    except Exception:
        pass

    lf.log.info("fp_navigation: unloaded")
