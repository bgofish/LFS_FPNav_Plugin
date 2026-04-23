"""FP Navigation panel — RML-driven with collapsible coordinate display."""

from pathlib import Path
import subprocess

import lichtfeld as lf
from ..operators.nav_ops import STATE, _do_stride, _do_yaw, _do_pitch
from ..keymaps import BINDINGS, OP_KEY_LABEL, _rebuild_op_key_label, _BASE
from .. import settings as _cfg

_SETTINGS_PATH = Path(__file__).resolve().parent.parent / "FPN_settings.json"


# ── Localisation strings ────────────────────────────────────────────────────

_LOC = {
    "fp_nav.set_floor":     "Set Floor to Eye Y",
    "fp_nav.move_forward":  "Forward",
    "fp_nav.move_backward": "Backward",
    "fp_nav.yaw_left":      "Turn to Right",
    "fp_nav.yaw_right":     "Turn to Left",
    "fp_nav.pitch_up":      "Look Up",
    "fp_nav.pitch_down":    "Look Down",
    "fp_nav.set_home":      "Set Home",
    "fp_nav.reset_home":    "Goto Home",
    "fp_nav.toggle_coords": "Toggle Coord Display",
}

def register_loc():
    for key, val in _LOC.items():
        lf.ui.loc_set(key, val)


def _key_for(op_id: str) -> str:
    return OP_KEY_LABEL.get(op_id, "—")


# ── Panel ────────────────────────────────────────────────────────────────────

