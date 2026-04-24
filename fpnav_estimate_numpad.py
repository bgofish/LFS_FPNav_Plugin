"""
fpnav_estimate_numpad.py  —  Proof-of-concept console script
=============================================================
Drop this into the Lichtfeld Studio console (or exec it via
  exec(open("fpnav_estimate_numpad.py").read())
and it will:

  1.  Read the bounding box of every visible splat node via
        scene.get_node_bounds(node_name)  →  (mn, mx)
      and union them all into a single world-space AABB.

  2.  Derive a camera (eye, target, up) for each of the 10
      numpad canonical views:
        KP5 – Top       KP0 – Bottom
        KP2 – Front     KP8 – Back
        KP6 – Right     KP4 – Left
        KP9 – NE        KP7 – NW
        KP3 – SE        KP1 – SW

  3.  The pull-back distance is calculated from the FOV so the
      whole splat fits inside the view with a small margin.

  4.  The computed (eye, target, up) tuples are written directly
      into STATE.numpad_views so pressing numpad keys jumps there.

Assumptions
-----------
* Y is UP (same convention used throughout FP_Navigation).
* Front  = +Z direction,  Right = +X direction.
* The diagonal views (NE/NW/SE/SW) are 45 ° horizontal rotations
  of the cardinal directions; pull-back uses the greatest of the
  three axis extents so nothing gets clipped.

Usage
-----
Just run the script.  It prints a summary and populates the
numpad slots — no restart needed.  Press a numpad key to jump
to the estimated view.

To re-run with a custom margin or FOV override:
    MARGIN_FACTOR = 1.15   # default 15 % breathing room
    FOV_OVERRIDE  = 60.0   # degrees; None = read from camera
"""

from __future__ import annotations
import math
import lichtfeld as lf

# ── Tunables ──────────────────────────────────────────────────────────────────
MARGIN_FACTOR: float       = 1.15   # extra breathing room (1.0 = tight fit)
FOV_OVERRIDE:  float | None = None  # degrees; None = read from lf.get_camera()
DEFAULT_FOV:   float       = 60.0   # fallback if camera has no fov attribute
NODE_NAME:     str  | None = None   # None = union all visible splat nodes
# ─────────────────────────────────────────────────────────────────────────────


def _union_bounds(scene, node_name: str | None):
    """Return (mn, mx) as plain lists; unions all visible splat nodes or one."""
    INF = float("inf")
    mn = [ INF,  INF,  INF]
    mx = [-INF, -INF, -INF]

    if node_name is not None:
        nodes_to_check = [n for n in scene.get_visible_nodes()
                          if n.name == node_name]
    else:
        nodes_to_check = [n for n in scene.get_visible_nodes()
                          if n.splat_data() is not None]

    if not nodes_to_check:
        raise RuntimeError("No visible splat nodes found.  "
                           "Make sure at least one splat node is visible.")

    for node in nodes_to_check:
        try:
            b_mn, b_mx = scene.get_node_bounds(node.name)
        except Exception as e:
            lf.log.warn(f"fpnav_estimate: skipping '{node.name}': {e}")
            continue
        for i in range(3):
            if b_mn[i] < mn[i]: mn[i] = b_mn[i]
            if b_mx[i] > mx[i]: mx[i] = b_mx[i]

    if mn[0] == INF:
        raise RuntimeError("Could not read bounds from any visible splat node.")

    return mn, mx


def _get_fov_deg() -> float:
    """Best-effort: read FOV from the camera object, else use override/default."""
    if FOV_OVERRIDE is not None:
        return FOV_OVERRIDE
    cam = lf.get_camera()
    if cam is not None:
        for attr in ("fov", "fov_y", "fovy", "vertical_fov"):
            v = getattr(cam, attr, None)
            if v is not None:
                deg = math.degrees(v) if v < math.pi * 2 else v  # radians guard
                if 1.0 < deg < 180.0:
                    return float(deg)
    lf.log.warn(f"fpnav_estimate: could not read FOV from camera; "
                f"using default {DEFAULT_FOV}°")
    return DEFAULT_FOV


def _pullback(half_extent: float, fov_deg: float) -> float:
    """Distance from centre so half_extent fits inside half the FOV."""
    return (half_extent * MARGIN_FACTOR) / math.tan(math.radians(fov_deg / 2.0))


