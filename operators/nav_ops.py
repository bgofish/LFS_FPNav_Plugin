"""
Walk-mode navigation operators for fp_navigation.

Walk mode behaviour
-------------------
- Eye height is locked to STATE.eye_height (world Y).  Moving forward/back
  slides the camera horizontally — Y is never changed by movement.
- ← / →  yaw  around world Y (turn head left/right).
- ↑ / ↓  translate along the horizontal projection of the view direction
          (stride across the floor, ignoring current pitch).
- Q / E  pitch the camera up / down around its local X axis (tilt head).
          Pitch is clamped to ±STATE.pitch_limit_deg so you cannot flip.

Camera pose convention (LichtFeld Studio)
------------------------------------------
Flat list of 16 floats, column-major 4×4, OpenGL convention:
  col 0  = right  vector  [0,1,2]
  col 1  = up     vector  [4,5,6]
  col 2  = -fwd   vector  [8,9,10]   (camera looks down -Z)
  col 3  = pos    [12,13,14], w=1
"""

from __future__ import annotations
import math
import lichtfeld as lf
from lfs_plugins.types import Operator


# ---------------------------------------------------------------------------
# Shared plugin state
# ---------------------------------------------------------------------------

class _State:
    yaw_step: float        = 5.0    # degrees per key press (turn)
    pitch_step: float      = 3.0    # degrees per key press (tilt)
    move_step: float       = 0.25   # world units per key press
    eye_height: float      = 1.65   # world Y of the camera (metres)
    pitch_limit_deg: float = 80.0   # max absolute pitch angle
    home_pose: list | None = None


STATE = _State()


# ---------------------------------------------------------------------------
# Camera helper
# ---------------------------------------------------------------------------

def _get_cam():
    try:
        return lf.viewport.get_camera()
    except AttributeError:
        try:
            return lf.get_viewport_camera()
        except AttributeError:
            return None


# ---------------------------------------------------------------------------
# Math helpers  (column-major: pose[col*4 + row])
# ---------------------------------------------------------------------------

def _mat4_mul(a: list, b: list) -> list:
    out = [0.0] * 16
    for r in range(4):
        for c in range(4):
            v = 0.0
            for k in range(4):
                v += a[r + k * 4] * b[k + c * 4]
            out[r + c * 4] = v
    return out


def _rot_world_y(angle_rad: float) -> list:
    """Rotation matrix around world Y (yaw)."""
    c, s = math.cos(angle_rad), math.sin(angle_rad)
    return [
         c,  0.0,  s,  0.0,
        0.0,  1.0,  0.0, 0.0,
        -s,  0.0,  c,  0.0,
        0.0,  0.0,  0.0, 1.0,
    ]


def _rot_local_x(pose: list, angle_rad: float) -> list:
    """Post-multiply a local-X rotation (pitch in camera space)."""
    c, s = math.cos(angle_rad), math.sin(angle_rad)
    rx = [
        1.0,  0.0,  0.0, 0.0,
        0.0,    c,    s, 0.0,
        0.0,   -s,    c, 0.0,
        0.0,  0.0,  0.0, 1.0,
    ]
    return _mat4_mul(pose, rx)


def _current_pitch_rad(pose: list) -> float:
    """Current pitch: asin of the forward vector's Y component."""
    fwd_y = -pose[9]                          # forward = -col2; fwd_y = -pose[9]
    return math.asin(max(-1.0, min(1.0, fwd_y)))


# ---------------------------------------------------------------------------
# Walk-mode core operations
# ---------------------------------------------------------------------------

def _walk_yaw(cam, angle_deg: float) -> set:
    pose = list(cam.get_pose())
    tx, tz = pose[12], pose[14]
    new_pose = _mat4_mul(_rot_world_y(math.radians(angle_deg)), pose)
    new_pose[12] = tx
    new_pose[13] = STATE.eye_height
    new_pose[14] = tz
    cam.set_pose(new_pose)
    return {"FINISHED"}


def _walk_stride(cam, delta: float) -> set:
    """Horizontal stride — projects forward vector onto XZ, ignores pitch."""
    pose = list(cam.get_pose())
    fx, fz = -pose[8], -pose[10]
    length = math.sqrt(fx * fx + fz * fz)
    if length < 1e-6:
        return {"CANCELLED"}
    fx /= length
    fz /= length
    pose[12] += fx * delta
    pose[13]  = STATE.eye_height
    pose[14] += fz * delta
    cam.set_pose(pose)
    return {"FINISHED"}


