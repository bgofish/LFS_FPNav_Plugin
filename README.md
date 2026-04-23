# FP_Navigation — First-Person Walk Mode

A [LichtFeld Studio](https://lichtfeld.io) plugin for first-person walk-mode
navigation of 3D Gaussian Splat scenes. Movement is horizontal and
height-locked to a configurable floor level so you stay on the ground plane.

---

## Default Key Bindings

| Key | Action |
|-----|--------|
| `←` | Turn to left (yaw around world Y) |
| `→` | Turn to right (yaw around world Y) |
| `↑` | Move forward (horizontal, floor-locked) |
| `↓` | Move backward (horizontal, floor-locked) |
| `Q` | Tilt head down (pitch) |
| `E` | Tilt head up (pitch) |

All bindings are active when the viewport has focus - [You will need to click your mouse cursor in the main view]. 

Pitch is clamped to ±80° so the camera cannot flip over. 

Keys can be set in the plugin FPN_Settings.json file.

---

## Installation
Not on the Market place yet so if you want to try it : Paste https://github.com/bgofish/LFS_FPNav_Plugin  into the Plugin.Installer from within LichtFeld Studio. 

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
6. Press **Set [Home]** to bookmark a position and **Goto [Home]** to return.
7. There are 6 other custom view slots that will have a tick beside them when set
8. Both [Home] & [V1 to V6] are saved in the FPN_settings.json file  so area able to be copied across projects
9. the settings buttons ae repeated at the bottom for convenience. 

---

## Panel Reference
<img width="551" height="959" alt="image" src="https://github.com/user-attachments/assets/a48bf19c-3433-4037-bd14-ae80f9027044" />

---

## Configuration & Persistence

All settings are adjusted live in the **FP Nav** panel and saved manually 
to `FPN_settings.json` in the plugin folder:

| Setting | Default | Description |
|---------|---------|-------------|
| Stride step | `0.25 m` | World units moved per forward/backward key press |
| Turn step | `5.0°` | Degrees rotated per left/right key press |
| Tilt step | `3.0°` | Degrees pitched per Q/E key press |
| Floor Y | `0.0` | Camera Y is clamped to this value during movement |
| Key bindings | see above | Customisable if needed (Stored as [GLFW key codes](https://www.glfw.org/docs/latest/group__keys.html)) |

Settings need to manually loaded after - the file lives at:

```
<plugin_folder>/fp_navigation/FPN_settings.json
```

<img width="1104" height="687" alt="image" src="https://github.com/user-attachments/assets/05a203be-dee9-47f4-bead-6b0d8617ea1e" />




---

## License

MIT — free to use, modify, and redistribute.
