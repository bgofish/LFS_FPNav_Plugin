"""
fp_navigation — First-person ← / → arrow-key navigation plugin for LichtFeld Studio.

Adds a side-panel (FP Nav) with:
  ←   Rotate camera left  (yaw)
  →   Rotate camera right (yaw)
  ↑   Move forward along view axis
  ↓   Move backward along view axis
  R   Reset to home position

Speed and step-size are configurable from the panel.
All operators are also accessible via Edit → Operator Search.
"""

import lichtfeld as lf
from .panels.nav_panel import FPNavPanel
from .operators.nav_ops import (
    FPNavYawLeft,
    FPNavYawRight,
    FPNavMoveForward,
    FPNavMoveBackward,
    FPNavResetHome,
    FPNavSetHome,
)
from .keymaps import register_keymaps, unregister_keymaps


def on_load() -> None:
    """Called by LichtFeld Studio when the plugin is loaded."""
    lf.ui.register_panel(FPNavPanel)

    lf.operators.register(FPNavYawLeft)
    lf.operators.register(FPNavYawRight)
    lf.operators.register(FPNavMoveForward)
    lf.operators.register(FPNavMoveBackward)
    lf.operators.register(FPNavResetHome)
    lf.operators.register(FPNavSetHome)

    register_keymaps()
    lf.log.info("fp_navigation: loaded — ← → ↑ ↓ arrow keys active")


def on_unload() -> None:
    """Called by LichtFeld Studio when the plugin is unloaded."""
    unregister_keymaps()

    lf.operators.unregister(FPNavSetHome)
    lf.operators.unregister(FPNavResetHome)
    lf.operators.unregister(FPNavMoveBackward)
    lf.operators.unregister(FPNavMoveForward)
    lf.operators.unregister(FPNavYawRight)
    lf.operators.unregister(FPNavYawLeft)

    lf.ui.unregister_panel(FPNavPanel)
    lf.log.info("fp_navigation: unloaded")
