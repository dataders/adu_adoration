# Option F ADU image-generation prompts

Updated for the current Option F floor and site plans. These prompts supersede geometry inferred from Option E models and all earlier renders.

## Source hierarchy

Use sources in this order when they conflict:

1. `../apartment/option-f-recommended-development.png` — current rooms, openings, stair, landing, patios, and circulation
2. `../plan/site-plan-option-f.png` — current placement, setbacks, exterior access, patio depth, and replacement shed
3. `../plan/site-plan-option-f.dxf` — true-scale site geometry
4. `../inspiration/03-craftsman-gray-red-trim-carriage-door.jpg` — exterior style and materials only
5. actual `../images/` photographs — vegetation, fences, alley, and yard character
6. `../model/adu-option-f.step` and `../model/adu-option-f.glb` — current coordinated Option F three-dimensional geometry
7. Option E CAD/axonometric files — historical comparison only; never use their doors, windows, patio depth, room program, access geometry, or vertical datums

Earlier generated renders are not geometry references. In particular, do not restore Option E's first-floor shower, downstairs laundry, smaller sliders, separate office door, 3-ft-6-in patio depth, or a landing that stops before the east patio.

## Prompt 1 — shared master prompt

Use this prompt as the base for either exterior camera block.

```text
Use case: sketch-to-render
Asset type: photorealistic exterior architectural visualization

REFERENCE ROLES
The Option F floor plan is authoritative for room adjacencies, exterior openings, stair, landing, patios, and doors. The Option F site plan controls placement, setbacks, circulation, patio depth, and replacement-shed placement. The Craftsman reference controls style and materials. Actual site photographs control the Richmond alley, garden, vegetation, and weathered context. Option E files may inform general gable massing only and never override Option F geometry.

PRIMARY REQUEST
Create a convincing photograph of the proposed detached Option F ADU at 112 W 29th St in Richmond, Virginia. It must feel specifically designed for this compact, informal backyard rather than like a generic suburban new build.

BUILDING MASSING
- Enclosed footprint: exactly 24 feet east-west by 20 feet north-south, 480 square feet gross per level.
- Exactly two stories: full-depth garage, support space, powder room, protected hall, and owner office/garden room below; one-bedroom apartment above.
- Working top-of-upper-subfloor elevation: 9 feet 3 inches above the level-1 slab datum.
- East-west gable ridge: 16-foot eaves and a 19-foot-10-inch maximum ridge basis, with west alley and east yard elevations as gable ends.
- Low-pitch dark-charcoal composition-shingle roof. No shed roof, flat roof, or dormers.
- ADU sits 5 feet east of the west alley property line and 5 feet south of the north property line.
- Keep the west rake and north eave flush to the setback walls. Add projections there only after zoning approval or inward relocation of the building.

STYLE AND MATERIALS
- muted sage or gray-green horizontal wood lap siding
- warm creamy-white corner boards, fascia, posts, stair structure, landing structure, and traditional painted wood guards
- muted barn-red window sashes and selected doors
- divided-light windows, restrained projections where allowed, exposed painted rafter tails, restrained Craftsman knee braces, and a small gable vent
- black traditional lantern sconces
- cream carriage-style garage door with square top-row windows and black hardware
- real wood stair treads and decking
- believable texture and slight weathering; refined but not pristine

EXACT SOUTH STAIR AND CONNECTED LANDING — HIGHEST PRIORITY
- One straight exterior stair flight is attached parallel to the outside of the south wall.
- Stair is 4 feet wide, has 14 risers and 13 treads, and has an 11-foot horizontal run.
- It starts at grade at the southwest alley end and rises west-to-east.
- The stair occupies only the western 11 feet. Do not stretch stair treads across the entire south wall.
- At the top, all treads stop and a flat, raised, 4-foot-deep landing continues east along the south wall.
- A separate conventional hinged apartment-entry door opens from this landing into the upper south wall.
- The landing passes the entry, wraps around the southeast corner, and connects openly to the upper east patio. Do not end it at a small square platform or place a guard across the patio connection.
- Stair, flat landing, corner turn, and east patio form one continuous L-shaped circulation route.

STACKED EAST PATIOS AND LARGE SLIDERS
- Ground east patio: exactly 4 feet deep by approximately 19 feet 6 inches long, running almost the full south-to-north east wall.
- Upper east patio: the same 4-foot by 19-foot-6-inch footprint, stacked directly above the ground patio on painted Craftsman posts.
- Keep the upper patio narrow and full-length; do not turn it into an oversized deep deck.
- Upper level: one large 6-foot sliding-glass door near the south end, opening from the living room directly to the upper patio.
- Lower level: one large 6-foot sliding-glass door near the north end, opening from the owner office/garden room directly to the ground patio.
- Include restrained kitchen/dining glazing farther north on the upper east wall where compatible.
- Do not invent a separate exterior office door and do not replace either slider with a small hinged door or ordinary window.

COVERED LOWER SOUTH PATIO
- The raised flat south landing shelters the lower south patio; do not invent a separate roof or canopy.
- The lower south patio continues openly around the southeast corner into the ground east patio.
- Keep the stair flight itself open to the sky.

INTERIOR INTENT
- Level 1 has a powder room only, with no shower.
- Washer/dryer is upstairs in the northwest low-eave seasonal-storage room beside the stacked bath, not downstairs.
- The lower northeast room is an owner office/garden room, not a bedroom or independent dwelling unit.
- Upper southeast is open living; kitchen and dining occupy the east/north side.

REPLACEMENT SHED AND SITE
- Remove the old 12-by-18-foot corrugated shed from the scene.
- Show a low-profile replacement shed: 18 feet east-west by 6 feet north-south, maximum 108-square-foot outer envelope.
- Keep a clearly usable 5-foot circulation, drainage, and maintenance strip between shed and stair.
- Replacement shed has approximately 7-foot eaves, a 9-foot-6-inch ridge, and a muted red sliding door on its east gable end.
- Use actual Richmond backyard character: mature deciduous trees, lush informal garden beds, weathered wood fencing, gravel alley and parking surface, and humid Virginia greenery.

PHOTOGRAPHY
Photorealistic architectural photography, eye level, 28-35 mm lens, natural proportions, soft overcast Richmond daylight, restrained dynamic range, realistic shadows, slight material imperfections, and sharp architectural detail.

CONSTRAINTS
Exactly two stories. No third story, shed roof, flat roof, dormers, separate roof over landing/stair, spiral or switchback stair, stair on east facade, stair treads along the flat landing, guard blocking the southeast connection, oversized wraparound deck, black industrial railing, garage door on east/south, separate exterior office door, old tall shed, cars, people, labels, arrows, dimensions, signs, logos, or watermark.
```

