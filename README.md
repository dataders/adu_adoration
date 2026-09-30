# ADU planning — 112 W 29th St, Richmond, Virginia

Design studies, source records, generated plans, and coordinated 3D artifacts for a
proposed detached accessory dwelling unit (ADU) at **112 W 29th St** (PID 43615 / PIN
S0001130005), Richmond, VA 23225.

## Project status

**Option F revision 2 is the current schematic owner study.** It is a 20 × 24 ft, two-story detached
building with a full-depth garage/shop and owner office below, an approximately 480 sf
one-bedroom apartment above, a south exterior stair, and stacked east patios. The working ridge datum is 19 ft 10 in; official height measurement and applicable zoning limits remain unverified.

Start with these files:

1. [Construction and engineering basis](output/pdf/adu-option-f-construction-engineering-basis.pdf)
   — schematic owner-coordination set, regenerated from the revision 2 geometry.
2. [Option F floor plans](apartment/option-f-recommended-development.svg) — current room,
   opening, stair, landing, and patio layout.
3. [Option F site plan](plan/site-plan-option-f-architect.pdf) — current placement,
   setbacks, access, and replacement-shed response.
4. [Interactive site model](model/site-model-3d.html#yard) — browser-based whole-site
   model with furnished floor cutaways and roof controls; serve over local HTTP as below.
5. [Coordination manifest](option-f-artifact-manifest.json) — machine-readable authority,
   version, invariants, and current-versus-historical artifact boundary.

Option E is the owner-sketch baseline. Options A–E and their model artifacts remain useful
design history, but they do not override Option F. Current model renderings use the same exported scene as the browser viewer. Earlier AI images are mood references only and do not govern geometry.

The earlier balcony-entry study in `plan/floor-plans-balcony-scheme.{svg,png}` and
`renderings/massing-3d-interactive.html` is retained as historical reference only. It does
not override the current Option F authority.

> This repository contains schematic design work, not sealed permit or construction
> documents. Survey, zoning determinations, code analysis, structural engineering, energy
> compliance, utility verification, and trade design still require qualified professionals.

## Working design basis

| Item | Current basis |
|---|---|
| Lot | 45 × 148 ft; approximately 6,660 sf; R-5 |
| Existing house | 1,303 sf; one story; built 1931 |
| Orientation | Alley west/rear; W 29th St east/front |
| ADU envelope | 24 ft east–west × 20 ft north–south; 480 sf gross per level |
| ADU vertical datums | Upper subfloor 9.25 ft; eave 16 ft; ridge 19.833 ft |
| ADU site position | 5 ft from alley/rear line and 5 ft from north line |
| Exterior access | 14 risers / 13 treads; connected south landing and 4-ft east patios |
| Replacement shed | 18 × 6 ft maximum envelope; 108 sf; 5 ft clear south of ADU access |
| Field measurement | 25 ft front setback confirmed 2026-06-28 |

Revision 2 retains a 23-ft-clear garage/shop bay and approximately 70-sq-ft northeast garden office. The lower hall is 39 inches clear. A northwest powder room stacks below the upper bath; upstairs laundry opens directly to common space. An L-shaped kitchen with peninsula replaces the island, and the TV moves to the bedroom partition. Schematic furniture clearances are 53.6 inches west of the peninsula, 38.4 inches from sofa to slider route, and 39.6 inches from dining chairs to counter. These are drawing checks, not code-compliance findings.

A separate [garden-room alternative](apartment/option-f-alternative-garden.svg) trades parking depth (18 ft clear) for approximately 121 sq ft of connected garden space. It is exploratory and does not override the current CAD or model.

[`model/option_f_geometry.py`](model/option_f_geometry.py) is the canonical geometry source. Generated drawings, CAD, browser mesh, and renderings must agree with it; stale generated artifacts do not override source intent. Finished headroom, wall/floor/roof assemblies, and appliance operation remain design holds.

The existing field-measured 12 × 18 ft shed is designated for removal. The assessor record
instead describes a 360 sf detached garage; reconcile that discrepancy during survey and
permitting.

## Quick start

Requires [uv](https://docs.astral.sh/uv/) and Python 3.11 or newer.

```sh
uv sync --group dev --group architecture
./bin/check
```

`./bin/check` runs Ruff lint and format checks, ty type checking, then the architecture
artifact suite. The architecture checks audit the Option F DXF and access geometry, compare
the coordination and model manifests, load the STEP solids with OpenCascade, verify actual door apertures and furniture clearances, compare the viewer against the canonical scene, validate render provenance hashes, inspect the GLB container, and parse committed PDF/PNG outputs. The model manifest counts physical solids separately from the ten nonphysical room zones. CI also runs the official Khronos glTF
Validator and requires zero errors and warnings.

Install optional commit hooks with:

```sh
uv run --group dev pre-commit install
```

## Regenerating artifacts

Run generators from the repository root. Commit source and regenerated artifacts together,
then run `./bin/check`.

```sh
# Floor-plan studies (SVG and PNG)
uv run python apartment/generate_floorplans.py

# Current Option F site plan (DXF and PDF)
uv run python plan/generate_site_plan.py --option F

# Current Option F building model (STEP, BREP, GLB, OBJ, manifest)
uv run --group architecture python model/generate_option_f_model.py

# Whole-site viewer and OBJ
uv run python model/generate_3d_model.py

# Schematic drawing set PDF
uv run python plan/generate_construction_basis_set.py

# Model-derived exterior and furnished cutaway images (Blender executable required)
blender --background --python model/render_model.py -- --views yard alley upper lower

# Preview static website and viewer (ES modules require HTTP, not file://)
uv run --no-project python -m http.server 8000
```

Open [the local website](http://localhost:8000/) or [the full-screen model](http://localhost:8000/model/site-model-3d.html#yard). Three.js 0.180.0 is vendored locally. Render provenance is recorded in [`renderings/model-render-manifest.json`](renderings/model-render-manifest.json), including hashes of the source scene, renderer, and each image.

Some historical Option E exports require FreeCAD or Sweet Home 3D. See
[model/README.md](model/README.md) before changing them.

## Repository map

| Path | Purpose |
|---|---|
| [`apartment/`](apartment/) | Historical studies A–E, revision 2 floor sheets, garden alternative, and generator |
| [`plan/`](plan/) | Current Option F and historical Option E site plans plus plan-set generator |
| [`model/`](model/) | Option F geometry contract, generators, CAD/mesh exports, whole-site viewer, and historical Option E models |
| [`output/pdf/`](output/pdf/) | Current combined concept and construction/engineering basis sets |
| [`renderings/`](renderings/) | Model-derived revision 2 images and archived AI mood references |
| [`images/`](images/) | Measured sketches, site photos, assessor sketch, and satellite references |
| [`documents/`](documents/) | Source property and owner PDFs |
| [`inspiration/`](inspiration/) | Curated and Pinterest-synced style references |
| [`sync/`](sync/) | Pull-only public Pinterest RSS sync |
| [`scripts/`](scripts/) | Repository validation implementation |
| [`bin/`](bin/) | Stable developer entry points |
| [`index.html`](index.html) | Static public project brief |
| [`requirements.html`](requirements.html) | Static high-level requirements brief |

Folder-specific documentation:

- [Floor-plan decisions and constraints](apartment/README.md)
- [3D formats and historical model boundary](model/README.md)
- [Source documents](documents/README.md)
- [Reference imagery](images/README.md)
- [Inspiration library](inspiration/README.md)
- [Pinterest sync](sync/README.md)
- [Agent/developer workflow](CLAUDE.md)

## Pinterest inspiration sync

The sync mirrors new images from a public Pinterest board into `inspiration/` through the
board RSS feed. It uses no login or API token and never pushes or deletes pins.

```sh
uv run --no-project python sync/pinterest_pull.py --dry-run
uv run --no-project python sync/pinterest_pull.py
```

See [sync/README.md](sync/README.md) for board setup and limitations.

## Open coordination items

- Confirm the working 5-ft north setback, roof projections, openings, and fire-separation
  strategy with Richmond zoning/building review.
- Reconcile field-measured shed dimensions with the assessor record.
- Verify survey, soil, grading, drainage, and utility locations.
- Resolve final roof/floor section, stair and guard details, structure, MEP, egress, and
  conditioned-area treatment with the design team.

## Research sources

Property data came from the saved [actDataScout report](documents/richmond-datascout-report-S0001130005.pdf)
and assessor sketch. Field sketches and measurements are in `documents/` and `images/`.

Zoning research was last checked August 12, 2026. The September design revision does not refresh legal or code findings. Earlier research used these City and Municode sources:

- [City of Richmond ADU guidance](https://www.rva.gov/planning-development-review/accessory-dwelling-units)
- [Richmond zoning ordinance, Chapter 30](https://library.municode.com/va/richmond/codes/code_of_ordinances)
- [R-5 district provisions](https://library.municode.com/va/richmond/codes/code_of_ordinances?nodeId=CH30ZO_ARTIVDIRE_DIV6SIMIREDI)
- [Accessory-building provisions](https://library.municode.com/va/richmond/codes/code_of_ordinances?nodeId=CH30ZO_ARTVISURE_DIV9ACBU)
- [Richmond Code Refresh](https://www.rva.gov/planning-development-review/code-refresh)

Relevant research notes cite §§30-410.4–.7, 30-620.1, 30-680.1, and 30-680.4. Recheck
current law and obtain written determinations before relying on those notes.
