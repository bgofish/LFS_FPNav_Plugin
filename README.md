# FP_Navigation — First-Person Walk Mode

A [LichtFeld Studio](https://lichtfeld.io) plugin for first-person walk-mode
navigation of 3D Gaussian Splat scenes. Movement is horizontal and
height-locked to a configurable floor level so you stay on the ground plane.

---

## Default Key Bindings

| Key | Action |
|-----|--------|
| `←` | Turn right (yaw around world Y) |
| `→` | Turn left (yaw around world Y) |
| `↑` | Stride forward (horizontal, floor-locked) |
| `↓` | Stride backward (horizontal, floor-locked) |
| `Q` | Tilt head down (pitch) |
| `E` | Tilt head up (pitch) |

All bindings are active when the viewport has focus. Pitch is clamped to ±80°
so the camera cannot flip over. Keys are fully rebindable from the panel.

---

## Installation
Paste https://github.com/bgofish/LFS_FPNav_Plugin  into the Plugin.Installer from within LichtFeld Studio. You may need to close & restart lichFeld Studio

<img width="967" height="239" alt="image" src="https://github.com/user-attachments/assets/7dc65b25-7993-4028-83a9-f8f87cc9251b" />

If you want to use it everytime: set to [Load on Startup] (Grid view required)

<img width="316" height="317" alt="image" src="https://github.com/user-attachments/assets/be0b346f-14b6-4657-a9fd-78450b8bed3b" />

---

## Usage

1. Open a scene with a loaded Gaussian splat.
2. Click inside the 3D viewport to give it focus - this is important to "link to the view"
3. Open the **FP Walk** panel (main panel tabs).
4. Optionally move the camera to your desired eye height and press
   **Set Floor to Eye Y** to lock the floor at that level.
5. Use `←` / `→` to turn, `↑` / `↓` to walk, `Q` / `E` to look up/down.
6. Press **Set Home** to bookmark a position and **Reset Home** to return.

---

## Panel Reference
<img width="535" height="446" alt="image" src="https://github.com/user-attachments/assets/2812ca88-f84f-4bd4-8c05-17a23b5f05f8" />

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
<img width="1091" height="388" alt="image" src="https://github.com/user-attachments/assets/2f00aff9-10d8-4e77-9c4c-84a8f95a9c91" />




---

## License

MIT — free to use, modify, and redistribute.
