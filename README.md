# fp_navigation — First-Person Walk Mode

A [LichtFeld Studio](https://lichtfeld.io) plugin for first-person walk-mode
navigation of 3D Gaussian Splat scenes. Movement is horizontal and
height-locked to a configurable floor level so you stay on a ground plane. This can be used in conjunction with any of the existing camera modes: Fly mode, Orbit & Free Orbit.

---

## Default Key Bindings (Fully customisable)

| Key | Action |
|-----|--------|
| `←` | Turn left (yaw around world Y) |
| `→` | Turn right (yaw around world Y) |
| `↑` | Stride forward (horizontal, floor-locked) |
| `↓` | Stride backward (horizontal, floor-locked) |
| `Q` | Tilt head up (pitch) |
| `E` | Tilt head down (pitch) |

All bindings are active when the viewport has focus. Pitch is clamped to ±80°
so the camera cannot flip over. Keys are fully rebindable from the panel.

---

## Installation

Copy the `fp_navigation/` folder into your LichtFeld plugin directory:

```
C:\Users\<you>\.lichtfeld\plugins\fp_navigation\   (Windows)
~/.lichtfeld/plugins/fp_navigation/                 (macOS / Linux)
```

LichtFeld Studio will detect and load it on next launch, or immediately if
hot-reload is enabled in the Plugin Manager.

---

## Usage

1. Open a scene with a loaded Gaussian splat.
2. Click inside the 3D viewport to give it focus.
3. Open the **FP Walk** panel (main panel tabs).
4. Optionally move the camera to your desired eye height and press
   **Set Floor to Eye Y** to lock the floor at that level.
5. Use `←` / `→` to turn, `↑` / `↓` to walk, `Q` / `E` to look up/down.
6. Press **Set Home** to bookmark a position and **Reset Home** to return.

---

## Panel Reference
<img width="533" height="456" alt="image" src="https://github.com/user-attachments/assets/9b57dbf2-f850-42ea-8eb2-721d9cf1b18c" />


Each button has a small **`[key]`** label next to it showing the current
binding. Click the `[key]` label to rebind — the panel enters capture mode,
press any key to assign it, or `Esc` to cancel.

---

## Configuration & Persistence

All settings are adjusted live in the **FP Walk** panel and saved automatically
to `settings.json` in the plugin folder:

| Setting | Default | Description |
|---------|---------|-------------|
| Stride step | `0.25 m` | World units moved per forward/backward key press |
| Turn step | `5.0°` | Degrees rotated per left/right key press |
| Tilt step | `3.0°` | Degrees pitched per Q/E key press |
| Floor Y | `0.0` | Camera Y is clamped to this value during movement |
| Key bindings | see above | Fully rebindable, stored as GLFW key codes |

Settings are loaded on startup and saved whenever you change a value or
rebind a key. The file lives at:

```
<plugin_folder>/fp_navigation/settings.json
```
<img width="1103" height="387" alt="image" src="https://github.com/user-attachments/assets/a7de45b7-b068-4249-9715-a06c5a281ae5" />

---

## License

MIT — free to use, modify, and redistribute.
