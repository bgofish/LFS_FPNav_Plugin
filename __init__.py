"""
fp_navigation — First-person walk mode plugin for LichtFeld Studio.

Key bindings (active when viewport has focus)
  ←  /  →    Turn left / right (yaw)
  ↑  /  ↓    Stride forward / backward (horizontal, height-locked)
  Q           Tilt head up (pitch)
  E           Tilt head down (pitch)
"""

import lichtfeld as lf
from .panels.nav_panel import FPNavPanel, FPWalkSettings
from .operators.nav_ops import (
    FPNavYawLeft, FPNavYawRight,
    FPNavMoveForward, FPNavMoveBackward,
    FPNavPitchUp, FPNavPitchDown,
    FPNavApplyHeight,
    FPNavSetHome, FPNavResetHome,
)
from .keymaps import register_keymaps, unregister_keymaps


def on_load() -> None:
    lf.ui.register_panel(FPNavPanel)

    for op in (
        FPNavYawLeft, FPNavYawRight,
        FPNavMoveForward, FPNavMoveBackward,
        FPNavPitchUp, FPNavPitchDown,
        FPNavApplyHeight,
        FPNavSetHome, FPNavResetHome,
    ):
        lf.operators.register(op)

    register_keymaps()
    lf.log.info("fp_navigation: walk mode loaded — ← → ↑ ↓ Q E")


def on_unload() -> None:
    unregister_keymaps()

    for op in (
        FPNavResetHome, FPNavSetHome,
        FPNavApplyHeight,
        FPNavPitchDown, FPNavPitchUp,
        FPNavMoveBackward, FPNavMoveForward,
        FPNavYawRight, FPNavYawLeft,
    ):
        lf.operators.unregister(op)

    lf.ui.unregister_panel(FPNavPanel)
    lf.log.info("fp_navigation: unloaded")
