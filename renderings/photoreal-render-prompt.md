# Final Option E ADU render prompts

Prompts used for the final Option E exterior renders:

- `option-e-final-alley-l-stair.png`
- `option-e-final-yard-l-stair.png`

Generated with built-in OpenAI ImageGen. The floor plan controls geometry; inspiration and site photos control exterior style, materials, scale, and setting.

## Reference hierarchy

1. Geometry source of truth:
   - `../apartment/option-e-primary-design-basis.png`
2. Primary exterior style:
   - `../inspiration/03-craftsman-gray-red-trim-carriage-door.jpg`
   - Craftsman direction documented in this repository
3. Supporting style:
   - `../inspiration/04-olive-carriage-door-balcony-cottage.jpg`
   - `../inspiration/pin-407012885098092632-garden-garage-apartment-with-glass-corner-sunroo.jpg`
   - remaining `../inspiration/` images for warmth, craftsmanship, compact residential scale, and mature landscaping
4. Actual site context:
   - `../images/09-backyard-shed-facing-west.jpg`
   - `../images/10-backyard-garden-facing-north.jpg`
   - `../images/11-backyard-alley-parking-facing-east.jpg`

Incompatible modern, brick, and shed-roof references are mood and scale references only. They do not override the primary Craftsman form, palette, or roof.

## Shared master prompt

```text
Use case: sketch-to-render
Asset type: photorealistic exterior architectural visualization

REFERENCE ROLES
The Option E floor plan is the absolute geometry source of truth. The Craftsman garage-ADU image is the primary exterior style reference. Supporting garage-apartment and garden references contribute compact scale, wood balcony character, warmth, and indoor-outdoor atmosphere. Actual backyard and alley photographs establish the Richmond site context. Do not copy geometry from style references.

PRIMARY REQUEST
Create a convincing photograph of the proposed detached ADU at 112 W 29th St in Richmond, Virginia. It must feel designed specifically for this existing informal backyard, not like a generic suburban new build.

BUILDING
A compact 24-foot east-west by 20-foot north-south, two-story garage ADU, no more than 20 feet tall. Garage, bathroom, office, and sunroom are downstairs; one-bedroom apartment is upstairs. Use an east-west roof ridge, so the alley-facing west elevation and yard-facing east elevation are gable ends. Use a low-pitch dark-charcoal composition-shingle gable roof.

STYLE AND MATERIALS
Match the nearby 1931 Craftsman bungalow:
- muted sage or gray-green horizontal wood lap siding
- warm creamy-white corner boards, fascia, posts, stair structure, and railings
- muted barn-red window sashes and selected doors
- divided-light double-hung windows
- wide eaves with exposed painted rafter tails
- restrained Craftsman knee braces
- small gable vent
- black traditional lantern sconces
- cream wood carriage-style garage door with square top-row windows and black strap hardware
- real wood stair treads and decking
- traditional painted wood guardrails, not modern black metal
- believable weathering and material texture; refined but not pristine

CRITICAL STAIR AND PATIO GEOMETRY — HIGHEST PRIORITY
The exterior stair and second-floor patio form one continuous L shape:

- One single straight stair flight runs WEST TO EAST along the OUTSIDE OF THE SOUTH WALL.
- The stair begins at grade beside the alley at the SOUTHWEST end.
- It rises eastward toward the yard.
- Its upper landing is at the SOUTHEAST corner.
- At that corner, circulation turns exactly 90 degrees and becomes the upper patio.
- The upper patio runs SOUTH TO NORTH along the OUTSIDE OF THE EAST WALL.
- The stair is parallel to the south wall.
- The patio is perpendicular to the stair and parallel to the east wall.
- Their walking surfaces and guardrails connect continuously at the southeast corner.
- Make this L-shaped relationship visually unmistakable.

This is not a stair on the east facade. It is not a switchback stair. It is not a stair climbing north-south. The patio does not continue west across the south facade. Do not separate the stair from the patio.

EAST ELEVATION
Use stacked outdoor spaces along the east wall:
- ground-level east patio serving the office and sunroom
- second-floor east patio directly above it
- upper apartment entered through a large sliding-glass door from the upper patio
- lower sunroom and office may use generous glazing
- painted Craftsman posts support the upper patio

Keep the upper patio narrow and proportional to the compact building, not a large wraparound deck.

SITE
Use the actual Richmond backyard character: mature deciduous trees, lush informal vegetable and flower garden, weathered horizontal-board garden enclosures, aged wood privacy fencing, gravel alley and parking surface, humid Virginia greenery, and the existing corrugated-metal shed with its barn-red sliding door. Preserve enough clearance around the south stair; the shed must not block or intersect it. Site should feel lived-in and specific, with natural irregularity rather than staged landscaping.

PHOTOGRAPHY
Photorealistic architectural photography, eye level, 28-35 mm lens, natural proportions, soft overcast Richmond daylight, restrained dynamic range, realistic shadows, slight material imperfections, and sharp architectural detail.

CONSTRAINTS
Exactly two stories. No third story. No shed roof. No flat roof. No dormers. No roof covering the stair. No spiral or switchback stair. No black industrial railing. No oversized luxury deck. No generic white stucco. No cars or people. No labels, arrows, dimensions, signs, logos, or watermark.
```

