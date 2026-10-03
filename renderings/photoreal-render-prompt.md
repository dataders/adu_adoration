# Option F revision 2 — rendering brief and image prompts

Updated September 30, 2026. Design version: `2026-09-30-option-f-basis-v2`.

## What has actually been generated

The current images are deterministic Blender Cycles architectural studies from
[`adu-option-f-scene.json`](../model/adu-option-f-scene.json), not AI-generated
photographs. Their source, renderer, and image hashes are recorded in
[`model-render-manifest.json`](model-render-manifest.json).

| View | Current generated image |
|---|---|
| Yard / southeast exterior | [Yard model render](option-f-yard-model.png) |
| Alley / southwest exterior | [Alley model render](option-f-alley-model.png) |
| Upper apartment cutaway | [Upper cutaway](option-f-upper-cutaway.png) |
| Lower garage and garden office cutaway | [Lower cutaway](option-f-lower-cutaway.png) |

All four are 1800 × 1200 pixels, rendered at 64 samples. Materials and context
are illustrative; the double-teardrop siding appearance is an approximate bump
profile, not a selected product. The older `*-photoreal*.png` and AI interior
images remain historical mood references. They have not been regenerated for
revision 2. The [previous prompt brief](archive/photoreal-render-prompt-v1.md)
is archived for provenance.

The prompts below are the updated brief for future image refinement. They did
not generate the four current Blender images. Keep any future AI refinements
separately named and labeled until their geometry has been checked.

## Source hierarchy and reference bundle

1. [Shared geometry contract](../model/option_f_geometry.py): dimensions,
   datums, rooms, openings, partitions, and furniture positions.
2. [Exported scene](../model/adu-option-f-scene.json),
   [STEP](../model/adu-option-f.step), and [GLB](../model/adu-option-f.glb):
   coordinated geometry. Source/OBJ coordinates are feet, Z-up; GLB is metres,
   Y-up; STEP is millimetres.
3. [Lower plan](../apartment/option-f-level-1.png),
   [upper plan](../apartment/option-f-level-2.png), and
   [site plan](../plan/site-plan-option-f.png): visual layout and placement checks.
4. The matching current model image above: fixed camera and geometry reference
   for any image-to-image refinement.
5. Actual [yard photo](../images/10-backyard-garden-facing-north.jpg),
   [alley photo](../images/11-backyard-alley-parking-facing-east.jpg), and
   [Craftsman reference](../inspiration/03-craftsman-gray-red-trim-carriage-door.jpg):
   context and material character only.

Resolve disagreements in the source geometry and regenerate affected outputs.
Never recover dimensions from an earlier AI image. The
[larger garden-room alternative](../apartment/option-f-alternative-garden.svg)
is a separate, unselected study and must not be mixed into these renders.

## Shared master prompt

Append one camera block below. Supply its matching model image and plan as
references; a text prompt alone does not establish dimensional fidelity.

