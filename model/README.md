# 3D lot model — house, replacement shed, proposed ADU

True-scale 3D massing model of the whole lot (1 unit = 1 foot), built from the same
measured geometry as [`plan/generate_site_plan.py`](../plan/generate_site_plan.py):
45×148 lot, existing 1931 house (with porch + deck), selected low-profile 18×6 replacement shed, and the proposed
20×24 two-story ADU at the R-5 20 ft accessory height cap, plus approximate massing
of the two neighboring houses for context.

## Files

- **`site-model-3d.html`** — interactive viewer, no internet or install needed: open it
  in any browser (double-click the file). Orbit with drag, zoom with scroll/pinch,
  pan with right-drag or shift-drag. Checkboxes toggle the ADU, shed, house, neighbors,
  R-5 setback lines and labels; buttons jump to preset views (also linkable via
  `#bird`, `#alley`, `#yard`, `#street`, `#top`).
- **`site-model.obj`** + **`site-model.mtl`** — the same model as a standard OBJ
  (Y-up, feet). Imports into SketchUp (File → Import), Blender, FreeCAD, or any
  online OBJ viewer. Hand this to an architect alongside `plan/site-plan.dxf`.
- **`generate_3d_model.py`** — regenerates all of the above:
  `python3 model/generate_3d_model.py` (stdlib only, no dependencies).

### Editable Option E FreeCAD model

- **`adu-option-e.FCStd`** — editable two-level Option E model. Organized into
  Level 1, Level 2, exterior access, and roof groups, with named walls, room
  zones, openings, fixtures, cabinetry, patios, balcony, and 13-step exterior
  stair. Objects retain source/category/level metadata.
- **`adu-option-e.glb`** — compact, color-preserving glTF 2.0 binary for WebGL,
  `<model-viewer>`, Three.js, Blender, and other real-time viewers.
- **`adu-option-e.obj`** — generic triangulated Wavefront OBJ export.
- **`adu-option-e-arch.obj`** + **`adu-option-e-arch.mtl`** — FreeCAD BIM/Arch
  Wavefront export with named objects and color materials.
- **`adu-option-e-sweethome.obj`** + **`adu-option-e-sweethome.mtl`** — same
  Arch geometry transformed from millimetres/Z-up to centimetres/Y-up; preferred
  Sweet Home 3D import.
- **`adu-option-e-sweethome-simple.obj`** — single-mesh, no-material fallback
  for Sweet Home 3D installations where the multi-material loader stalls.
- **`adu-option-e.step`** — named, color-preserving STEP export for CAD tools.
- **`adu-option-e.brep`** — ASCII OpenCASCADE geometry for low-level textual
  inspection. Exact but noisy in Git diffs.
- **`adu-option-e-manifest.json`** — deterministic semantic summary of every
  object's name, category, level, color, bounds, area, volume, and topology;
  preferred human-readable Git diff.
- **`adu-option-e-level-1.png`**, **`adu-option-e-level-2.png`**, and
  **`adu-option-e-axon.png`** — checked FreeCAD views for quick review.
- **`generate_freecad_adu.py`** — deterministic native-FreeCAD generator using
  the dimensions in `apartment/generate_floorplans.py`.
- **`export_freecad_formats.py`** — regenerates all interchange and diff exports
  from the saved FCStd model.
- **`convert_arch_obj_to_glb.py`** — converts the color-material Arch OBJ from
  millimetres/Z-up to a web-oriented GLB in metres/Y-up.
- **`prepare_sweethome_obj.py`** — converts the Arch OBJ units and up-axis for
  an exact-scale Sweet Home 3D import.
- **`BuildSweetHomeProject.java`** — uses Sweet Home 3D's bundled model API to
  create separate, non-overlapping `adu-option-e-level-1.sh3d` and
  `adu-option-e-level-2.sh3d` editable floor plans. `adu-option-e-floorplans.sh3d`
  is retained as a clean Level 2 view. Each keeps the fallback OBJ as a hidden
  3D reference.
- **`export_colored_step_gui.py`** — FreeCAD GUI startup script that overwrites
  the headless STEP baseline with names and native AP214 presentation colors.
- **`apply_freecad_view.FCMacro`** — reapplies stored colors and the saved
  axonometric view after a headless regeneration.

FreeCAD 1.1.3 on macOS bundles Qt 6.8.3. Qt's ARM CPU probe fails inside the
Codex sandbox because that environment blocks `sysctlbyname`; run this command
outside the sandbox. FreeCAD's bundled Python plus explicit module path avoids
the macOS `freecadcmd` positional-script issue:

```sh
PYTHONPATH=/Applications/FreeCAD.app/Contents/Resources/lib \
  /Applications/FreeCAD.app/Contents/Resources/bin/python \
  model/generate_freecad_adu.py
```

Then open `adu-option-e.FCStd` in FreeCAD and run
`apply_freecad_view.FCMacro` from **Macro → Macros…**. FreeCAD stores geometry
in millimetres; source coordinates and plan metadata remain in feet.

Regenerate the headless interchange exports:

```sh
PYTHONPATH=/Applications/FreeCAD.app/Contents/Resources/lib \
  /Applications/FreeCAD.app/Contents/Resources/bin/python \
  model/export_freecad_formats.py

uv run --with trimesh --with numpy python3 \
  model/convert_arch_obj_to_glb.py

uv run --with trimesh --with numpy python3 model/prepare_sweethome_obj.py

/Applications/FreeCAD.app/Contents/Resources/bin/freecad \
  -u /tmp/adu-freecad-export-user.cfg \
  -s /tmp/adu-freecad-export-system.cfg \
  "$PWD/model/export_colored_step_gui.py"
```

This remains a design-development model, not construction documentation.
Architect must verify floor/roof section, structure, stair and guards, egress,
fire separation, plumbing, and zoning treatment.

## Heights used (estimates — field-verify)

| building | eave | ridge | notes |
|---|---|---|---|
| house | 10′ | 20′ | 1-story, gable ridge E–W, green siding |
| replacement shed | 7′ | 9.5′ | 18×6 low-profile massing, red slider on east gable end |
| ADU | 16′ | 20′ | two-story at the §30-680.4 20′ accessory cap |

Footprints and setbacks are the measured/confirmed values from the site plan
(front setback 25′, ADU 5′ off alley / 5′ off north line).
Preliminary massing only — not for construction.
