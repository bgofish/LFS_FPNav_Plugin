"""
fp_navigation — walk mode operators using confirmed CameraState API.
"""

from __future__ import annotations
import math
import lichtfeld as lf
from lfs_plugins.types import Operator


# ---------------------------------------------------------------------------
# Shared state
# ---------------------------------------------------------------------------

class _State:
    floor_y:     float        = 0.0
    yaw_step:    float        = 5.0
    pitch_step:  float        = 3.0
    move_step:   float        = 0.25
    pitch_limit: float        = 80.0
    home_eye:    tuple | None = None
    home_target: tuple | None = None
    home_up:     tuple | None = None


STATE = _State()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _vec_sub(a, b):
    return (a[0]-b[0], a[1]-b[1], a[2]-b[2])

def _vec_add(a, b):
    return (a[0]+b[0], a[1]+b[1], a[2]+b[2])

def _vec_scale(v, s):
    return (v[0]*s, v[1]*s, v[2]*s)

def _vec_len(v):
    return math.sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2])

def _vec_norm(v):
    l = _vec_len(v)
    return (v[0]/l, v[1]/l, v[2]/l) if l > 1e-9 else v

def _vec_cross(a, b):
    return (
        a[1]*b[2] - a[2]*b[1],
        a[2]*b[0] - a[0]*b[2],
        a[0]*b[1] - a[1]*b[0],
    )

def _rot_around_axis(v, axis, rad):
    c, s = math.cos(rad), math.sin(rad)
    ax, ay, az = axis
    vx, vy, vz = v
    dot = ax*vx + ay*vy + az*vz
    return (
        ax*dot*(1-c) + vx*c + (-az*vy + ay*vz)*s,
        ay*dot*(1-c) + vy*c + ( az*vx - ax*vz)*s,
        az*dot*(1-c) + vz*c + (-ay*vx + ax*vy)*s,
    )

def _clamp_floor(eye, target):
    if eye[1] < STATE.floor_y:
        diff = STATE.floor_y - eye[1]
        eye    = (eye[0],    STATE.floor_y,    eye[2])
        target = (target[0], target[1] + diff, target[2])
    return eye, target

def _current_pitch(eye, target):
    fwd = _vec_norm(_vec_sub(target, eye))
    return math.asin(max(-1.0, min(1.0, fwd[1])))


# ---------------------------------------------------------------------------
# Core operations — all use lf.set_camera(eye, target, up)
# ---------------------------------------------------------------------------

def _do_yaw(deg: float) -> set:
    cam = lf.get_camera()
    eye, target = cam.eye, cam.target
    rad = math.radians(deg)
    fwd = _vec_sub(target, eye)
    new_fwd = _rot_around_axis(fwd, (0, 1, 0), rad)
    new_target = _vec_add(eye, new_fwd)
    eye, new_target = _clamp_floor(eye, new_target)
    lf.set_camera(eye, new_target, (0.0, 1.0, 0.0))
    return {"FINISHED"}


def _do_stride(delta: float) -> set:
    cam = lf.get_camera()
    eye, target = cam.eye, cam.target
    fwd = _vec_sub(target, eye)
    hfwd = _vec_norm((fwd[0], 0.0, fwd[2]))
    move = _vec_scale(hfwd, delta)
    new_eye    = _vec_add(eye,    move)
    new_target = _vec_add(target, move)
    new_eye, new_target = _clamp_floor(new_eye, new_target)
    lf.set_camera(new_eye, new_target, (0.0, 1.0, 0.0))
    return {"FINISHED"}