```text
Create an architectural visualization of Option F revision 2. Preserve the
supplied model's silhouette, proportions, openings, partitions, furniture
locations, stair, landing, and balconies. Refine light and materials only.
If a reference is missing or ambiguous, flag it instead of inventing geometry.

GEOMETRY
Exactly two stories; enclosed footprint 24 ft east-west × 20 ft north-south.
West is the alley; east is the yard. The gable ridge runs east-west. No dormers.
Project datums: ground slab top +0.5 ft, upper floor +9.25 ft, eave +16 ft,
ridge +19.833333 ft. The floor-to-floor rise is 8.75 ft, not 9.25 ft.
Roof slope follows these datums, approximately 4.6:12. North eave and west
rake stay flush. These are project datums, not a verified legal grade height.

ACCESS AND OPENINGS
The straight south stair rises west-to-east, with 14 risers of 7.5 inches,
13 treads, an 11-ft run and 4-ft width. Treads stop at the upper landing.
The flat 4-ft-deep south landing continues east and turns openly onto the
4-ft-deep east balcony. Keep the connection free of a crossing guard.
The east patios are approximately 19.5 ft long and stack vertically.
One hinged upper entry and one 5-ft living window are on the south wall.
The west garage door is below the single upper bedroom window.
East: a lower shop window and 6-ft garden-office slider near the north end;
above, a 6-ft living slider near the south end and dining window farther north.
Use exact opening positions from the model. No north-wall openings.

ROOMS AND CIRCULATION
Below: 23-ft-clear garage/shop, 39-inch-clear hall, powder room, mechanical
support, and approximately 70-sq-ft northeast garden office. No shower,
bedroom, laundry, or additional exterior office door downstairs.
Above: west bedroom and closet, northwest full bath, laundry cupboard with
access directly from common space, and open east living/kitchen/dining.
Use the L-shaped kitchen and attached peninsula, not a freestanding island.
The sofa faces the TV on the bedroom partition; no freestanding media wall.
Preserve the 53.6-inch kitchen approach, 38.4-inch sofa-to-slider route and
39.6-inch dining-chair-to-counter gap shown by the schematic furniture test.
Do not enlarge rooms, move walls, or substitute the 121-sq-ft garden alternative.

APPEARANCE
Restrained Craftsman character: sage/gray-green double-teardrop-style siding,
cream trim and guards, muted red accents, charcoal roof, warm wood decking.
Keep structural silhouettes and window divisions from the supplied model.
No invented braces, roof overhangs, gable vents, canopies, or extra openings.
Color and finish are illustrative selections. Use soft directional daylight,
readable shadows, natural material texture and a calm, uncluttered background.
No people, labels, dimensions, logos or watermarks. Do not imply permit approval.
```

## Yard exterior camera

Reference: current yard model image, both plans, site plan, and actual yard photo.

```text
View from southeast toward northwest. East gable and stacked balconies are
primary; south stair remains visible on camera-left. Frame the complete stair,
flat landing, southeast turn, both east sliders and both balcony levels.
Keep the upper slider south and the lower garden-office slider north.
Use the supplied model camera for a directly comparable architectural study.
For an explicitly requested photographic variant, use a natural 28–35 mm lens
and maintain all model geometry; do not use perspective to conceal mismatches.
```

## Alley exterior camera

Reference: current alley model image, both plans, site plan, and actual alley photo.

```text
View from southwest toward northeast. West gable, garage door and one upper
bedroom window are primary. South stair is camera-right, rising away from the
alley before reaching a flat landing. Show the connected landing and east turn.
Do not place the garage door on the east facade or continue treads along the
landing. Any site context must follow the site plan: ADU 5 ft from west and
north lot lines; replacement shed 18 × 6 ft, with a 5-ft gap south of access.
Shed and existing-house heights are approximate; their masses are optional
context, not required parts of a close building view.
```

## Upper apartment cutaway

Reference: current upper cutaway and upper floor plan.

```text
Elevated southeast three-quarter cutaway looking northwest. Remove roof and
clip architectural walls 3 ft above the +9.25-ft upper floor; cap cut surfaces.
Keep furniture at its modeled height, and show the whole apartment and balcony.
Read the west bedroom/closet, northwest bath, direct-access laundry, attached
kitchen peninsula, northeast dining, southeast sofa and west-facing TV clearly.
Keep door apertures visible. Do not substitute an imagined eye-level room,
widen circulation, relocate appliances or add a freestanding kitchen island.
```

## Lower garage and garden-office cutaway

Reference: current lower cutaway and lower floor plan.

```text
Elevated southeast three-quarter cutaway looking northwest. Remove the upper
story and roof, clip architectural walls 3 ft above the +0.5-ft slab, and cap
cut surfaces. Show an empty garage/shop so its clear depth can be read.
Retain the hall, powder room, mechanical support, furnished garden office and
northeast yard slider. Preserve actual door openings and the 39-inch hall.
Do not fill the garage with a giant vehicle proxy or enlarge the office.
```

## Reproduce the current model images

From the repository root, with Blender available:

```sh
uv run --group architecture python model/generate_option_f_model.py
blender --background --python model/render_model.py -- --views yard alley upper lower --width 1800 --samples 64
uv run python model/generate_3d_model.py
uv run python plan/generate_construction_basis_set.py
./bin/check
```

After geometry changes, regenerate plans too. Inspect all images against the
current plans, including openings, stair transitions, furniture and circulation.
Refresh PDF covers and the provenance manifest together. Finished headroom,
assemblies, structure, guards, survey and permits remain professional design items.
