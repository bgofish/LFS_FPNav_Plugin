# fp_navigation — First-Person Walk Mode

A [LichtFeld Studio](https://lichtfeld.io) plugin for first-person walk-mode
navigation of 3D Gaussian Splat scenes. Eye height is locked to a configurable
value — movement always stays on the ground plane.

| Key | Action |
|-----|--------|
| `←` | Turn left (yaw around world Y) |
| `→` | Turn right (yaw around world Y) |
| `↑` | Stride forward (horizontal, height-locked) |
| `↓` | Stride backward (horizontal, height-locked) |
| `Q` | Tilt head up (pitch) |
| `E` | Tilt head down (pitch) |

All bindings are active when the viewport has focus. Pitch is clamped to ±80°
so the camera cannot flip over.

---

## Installation

### Manual install

Copy the `fp_navigation/` folder into your plugin directory:

```
~/.lichtfeld/plugins/fp_navigation/
```

LichtFeld Studio will detect and load it on next launch (or immediately
if hot-reload is enabled).

### Via Python

```python
import lichtfeld as lf
lf.plugins.install("path/to/fp_navigation")
```

---

## Usage

1. Open a scene with a loaded Gaussian splat.
2. Click inside the 3D viewport to give it focus.
3. Set your **Eye height** in the **FP Walk** sidebar panel and press
   **Snap Camera to Height** to position the camera at eye level.
4. Use `←` / `→` to turn, `↑` / `↓` to walk, and `Q` / `E` to look up or down.
5. Click **Set Home** to bookmark a position, and **Reset** to return to it.

---

## Panel (N-panel → Navigation → FP Walk)

```
Eye height  [1.65]   [Snap Camera to Height]

Move  (↑ ↓)   stride step [0.25]
  [↑ Forward]  [↓ Backward]

Turn  (← →)   turn step [5°]
  [← Left]  [→ Right]

Tilt head  (Q / E)   tilt step [3°]
  [Q Look Up]  [E Look Down]

Home position
  [Set Home]  [Reset]
```

---

## File structure

```
fp_navigation/
├── pyproject.toml          # Plugin manifest & LichtFeld compatibility
├── __init__.py             # on_load / on_unload entry points
├── keymaps.py              # Key bindings (VIEWPORT context)
├── operators/
│   ├── __init__.py
│   └── nav_ops.py          # All walk operators + shared STATE
└── panels/
    ├── __init__.py
    └── nav_panel.py        # "FP Walk" sidebar panel
```

---

## Configuration

All settings live in the **FP Walk** sidebar panel and take effect immediately
(no restart required):

| Setting | Default | Description |
|---------|---------|-------------|
| Eye height | `1.65` | Camera Y locked during all movement (world units) |
| Stride step | `0.25` | World units moved per ↑ / ↓ key press |
| Turn step | `5.0°` | Degrees rotated per ← / → key press |
| Tilt step | `3.0°` | Degrees pitched per Q / E key press |

---

## License

MIT — free to use, modify, and redistribute.