class FPNavPanel(lf.ui.Panel):
    id                 = "fp_navigation.panel"
    label              = "FP Nav."
    space              = lf.ui.PanelSpace.MAIN_PANEL_TAB
    order              = 10
    template           = str(Path(__file__).resolve().with_name("nav_panel.rml"))
    height_mode        = lf.ui.PanelHeightMode.CONTENT
    update_interval_ms = 100

    def __init__(self):
        self._coords_expanded    = True
        self._handle             = None
        self._settings_status    = ""
        self._settings_status_ok = True
        self._first_update       = True

    # ── Lifecycle ──────────────────────────────────────────────────────

    def on_bind_model(self, ctx):
        model = ctx.create_data_model("fp_nav_panel")

        # ── Coordinates (collapsible) ──────────────────────────────────
        model.bind_func("coords_expanded",      lambda: self._coords_expanded)
        model.bind_func("coords_section_label", lambda:
            "▼ Coordinates" if self._coords_expanded else "▶ Coordinates")
        model.bind_event("coords_toggle",       self._on_coords_toggle)

        model.bind_func("no_camera",  lambda: lf.get_camera() is None)
        model.bind_func("has_camera", lambda: lf.get_camera() is not None)

        model.bind_func("eye_x", lambda: f"{lf.get_camera().eye[0]:>10.4f}"    if lf.get_camera() else "—")
        model.bind_func("eye_y", lambda: f"{lf.get_camera().eye[1]:>10.4f}"    if lf.get_camera() else "—")
        model.bind_func("eye_z", lambda: f"{lf.get_camera().eye[2]:>10.4f}"    if lf.get_camera() else "—")
        model.bind_func("tgt_x", lambda: f"{lf.get_camera().target[0]:>10.4f}" if lf.get_camera() else "—")
        model.bind_func("tgt_y", lambda: f"{lf.get_camera().target[1]:>10.4f}" if lf.get_camera() else "—")
        model.bind_func("tgt_z", lambda: f"{lf.get_camera().target[2]:>10.4f}" if lf.get_camera() else "—")

        # ── Step sliders ───────────────────────────────────────────────
        model.bind("move_step_str",
                   lambda: f"{STATE.move_step:.2f}",
                   lambda v: self._set_float(v, "move_step", 0.01, 10.0))
        model.bind_func("move_step_min", lambda: "0.01")
        model.bind_func("move_step_max", lambda: "10.0")
        model.bind_func("move_step_inc", lambda: "0.01")

        model.bind("yaw_step_str",
                   lambda: f"{STATE.yaw_step:.1f}",
                   lambda v: self._set_float(v, "yaw_step", 0.1, 45.0))
        model.bind_func("yaw_step_min", lambda: "0.1")
        model.bind_func("yaw_step_max", lambda: "45.0")
        model.bind_func("yaw_step_inc", lambda: "0.1")

        model.bind("pitch_step_str",
                   lambda: f"{STATE.pitch_step:.1f}",
                   lambda v: self._set_float(v, "pitch_step", 0.1, 45.0))
        model.bind_func("pitch_step_min", lambda: "0.1")
        model.bind_func("pitch_step_max", lambda: "45.0")
        model.bind_func("pitch_step_inc", lambda: "0.1")

        model.bind_func("floor_y_str", lambda: f"{STATE.floor_y:.3f}")

        # ── Key label displays (read-only) ─────────────────────────────
        model.bind_func("key_move_forward",  lambda: _key_for(_BASE + "FPNavMoveForward"))
        model.bind_func("key_move_backward", lambda: _key_for(_BASE + "FPNavMoveBackward"))
        model.bind_func("key_yaw_right",     lambda: _key_for(_BASE + "FPNavYawRight"))
        model.bind_func("key_yaw_left",      lambda: _key_for(_BASE + "FPNavYawLeft"))
        model.bind_func("key_pitch_up",      lambda: _key_for(_BASE + "FPNavPitchUp"))
        model.bind_func("key_pitch_down",    lambda: _key_for(_BASE + "FPNavPitchDown"))

        # ── Operator buttons ───────────────────────────────────────────
        model.bind_event("op_move_forward",  self._on_op_move_forward)
        model.bind_event("op_move_backward", self._on_op_move_backward)
        model.bind_event("op_yaw_right",     self._on_op_yaw_right)
        model.bind_event("op_yaw_left",      self._on_op_yaw_left)
        model.bind_event("op_pitch_up",      self._on_op_pitch_up)
        model.bind_event("op_pitch_down",    self._on_op_pitch_down)
        model.bind_event("op_set_floor",     self._on_op_set_floor)
        model.bind_event("op_set_home",      self._on_op_set_home)
        model.bind_event("op_reset_home",    self._on_op_reset_home)

        # ── Favourite views V1–V6 ──────────────────────────────────────
        for i in range(6):
            idx = i  # capture
            model.bind_event(f"op_set_v{idx+1}",
                lambda h, e, a, i=idx: self._on_set_view(i))
            model.bind_event(f"op_goto_v{idx+1}",
                lambda h, e, a, i=idx: self._on_goto_view(i))
            model.bind_func(f"v{idx+1}_label",
                lambda i=idx: f"V{i+1} ✓" if STATE.views and STATE.views[i] else f"V{i+1}")

        # ── Settings ───────────────────────────────────────────────────
        model.bind_event("do_save_settings", self._on_save_settings)
        model.bind_event("do_load_settings", self._on_load_settings)
        model.bind_event("do_open_settings", self._on_open_settings)
        model.bind_func("settings_status",       lambda: self._settings_status)
        model.bind_func("settings_status_class", lambda:
            "section-label" if self._settings_status_ok else "text-muted")

        self._handle = model.get_handle()
        self._first_update = True   # belt-and-suspenders: also dirty on first on_update
        # Dirty all fields immediately so sliders read STATE (already loaded) not defaults
        self._dirty_all()

    def on_update(self, doc):
        if self._first_update:
            self._first_update = False
            self._dirty_all()   # push correct STATE values to all sliders/labels
            return True
        if self._coords_expanded:
            self._dirty("eye_x", "eye_y", "eye_z",
                        "tgt_x", "tgt_y", "tgt_z",
                        "no_camera", "has_camera")
            return True
        return False

    def on_unmount(self, doc):
        doc.remove_data_model("fp_nav_panel")
        self._handle = None

    # ── Dirty helpers ──────────────────────────────────────────────────

    def _dirty(self, *fields):
        if not self._handle:
            return
        for f in fields:
            self._handle.dirty(f)

    def _dirty_all(self):
        self._dirty(
            "coords_expanded", "coords_section_label",
            "no_camera", "has_camera",
            "eye_x", "eye_y", "eye_z", "tgt_x", "tgt_y", "tgt_z",
            "move_step_str", "yaw_step_str", "pitch_step_str", "floor_y_str",
            "key_move_forward", "key_move_backward",
            "key_yaw_right", "key_yaw_left",
            "key_pitch_up", "key_pitch_down",
            "settings_status", "settings_status_class",
            *[f"v{i+1}_label" for i in range(6)],
        )

    # ── Internal ───────────────────────────────────────────────────────

    def _set_float(self, value_str, attr: str, lo: float, hi: float):
        try:
            v = max(lo, min(hi, float(value_str)))
            setattr(STATE, attr, v)
        except (ValueError, TypeError):
            pass

    def _set_status(self, msg: str, ok: bool = True):
        self._settings_status    = msg
        self._settings_status_ok = ok
        self._dirty("settings_status", "settings_status_class")

    def _open_in_editor(self, path: Path) -> str:
        """Open path in Notepad++ or fall back to Notepad."""
        npp_candidates = [
            r"C:\Program Files\Notepad++\notepad++.exe",
            r"C:\Program Files (x86)\Notepad++\notepad++.exe",
        ]
        npp = next((p for p in npp_candidates if Path(p).exists()), None)
        if npp:
            subprocess.Popen([npp, str(path)])
            return f"Opened in Notepad++."
        else:
            subprocess.Popen(["notepad.exe", str(path)])
            return "Notepad++ not found — opened in Notepad."

    # ── Coords toggle ──────────────────────────────────────────────────

    def _on_coords_toggle(self, handle, event, args):
        self._coords_expanded = not self._coords_expanded
        self._dirty("coords_expanded", "coords_section_label")

    # ── Movement / turn / tilt — call helpers directly so floor_y_str
    #    and coords update immediately without waiting for next poll ────

    def _on_op_move_forward(self,  h, e, a): _do_stride( STATE.move_step)
    def _on_op_move_backward(self, h, e, a): _do_stride(-STATE.move_step)
    def _on_op_yaw_right(self,     h, e, a): _do_yaw( STATE.yaw_step)
    def _on_op_yaw_left(self,      h, e, a): _do_yaw(-STATE.yaw_step)
    def _on_op_pitch_up(self,      h, e, a): _do_pitch( STATE.pitch_step)
    def _on_op_pitch_down(self,    h, e, a): _do_pitch(-STATE.pitch_step)

    def _on_op_set_floor(self, h, e, a):
        cam = lf.get_camera()
        if cam is None:
            return
        STATE.floor_y = cam.eye[1]
        lf.log.info(f"fp_navigation: floor set to Y={STATE.floor_y:.3f}")
        self._dirty("floor_y_str")

    def _on_op_set_home(self, h, e, a):
        cam = lf.get_camera()
        if cam is None:
            return
        STATE.home_eye    = cam.eye
        STATE.home_target = cam.target
        STATE.home_up     = cam.up
        lf.log.info("fp_navigation: home saved")

    def _on_op_reset_home(self, h, e, a):
        if STATE.home_eye is None:
            return
        lf.set_camera(STATE.home_eye, STATE.home_target, STATE.home_up)

    # ── Favourite view handlers ───────────────────────────────────────

    def _on_set_view(self, idx: int):
        cam = lf.get_camera()
        if cam is None:
            return
        STATE.views[idx] = (cam.eye, cam.target, cam.up)
        _cfg.save(BINDINGS, STATE)
        lf.log.info(f"fp_navigation: V{idx+1} saved")
        self._dirty(f"v{idx+1}_label")

    def _on_goto_view(self, idx: int):
        if not STATE.views or STATE.views[idx] is None:
            return
        eye, target, up = STATE.views[idx]
        lf.set_camera(eye, target, up)

    # ── Settings handlers ──────────────────────────────────────────────

    def _on_save_settings(self, handle, event, args):
        try:
            _cfg.save(BINDINGS, STATE)
            self._set_status("Settings saved.")
        except Exception as e:
            self._set_status(f"Save failed: {e}", ok=False)

    def _on_load_settings(self, handle, event, args):
        try:
            from ..keymaps import KEY_NAMES, _remap_bindings
            data = _cfg.load()
            if "bindings" in data:
                data["bindings"] = _remap_bindings(data["bindings"])
            _cfg.apply(data, BINDINGS, STATE)
            _rebuild_op_key_label()
            self._dirty_all()
            self._set_status("Settings loaded.")
        except Exception as e:
            self._set_status(f"Load failed: {e}", ok=False)

    def _on_open_settings(self, handle, event, args):
        try:
            if not _SETTINGS_PATH.exists():
                _cfg.save(BINDINGS, STATE)
            msg = self._open_in_editor(_SETTINGS_PATH)
            self._set_status(msg)
        except Exception as e:
            self._set_status(f"Could not open: {e}", ok=False)
