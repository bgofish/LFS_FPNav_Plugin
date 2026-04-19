"""
FP Navigation panel — renders in the right-hand sidebar as "FP Nav".

Layout
------
  ┌────────────────────────────────┐
  │  FP Navigation                 │
  ├────────────────────────────────┤
  │  [←]  Rotate Left              │
  │  [→]  Rotate Right             │
  │  [↑]  Move Forward             │
  │  [↓]  Move Backward            │
  ├────────────────────────────────┤
  │  Yaw step   [5.0°]             │
  │  Move step  [0.25]             │
  ├────────────────────────────────┤
  │  [Set Home]   [Reset to Home]  │
  └────────────────────────────────┘
"""

import lichtfeld as lf
from lfs_plugins.types import FloatProperty
from ..operators.nav_ops import STATE


class FPNavPanel(lf.ui.Panel):
    id = "fp_navigation.panel"
    label = "FP Nav"
    space = lf.ui.PanelSpace.SIDEBAR
    category = "Navigation"
    order = 10

    # Panel-level property definitions (displayed as editable fields)
    yaw_step: FloatProperty(
        name="Yaw step (°)",
        description="Degrees rotated per arrow-key press",
        default=5.0,
        min=0.1,
        max=45.0,
        update=lambda self, ctx: setattr(STATE, "yaw_step", self.yaw_step),
    )

    move_step: FloatProperty(
        name="Move step",
        description="World units moved per arrow-key press",
        default=0.25,
        min=0.001,
        max=10.0,
        update=lambda self, ctx: setattr(STATE, "move_step", self.move_step),
    )

    def draw(self, ui) -> None:
        # ── Key controls ───────────────────────────────────────────────────
        ui.label("Arrow key controls")
        ui.separator()

        row = ui.row()
        row.operator("fp_navigation.yaw_left",     label="← Left")
        row.operator("fp_navigation.yaw_right",    label="→ Right")

        row2 = ui.row()
        row2.operator("fp_navigation.move_forward",  label="↑ Forward")
        row2.operator("fp_navigation.move_backward", label="↓ Backward")

        ui.separator()

        # ── Step size settings ─────────────────────────────────────────────
        ui.label("Step sizes")
        ui.prop(self, "yaw_step")
        ui.prop(self, "move_step")

        ui.separator()

        # ── Home position ──────────────────────────────────────────────────
        ui.label("Home position")
        row3 = ui.row()
        row3.operator("fp_navigation.set_home",   label="Set Home")
        row3.operator(
            "fp_navigation.reset_home",
            label="Reset",
            enabled=STATE.home_pose is not None,
        )
