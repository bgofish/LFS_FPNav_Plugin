"""Keymap bindings for fp_navigation walk mode."""

import lichtfeld as lf

_registered: list = []


def register_keymaps() -> None:
    km = lf.keymaps
    bindings = [
        ("LEFT_ARROW",  "fp_navigation.yaw_left"),
        ("RIGHT_ARROW", "fp_navigation.yaw_right"),
        ("UP_ARROW",    "fp_navigation.move_forward"),
        ("DOWN_ARROW",  "fp_navigation.move_backward"),
        ("Q",           "fp_navigation.pitch_up"),
        ("E",           "fp_navigation.pitch_down"),
    ]
    for key, op_id in bindings:
        entry = km.add(
            context="VIEWPORT",
            key=key,
            operator=op_id,
            modifiers=[],
            repeat=True,
        )
        _registered.append(entry)
    lf.log.info(f"fp_navigation: {len(_registered)} key bindings registered")


def unregister_keymaps() -> None:
    km = lf.keymaps
    for entry in _registered:
        try:
            km.remove(entry)
        except Exception as exc:
            lf.log.warn(f"fp_navigation: could not remove keymap: {exc}")
    _registered.clear()
