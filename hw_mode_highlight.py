bl_info = {
    "name": "HW Mode Highlight",
    "author": "Martin",
    "version": (0, 1, 0),
    "blender": (5, 1, 0),
    "location": "Preferences > Add-ons > HW Mode Highlight",
    "description": "Change editor header colors based on the current Blender mode.",
    "support": "COMMUNITY",
    "category": "Interface",
}

import bpy
from bpy.app.handlers import persistent
from bpy.props import (
    BoolProperty,
    EnumProperty,
    FloatProperty,
    FloatVectorProperty,
)
from bpy.types import AddonPreferences, Operator


ADDON_ID = __name__
TIMER_INTERVAL_DEFAULT = 0.15

_ORIGINAL_HEADER_COLORS = {}
_LAST_APPLIED_COLOR = None
_LAST_TARGET_SCOPE = None


def _preference_updated(self, context):
    """Apply preference changes immediately so color tweaks can be previewed live."""
    _apply_current_highlight(context)


class HW_MODE_HIGHLIGHT_Preferences(AddonPreferences):
    bl_idname = ADDON_ID

    enabled: BoolProperty(
        name="Enable Highlighting",
        description="Continuously update header colors to reflect the active mode",
        default=True,
        update=_preference_updated,
    )
    target_scope: EnumProperty(
        name="Header Scope",
        description="Choose which editor headers should receive the mode highlight",
        items=(
            ("VIEW_3D", "3D View Only", "Only tint 3D View headers"),
            ("ALL", "All Editors", "Tint every editor header that exposes a theme color"),
        ),
        default="VIEW_3D",
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
    object_color: FloatVectorProperty(
        name="Object Mode",
        subtype="COLOR",
        size=4,
        min=0.0,
        max=1.0,
        default=(0.13, 0.13, 0.13, 1.0),
        update=_preference_updated,
    )
    edit_color: FloatVectorProperty(
        name="Edit Mode",
        subtype="COLOR",
        size=4,
        min=0.0,
        max=1.0,
        default=(0.80, 0.45, 0.10, 1.0),
        update=_preference_updated,
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
    mixed_select_color: FloatVectorProperty(
        name="Mixed Mesh Select",
        subtype="COLOR",
        size=4,
        min=0.0,
        max=1.0,
        default=(0.46, 0.24, 0.75, 1.0),
        update=_preference_updated,
    )
    sculpt_color: FloatVectorProperty(
        name="Sculpt Mode",
        subtype="COLOR",
        size=4,
        min=0.0,
        max=1.0,
        default=(0.40, 0.20, 0.58, 1.0),
        update=_preference_updated,
    )
    pose_color: FloatVectorProperty(
        name="Pose Mode",
        subtype="COLOR",
        size=4,
        min=0.0,
        max=1.0,
        default=(0.12, 0.48, 0.62, 1.0),
        update=_preference_updated,
    )
    paint_color: FloatVectorProperty(
        name="Paint Modes",
        subtype="COLOR",
        size=4,
        min=0.0,
        max=1.0,
        default=(0.56, 0.32, 0.12, 1.0),
        update=_preference_updated,
    )
    fallback_color: FloatVectorProperty(
        name="Other Modes",
        subtype="COLOR",
        size=4,
        min=0.0,
        max=1.0,
        default=(0.18, 0.18, 0.18, 1.0),
        update=_preference_updated,
    )

    def draw(self, context):
        """Expose mode colors in add-on preferences because artists tune these visually."""
        layout = self.layout
        layout.prop(self, "enabled")
        layout.prop(self, "target_scope")
        layout.prop(self, "timer_interval")

        mode_box = layout.box()
        mode_box.label(text="Object Modes")
        mode_box.prop(self, "object_color")
        mode_box.prop(self, "edit_color")
        mode_box.prop(self, "sculpt_color")
        mode_box.prop(self, "pose_color")
        mode_box.prop(self, "paint_color")
        mode_box.prop(self, "fallback_color")

        select_box = layout.box()
        select_box.label(text="Mesh Edit Select Modes")
        select_box.prop(self, "vertex_select_color")
        select_box.prop(self, "edge_select_color")
        select_box.prop(self, "face_select_color")
        select_box.prop(self, "mixed_select_color")


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
    """Return add-on preferences when Blender has registered them for this module."""
    addon = context.preferences.addons.get(ADDON_ID)
    if addon is None:
        return None
    return addon.preferences


def _get_header_spaces(preferences, context):
    """Find theme header color owners so the add-on can restore exactly what it touches."""
    theme = context.preferences.themes[0]

    if preferences.target_scope == "VIEW_3D":
        return [theme.view_3d.space]

    header_spaces = []
    for prop in theme.bl_rna.properties:
        if prop.identifier == "rna_type":
            continue

        themed_area = getattr(theme, prop.identifier, None)
        space = getattr(themed_area, "space", None)
        if space is not None and hasattr(space, "header"):
            header_spaces.append(space)

    return header_spaces


def _remember_original_header(space):
    """Capture the untouched header color once so disabling the add-on restores the theme."""
    key = space.as_pointer()
    if key not in _ORIGINAL_HEADER_COLORS:
        _ORIGINAL_HEADER_COLORS[key] = (space, tuple(space.header))


def _restore_original_headers():
    """Restore all headers touched by this runtime to avoid leaving theme side effects behind."""
    global _LAST_APPLIED_COLOR, _LAST_TARGET_SCOPE

    for space, color in _ORIGINAL_HEADER_COLORS.values():
        try:
            space.header = color
        except ReferenceError:
            continue

    _ORIGINAL_HEADER_COLORS.clear()
    _LAST_APPLIED_COLOR = None
    _LAST_TARGET_SCOPE = None


def _get_mesh_select_mode_color(preferences, context):
    """Map vertex, edge, and face select modes to separate colors inside mesh Edit Mode."""
    vertex_enabled, edge_enabled, face_enabled = context.tool_settings.mesh_select_mode
    enabled_modes = [
        mode
        for mode, is_enabled in (
            ("VERTEX", vertex_enabled),
            ("EDGE", edge_enabled),
            ("FACE", face_enabled),
        )
        if is_enabled
    ]

    if enabled_modes == ["VERTEX"]:
        return tuple(preferences.vertex_select_color)
    if enabled_modes == ["EDGE"]:
        return tuple(preferences.edge_select_color)
    if enabled_modes == ["FACE"]:
        return tuple(preferences.face_select_color)
    if enabled_modes:
        return tuple(preferences.mixed_select_color)

    return tuple(preferences.edit_color)


def _get_mode_color(preferences, context):
    """Choose the active highlight color from Blender mode first, then mesh select mode."""
    active_object = context.object
    mode = active_object.mode if active_object is not None else "OBJECT"

    if mode == "OBJECT":
        return tuple(preferences.object_color)
    if mode == "EDIT":
        if active_object is not None and active_object.type == "MESH":
            return _get_mesh_select_mode_color(preferences, context)
        return tuple(preferences.edit_color)
    if mode == "SCULPT":
        return tuple(preferences.sculpt_color)
    if mode == "POSE":
        return tuple(preferences.pose_color)
    if mode in {"VERTEX_PAINT", "WEIGHT_PAINT", "TEXTURE_PAINT"}:
        return tuple(preferences.paint_color)

    return tuple(preferences.fallback_color)


def _apply_header_color(preferences, context, color):
    """Write the active color into the selected theme headers only when it has changed."""
    global _LAST_APPLIED_COLOR, _LAST_TARGET_SCOPE

    if preferences.target_scope != _LAST_TARGET_SCOPE:
        _restore_original_headers()

    if color == _LAST_APPLIED_COLOR and preferences.target_scope == _LAST_TARGET_SCOPE:
        return

    for space in _get_header_spaces(preferences, context):
        _remember_original_header(space)
        space.header = color

    _LAST_APPLIED_COLOR = color
    _LAST_TARGET_SCOPE = preferences.target_scope


def _apply_current_highlight(context):
    """Refresh the UI highlight so mode changes are visible without manual user action."""
    preferences = _get_preferences(context)
    if preferences is None:
        return

    if not preferences.enabled:
        _restore_original_headers()
        return

    _apply_header_color(preferences, context, _get_mode_color(preferences, context))


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
