# Option F revision 2 — shared 3D geometry

Current schematic owner study for a 24 × 20 ft ADU, with a garage and garden office below a 480-sq-ft gross apartment. Geometry is defined in [`option_f_geometry.py`](option_f_geometry.py). Site placement and existing buildings are working assumptions, not a surveyed or approved model.

## View the project

The viewer uses ES modules and must be served over HTTP. From repository root:

```sh
uv run --no-project python -m http.server 8000
```

Open [the project](http://localhost:8000/) or [the model](http://localhost:8000/model/site-model-3d.html#yard). Directly opening the HTML as `file://` is unsupported. Three.js 0.186.1 and its controls are vendored under `vendor/`; the viewer needs no CDN. The five view links are `#yard`, `#alley`, `#level1`, `#level2`, and `#site`. Drag to orbit, scroll/pinch to zoom, toggle the roof or furniture, and use furnished cutaways to inspect circulation. A static-image fallback is shown when WebGL cannot initialize.

## Current files and authority

- **`option_f_geometry.py`** — canonical feet/Z-up dimensions, openings, partitions, rooms, furniture, and checked circulation widths. Southwest building corner is origin; X east, Y north, Z up.
- **`generate_option_f_model.py`** — generates physical model components, cuts real wall apertures, and exports exact meshes plus neutral CAD.
- **`adu-option-f-scene.json`** — shared exact mesh data and semantic parts. Ten room zones are nonphysical metadata and are excluded from CAD/GLB/OBJ physical-solid counts.
- **`adu-option-f.step`**, **`.brep`** — physical schematic solids, in millimetres/Z-up. The manifest reports source geometry in feet.
- **`adu-option-f.obj`** — building mesh in feet/Z-up. **`adu-option-f.glb`** uses metres/Y-up.
- **`adu-option-f-manifest.json`** — version, physical-solid count, all semantic parts, datums, bounds, and circulation widths.
- **`site-model-3d.html`** — generated viewer with the exact canonical scene embedded. **`viewer-template.html`**, **`viewer.js`**, and **`viewer.css`** own its interface.
- **`site-model.obj`** — canonical building translated into site coordinates plus approximate context, in feet/Z-up. Pair with [`../plan/site-plan-option-f.dxf`](../plan/site-plan-option-f.dxf). `site-model.mtl` is retained from the earlier export and does not define current geometry.
- **`render_model.py`** — Blender renderer for model-derived exterior and furnished cutaway images; adds materials, lighting, ground, and sparse landscape context rather than inventing building geometry.

Regenerate in dependency order:

```sh
uv run --group architecture python model/generate_option_f_model.py
uv run python model/generate_3d_model.py
blender --background --python model/render_model.py -- --views yard alley upper lower
./bin/check
```

The four images are `renderings/option-f-yard-model.png`, `option-f-alley-model.png`, `option-f-upper-cutaway.png`, and `option-f-lower-cutaway.png`. `renderings/model-render-manifest.json` records source scene, image, and renderer SHA-256 hashes. Run all four views after geometry changes. Earlier AI images remain historical mood references.

## Revision 2 decisions

The 39-inch-clear downstairs hall connects the powder room and approximately 70-sq-ft garden office while retaining 23 ft of parking depth. Upstairs has an L-shaped kitchen and peninsula, common-space laundry access, and a TV on the bedroom partition. A separate approximately 121-sq-ft garden-room study shortens parking depth to 18 ft; it is not represented in the selected model.

Vertical datums remain +9.25 ft upper subfloor, +16 ft eave, and +19.833333 ft ridge. The exterior stair has fourteen risers from the +0.5 ft ground landing to the upper floor. The roof assembly allowance is provisional; finish headroom and actual assemblies require professional design. Four-foot exterior patios are principally circulation, and guard details and usable clear widths remain unresolved.

### Historical Option E FreeCAD model

Files below are retained only to document the previous Option E study. They are
not current geometry and must not be used to override Option F plans or models.

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
| ADU Option F | 16′ | 19′-10″ | +9′-3″ upper-subfloor basis; north eave and west rake flush pending zoning |

Footprints and setbacks follow the working site-plan basis (owner-measured front setback 25′, proposed ADU 5′ off alley / 5′ off north line), pending survey and zoning review.
Preliminary massing only — not for construction.
