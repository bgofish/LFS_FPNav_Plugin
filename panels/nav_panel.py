"""
FP Walk Navigation panel — sidebar category "Navigation", label "FP Walk".
"""

import lichtfeld as lf
from lfs_plugins.props import PropertyGroup, FloatProperty
from ..operators.nav_ops import STATE


class FPWalkSettings(PropertyGroup):
    eye_height: FloatProperty(
        name="Eye height",
        description="Camera Y position locked during walk (world units)",
        default=1.65,
        min=0.0,
        max=50.0,
    )
    yaw_step: FloatProperty(
        name="Turn step (°)",
        description="Degrees per ← / → key press",
        default=5.0,
        min=0.1,
        max=45.0,
    )
    pitch_step: FloatProperty(
        name="Tilt step (°)",
        description="Degrees per Q / E key press",
        default=3.0,
        min=0.1,
        max=30.0,
    )
    move_step: FloatProperty(
        name="Stride step",
        description="World units per ↑ / ↓ key press",
        default=0.25,
        min=0.001,
        max=10.0,
    )


class FPNavPanel(lf.ui.Panel):
    id    = "fp_navigation.panel"
    label = "FP Walk"
    space = lf.ui.PanelSpace.MAIN_PANEL_TAB
    order = 10

    def draw(self, ui) -> None:
        s = FPWalkSettings.get_instance()

        # Sync settings → STATE every redraw
        STATE.eye_height  = s.eye_height
        STATE.yaw_step    = s.yaw_step
        STATE.pitch_step  = s.pitch_step
        STATE.move_step   = s.move_step

        # ── Eye height ─────────────────────────────────────────────────────
        ui.label("Eye height")
        ui.prop(s, "eye_height")
        ui.operator("fp_navigation.apply_height", label="Snap Camera to Height")

        ui.separator()

        # ── Movement ───────────────────────────────────────────────────────
        ui.label("Move  (↑ ↓)")
        ui.prop(s, "move_step")
        row = ui.row()
        row.operator("fp_navigation.move_forward",  label="↑ Forward")
        row.operator("fp_navigation.move_backward", label="↓ Backward")

        ui.separator()

        # ── Turn ───────────────────────────────────────────────────────────
        ui.label("Turn  (← →)")
        ui.prop(s, "yaw_step")
        row2 = ui.row()
        row2.operator("fp_navigation.yaw_left",  label="← Left")
        row2.operator("fp_navigation.yaw_right", label="→ Right")

        ui.separator()

        # ── Tilt ───────────────────────────────────────────────────────────
        ui.label("Tilt head  (Q / E)")
        ui.prop(s, "pitch_step")
        row3 = ui.row()
        row3.operator("fp_navigation.pitch_up",   label="Q  Look Up")
        row3.operator("fp_navigation.pitch_down", label="E  Look Down")

        ui.separator()

        # ── Home ───────────────────────────────────────────────────────────
        ui.label("Home position")
        row4 = ui.row()
        row4.operator("fp_navigation.set_home",  label="Set Home")
        row4.operator(
            "fp_navigation.reset_home",
            label="Reset",
            enabled=STATE.home_pose is not None,
        )
