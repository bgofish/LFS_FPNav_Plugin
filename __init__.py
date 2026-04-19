"""
fp_navigation — fly mode + ground lock for LichtFeld Studio.

Key bindings (viewport focus required)
  ←  /  →    Turn left / right
  ↑  /  ↓    Stride forward / backward (floor-clamped)
  Q           Tilt head up
  E           Tilt head down
"""

import lichtfeld as lf
from .panels.nav_panel import FPNavPanel
from .operators.nav_ops import (
    FPNavYawLeft, FPNavYawRight,
    FPNavMoveForward, FPNavMoveBackward,
    FPNavPitchUp, FPNavPitchDown,
    FPNavSetFloor,
    FPNavSetHome, FPNavResetHome,
)
from .keymaps import register_keymaps, unregister_keymaps


def on_load() -> None:
    lf.ui.register_panel(FPNavPanel)

    for op in (
        FPNavYawLeft, FPNavYawRight,
        FPNavMoveForward, FPNavMoveBackward,
        FPNavPitchUp, FPNavPitchDown,
        FPNavSetFloor,
        FPNavSetHome, FPNavResetHome,
    ):
        lf.operators.register(op)

    register_keymaps()
    lf.log.info("fp_navigation: loaded — ← → ↑ ↓ Q E + floor lock")


def on_unload() -> None:
    unregister_keymaps()

    for op in (
        FPNavResetHome, FPNavSetHome,
        FPNavSetFloor,
        FPNavPitchDown, FPNavPitchUp,
        FPNavMoveBackward, FPNavMoveForward,
        FPNavYawRight, FPNavYawLeft,
    ):
        lf.operators.unregister(op)

    lf.ui.unregister_panel(FPNavPanel)
    lf.log.info("fp_navigation: unloaded")
