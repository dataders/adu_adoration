# Option E ADU image-generation prompts

Updated for the latest Option E CAD model and site plan. These prompts supersede geometry inferred from earlier renders.

## Source hierarchy

Use sources in this order when they conflict:

1. `../model/adu-option-e-manifest.json` — exact modeled dimensions and named elements
2. `../model/adu-option-e-axon.png` — exterior-access and roof geometry
3. `../apartment/option-e-primary-design-basis.png` — room layout and circulation intent
4. `../plan/site-plan.png` — site placement, setbacks, and replacement shed
5. `../inspiration/03-craftsman-gray-red-trim-carriage-door.jpg` — primary exterior style
6. actual `../images/` site photographs — vegetation, fences, alley, and yard character

Earlier generated renders are not geometry references. Incompatible modern, brick, and shed-roof inspiration images may inform warmth and scale only; they never override the selected Craftsman form, gable roof, or materials.

## Prompt 1 — shared master prompt

Use this prompt as the base for either exterior camera block.

```text
Use case: sketch-to-render
Asset type: photorealistic exterior architectural visualization

REFERENCE ROLES
The Option E CAD manifest and axonometric model are the absolute exterior-geometry sources of truth. The Option E floor plan controls interior adjacency, openings, and circulation intent. The site plan controls setbacks and replacement-shed placement. The Craftsman reference controls exterior style and materials. Actual site photographs control the Richmond alley, garden, vegetation, and weathered context. Do not copy geometry from style photographs or earlier generated renders.

PRIMARY REQUEST
Create a convincing photograph of the proposed detached Option E ADU at 112 W 29th St in Richmond, Virginia. It must look specifically designed for this compact, informal backyard rather than like a generic suburban new build.

BUILDING MASSING
- Enclosed footprint: exactly 24 feet east-west by 20 feet north-south, 480 square feet gross per level.
- Exactly two stories: garage, bathroom, office, and sunroom below; one-bedroom apartment above.
- Working second-floor elevation: 9 feet 6 inches above grade.
- East-west gable ridge: 16-foot eaves and 20-foot ridge, with west alley and east yard elevations as gable ends.
- Low-pitch dark-charcoal composition-shingle roof. No shed roof, flat roof, or dormers.
- ADU sits 5 feet east of the west alley property line and 5 feet south of the north property line.

STYLE AND MATERIALS
Match the nearby 1931 Craftsman bungalow:
- muted sage or gray-green horizontal wood lap siding
- warm creamy-white corner boards, fascia, posts, stair structure, landing structure, and guardrails
- muted barn-red window sashes and selected doors
- divided-light double-hung windows
- wide eaves with exposed painted rafter tails
- restrained Craftsman knee braces and a small gable vent
- black traditional lantern sconces
- cream wood carriage-style garage door with square top-row windows and black strap hardware
- real wood stair treads and decking
- traditional painted wood guards, not black industrial metal
- believable texture and slight weathering; refined but not pristine

EXACT SOUTH STAIR AND LANDING GEOMETRY — HIGHEST PRIORITY
- One straight exterior stair flight is attached parallel to the outside of the south wall.
- Stair is 4 feet wide, has 13 steps, and has an 11-foot horizontal run.
- It starts at grade at the southwest alley end and rises west-to-east.
- The stair flight occupies only the western 11 feet. Do not stretch stair treads across the entire south wall.
- At the top of the flight, a raised 16-foot-long by 4-foot-deep upper landing continues east along the south side.
- Of that landing, 12 feet 6 inches runs directly beside the south wall; its final 3 feet 6 inches extends beyond the east wall to align with the outer edge of the east patio.
- The landing wraps around the southeast corner and has a fully open 3-foot-6-inch connection into the upper east patio. Do not stop the landing at the building wall and do not place a guard across this opening.
- Stair flight, long upper landing, corner wrap, and east patio form one continuous L-shaped circulation route with continuous code-scale painted wood guards along exposed edges.

STACKED EAST PATIOS
- Ground east patio: 3 feet 6 inches deep by approximately 19 feet 6 inches long, running south-to-north outside the east wall.
- Upper east patio: same 3-foot-6-inch by 19-foot-6-inch footprint, stacked directly above the ground patio.
- The upper landing and upper east patio meet at their shared 3-foot-6-inch southeast edge with no barrier.
- Painted Craftsman posts support the upper east patio.
- The upper apartment entry is a 5-foot-wide sliding-glass door near the south end of the east wall.
- A separate east kitchen window sits farther north on level 2.
- Level 1 has a sunroom east window, a 4-foot-wide sunroom sliding-glass door, and a separate office door near the north end.
- Never place a garage door on the east or south elevation.

COVERED LOWER SOUTH PATIO
- Directly below the raised 16-by-4-foot upper landing is a matching 16-by-4-foot level-1 south patio.
- The upper landing itself shelters this lower patio; do not invent a separate roof or canopy.
- The lower south patio continues around the southeast corner into the ground east patio through the same open 3-foot-6-inch connection.
- Keep the 11-foot stair flight open to the sky. Do not roof over the stair.

REPLACEMENT SHED AND SITE
- Do not show the old 12-by-18-foot corrugated shed; it is removed.
- Show the selected replacement shed: low-profile 18 feet east-west by 6 feet north-south, maximum 108-square-foot outer envelope.
- Replacement shed is 8 feet east of the alley, its south edge sits on the 5-foot side-setback line, and its north edge remains 5 feet south of the ADU stair.
- Shed has approximately 7-foot eaves, a 9-foot-6-inch ridge, and a red sliding door on its east gable end. Roof edges, gutters, and foundation remain inside the 18-by-6-foot envelope.
- Preserve a clearly usable 5-foot circulation, drainage, and maintenance strip between shed and stair.
- Use actual Richmond backyard character: mature deciduous trees, lush informal vegetable and flower beds, weathered horizontal-board garden enclosures, aged wood privacy fencing, gravel alley and parking surface, and humid Virginia greenery.
- Site should feel lived-in and naturally irregular, not professionally staged.

PHOTOGRAPHY
Photorealistic architectural photography, eye level, 28-35 mm lens, natural proportions, soft overcast Richmond daylight, restrained dynamic range, realistic shadows, slight material imperfections, and sharp architectural detail.

CONSTRAINTS
Exactly two stories. No third story. No shed roof. No flat roof. No dormers. No separate roof over landing or stair. No spiral or switchback stair. No stair on the east facade. No stair treads along the 16-foot landing. No guard blocking the southeast connection. No oversized wraparound deck. No black industrial railing. No generic white stucco. No old 12-by-18-foot shed. No cars or people. No labels, arrows, dimensions, signs, logos, or watermark.
```

