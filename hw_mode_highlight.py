bl_info = {
    "name": "hw_modeHighlight",
    "author": "Hal Wayland",
    "version": (0, 2, 0),
    "blender": (5, 1, 0),
    "location": "Preferences > Add-ons > hw_modeHighlight",
    "description": "Change the 3D View header color based on mesh edit select mode.",
    "support": "COMMUNITY",
    "category": "Interface",
}

import bpy
from bpy.app.handlers import persistent
from bpy.props import (
    BoolProperty,
    FloatProperty,
    FloatVectorProperty,
)
from bpy.types import AddonPreferences, Operator


ADDON_ID = __package__ if __package__ else __name__
TIMER_INTERVAL_DEFAULT = 0.15

_ORIGINAL_HEADER_COLORS = {}
_LAST_APPLIED_COLOR = None


def _preference_updated(self, context):
    """Apply preference changes immediately so color tweaks can be previewed live."""
    _apply_current_highlight(context)


class HW_MODE_HIGHLIGHT_Preferences(AddonPreferences):
    bl_idname = ADDON_ID

    enabled: BoolProperty(
        name="Enable Highlighting",
        description="Continuously update the 3D View header color in mesh Edit Mode",
        default=True,
        update=_preference_updated,
    )
    timer_interval: FloatProperty(
        name="Refresh Interval",
        description="How often to check Blender mode and mesh select mode changes",
        default=TIMER_INTERVAL_DEFAULT,
        min=0.05,
        max=2.0,
        step=5,
        precision=2,
    )
    vertex_select_color: FloatVectorProperty(
        name="Vertex Select",
        subtype="COLOR",
        size=4,
        min=0.0,
        max=1.0,
        default=(0.15, 0.38, 0.95, 1.0),
        update=_preference_updated,
    )
    edge_select_color: FloatVectorProperty(
        name="Edge Select",
        subtype="COLOR",
        size=4,
        min=0.0,
        max=1.0,
        default=(0.20, 0.62, 0.22, 1.0),
        update=_preference_updated,
    )
    face_select_color: FloatVectorProperty(
        name="Face Select",
        subtype="COLOR",
        size=4,
        min=0.0,
        max=1.0,
        default=(0.82, 0.25, 0.16, 1.0),
        update=_preference_updated,
    )

    def draw(self, context):
        """Expose only select-mode colors because the add-on's purpose is edit-mode feedback."""
        layout = self.layout
        layout.prop(self, "enabled")

        select_box = layout.box()
        select_box.label(text="3D View Header Colors")
        select_box.prop(self, "vertex_select_color")
        select_box.prop(self, "edge_select_color")
        select_box.prop(self, "face_select_color")

        advanced_box = layout.box()
        advanced_box.label(text="Advanced")
        advanced_box.prop(self, "timer_interval")


class HW_MODE_HIGHLIGHT_OT_apply_now(Operator):
    bl_idname = "wm.hw_mode_highlight_apply_now"
    bl_label = "Apply Mode Highlight"
    bl_description = "Refresh the active mode highlight immediately"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        """Refresh on demand so Blender registers a concrete operator for the add-on."""
        _apply_current_highlight(context)
        return {"FINISHED"}


CLASSES = (
    HW_MODE_HIGHLIGHT_Preferences,
    HW_MODE_HIGHLIGHT_OT_apply_now,
)


def _get_preferences(context):
    """Return add-on preferences using the package id required by Blender extensions."""
    addon = context.preferences.addons.get(ADDON_ID)
    if addon is None:
        return None
    return addon.preferences


def _get_view3d_header_space(context):
    """Return the theme owner for the 3D View header bar the user sees above the viewport."""
    theme = context.preferences.themes[0]
    return theme.view_3d.space


def _redraw_view3d_headers(context):
    """Request redraws so theme color changes appear in open 3D View headers promptly."""
    screen = context.screen
    if screen is None:
        return

    for area in screen.areas:
        if area.type == "VIEW_3D":
            area.tag_redraw()


