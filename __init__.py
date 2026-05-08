"""Blender extension entry point for HW Mode Highlight."""

from . import hw_mode_highlight as _addon


bl_info = _addon.bl_info


def register():
    """Register the add-on through Blender's extension package entry point."""
    _addon.register()


def unregister():
    """Unregister the add-on through Blender's extension package entry point."""
    _addon.unregister()
