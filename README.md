# fp_navigation — First-Person Arrow Key Navigation

A [LichtFeld Studio](https://lichtfeld.io) plugin that binds the four arrow
keys to first-person viewport camera movement.

| Key | Action |
|-----|--------|
| `←` | Rotate camera left (yaw) |
| `→` | Rotate camera right (yaw) |
| `↑` | Move forward along view axis |
| `↓` | Move backward along view axis |

Step sizes and a home-position save/reset are configurable from the
**FP Nav** sidebar panel.

---

## Installation

### Via the LichtFeld Studio plugin registry (recommended)

```python
import lichtfeld as lf
lf.plugins.install("your-github-username/fp_navigation")
```

### Manual install

Copy (or symlink) the `fp_navigation/` folder into your plugin directory:

```
~/.lichtfeld/plugins/fp_navigation/
```

LichtFeld Studio will detect and load it on next launch (or immediately
if hot-reload is enabled).

---

## Usage

1. Open a scene with a loaded Gaussian splat.
2. Click inside the 3D viewport to give it focus.
3. Use `←` / `→` to rotate the camera and `↑` / `↓` to fly forward/back.
4. Adjust **Yaw step** and **Move step** in the **FP Nav** sidebar panel
   (`N` panel → *Navigation* category).
5. Click **Set Home** to bookmark a position, and **Reset** to return to it.

---

## File structure

```
fp_navigation/
├── pyproject.toml          # Plugin manifest & LichtFeld compatibility
├── __init__.py             # on_load / on_unload entry points
├── keymaps.py              # Arrow key bindings (VIEWPORT context)
├── operators/
│   ├── __init__.py
│   └── nav_ops.py          # FPNavYawLeft/Right, MoveForward/Backward,
│                           # SetHome, ResetHome
└── panels/
    ├── __init__.py
    └── nav_panel.py        # "FP Nav" sidebar panel with step controls
```

---

## Configuration

All settings are exposed in the **FP Nav** sidebar panel and take effect
immediately (no restart required):

| Setting | Default | Description |
|---------|---------|-------------|
| Yaw step | `5.0°` | Degrees rotated per key press |
| Move step | `0.25` | World units moved per key press |

---

## License

MIT — free to use, modify, and redistribute.
