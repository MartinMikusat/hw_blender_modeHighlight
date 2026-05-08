# hw_modeHighlight

Automatically changes the Blender 3D View header color based on the active mesh Edit Mode select state.

Maintainer: Hal Wayland

## Features

- Highlights the 3D View header bar that contains menus such as **View**, **Select**, and **Add**.
- Provides three configurable colors for Vertex, Edge, and Face select modes.
- Blends the selected colors when Blender has multiple mesh select modes active.
- Restores the original 3D View header color outside mesh Edit Mode or when the add-on is disabled.

## Installation

### Blender 5.1 Extension Install

1. Build the extension zip:

   ```sh
   mkdir -p dist
   zip -j dist/hw_mode_highlight-0.2.0.zip blender_manifest.toml __init__.py hw_mode_highlight.py README.md
   ```

2. In Blender, open **Edit > Preferences > Extensions**.
3. Use **Install from Disk...** and select `dist/hw_mode_highlight-0.2.0.zip`.
4. Enable **hw_modeHighlight**.

### Legacy Python Add-on Install

1. In Blender, open **Edit > Preferences > Add-ons**.
2. Click **Install...**.
3. Select `hw_mode_highlight.py` from this repository.
4. Enable **Interface: hw_modeHighlight**.

## Configuration

Open the add-on preferences to customize colors:

- **Vertex Select** controls the 3D View header color in vertex select mode.
- **Edge Select** controls the 3D View header color in edge select mode.
- **Face Select** controls the 3D View header color in face select mode.
- **Refresh Interval** controls how often the add-on checks mesh select mode changes. The default is quick enough to feel immediate while staying lightweight.

## Development

`hw_mode_highlight.py` contains the add-on implementation and can be installed directly as a legacy add-on. `__init__.py` and `blender_manifest.toml` provide the Blender 5 extension package entry point.

Generated extension zips belong in `dist/`, which is ignored by git.