## Alley-side camera block

Append this block to the shared prompt:

```text
CAMERA — ALLEY-SIDE VIEW
Camera stands in the west alley, slightly southwest of the ADU, looking northeast. The west gable and garage elevation is the primary facade. Show the cream carriage-style garage door, upper divided-light windows, Craftsman gable, and relocated metal shed nearby.

South is camera-right. The stair begins near the camera at the southwest corner, then recedes along the right or south wall while rising west-to-east toward the southeast corner. Show enough east-side depth to reveal the 90-degree turn into the upper east patio. Do not make the stair climb across the west garage facade.
```

Reference bundle used:

1. `../apartment/option-e-primary-design-basis.png`
2. `../inspiration/03-craftsman-gray-red-trim-carriage-door.jpg`
3. `../inspiration/04-olive-carriage-door-balcony-cottage.jpg`
4. `../inspiration/pin-407012885098092632-garden-garage-apartment-with-glass-corner-sunroo.jpg`
5. `../images/11-backyard-alley-parking-facing-east.jpg`

## Yard-side camera block

Append this block to the shared prompt:

```text
CAMERA — YARD-SIDE VIEW
Camera stands in the east yard, slightly southeast of the ADU, looking northwest at the southeast corner. The east gable elevation and stacked patios are primary. Show the garden, lower patio and sunroom, upper patio, Craftsman posts, and upper sliding-glass apartment entry.

The south wall recedes on camera-left. One straight exterior stair begins at southwest grade farther back along that wall and rises west-to-east toward the visible southeast corner. At the corner it turns exactly 90 degrees to camera-right into the south end of the upper patio, which continues south-to-north along the east wall. Show the stair top, square corner landing, and east patio as one continuous L-shaped walking surface with continuous cream-painted wood guardrails. Do not place the stair across the east facade. Do not place a garage door on the east or south elevation.
```

The final yard render used `option-e-yard-east-elevation-v3.png` as an edit target to preserve the east-gable camera and stacked-patio composition. It was corrected to match the final alley render's materials and to enforce these invariants:

```text
Preserve the east-yard viewpoint, east-facing gable, stacked east patios, and garden setting. Match the final alley render's exact Craftsman materials and scale. The east elevation must not have a garage door; the garage door exists only on the west alley elevation.

The south-wall stair starts at southwest grade and rises eastward to the southeast corner. At that corner it turns 90 degrees into the south end of the east-wall upper patio. Show stair, square corner landing, and patio as one continuous L shape. No stair across the east facade, no patio along the south facade, no switchback, detached landing, extra stair, or wraparound deck.
```

Reference bundle used for the final yard correction:

1. `option-e-yard-east-elevation-v3.png` — edit target
2. `option-e-final-alley-l-stair.png` — final style and building-consistency anchor
3. `../apartment/option-e-primary-design-basis.png` — geometry source of truth
4. `../inspiration/03-craftsman-gray-red-trim-carriage-door.jpg` — primary style
5. `../images/10-backyard-garden-facing-north.jpg` — site context
