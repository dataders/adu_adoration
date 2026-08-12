# CLAUDE.md

Repository guidance for coding agents and human contributors.

## Purpose and status

This repository coordinates schematic ADU design studies, generated drawings, 3D models,
reference material, and a static public brief. **Option F, basis version
`2026-08-03-option-f-basis-v1`, is current.** Work remains preliminary and not for
construction.

Do not turn research notes into claims of permit approval, code compliance, or
constructability. Preserve explicit field-verification and professional-review caveats.

## Source authority

Use `option-f-artifact-manifest.json` as the index of current artifacts and invariants. When
current files disagree, resolve intent in this order:

1. `output/pdf/adu-option-f-construction-engineering-basis.pdf`
2. `apartment/option-f-recommended-development.svg`
3. `plan/site-plan-option-f.dxf`
4. `model/option_f_geometry.py`

Use source records in `documents/` and `images/` for existing conditions. Use
`renderings/photoreal-render-prompt.md` for rendering source precedence. Never infer or
replace measured geometry from a photoreal rendering.

Option E and Options A–D are historical studies. Files matching `model/adu-option-e.*`,
`plan/site-plan.*`, and `plan/site-plan-architect.pdf` do not override current Option F
artifacts. Preserve them unless a task explicitly removes design history.

## Tooling

- Use `uv`; never invoke bare `pip`, `pip3`, or `python3`.
- Python requirement: 3.11 or newer.
- Install the complete local environment with
  `uv sync --group dev --group architecture`.
- Run the full repository gate with `./bin/check`.
- Run only architecture artifact checks with `./bin/check-plans`.
- Install hooks with `uv run --group dev pre-commit install`.

## Edit workflow

1. Inspect `git status` and preserve unrelated or untracked work.
2. Identify the governing source before editing a generated artifact.
3. Change the source and regenerate every affected committed output.
4. Update `option-f-artifact-manifest.json` when authority, paths, version, or coordinated
   invariants change.
5. Update README files and the public `index.html` when current deliverables or design status
   change.
6. Run `./bin/check` and review the full diff, including generated binaries and manifests.

Do not casually reformat generated SVG, HTML model payloads, DXF, OBJ, STEP, BREP, GLB, PDF,
or PNG files. Regenerate them through their owning scripts.

## Generator map

| Source | Owned outputs |
|---|---|
| `apartment/generate_floorplans.py` | `apartment/option-*.svg` and `.png` |
| `plan/generate_site_plan.py --option F` | `plan/site-plan-option-f.dxf` and architect PDF |
| `model/generate_option_f_model.py` | Option F STEP, BREP, GLB, OBJ, and model manifest |
| `model/generate_3d_model.py` | `model/site-model-3d.html`, `.obj`, and `.mtl` |
| `plan/generate_construction_basis_set.py` | construction/engineering basis PDF |
| `sync/pinterest_pull.py` | new `inspiration/pin-*` files and `sync/manifest.json` |

Generator commands live in the root README. Historical FreeCAD and Sweet Home 3D commands
and platform constraints live in `model/README.md`.

## Current Option F invariants

- Enclosed footprint: 24 × 20 ft.
- Upper subfloor: 9.25 ft; eave: 16 ft; ridge: 19.833 ft.
- Exterior access: 14 risers, 13 treads, connected south landing, 4-ft east patios.
- East sliders: 6 ft on both floors.
- North wall: no openings at concept stage.
- West upper wall: one bedroom window.
- Setback-side roof edges: north eave and west rake flush in current basis.

`scripts/check_plans.py` enforces these values against committed artifacts. If design intent
changes, update source geometry, generators, manifests, checks, outputs, and documentation in
one coordinated change; do not weaken checks merely to accept drift.

## Documentation rules

- Call Option F **current** and Options A–E **historical**, **study**, or **baseline** as
  appropriate.
- Keep README focused on status, entry points, verification, and repo navigation. Put detailed
  format or subsystem instructions in folder READMEs.
- Link to repository files with relative Markdown links.
- Distinguish measured facts, property-record facts, working assumptions, and unresolved items.
- Date time-sensitive zoning or code research and recommend live re-verification.
- Keep public `index.html`, root `README.md`, and the coordination manifest aligned.

## Safety and scope

Source PDFs, site photographs, owner sketches, and curated inspiration are project records,
not disposable build outputs. Pinterest sync is pull-only and must not require credentials.
Never add secrets, private board data, or local absolute paths to tracked files.