def estimate_numpad_views(
    node_name: str | None = NODE_NAME,
) -> dict[str, tuple]:
    """
    Calculate all 10 numpad camera poses from the splat AABB.

    Returns a dict  slot_name → (eye, target, up)  using the same
    slot names as FP_Navigation's NUMPAD_SLOTS.
    """
    if not lf.has_scene():
        raise RuntimeError("No scene loaded.")

    scene = lf.get_scene()
    mn, mx = _union_bounds(scene, node_name)

    # ── Extents & centre ────────────────────────────────────────────────────
    cx = (mn[0] + mx[0]) / 2.0
    cy = (mn[1] + mx[1]) / 2.0
    cz = (mn[2] + mx[2]) / 2.0
    centre = (cx, -cy, -cz)

    dx = mx[0] - mn[0]   # width  (X)
    dy = mx[1] - mn[1]   # height (Y)
    dz = mx[2] - mn[2]   # depth  (Z)

    fov = _get_fov_deg()

    # Per-axis half-extents used to drive pull-back for each view plane.
    # For a view along Z we need to frame X and Y, so half_extent
    # is the *larger* of the two perpendicular dimensions.
    hx = dx / 2.0
    hy = dy / 2.0
    hz = dz / 2.0

    # Diagonal views need to frame the full footprint — use the longest
    # axis among all three.
    h_diag = max(dx, dy, dz) / 2.0

    # ── Helper: build (eye, target, up) ─────────────────────────────────────
    def _pose(eye, up=(0.0, 1.0, 0.0)):
        return (eye, centre, up)

    # ── Top  (KP5) — look straight down ──────────────────────────────────
    # Frames X and Z; camera is directly above centre, looks at centre.
    d_top = _pullback(max(hx, hz), fov)
    top = _pose((cx, cy + d_top, cz), up=(0.0, 0.0, -1.0))
    # "Up" vector for a top-down view must not be (0,1,0) — use -Z (front)

    # ── Bottom  (KP0) — look straight up ─────────────────────────────────
    d_bot = d_top
    bottom = _pose((cx, cy - d_bot, cz), up=(0.0, 0.0, 1.0))

    # ── Front  (KP2) — along -Z axis (looking toward +Z into the scene) ──
    d_front = _pullback(max(hx, hy), fov)
    front = _pose((cx, cy, cz - d_front))

    # ── Back  (KP8) — along +Z axis ──────────────────────────────────────
    d_back = d_front
    back = _pose((cx, cy, cz + d_back))

    # ── Right  (KP6) — along -X axis (looking toward +X) ────────────────
    d_right = _pullback(max(hz, hy), fov)
    right = _pose((cx + d_right, cy, cz))

    # ── Left  (KP4) — along +X axis ──────────────────────────────────────
    d_left = d_right
    left = _pose((cx - d_left, cy, cz))

    # ── Diagonal corners — 45° horizontal yaw, 45° downward pitch ────────
    #
    # The eye sits at a true 45° elevation above the horizontal plane through
    # the scene centre, so it looks down-and-in rather than straight across.
    #
    # Geometry:
    #   • We want the 3D pull-back distance D to frame h_diag at the given FOV.
    #   • At 45° pitch the eye is split equally: horiz_offset = vert_offset = D/√2
    #     so the horizontal ground distance from centre = D / √2.
    #   • That horizontal distance is then split equally again between the two
    #     ground axes (45° yaw), so each axis offset = D / √2 / √2 = D / 2.
    #
    # Result: eye = centre + (±D/2,  +D/√2,  ±D/2)
    #         The view direction points straight at centre from 45° above.
    #
    # We scale D up by √2 so the *projected* coverage at the 45° angle still
    # frames the full h_diag extent (same logic as the top-view pull-back but
    # accounting for the foreshortening of a tilted view).
    # Extra scale so the tilted view fits the full diagonal footprint:
    # effective half-extent seen from 45° pitch = h_diag / cos(45°) = h_diag*√2
    d45_3d = _pullback(h_diag * math.sqrt(2.0), fov)
    d45_horiz_axis = d45_3d / 2.0          # per ground axis (X or Z)
    d45_vert       = d45_3d / math.sqrt(2.0)  # Y rise

    # NE  (KP9) — behind-right  (+Z, +X side), elevated
    ne = _pose((cx + d45_horiz_axis, cy + d45_vert, cz + d45_horiz_axis))
    # NW  (KP7) — behind-left   (+Z, -X side), elevated
    nw = _pose((cx - d45_horiz_axis, cy + d45_vert, cz + d45_horiz_axis))
    # SE  (KP3) — front-right   (-Z, +X side), elevated
    se = _pose((cx + d45_horiz_axis, cy + d45_vert, cz - d45_horiz_axis))
    # SW  (KP1) — front-left    (-Z, -X side), elevated
    sw = _pose((cx - d45_horiz_axis, cy + d45_vert, cz - d45_horiz_axis))

    return {
        "KP_5_top":        top,
        "KP_0_bottom":     bottom,
        "KP_2_front":      front,
        "KP_8_back":       back,
        "KP_6_right":      right,
        "KP_4_left":       left,
        "KP_9_north_east": ne,
        "KP_7_north_west": nw,
        "KP_3_south_east": se,
        "KP_1_south_west": sw,
    }


