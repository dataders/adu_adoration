# 3D lot model — house, shed, proposed ADU

True-scale 3D massing model of the whole lot (1 unit = 1 foot), built from the same
measured geometry as [`plan/generate_site_plan.py`](../plan/generate_site_plan.py):
45×148 lot, existing 1931 house (with porch + deck), 12×18 shed, and the proposed
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

## Heights used (estimates — field-verify)

| building | eave | ridge | notes |
|---|---|---|---|
| house | 10′ | 20′ | 1-story, gable ridge E–W, green siding |
| shed | 7.5′ | 10.8′ | corrugated metal, red slider on east gable end |
| ADU | 16′ | 20′ | two-story at the §30-680.4 20′ accessory cap |

Footprints and setbacks are the measured/confirmed values from the site plan
(front setback 25′, ADU 5′ off alley / 3′ off north line — variance required).
Preliminary massing only — not for construction.
