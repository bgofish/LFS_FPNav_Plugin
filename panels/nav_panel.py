"""FP Navigation panel."""

import lichtfeld as lf
from ..operators.nav_ops import STATE
from ..keymaps import BINDINGS, OP_KEY_LABEL, KEY_NAMES, _handle_event, _rebuild_op_key_label, _BASE
from .. import settings as _cfg



_LOC = {
    "fp_nav.set_floor":     "Set Floor to Eye Y",
    "fp_nav.move_forward":  "Forward",
    "fp_nav.move_backward": "Backward",
    "fp_nav.yaw_left":      "Turn Left",
    "fp_nav.yaw_right":     "Turn Right",
    "fp_nav.pitch_up":      "Look Up",
    "fp_nav.pitch_down":    "Look Down",
    "fp_nav.set_home":      "Set Home",
    "fp_nav.reset_home":    "Reset Home",
}

def register_loc():
    for key, val in _LOC.items():
        lf.ui.loc_set(key, val)


_capturing: str | None = None


class FPNavPanel(lf.ui.Panel):
    id    = "fp_navigation.panel"
    label = "FP Nav."
    space = lf.ui.PanelSpace.MAIN_PANEL_TAB
    order = 10

    def draw(self, ui) -> None:

        # ── Movement ───────────────────────────────────────────────────────
        changed, new_val = ui.drag_float("Stride (m)##stride", STATE.move_step, 0.01, 0.01, 10.0)
        if changed:
            STATE.move_step = new_val
            _cfg.save(BINDINGS, STATE)
        _op_row(ui, _BASE + "FPNavMoveForward",  "fp_nav.move_forward")
        ui.same_line()
        _op_row(ui, _BASE + "FPNavMoveBackward", "fp_nav.move_backward")

        ui.separator()

        # ── Turn ───────────────────────────────────────────────────────────
        changed, new_val = ui.drag_float("Turn (°)##turn", STATE.yaw_step, 0.1, 0.1, 45.0)
        if changed:
            STATE.yaw_step = new_val
            _cfg.save(BINDINGS, STATE)
        _op_row(ui, _BASE + "FPNavYawRight",  "fp_nav.yaw_left")
        ui.same_line()

        _op_row(ui, _BASE + "FPNavYawLeft",  "fp_nav.yaw_right")
        ui.separator()

        # ── Tilt ───────────────────────────────────────────────────────────
        changed, new_val = ui.drag_float("Tilt (°)##tilt", STATE.pitch_step, 0.1, 0.1, 45.0)
        if changed:
            STATE.pitch_step = new_val
            _cfg.save(BINDINGS, STATE)
        _op_row(ui, _BASE + "FPNavPitchUp",   "fp_nav.pitch_up")
        ui.same_line()
        _op_row(ui, _BASE + "FPNavPitchDown", "fp_nav.pitch_down")

        ui.separator()

        # ── Floor lock ─────────────────────────────────────────────────────
        ui.label(f"Floor Y: {STATE.floor_y:.3f}")
        ui.operator_(_BASE + "FPNavSetFloor", "fp_nav.set_floor")

        ui.separator()

        # ── Home ───────────────────────────────────────────────────────────
        ui.operator_(_BASE + "FPNavSetHome",   "fp_nav.set_home")
        ui.same_line()
        ui.operator_(_BASE + "FPNavResetHome", "fp_nav.reset_home")


def _op_short(op_id: str) -> str:
    return op_id.split(".")[-1].replace("FPNav", "")


def _op_row(ui, op_id: str, loc_key: str) -> None:
    global _capturing
    key_label = OP_KEY_LABEL.get(op_id, "?")
    ui.operator_(op_id, loc_key)
    ui.same_line()
    if ui.small_button(f"[{key_label}]##{op_id}"):
        _capturing = op_id
        _install_capture(op_id)


def _install_capture(op_id: str) -> None:
    global _capturing

    def _capture(event):
        global _capturing
        if event.type != lf.ui.ModalEventType.Key or event.action != 1:
            return False
        if event.over_gui:
            return False

        if event.key == 256:  # Esc — cancel
            _capturing = None
        else:
            # Remove any existing binding for this op
            for k in [k for k, v in BINDINGS.items() if v == op_id]:
                del BINDINGS[k]
                KEY_NAMES.pop(k, None)
            # Remove any existing binding for this key
            BINDINGS.pop(event.key, None)
            # Set new binding
            BINDINGS[event.key] = op_id
            label = chr(event.key) if 32 <= event.key < 127 else str(event.key)
            KEY_NAMES[event.key] = label
            _rebuild_op_key_label()
            _cfg.save(BINDINGS, STATE)
            _capturing = None

        lf.ui.set_modal_event_callback(_handle_event)
        return True

    lf.ui.set_modal_event_callback(_capture)