## Prompt 2 — alley-side camera block

Append this block to Prompt 1.

```text
CAMERA — ALLEY-SIDE VIEW
Camera stands in the west alley, slightly southwest of the ADU, looking northeast. The west gable and garage elevation is the primary facade. Frame enough of the south elevation and east end to prove the entire access sequence.

Show the west elevation accurately: one cream carriage-style garage door at level 1; separate upper west bedroom and bathroom windows rather than a symmetrical decorative pair; Craftsman gable, vent, brackets, eaves, and lanterns.

South is camera-right. Near the camera, the 4-foot-wide 13-step stair rises away from the alley for an 11-foot run. At the top, treads stop and the flat 16-by-4-foot landing continues east beside the south wall, then projects 3 feet 6 inches past the southeast corner to align with the east patio. Show the long flat landing and the covered lower south patio beneath it. Reveal enough of the east side to show the fully open 90-degree connection into the stacked 3-foot-6-inch-deep east patios.

Show the new low-profile 18-by-6-foot replacement shed south of the stair, not the old tall 12-by-18-foot shed. Keep a visible 5-foot clear strip between shed and stair. The replacement shed should read as a narrow east-west garden-storage building with its red slider on the east gable, not as a second garage.

Do not make the stair climb across the west garage facade. Do not continue stair treads across the long landing. Do not hide the landing beneath an invented stair roof.
```

Five-image reference bundle:

1. `../model/adu-option-e-axon.png`
2. `../apartment/option-e-primary-design-basis.png`
3. `../plan/site-plan.png`
4. `../inspiration/03-craftsman-gray-red-trim-carriage-door.jpg`
5. `../images/11-backyard-alley-parking-facing-east.jpg`

## Prompt 3 — yard-side camera block

Append this block to Prompt 1.

```text
CAMERA — YARD-SIDE VIEW
Camera stands southeast of the ADU in the east yard, looking northwest at the southeast corner. The east gable and stacked patios are primary; the south wall recedes on camera-left. Use a wide eye-level three-quarter composition that keeps the stair, long landing, southeast opening, and most of both east patios visible at once.

Show the east elevation accurately. The 3-foot-6-inch-deep upper patio runs almost the full 20-foot north-south wall and is stacked directly above the ground patio on painted Craftsman posts. Place the 5-foot upper sliding-glass entry near the south end, the separate kitchen window farther north, the lower sunroom window and 4-foot slider below, and the separate office door near the north end. Never place a garage door on this elevation.

On camera-left, show the 13-step stair running along the south wall from southwest grade toward the camera. Treads end after the 11-foot flight. From there, the raised 16-by-4-foot flat landing continues to and beyond the southeast corner, sheltering the matching covered lower patio. At the corner, clearly show the full 3-foot-6-inch-wide barrier-free opening where the landing turns 90 degrees into the upper east patio. The lower covered south patio must also connect openly around the corner into the ground east patio.

Place the low 18-by-6-foot replacement shed farther south with a visible 5-foot clear strip to the stair. The shed may appear at the edge of the frame but must not block the stair, landing, or southeast connection. Do not reproduce the old tall corrugated shed from site photographs.

Do not put stair treads across the east facade or long landing. Do not reduce the landing to a small square. Do not place a guard across the open corner connection. Do not create a detached platform, switchback stair, wraparound deck, or extra roof.
```

Five-image reference bundle:

1. `../model/adu-option-e-axon.png`
2. `../apartment/option-e-primary-design-basis.png`
3. `../plan/site-plan.png`
4. `../inspiration/03-craftsman-gray-red-trim-carriage-door.jpg`
5. `../images/10-backyard-garden-facing-north.jpg`