def _walk_pitch(cam, angle_deg: float) -> set:
    """Tilt head up/down — clamped local-X rotation."""
    pose = list(cam.get_pose())
    angle_rad = math.radians(angle_deg)
    current = _current_pitch_rad(pose)
    limit   = math.radians(STATE.pitch_limit_deg)
    new_p   = current + angle_rad
    if new_p > limit:
        angle_rad = limit - current
    elif new_p < -limit:
        angle_rad = -limit - current
    if abs(angle_rad) < 1e-6:
        return {"FINISHED"}
    new_pose = _rot_local_x(pose, angle_rad)
    new_pose[12] = pose[12]
    new_pose[13] = STATE.eye_height
    new_pose[14] = pose[14]
    cam.set_pose(new_pose)
    return {"FINISHED"}


def apply_eye_height(cam) -> None:
    pose = list(cam.get_pose())
    pose[13] = STATE.eye_height
    cam.set_pose(pose)


# ---------------------------------------------------------------------------
# Operators
# ---------------------------------------------------------------------------

class FPNavYawLeft(Operator):
    id = "fp_navigation.yaw_left"
    label = "FP Walk: Turn Left"
    description = "Turn left (← key)"
    @classmethod
    def poll(cls, ctx): return _get_cam() is not None
    def execute(self, ctx):
        cam = _get_cam()
        return {"CANCELLED"} if cam is None else _walk_yaw(cam, -STATE.yaw_step)


class FPNavYawRight(Operator):
    id = "fp_navigation.yaw_right"
    label = "FP Walk: Turn Right"
    description = "Turn right (→ key)"
    @classmethod
    def poll(cls, ctx): return _get_cam() is not None
    def execute(self, ctx):
        cam = _get_cam()
        return {"CANCELLED"} if cam is None else _walk_yaw(cam, STATE.yaw_step)


class FPNavMoveForward(Operator):
    id = "fp_navigation.move_forward"
    label = "FP Walk: Move Forward"
    description = "Stride forward on the ground plane (↑ key)"
    @classmethod
    def poll(cls, ctx): return _get_cam() is not None
    def execute(self, ctx):
        cam = _get_cam()
        return {"CANCELLED"} if cam is None else _walk_stride(cam, STATE.move_step)


class FPNavMoveBackward(Operator):
    id = "fp_navigation.move_backward"
    label = "FP Walk: Move Backward"
    description = "Stride backward on the ground plane (↓ key)"
    @classmethod
    def poll(cls, ctx): return _get_cam() is not None
    def execute(self, ctx):
        cam = _get_cam()
        return {"CANCELLED"} if cam is None else _walk_stride(cam, -STATE.move_step)


class FPNavPitchUp(Operator):
    id = "fp_navigation.pitch_up"
    label = "FP Walk: Look Up"
    description = "Tilt head upward (Q key)"
    @classmethod
    def poll(cls, ctx): return _get_cam() is not None
    def execute(self, ctx):
        cam = _get_cam()
        return {"CANCELLED"} if cam is None else _walk_pitch(cam, STATE.pitch_step)


class FPNavPitchDown(Operator):
    id = "fp_navigation.pitch_down"
    label = "FP Walk: Look Down"
    description = "Tilt head downward (E key)"
    @classmethod
    def poll(cls, ctx): return _get_cam() is not None
    def execute(self, ctx):
        cam = _get_cam()
        return {"CANCELLED"} if cam is None else _walk_pitch(cam, -STATE.pitch_step)


class FPNavApplyHeight(Operator):
    id = "fp_navigation.apply_height"
    label = "FP Walk: Snap to Eye Height"
    description = "Move camera Y to the configured eye height immediately"
    @classmethod
    def poll(cls, ctx): return _get_cam() is not None
    def execute(self, ctx):
        cam = _get_cam()
        if cam is None:
            return {"CANCELLED"}
        apply_eye_height(cam)
        lf.log.info(f"fp_navigation: eye height set to {STATE.eye_height:.3f}")
        return {"FINISHED"}


class FPNavSetHome(Operator):
    id = "fp_navigation.set_home"
    label = "FP Walk: Set Home"
    description = "Bookmark current camera pose"
    @classmethod
    def poll(cls, ctx): return _get_cam() is not None
    def execute(self, ctx):
        cam = _get_cam()
        if cam is None:
            return {"CANCELLED"}
        STATE.home_pose = list(cam.get_pose())
        lf.log.info("fp_navigation: home position saved")
        return {"FINISHED"}


class FPNavResetHome(Operator):
    id = "fp_navigation.reset_home"
    label = "FP Walk: Reset to Home"
    description = "Return camera to saved home position"
    @classmethod
    def poll(cls, ctx): return _get_cam() is not None and STATE.home_pose is not None
    def execute(self, ctx):
        cam = _get_cam()
        if cam is None or STATE.home_pose is None:
            return {"CANCELLED"}
        cam.set_pose(list(STATE.home_pose))
        return {"FINISHED"}