## Prompt 2 — alley-side camera block

Append this block to Prompt 1.

```text
CAMERA — ALLEY-SIDE VIEW
Camera stands in the west alley, slightly southwest of the ADU, looking northeast. The west gable and garage elevation are primary. Frame enough of the south wall and east end to prove the complete access sequence.

Show one cream carriage-style garage door at level 1 and exactly one generous upper west bedroom EERO casement. Keep the west gable rake flush. South is camera-right. Near the camera, the 4-foot-wide stair rises away from the alley for its 11-foot run. At the top, treads stop and the long flat landing continues past the conventional upper entry and five-foot-wide raised-sill living window, then wraps openly around the southeast corner. There is no south-wall slider. Reveal enough of the stacked east patios and their two large sliders to make that connection legible.

Show the low 18-by-6-foot replacement shed south of the stair, not the old tall shed. Keep a visible 5-foot clear strip between shed and stair. Do not make the stair climb across the west garage facade, continue treads along the landing, or hide circulation beneath an invented stair roof.
```

Reference bundle:

1. `../apartment/option-f-recommended-development.png`
2. `../plan/site-plan-option-f.png`
3. `../inspiration/03-craftsman-gray-red-trim-carriage-door.jpg`
4. `../images/11-backyard-alley-parking-facing-east.jpg`

Current generated output: `option-f-alley-photoreal-v2.png`

## Prompt 3 — yard-side camera block

Append this block to Prompt 1.

```text
CAMERA — YARD-SIDE VIEW
Camera stands southeast of the ADU in the east yard, looking northwest at the southeast corner. The east gable and stacked patios are primary; the south wall and exterior stair recede on camera-left. Use a wide eye-level three-quarter composition that keeps both patios, both sliders, the flat landing, and the stair visible.

Show the upper and ground east patios at the same 4-foot by 19-foot-6-inch footprint. Clearly show the upper 6-foot living-room slider near the south end and lower 6-foot owner-room slider near the north end. The two sliders are separate openings serving different rooms. Include restrained upper kitchen/dining glazing farther north. Retain the conventional hinged apartment-entry door on the south landing and do not invent a separate exterior office door.

On camera-left, show the stair running along the south wall from southwest grade. Treads end after the 11-foot flight. The flat raised landing continues to the southeast corner, where it turns 90 degrees into the upper east patio with no guard across the opening. The landing shelters the lower south patio, which also connects openly to the ground east patio.

The low replacement shed may appear at the south edge of frame but must not block the stair, landing, or corner connection. Do not put stair treads across the east facade or long landing, reduce the landing to a small square, create a detached platform, or add an extra roof.
```

Reference bundle:

1. `../apartment/option-f-recommended-development.png`
2. `../plan/site-plan-option-f.png`
3. `../inspiration/03-craftsman-gray-red-trim-carriage-door.jpg`
4. `../images/10-backyard-garden-facing-north.jpg`

Current generated output: `option-f-yard-photoreal-v2.png`

## Remaining design caveat

The renderings communicate intent, not construction geometry. Before further render refinement, an architect and structural engineer should resolve the exact stair/guard section, clear patio width after guards, posts and lateral bracing, drainage/flashing, roof headroom, opening headers, and garage fire separation. Update the reference plans before regenerating images whenever those decisions change.
