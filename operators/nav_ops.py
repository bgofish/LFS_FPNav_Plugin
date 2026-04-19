"""
Navigation operators for fp_navigation.

Each operator reads the current viewport camera pose, applies a
delta (rotation or translation), and writes the result back.

Camera pose is a 4x4 column-major float32 transform matrix
(OpenGL convention: -Z forward, Y up).
"""

from __future__ import annotations
import math
import lichtfeld as lf
from lfs_plugins.types import Operator

# ---------------------------------------------------------------------------
# Shared plugin state (survives hot-reload within a session)
# ---------------------------------------------------------------------------

class _State:
    """Mutable plugin-global state shared across all operators."""
    yaw_step: float = 5.0      # degrees per key press
    move_step: float = 0.25    # world units per key press
    home_pose: list | None = None  # saved 4x4 flat list, or None


STATE = _State()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_viewport_camera() -> "lf.ViewportCamera | None":
    """Return the active viewport camera, or None."""
    try:
        return lf.viewport.get_camera()
    except AttributeError:
        # Fallback path for older API surfaces
        try:
            return lf.get_viewport_camera()
        except AttributeError:
            return None


def _make_rotation_y(angle_rad: float) -> list[float]:
    """4x4 column-major rotation matrix around world Y axis."""
    c = math.cos(angle_rad)
    s = math.sin(angle_rad)
    return [
        c,  0.0,  s, 0.0,
        0.0, 1.0, 0.0, 0.0,
       -s,  0.0,  c, 0.0,
        0.0, 0.0, 0.0, 1.0,
    ]


def _mat4_mul(a: list[float], b: list[float]) -> list[float]:
    """Multiply two 4x4 column-major matrices."""
    out = [0.0] * 16
    for row in range(4):
        for col in range(4):
            v = 0.0
            for k in range(4):
                v += a[row + k * 4] * b[k + col * 4]
            out[row + col * 4] = v
    return out


def _apply_yaw(cam, angle_deg: float) -> set:
    """Rotate the camera around world Y, keeping its position."""
    pose = list(cam.get_pose())           # flat 16 floats, col-major
    angle_rad = math.radians(angle_deg)

    # Extract translation from current pose (column 3)
    tx, ty, tz = pose[12], pose[13], pose[14]

    # Build rotation about world Y at origin, then restore position
    rot = _make_rotation_y(angle_rad)
    new_pose = _mat4_mul(rot, pose)
    new_pose[12], new_pose[13], new_pose[14] = tx, ty, tz  # keep position

    cam.set_pose(new_pose)
    return {"FINISHED"}


def _apply_translate(cam, delta_local_z: float) -> set:
    """Move the camera along its local -Z (forward) axis."""
    pose = list(cam.get_pose())

    # Local forward = -Z column of the rotation part (col 2, negated)
    fx = -pose[8]
    fy = -pose[9]
    fz = -pose[10]

    # Normalise (should already be unit length, but be safe)
    length = math.sqrt(fx*fx + fy*fy + fz*fz)
    if length > 1e-6:
        fx /= length
        fy /= length
        fz /= length

    pose[12] += fx * delta_local_z
    pose[13] += fy * delta_local_z
    pose[14] += fz * delta_local_z

    cam.set_pose(pose)
    return {"FINISHED"}


# ---------------------------------------------------------------------------
# Operator definitions
# ---------------------------------------------------------------------------

class FPNavYawLeft(Operator):
    id = "fp_navigation.yaw_left"
    label = "FP Nav: Rotate Left"
    description = "Rotate viewport camera left (← key)"

    @classmethod
    def poll(cls, context) -> bool:
        return _get_viewport_camera() is not None

    def execute(self, context) -> set:
        cam = _get_viewport_camera()
        if cam is None:
            return {"CANCELLED"}
        return _apply_yaw(cam, -STATE.yaw_step)


class FPNavYawRight(Operator):
    id = "fp_navigation.yaw_right"
    label = "FP Nav: Rotate Right"
    description = "Rotate viewport camera right (→ key)"

    @classmethod
    def poll(cls, context) -> bool:
        return _get_viewport_camera() is not None

    def execute(self, context) -> set:
        cam = _get_viewport_camera()
        if cam is None:
            return {"CANCELLED"}
        return _apply_yaw(cam, STATE.yaw_step)


class FPNavMoveForward(Operator):
    id = "fp_navigation.move_forward"
    label = "FP Nav: Move Forward"
    description = "Move viewport camera forward (↑ key)"

    @classmethod
    def poll(cls, context) -> bool:
        return _get_viewport_camera() is not None

    def execute(self, context) -> set:
        cam = _get_viewport_camera()
        if cam is None:
            return {"CANCELLED"}
        return _apply_translate(cam, STATE.move_step)


class FPNavMoveBackward(Operator):
    id = "fp_navigation.move_backward"
    label = "FP Nav: Move Backward"
    description = "Move viewport camera backward (↓ key)"

    @classmethod
    def poll(cls, context) -> bool:
        return _get_viewport_camera() is not None

    def execute(self, context) -> set:
        cam = _get_viewport_camera()
        if cam is None:
            return {"CANCELLED"}
        return _apply_translate(cam, -STATE.move_step)


class FPNavSetHome(Operator):
    id = "fp_navigation.set_home"
    label = "FP Nav: Set Home"
    description = "Save current camera position as the home (reset) position"

    @classmethod
    def poll(cls, context) -> bool:
        return _get_viewport_camera() is not None

    def execute(self, context) -> set:
        cam = _get_viewport_camera()
        if cam is None:
            return {"CANCELLED"}
        STATE.home_pose = list(cam.get_pose())
        lf.log.info("fp_navigation: home position saved")
        return {"FINISHED"}


class FPNavResetHome(Operator):
    id = "fp_navigation.reset_home"
    label = "FP Nav: Reset to Home"
    description = "Return viewport camera to the saved home position"

    @classmethod
    def poll(cls, context) -> bool:
        return _get_viewport_camera() is not None and STATE.home_pose is not None

    def execute(self, context) -> set:
        cam = _get_viewport_camera()
        if cam is None or STATE.home_pose is None:
            return {"CANCELLED"}
        cam.set_pose(STATE.home_pose)
        return {"FINISHED"}
