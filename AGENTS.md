# AGENTS.md

## Project Overview

`hw_modeHighlight` is a Blender 5.1+ extension/add-on maintained by Hal Wayland. Its purpose is intentionally narrow: while a mesh object is in Edit Mode, it changes the 3D View header bar color based on the active mesh select mode.

The highlighted UI element is the 3D View header that contains menu items such as **View**, **Select**, and **Add**. Do not broaden the add-on to tint arbitrary Blender editor headers unless explicitly requested.

## Repository Layout

- `hw_mode_highlight.py` contains the add-on implementation.
- `__init__.py` is the Blender extension package entry point.
- `blender_manifest.toml` contains Blender 5 extension metadata.
- `README.md` is the user-facing overview, installation, and configuration document.
- `dist/` is ignored and should only contain generated extension zip files.

## Blender Target

- Primary target: Blender `5.1.1`.
- The user's Steam Blender binary is:
  `/Users/martin/Library/Application Support/Steam/steamapps/common/Blender/Blender.app/Contents/MacOS/Blender`
- Prefer validating against this binary when possible.

## Core Behavior To Preserve

- Only apply highlighting in mesh Edit Mode.
- Restore the original 3D View header color outside mesh Edit Mode, when no mesh select mode is active, or when the add-on is disabled.
- Expose exactly three primary color preferences:
  - `Vertex Select`
  - `Edge Select`
  - `Face Select`
- When multiple mesh select modes are active, blend the selected configured colors rather than adding another preference.
- Use `theme.view_3d.space.header` for the header color. This is the theme property for the 3D View header bar.
- Keep extension preference lookup compatible with Blender extensions. `ADDON_ID` should resolve to the package id when installed as an extension.

## Development Commands

Run syntax checks:

```sh
python3 - <<'PY'
from pathlib import Path
for filename in ("hw_mode_highlight.py", "__init__.py"):
    path = Path(filename)
    compile(path.read_text(), str(path), "exec")
print("syntax ok")
PY
```

Build the extension zip:

```sh
mkdir -p dist
zip -j dist/hw_mode_highlight-0.2.0.zip blender_manifest.toml __init__.py hw_mode_highlight.py README.md
```

Validate the extension package with Steam Blender:

```sh
"/Users/martin/Library/Application Support/Steam/steamapps/common/Blender/Blender.app/Contents/MacOS/Blender" \
  --background \
  --factory-startup \
  --command extension validate "dist/hw_mode_highlight-0.2.0.zip"
```

Smoke-test register/unregister with Steam Blender:

```sh
"/Users/martin/Library/Application Support/Steam/steamapps/common/Blender/Blender.app/Contents/MacOS/Blender" \
  --background \
  --factory-startup \
  --python-expr "import importlib.util, pathlib, sys; root=pathlib.Path('.').resolve(); spec=importlib.util.spec_from_file_location('hw_mode_highlight', root / '__init__.py', submodule_search_locations=[str(root)]); mod=importlib.util.module_from_spec(spec); sys.modules[spec.name]=mod; spec.loader.exec_module(mod); print('loaded', mod.bl_info); mod.register(); print('registered'); mod.unregister(); print('unregistered')"
```

## Coding Guidelines

- Keep the implementation small and Blender-native; avoid extra dependencies.
- Use succinct docstrings for functions, including the motivation when useful.
- Give named functions/classes instead of anonymous callbacks.
- Preserve the add-on display name `hw_modeHighlight` unless the user explicitly asks to rename it.
- Preserve maintainer metadata as `Hal Wayland` unless the user explicitly asks to change it.
- Update `README.md` and `blender_manifest.toml` whenever behavior, versioning, install steps, or metadata changes.

## Git Guidance

- Use conventional commit messages.
- Do not commit unless the user explicitly asks.
- Do not push unless the user explicitly asks.
- Generated files in `dist/` should not be committed.
