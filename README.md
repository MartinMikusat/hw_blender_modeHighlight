# HW Mode Highlight

Automatically changes Blender editor header colors based on the current mode.

Author: Martin

## Features

- Highlights Object, Edit, Sculpt, Pose, and Paint modes with configurable colors.
- Highlights mesh Edit Mode select state separately for Vertex, Edge, and Face select modes.
- Uses a separate Mixed Mesh Select color when more than one mesh select mode is active.
- Can tint only the 3D View header or every editor header exposed by the active Blender theme.
- Restores the original theme header colors when the add-on is disabled.

## Installation

### Blender 5.1 Extension Install

1. Build the extension zip:

   ```sh
   mkdir -p dist
   zip -j dist/hw_mode_highlight-0.1.0.zip blender_manifest.toml __init__.py hw_mode_highlight.py README.md
   ```

2. In Blender, open **Edit > Preferences > Extensions**.
3. Use **Install from Disk...** and select `dist/hw_mode_highlight-0.1.0.zip`.
4. Enable **HW Mode Highlight**.

### Legacy Python Add-on Install

1. In Blender, open **Edit > Preferences > Add-ons**.
2. Click **Install...**.
3. Select `hw_mode_highlight.py` from this repository.
4. Enable **Interface: HW Mode Highlight**.

## Configuration

Open the add-on preferences to customize colors and behavior:

- **Header Scope** controls whether highlighting is limited to the 3D View or applied to all editor headers.
- **Object Modes** contains the colors used for regular Blender modes.
- **Mesh Edit Select Modes** contains the colors used when a mesh is in Edit Mode:
  - **Vertex Select** when only vertex select is active.
  - **Edge Select** when only edge select is active.
  - **Face Select** when only face select is active.
  - **Mixed Mesh Select** when multiple select modes are active at the same time.
- **Refresh Interval** controls how often the add-on checks the active mode. The default is quick enough to feel immediate while staying lightweight.

## Development

`hw_mode_highlight.py` contains the add-on implementation and can be installed directly as a legacy add-on. `__init__.py` and `blender_manifest.toml` provide the Blender 5 extension package entry point.

Generated extension zips belong in `dist/`, which is ignored by git.