def _do_pitch(deg: float) -> set:
    cam = lf.get_camera()
    eye, target = cam.eye, cam.target
    rad = math.radians(deg)
    cur_pitch = _current_pitch(eye, target)
    lim = math.radians(STATE.pitch_limit)
    new_pitch = cur_pitch + rad
    if new_pitch > lim:    rad = lim - cur_pitch
    elif new_pitch < -lim: rad = -lim - cur_pitch
    if abs(rad) < 1e-6:
        return {"FINISHED"}
    fwd   = _vec_norm(_vec_sub(target, eye))
    right = _vec_norm(_vec_cross(fwd, (0, 1, 0)))
    dist  = _vec_len(_vec_sub(target, eye))
    new_fwd    = _vec_norm(_rot_around_axis(fwd, right, rad))
    new_target = _vec_add(eye, _vec_scale(new_fwd, dist))
    lf.set_camera(eye, new_target, (0.0, 1.0, 0.0))
    return {"FINISHED"}


# ---------------------------------------------------------------------------
# Operators
# ---------------------------------------------------------------------------

class FPNavYawLeft(Operator):
    id = "fp_navigation.yaw_left"
    label = "FP: Turn Left"
    description = "Turn left — ← key"
    @classmethod
    def poll(cls, ctx): return lf.get_camera() is not None
    def execute(self, ctx): return _do_yaw(-STATE.yaw_step)


class FPNavYawRight(Operator):
    id = "fp_navigation.yaw_right"
    label = "FP: Turn Right"
    description = "Turn right — → key"
    @classmethod
    def poll(cls, ctx): return lf.get_camera() is not None
    def execute(self, ctx): return _do_yaw(STATE.yaw_step)


class FPNavMoveForward(Operator):
    id = "fp_navigation.move_forward"
    label = "FP: Move Forward"
    description = "Stride forward — ↑ key"
    @classmethod
    def poll(cls, ctx): return lf.get_camera() is not None
    def execute(self, ctx): return _do_stride(STATE.move_step)


class FPNavMoveBackward(Operator):
    id = "fp_navigation.move_backward"
    label = "FP: Move Backward"
    description = "Stride backward — ↓ key"
    @classmethod
    def poll(cls, ctx): return lf.get_camera() is not None
    def execute(self, ctx): return _do_stride(-STATE.move_step)


class FPNavPitchUp(Operator):
    id = "fp_navigation.pitch_up"
    label = "FP: Look Up"
    description = "Tilt head up — Q key"
    @classmethod
    def poll(cls, ctx): return lf.get_camera() is not None
    def execute(self, ctx): return _do_pitch(STATE.pitch_step)


class FPNavPitchDown(Operator):
    id = "fp_navigation.pitch_down"
    label = "FP: Look Down"
    description = "Tilt head down — E key"
    @classmethod
    def poll(cls, ctx): return lf.get_camera() is not None
    def execute(self, ctx): return _do_pitch(-STATE.pitch_step)


class FPNavSetFloor(Operator):
    id = "fp_navigation.set_floor"
    label = "FP: Set Floor Here"
    description = "Use current camera eye Y as the floor level"
    @classmethod
    def poll(cls, ctx): return lf.get_camera() is not None
    def execute(self, ctx):
        STATE.floor_y = lf.get_camera().eye[1]
        lf.log.info(f"fp_navigation: floor set to Y={STATE.floor_y:.3f}")
        return {"FINISHED"}


class FPNavSetHome(Operator):
    id = "fp_navigation.set_home"
    label = "FP: Set Home"
    description = "Bookmark current camera pose"
    @classmethod
    def poll(cls, ctx): return lf.get_camera() is not None
    def execute(self, ctx):
        cam = lf.get_camera()
        STATE.home_eye    = cam.eye
        STATE.home_target = cam.target
        STATE.home_up     = cam.up
        lf.log.info("fp_navigation: home saved")
        return {"FINISHED"}


class FPNavResetHome(Operator):
    id = "fp_navigation.reset_home"
    label = "FP: Reset to Home"
    description = "Return camera to saved home position"
    @classmethod
    def poll(cls, ctx): return lf.get_camera() is not None and STATE.home_eye is not None
    def execute(self, ctx):
        if STATE.home_eye is None:
            return {"CANCELLED"}
        lf.set_camera(STATE.home_eye, STATE.home_target, STATE.home_up)
        return {"FINISHED"}