def apply_to_state(views: dict) -> None:
    """Push computed views into FP_Navigation's live STATE.numpad_views."""
    try:
        # Works whether the plugin was installed as "FP_Navigation" or by its
        # folder name — just import from the already-loaded module cache.
        import importlib, sys
        nav_mod = None
        for mod_name, mod in sys.modules.items():
            if mod_name.endswith("operators.nav_ops") and hasattr(mod, "STATE"):
                nav_mod = mod
                break
        if nav_mod is None:
            # Try the canonical path as a fallback
            nav_mod = importlib.import_module(
                "lfs_plugins.FP_Navigation.operators.nav_ops")

        if nav_mod.STATE.numpad_views is None:
            nav_mod.STATE.numpad_views = {}
        nav_mod.STATE.numpad_views.update(views)
        lf.log.info("fpnav_estimate: STATE.numpad_views updated successfully.")
    except Exception as e:
        lf.log.warn(f"fpnav_estimate: could not update STATE directly: {e}\n"
                    f"  You can apply manually — see printed output above.")


# ── Main ──────────────────────────────────────────────────────────────────────

def run(node_name: str | None = NODE_NAME, apply: bool = True) -> dict:
    """
    Main entry point.

    Parameters
    ----------
    node_name : str | None
        Name of a specific splat node to use, or None to union all visible
        splat nodes.
    apply : bool
        If True, push the views straight into STATE.numpad_views.

    Returns
    -------
    dict  slot → (eye, target, up)
    """
    scene  = lf.get_scene()
    mn, mx = _union_bounds(scene, node_name)
    fov    = _get_fov_deg()

    print("\n── fpnav_estimate_numpad ─────────────────────────────────────────")
    print(f"  Bounds  X: [{mn[0]:.3f}, {mx[0]:.3f}]  "
          f"Y: [{mn[1]:.3f}, {mx[1]:.3f}]  "
          f"Z: [{mn[2]:.3f}, {mx[2]:.3f}]")
    print(f"  Size    dX={mx[0]-mn[0]:.3f}  dY={mx[1]-mn[1]:.3f}  dZ={mx[2]-mn[2]:.3f}")
    cx = (mn[0]+mx[0])/2; cy = (mn[1]+mx[1])/2; cz = (mn[2]+mx[2])/2
    print(f"  Centre  ({cx:.3f}, {cy:.3f}, {cz:.3f})")
    print(f"  FOV     {fov:.1f}°   Margin {MARGIN_FACTOR:.0%}")
    print()

    views = estimate_numpad_views(node_name)

    labels = {
        "KP_5_top":        "KP5 Top",
        "KP_0_bottom":     "KP0 Bottom",
        "KP_2_front":      "KP2 Front",
        "KP_8_back":       "KP8 Back",
        "KP_6_right":      "KP6 Right",
        "KP_4_left":       "KP4 Left",
        "KP_9_north_east": "KP9 NE",
        "KP_7_north_west": "KP7 NW",
        "KP_3_south_east": "KP3 SE",
        "KP_1_south_west": "KP1 SW",
    }

    for slot, (eye, tgt, up) in views.items():
        print(f"  {labels[slot]:<12}  "
              f"eye=({eye[0]:7.3f}, {eye[1]:7.3f}, {eye[2]:7.3f})  "
              f"up=({up[0]:.0f},{up[1]:.0f},{up[2]:.0f})")

    print()

    if apply:
        apply_to_state(views)
        print("  ✓  Views written to STATE.numpad_views.")
        print("     Press a numpad key to jump to its estimated view.")
    else:
        print("  apply=False — views NOT written to STATE (dry run).")

    print("─────────────────────────────────────────────────────────────────\n")
    return views


# ── Auto-run when exec()'d in the console ─────────────────────────────────────
if __name__ == "__main__" or True:
    run()