def _remember_original_header(space):
    """Capture the untouched header color once so disabling the add-on restores the theme."""
    key = space.as_pointer()
    if key not in _ORIGINAL_HEADER_COLORS:
        _ORIGINAL_HEADER_COLORS[key] = (space, tuple(space.header))


def _restore_original_headers():
    """Restore all headers touched by this runtime to avoid leaving theme side effects behind."""
    global _LAST_APPLIED_COLOR

    for space, color in _ORIGINAL_HEADER_COLORS.values():
        try:
            space.header = color
        except ReferenceError:
            continue

    _ORIGINAL_HEADER_COLORS.clear()
    _LAST_APPLIED_COLOR = None


def _blend_colors(colors):
    """Average selected colors so multi-select modes still use only the three configured values."""
    color_count = len(colors)
    return tuple(sum(color[channel] for color in colors) / color_count for channel in range(4))


def _is_mesh_edit_mode(context):
    """Limit highlighting to mesh Edit Mode because other modes should keep the normal theme."""
    active_object = context.object
    return (
        active_object is not None
        and active_object.type == "MESH"
        and active_object.mode == "EDIT"
    )


def _get_mesh_select_mode_color(preferences, context):
    """Map vertex, edge, and face select modes to the configured 3D View header colors."""
    vertex_enabled, edge_enabled, face_enabled = context.tool_settings.mesh_select_mode
    selected_colors = []

    if vertex_enabled:
        selected_colors.append(tuple(preferences.vertex_select_color))
    if edge_enabled:
        selected_colors.append(tuple(preferences.edge_select_color))
    if face_enabled:
        selected_colors.append(tuple(preferences.face_select_color))

    if not selected_colors:
        return None
    if len(selected_colors) == 1:
        return selected_colors[0]

    return _blend_colors(selected_colors)


def _apply_header_color(preferences, context, color):
    """Write the active color to the 3D View header only when it has changed."""
    global _LAST_APPLIED_COLOR

    if color == _LAST_APPLIED_COLOR:
        return

    space = _get_view3d_header_space(context)
    _remember_original_header(space)
    space.header = color

    _LAST_APPLIED_COLOR = color
    _redraw_view3d_headers(context)


def _apply_current_highlight(context):
    """Refresh the 3D View header so select-mode changes are visible without user action."""
    preferences = _get_preferences(context)
    if preferences is None:
        return

    if not preferences.enabled or not _is_mesh_edit_mode(context):
        _restore_original_headers()
        _redraw_view3d_headers(context)
        return

    color = _get_mesh_select_mode_color(preferences, context)
    if color is None:
        _restore_original_headers()
        _redraw_view3d_headers(context)
        return

    _apply_header_color(preferences, context, color)


def _highlight_timer():
    """Poll mode state because mesh select mode changes are not exposed as a simple event."""
    context = bpy.context
    preferences = _get_preferences(context)

    if preferences is None:
        return TIMER_INTERVAL_DEFAULT

    _apply_current_highlight(context)
    return preferences.timer_interval if preferences.enabled else TIMER_INTERVAL_DEFAULT


@persistent
def _load_post_handler(_dummy):
    """Reapply highlighting after loading a file because themes and areas may be rebuilt."""
    _ORIGINAL_HEADER_COLORS.clear()
    _apply_current_highlight(bpy.context)


def register():
    """Register preferences and start the lightweight timer that keeps highlights current."""
    for cls in CLASSES:
        bpy.utils.register_class(cls)

    if _load_post_handler not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(_load_post_handler)

    if not bpy.app.timers.is_registered(_highlight_timer):
        bpy.app.timers.register(_highlight_timer, first_interval=0.1, persistent=True)


def unregister():
    """Remove add-on state and restore theme colors when Blender disables the add-on."""
    if bpy.app.timers.is_registered(_highlight_timer):
        bpy.app.timers.unregister(_highlight_timer)

    if _load_post_handler in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(_load_post_handler)

    _restore_original_headers()

    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
