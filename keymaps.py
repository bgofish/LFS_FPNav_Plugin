"""
Keymap registration for fp_navigation.

Binds the four arrow keys in the Viewport context so they fire
the FP Nav operators while the viewport has focus.
"""

import lichtfeld as lf

# Keep references to registered keymaps so we can remove them on unload
_registered: list = []


def register_keymaps() -> None:
    """Bind ← → ↑ ↓ arrow keys to fp_navigation operators."""
    km = lf.keymaps

    bindings = [
        ("LEFT_ARROW",  "fp_navigation.yaw_left"),
        ("RIGHT_ARROW", "fp_navigation.yaw_right"),
        ("UP_ARROW",    "fp_navigation.move_forward"),
        ("DOWN_ARROW",  "fp_navigation.move_backward"),
    ]

    for key, op_id in bindings:
        entry = km.add(
            context="VIEWPORT",   # active in the 3D viewport
            key=key,
            operator=op_id,
            modifiers=[],         # no Shift/Ctrl/Alt required
            repeat=True,          # fires continuously while held
        )
        _registered.append(entry)

    lf.log.info(f"fp_navigation: {len(_registered)} key bindings registered")


def unregister_keymaps() -> None:
    """Remove all key bindings registered by this plugin."""
    km = lf.keymaps
    for entry in _registered:
        try:
            km.remove(entry)
        except Exception as exc:
            lf.log.warn(f"fp_navigation: could not remove keymap entry: {exc}")
    _registered.clear()
